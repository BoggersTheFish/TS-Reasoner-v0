from __future__ import annotations

from pathlib import Path
import json
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_agl.os.ts_os_v1 import run_ts_os_v1


def evaluate() -> dict:
    result = run_ts_os_v1()
    payload = result.to_dict()

    report = {
        "artifact": "ts_os_v1_report",
        "release": "v25.0.0",
        "shell_surface_passed": payload["components"]["shell_surface"]["payload"]["all_gates_passed"],
        "shell_route_passed": payload["components"]["shell_route"]["payload"]["all_gates_passed"],
        "router_stack_passed": payload["components"]["router_stack"]["all_gates_passed"],
        "session_ledger_passed": payload["components"]["session_summary"]["all_gates_passed"],
        "local_project_operator_passed": payload["components"]["local_project_operator"]["all_gates_passed"],
        "external_adapter_gate_passed": payload["components"]["external_adapter_gate"]["all_gates_passed"],
        "network_call_performed_count": payload["network_call_performed_count"],
        "external_side_effect_performed_count": payload["external_side_effect_performed_count"],
        "external_llm_used": payload["external_llm_used"],
        "candidate_graph_contamination_count": payload["candidate_graph_contamination_count"],
        "language_layer_is_proof_authority": payload["language_layer_is_proof_authority"],
        "router_confidence_is_proof": payload["router_confidence_is_proof"],
        "session_replay_is_proof_authority": payload["session_replay_is_proof_authority"],
        "external_gate_authorization_is_execution": payload["external_gate_authorization_is_execution"],
        "all_gates_passed": payload["all_gates_passed"],
    }

    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/ts_os_v1_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path("artifacts/ts_os_v1_receipt.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    result = evaluate()
    raise SystemExit(0 if result["all_gates_passed"] else 1)
