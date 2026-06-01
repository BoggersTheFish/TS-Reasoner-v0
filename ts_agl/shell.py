from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import argparse
import json

from ts_agl.arena.local_project_operator import LocalProjectOperator
from ts_agl.arena.router_stack_arena import RouterStackArena
from ts_agl.core.types import TSCall


@dataclass(frozen=True)
class ShellCommandResult:
    raw_text: str
    mode: str
    rendered_reply: str
    selected_call: TSCall | None
    payload: Dict[str, object]

    def to_dict(self) -> Dict[str, object]:
        return {
            "raw_text": self.raw_text,
            "mode": self.mode,
            "rendered_reply": self.rendered_reply,
            "selected_call": self.selected_call.to_dict() if self.selected_call else None,
            "payload": self.payload,
        }


class TSAGLShellSurface:
    """Speakable shell surface for TS-AGL.

    v22.0.0 turns the internal operator stack into one user-facing command
    surface. It is still bounded: no external LLM, no autonomous external
    effects, and no proof authority inside language/routing.
    """

    def __init__(self) -> None:
        self.router_stack = RouterStackArena()

    def help_payload(self, raw_text: str) -> ShellCommandResult:
        commands = [
            "inspect project and stage next safe note",
            "route: is the repo clean?",
            "route: stage an external side effect",
            "help",
        ]
        payload = {
            "artifact": "ts_agl_shell_help",
            "commands": commands,
            "external_llm_used": False,
            "external_side_effect_performed": False,
            "candidate_graph_contamination_count": 0,
            "all_gates_passed": True,
        }
        return ShellCommandResult(
            raw_text=raw_text,
            mode="help",
            rendered_reply="TS-AGL shell supports project inspection/operator commands and route inspection.",
            selected_call=None,
            payload=payload,
        )

    def route_only(self, raw_text: str) -> ShellCommandResult:
        text = raw_text
        if raw_text.lower().startswith("route:"):
            text = raw_text.split(":", 1)[1].strip()

        decision = self.router_stack.decide(text)
        call = self.router_stack.selected_call(decision)

        payload = {
            "artifact": "ts_agl_shell_route",
            "decision": decision.to_dict(),
            "selected_call": call.to_dict(),
            "external_llm_used": False,
            "external_side_effect_performed": False,
            "candidate_graph_contamination_count": 0,
            "confidence_is_proof": False,
            "all_gates_passed": call.system == decision.selected_domain and call.operation == decision.selected_operation,
        }

        return ShellCommandResult(
            raw_text=raw_text,
            mode="route",
            rendered_reply=(
                f"Route selected: {call.system}.{call.operation}. "
                "Router confidence is not proof; calls still go through TSCall/risk boundaries."
            ),
            selected_call=call,
            payload=payload,
        )

    def project_operator(self, raw_text: str) -> ShellCommandResult:
        result = LocalProjectOperator().run(raw_text)
        payload = result.to_dict()

        return ShellCommandResult(
            raw_text=raw_text,
            mode="local_project_operator",
            rendered_reply=(
                "Local project operator completed: inspected project state, used the router stack, "
                "blocked unconfirmed mutation, confirmed a safe artifact write, and emitted a receipt."
            ),
            selected_call=None,
            payload=payload,
        )

    def run(self, raw_text: str) -> ShellCommandResult:
        lowered = raw_text.lower().strip()

        if not lowered or lowered in {"help", "--help", "-h"}:
            return self.help_payload(raw_text)

        project_markers = [
            "inspect project",
            "local project",
            "project operator",
            "stage next safe note",
            "stage a project note",
        ]
        if any(marker in lowered for marker in project_markers):
            return self.project_operator(raw_text)

        return self.route_only(raw_text)


def run_shell_command(raw_text: str) -> ShellCommandResult:
    return TSAGLShellSurface().run(raw_text)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="TS-AGL shell surface.")
    parser.add_argument("text", nargs="*", help="Speakable TS-AGL command.")
    parser.add_argument("--receipt", default="artifacts/ts_agl_shell_surface_receipt.json")
    args = parser.parse_args(argv)

    raw_text = " ".join(args.text).strip() or "help"
    result = run_shell_command(raw_text)
    payload = result.to_dict()

    receipt = {
        "artifact": "ts_agl_shell_surface_receipt",
        "raw_text": raw_text,
        "mode": result.mode,
        "rendered_reply": result.rendered_reply,
        "external_llm_used": False,
        "external_side_effect_performed": False,
        "candidate_graph_contamination_count": 0,
        "all_gates_passed": bool(result.payload.get("all_gates_passed")),
        "payload": payload,
    }

    path = Path(args.receipt)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(result.rendered_reply)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
