#!/usr/bin/env python3
"""Deterministic TS-Chat v0.8 suggestion confirmation demo."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_reasoner.ts_chat_repair_suggestions import load_suggestions_jsonl
from ts_reasoner.ts_chat_suggestion_confirmation import (
    confirm_suggestions_demo_cases,
    evaluate_suggestion_confirmations,
    load_confirmations_jsonl,
    write_confirmations_jsonl,
)


SUGGESTIONS_PATH = Path("data/ts_chat_repair_suggestions_v0_7.jsonl")
CONFIRMATIONS_PATH = Path("data/ts_chat_suggestion_confirmations_v0_8.jsonl")
RECEIPT_PATH = Path("artifacts/ts_chat_v0_8_suggestion_confirmation_demo_receipt.json")


def main() -> None:
    suggestions = load_suggestions_jsonl(SUGGESTIONS_PATH)
    confirmations = confirm_suggestions_demo_cases(suggestions)
    write_confirmations_jsonl(confirmations, CONFIRMATIONS_PATH)

    loaded = load_confirmations_jsonl(CONFIRMATIONS_PATH)
    metrics = evaluate_suggestion_confirmations(loaded)

    receipt = {
        "release": "v5.8.0",
        "name": "TS-Chat Suggestion Confirmation",
        "suggestions_path": str(SUGGESTIONS_PATH),
        "confirmations_path": str(CONFIRMATIONS_PATH),
        "boundary": {
            "general_english_understanding": False,
            "external_llm_used": False,
            "neural_training": False,
            "user_confirmation_is_proof": False,
            "typed_verifier_support_required_for_proof": True,
        },
        "metrics": metrics,
    }

    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
