#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ts_reasoner.runtime_os import evaluate_runtime_os_cases
DATA_PATH = ROOT / "data" / "v10_0" / "runtime_os_cases.jsonl"
REPORT_PATH = ROOT / "artifacts" / "runtime_os_report.json"
RECEIPT_PATH = ROOT / "artifacts" / "runtime_os_receipt.json"


def load_cases() -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in DATA_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> int:
    report = evaluate_runtime_os_cases(load_cases())
    receipt = {
        "release": "v10.0.0",
        "receipt_type": "runtime_os",
        "all_gates_passed": report["all_gates_passed"],
        "case_count": report["case_count"],
        "runtime_os_accuracy": report["runtime_os_accuracy"],
        "candidate_graph_contamination_count": report["candidate_graph_contamination_count"],
        "unified_runtime_session": True,
        "runtime_replay_available": True,
        "tamper_evident_ledger_available": True,
        "checkpoint_restore_available": True,
        "policy_contracts_available": True,
        "recovery_drill_available": True,
        "generated_text_is_not_proof": True,
        "candidate_generation_is_not_proof": True,
        "model_confidence_is_not_proof": True,
        "typed_verifier_support_remains_proof_boundary": True,
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
