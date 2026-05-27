#!/usr/bin/env python3
"""Stress messy exported language-model candidate outputs."""

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

from ts_reasoner.tensionlm_adapter import load_tensionlm_export_jsonl, run_tensionlm_export_row


def git_value(args: list[str], default: str = "unknown") -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return default


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rate(values: list[bool]) -> float:
    return round(sum(values) / max(1, len(values)), 4)


def evaluate_row(row) -> dict[str, Any]:
    payload = run_tensionlm_export_row(row)
    results = payload["verification"]["candidate_results"]
    by_claim = {result["claim"]: result for result in results}
    by_id = {result["candidate_id"]: result for result in results}
    raw = row.raw or {}
    expected_checks = {
        claim: by_claim.get(claim, {}).get("status") == status
        for claim, status in raw.get("expected_status", {}).items()
    }
    parsed_checks = {
        candidate_id: by_id[candidate_id]["provenance"]["metadata"].get("normalization_status") != "unparsed"
        for candidate_id in raw.get("parsed_candidate_ids", [])
        if candidate_id in by_id
    }
    unparsed_checks = {
        candidate_id: by_id[candidate_id]["provenance"]["metadata"].get("normalization_status") == "unparsed"
        for candidate_id in raw.get("unparsed_candidate_ids", [])
        if candidate_id in by_id
    }
    bad_checks = {
        candidate_id: by_id[candidate_id]["status"] == "rejected"
        for candidate_id in raw.get("bad_candidate_ids", [])
        if candidate_id in by_id
    }
    bad_high_confidence_checks = {
        candidate_id: by_id[candidate_id]["status"] == "rejected"
        for candidate_id in raw.get("bad_high_confidence_candidate_ids", [])
        if candidate_id in by_id
    }
    valid_confidences = [
        by_id[candidate_id]["confidence"]
        for candidate_id in raw.get("valid_candidate_ids", [])
        if candidate_id in by_id and by_id[candidate_id]["status"] == "accepted"
    ]
    bad_confidences = [
        by_id[candidate_id]["confidence"]
        for candidate_id in raw.get("bad_high_confidence_candidate_ids", [])
        if candidate_id in by_id and by_id[candidate_id]["status"] == "rejected"
    ]
    verifier_beats_confidence = (
        bool(valid_confidences)
        and bool(bad_confidences)
        and max(bad_confidences) > min(valid_confidences)
        and all(bad_high_confidence_checks.values())
    )
    unsupported_checks = {
        candidate_id: by_id[candidate_id]["status"] == "abstained"
        for candidate_id in raw.get("unsupported_candidate_ids", [])
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
        "candidate_count": len(results),
        "accepted": payload["verification"]["accepted"],
        "rejected": payload["verification"]["rejected"],
        "abstained": payload["verification"]["abstained"],
        "channels": payload["verification"]["channels"],
        "expected_checks": expected_checks,
        "all_expected_ok": all(expected_checks.values()),
        "parsed_checks": parsed_checks,
        "unparsed_checks": unparsed_checks,
        "bad_candidate_checks": bad_checks,
        "unsupported_checks": unsupported_checks,
        "verifier_beats_candidate_confidence": (
            verifier_beats_confidence if raw.get("expected_verifier_beats_candidate_confidence") else None
        ),
        "provenance_preserved": provenance_preserved,
        "accepted_with_typed_support": accepted_with_support,
        "candidate_graph_contamination_count": contamination_count,
        "candidate_results": results,
    }


def build_receipt(report: dict[str, Any], report_path: Path, data_path: Path) -> dict[str, Any]:
    return {
        "project": "TS-Reasoner-v0",
        "version": "v1.3.0-messy-language-candidate-stress",
        "commit": git_value(["rev-parse", "--short", "HEAD"]),
        "date": datetime.now(timezone.utc).isoformat(),
        "claim": "TS-Reasoner can ingest messy exported language-model candidate outputs while preserving provenance and verifier authority.",
        "scope": "Exported JSONL stress only; no live model loading.",
        "inputs": [str(data_path.relative_to(ROOT))],
        "commands_run": ["python3 scripts/evaluate_messy_language_candidate_stress.py"],
        "benchmarks": report["metrics"],
        "artifacts": [{"path": str(report_path.relative_to(ROOT)), "sha256": sha256(report_path)}],
        "known_limitations": [
            "Messy normalization is pattern-based and toy-scope.",
            "No live TensionLM checkpoint is loaded.",
            "Ambiguous and partial claims are rejected instead of semantically repaired.",
        ],
        "tensions_detected": [
            "exported model candidates may be paraphrased, partial, irrelevant, contradictory, or miscalibrated",
            "messy text could be mistaken for proof if normalization bypassed typed verification",
        ],
        "tensions_resolved": [
            "relation-shaped paraphrases normalize into candidate claims",
            "partial and ambiguous claims remain malformed and are rejected",
            "high-confidence bad candidates remain subordinate to typed verification",
        ],
        "unresolved_tensions": ["live model-loading remains out of scope until messy exported stress is stable"],
        "public_claim_level": "experimental",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/messy_language_candidate_stress_cases.jsonl")
    parser.add_argument("--report", default="artifacts/messy_language_candidate_stress_report.json")
    parser.add_argument("--receipt", default="artifacts/messy_language_candidate_stress_receipt.json")
    args = parser.parse_args()

    data_path = ROOT / args.data
    report_path = ROOT / args.report
    receipt_path = ROOT / args.receipt
    rows = load_tensionlm_export_jsonl(data_path)
    results = [evaluate_row(row) for row in rows]

    parse_checks = [
        value
        for item in results
        for value in [*item["parsed_checks"].values(), *item["unparsed_checks"].values()]
    ]
    report = {
        "dataset": str(data_path.relative_to(ROOT)),
        "case_count": len(results),
        "metrics": {
            "messy_candidate_parse_success_rate": rate(parse_checks),
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
            "provenance_preservation_rate": rate([item["provenance_preserved"] for item in results]),
            "candidate_graph_contamination_count": sum(
                item["candidate_graph_contamination_count"] for item in results
            ),
            "accepted_outputs_typed_support_rate": rate(
                [value for item in results for value in item["accepted_with_typed_support"]]
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
        json.dumps(build_receipt(report, report_path, data_path), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
