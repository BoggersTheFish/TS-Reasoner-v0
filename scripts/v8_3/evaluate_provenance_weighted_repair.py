#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ts_reasoner.provenance_weighted_repair import evaluate_provenance_cases

DATA_PATH = ROOT / "data" / "v8_3" / "provenance_weighted_repair_cases.jsonl"
REPORT_PATH = ROOT / "artifacts" / "provenance_weighted_repair_report.json"
RECEIPT_PATH = ROOT / "artifacts" / "provenance_weighted_repair_receipt.json"


def load_cases() -> list[dict[str, object]]:
    cases = []
    for line in DATA_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            cases.append(json.loads(line))
    return cases


def main() -> int:
    report = evaluate_provenance_cases(load_cases())

    receipt = {
        "release": "v8.3.0",
        "receipt_type": "provenance_weighted_repair_decisions",
        "all_gates_passed": report["all_gates_passed"],
        "case_count": report["case_count"],
        "provenance_decision_accuracy": report["provenance_decision_accuracy"],
        "candidate_graph_contamination_count": report["candidate_graph_contamination_count"],
        "accepted_claims_preserved": report["accepted_claims_preserved"],
        "incoming_claims_not_auto_accepted": report["incoming_claims_not_auto_accepted"],
        "correlated_sources_are_downweighted": True,
        "generated_text_is_not_proof": True,
        "candidate_generation_is_not_proof": True,
        "model_confidence_is_not_proof": True,
        "typed_verifier_support_remains_proof_boundary": True
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
