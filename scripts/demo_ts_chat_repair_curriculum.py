#!/usr/bin/env python3
"""Deterministic TS-Chat v0.6 repair curriculum demo."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_reasoner.ts_chat_repair_curriculum import (
    evaluate_curriculum_entries,
    load_curriculum_jsonl,
    repair_targets_to_curriculum_entries,
    write_curriculum_jsonl,
)


DATA_PATH = Path("data/ts_chat_repair_curriculum_v0_6.jsonl")
RECEIPT_PATH = Path("artifacts/ts_chat_v0_6_repair_curriculum_demo_receipt.json")


def main() -> None:
    session_id = "ts_chat_v0_6_demo_session"

    turn_text_by_id = {
        "turn_001": "are all sparks lanterns?",
        "turn_002": "all sparks are flames. all flames are lanterns.",
        "turn_003": "sparks kinda lantern-vibe sideways??",
    }

    repair_targets = [
        {
            "repair_target_id": "repair_missing_support_001",
            "source_turn_id": "turn_001",
            "repair_type": "missing_support",
            "original_user_text": turn_text_by_id["turn_001"],
            "target_claim_text": "All sparks are lanterns",
            "status": "resolved",
        },
        {
            "repair_target_id": "repair_parse_failure_001",
            "source_turn_id": "turn_003",
            "repair_type": "parse_failure",
            "original_user_text": turn_text_by_id["turn_003"],
            "target_parse_text": "sparks kinda lantern-vibe sideways??",
            "status": "open",
        },
    ]

    entries = repair_targets_to_curriculum_entries(
        session_id=session_id,
        repair_targets=repair_targets,
        turn_text_by_id=turn_text_by_id,
    )
    write_curriculum_jsonl(entries, DATA_PATH)

    loaded_entries = load_curriculum_jsonl(DATA_PATH)
    metrics = evaluate_curriculum_entries(loaded_entries)

    receipt = {
        "release": "v5.6.0",
        "name": "TS-Chat Repair Curriculum",
        "session_id": session_id,
        "curriculum_path": str(DATA_PATH),
        "boundary": {
            "general_english_understanding": False,
            "external_llm_used": False,
            "neural_training": False,
            "curriculum_entries_are_proof": False,
            "typed_verifier_remains_proof_authority": True,
        },
        "metrics": metrics,
    }

    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(receipt["metrics"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
