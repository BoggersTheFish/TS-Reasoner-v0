#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_agl.os.chat_loop import FIRST_CONTACT_SCRIPT, run_first_contact_chat_demo


def evaluate() -> dict:
    session = run_first_contact_chat_demo(FIRST_CONTACT_SCRIPT)
    receipt = session.to_dict()
    metrics = receipt["metrics"]
    report = {
        "artifact": "ts_os_chat_loop_report",
        "release": "v26.0.0",
        **metrics,
        "external_side_effect_performed": receipt["external_side_effect_performed"],
        "all_gates_passed": receipt["all_gates_passed"],
    }
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/ts_os_chat_loop_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path("artifacts/ts_os_chat_loop_receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    result = evaluate()
    raise SystemExit(0 if result["all_gates_passed"] else 1)
