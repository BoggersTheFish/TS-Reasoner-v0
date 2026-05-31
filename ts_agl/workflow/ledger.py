from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time

from ts_agl.core.types import ResultPacket, TSCall, stable_id
from ts_agl.router import Dispatcher


def build_confirmation_token(call: TSCall) -> str:
    """Build a deterministic confirmation token for a staged call.

    This is not a security token. It is a traceable confirmation handle for
    the bounded local workflow ledger.
    """

    return stable_id(
        "confirm",
        {
            "call_id": call.call_id,
            "system": call.system,
            "operation": call.operation,
            "args": call.args,
            "risk": call.risk,
        },
    )


@dataclass
class WorkflowEvent:
    event_type: str
    action_id: str
    status: str
    message: str
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, object]:
        return {
            "event_type": self.event_type,
            "action_id": self.action_id,
            "status": self.status,
            "message": self.message,
            "created_at": self.created_at,
        }


@dataclass
class PendingAction:
    action_id: str
    call: TSCall
    confirmation_token: str
    status: str = "pending"
    created_at: float = field(default_factory=time.time)
    executed_at: Optional[float] = None
    result: Optional[ResultPacket] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "action_id": self.action_id,
            "call": self.call.to_dict(),
            "confirmation_token": self.confirmation_token,
            "status": self.status,
            "created_at": self.created_at,
            "executed_at": self.executed_at,
            "result": self.result.to_dict() if self.result else None,
        }


class WorkflowLedger:
    """Multi-turn pending action ledger for TS-AGL.

    v15.0 proves the system can hold an action as pending, block execution
    without the expected confirmation token, execute after confirmation, and
    record a replayable event ledger.
    """

    def __init__(self) -> None:
        self.pending_actions: Dict[str, PendingAction] = {}
        self.events: List[WorkflowEvent] = []

    def stage_call(self, call: TSCall) -> PendingAction:
        action_id = stable_id(
            "action",
            {
                "call_id": call.call_id,
                "system": call.system,
                "operation": call.operation,
                "args": call.args,
            },
        )
        pending = PendingAction(
            action_id=action_id,
            call=call,
            confirmation_token=build_confirmation_token(call),
        )
        self.pending_actions[action_id] = pending
        self.events.append(
            WorkflowEvent(
                event_type="stage",
                action_id=action_id,
                status="pending",
                message=f"Staged {call.system}.{call.operation} with risk {call.risk}.",
            )
        )
        return pending

    def get_pending(self, action_id: str) -> Optional[PendingAction]:
        return self.pending_actions.get(action_id)

    def attempt_execute(
        self,
        action_id: str,
        dispatcher: Dispatcher,
        confirmation_token: Optional[str] = None,
    ) -> ResultPacket:
        pending = self.pending_actions.get(action_id)
        if pending is None:
            result = ResultPacket(
                status="failed",
                system="workflow",
                operation="execute_pending_action",
                error=f"No pending action found: {action_id}",
                mutated_state=False,
            )
            self.events.append(
                WorkflowEvent(
                    event_type="execute_missing",
                    action_id=action_id,
                    status=result.status,
                    message=result.error or "missing pending action",
                )
            )
            return result

        call = pending.call
        requires_confirmation = call.requires_confirmation or call.risk != "read_only"
        token_matches = confirmation_token == pending.confirmation_token

        if requires_confirmation and not token_matches:
            result = ResultPacket(
                status="needs_confirmation",
                system=call.system,
                operation=call.operation,
                data={
                    "action_id": action_id,
                    "risk": call.risk,
                    "requires_confirmation": True,
                    "confirmation_token_required": True,
                    "confirmation_token_matched": False,
                },
                mutated_state=False,
            )
            self.events.append(
                WorkflowEvent(
                    event_type="execute_blocked",
                    action_id=action_id,
                    status=result.status,
                    message="Execution blocked because confirmation token was missing or wrong.",
                )
            )
            return result

        result = dispatcher.dispatch(call, confirmed=True)
        pending.result = result

        if result.status == "success":
            pending.status = "executed"
            pending.executed_at = time.time()
        else:
            pending.status = "failed"

        self.events.append(
            WorkflowEvent(
                event_type="execute_confirmed",
                action_id=action_id,
                status=result.status,
                message=f"Confirmed execution returned {result.status}.",
            )
        )
        return result

    def to_dict(self) -> Dict[str, object]:
        return {
            "pending_actions": {
                action_id: pending.to_dict()
                for action_id, pending in sorted(self.pending_actions.items())
            },
            "events": [event.to_dict() for event in self.events],
            "event_count": len(self.events),
            "pending_count": sum(1 for p in self.pending_actions.values() if p.status == "pending"),
            "executed_count": sum(1 for p in self.pending_actions.values() if p.status == "executed"),
            "failed_count": sum(1 for p in self.pending_actions.values() if p.status == "failed"),
        }
