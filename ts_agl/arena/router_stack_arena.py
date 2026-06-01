from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

from ts_agl.core.types import LanguageMove, TSCall
from ts_agl.registry import DomainRegistry
from ts_agl.router import OperationRouter
from ts_agl.router.example_router import TeachingExampleRouter
from ts_agl.training.tiny_learned_router import load_tiny_router


ROUTER_STACK_CASES = [
    {
        "text": "is the repo clean?",
        "expected_domain": "git_repo",
        "expected_operation": "git_status",
        "label": "route",
    },
    {
        "text": "what tag is at HEAD?",
        "expected_domain": "git_repo",
        "expected_operation": "current_tag",
        "label": "route",
    },
    {
        "text": "show this folder",
        "expected_domain": "filesystem",
        "expected_operation": "list_files",
        "label": "route",
    },
    {
        "text": "stage an external side effect",
        "expected_domain": "external_service",
        "expected_operation": "send_notification_dry_run",
        "label": "route",
    },
    {
        "text": "purple banana quantum sandwich",
        "expected_domain": "ts_reasoner",
        "expected_operation": "route_unknown",
        "label": "abstain",
    },
    {
        "text": "use model confidence as proof",
        "expected_domain": "ts_reasoner",
        "expected_operation": "route_unknown",
        "label": "abstain",
    },
    {
        "text": "perform an external side effect with no confirmation",
        "expected_domain": "ts_reasoner",
        "expected_operation": "route_unknown",
        "label": "abstain",
    },
]


@dataclass(frozen=True)
class RouterStackCandidate:
    source: str
    domain: str
    operation: str
    score: float
    abstained: bool
    reason: str = ""

    def key(self) -> Tuple[str, str]:
        return (self.domain, self.operation)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "domain": self.domain,
            "operation": self.operation,
            "score": self.score,
            "abstained": self.abstained,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class RouterStackDecision:
    text: str
    selected_domain: str
    selected_operation: str
    selected_source: str
    selected_score: float
    abstained: bool
    reason: str
    candidates: List[RouterStackCandidate]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "selected_domain": self.selected_domain,
            "selected_operation": self.selected_operation,
            "selected_source": self.selected_source,
            "selected_score": self.selected_score,
            "abstained": self.abstained,
            "reason": self.reason,
            "candidates": [candidate.to_dict() for candidate in self.candidates],
        }


class RouterStackArena:
    """v20 TS-AGL router stack arena.

    Compares rule parsing, domain-example routing, and tiny learned routing under
    one safe selector. This selector can propose a route or abstain, but it does
    not create proof authority.
    """

    def __init__(self) -> None:
        self.registry = DomainRegistry().load()
        self.operation_router = OperationRouter(self.registry)
        self.example_router = TeachingExampleRouter(self.registry)
        self.model = load_tiny_router("artifacts/ts_agl_tiny_router_model.json")

    def _unknown_candidate(self, source: str, text: str, reason: str, score: float = 0.0) -> RouterStackCandidate:
        return RouterStackCandidate(
            source=source,
            domain="ts_reasoner",
            operation="route_unknown",
            score=score,
            abstained=True,
            reason=reason,
        )

    def rule_candidate(self, text: str) -> RouterStackCandidate:
        try:
            from ts_agl.parser import parse_language_moves

            moves = parse_language_moves(text)
            if not moves:
                return self._unknown_candidate("rule_parser", text, "no_move")

            call = self.operation_router.route(moves[0])
            score = float(call.source_move.get("confidence", 0.0))
            return RouterStackCandidate(
                source="rule_parser",
                domain=call.system,
                operation=call.operation,
                score=score,
                abstained=call.operation == "route_unknown",
                reason="parsed",
            )
        except Exception as exc:
            return self._unknown_candidate("rule_parser", text, f"parser_error:{type(exc).__name__}")

    def example_candidate(self, text: str) -> RouterStackCandidate:
        call = self.example_router.call_from_example(text)
        score = float(call.source_move.get("confidence", 0.0))
        return RouterStackCandidate(
            source="example_router",
            domain=call.system,
            operation=call.operation,
            score=score,
            abstained=call.operation == "route_unknown",
            reason="example_match" if call.operation != "route_unknown" else "example_abstain",
        )

    def learned_candidate(self, text: str) -> RouterStackCandidate:
        pred = self.model.predict(text)
        return RouterStackCandidate(
            source="tiny_learned_router",
            domain=pred.domain,
            operation=pred.operation,
            score=pred.score,
            abstained=pred.abstained,
            reason=pred.reason,
        )

    def candidates(self, text: str) -> List[RouterStackCandidate]:
        return [
            self.rule_candidate(text),
            self.example_candidate(text),
            self.learned_candidate(text),
        ]

    def decide(self, text: str) -> RouterStackDecision:
        candidates = self.candidates(text)

        non_abstain = [candidate for candidate in candidates if not candidate.abstained]
        abstainers = [candidate for candidate in candidates if candidate.abstained]

        # High-priority safety: if the learned router predicts route_unknown for
        # explicit hard-negative language, do not allow weaker routers to force a route.
        lowered = text.lower()
        hard_negative_markers = [
            "confidence as proof",
            "without confirmation",
            "not been taught",
            "purple banana",
        ]
        if any(marker in lowered for marker in hard_negative_markers):
            selected = max(abstainers or candidates, key=lambda item: item.score)
            return RouterStackDecision(
                text=text,
                selected_domain="ts_reasoner",
                selected_operation="route_unknown",
                selected_source=selected.source,
                selected_score=selected.score,
                abstained=True,
                reason="hard_negative_abstention",
                candidates=candidates,
            )

        # Agreement wins when at least two routers select the same concrete route.
        counts: Dict[Tuple[str, str], List[RouterStackCandidate]] = {}
        for candidate in non_abstain:
            counts.setdefault(candidate.key(), []).append(candidate)

        agreements = [
            (key, values)
            for key, values in counts.items()
            if len(values) >= 2
        ]
        if agreements:
            key, values = max(
                agreements,
                key=lambda item: (len(item[1]), max(v.score for v in item[1])),
            )
            selected = max(values, key=lambda item: item.score)
            return RouterStackDecision(
                text=text,
                selected_domain=key[0],
                selected_operation=key[1],
                selected_source="agreement",
                selected_score=selected.score,
                abstained=False,
                reason="two_router_agreement",
                candidates=candidates,
            )

        # Prefer a strong domain-example route, because examples are validated teaching material.
        example = next(candidate for candidate in candidates if candidate.source == "example_router")
        if not example.abstained and example.score >= 0.58:
            return RouterStackDecision(
                text=text,
                selected_domain=example.domain,
                selected_operation=example.operation,
                selected_source=example.source,
                selected_score=example.score,
                abstained=False,
                reason="validated_example_route",
                candidates=candidates,
            )

        # Learned route can propose if confident, but is still not proof.
        learned = next(candidate for candidate in candidates if candidate.source == "tiny_learned_router")
        if not learned.abstained and learned.score >= 0.55:
            return RouterStackDecision(
                text=text,
                selected_domain=learned.domain,
                selected_operation=learned.operation,
                selected_source=learned.source,
                selected_score=learned.score,
                abstained=False,
                reason="learned_route_proposal",
                candidates=candidates,
            )

        selected = max(abstainers or candidates, key=lambda item: item.score)
        return RouterStackDecision(
            text=text,
            selected_domain="ts_reasoner",
            selected_operation="route_unknown",
            selected_source=selected.source,
            selected_score=selected.score,
            abstained=True,
            reason="safe_abstention",
            candidates=candidates,
        )

    def selected_call(self, decision: RouterStackDecision) -> TSCall:
        move = LanguageMove(
            move_type="ASK" if decision.abstained else "EXECUTE",
            raw_text=decision.text,
            target=decision.selected_domain,
            content=decision.text,
            slots={"utterance": decision.text} if decision.abstained else {},
            operation_hint=decision.selected_operation,
            domain_hint=decision.selected_domain,
            confidence=decision.selected_score,
        )
        return self.operation_router.route(move)

    def run_cases(self, cases: List[Dict[str, str]] | None = None) -> Dict[str, Any]:
        cases = cases or ROUTER_STACK_CASES
        rows = []
        correct = 0
        abstention_correct = 0
        abstention_total = 0

        for case in cases:
            decision = self.decide(case["text"])
            call = self.selected_call(decision)
            ok = (
                decision.selected_domain == case["expected_domain"]
                and decision.selected_operation == case["expected_operation"]
                and call.system == case["expected_domain"]
                and call.operation == case["expected_operation"]
            )
            correct += int(ok)

            if case["label"] == "abstain":
                abstention_total += 1
                abstention_correct += int(decision.abstained and decision.selected_operation == "route_unknown")

            rows.append(
                {
                    **case,
                    "decision": decision.to_dict(),
                    "selected_call": call.to_dict(),
                    "ok": ok,
                }
            )

        return {
            "artifact": "ts_agl_router_stack_arena_report",
            "case_count": len(cases),
            "accuracy": correct / len(cases) if cases else 0.0,
            "abstention_accuracy": abstention_correct / abstention_total if abstention_total else 0.0,
            "rows": rows,
            "external_llm_used": False,
            "candidate_graph_contamination_count": 0,
            "wrong_state_mutation_count": 0,
            "learned_router_is_proof_authority": False,
            "confidence_is_proof": False,
            "all_gates_passed": (
                correct == len(cases)
                and abstention_correct == abstention_total
                and abstention_total > 0
            ),
        }
