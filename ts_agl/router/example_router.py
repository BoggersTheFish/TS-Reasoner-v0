from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Set
import re

from ts_agl.core.types import LanguageMove, TSCall
from ts_agl.registry.domain_registry import DomainRegistry
from ts_agl.router.operation_router import OperationRouter


def _tokens(text: str) -> Set[str]:
    return set(re.findall(r"[a-z0-9_]+", text.lower()))


def _score(query: str, example: str) -> float:
    """Transparent v0 score for language-example routing.

    Combines token overlap with character similarity. This is deliberately
    small and inspectable; learned routing can come later from these traces.
    """

    q_tokens = _tokens(query)
    e_tokens = _tokens(example)

    if not q_tokens or not e_tokens:
        return 0.0

    overlap = len(q_tokens & e_tokens) / len(q_tokens | e_tokens)
    sequence = SequenceMatcher(None, query.lower(), example.lower()).ratio()

    substring_bonus = 0.0
    q_low = query.lower().strip()
    e_low = example.lower().strip()
    if q_low == e_low:
        substring_bonus = 0.30
    elif q_low in e_low or e_low in q_low:
        substring_bonus = 0.12

    return min(1.0, (0.65 * overlap) + (0.35 * sequence) + substring_bonus)


@dataclass(frozen=True)
class ExampleRoute:
    domain: str
    operation: str
    example: str
    score: float
    risk: str
    requires_confirmation: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "operation": self.operation,
            "example": self.example,
            "score": self.score,
            "risk": self.risk,
            "requires_confirmation": self.requires_confirmation,
        }


class TeachingExampleRouter:
    """Routes natural language using examples declared in domain packs.

    This is the first concrete "teaching pack -> routing behaviour" bridge.
    """

    def __init__(self, registry: DomainRegistry, threshold: float = 0.58) -> None:
        self.registry = registry
        self.threshold = threshold
        self.operation_router = OperationRouter(registry)

    def all_examples(self) -> List[ExampleRoute]:
        rows: List[ExampleRoute] = []
        for domain in self.registry.list_domains():
            for op in self.registry.operations(domain):
                for example in op.get("examples", []):
                    rows.append(
                        ExampleRoute(
                            domain=domain,
                            operation=op["name"],
                            example=example,
                            score=1.0,
                            risk=op.get("risk", "read_only"),
                            requires_confirmation=bool(op.get("requires_confirmation", False)),
                        )
                    )
        return rows

    def rank(self, text: str) -> List[ExampleRoute]:
        ranked: List[ExampleRoute] = []
        for domain in self.registry.list_domains():
            for op in self.registry.operations(domain):
                for example in op.get("examples", []):
                    ranked.append(
                        ExampleRoute(
                            domain=domain,
                            operation=op["name"],
                            example=example,
                            score=_score(text, example),
                            risk=op.get("risk", "read_only"),
                            requires_confirmation=bool(op.get("requires_confirmation", False)),
                        )
                    )

        return sorted(ranked, key=lambda item: item.score, reverse=True)

    def best(self, text: str) -> Optional[ExampleRoute]:
        ranked = self.rank(text)
        if not ranked:
            return None
        best = ranked[0]
        if best.score < self.threshold:
            return None
        return best

    def move_from_example(self, text: str) -> LanguageMove:
        best = self.best(text)
        if best is None:
            return LanguageMove(
                move_type="ASK",
                raw_text=text,
                content=text,
                slots={"utterance": text},
                operation_hint="route_unknown",
                domain_hint="ts_reasoner",
                confidence=0.0,
            )

        return LanguageMove(
            move_type="EXECUTE" if best.risk != "read_only" else "INSPECT",
            raw_text=text,
            target=best.domain,
            content=text,
            slots={},
            unresolved_slots=[],
            operation_hint=best.operation,
            domain_hint=best.domain,
            confidence=best.score,
        )

    def call_from_example(self, text: str) -> TSCall:
        move = self.move_from_example(text)
        return self.operation_router.route(move)

    def explain_route(self, text: str, top_k: int = 3) -> Dict[str, Any]:
        ranked = self.rank(text)[:top_k]
        selected = self.best(text)
        return {
            "raw_text": text,
            "threshold": self.threshold,
            "selected": selected.to_dict() if selected else None,
            "ranked": [row.to_dict() for row in ranked],
        }
