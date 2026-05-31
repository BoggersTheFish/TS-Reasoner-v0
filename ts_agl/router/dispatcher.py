from __future__ import annotations

from typing import Dict

from ts_agl.adapters.filesystem_adapter import FilesystemAdapter
from ts_agl.adapters.git_adapter import GitAdapter
from ts_agl.adapters.ts_reasoner_adapter import TSReasonerAdapter
from ts_agl.adapters.external_service_adapter import ExternalServiceAdapter
from ts_agl.core.types import ResultPacket, TSCall
from ts_agl.router.risk_gate import gate_call


class Dispatcher:
    """Executes TSCall objects through concrete adapters."""

    def __init__(self) -> None:
        self.adapters: Dict[str, object] = {
            "git_repo": GitAdapter(),
            "filesystem": FilesystemAdapter(),
            "ts_reasoner": TSReasonerAdapter(),
            "external_service": ExternalServiceAdapter(),
        }

    def dispatch(self, call: TSCall, confirmed: bool = False) -> ResultPacket:
        gated = gate_call(call, confirmed=confirmed)
        if gated is not None:
            return gated

        adapter = self.adapters.get(call.system)
        if adapter is None:
            return ResultPacket(
                status="failed",
                system=call.system,
                operation=call.operation,
                error=f"No adapter registered for system: {call.system}",
                mutated_state=False,
            )

        execute = getattr(adapter, "execute", None)
        if execute is None:
            return ResultPacket(
                status="failed",
                system=call.system,
                operation=call.operation,
                error=f"Adapter has no execute method: {call.system}",
                mutated_state=False,
            )

        return execute(call)
