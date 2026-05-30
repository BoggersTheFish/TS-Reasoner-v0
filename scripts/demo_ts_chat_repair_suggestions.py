#!/usr/bin/env python3
"""Deterministic TS-Chat v0.7 repair suggestion demo."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_reasoner.ts_chat_repair_curriculum import load_curriculum_jsonl
from ts_reasoner.ts_chat_repair_suggestions import (
    evaluate_repair_suggestions,
    load_suggestions_jsonl,
    suggestions_from_curriculum_entries,
    write_suggestions_jsonl,
)


CURRICULUM_PATH = Path("data/ts_chat_repair_curriculum_v0_6.jsonl")
SUGGESTIONS_PATH = Path("data/ts_chat_repair_suggestions_v0_7.jsonl")
RECEIPT_PATH = Path("artifacts/ts_chat_v0_7_repair_suggestions_demo_receipt.json")


def main() -> None:
    entries = load_curriculum_jsonl(CURRICULUM_PATH)
    suggestions = suggestions_from_curriculum_entries(entries)
    write_suggestions_jsonl(suggestions, SUGGESTIONS_PATH)

    loaded = load_suggestions_jsonl(SUGGESTIONS_PATH)
    metrics = evaluate_repair_suggestions(loaded)

    receipt = {
        "release": "v5.7.0",
        "name": "TS-Chat Repair Suggestions",
        "curriculum_path": str(CURRICULUM_PATH),
        "suggestions_path": str(SUGGESTIONS_PATH),
        "boundary": {
            "general_english_understanding": False,
            "external_llm_used": False,
            "neural_training": False,
            "repair_suggestions_are_proof": False,
            "suggestions_auto_accepted": False,
            "typed_verifier_or_user_confirmation_required": True,
        },
        "metrics": metrics,
    }

    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
