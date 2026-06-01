from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict
import os

from ts_agl.core.types import ResultPacket, stable_id


EXTERNAL_LIVE_ENV_VAR = "TS_AGL_ALLOW_EXTERNAL_LIVE"


def build_external_confirmation_token(
    service: str,
    operation: str,
    payload: Dict[str, Any],
    mode: str,
) -> str:
    """Deterministic confirmation handle for external adapter gate tests.

    This is not a secret. It is a traceable confirmation token proving that a
    high-risk external action was explicitly acknowledged by the caller.
    """

    return stable_id(
        "external_confirm",
        {
            "service": service,
            "operation": operation,
            "payload": payload,
            "mode": mode,
        },
    )


@dataclass(frozen=True)
class ExternalAdapterRequest:
    service: str
    operation: str
    payload: Dict[str, Any] = field(default_factory=dict)
    mode: str = "dry_run"
    risk: str = "external_side_effect"
    requires_confirmation: bool = True

    @property
    def confirmation_token(self) -> str:
        return build_external_confirmation_token(
            service=self.service,
            operation=self.operation,
            payload=self.payload,
            mode=self.mode,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service": self.service,
            "operation": self.operation,
            "payload": self.payload,
            "mode": self.mode,
            "risk": self.risk,
            "requires_confirmation": self.requires_confirmation,
            "confirmation_token": self.confirmation_token,
        }


class ExternalAdapterGate:
    """Controlled external adapter gate.

    The gate does not perform real network activity. It only decides whether an
    external-side-effect request is blocked, dry-run accepted, or live-gate
    authorized for a downstream adapter.

    Boundary:
    - dry-run by default
    - confirmation is required
    - live mode is blocked unless TS_AGL_ALLOW_EXTERNAL_LIVE=1
    - gate authorization is not execution
    - no network call is performed here
    """

    def __init__(self, live_env_var: str = EXTERNAL_LIVE_ENV_VAR) -> None:
        self.live_env_var = live_env_var

    def evaluate(
        self,
        request: ExternalAdapterRequest,
        confirmation_token: str | None = None,
    ) -> ResultPacket:
        if request.mode not in {"dry_run", "live"}:
            return ResultPacket(
                status="failed",
                system=request.service,
                operation=request.operation,
                error=f"Unsupported external adapter mode: {request.mode}",
                data={
                    "mode": request.mode,
                    "network_call_performed": False,
                    "external_side_effect_performed": False,
                },
                mutated_state=False,
            )

        token_matches = confirmation_token == request.confirmation_token
        if request.requires_confirmation and not token_matches:
            return ResultPacket(
                status="needs_confirmation",
                system=request.service,
                operation=request.operation,
                data={
                    "mode": request.mode,
                    "risk": request.risk,
                    "requires_confirmation": True,
                    "confirmation_token_required": True,
                    "confirmation_token_matched": False,
                    "network_call_performed": False,
                    "external_side_effect_performed": False,
                    "live_gate_open": False,
                },
                mutated_state=False,
            )

        if request.mode == "dry_run":
            return ResultPacket(
                status="success",
                system=request.service,
                operation=request.operation,
                data={
                    "mode": "dry_run",
                    "risk": request.risk,
                    "requires_confirmation": request.requires_confirmation,
                    "confirmation_token_matched": True,
                    "dry_run": True,
                    "live_gate_open": False,
                    "network_call_performed": False,
                    "external_side_effect_performed": False,
                    "payload": request.payload,
                },
                mutated_state=False,
            )

        live_env_value = os.environ.get(self.live_env_var)
        if live_env_value != "1":
            return ResultPacket(
                status="external_live_blocked",
                system=request.service,
                operation=request.operation,
                data={
                    "mode": "live",
                    "risk": request.risk,
                    "requires_confirmation": request.requires_confirmation,
                    "confirmation_token_matched": True,
                    "required_env_var": self.live_env_var,
                    "required_env_value": "1",
                    "actual_env_value": live_env_value,
                    "live_gate_open": False,
                    "network_call_performed": False,
                    "external_side_effect_performed": False,
                },
                mutated_state=False,
            )

        return ResultPacket(
            status="live_gate_authorized",
            system=request.service,
            operation=request.operation,
            data={
                "mode": "live",
                "risk": request.risk,
                "requires_confirmation": request.requires_confirmation,
                "confirmation_token_matched": True,
                "required_env_var": self.live_env_var,
                "required_env_value": "1",
                "actual_env_value": live_env_value,
                "live_gate_open": True,
                "gate_authorizes_downstream_adapter": True,
                "gate_performs_network_call": False,
                "network_call_performed": False,
                "external_side_effect_performed": False,
                "payload": request.payload,
            },
            mutated_state=False,
        )
