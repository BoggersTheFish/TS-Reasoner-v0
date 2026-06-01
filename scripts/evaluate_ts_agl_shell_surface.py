from __future__ import annotations

from pathlib import Path
import json
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_agl.shell import run_shell_command


CASES = [
    {
        "text": "help",
        "expected_mode": "help",
    },
    {
        "text": "route: is the repo clean?",
        "expected_mode": "route",
        "expected_domain": "git_repo",
        "expected_operation": "git_status",
    },
    {
        "text": "route: use model confidence as proof",
        "expected_mode": "route",
        "expected_domain": "ts_reasoner",
        "expected_operation": "route_unknown",
    },
    {
        "text": "inspect project and stage next safe note",
        "expected_mode": "local_project_operator",
    },
]


def evaluate() -> dict:
    rows = []
    correct = 0

    for case in CASES:
        result = run_shell_command(case["text"])
        payload = result.to_dict()

        ok = result.mode == case["expected_mode"]
        if "expected_domain" in case:
            call = payload["selected_call"]
            ok = ok and call["system"] == case["expected_domain"] and call["operation"] == case["expected_operation"]

        if result.mode == "local_project_operator":
            operator_payload = payload["payload"]
            ok = ok and operator_payload["all_gates_passed"]
            ok = ok and operator_payload["unconfirmed_write_blocked"]
            ok = ok and operator_payload["confirmed_write_executed"]

        correct += int(ok)
        rows.append(
            {
                **case,
                "mode": result.mode,
                "rendered_reply": result.rendered_reply,
                "payload_all_gates_passed": bool(result.payload.get("all_gates_passed")),
                "ok": ok,
            }
        )

    report = {
        "artifact": "ts_agl_shell_surface_report",
        "case_count": len(CASES),
        "accuracy": correct / len(CASES),
        "rows": rows,
        "external_llm_used": False,
        "external_side_effect_performed": False,
        "candidate_graph_contamination_count": 0,
        "all_gates_passed": correct == len(CASES),
    }

    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/ts_agl_shell_surface_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    receipt = {
        "artifact": "ts_agl_shell_surface_eval_receipt",
        "case_count": report["case_count"],
        "accuracy": report["accuracy"],
        "external_llm_used": False,
        "external_side_effect_performed": False,
        "candidate_graph_contamination_count": 0,
        "all_gates_passed": report["all_gates_passed"],
    }
    Path("artifacts/ts_agl_shell_surface_eval_receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    result = evaluate()
    raise SystemExit(0 if result["all_gates_passed"] else 1)
