#!/usr/bin/env python3
"""Evaluate TS-Chat v1.0 closed repair loop receipt."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_reasoner.ts_chat_closed_repair_loop import (
    evaluate_closed_repair_loop_receipt,
    load_closed_repair_loop_receipt,
)


RECEIPT_PATH = Path("artifacts/ts_chat_v1_0_closed_repair_loop_receipt.json")
REPORT_PATH = Path("artifacts/ts_chat_v1_0_closed_repair_loop_eval_report.json")


def main() -> None:
    receipt = load_closed_repair_loop_receipt(RECEIPT_PATH)
    metrics = evaluate_closed_repair_loop_receipt(receipt)

    report = {
        "release": "v6.0.0",
        "name": "TS-Chat Closed Repair Loop Evaluation",
        "receipt_path": str(RECEIPT_PATH),
        "metrics": metrics,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(metrics, indent=2, sort_keys=True))

    if not metrics["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
