"""Bounded belief-revision candidates for TS-Chat v6.5.0.

Revision candidates are candidate repair actions, not proof.

Scope:
- built on v6.4 contradiction repair targets
- produces inspectable candidate actions
- preserves support paths/provenance where available
- never auto-accepts generated text or repair suggestions
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from ts_chat.repair_memory import get_repair_target
from ts_chat.sessions import ChatSession


SCHEMA = "ts_chat_revision_candidates_v1"
RELEASE = "v6.5.0"


@dataclass(frozen=True)
class RevisionCandidate:
    candidate_id: str
    repair_id: str
    claim_text: str
    action: str
    description: str
    requires_user_confirmation: bool = True
    requires_typed_verifier: bool = True
    creates_proof: bool = False
    auto_accept: bool = False


def _candidate(
    candidate_id: str,
    repair_id: str,
    claim_text: str,
    action: str,
    description: str,
) -> RevisionCandidate:
    return RevisionCandidate(
        candidate_id=candidate_id,
        repair_id=repair_id,
        claim_text=claim_text,
        action=action,
        description=description,
        requires_user_confirmation=True,
        requires_typed_verifier=True,
        creates_proof=False,
        auto_accept=False,
    )


def generate_revision_candidates(
    session: ChatSession,
    repair_id: str,
    contradiction_trace: dict[str, Any] | None = None,
) -> dict[str, Any]:
    target = get_repair_target(session, repair_id)

    support_path = []
    contradiction_type = "unknown"
    if contradiction_trace is not None:
        support_path = list(contradiction_trace.get("support_path", []))
        contradiction_type = str(contradiction_trace.get("contradiction_type", "unknown"))

    candidates = [
        _candidate(
            "revision_001",
            repair_id,
            target.claim_text,
            "reject_new_claim",
            "Keep the contradictory/unsupported claim rejected unless typed support changes.",
        ),
        _candidate(
            "revision_002",
            repair_id,
            target.claim_text,
            "challenge_existing_support_path",
            "Inspect the existing support path that caused the contradiction and mark a premise disputed only if independently justified.",
        ),
        _candidate(
            "revision_003",
            repair_id,
            target.claim_text,
            "split_or_refine_subject",
            "Split or refine the subject/object into a narrower bounded claim before re-verification.",
        ),
        _candidate(
            "revision_004",
            repair_id,
            target.claim_text,
            "request_typed_support",
            "Ask for verifier-checkable support before allowing the claim into common ground.",
        ),
        _candidate(
            "revision_005",
            repair_id,
            target.claim_text,
            "keep_open_repair_target",
            "Leave the repair target open and preserve it for later repair memory.",
        ),
    ]

    candidate_dicts = [asdict(candidate) for candidate in candidates]

    return {
        "schema": SCHEMA,
        "release": RELEASE,
        "session_id": session.session_id,
        "repair_id": repair_id,
        "claim_text": target.claim_text,
        "repair_reason": target.reason,
        "repair_status": target.status,
        "contradiction_type": contradiction_type,
        "support_path": support_path,
        "candidate_count": len(candidate_dicts),
        "candidates": candidate_dicts,
        "all_candidates_require_user_confirmation": all(
            candidate["requires_user_confirmation"] is True for candidate in candidate_dicts
        ),
        "all_candidates_require_typed_verifier": all(
            candidate["requires_typed_verifier"] is True for candidate in candidate_dicts
        ),
        "all_candidates_create_no_proof": all(
            candidate["creates_proof"] is False for candidate in candidate_dicts
        ),
        "all_candidates_not_auto_accepted": all(
            candidate["auto_accept"] is False for candidate in candidate_dicts
        ),
        "creates_proof": False,
        "proof_authority": "typed_verifier",
        "external_llm_used": False,
    }


def revision_candidate_bundle_valid(bundle: dict[str, Any]) -> bool:
    required = {
        "schema",
        "release",
        "session_id",
        "repair_id",
        "claim_text",
        "candidate_count",
        "candidates",
        "all_candidates_require_user_confirmation",
        "all_candidates_require_typed_verifier",
        "all_candidates_create_no_proof",
        "all_candidates_not_auto_accepted",
        "creates_proof",
        "proof_authority",
        "external_llm_used",
    }

    if not required.issubset(bundle):
        return False

    if bundle["schema"] != SCHEMA:
        return False

    if bundle["release"] != RELEASE:
        return False

    if bundle["creates_proof"] is not False:
        return False

    if bundle["proof_authority"] != "typed_verifier":
        return False

    if bundle["external_llm_used"] is not False:
        return False

    if bundle["candidate_count"] != len(bundle["candidates"]):
        return False

    if bundle["candidate_count"] == 0:
        return False

    if bundle["all_candidates_require_user_confirmation"] is not True:
        return False

    if bundle["all_candidates_require_typed_verifier"] is not True:
        return False

    if bundle["all_candidates_create_no_proof"] is not True:
        return False

    if bundle["all_candidates_not_auto_accepted"] is not True:
        return False

    return True


def revision_candidates_do_not_accept_claim(session: ChatSession, bundle: dict[str, Any]) -> bool:
    return bundle["claim_text"] not in session.accepted_claim_texts()


def candidate_graph_contamination_count(session: ChatSession, bundle: dict[str, Any]) -> int:
    """Count revision candidates that incorrectly became accepted claims."""
    accepted = set(session.accepted_claim_texts())
    count = 0

    for candidate in bundle["candidates"]:
        if candidate["claim_text"] in accepted and candidate["creates_proof"] is False:
            count += 1

    return count
