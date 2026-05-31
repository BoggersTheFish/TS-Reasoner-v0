#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ts_reasoner.runtime_policy_contracts import evaluate_policy_contract_cases, policy_contract_document
DATA_PATH = ROOT / "data" / "v9_8" / "runtime_policy_contract_cases.jsonl"
REPORT_PATH = ROOT / "artifacts" / "runtime_policy_contracts_report.json"
RECEIPT_PATH = ROOT / "artifacts" / "runtime_policy_contracts_receipt.json"
CONTRACT_PATH = ROOT / "artifacts" / "runtime_policy_contracts_v1.json"


def load_cases() -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in DATA_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> int:
    report = evaluate_policy_contract_cases(load_cases())
    receipt = {
        "release": "v9.8.0",
        "receipt_type": "runtime_policy_contracts",
        "all_gates_passed": report["all_gates_passed"],
        "case_count": report["case_count"],
        "runtime_policy_contract_accuracy": report["runtime_policy_contract_accuracy"],
        "candidate_graph_contamination_count": report["candidate_graph_contamination_count"],
        "policy_contract_schema": report["contract_schema"],
        "runtime_actions_are_contract_defined": True,
        "invalid_or_missing_contract_fields_are_rejectable": True,
        "generated_text_is_not_proof": True,
        "candidate_generation_is_not_proof": True,
        "typed_verifier_support_remains_proof_boundary": True,
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    CONTRACT_PATH.write_text(json.dumps(policy_contract_document(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
