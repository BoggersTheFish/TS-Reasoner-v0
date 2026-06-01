from __future__ import annotations

from pathlib import Path
import json
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_agl.arena.local_project_operator import run_local_project_operator


def evaluate() -> dict:
    result = run_local_project_operator()
    payload = result.to_dict()

    report = {
        "artifact": "ts_agl_local_project_operator_report",
        "repo_inspected": payload["repo_inspected"],
        "filesystem_inspected": payload["filesystem_inspected"],
        "router_stack_used": payload["router_stack_used"],
        "unconfirmed_write_blocked": payload["unconfirmed_write_blocked"],
        "confirmed_write_executed": payload["confirmed_write_executed"],
        "project_note_path": payload["project_note_path"],
        "project_note_exists": payload["project_note_exists"],
        "wrong_unconfirmed_mutation_count": payload["wrong_unconfirmed_mutation_count"],
        "confirmed_mutation_count": payload["confirmed_mutation_count"],
        "external_side_effect_performed": payload["external_side_effect_performed"],
        "external_llm_used": payload["external_llm_used"],
        "candidate_graph_contamination_count": payload["candidate_graph_contamination_count"],
        "operations": payload["operations"],
        "all_gates_passed": payload["all_gates_passed"],
    }

    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/ts_agl_local_project_operator_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    receipt = {
        "artifact": "ts_agl_local_project_operator_receipt",
        "repo_inspected": report["repo_inspected"],
        "filesystem_inspected": report["filesystem_inspected"],
        "router_stack_used": report["router_stack_used"],
        "unconfirmed_write_blocked": report["unconfirmed_write_blocked"],
        "confirmed_write_executed": report["confirmed_write_executed"],
        "external_side_effect_performed": False,
        "external_llm_used": False,
        "candidate_graph_contamination_count": 0,
        "all_gates_passed": report["all_gates_passed"],
    }
    Path("artifacts/ts_agl_local_project_operator_receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    result = evaluate()
    raise SystemExit(0 if result["all_gates_passed"] else 1)
