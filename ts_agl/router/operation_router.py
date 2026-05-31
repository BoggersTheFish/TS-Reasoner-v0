from __future__ import annotations

from typing import List

from ts_agl.core.types import LanguageMove, TSCall
from ts_agl.registry.domain_registry import DomainRegistry


class OperationRouter:
    """Routes LanguageMove objects into TSCall objects using manifest constraints."""

    def __init__(self, registry: DomainRegistry) -> None:
        self.registry = registry

    def route(self, move: LanguageMove) -> TSCall:
        domain = move.domain_hint or "ts_reasoner"
        operation = move.operation_hint or "route_unknown"

        op_meta = self.registry.find_operation(domain, operation)
        if op_meta is None:
            return TSCall(
                system=domain,
                operation="route_unknown",
                args={"raw_text": move.raw_text, "requested_operation": operation},
                risk="read_only",
                requires_confirmation=False,
                source_move=move.to_dict(),
                missing_slots=[],
            )

        required_inputs: List[str] = op_meta.get("required_inputs", [])
        missing_slots = [slot for slot in required_inputs if slot not in move.slots or move.slots.get(slot) in (None, "")]
        risk = op_meta.get("risk", "read_only")
        requires_confirmation = bool(op_meta.get("requires_confirmation", risk != "read_only"))

        return TSCall(
            system=domain,
            operation=operation,
            args=dict(move.slots),
            risk=risk,
            requires_confirmation=requires_confirmation,
            source_move=move.to_dict(),
            missing_slots=missing_slots,
        )

    def route_many(self, moves: List[LanguageMove]) -> List[TSCall]:
        return [self.route(move) for move in moves]
