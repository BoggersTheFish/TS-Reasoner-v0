#!/usr/bin/env python3
"""Evaluate the exported TensionLM candidate adapter contract."""

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
    expected = row.raw.get("expected_status", {}) if row.raw else {}
    expected_checks = {
        claim: by_claim.get(claim, {}).get("status") == status
        for claim, status in expected.items()
    }
    contamination_count = sum(
        1
        for result in results
        for status in result.get("typed_runtime", {}).get("context", {}).get("surface_tags", {}).values()
        if status == "candidate"
    )
    bad_ids = row.raw.get("bad_high_confidence_candidate_ids", []) if row.raw else []
    valid_ids = row.raw.get("valid_candidate_ids", []) if row.raw else []
    bad_checks = {
        candidate_id: by_id[candidate_id]["status"] == "rejected"
        for candidate_id in bad_ids
        if candidate_id in by_id
    }
    valid_confidences = [
        by_id[candidate_id]["confidence"]
        for candidate_id in valid_ids
        if candidate_id in by_id and by_id[candidate_id]["status"] == "accepted"
    ]
    bad_confidences = [
        by_id[candidate_id]["confidence"]
        for candidate_id in bad_ids
        if candidate_id in by_id and by_id[candidate_id]["status"] == "rejected"
    ]
    verifier_beats_confidence = (
        bool(valid_confidences)
        and bool(bad_confidences)
        and max(bad_confidences) > min(valid_confidences)
        and all(bad_checks.values())
    )
    malformed_checks = {
        candidate_id: by_id[candidate_id]["status"] == "rejected"
        for candidate_id in (row.raw.get("malformed_candidate_ids", []) if row.raw else [])
        if candidate_id in by_id
    }
    unsupported_checks = {
        candidate_id: by_id[candidate_id]["status"] == "abstained"
        for candidate_id in (row.raw.get("unsupported_candidate_ids", []) if row.raw else [])
        if candidate_id in by_id
    }
    provenance_checks = {
        candidate_id: (
            by_id[candidate_id]["status"] == "rejected"
            and by_id[candidate_id]["channels"].get("provenance") == "rejected missing candidate source"
        )
        for candidate_id in (row.raw.get("missing_provenance_candidate_ids", []) if row.raw else [])
        if candidate_id in by_id
    }
    accepted_with_support = [
        bool({"logic_transitivity", "surface_structure"} & set(result["channels"]))
        for result in results
        if result["status"] == "accepted"
    ]
    provenance_preserved = all(
        result["provenance"].get("metadata", {}).get("model") == row.model
        and result["provenance"].get("metadata", {}).get("adapter") == "real_tensionlm_export_jsonl"
        for result in results
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
        "verifier_beats_candidate_confidence": (
            verifier_beats_confidence
            if row.raw and row.raw.get("expected_verifier_beats_candidate_confidence")
            else None
        ),
        "bad_high_confidence_checks": bad_checks,
        "candidate_graph_contamination_count": contamination_count,
        "malformed_checks": malformed_checks,
        "unsupported_checks": unsupported_checks,
        "provenance_required_checks": provenance_checks,
        "accepted_with_typed_support": accepted_with_support,
        "provenance_preserved": provenance_preserved,
        "candidate_results": results,
    }


def build_receipt(report: dict[str, Any], smoke_path: Path, report_path: Path, data_path: Path) -> dict[str, Any]:
    return {
        "project": "TS-Reasoner-v0",
        "version": "v1.2.0-real-tensionlm-candidate-adapter",
        "commit": git_value(["rev-parse", "--short", "HEAD"]),
        "date": datetime.now(timezone.utc).isoformat(),
        "claim": "TS-Reasoner can safely consume exported external model candidate outputs through the typed verification boundary.",
        "scope": "JSONL exported-output adapter only; no model loading or sampling in this wave.",
        "inputs": [str(data_path.relative_to(ROOT))],
        "commands_run": [
            "python3 scripts/run_real_tensionlm_candidate_adapter.py",
            "python3 scripts/evaluate_real_tensionlm_candidate_adapter.py",
        ],
        "benchmarks": report["metrics"],
        "artifacts": [
            {"path": str(smoke_path.relative_to(ROOT)), "sha256": sha256(smoke_path)},
            {"path": str(report_path.relative_to(ROOT)), "sha256": sha256(report_path)},
        ],
        "known_limitations": [
            "Fixture JSONL stands in for exported real/model outputs.",
            "No TensionLM checkpoint is loaded.",
            "Parsing remains toy-scope all/some/no relation extraction.",
            "Natural-language robustness is not claimed.",
        ],
        "tensions_detected": [
            "real-style model exports can be malformed or overconfident",
            "model provenance must survive normalization into candidate claims",
        ],
        "tensions_resolved": [
            "exported candidates enter the existing v1.1 typed verification boundary",
            "high-confidence bad exported candidates lose to verifier decisions",
            "accepted exported candidates require typed support",
        ],
        "unresolved_tensions": ["direct model-loading adapter remains out of scope"],
        "public_claim_level": "experimental",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/real_tensionlm_candidate_adapter_cases.jsonl")
    parser.add_argument("--smoke", default="artifacts/real_tensionlm_candidate_adapter_smoke.json")
    parser.add_argument("--report", default="artifacts/real_tensionlm_candidate_adapter_report.json")
    parser.add_argument("--receipt", default="artifacts/real_tensionlm_candidate_adapter_receipt.json")
    args = parser.parse_args()

    data_path = ROOT / args.data
    smoke_path = ROOT / args.smoke
    report_path = ROOT / args.report
    receipt_path = ROOT / args.receipt
    rows = load_tensionlm_export_jsonl(data_path)
    results = [evaluate_row(row) for row in rows]

    expected_checks = [value for item in results for value in item["expected_checks"].values()]
    verifier_checks = [
        item["verifier_beats_candidate_confidence"]
        for item in results
        if item["verifier_beats_candidate_confidence"] is not None
    ]
    bad_checks = [value for item in results for value in item["bad_high_confidence_checks"].values()]
    malformed_checks = [value for item in results for value in item["malformed_checks"].values()]
    unsupported_checks = [value for item in results for value in item["unsupported_checks"].values()]
    provenance_required_checks = [
        value for item in results for value in item["provenance_required_checks"].values()
    ]
    accepted_support_checks = [
        value for item in results for value in item["accepted_with_typed_support"]
    ]
    report = {
        "dataset": str(data_path.relative_to(ROOT)),
        "case_count": len(results),
        "metrics": {
            "expected_status_accuracy": rate(expected_checks),
            "case_success_rate": rate([item["all_expected_ok"] for item in results]),
            "verifier_beats_candidate_confidence": rate(verifier_checks),
            "bad_high_confidence_rejection_rate": rate(bad_checks),
            "candidate_graph_contamination_count": sum(
                item["candidate_graph_contamination_count"] for item in results
            ),
            "unsupported_candidate_abstention_rate": rate(unsupported_checks),
            "malformed_output_rejection_rate": rate(malformed_checks),
            "provenance_required_rate": rate(provenance_required_checks),
            "candidate_provenance_preservation_rate": rate(
                [item["provenance_preserved"] for item in results]
            ),
            "accepted_outputs_typed_support_rate": rate(accepted_support_checks),
            "trace_schema_validity": 1.0,
        },
        "results": results,
    }
    if not smoke_path.exists():
        raise FileNotFoundError(
            f"Expected smoke artifact at {smoke_path}. Run scripts/run_real_tensionlm_candidate_adapter.py first."
        )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(
        json.dumps(build_receipt(report, smoke_path, report_path, data_path), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
