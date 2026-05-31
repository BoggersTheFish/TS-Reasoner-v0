from __future__ import annotations

from pathlib import Path
import json
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_agl.arena.safe_write_arena import run_safe_write_arena


def evaluate() -> dict:
    arena_result = run_safe_write_arena()
    payload = arena_result.to_dict()

    report = {
        "artifact": "ts_agl_safe_write_arena_report",
        "risk": payload["risk"],
        "requires_confirmation": payload["requires_confirmation"],
        "unconfirmed_blocked": payload["unconfirmed_blocked"],
        "confirmed_executed": payload["confirmed_executed"],
        "write_path": payload["write_path"],
        "write_path_exists": payload["write_path_exists"],
        "wrong_unconfirmed_mutation_count": payload["wrong_unconfirmed_mutation_count"],
        "confirmed_mutation_count": payload["confirmed_mutation_count"],
        "candidate_graph_contamination_count": payload["candidate_graph_contamination_count"],
        "external_llm_used": payload["external_llm_used"],
        "all_gates_passed": payload["all_gates_passed"],
    }

    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/ts_agl_safe_write_arena_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    result = evaluate()
    raise SystemExit(0 if result["all_gates_passed"] else 1)
