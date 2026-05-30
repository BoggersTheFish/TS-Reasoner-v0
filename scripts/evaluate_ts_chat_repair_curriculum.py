#!/usr/bin/env python3
"""Evaluate TS-Chat v0.6 repair curriculum."""

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
)


DATA_PATH = Path("data/ts_chat_repair_curriculum_v0_6.jsonl")
REPORT_PATH = Path("artifacts/ts_chat_v0_6_repair_curriculum_eval_report.json")


def main() -> None:
    entries = load_curriculum_jsonl(DATA_PATH)
    metrics = evaluate_curriculum_entries(entries)

    report = {
        "release": "v5.6.0",
        "name": "TS-Chat Repair Curriculum Evaluation",
        "curriculum_path": str(DATA_PATH),
        "metrics": metrics,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(metrics, indent=2, sort_keys=True))

    if not metrics["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
