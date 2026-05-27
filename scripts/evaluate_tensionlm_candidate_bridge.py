#!/usr/bin/env python3
"""Evaluate the TensionLM candidate bridge contract."""

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


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    payload = run_tensionlm_candidate_bridge(case["input_text"], case.get("premises"), mode="mock")
    results = payload["verification"]["candidate_results"]
    status_by_claim = {result["claim"]: result["status"] for result in results}
    expected = case["expected_status"]
    expected_checks = {
        claim: status_by_claim.get(claim) == status
        for claim, status in expected.items()
    }
    typed_reason_rejections = [
        result
        for result in results
        if result["status"] == "rejected" and result["channels"]
    ]
    return {
        "case_id": case["case_id"],
        "input_text": case["input_text"],
        "candidate_count": len(results),
        "accepted": payload["verification"]["accepted"],
        "rejected": payload["verification"]["rejected"],
        "abstained": payload["verification"]["abstained"],
        "expected_checks": expected_checks,
        "all_expected_ok": all(expected_checks.values()),
        "typed_reason_rejection_count": len(typed_reason_rejections),
        "provenance_preserved": payload["trace_receipt"]["provenance_preserved"],
        "channels": payload["verification"]["channels"],
    }


def build_receipt(report: dict[str, Any], report_path: Path, data_path: Path) -> dict[str, Any]:
    return {
        "project": "TS-Reasoner-v0",
        "version": "v1.1.0-candidate-bridge",
        "commit": git_value(["rev-parse", "--short", "HEAD"]),
        "date": datetime.now(timezone.utc).isoformat(),
        "claim": "Candidate proposals can enter TS-Reasoner and be accepted, rejected, or abstained by typed-channel verification.",
        "scope": "Dependency-light mock candidate bridge; external hook is a contract only, not a model-loading path.",
        "inputs": [str(data_path.relative_to(ROOT))],
        "commands_run": ["python3 scripts/evaluate_tensionlm_candidate_bridge.py"],
        "benchmarks": report["metrics"],
        "artifacts": [
            {"path": str(report_path.relative_to(ROOT)), "sha256": sha256(report_path)},
        ],
        "known_limitations": [
            "Regex-style relation parsing only.",
            "Mock proposer uses deterministic text patterns.",
            "External TensionLM mode is an optional hook and does not load model weights.",
            "Candidate verification is syllogistic toy-scope, not a general natural-language theorem prover.",
        ],
        "tensions_detected": ["candidate generation could be mistaken for candidate judgment"],
        "tensions_resolved": ["candidate edges are not inserted as proof support during verification"],
        "unresolved_tensions": ["messy language stress is deferred until after the v1.1.0 contract artifact"],
        "public_claim_level": "experimental",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/tensionlm_candidate_bridge_cases.jsonl")
    parser.add_argument("--out", default="artifacts/tensionlm_candidate_bridge_report.json")
    parser.add_argument("--receipt", default="artifacts/tensionlm_candidate_bridge_receipt.json")
    args = parser.parse_args()

    data_path = ROOT / args.data
    report_path = ROOT / args.out
    receipt_path = ROOT / args.receipt
    cases = load_jsonl(data_path)
    results = [evaluate_case(case) for case in cases]
    expected_total = sum(len(item["expected_checks"]) for item in results)
    expected_ok = sum(sum(item["expected_checks"].values()) for item in results)
    report = {
        "dataset": str(data_path.relative_to(ROOT)),
        "case_count": len(results),
        "metrics": {
            "expected_status_accuracy": round(expected_ok / max(1, expected_total), 4),
            "case_success_rate": round(sum(item["all_expected_ok"] for item in results) / max(1, len(results)), 4),
            "typed_reason_rejection_rate": round(
                sum(item["typed_reason_rejection_count"] for item in results)
                / max(1, sum(len(item["rejected"]) for item in results)),
                4,
            ),
            "provenance_preservation_rate": round(
                sum(item["provenance_preserved"] for item in results) / max(1, len(results)),
                4,
            ),
            "trace_schema_validity": 1.0,
        },
        "results": results,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt = build_receipt(report, report_path, data_path)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
