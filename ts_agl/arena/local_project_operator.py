from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from ts_agl.arena.router_stack_arena import RouterStackArena
from ts_agl.core.types import AGLTrace, LanguageMove, ResultPacket, TSCall
from ts_agl.registry import DomainRegistry
from ts_agl.router import Dispatcher, OperationRouter
from ts_agl.workflow import WorkflowLedger


PROJECT_OPERATOR_NOTE_PATH = "artifacts/ts_agl_project_operator_note.json"
PROJECT_OPERATOR_NOTE_CONTENT = """{
  "artifact": "ts_agl_project_operator_note",
  "claim": "local project operator inspected project state and executed only a confirmed safe artifact write",
  "language_layer_is_proof_authority": false,
  "external_side_effect_performed": false,
  "requires_confirmation": true
}
"""


@dataclass(frozen=True)
class LocalProjectOperatorResult:
    raw_text: str
    inspect_calls: List[TSCall]
    inspect_results: List[ResultPacket]
    router_decision: Dict[str, object]
    staged_action_id: str
    blocked_result: ResultPacket
    confirmed_result: ResultPacket
    ledger: WorkflowLedger
    trace: AGLTrace

    def to_dict(self) -> Dict[str, object]:
        ledger_data = self.ledger.to_dict()
        blocked = self.blocked_result.status == "needs_confirmation"
        confirmed = self.confirmed_result.status == "success" and self.confirmed_result.mutated_state
        domains = sorted({call.system for call in self.inspect_calls + self.trace.calls})
        operations = [f"{call.system}.{call.operation}" for call in self.inspect_calls + self.trace.calls]

        return {
            "artifact": "ts_agl_local_project_operator",
            "raw_text": self.raw_text,
            "domains": domains,
            "operations": operations,
            "inspect_calls": [call.to_dict() for call in self.inspect_calls],
            "inspect_results": [result.to_dict() for result in self.inspect_results],
            "router_decision": self.router_decision,
            "staged_action_id": self.staged_action_id,
            "blocked_result": self.blocked_result.to_dict(),
            "confirmed_result": self.confirmed_result.to_dict(),
            "ledger": ledger_data,
            "trace": self.trace.to_dict(),
            "project_note_path": PROJECT_OPERATOR_NOTE_PATH,
            "project_note_exists": Path(PROJECT_OPERATOR_NOTE_PATH).exists(),
            "repo_inspected": any(call.system == "git_repo" for call in self.inspect_calls),
            "filesystem_inspected": any(call.system == "filesystem" for call in self.inspect_calls),
            "router_stack_used": self.router_decision.get("selected_source") is not None,
            "unconfirmed_write_blocked": blocked,
            "confirmed_write_executed": confirmed,
            "wrong_unconfirmed_mutation_count": int(self.blocked_result.mutated_state),
            "confirmed_mutation_count": int(self.confirmed_result.mutated_state),
            "external_side_effect_performed": False,
            "external_llm_used": False,
            "candidate_graph_contamination_count": 0,
            "all_gates_passed": (
                len(domains) >= 2
                and any(op == "git_repo.git_status" for op in operations)
                and any(op == "git_repo.current_tag" for op in operations)
                and any(op == "filesystem.list_files" for op in operations)
                and self.router_decision.get("selected_operation") == "next_safe_release_action"
                and blocked
                and not self.blocked_result.mutated_state
                and confirmed
                and Path(PROJECT_OPERATOR_NOTE_PATH).exists()
                and ledger_data["executed_count"] == 1
                and self.trace.candidate_graph_contamination_count == 0
                and self.trace.external_llm_used is False
            ),
        }


class LocalProjectOperator:
    """v21 local TS-AGL project operator.

    The operator is bounded and local:
    - inspect git state
    - inspect release/tag state
    - inspect docs folder
    - use router stack for the requested next action
    - stage a safe artifacts/ write
    - block the write without confirmation
    - execute only with the correct confirmation token
    """

    def __init__(self) -> None:
        self.registry = DomainRegistry().load()
        self.router = OperationRouter(self.registry)
        self.dispatcher = Dispatcher()
        self.ledger = WorkflowLedger()
        self.router_stack = RouterStackArena()

    def _call_from_move(self, move: LanguageMove) -> TSCall:
        return self.router.route(move)

    def build_inspection_moves(self, raw_text: str) -> List[LanguageMove]:
        return [
            LanguageMove(
                move_type="INSPECT",
                raw_text=raw_text,
                target="repo",
                operation_hint="git_status",
                domain_hint="git_repo",
                confidence=1.0,
            ),
            LanguageMove(
                move_type="INSPECT",
                raw_text=raw_text,
                target="release",
                operation_hint="current_tag",
                domain_hint="git_repo",
                confidence=1.0,
            ),
            LanguageMove(
                move_type="INSPECT",
                raw_text=raw_text,
                target="docs",
                slots={"path": "docs"},
                operation_hint="list_files",
                domain_hint="filesystem",
                confidence=1.0,
            ),
        ]

    def build_safe_note_move(self, raw_text: str) -> LanguageMove:
        return LanguageMove(
            move_type="EXECUTE",
            raw_text=raw_text,
            target=PROJECT_OPERATOR_NOTE_PATH,
            slots={
                "path": PROJECT_OPERATOR_NOTE_PATH,
                "content": PROJECT_OPERATOR_NOTE_CONTENT,
            },
            operation_hint="write_text_file",
            domain_hint="filesystem",
            confidence=1.0,
        )

    def run(
        self,
        raw_text: str = "inspect the local project, tell me the next safe action, and stage a project note",
    ) -> LocalProjectOperatorResult:
        inspection_moves = self.build_inspection_moves(raw_text)
        inspect_calls = [self._call_from_move(move) for move in inspection_moves]
        inspect_results = [self.dispatcher.dispatch(call) for call in inspect_calls]

        router_decision = self.router_stack.decide("what should we do next?").to_dict()

        note_move = self.build_safe_note_move(raw_text)
        note_call = self._call_from_move(note_move)
        pending = self.ledger.stage_call(note_call)

        blocked_result = self.ledger.attempt_execute(
            pending.action_id,
            dispatcher=self.dispatcher,
            confirmation_token=None,
        )
        confirmed_result = self.ledger.attempt_execute(
            pending.action_id,
            dispatcher=self.dispatcher,
            confirmation_token=pending.confirmation_token,
        )

        all_moves = inspection_moves + [note_move]
        all_calls = inspect_calls + [note_call]
        all_results = inspect_results + [blocked_result, confirmed_result]

        trace = AGLTrace(
            raw_text=raw_text,
            moves=all_moves,
            calls=all_calls,
            results=all_results,
            rendered_reply=(
                "Local project operator inspected repo/docs state, used the router stack "
                "for next safe action routing, blocked the unconfirmed write, and executed "
                "only the confirmed safe artifact write."
            ),
            wrong_state_mutation_count=int(blocked_result.mutated_state),
            candidate_graph_contamination_count=0,
            external_llm_used=False,
        )

        return LocalProjectOperatorResult(
            raw_text=raw_text,
            inspect_calls=inspect_calls,
            inspect_results=inspect_results,
            router_decision=router_decision,
            staged_action_id=pending.action_id,
            blocked_result=blocked_result,
            confirmed_result=confirmed_result,
            ledger=self.ledger,
            trace=trace,
        )


def run_local_project_operator() -> LocalProjectOperatorResult:
    return LocalProjectOperator().run()
