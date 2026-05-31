from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set

from ts_agl.core.types import AGLTrace, LanguageMove, ResultPacket, TSCall
from ts_agl.registry import DomainRegistry
from ts_agl.router import Dispatcher, OperationRouter
from ts_agl.renderer import render_results


DEFAULT_CROSS_DOMAIN_REQUEST = (
    "Check the repo, inspect the release state, inspect the docs folder, "
    "summarise the TS-AGL session, and tell me the next safe action."
)


@dataclass(frozen=True)
class ArenaStep:
    """One planned cross-domain TS-AGL operation."""

    label: str
    move: LanguageMove

    def to_dict(self) -> Dict[str, object]:
        return {
            "label": self.label,
            "move": self.move.to_dict(),
        }


class CrossDomainArena:
    """Deterministic cross-domain TS-AGL arena.

    v13.0 proves one natural-language request can coordinate multiple taught
    domains through the same LanguageMove -> TSCall -> ResultPacket surface.

    Boundary:
    - no external LLM
    - read-only operations only in this arena
    - language routing is not proof authority
    - adapter results are grounded result packets
    """

    def __init__(self) -> None:
        self.registry = DomainRegistry().load()
        self.router = OperationRouter(self.registry)
        self.dispatcher = Dispatcher()

    def plan(self, raw_text: str = DEFAULT_CROSS_DOMAIN_REQUEST) -> List[ArenaStep]:
        """Create a deterministic arena plan from a broad cross-domain request.

        v13.0 intentionally keeps the planner transparent: the request is broad,
        but the arena maps it into a fixed suite of read-only taught-domain calls.
        Later versions can replace this with learned/interactive planning.
        """

        return [
            ArenaStep(
                label="inspect_repo_status",
                move=LanguageMove(
                    move_type="INSPECT",
                    raw_text=raw_text,
                    target="repo",
                    operation_hint="git_status",
                    domain_hint="git_repo",
                    confidence=1.0,
                ),
            ),
            ArenaStep(
                label="inspect_release_tag",
                move=LanguageMove(
                    move_type="INSPECT",
                    raw_text=raw_text,
                    target="release",
                    operation_hint="current_tag",
                    domain_hint="git_repo",
                    confidence=1.0,
                ),
            ),
            ArenaStep(
                label="inspect_docs_folder",
                move=LanguageMove(
                    move_type="INSPECT",
                    raw_text=raw_text,
                    target="docs",
                    slots={"path": "docs"},
                    operation_hint="list_files",
                    domain_hint="filesystem",
                    confidence=1.0,
                ),
            ),
            ArenaStep(
                label="summarize_ts_agl_session",
                move=LanguageMove(
                    move_type="SUMMARISE",
                    raw_text=raw_text,
                    target="session",
                    operation_hint="summarize_session",
                    domain_hint="ts_reasoner",
                    confidence=1.0,
                ),
            ),
            ArenaStep(
                label="plan_next_safe_action",
                move=LanguageMove(
                    move_type="PLAN",
                    raw_text=raw_text,
                    target="current_project_state",
                    operation_hint="next_safe_release_action",
                    domain_hint="git_repo",
                    confidence=1.0,
                ),
            ),
        ]

    def run(self, raw_text: str = DEFAULT_CROSS_DOMAIN_REQUEST) -> AGLTrace:
        steps = self.plan(raw_text)
        moves = [step.move for step in steps]
        calls = [self.router.route(move) for move in moves]
        results = [self.dispatcher.dispatch(call) for call in calls]
        rendered = self.render_cross_domain_reply(results)

        return AGLTrace(
            raw_text=raw_text,
            moves=moves,
            calls=calls,
            results=results,
            rendered_reply=rendered,
            wrong_state_mutation_count=sum(1 for result in results if result.mutated_state),
            candidate_graph_contamination_count=0,
            external_llm_used=False,
        )

    def render_cross_domain_reply(self, results: List[ResultPacket]) -> str:
        base = render_results(results)
        domains = sorted({result.system for result in results})
        return (
            f"Cross-domain TS-AGL arena completed across {', '.join(domains)}. "
            f"{base}"
        )


def run_cross_domain_arena(raw_text: str = DEFAULT_CROSS_DOMAIN_REQUEST) -> AGLTrace:
    return CrossDomainArena().run(raw_text)


def summarize_cross_domain_trace(trace: AGLTrace) -> Dict[str, object]:
    domains: Set[str] = {call.system for call in trace.calls}
    operations = [f"{call.system}.{call.operation}" for call in trace.calls]
    statuses = [result.status for result in trace.results]
    risky_calls = [call.to_dict() for call in trace.calls if call.risk != "read_only"]

    return {
        "raw_text": trace.raw_text,
        "domain_count": len(domains),
        "domains": sorted(domains),
        "call_count": len(trace.calls),
        "operations": operations,
        "statuses": statuses,
        "all_calls_read_only": len(risky_calls) == 0,
        "risky_calls": risky_calls,
        "wrong_state_mutation_count": trace.wrong_state_mutation_count,
        "candidate_graph_contamination_count": trace.candidate_graph_contamination_count,
        "external_llm_used": trace.external_llm_used,
        "rendered_reply": trace.rendered_reply,
        "trace": trace.to_dict(),
        "all_gates_passed": (
            len(domains) >= 3
            and len(trace.calls) >= 5
            and len(risky_calls) == 0
            and trace.wrong_state_mutation_count == 0
            and trace.candidate_graph_contamination_count == 0
            and trace.external_llm_used is False
            and all(status in {"success", "abstained"} for status in statuses)
        ),
    }
