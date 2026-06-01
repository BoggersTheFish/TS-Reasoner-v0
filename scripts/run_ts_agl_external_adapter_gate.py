from __future__ import annotations

from pathlib import Path
import argparse
import json
import os
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_agl.external import EXTERNAL_LIVE_ENV_VAR, ExternalAdapterGate, ExternalAdapterRequest


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the v24 controlled external adapter gate.")
    parser.add_argument("--receipt", default="artifacts/ts_agl_external_adapter_gate_receipt.json")
    args = parser.parse_args()

    gate = ExternalAdapterGate()
    request = ExternalAdapterRequest(
        service="github",
        operation="create_issue",
        payload={
            "repo": "BoggersTheFish/TS-Reasoner-v0",
            "title": "dry-run external adapter gate test",
        },
        mode="dry_run",
    )

    blocked = gate.evaluate(request, confirmation_token=None)
    confirmed = gate.evaluate(request, confirmation_token=request.confirmation_token)

    live_request = ExternalAdapterRequest(
        service="github",
        operation="create_issue",
        payload=request.payload,
        mode="live",
    )
    old_env = os.environ.pop(EXTERNAL_LIVE_ENV_VAR, None)
    live_blocked = gate.evaluate(live_request, confirmation_token=live_request.confirmation_token)
    if old_env is not None:
        os.environ[EXTERNAL_LIVE_ENV_VAR] = old_env

    payload = {
        "artifact": "ts_agl_external_adapter_gate_receipt",
        "blocked_without_confirmation": blocked.status == "needs_confirmation",
        "dry_run_confirmed": confirmed.status == "success",
        "live_without_env_blocked": live_blocked.status == "external_live_blocked",
        "network_call_performed_count": int(blocked.data.get("network_call_performed", False))
        + int(confirmed.data.get("network_call_performed", False))
        + int(live_blocked.data.get("network_call_performed", False)),
        "external_side_effect_performed_count": int(blocked.data.get("external_side_effect_performed", False))
        + int(confirmed.data.get("external_side_effect_performed", False))
        + int(live_blocked.data.get("external_side_effect_performed", False)),
        "external_llm_used": False,
        "candidate_graph_contamination_count": 0,
        "results": {
            "blocked": blocked.to_dict(),
            "confirmed": confirmed.to_dict(),
            "live_blocked": live_blocked.to_dict(),
        },
    }
    payload["all_gates_passed"] = (
        payload["blocked_without_confirmation"]
        and payload["dry_run_confirmed"]
        and payload["live_without_env_blocked"]
        and payload["network_call_performed_count"] == 0
        and payload["external_side_effect_performed_count"] == 0
    )

    path = Path(args.receipt)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
