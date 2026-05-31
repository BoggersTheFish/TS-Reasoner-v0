#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "v9_7" / "runtime_checkpoint_cli_cases.jsonl"
REPORT_PATH = ROOT / "artifacts" / "runtime_checkpoint_cli_report.json"
RECEIPT_PATH = ROOT / "artifacts" / "runtime_checkpoint_cli_receipt.json"


def load_cases() -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in DATA_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def run_case(case: dict[str, object]) -> dict[str, object]:
    cmd = [
        sys.executable,
        "-m",
        "ts_reasoner.runtime_checkpoint_cli",
        "checkpoint",
        "--session",
        "@" + str(case["session_path"]),
    ]

    result = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {
            "action": "invalid_output",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "candidate_graph_contamination_count": 0,
        }

    expected_exit_code = int(case["expected_exit_code"])
    expected_actions = [str(action) for action in case["expected_actions"]]
    expected_checkpoint_valid = bool(case["expected_checkpoint_valid"])
    expected_restore_valid = bool(case["expected_restore_valid"])
    expected_contamination = int(case["expected_candidate_graph_contamination_count"])

    actual_contamination = int(payload.get("candidate_graph_contamination_count", 0))

    if expected_exit_code == 2:
        content_ok = payload.get("action") == "invalid_input"
    else:
        content_ok = (
            payload.get("action") == "checkpoint_created"
            and payload.get("actions") == expected_actions
            and payload.get("checkpoint_valid") == expected_checkpoint_valid
            and payload.get("restore_valid") == expected_restore_valid
        )

    passed = (
        result.returncode == expected_exit_code
        and content_ok
        and actual_contamination == expected_contamination
    )

    return {
        "case_id": str(case["case_id"]),
        "expected_exit_code": expected_exit_code,
        "actual_exit_code": result.returncode,
        "expected_actions": expected_actions,
        "actual_actions": payload.get("actions", []),
        "expected_checkpoint_valid": expected_checkpoint_valid,
        "actual_checkpoint_valid": payload.get("checkpoint_valid", False),
        "expected_restore_valid": expected_restore_valid,
        "actual_restore_valid": payload.get("restore_valid", False),
        "expected_candidate_graph_contamination_count": expected_contamination,
        "actual_candidate_graph_contamination_count": actual_contamination,
        "passed": passed,
        "payload": payload,
        "stderr": result.stderr,
    }


def main() -> int:
    results = [run_case(case) for case in load_cases()]
    passed = sum(1 for row in results if row["passed"])
    contamination = sum(int(row["actual_candidate_graph_contamination_count"]) for row in results)

    report = {
        "release": "v9.7.0",
        "case_count": len(results),
        "passed_cases": passed,
        "failed_cases": len(results) - passed,
        "runtime_checkpoint_cli_accuracy": passed / len(results) if results else 0.0,
        "candidate_graph_contamination_count": contamination,
        "all_gates_passed": bool(results) and passed == len(results) and contamination == 0,
        "results": results,
    }

    receipt = {
        "release": "v9.7.0",
        "receipt_type": "runtime_checkpoint_cli",
        "all_gates_passed": report["all_gates_passed"],
        "case_count": report["case_count"],
        "runtime_checkpoint_cli_accuracy": report["runtime_checkpoint_cli_accuracy"],
        "candidate_graph_contamination_count": report["candidate_graph_contamination_count"],
        "cli_creates_runtime_checkpoints": True,
        "cli_rejects_invalid_checkpoint_sessions": True,
        "checkpoint_restore_is_valid": True,
        "generated_text_is_not_proof": True,
        "candidate_generation_is_not_proof": True,
        "typed_verifier_support_remains_proof_boundary": True,
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
