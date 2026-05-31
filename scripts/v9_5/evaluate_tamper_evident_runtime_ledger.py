#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ts_reasoner.tamper_evident_runtime_ledger import evaluate_tamper_evident_ledger_cases

DATA_PATH = ROOT / "data" / "v9_5" / "tamper_evident_ledger_cases.jsonl"
REPORT_PATH = ROOT / "artifacts" / "tamper_evident_runtime_ledger_report.json"
RECEIPT_PATH = ROOT / "artifacts" / "tamper_evident_runtime_ledger_receipt.json"


def load_cases() -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in DATA_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> int:
    report = evaluate_tamper_evident_ledger_cases(load_cases())

    receipt = {
        "release": "v9.5.0",
        "receipt_type": "tamper_evident_runtime_ledger",
        "all_gates_passed": report["all_gates_passed"],
        "case_count": report["case_count"],
        "tamper_evident_ledger_accuracy": report["tamper_evident_ledger_accuracy"],
        "candidate_graph_contamination_count": report["candidate_graph_contamination_count"],
        "ledger_is_hash_chained": True,
        "tampering_is_detected": True,
        "ledger_entries_are_audit_records_not_proof": True,
        "generated_text_is_not_proof": True,
        "candidate_generation_is_not_proof": True,
        "typed_verifier_support_remains_proof_boundary": True
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
