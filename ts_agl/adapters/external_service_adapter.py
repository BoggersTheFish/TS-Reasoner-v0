from __future__ import annotations

from ts_agl.core.types import ResultPacket, TSCall


class ExternalServiceAdapter:
    """Dry-run adapter for external side-effect discipline.

    This adapter intentionally performs no network request. It proves that
    external_side_effect operations can be represented, confirmed, dispatched,
    and receipted without giving language autonomous side-effect authority.
    """

    def execute(self, call: TSCall) -> ResultPacket:
        if call.operation == "send_notification_dry_run":
            recipient = call.args.get("recipient")
            message = call.args.get("message")

            missing = []
            if not recipient:
                missing.append("recipient")
            if not message:
                missing.append("message")

            if missing:
                return ResultPacket(
                    status="missing_slots",
                    system=call.system,
                    operation=call.operation,
                    data={"missing_slots": missing},
                    mutated_state=False,
                )

            return ResultPacket(
                status="success",
                system=call.system,
                operation=call.operation,
                data={
                    "recipient": recipient,
                    "message": message,
                    "risk": call.risk,
                    "requires_confirmation": call.requires_confirmation,
                    "external_side_effect_declared": True,
                    "dry_run": True,
                    "network_call_performed": False,
                    "language_layer_is_proof_authority": False,
                },
                mutated_state=False,
            )

        return ResultPacket(
            status="failed",
            system=call.system,
            operation=call.operation,
            error=f"Unknown external service operation: {call.operation}",
            mutated_state=False,
        )
