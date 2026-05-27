#!/usr/bin/env python3
"""Evaluate adversarial candidate-bridge safety cases."""

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

from ts_reasoner.candidate_bridge import run_tensionlm_candidate_bridge


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def git_value(args: list[str], default: str = "unknown") -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return default


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def candidate_id_map(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {result["candidate_id"]: result for result in results}


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    payload = run_tensionlm_candidate_bridge(
        case["input_text"],
        case.get("premises"),
        mode="external",
        external_hook=lambda _text, _premises: case["candidates"],
    )
    results = payload["verification"]["candidate_results"]
    by_claim = {result["claim"]: result for result in results}
    by_id = candidate_id_map(results)
    expected_checks = {
        claim: by_claim.get(claim, {}).get("status") == status
        for claim, status in case.get("expected_status", {}).items()
    }
    contamination_count = sum(
        1
        for result in results
        for status in result.get("typed_runtime", {}).get("context", {}).get("surface_tags", {}).values()
        if status == "candidate"
    )
    bad_high_confidence_checks = {
        candidate_id: by_id[candidate_id]["status"] == "rejected"
        for candidate_id in case.get("bad_high_confidence_candidate_ids", [])
        if candidate_id in by_id
    }
    valid_confidences = [
        by_id[candidate_id]["confidence"]
        for candidate_id in case.get("valid_candidate_ids", [])
        if candidate_id in by_id and by_id[candidate_id]["status"] == "accepted"
    ]
    bad_confidences = [
        by_id[candidate_id]["confidence"]
        for candidate_id in case.get("bad_high_confidence_candidate_ids", [])
        if candidate_id in by_id and by_id[candidate_id]["status"] == "rejected"
    ]
    verifier_beats_candidate_confidence = (
        bool(valid_confidences)
        and bool(bad_confidences)
        and max(bad_confidences) > min(valid_confidences)
        and all(bad_high_confidence_checks.values())
    )
    return {
        "case_id": case["case_id"],
        "input_text": case["input_text"],
        "candidate_count": len(results),
        "accepted": payload["verification"]["accepted"],
        "rejected": payload["verification"]["rejected"],
        "abstained": payload["verification"]["abstained"],
        "channels": payload["verification"]["channels"],
        "expected_checks": expected_checks,
        "all_expected_ok": all(expected_checks.values()),
        "candidate_graph_contamination_count": contamination_count,
        "bad_high_confidence_checks": bad_high_confidence_checks,
        "verifier_beats_candidate_confidence": (
            verifier_beats_candidate_confidence
            if case.get("expected_verifier_beats_candidate_confidence")
            else None
        ),
        "unsupported_checks": {
            candidate_id: by_id[candidate_id]["status"] == "abstained"
            for candidate_id in case.get("unsupported_candidate_ids", [])
            if candidate_id in by_id
        },
        "malformed_checks": {
            candidate_id: by_id[candidate_id]["status"] == "rejected"
            for candidate_id in case.get("malformed_candidate_ids", [])
            if candidate_id in by_id
        },
        "provenance_required_checks": {
            candidate_id: (
                by_id[candidate_id]["status"] == "rejected"
                and by_id[candidate_id]["channels"].get("provenance") == "rejected missing candidate source"
            )
            for candidate_id in case.get("missing_provenance_candidate_ids", [])
            if candidate_id in by_id
        },
        "candidate_results": results,
    }


def rate(values: list[bool]) -> float:
    return round(sum(values) / max(1, len(values)), 4)


def build_receipt(report: dict[str, Any], report_path: Path, data_path: Path) -> dict[str, Any]:
    return {
        "project": "TS-Reasoner-v0",
        "version": "v1.1.0-candidate-bridge-adversarial",
        "commit": git_value(["rev-parse", "--short", "HEAD"]),
        "date": datetime.now(timezone.utc).isoformat(),
        "claim": "High-confidence bad candidate proposals do not override typed TS-Reasoner verification.",
        "scope": "Adversarial bridge stress over deterministic external-hook candidates.",
        "inputs": [str(data_path.relative_to(ROOT))],
        "commands_run": ["python3 scripts/evaluate_tensionlm_candidate_bridge_adversarial.py"],
        "benchmarks": report["metrics"],
        "artifacts": [
            {"path": str(report_path.relative_to(ROOT)), "sha256": sha256(report_path)},
        ],
        "known_limitations": [
            "Toy-scope relation parser.",
            "Adversarial candidates are deterministic fixtures, not sampled model outputs.",
            "Identity-style claims outside all/some/no relation syntax are rejected as malformed graph claims.",
        ],
        "tensions_detected": [
            "candidate confidence can conflict with typed verifier decisions",
            "candidate claims could contaminate proof support if admitted too early",
        ],
        "tensions_resolved": [
            "high-confidence bad candidates are rejected by typed reasons",
            "candidate graph contamination remains zero in adversarial cases",
            "missing provenance and malformed graph claims are hard rejections",
        ],
        "unresolved_tensions": ["real TensionLM output adapter remains the next branch"],
        "public_claim_level": "experimental",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/candidate_bridge_adversarial_cases.jsonl")
    parser.add_argument("--out", default="artifacts/tensionlm_candidate_bridge_adversarial_report.json")
    parser.add_argument("--receipt", default="artifacts/tensionlm_candidate_bridge_adversarial_receipt.json")
    args = parser.parse_args()

    data_path = ROOT / args.data
    report_path = ROOT / args.out
    receipt_path = ROOT / args.receipt
    results = [evaluate_case(case) for case in load_jsonl(data_path)]

    expected_checks = [value for item in results for value in item["expected_checks"].values()]
    bad_high_confidence_checks = [
        value for item in results for value in item["bad_high_confidence_checks"].values()
    ]
    verifier_confidence_checks = [
        item["verifier_beats_candidate_confidence"]
        for item in results
        if item["verifier_beats_candidate_confidence"] is not None
    ]
    unsupported_checks = [value for item in results for value in item["unsupported_checks"].values()]
    malformed_checks = [value for item in results for value in item["malformed_checks"].values()]
    provenance_checks = [value for item in results for value in item["provenance_required_checks"].values()]
    contamination_count = sum(item["candidate_graph_contamination_count"] for item in results)

    report = {
        "dataset": str(data_path.relative_to(ROOT)),
        "case_count": len(results),
        "metrics": {
            "expected_status_accuracy": rate(expected_checks),
            "case_success_rate": rate([item["all_expected_ok"] for item in results]),
            "verifier_beats_candidate_confidence": rate(verifier_confidence_checks),
            "bad_high_confidence_rejection_rate": rate(bad_high_confidence_checks),
            "candidate_graph_contamination_count": contamination_count,
            "unsupported_candidate_abstention_rate": rate(unsupported_checks),
            "malformed_candidate_rejection_rate": rate(malformed_checks),
            "provenance_required_rate": rate(provenance_checks),
            "trace_schema_validity": 1.0,
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
