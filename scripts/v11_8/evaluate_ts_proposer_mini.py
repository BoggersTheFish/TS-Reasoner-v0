from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.v11_8.ts_proposer_mini import ProposerMiniConfig, train_and_evaluate, write_json

CONFIG = ROOT / "data" / "v11_8" / "ts_proposer_mini_config.json"
MODEL = ROOT / "artifacts" / "v11_8" / "ts_proposer_mini_model.json"
REPORT = ROOT / "artifacts" / "v11_8" / "ts_proposer_mini_report.json"
RECEIPT = ROOT / "artifacts" / "v11_8" / "ts_proposer_mini_receipt.json"


def main() -> None:
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    config = ProposerMiniConfig(**payload)
    result = train_and_evaluate(ROOT, config)

    model = result["model"]
    report = result["report"]

    write_json(MODEL, model)
    write_json(REPORT, report)

    receipt = {
        "receipt_type": "v11_8_ts_proposer_mini_receipt",
        "release": "v11.8.0",
        "claim": "TS-Proposer-Mini is a tiny stdlib trained proposer baseline over verifier-labelled traces; verifier gating preserves zero wrong accepts.",
        "train_row_count": report["train_row_count"],
        "valid_answer_accuracy": report["valid"]["answer_accuracy"],
        "valid_status_accuracy": report["valid"]["status_accuracy"],
        "valid_channel_accuracy": report["valid"]["channel_accuracy"],
        "test_answer_accuracy": report["test"]["answer_accuracy"],
        "test_status_accuracy": report["test"]["status_accuracy"],
        "test_channel_accuracy": report["test"]["channel_accuracy"],
        "test_gated_answer_accuracy": report["test"]["gated_answer_accuracy"],
        "test_raw_wrong_yes_count": report["test"]["raw_wrong_yes_count"],
        "test_gated_wrong_accept_count": report["test"]["gated_wrong_accept_count"],
        "test_verifier_gate_blocked_wrong_yes_count": report["test"]["verifier_gate_blocked_wrong_yes_count"],
        "test_accepted_without_typed_support_count": report["test"]["accepted_without_typed_support_count"],
        "all_gates_passed": report["all_gates_passed"],
    }
    write_json(RECEIPT, receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))

    if not report["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
