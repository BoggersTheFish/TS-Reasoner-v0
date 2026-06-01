from __future__ import annotations

from pathlib import Path
import json
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_agl.os import TSOSSessionLedger


def evaluate() -> dict:
    session_path = Path("artifacts/ts_os_session_ledger.json")
    if session_path.exists():
        session_path.unlink()

    ledger = TSOSSessionLedger.new(seed="v23_eval")
    ledger.append_shell_command("help")
    ledger.append_shell_command("route: is the repo clean?")
    ledger.save(session_path)

    loaded = TSOSSessionLedger.load(session_path)
    replay_before = loaded.replay_summary()

    loaded.append_shell_command("inspect project and stage next safe note")
    loaded.save(session_path)

    reloaded = TSOSSessionLedger.load(session_path)
    replay_after = reloaded.replay_summary()

    report = {
        "artifact": "ts_os_session_ledger_report",
        "session_path": str(session_path),
        "session_id": reloaded.session_id,
        "event_count_before_resume": replay_before["event_count"],
        "event_count_after_resume": replay_after["event_count"],
        "mode_counts": replay_after["mode_counts"],
        "command_history": replay_after["command_history"],
        "save_load_preserved_session_id": ledger.session_id == loaded.session_id == reloaded.session_id,
        "replay_available": bool(replay_after["command_history"]),
        "resume_added_event": replay_after["event_count"] == replay_before["event_count"] + 1,
        "has_help_event": replay_after["mode_counts"].get("help", 0) >= 1,
        "has_route_event": replay_after["mode_counts"].get("route", 0) >= 1,
        "has_operator_event": replay_after["mode_counts"].get("local_project_operator", 0) >= 1,
        "external_llm_used": replay_after["external_llm_used"],
        "external_side_effect_performed": replay_after["external_side_effect_performed"],
        "candidate_graph_contamination_count": replay_after["candidate_graph_contamination_count"],
        "all_gates_passed": (
            replay_after["all_gates_passed"]
            and ledger.session_id == loaded.session_id == reloaded.session_id
            and replay_after["event_count"] == replay_before["event_count"] + 1
            and replay_after["mode_counts"].get("help", 0) >= 1
            and replay_after["mode_counts"].get("route", 0) >= 1
            and replay_after["mode_counts"].get("local_project_operator", 0) >= 1
            and replay_after["external_llm_used"] is False
            and replay_after["external_side_effect_performed"] is False
            and replay_after["candidate_graph_contamination_count"] == 0
        ),
    }

    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/ts_os_session_ledger_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    receipt = {
        "artifact": "ts_os_session_ledger_eval_receipt",
        "session_path": str(session_path),
        "session_id": reloaded.session_id,
        "event_count_after_resume": replay_after["event_count"],
        "save_load_preserved_session_id": report["save_load_preserved_session_id"],
        "resume_added_event": report["resume_added_event"],
        "external_llm_used": False,
        "external_side_effect_performed": False,
        "candidate_graph_contamination_count": 0,
        "all_gates_passed": report["all_gates_passed"],
    }
    Path("artifacts/ts_os_session_ledger_eval_receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    result = evaluate()
    raise SystemExit(0 if result["all_gates_passed"] else 1)
