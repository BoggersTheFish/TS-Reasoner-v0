from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from ts_agl.core.types import AGLTrace, LanguageMove, ResultPacket
from ts_agl.registry import DomainRegistry
from ts_agl.router import Dispatcher, OperationRouter
from ts_agl.workflow import WorkflowLedger


WORKFLOW_MARKER_PATH = "artifacts/ts_agl_interactive_workflow_marker.json"
WORKFLOW_MARKER_CONTENT = """{
  "artifact": "ts_agl_interactive_workflow_marker",
  "claim": "pending action executed only after workflow confirmation",
  "language_layer_is_proof_authority": false,
  "requires_confirmation": true
}
"""


@dataclass(frozen=True)
class InteractiveWorkflowArenaResult:
    staged_action_id: str
    missing_confirmation_result: ResultPacket
    wrong_confirmation_result: ResultPacket
    confirmed_result: ResultPacket
    trace: AGLTrace
    ledger: WorkflowLedger

    def to_dict(self) -> Dict[str, object]:
        ledger_data = self.ledger.to_dict()
        missing_blocked = self.missing_confirmation_result.status == "needs_confirmation"
        wrong_blocked = self.wrong_confirmation_result.status == "needs_confirmation"
        confirmed_executed = self.confirmed_result.status == "success" and self.confirmed_result.mutated_state

        return {
            "artifact": "ts_agl_interactive_workflow_ledger",
            "staged_action_id": self.staged_action_id,
            "missing_confirmation_result": self.missing_confirmation_result.to_dict(),
            "wrong_confirmation_result": self.wrong_confirmation_result.to_dict(),
            "confirmed_result": self.confirmed_result.to_dict(),
            "ledger": ledger_data,
            "trace": self.trace.to_dict(),
            "write_path": WORKFLOW_MARKER_PATH,
            "write_path_exists": Path(WORKFLOW_MARKER_PATH).exists(),
            "missing_confirmation_blocked": missing_blocked,
            "wrong_confirmation_blocked": wrong_blocked,
            "confirmed_execution_succeeded": confirmed_executed,
            "event_count": ledger_data["event_count"],
            "executed_count": ledger_data["executed_count"],
            "wrong_unconfirmed_mutation_count": int(self.missing_confirmation_result.mutated_state)
            + int(self.wrong_confirmation_result.mutated_state),
            "confirmed_mutation_count": int(self.confirmed_result.mutated_state),
            "candidate_graph_contamination_count": self.trace.candidate_graph_contamination_count,
            "external_llm_used": self.trace.external_llm_used,
            "all_gates_passed": (
                missing_blocked
                and wrong_blocked
                and confirmed_executed
                and ledger_data["event_count"] >= 4
                and ledger_data["executed_count"] == 1
                and self.missing_confirmation_result.mutated_state is False
                and self.wrong_confirmation_result.mutated_state is False
                and self.confirmed_result.mutated_state is True
                and self.trace.candidate_graph_contamination_count == 0
                and self.trace.external_llm_used is False
            ),
        }


class InteractiveWorkflowArena:
    """v15 interactive workflow ledger arena.

    This simulates a multi-turn flow:

    1. user asks to create a safe workflow marker
    2. TS-AGL stages a reversible write as pending
    3. execution without confirmation is blocked
    4. execution with the wrong confirmation token is blocked
    5. execution with the correct token succeeds
    6. all events are preserved in a ledger
    """

    def __init__(self) -> None:
        self.registry = DomainRegistry().load()
        self.router = OperationRouter(self.registry)
        self.dispatcher = Dispatcher()
        self.ledger = WorkflowLedger()

    def build_move(self) -> LanguageMove:
        return LanguageMove(
            move_type="EXECUTE",
            raw_text="stage a safe workflow marker and wait for confirmation",
            target=WORKFLOW_MARKER_PATH,
            slots={
                "path": WORKFLOW_MARKER_PATH,
                "content": WORKFLOW_MARKER_CONTENT,
            },
            operation_hint="write_text_file",
            domain_hint="filesystem",
            confidence=1.0,
        )

    def run(self) -> InteractiveWorkflowArenaResult:
        move = self.build_move()
        call = self.router.route(move)
        pending = self.ledger.stage_call(call)

        missing_confirmation_result = self.ledger.attempt_execute(
            pending.action_id,
            dispatcher=self.dispatcher,
            confirmation_token=None,
        )
        wrong_confirmation_result = self.ledger.attempt_execute(
            pending.action_id,
            dispatcher=self.dispatcher,
            confirmation_token="wrong-token",
        )
        confirmed_result = self.ledger.attempt_execute(
            pending.action_id,
            dispatcher=self.dispatcher,
            confirmation_token=pending.confirmation_token,
        )

        results = [
            missing_confirmation_result,
            wrong_confirmation_result,
            confirmed_result,
        ]

        trace = AGLTrace(
            raw_text=move.raw_text,
            moves=[move],
            calls=[call],
            results=results,
            rendered_reply=(
                "Interactive workflow ledger staged one reversible action, "
                "blocked unconfirmed attempts, and executed only after the correct confirmation token."
            ),
            wrong_state_mutation_count=int(missing_confirmation_result.mutated_state)
            + int(wrong_confirmation_result.mutated_state),
            candidate_graph_contamination_count=0,
            external_llm_used=False,
        )

        return InteractiveWorkflowArenaResult(
            staged_action_id=pending.action_id,
            missing_confirmation_result=missing_confirmation_result,
            wrong_confirmation_result=wrong_confirmation_result,
            confirmed_result=confirmed_result,
            trace=trace,
            ledger=self.ledger,
        )


def run_interactive_workflow_arena() -> InteractiveWorkflowArenaResult:
    return InteractiveWorkflowArena().run()
