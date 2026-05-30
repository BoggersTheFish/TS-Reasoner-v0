#!/usr/bin/env python3
"""Deterministic TS-Chat v0.9 improvement ledger demo."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_reasoner.ts_chat_improvement_ledger import (
    build_improvement_ledger,
    evaluate_improvement_ledger,
    write_improvement_ledger,
)


CURRICULUM_PATH = Path("data/ts_chat_repair_curriculum_v0_6.jsonl")
SUGGESTIONS_PATH = Path("data/ts_chat_repair_suggestions_v0_7.jsonl")
CONFIRMATIONS_PATH = Path("data/ts_chat_suggestion_confirmations_v0_8.jsonl")
LEDGER_PATH = Path("artifacts/ts_chat_v0_9_improvement_ledger.json")
RECEIPT_PATH = Path("artifacts/ts_chat_v0_9_improvement_ledger_demo_receipt.json")


def main() -> None:
    ledger = build_improvement_ledger(
        curriculum_path=CURRICULUM_PATH,
        suggestions_path=SUGGESTIONS_PATH,
        confirmations_path=CONFIRMATIONS_PATH,
    )
    write_improvement_ledger(ledger, LEDGER_PATH)

    metrics = evaluate_improvement_ledger(ledger.to_dict())

    receipt = {
        "release": "v5.9.0",
        "name": "TS-Chat Improvement Ledger",
        "curriculum_path": str(CURRICULUM_PATH),
        "suggestions_path": str(SUGGESTIONS_PATH),
        "confirmations_path": str(CONFIRMATIONS_PATH),
        "ledger_path": str(LEDGER_PATH),
        "boundary": {
            "general_english_understanding": False,
            "external_llm_used": False,
            "neural_training": False,
            "ledger_metrics_are_proof": False,
            "typed_verifier_support_required_for_proof": True,
        },
        "ledger": ledger.to_dict(),
        "metrics": metrics,
    }

    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
