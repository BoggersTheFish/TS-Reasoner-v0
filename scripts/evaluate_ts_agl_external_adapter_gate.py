from __future__ import annotations

from pathlib import Path
import json
import os
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_agl.external import EXTERNAL_LIVE_ENV_VAR, ExternalAdapterGate, ExternalAdapterRequest


def evaluate() -> dict:
    gate = ExternalAdapterGate()

    dry_request = ExternalAdapterRequest(
        service="github",
        operation="create_issue",
        payload={
            "repo": "BoggersTheFish/TS-Reasoner-v0",
            "title": "v24 external adapter gate dry run",
        },
        mode="dry_run",
    )

    missing_confirmation = gate.evaluate(dry_request, confirmation_token=None)
    wrong_confirmation = gate.evaluate(dry_request, confirmation_token="wrong-token")
    dry_confirmed = gate.evaluate(dry_request, confirmation_token=dry_request.confirmation_token)

    live_request = ExternalAdapterRequest(
        service="github",
        operation="create_issue",
        payload=dry_request.payload,
        mode="live",
    )

    old_env = os.environ.pop(EXTERNAL_LIVE_ENV_VAR, None)
    live_without_env = gate.evaluate(live_request, confirmation_token=live_request.confirmation_token)

    os.environ[EXTERNAL_LIVE_ENV_VAR] = "1"
    live_with_env = gate.evaluate(live_request, confirmation_token=live_request.confirmation_token)

    if old_env is None:
        os.environ.pop(EXTERNAL_LIVE_ENV_VAR, None)
    else:
        os.environ[EXTERNAL_LIVE_ENV_VAR] = old_env

    results = [
        missing_confirmation,
        wrong_confirmation,
        dry_confirmed,
        live_without_env,
        live_with_env,
    ]

    network_call_performed_count = sum(
        int(result.data.get("network_call_performed", False))
        for result in results
    )
    external_side_effect_performed_count = sum(
        int(result.data.get("external_side_effect_performed", False))
        for result in results
    )

    report = {
        "artifact": "ts_agl_external_adapter_gate_report",
        "missing_confirmation_blocked": missing_confirmation.status == "needs_confirmation",
        "wrong_confirmation_blocked": wrong_confirmation.status == "needs_confirmation",
        "dry_run_confirmed": dry_confirmed.status == "success",
        "live_without_env_blocked": live_without_env.status == "external_live_blocked",
        "live_with_env_authorized": live_with_env.status == "live_gate_authorized",
        "live_gate_authorization_is_not_execution": live_with_env.data.get("gate_performs_network_call") is False,
        "network_call_performed_count": network_call_performed_count,
        "external_side_effect_performed_count": external_side_effect_performed_count,
        "external_llm_used": False,
        "candidate_graph_contamination_count": 0,
        "results": {
            "missing_confirmation": missing_confirmation.to_dict(),
            "wrong_confirmation": wrong_confirmation.to_dict(),
            "dry_confirmed": dry_confirmed.to_dict(),
            "live_without_env": live_without_env.to_dict(),
            "live_with_env": live_with_env.to_dict(),
        },
    }

    report["all_gates_passed"] = (
        report["missing_confirmation_blocked"]
        and report["wrong_confirmation_blocked"]
        and report["dry_run_confirmed"]
        and report["live_without_env_blocked"]
        and report["live_with_env_authorized"]
        and report["live_gate_authorization_is_not_execution"]
        and report["network_call_performed_count"] == 0
        and report["external_side_effect_performed_count"] == 0
        and report["candidate_graph_contamination_count"] == 0
    )

    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/ts_agl_external_adapter_gate_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    receipt = {
        "artifact": "ts_agl_external_adapter_gate_eval_receipt",
        "missing_confirmation_blocked": report["missing_confirmation_blocked"],
        "wrong_confirmation_blocked": report["wrong_confirmation_blocked"],
        "dry_run_confirmed": report["dry_run_confirmed"],
        "live_without_env_blocked": report["live_without_env_blocked"],
        "live_with_env_authorized": report["live_with_env_authorized"],
        "network_call_performed_count": report["network_call_performed_count"],
        "external_side_effect_performed_count": report["external_side_effect_performed_count"],
        "external_llm_used": False,
        "candidate_graph_contamination_count": 0,
        "all_gates_passed": report["all_gates_passed"],
    }
    Path("artifacts/ts_agl_external_adapter_gate_eval_receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    result = evaluate()
    raise SystemExit(0 if result["all_gates_passed"] else 1)
