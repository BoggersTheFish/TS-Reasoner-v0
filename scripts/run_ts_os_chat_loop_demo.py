#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_agl.os.chat_loop import FIRST_CONTACT_SCRIPT, run_first_contact_chat_demo


def main() -> int:
    session = run_first_contact_chat_demo(FIRST_CONTACT_SCRIPT)
    payload = session.to_dict()
    demo = {
        "artifact": "ts_os_chat_loop_demo",
        "inputs": FIRST_CONTACT_SCRIPT,
        "rendered_replies": [turn.rendered_reply for turn in session.turns],
        "receipt": payload,
        "all_gates_passed": payload["all_gates_passed"],
    }
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/ts_os_chat_loop_demo.json").write_text(
        json.dumps(demo, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path("artifacts/ts_os_chat_loop_receipt.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for line in demo["rendered_replies"]:
        print(line)
    return 0 if payload["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
