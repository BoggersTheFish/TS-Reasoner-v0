#!/usr/bin/env python3
"""Evaluate v1.7 deeper-chain support repair under the candidate boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.tensionlm_adapter import load_tensionlm_export_jsonl, run_tensionlm_export_row


CLAIM_RE = re.compile(r"^(?P<quantifier>All|Some|No)\s+(?P<subject>\S+)\s+are\s+(?P<predicate>\S+)$")


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


def identity_collapse_count(results: list[dict[str, Any]]) -> int:
    count = 0
    for result in results:
        if result["status"] != "accepted":
            continue
        match = CLAIM_RE.match(result["claim"])
        if match and match.group("subject").lower() == match.group("predicate").lower():
            count += 1
    return count


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
    deeper_chain_checks = {
        candidate_id: by_id[candidate_id]["status"] == "accepted"
        and "logic_transitivity" in by_id[candidate_id]["channels"]
        for candidate_id in raw.get("deeper_chain_candidate_ids", [])
        if candidate_id in by_id
    }
    reverse_checks = {
        candidate_id: by_id[candidate_id]["status"] == "rejected"
        and "directionality" in by_id[candidate_id]["channels"]
        for candidate_id in raw.get("wrong_reverse_candidate_ids", [])
        if candidate_id in by_id
    }
    v1_6_repair_checks = {
        candidate_id: raw.get("v1_6_expected_status", {}).get(by_id[candidate_id]["claim"]) == "abstained"
        and by_id[candidate_id]["status"] == "accepted"
        for candidate_id in raw.get("v1_6_failure_candidate_ids", [])
        if candidate_id in by_id
    }
    contamination_count = sum(
        1
        for result in results
        for status in result.get("typed_runtime", {}).get("context", {}).get("surface_tags", {}).values()
        if status == "candidate"
    )
    return {
        "case_id": row.row_id,
        "model": row.model,
        "source_artifact": raw.get("source_artifact"),
        "source_result_index": raw.get("source_result_index"),
        "candidate_count": len(results),
        "accepted": payload["verification"]["accepted"],
        "rejected": payload["verification"]["rejected"],
        "abstained": payload["verification"]["abstained"],
        "expected_checks": expected_checks,
        "deeper_chain_checks": deeper_chain_checks,
        "wrong_reverse_checks": reverse_checks,
        "v1_6_failure_repair_checks": v1_6_repair_checks,
        "identity_collapse_count": identity_collapse_count(results),
        "candidate_graph_contamination_count": contamination_count,
        "trace_schema_valid": trace_schema_valid(payload),
        "candidate_results": results,
    }


def build_receipt(report: dict[str, Any], report_path: Path, data_path: Path) -> dict[str, Any]:
    return {
        "project": "TS-Reasoner-v0",
        "version": "v1.7.0-deeper-chain-support-repair",
        "commit": git_value(["rev-parse", "--short", "HEAD"]),
        "date": datetime.now(timezone.utc).isoformat(),
        "claim": "The v1.6 deeper-chain current-limit candidate is repaired inside the typed verifier boundary.",
        "scope": "Structural verifier repair only; no model loading or training inside TS-Reasoner.",
        "inputs": [str(data_path.relative_to(ROOT))],
        "commands_run": ["python3 scripts/evaluate_deeper_chain_support_repair.py"],
        "benchmarks": report["metrics"],
        "artifacts": [{"path": str(report_path.relative_to(ROOT)), "sha256": sha256(report_path)}],
        "known_limitations": [
            "Repair covers positive all/all deeper-chain support only.",
            "No TensionLM model is loaded into TS-Reasoner.",
            "No training is performed.",
            "Candidate confidence remains metadata, not proof authority.",
        ],
        "tensions_detected": [
            "v1.6 preserved a correct deeper-chain exported candidate as abstained",
            "single-pass transitivity resolution did not close A -> B -> C -> D support",
        ],
        "tensions_resolved": [
            "typed transitivity now closes positive all/all support chains in one verifier pass",
            "wrong reverse candidates remain rejected by directionality",
            "candidate graph contamination remains blocked",
        ],
        "unresolved_tensions": ["non-all quantifier chains remain outside this repair"],
        "public_claim_level": "experimental",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/deeper_chain_support_repair_cases.jsonl")
    parser.add_argument("--report", default="artifacts/deeper_chain_support_repair_report.json")
    parser.add_argument("--receipt", default="artifacts/deeper_chain_support_repair_receipt.json")
    args = parser.parse_args()

    data_path = ROOT / args.data
    report_path = ROOT / args.report
    receipt_path = ROOT / args.receipt
    rows = load_tensionlm_export_jsonl(data_path)
    results = [evaluate_row(row) for row in rows]
    report = {
        "dataset": str(data_path.relative_to(ROOT)),
        "case_count": len(results),
        "metrics": {
            "deeper_chain_acceptance_rate": rate(
                [value for item in results for value in item["deeper_chain_checks"].values()]
            ),
            "wrong_reverse_rejection_rate": rate(
                [value for item in results for value in item["wrong_reverse_checks"].values()]
            ),
            "identity_collapse_count": sum(item["identity_collapse_count"] for item in results),
            "candidate_graph_contamination_count": sum(
                item["candidate_graph_contamination_count"] for item in results
            ),
            "trace_schema_validity": rate([item["trace_schema_valid"] for item in results]),
            "v1_6_failure_repair_rate": rate(
                [value for item in results for value in item["v1_6_failure_repair_checks"].values()]
            ),
            "expected_status_accuracy": rate(
                [value for item in results for value in item["expected_checks"].values()]
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
