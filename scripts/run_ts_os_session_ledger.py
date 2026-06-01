from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_agl.os import TSOSSessionLedger, load_or_create_session


DEFAULT_COMMANDS = [
    "help",
    "route: is the repo clean?",
    "inspect project and stage next safe note",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the v23 persistent TS-OS session ledger.")
    parser.add_argument("text", nargs="*", help="Optional shell command. If omitted, runs the default session demo.")
    parser.add_argument("--session", default="artifacts/ts_os_session_ledger.json")
    parser.add_argument("--receipt", default="artifacts/ts_os_session_ledger_receipt.json")
    parser.add_argument("--reset", action="store_true", help="Start a fresh session even if the session file exists.")
    args = parser.parse_args()

    session_path = Path(args.session)
    if args.reset or not session_path.exists():
        ledger = TSOSSessionLedger.new(seed=str(session_path))
    else:
        ledger = load_or_create_session(session_path, seed=str(session_path))

    commands = [" ".join(args.text).strip()] if args.text else DEFAULT_COMMANDS
    commands = [command for command in commands if command]

    for command in commands:
        ledger.append_shell_command(command)

    ledger.save(session_path)
    summary = ledger.replay_summary()

    receipt = {
        "artifact": "ts_os_session_ledger_receipt",
        "session_path": str(session_path),
        "session_id": ledger.session_id,
        "event_count": summary["event_count"],
        "mode_counts": summary["mode_counts"],
        "can_resume": summary["can_resume"],
        "external_llm_used": summary["external_llm_used"],
        "external_side_effect_performed": summary["external_side_effect_performed"],
        "candidate_graph_contamination_count": summary["candidate_graph_contamination_count"],
        "all_gates_passed": summary["all_gates_passed"],
    }

    receipt_path = Path(args.receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
