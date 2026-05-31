from __future__ import annotations

from ts_agl.core.types import ResultPacket, TSCall


def gate_call(call: TSCall, confirmed: bool = False) -> ResultPacket | None:
    """Return a ResultPacket if execution must stop, otherwise None."""

    if call.missing_slots:
        return ResultPacket(
            status="missing_slots",
            system=call.system,
            operation=call.operation,
            data={"missing_slots": call.missing_slots, "call": call.to_dict()},
            mutated_state=False,
        )

    if call.risk != "read_only" and not confirmed:
        return ResultPacket(
            status="needs_confirmation",
            system=call.system,
            operation=call.operation,
            data={"risk": call.risk, "call": call.to_dict()},
            mutated_state=False,
        )

    if call.requires_confirmation and not confirmed:
        return ResultPacket(
            status="needs_confirmation",
            system=call.system,
            operation=call.operation,
            data={"risk": call.risk, "call": call.to_dict()},
            mutated_state=False,
        )

    return None
