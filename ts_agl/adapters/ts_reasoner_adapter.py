from __future__ import annotations

from ts_agl.core.types import ResultPacket, TSCall


class TSReasonerAdapter:
    """Bounded TS-Reasoner shim for AGL v0.

    This adapter does not claim broad reasoning. It proves the call boundary:
    language can route into reasoner-shaped operations without becoming proof authority.
    """

    def execute(self, call: TSCall) -> ResultPacket:
        if call.operation == "check_support":
            claim = call.args.get("claim")
            if not claim:
                return ResultPacket(
                    status="missing_slots",
                    system=call.system,
                    operation=call.operation,
                    data={"missing_slots": ["claim"]},
                    mutated_state=False,
                )
            return ResultPacket(
                status="abstained",
                system=call.system,
                operation=call.operation,
                data={
                    "claim": claim,
                    "supported": False,
                    "reason": "AGL v0 routed the request, but no live verifier graph was bound to this adapter.",
                    "language_layer_is_proof_authority": False,
                },
                mutated_state=False,
            )

        if call.operation == "explain_rejection":
            return ResultPacket(
                status="success",
                system=call.system,
                operation=call.operation,
                data={
                    "target": call.args.get("claim_id", "last_rejected_claim"),
                    "explanation": "The language layer can ask for a rejection explanation, but v0 needs a bound TS-Reasoner session to retrieve the exact trace.",
                    "language_layer_is_proof_authority": False,
                },
                mutated_state=False,
            )

        if call.operation == "summarize_session":
            return ResultPacket(
                status="success",
                system=call.system,
                operation=call.operation,
                data={
                    "summary": "TS-AGL v0 is active: language moves can route to TS-shaped operations, git operations, and filesystem operations. Durable proof/state promotion remains outside the language layer.",
                    "accepted_graph_changed": False,
                },
                mutated_state=False,
            )

        if call.operation == "correct_candidate":
            return ResultPacket(
                status="success",
                system=call.system,
                operation=call.operation,
                data={
                    "correction_recorded_as_candidate": True,
                    "replacement": call.args.get("replacement"),
                    "accepted_graph_changed": False,
                },
                mutated_state=False,
            )

        if call.operation == "route_unknown":
            return ResultPacket(
                status="abstained",
                system=call.system,
                operation=call.operation,
                data={
                    "reason": "No confident AGL route found.",
                    "raw_text": call.args.get("raw_text"),
                },
                mutated_state=False,
            )

        return ResultPacket(
            status="failed",
            system=call.system,
            operation=call.operation,
            error=f"Unknown TS-Reasoner operation: {call.operation}",
            mutated_state=False,
        )
