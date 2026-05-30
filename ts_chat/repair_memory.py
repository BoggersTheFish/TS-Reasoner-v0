"""Durable repair-memory helpers for TS-Chat v6.2.0.

v6.2 builds on v6.1 persistent sessions.

Boundary:
- repair targets are memory, not proof
- repair suggestions are candidate actions, not accepted claims
- user confirmation is not proof
- typed verifier support remains proof authority
"""

from __future__ import annotations

from dataclasses import asdict, replace
from typing import Any

from ts_chat.sessions import ChatSession, RepairTarget


SCHEMA = "ts_chat_repair_memory_v1"
RELEASE = "v6.2.0"


def open_repair_targets(session: ChatSession) -> list[RepairTarget]:
    return [target for target in session.repair_targets if target.status == "open"]


def resolved_repair_targets(session: ChatSession) -> list[RepairTarget]:
    return [target for target in session.repair_targets if target.status == "resolved"]


def rejected_repair_targets(session: ChatSession) -> list[RepairTarget]:
    return [target for target in session.repair_targets if target.status == "rejected"]


def get_repair_target(session: ChatSession, repair_id: str) -> RepairTarget:
    for target in session.repair_targets:
        if target.repair_id == repair_id:
            return target
    raise KeyError(f"Repair target not found: {repair_id}")


def repair_memory_snapshot(session: ChatSession) -> dict[str, Any]:
    targets = [asdict(target) for target in session.repair_targets]
    open_targets = [target for target in targets if target["status"] == "open"]

    return {
        "schema": SCHEMA,
        "release": RELEASE,
        "session_id": session.session_id,
        "external_llm_used": False,
        "repair_target_count": len(targets),
        "open_repair_target_count": len(open_targets),
        "resolved_repair_target_count": len([target for target in targets if target["status"] == "resolved"]),
        "rejected_repair_target_count": len([target for target in targets if target["status"] == "rejected"]),
        "repair_targets": targets,
        "open_repair_targets": open_targets,
    }


def revisit_repair_target(session: ChatSession, repair_id: str) -> dict[str, Any]:
    target = get_repair_target(session, repair_id)

    return {
        "schema": "ts_chat_repair_revisit_v1",
        "release": RELEASE,
        "session_id": session.session_id,
        "repair_id": target.repair_id,
        "claim_text": target.claim_text,
        "reason": target.reason,
        "source_turn_id": target.source_turn_id,
        "status": target.status,
        "creates_proof": False,
        "candidate_actions": [
            {
                "action": "provide_typed_support",
                "description": "Add verifier-checkable support for the missing claim.",
                "creates_proof_without_verifier": False,
            },
            {
                "action": "reject_claim",
                "description": "Keep the claim rejected/unsupported if no support is available.",
                "creates_proof_without_verifier": False,
            },
            {
                "action": "split_or_refine_claim",
                "description": "Rewrite the claim into a more precise bounded form before verification.",
                "creates_proof_without_verifier": False,
            },
        ],
    }


def mark_repair_target_resolved(session: ChatSession, repair_id: str) -> ChatSession:
    """Return a copy-like session with one repair marked resolved.

    This does not accept the claim as proof. It only records repair-memory status.
    """
    updated_targets: list[RepairTarget] = []

    found = False
    for target in session.repair_targets:
        if target.repair_id == repair_id:
            updated_targets.append(replace(target, status="resolved"))
            found = True
        else:
            updated_targets.append(target)

    if not found:
        raise KeyError(f"Repair target not found: {repair_id}")

    return ChatSession(
        session_id=session.session_id,
        claims=list(session.claims),
        repair_targets=updated_targets,
        external_llm_used=False,
    )


def repair_targets_not_proof(session: ChatSession) -> bool:
    accepted = set(session.accepted_claim_texts())
    for target in session.repair_targets:
        if target.status == "open" and target.claim_text in accepted:
            return False
    return True
