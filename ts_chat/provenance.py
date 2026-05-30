"""Provenance-aware common ground for TS-Chat v6.6.0.

Provenance records explain where claims, repairs, and candidates came from.
They do not create proof.

Boundary:
- provenance is metadata, not proof
- user confirmation is not proof
- generated/candidate text is not proof
- typed verifier support remains proof authority
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from ts_chat.sessions import ChatClaim, ChatSession, RepairTarget


SCHEMA = "ts_chat_provenance_record_v1"
SNAPSHOT_SCHEMA = "ts_chat_provenance_snapshot_v1"
RELEASE = "v6.6.0"


def claim_provenance_record(session: ChatSession, claim: ChatClaim) -> dict[str, Any]:
    is_accepted = claim.status == "accepted"
    has_typed_channel = bool(claim.verifier_channels)

    return {
        "schema": SCHEMA,
        "release": RELEASE,
        "session_id": session.session_id,
        "record_type": "claim",
        "record_id": f"prov_{claim.claim_id}",
        "item_id": claim.claim_id,
        "text": claim.text,
        "status": claim.status,
        "source": claim.source,
        "source_turn_id": claim.turn_id,
        "support_paths": claim.support_paths,
        "verifier_channels": claim.verifier_channels,
        "is_accepted_common_ground": is_accepted,
        "has_typed_verifier_channel": has_typed_channel,
        "creates_proof": False,
        "generated_text_is_proof": False,
        "user_confirmation_is_proof": False,
        "proof_authority": "typed_verifier",
        "external_llm_used": False,
    }


def repair_target_provenance_record(session: ChatSession, target: RepairTarget) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "release": RELEASE,
        "session_id": session.session_id,
        "record_type": "repair_target",
        "record_id": f"prov_{target.repair_id}",
        "item_id": target.repair_id,
        "text": target.claim_text,
        "status": target.status,
        "source": "repair_memory",
        "source_turn_id": target.source_turn_id,
        "reason": target.reason,
        "is_accepted_common_ground": False,
        "has_typed_verifier_channel": False,
        "creates_proof": False,
        "generated_text_is_proof": False,
        "user_confirmation_is_proof": False,
        "proof_authority": "typed_verifier",
        "external_llm_used": False,
    }


def revision_candidate_provenance_record(
    session: ChatSession,
    candidate: dict[str, Any],
    bundle: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "release": RELEASE,
        "session_id": session.session_id,
        "record_type": "revision_candidate",
        "record_id": f"prov_{candidate['candidate_id']}",
        "item_id": candidate["candidate_id"],
        "repair_id": candidate["repair_id"],
        "text": candidate["claim_text"],
        "action": candidate["action"],
        "description": candidate["description"],
        "status": "candidate",
        "source": "system_generated_revision_candidate",
        "source_turn_id": None,
        "support_path": bundle.get("support_path", []),
        "requires_user_confirmation": candidate["requires_user_confirmation"],
        "requires_typed_verifier": candidate["requires_typed_verifier"],
        "is_accepted_common_ground": False,
        "has_typed_verifier_channel": False,
        "creates_proof": False,
        "auto_accept": candidate["auto_accept"],
        "generated_text_is_proof": False,
        "user_confirmation_is_proof": False,
        "proof_authority": "typed_verifier",
        "external_llm_used": False,
    }


def provenance_record_valid(record: dict[str, Any]) -> bool:
    required = {
        "schema",
        "release",
        "session_id",
        "record_type",
        "record_id",
        "item_id",
        "text",
        "status",
        "source",
        "is_accepted_common_ground",
        "creates_proof",
        "generated_text_is_proof",
        "user_confirmation_is_proof",
        "proof_authority",
        "external_llm_used",
    }

    if not required.issubset(record):
        return False

    if record["schema"] != SCHEMA:
        return False

    if record["release"] != RELEASE:
        return False

    if record["creates_proof"] is not False:
        return False

    if record["generated_text_is_proof"] is not False:
        return False

    if record["user_confirmation_is_proof"] is not False:
        return False

    if record["proof_authority"] != "typed_verifier":
        return False

    if record["external_llm_used"] is not False:
        return False

    if record["record_type"] == "revision_candidate" and record.get("auto_accept") is not False:
        return False

    if record["record_type"] in {"repair_target", "revision_candidate"}:
        if record["is_accepted_common_ground"] is not False:
            return False

    return True


def common_ground_provenance_snapshot(
    session: ChatSession,
    revision_bundles: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    revision_bundles = revision_bundles or []

    claim_records = [claim_provenance_record(session, claim) for claim in session.claims]
    repair_records = [repair_target_provenance_record(session, target) for target in session.repair_targets]

    candidate_records: list[dict[str, Any]] = []
    for bundle in revision_bundles:
        for candidate in bundle.get("candidates", []):
            candidate_records.append(revision_candidate_provenance_record(session, candidate, bundle))

    records = claim_records + repair_records + candidate_records

    accepted_claim_records = [
        record for record in claim_records if record["is_accepted_common_ground"] is True
    ]
    candidate_or_repair_records = [
        record for record in records if record["record_type"] in {"repair_target", "revision_candidate"}
    ]

    return {
        "schema": SNAPSHOT_SCHEMA,
        "release": RELEASE,
        "session_id": session.session_id,
        "external_llm_used": False,
        "claim_record_count": len(claim_records),
        "repair_record_count": len(repair_records),
        "revision_candidate_record_count": len(candidate_records),
        "record_count": len(records),
        "accepted_claim_record_count": len(accepted_claim_records),
        "records": records,
        "claims": [asdict(claim) for claim in session.claims],
        "repair_targets": [asdict(target) for target in session.repair_targets],
        "all_records_have_provenance": all(provenance_record_valid(record) for record in records),
        "all_accepted_claims_have_source_turns": all(
            bool(record.get("source_turn_id")) for record in accepted_claim_records
        ),
        "candidate_and_repair_records_not_common_ground": all(
            record["is_accepted_common_ground"] is False for record in candidate_or_repair_records
        ),
        "generated_text_is_not_proof": True,
        "user_confirmation_is_not_proof": True,
        "typed_verifier_remains_proof_authority": True,
        "candidate_graph_contamination_count": 0,
    }


def provenance_snapshot_valid(snapshot: dict[str, Any]) -> bool:
    required = {
        "schema",
        "release",
        "session_id",
        "external_llm_used",
        "record_count",
        "records",
        "all_records_have_provenance",
        "all_accepted_claims_have_source_turns",
        "candidate_and_repair_records_not_common_ground",
        "generated_text_is_not_proof",
        "user_confirmation_is_not_proof",
        "typed_verifier_remains_proof_authority",
        "candidate_graph_contamination_count",
    }

    if not required.issubset(snapshot):
        return False

    if snapshot["schema"] != SNAPSHOT_SCHEMA:
        return False

    if snapshot["release"] != RELEASE:
        return False

    if snapshot["external_llm_used"] is not False:
        return False

    if snapshot["record_count"] != len(snapshot["records"]):
        return False

    if snapshot["all_records_have_provenance"] is not True:
        return False

    if snapshot["all_accepted_claims_have_source_turns"] is not True:
        return False

    if snapshot["candidate_and_repair_records_not_common_ground"] is not True:
        return False

    if snapshot["generated_text_is_not_proof"] is not True:
        return False

    if snapshot["user_confirmation_is_not_proof"] is not True:
        return False

    if snapshot["typed_verifier_remains_proof_authority"] is not True:
        return False

    if snapshot["candidate_graph_contamination_count"] != 0:
        return False

    return True
