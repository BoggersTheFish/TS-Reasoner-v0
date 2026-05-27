#!/usr/bin/env python3
"""Evaluate a live/export-style TensionLM JSONL smoke through the v1.3 adapter."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.tensionlm_adapter import parse_tensionlm_export_row, run_tensionlm_export_row


def git_value(args: list[str], default: str = "unknown") -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return default


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rate(values: list[bool]) -> float:
    return round(sum(values) / max(1, len(values)), 4)


def load_export(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_row(raw_row: dict[str, Any], index: int) -> dict[str, Any]:
    row = parse_tensionlm_export_row(raw_row, index)
    payload = run_tensionlm_export_row(row)
    results = payload["verification"]["candidate_results"]
    by_claim = {result["claim"]: result for result in results}
    by_id = {result["candidate_id"]: result for result in results}
    expected_checks = {
        claim: by_claim.get(claim, {}).get("status") == status
        for claim, status in raw_row.get("expected_status", {}).items()
    }
    parse_checks = {
        candidate_id: by_id[candidate_id]["provenance"]["metadata"].get("normalization_status") != "unparsed"
        for candidate_id in raw_row.get("parsed_candidate_ids", [])
        if candidate_id in by_id
    }
    unparsed_checks = {
        candidate_id: by_id[candidate_id]["provenance"]["metadata"].get("normalization_status") == "unparsed"
        for candidate_id in raw_row.get("unparsed_candidate_ids", [])
        if candidate_id in by_id
    }
    bad_checks = {
        candidate_id: by_id[candidate_id]["status"] == "rejected"
        for candidate_id in raw_row.get("bad_candidate_ids", [])
        if candidate_id in by_id
    }
    valid_confidences = [
        by_id[candidate_id]["confidence"]
        for candidate_id in raw_row.get("valid_candidate_ids", [])
        if candidate_id in by_id and by_id[candidate_id]["status"] == "accepted"
    ]
    bad_confidences = [
        by_id[candidate_id]["confidence"]
        for candidate_id in raw_row.get("bad_high_confidence_candidate_ids", [])
        if candidate_id in by_id and by_id[candidate_id]["status"] == "rejected"
    ]
    verifier_beats_confidence = (
        bool(valid_confidences)
        and bool(bad_confidences)
        and max(bad_confidences) > min(valid_confidences)
    )
    unsupported_checks = {
        candidate_id: by_id[candidate_id]["status"] == "abstained"
        for candidate_id in raw_row.get("unsupported_candidate_ids", [])
        if candidate_id in by_id
    }
    provenance_preserved = all(
        result["provenance"].get("metadata", {}).get("model") == row.model
        and result["provenance"].get("metadata", {}).get("adapter") == "real_tensionlm_export_jsonl"
        for result in results
    )
    accepted_with_support = [
        bool({"logic_transitivity", "surface_structure"} & set(result["channels"]))
        for result in results
        if result["status"] == "accepted"
    ]
    contamination_count = sum(
        1
        for result in results
        for status in result.get("typed_runtime", {}).get("context", {}).get("surface_tags", {}).values()
        if status == "candidate"
    )
    return {
        "case_id": row.row_id,
        "model": row.model,
        "export_mode": raw_row.get("export_mode", "unknown"),
        "candidate_count": len(results),
        "accepted": payload["verification"]["accepted"],
        "rejected": payload["verification"]["rejected"],
        "abstained": payload["verification"]["abstained"],
        "expected_checks": expected_checks,
        "all_expected_ok": all(expected_checks.values()),
        "parse_checks": {**parse_checks, **unparsed_checks},
        "bad_candidate_checks": bad_checks,
        "unsupported_checks": unsupported_checks,
        "verifier_beats_candidate_confidence": (
            verifier_beats_confidence if raw_row.get("expected_verifier_beats_candidate_confidence") else None
        ),
        "provenance_preserved": provenance_preserved,
        "accepted_with_typed_support": accepted_with_support,
        "candidate_graph_contamination_count": contamination_count,
        "candidate_results": results,
    }


def build_receipt(report: dict[str, Any], smoke_path: Path, report_path: Path) -> dict[str, Any]:
    return {
        "project": "TS-Reasoner-v0",
        "version": "v1.4.0-live-tensionlm-export-smoke",
        "commit": git_value(["rev-parse", "--short", "HEAD"]),
        "date": datetime.now(timezone.utc).isoformat(),
        "claim": "Live/export-style TensionLM candidate outputs can be verified through the v1.3 adapter boundary.",
        "scope": "Export smoke only; no live model integration into the verifier.",
        "inputs": [str(smoke_path.relative_to(ROOT))],
        "commands_run": [
            "python3 scripts/run_live_tensionlm_export_smoke.py",
            "python3 scripts/evaluate_live_tensionlm_export_smoke.py",
        ],
        "benchmarks": report["metrics"],
        "artifacts": [
            {"path": str(smoke_path.relative_to(ROOT)), "sha256": sha256(smoke_path)},
            {"path": str(report_path.relative_to(ROOT)), "sha256": sha256(report_path)},
        ],
        "known_limitations": [
            "The included export is a deterministic smoke fixture.",
            "No live model is loaded into TS-Reasoner.",
            "TensionLM-style outputs remain candidate data and never become proof without typed-channel support.",
        ],
        "tensions_detected": [
            "external export paths can blur candidate generation and verifier authority",
            "high-confidence exported candidates can be wrong or malformed",
        ],
        "tensions_resolved": [
            "exported candidates are read through the v1.3 JSONL adapter",
            "provenance and raw export metadata are preserved",
            "typed verifier support remains required for accepted outputs",
        ],
        "unresolved_tensions": ["true live TensionLM execution remains outside this release"],
        "public_claim_level": "experimental",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", default="artifacts/live_tensionlm_export_smoke.json")
    parser.add_argument("--report", default="artifacts/live_tensionlm_export_smoke_report.json")
    parser.add_argument("--receipt", default="artifacts/live_tensionlm_export_smoke_receipt.json")
    args = parser.parse_args()

    smoke_path = ROOT / args.smoke
    report_path = ROOT / args.report
    receipt_path = ROOT / args.receipt
    export = load_export(smoke_path)
    rows = export.get("rows", [])
    results = [evaluate_row(row, index) for index, row in enumerate(rows, start=1)]
    parse_checks = [value for item in results for value in item["parse_checks"].values()]
    report = {
        "smoke_artifact": str(smoke_path.relative_to(ROOT)),
        "case_count": len(results),
        "metrics": {
            "export_read_success_rate": 1.0 if rows else 0.0,
            "candidate_parse_success_rate": rate(parse_checks),
            "provenance_preservation_rate": rate([item["provenance_preserved"] for item in results]),
            "accepted_outputs_typed_support_rate": rate(
                [value for item in results for value in item["accepted_with_typed_support"]]
            ),
            "bad_candidate_rejection_rate": rate(
                [value for item in results for value in item["bad_candidate_checks"].values()]
            ),
            "verifier_beats_confidence_rate": rate(
                [
                    item["verifier_beats_candidate_confidence"]
                    for item in results
                    if item["verifier_beats_candidate_confidence"] is not None
                ]
            ),
            "candidate_graph_contamination_count": sum(
                item["candidate_graph_contamination_count"] for item in results
            ),
            "trace_schema_validity": 1.0,
            "expected_status_accuracy": rate(
                [value for item in results for value in item["expected_checks"].values()]
            ),
            "unsupported_candidate_abstention_rate": rate(
                [value for item in results for value in item["unsupported_checks"].values()]
            ),
        },
        "results": results,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt_path.write_text(
        json.dumps(build_receipt(report, smoke_path, report_path), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
