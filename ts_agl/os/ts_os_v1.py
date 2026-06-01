from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List
import argparse
import json
import os

from ts_agl.arena.local_project_operator import run_local_project_operator
from ts_agl.arena.router_stack_arena import RouterStackArena
from ts_agl.external import EXTERNAL_LIVE_ENV_VAR, ExternalAdapterGate, ExternalAdapterRequest
from ts_agl.os.session_ledger import TSOSSessionLedger
from ts_agl.shell import run_shell_command


TS_OS_SESSION_PATH = "artifacts/ts_os_v1_session.json"


@dataclass(frozen=True)
class TSOSV1Result:
    shell_help: Dict[str, Any]
    shell_route: Dict[str, Any]
    router_stack: Dict[str, Any]
    session_summary: Dict[str, Any]
    project_operator: Dict[str, Any]
    external_gate: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        network_call_performed_count = int(
            self.external_gate.get("network_call_performed_count", 0)
        )
        external_side_effect_performed_count = int(
            self.external_gate.get("external_side_effect_performed_count", 0)
        )

        candidate_graph_contamination_count = (
            int(self.shell_help.get("payload", {}).get("candidate_graph_contamination_count", 0))
            + int(self.shell_route.get("payload", {}).get("candidate_graph_contamination_count", 0))
            + int(self.router_stack.get("candidate_graph_contamination_count", 0))
            + int(self.session_summary.get("candidate_graph_contamination_count", 0))
            + int(self.project_operator.get("candidate_graph_contamination_count", 0))
            + int(self.external_gate.get("candidate_graph_contamination_count", 0))
        )

        external_llm_used = (
            bool(self.shell_help.get("payload", {}).get("external_llm_used", False))
            or bool(self.shell_route.get("payload", {}).get("external_llm_used", False))
            or bool(self.router_stack.get("external_llm_used", False))
            or bool(self.session_summary.get("external_llm_used", False))
            or bool(self.project_operator.get("external_llm_used", False))
            or bool(self.external_gate.get("external_llm_used", False))
        )

        all_gates_passed = (
            bool(self.shell_help.get("payload", {}).get("all_gates_passed", False))
            and bool(self.shell_route.get("payload", {}).get("all_gates_passed", False))
            and bool(self.router_stack.get("all_gates_passed", False))
            and bool(self.session_summary.get("all_gates_passed", False))
            and bool(self.project_operator.get("all_gates_passed", False))
            and bool(self.external_gate.get("all_gates_passed", False))
            and network_call_performed_count == 0
            and external_side_effect_performed_count == 0
            and candidate_graph_contamination_count == 0
            and external_llm_used is False
        )

        return {
            "artifact": "ts_os_v1_receipt",
            "release": "v25.0.0",
            "claim": "TS-OS v1 packages shell, sessions, routing, local project operation, external adapter gate, and receipts into one bounded operating layer.",
            "components": {
                "shell_surface": self.shell_help,
                "shell_route": self.shell_route,
                "router_stack": self.router_stack,
                "session_summary": self.session_summary,
                "local_project_operator": self.project_operator,
                "external_adapter_gate": self.external_gate,
            },
            "network_call_performed_count": network_call_performed_count,
            "external_side_effect_performed_count": external_side_effect_performed_count,
            "external_llm_used": external_llm_used,
            "candidate_graph_contamination_count": candidate_graph_contamination_count,
            "language_layer_is_proof_authority": False,
            "router_confidence_is_proof": False,
            "session_replay_is_proof_authority": False,
            "external_gate_authorization_is_execution": False,
            "all_gates_passed": all_gates_passed,
        }


class TSOSV1:
    """Bounded TS-OS v1 package.

    TS-OS v1 is not broad autonomous agency. It is one bounded operating
    surface over the existing TS-AGL stack:

    - shell
    - router stack
    - persistent session ledger
    - local project operator
    - controlled external adapter gate
    - receipts
    """

    def run_shell_help(self) -> Dict[str, Any]:
        return run_shell_command("help").to_dict()

    def run_shell_route(self) -> Dict[str, Any]:
        return run_shell_command("route: is the repo clean?").to_dict()

    def run_router_stack(self) -> Dict[str, Any]:
        return RouterStackArena().run_cases()

    def run_session_ledger(self) -> Dict[str, Any]:
        session_path = Path(TS_OS_SESSION_PATH)
        if session_path.exists():
            session_path.unlink()

        ledger = TSOSSessionLedger.new(seed="ts_os_v1")
        ledger.append_shell_command("help")
        ledger.append_shell_command("route: is the repo clean?")
        ledger.append_shell_command("inspect project and stage next safe note")
        ledger.save(session_path)

        loaded = TSOSSessionLedger.load(session_path)
        summary = loaded.replay_summary()
        summary["session_path"] = str(session_path)
        summary["save_load_roundtrip"] = loaded.session_id == ledger.session_id
        summary["all_gates_passed"] = (
            summary["all_gates_passed"]
            and summary["save_load_roundtrip"]
            and summary["event_count"] >= 3
            and summary["mode_counts"].get("help", 0) >= 1
            and summary["mode_counts"].get("route", 0) >= 1
            and summary["mode_counts"].get("local_project_operator", 0) >= 1
        )
        return summary

    def run_project_operator(self) -> Dict[str, Any]:
        return run_local_project_operator().to_dict()

    def run_external_gate(self) -> Dict[str, Any]:
        gate = ExternalAdapterGate()

        dry_request = ExternalAdapterRequest(
            service="github",
            operation="create_issue",
            payload={
                "repo": "BoggersTheFish/TS-Reasoner-v0",
                "title": "TS-OS v1 external gate dry-run check",
            },
            mode="dry_run",
        )
        missing_confirmation = gate.evaluate(dry_request, confirmation_token=None)
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

        results = [missing_confirmation, dry_confirmed, live_without_env, live_with_env]
        network_call_count = sum(int(result.data.get("network_call_performed", False)) for result in results)
        side_effect_count = sum(int(result.data.get("external_side_effect_performed", False)) for result in results)

        return {
            "artifact": "ts_os_v1_external_gate",
            "missing_confirmation_blocked": missing_confirmation.status == "needs_confirmation",
            "dry_run_confirmed": dry_confirmed.status == "success",
            "live_without_env_blocked": live_without_env.status == "external_live_blocked",
            "live_with_env_authorized": live_with_env.status == "live_gate_authorized",
            "live_gate_authorization_is_execution": False,
            "network_call_performed_count": network_call_count,
            "external_side_effect_performed_count": side_effect_count,
            "external_llm_used": False,
            "candidate_graph_contamination_count": 0,
            "all_gates_passed": (
                missing_confirmation.status == "needs_confirmation"
                and dry_confirmed.status == "success"
                and live_without_env.status == "external_live_blocked"
                and live_with_env.status == "live_gate_authorized"
                and network_call_count == 0
                and side_effect_count == 0
            ),
            "results": {
                "missing_confirmation": missing_confirmation.to_dict(),
                "dry_confirmed": dry_confirmed.to_dict(),
                "live_without_env": live_without_env.to_dict(),
                "live_with_env": live_with_env.to_dict(),
            },
        }

    def run(self) -> TSOSV1Result:
        return TSOSV1Result(
            shell_help=self.run_shell_help(),
            shell_route=self.run_shell_route(),
            router_stack=self.run_router_stack(),
            session_summary=self.run_session_ledger(),
            project_operator=self.run_project_operator(),
            external_gate=self.run_external_gate(),
        )


def run_ts_os_v1() -> TSOSV1Result:
    return TSOSV1().run()


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run TS-OS v1 bounded package.")
    parser.add_argument("--receipt", default="artifacts/ts_os_v1_receipt.json")
    args = parser.parse_args(argv)

    result = run_ts_os_v1()
    payload = result.to_dict()

    path = Path(args.receipt)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
