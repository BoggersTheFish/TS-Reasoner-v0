"""Typed explanation traces for TS-Chat v6.3.0.

Explanations are inspectable traces, not proof.
They expose why a claim is accepted, unsupported, rejected, or repairable.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from ts_chat.repair_memory import get_repair_target, revisit_repair_target
from ts_chat.sessions import ChatClaim, ChatSession


SCHEMA = "ts_chat_explanation_trace_v1"
RELEASE = "v6.3.0"


def _claim_to_trace(session: ChatSession, claim: ChatClaim) -> dict[str, Any]:
    accepted = claim.status == "accepted"
    support_paths = claim.support_paths or []
    verifier_channels = claim.verifier_channels or []

    if accepted:
        decision = "accepted"
        reason = "claim is accepted in common ground"
        if support_paths:
            reason = "typed support path found"
        elif verifier_channels:
            reason = "accepted through recorded verifier/common-ground channel"
    elif claim.status == "unsupported":
        decision = "unsupported"
        reason = "missing typed verifier support"
    elif claim.status == "candidate":
        decision = "candidate"
        reason = "candidate claim requires typed verifier support before acceptance"
    elif claim.status == "rejected":
        decision = "rejected"
        reason = "claim is rejected or blocked by current verifier state"
    elif claim.status == "abstained":
        decision = "abstained"
        reason = "system abstained because support was insufficient"
    else:
        decision = "unknown"
        reason = "unknown claim status"

    return {
        "schema": SCHEMA,
        "release": RELEASE,
        "session_id": session.session_id,
        "trace_type": "claim_decision",
        "claim_id": claim.claim_id,
        "claim_text": claim.text,
        "status": claim.status,
        "decision": decision,
        "reason": reason,
        "source": claim.source,
        "turn_id": claim.turn_id,
        "support_paths": support_paths,
        "verifier_channels": verifier_channels,
        "creates_proof": False,
        "proof_authority": "typed_verifier",
        "external_llm_used": False,
    }


def explain_claim(session: ChatSession, claim_text: str) -> dict[str, Any]:
    for claim in session.claims:
        if claim.text == claim_text:
            return _claim_to_trace(session, claim)

    return {
        "schema": SCHEMA,
        "release": RELEASE,
        "session_id": session.session_id,
        "trace_type": "missing_claim",
        "claim_text": claim_text,
        "status": "missing",
        "decision": "abstained",
        "reason": "claim is not present in session common ground or candidates",
        "support_paths": [],
        "verifier_channels": [],
        "creates_proof": False,
        "proof_authority": "typed_verifier",
        "external_llm_used": False,
    }


def explain_repair_target(session: ChatSession, repair_id: str) -> dict[str, Any]:
    target = get_repair_target(session, repair_id)
    revisit = revisit_repair_target(session, repair_id)

    return {
        "schema": SCHEMA,
        "release": RELEASE,
        "session_id": session.session_id,
        "trace_type": "repair_target",
        "repair_id": target.repair_id,
        "claim_text": target.claim_text,
        "status": target.status,
        "reason": target.reason,
        "source_turn_id": target.source_turn_id,
        "repair_revisit": revisit,
        "support_paths": [],
        "verifier_channels": [],
        "creates_proof": False,
        "proof_authority": "typed_verifier",
        "external_llm_used": False,
    }


def explain_last_claim(session: ChatSession) -> dict[str, Any]:
    if not session.claims:
        return {
            "schema": SCHEMA,
            "release": RELEASE,
            "session_id": session.session_id,
            "trace_type": "empty_session",
            "decision": "abstained",
            "reason": "session has no claims to explain",
            "support_paths": [],
            "verifier_channels": [],
            "creates_proof": False,
            "proof_authority": "typed_verifier",
            "external_llm_used": False,
        }

    return _claim_to_trace(session, session.claims[-1])


def explanation_trace_valid(trace: dict[str, Any]) -> bool:
    required = {
        "schema",
        "release",
        "session_id",
        "trace_type",
        "reason",
        "support_paths",
        "verifier_channels",
        "creates_proof",
        "proof_authority",
        "external_llm_used",
    }

    if not required.issubset(trace):
        return False

    if trace["schema"] != SCHEMA:
        return False

    if trace["creates_proof"] is not False:
        return False

    if trace["external_llm_used"] is not False:
        return False

    if trace["proof_authority"] != "typed_verifier":
        return False

    if not isinstance(trace["support_paths"], list):
        return False

    if not isinstance(trace["verifier_channels"], list):
        return False

    return True


def explanation_bundle(session: ChatSession) -> dict[str, Any]:
    claim_traces = [_claim_to_trace(session, claim) for claim in session.claims]
    repair_traces = [explain_repair_target(session, target.repair_id) for target in session.repair_targets]

    traces = claim_traces + repair_traces

    return {
        "schema": "ts_chat_explanation_bundle_v1",
        "release": RELEASE,
        "session_id": session.session_id,
        "external_llm_used": False,
        "claim_trace_count": len(claim_traces),
        "repair_trace_count": len(repair_traces),
        "trace_count": len(traces),
        "traces": traces,
        "all_traces_valid": all(explanation_trace_valid(trace) for trace in traces),
        "all_traces_create_no_proof": all(trace["creates_proof"] is False for trace in traces),
        "candidate_graph_contamination_count": 0,
        "claims": [asdict(claim) for claim in session.claims],
    }
