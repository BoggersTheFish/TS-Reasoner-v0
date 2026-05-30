#!/usr/bin/env python3
"""Evaluate TS-Chat v0.8 suggestion confirmations."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_reasoner.ts_chat_suggestion_confirmation import (
    evaluate_suggestion_confirmations,
    load_confirmations_jsonl,
)


CONFIRMATIONS_PATH = Path("data/ts_chat_suggestion_confirmations_v0_8.jsonl")
REPORT_PATH = Path("artifacts/ts_chat_v0_8_suggestion_confirmation_eval_report.json")


def main() -> None:
    confirmations = load_confirmations_jsonl(CONFIRMATIONS_PATH)
    metrics = evaluate_suggestion_confirmations(confirmations)

    report = {
        "release": "v5.8.0",
        "name": "TS-Chat Suggestion Confirmation Evaluation",
        "confirmations_path": str(CONFIRMATIONS_PATH),
        "metrics": metrics,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(metrics, indent=2, sort_keys=True))

    if not metrics["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
