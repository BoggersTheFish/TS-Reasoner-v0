from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional
import hashlib
import json
import time


def stable_id(prefix: str, payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


@dataclass(frozen=True)
class LanguageMove:
    """A parsed user language move.

    This is candidate structure, not accepted truth.
    """

    move_type: str
    raw_text: str
    target: Optional[str] = None
    content: Optional[str] = None
    slots: Dict[str, Any] = field(default_factory=dict)
    unresolved_slots: List[str] = field(default_factory=list)
    operation_hint: Optional[str] = None
    domain_hint: Optional[str] = None
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TSCall:
    """A structured operation request produced from a LanguageMove."""

    system: str
    operation: str
    args: Dict[str, Any] = field(default_factory=dict)
    risk: str = "read_only"
    requires_confirmation: bool = False
    source_move: Dict[str, Any] = field(default_factory=dict)
    missing_slots: List[str] = field(default_factory=list)
    call_id: Optional[str] = None

    def __post_init__(self) -> None:
        if self.call_id is None:
            object.__setattr__(
                self,
                "call_id",
                stable_id(
                    "call",
                    {
                        "system": self.system,
                        "operation": self.operation,
                        "args": self.args,
                        "source_move": self.source_move,
                    },
                ),
            )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ResultPacket:
    """Structured result from an adapter/tool/system call."""

    status: str
    system: str
    operation: str
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    mutated_state: bool = False
    result_id: Optional[str] = None

    def __post_init__(self) -> None:
        if self.result_id is None:
            object.__setattr__(
                self,
                "result_id",
                stable_id(
                    "result",
                    {
                        "status": self.status,
                        "system": self.system,
                        "operation": self.operation,
                        "data": self.data,
                        "error": self.error,
                        "mutated_state": self.mutated_state,
                    },
                ),
            )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AGLTrace:
    """Receipt-style trace for a full language -> operation -> result pass."""

    raw_text: str
    moves: List[LanguageMove]
    calls: List[TSCall]
    results: List[ResultPacket]
    rendered_reply: str
    created_at: float = field(default_factory=time.time)
    wrong_state_mutation_count: int = 0
    candidate_graph_contamination_count: int = 0
    external_llm_used: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw_text": self.raw_text,
            "moves": [m.to_dict() for m in self.moves],
            "calls": [c.to_dict() for c in self.calls],
            "results": [r.to_dict() for r in self.results],
            "rendered_reply": self.rendered_reply,
            "created_at": self.created_at,
            "wrong_state_mutation_count": self.wrong_state_mutation_count,
            "candidate_graph_contamination_count": self.candidate_graph_contamination_count,
            "external_llm_used": self.external_llm_used,
            "all_gates_passed": (
                self.wrong_state_mutation_count == 0
                and self.candidate_graph_contamination_count == 0
                and self.external_llm_used is False
            ),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True, ensure_ascii=False)
