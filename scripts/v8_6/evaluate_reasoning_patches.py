#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ts_reasoner.reasoning_patches import evaluate_reasoning_patch_cases

DATA_PATH = ROOT / "data" / "v8_6" / "reasoning_patch_cases.jsonl"
REPORT_PATH = ROOT / "artifacts" / "reasoning_patches_report.json"
RECEIPT_PATH = ROOT / "artifacts" / "reasoning_patches_receipt.json"


def load_cases() -> list[dict[str, object]]:
    cases = []
    for line in DATA_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            cases.append(json.loads(line))
    return cases


def main() -> int:
    report = evaluate_reasoning_patch_cases(load_cases())

    receipt = {
        "release": "v8.6.0",
        "receipt_type": "reasoning_diff_patch_language",
        "all_gates_passed": report["all_gates_passed"],
        "case_count": report["case_count"],
        "reasoning_patch_accuracy": report["reasoning_patch_accuracy"],
        "candidate_graph_contamination_count": report["candidate_graph_contamination_count"],
        "patches_are_audit_records_not_proof": True,
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
