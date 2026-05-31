from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ts_reasoner.runtime_os import run_runtime_os_suite, run_runtime_session


def load_json_arg(value: str) -> Any:
    if value.startswith("@"):
        return json.loads(Path(value[1:]).read_text(encoding="utf-8"))
    return json.loads(value)


def run_session_payload(session: Any) -> tuple[int, dict[str, Any]]:
    if not isinstance(session, dict):
        return 2, {
            "action": "invalid_input",
            "error": "session_must_be_json_object",
            "candidate_graph_contamination_count": 0,
        }

    initial_state = session.get("initial_state")
    events = session.get("events")
    if not isinstance(initial_state, dict) or not isinstance(events, list):
        return 2, {
            "action": "invalid_input",
            "error": "initial_state_must_be_object_and_events_must_be_list",
            "candidate_graph_contamination_count": 0,
        }

    if not all(isinstance(event, dict) for event in events):
        return 2, {
            "action": "invalid_input",
            "error": "events_must_be_json_objects",
            "candidate_graph_contamination_count": 0,
        }

    result = run_runtime_session(
        case_id=str(session.get("case_id", "v10_runtime_session")),
        initial_state=initial_state,
        events=events,
    ).to_dict()
    result["action"] = "runtime_session_completed"
    return 0, result


def run_suite_payload(session: Any) -> tuple[int, dict[str, Any]]:
    if not isinstance(session, dict):
        return 2, {
            "action": "invalid_input",
            "error": "session_must_be_json_object",
            "candidate_graph_contamination_count": 0,
        }

    initial_state = session.get("initial_state")
    events = session.get("events")
    continuation_events = session.get("continuation_events", [])
    if (
        not isinstance(initial_state, dict)
        or not isinstance(events, list)
        or not isinstance(continuation_events, list)
    ):
        return 2, {
            "action": "invalid_input",
            "error": "initial_state_must_be_object_and_events_must_be_lists",
            "candidate_graph_contamination_count": 0,
        }

    if not all(isinstance(event, dict) for event in [*events, *continuation_events]):
        return 2, {
            "action": "invalid_input",
            "error": "events_must_be_json_objects",
            "candidate_graph_contamination_count": 0,
        }

    result = run_runtime_os_suite(
        case_id=str(session.get("case_id", "v10_runtime_os")),
        initial_state=initial_state,
        events=events,
        continuation_events=continuation_events,
    )
    result["action"] = "runtime_os_suite_completed"
    return 0, result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ts-runtime-os")
    sub = parser.add_subparsers(dest="command", required=True)

    session = sub.add_parser("session")
    session.add_argument("--session", required=True)

    suite = sub.add_parser("suite")
    suite.add_argument("--session", required=True)

    args = parser.parse_args(argv)

    try:
        payload = load_json_arg(args.session)
    except Exception as exc:
        print(json.dumps({
            "action": "invalid_input",
            "error": str(exc),
            "candidate_graph_contamination_count": 0,
        }, sort_keys=True))
        return 2

    if args.command == "session":
        exit_code, output = run_session_payload(payload)
    else:
        exit_code, output = run_suite_payload(payload)

    print(json.dumps(output, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
