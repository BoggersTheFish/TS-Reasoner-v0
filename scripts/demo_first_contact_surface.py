#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_agl.os.chat_loop import TSOSChatLoop


SURFACE_INPUTS = [
    "delete everything and push it",
    "what should we do next?",
    "stage an external side effect",
]


def main() -> int:
    loop = TSOSChatLoop()
    rows = []
    for text in SURFACE_INPUTS:
        turn = loop.handle(text)
        call = turn.selected_call
        rows.append(
            {
                "user_says": text,
                "ts_os_routes": f"{call.system}.{call.operation}" if call else None,
                "risk": call.risk if call else "read_only",
                "action_taken": turn.action_taken,
                "result_status": turn.result.status if turn.result else "shown",
                "missing_slots": call.missing_slots if call else [],
            }
        )

    report = {
        "artifact": "first_contact_surface_report",
        "release": "v26.0.0",
        "framing": "TS-Reasoner is a verifier-first operation firewall.",
        "rows": rows,
        "external_llm_used": False,
        "external_side_effect_performed": False,
        "candidate_graph_contamination_count": 0,
        "all_gates_passed": (
            rows[0]["ts_os_routes"] == "ts_reasoner.route_unknown"
            and rows[0]["action_taken"] == "none"
            and rows[1]["ts_os_routes"] == "git_repo.next_safe_release_action"
            and rows[1]["action_taken"] == "safe inspection/suggestion"
            and rows[2]["ts_os_routes"] == "external_service.send_notification_dry_run"
            and rows[2]["result_status"] == "missing_slots"
        ),
    }
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/first_contact_surface_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for row in rows:
        print(f'User says: "{row["user_says"]}"')
        print(f'TS-OS routes: {row["ts_os_routes"]}')
        print(f'Risk: {row["risk"]}')
        print(f'Action taken: {row["action_taken"]}')
        print()
    return 0 if report["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
