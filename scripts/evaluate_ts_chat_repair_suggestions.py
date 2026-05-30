#!/usr/bin/env python3
"""Evaluate TS-Chat v0.7 repair suggestions."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_reasoner.ts_chat_repair_suggestions import (
    evaluate_repair_suggestions,
    load_suggestions_jsonl,
)


SUGGESTIONS_PATH = Path("data/ts_chat_repair_suggestions_v0_7.jsonl")
REPORT_PATH = Path("artifacts/ts_chat_v0_7_repair_suggestions_eval_report.json")


def main() -> None:
    suggestions = load_suggestions_jsonl(SUGGESTIONS_PATH)
    metrics = evaluate_repair_suggestions(suggestions)

    report = {
        "release": "v5.7.0",
        "name": "TS-Chat Repair Suggestions Evaluation",
        "suggestions_path": str(SUGGESTIONS_PATH),
        "metrics": metrics,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(metrics, indent=2, sort_keys=True))

    if not metrics["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
