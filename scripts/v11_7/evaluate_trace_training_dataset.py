from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.v11_7.build_trace_training_data import (
    TraceDatasetConfig,
    build_trace_rows,
    split_rows,
    summarize_dataset,
    write_jsonl,
)

CONFIG = ROOT / "data" / "v11_7" / "verifier_trace_training_config.json"
TRAIN = ROOT / "artifacts" / "v11_7" / "verifier_trace_train.jsonl"
VALID = ROOT / "artifacts" / "v11_7" / "verifier_trace_valid.jsonl"
TEST = ROOT / "artifacts" / "v11_7" / "verifier_trace_test.jsonl"
SUMMARY = ROOT / "artifacts" / "v11_7" / "verifier_trace_dataset_summary.json"
RECEIPT = ROOT / "artifacts" / "v11_7" / "verifier_trace_dataset_receipt.json"


def main() -> None:
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    config = TraceDatasetConfig(**payload)

    rows = build_trace_rows(config)
    splits = split_rows(rows, config)
    summary = summarize_dataset(splits)

    write_jsonl(TRAIN, splits["train"])
    write_jsonl(VALID, splits["valid"])
    write_jsonl(TEST, splits["test"])
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    receipt = {
        "receipt_type": "v11_7_verifier_trace_dataset_receipt",
        "release": "v11.7.0",
        "claim": "TS-Reasoner generates verifier-labelled training data where labels replay through typed verifier traces.",
        "row_count": summary["row_count"],
        "split_counts": summary["split_counts"],
        "status_counts": summary["status_counts"],
        "label_verifier_replay_rate": summary["label_verifier_replay_rate"],
        "trace_hash_validity": summary["trace_hash_validity"],
        "accepted_without_typed_support_count": summary["accepted_without_typed_support_count"],
        "class_balance_valid": summary["class_balance_valid"],
        "leakage_check_passed": summary["leakage_check_passed"],
        "dataset_hash": summary["dataset_hash"],
        "all_gates_passed": summary["all_gates_passed"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))

    if not summary["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
