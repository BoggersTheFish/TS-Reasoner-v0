#!/usr/bin/env python3
"""Evaluate a set of exported TensionLM-side samples through the adapter."""

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


def trace_schema_valid(payload: dict[str, Any]) -> bool:
    verification = payload.get("verification", {})
    return all(
        key in payload
        for key in ("input_text", "premises", "candidate_claims", "verification", "trace_receipt")
    ) and all(
        key in verification
        for key in ("accepted", "rejected", "abstained", "channels", "candidate_results")
    )


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
    parseable_checks = [
        result["provenance"]["metadata"].get("normalization_status") != "unparsed"
        for result in results
    ]
    parse_expectation_checks = {
        candidate_id: by_id[candidate_id]["provenance"]["metadata"].get("normalization_status") != "unparsed"
        for candidate_id in raw.get("parsed_candidate_ids", [])
        if candidate_id in by_id
    }
    parse_expectation_checks.update(
        {
            candidate_id: by_id[candidate_id]["provenance"]["metadata"].get("normalization_status") == "unparsed"
            for candidate_id in raw.get("unparsed_candidate_ids", [])
            if candidate_id in by_id
        }
    )
    bad_checks = {
        candidate_id: by_id[candidate_id]["status"] == "rejected"
        for candidate_id in raw.get("bad_candidate_ids", [])
        if candidate_id in by_id
    }
    unsupported_checks = {
        candidate_id: by_id[candidate_id]["status"] == "abstained"
        for candidate_id in raw.get("unsupported_candidate_ids", [])
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
    )
    provenance_preserved = all(
        result["provenance"].get("metadata", {}).get("model") == row.model
        and result["provenance"].get("metadata", {}).get("adapter") == "real_tensionlm_export_jsonl"
        and result["source"] == "tensionlm_eval_export"
        and result["provenance"].get("raw_output") is not None
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
    failure_reasons = []
    for result in results:
        if result["status"] != "accepted":
            failure_reasons.append(
                {
                    "candidate_id": result["candidate_id"],
                    "claim": result["claim"],
                    "status": result["status"],
                    "reason": result["reason"],
                    "channels": result["channels"],
                    "normalization_status": result["provenance"]["metadata"].get("normalization_status"),
                    "expected_failure_reason": raw.get("expected_failure_reason"),
                }
            )
    return {
        "case_id": row.row_id,
        "model": row.model,
        "source_artifact": raw.get("source_artifact"),
        "source_result_index": raw.get("source_result_index"),
        "source_checkpoint": raw.get("source_checkpoint"),
        "source_prompt": raw.get("source_prompt"),
        "candidate_count": len(results),
        "accepted": payload["verification"]["accepted"],
        "rejected": payload["verification"]["rejected"],
        "abstained": payload["verification"]["abstained"],
        "expected_checks": expected_checks,
        "all_expected_ok": all(expected_checks.values()),
        "parseable_checks": parseable_checks,
        "parse_expectation_checks": parse_expectation_checks,
        "bad_candidate_checks": bad_checks,
        "unsupported_checks": unsupported_checks,
        "verifier_beats_candidate_confidence": (
            verifier_beats_confidence if raw.get("expected_verifier_beats_candidate_confidence") else None
        ),
        "provenance_preserved": provenance_preserved,
        "accepted_with_typed_support": accepted_with_support,
        "candidate_graph_contamination_count": contamination_count,
        "trace_schema_valid": trace_schema_valid(payload),
        "failure_reasons": failure_reasons,
        "candidate_results": results,
    }


def build_receipt(report: dict[str, Any], report_path: Path, data_path: Path) -> dict[str, Any]:
    return {
        "project": "TS-Reasoner-v0",
        "version": "v1.6.0-tensionlm-export-set-evaluation",
        "commit": git_value(["rev-parse", "--short", "HEAD"]),
        "date": datetime.now(timezone.utc).isoformat(),
        "claim": "Multiple real exported TensionLM-side samples can cross into TS-Reasoner while staying contained by typed verification.",
        "scope": "Existing exported JSONL set only; no model loading or training inside TS-Reasoner.",
        "inputs": [str(data_path.relative_to(ROOT))],
        "source_evidence": [
            {
                "repository": "/home/boggersthefish/BoggersSpace/bozo",
                "artifact": "logs/eval/117m_transitivity_seed42.json",
                "checkpoint": "checkpoints/117m-curriculum/pytorch_model.pt",
            }
        ],
        "commands_run": ["python3 scripts/evaluate_tensionlm_export_set.py"],
        "benchmarks": report["metrics"],
        "artifacts": [{"path": str(report_path.relative_to(ROOT)), "sha256": sha256(report_path)}],
        "known_limitations": [
            "Uses existing TensionLM-side eval artifacts rather than running new model samples in this repo.",
            "Export-side normalized claims are evaluated by TS-Reasoner unchanged.",
            "No TensionLM model is loaded into TS-Reasoner.",
            "No training is performed.",
            "The set is small and focused on transitivity-shaped exported samples.",
        ],
        "tensions_detected": [
            "real exported completions include wrong, malformed, contradictory, and unsupported candidates",
            "some correct deeper-chain exported samples exceed the current candidate-bridge support depth",
            "candidate confidence can be higher for bad candidates than for valid candidates",
        ],
        "tensions_resolved": [
            "raw completions are preserved as candidate provenance",
            "typed channels remain the proof authority",
            "candidate graph contamination remains blocked",
            "per-sample failure reasons are preserved in the aggregate report",
        ],
        "unresolved_tensions": ["larger real TensionLM export sets remain future work"],
        "public_claim_level": "experimental",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/tensionlm_export_set_cases.jsonl")
    parser.add_argument("--report", default="artifacts/tensionlm_export_set_report.json")
    parser.add_argument("--receipt", default="artifacts/tensionlm_export_set_receipt.json")
    args = parser.parse_args()

    data_path = ROOT / args.data
    report_path = ROOT / args.report
    receipt_path = ROOT / args.receipt
    rows = load_tensionlm_export_jsonl(data_path)
    results = [evaluate_row(row) for row in rows]
    per_sample_failure_reasons = {
        item["case_id"]: item["failure_reasons"] for item in results if item["failure_reasons"]
    }
    report = {
        "dataset": str(data_path.relative_to(ROOT)),
        "case_count": len(results),
        "metrics": {
            "export_set_read_success_rate": 1.0 if results else 0.0,
            "candidate_parse_success_rate": rate(
                [value for item in results for value in item["parseable_checks"]]
            ),
            "candidate_parse_expectation_rate": rate(
                [value for item in results for value in item["parse_expectation_checks"].values()]
            ),
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
            "trace_schema_validity": rate([item["trace_schema_valid"] for item in results]),
            "expected_status_accuracy": rate(
                [value for item in results for value in item["expected_checks"].values()]
            ),
            "unsupported_candidate_abstention_rate": rate(
                [value for item in results for value in item["unsupported_checks"].values()]
            ),
            "per_sample_failure_reasons": per_sample_failure_reasons,
        },
        "per_sample_failure_reasons": per_sample_failure_reasons,
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
