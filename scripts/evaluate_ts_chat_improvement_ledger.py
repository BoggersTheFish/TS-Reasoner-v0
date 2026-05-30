#!/usr/bin/env python3
"""Evaluate TS-Chat v0.9 improvement ledger."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_reasoner.ts_chat_improvement_ledger import (
    evaluate_improvement_ledger,
    load_improvement_ledger,
)


LEDGER_PATH = Path("artifacts/ts_chat_v0_9_improvement_ledger.json")
REPORT_PATH = Path("artifacts/ts_chat_v0_9_improvement_ledger_eval_report.json")


def main() -> None:
    ledger = load_improvement_ledger(LEDGER_PATH)
    metrics = evaluate_improvement_ledger(ledger)

    report = {
        "release": "v5.9.0",
        "name": "TS-Chat Improvement Ledger Evaluation",
        "ledger_path": str(LEDGER_PATH),
        "metrics": metrics,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(metrics, indent=2, sort_keys=True))

    if not metrics["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
