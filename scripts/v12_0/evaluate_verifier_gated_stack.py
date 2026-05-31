from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.proposer_stack import StackConfig, evaluate_stack, write_json, write_jsonl

CONFIG = ROOT / "data" / "v12_0" / "verifier_gated_stack_config.json"
CASES = ROOT / "artifacts" / "v12_0" / "verifier_gated_stack_cases.jsonl"
TRACE = ROOT / "artifacts" / "v12_0" / "verifier_gated_stack_trace.jsonl"
REPORT = ROOT / "artifacts" / "v12_0" / "verifier_gated_stack_report.json"
RECEIPT = ROOT / "artifacts" / "v12_0" / "verifier_gated_stack_receipt.json"


def main() -> None:
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    config = StackConfig(**payload)

    result = evaluate_stack(ROOT, config)
    cases = result["cases"]
    rows = result["rows"]
    report = result["report"]

    write_jsonl(CASES, cases)
    write_jsonl(TRACE, rows)
    write_json(REPORT, report)

    receipt = {
        "receipt_type": "v12_0_verifier_gated_proposer_stack_receipt",
        "release": "v12.0.0",
        "claim": "TS-Reasoner runs paragraph decomposition, trained proposer prediction, verifier gating, and traceable final answers as one end-to-end stack.",
        "train_row_count": report["train_row_count"],
        "case_count": report["case_count"],
        "decomposition_success_rate": report["decomposition_success_rate"],
        "proposer_answer_accuracy": report["proposer_answer_accuracy"],
        "proposer_status_accuracy": report["proposer_status_accuracy"],
        "proposer_channel_accuracy": report["proposer_channel_accuracy"],
        "final_answer_accuracy": report["final_answer_accuracy"],
        "final_status_accuracy": report["final_status_accuracy"],
        "final_channel_accuracy": report["final_channel_accuracy"],
        "raw_wrong_yes_count": report["raw_wrong_yes_count"],
        "final_wrong_accept_count": report["final_wrong_accept_count"],
        "accepted_without_typed_support_count": report["accepted_without_typed_support_count"],
        "candidate_graph_contamination_count": report["candidate_graph_contamination_count"],
        "stack_case_hash": report["stack_case_hash"],
        "stack_result_hash": report["stack_result_hash"],
        "all_gates_passed": report["all_gates_passed"],
    }

    write_json(RECEIPT, receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))

    if not report["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
