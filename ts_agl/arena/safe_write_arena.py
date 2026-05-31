from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from ts_agl.core.types import AGLTrace, LanguageMove, ResultPacket, TSCall
from ts_agl.registry import DomainRegistry
from ts_agl.router import Dispatcher, OperationRouter
from ts_agl.renderer import render_results


SAFE_WRITE_PATH = "artifacts/ts_agl_safe_write_marker.json"
SAFE_WRITE_CONTENT = """{
  "artifact": "ts_agl_safe_write_marker",
  "claim": "confirmed reversible write executed through TS-AGL risk gate",
  "language_layer_is_proof_authority": false,
  "requires_confirmation": true
}
"""


@dataclass(frozen=True)
class SafeWriteArenaResult:
    staged_call: TSCall
    unconfirmed_result: ResultPacket
    confirmed_result: ResultPacket
    trace: AGLTrace

    def to_dict(self) -> Dict[str, object]:
        unconfirmed_blocked = self.unconfirmed_result.status == "needs_confirmation"
        confirmed_executed = self.confirmed_result.status == "success" and self.confirmed_result.mutated_state
        return {
            "artifact": "ts_agl_safe_write_arena",
            "staged_call": self.staged_call.to_dict(),
            "unconfirmed_result": self.unconfirmed_result.to_dict(),
            "confirmed_result": self.confirmed_result.to_dict(),
            "trace": self.trace.to_dict(),
            "unconfirmed_blocked": unconfirmed_blocked,
            "confirmed_executed": confirmed_executed,
            "write_path": SAFE_WRITE_PATH,
            "write_path_exists": Path(SAFE_WRITE_PATH).exists(),
            "risk": self.staged_call.risk,
            "requires_confirmation": self.staged_call.requires_confirmation,
            "wrong_unconfirmed_mutation_count": 1 if self.unconfirmed_result.mutated_state else 0,
            "confirmed_mutation_count": 1 if self.confirmed_result.mutated_state else 0,
            "candidate_graph_contamination_count": self.trace.candidate_graph_contamination_count,
            "external_llm_used": self.trace.external_llm_used,
            "all_gates_passed": (
                self.staged_call.risk == "reversible_write"
                and self.staged_call.requires_confirmation is True
                and unconfirmed_blocked
                and self.unconfirmed_result.mutated_state is False
                and confirmed_executed
                and self.trace.candidate_graph_contamination_count == 0
                and self.trace.external_llm_used is False
            ),
        }


class SafeWriteArena:
    """Interactive confirmation + safe write arena.

    The arena stages a reversible filesystem write, proves it is blocked without
    confirmation, then executes the same call with explicit confirmation.

    Boundary:
    - no external LLM
    - reversible write only
    - write target restricted to artifacts/
    - confirmation is required before mutation
    - language layer is not proof authority
    """

    def __init__(self) -> None:
        self.registry = DomainRegistry().load()
        self.router = OperationRouter(self.registry)
        self.dispatcher = Dispatcher()

    def build_move(self) -> LanguageMove:
        return LanguageMove(
            move_type="EXECUTE",
            raw_text="create a safe write marker in artifacts",
            target="artifacts/ts_agl_safe_write_marker.json",
            slots={
                "path": SAFE_WRITE_PATH,
                "content": SAFE_WRITE_CONTENT,
            },
            operation_hint="write_text_file",
            domain_hint="filesystem",
            confidence=1.0,
        )

    def run(self) -> SafeWriteArenaResult:
        move = self.build_move()
        call = self.router.route(move)

        unconfirmed_result = self.dispatcher.dispatch(call, confirmed=False)
        confirmed_result = self.dispatcher.dispatch(call, confirmed=True)

        results: List[ResultPacket] = [unconfirmed_result, confirmed_result]
        rendered = (
            "Safe write arena staged a reversible write. "
            + render_results(results)
        )

        trace = AGLTrace(
            raw_text=move.raw_text,
            moves=[move],
            calls=[call],
            results=results,
            rendered_reply=rendered,
            wrong_state_mutation_count=1 if unconfirmed_result.mutated_state else 0,
            candidate_graph_contamination_count=0,
            external_llm_used=False,
        )

        return SafeWriteArenaResult(
            staged_call=call,
            unconfirmed_result=unconfirmed_result,
            confirmed_result=confirmed_result,
            trace=trace,
        )


def run_safe_write_arena() -> SafeWriteArenaResult:
    return SafeWriteArena().run()
