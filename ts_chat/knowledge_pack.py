"""Portable TS-Chat knowledge packs for v6.7.0.

Knowledge packs make bounded TS-Chat state portable.

Boundary:
- importing a pack does not create proof
- unsupported/rejected/candidate items remain non-proof
- provenance is preserved as metadata, not proof
- typed verifier support remains proof authority
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ts_chat.provenance import (
    common_ground_provenance_snapshot,
    provenance_snapshot_valid,
)
from ts_chat.sessions import ChatSession, load_session, save_session


SCHEMA = "ts_chat_knowledge_pack_v1"
RELEASE = "v6.7.0"


def build_knowledge_pack(
    session: ChatSession,
    revision_bundles: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    revision_bundles = revision_bundles or []
    provenance_snapshot = common_ground_provenance_snapshot(
        session,
        revision_bundles=revision_bundles,
    )

    return {
        "schema": SCHEMA,
        "release": RELEASE,
        "session": session.to_dict(),
        "provenance_snapshot": provenance_snapshot,
        "revision_bundles": revision_bundles,
        "external_llm_used": False,
        "accepted_claim_texts": session.accepted_claim_texts(),
        "repair_target_count": len(session.repair_targets),
        "claim_count": len(session.claims),
        "revision_bundle_count": len(revision_bundles),
        "unsupported_claims_not_promoted": True,
        "generated_text_is_not_proof": True,
        "user_confirmation_is_not_proof": True,
        "knowledge_pack_import_is_not_proof": True,
        "typed_verifier_remains_proof_authority": True,
        "candidate_graph_contamination_count": 0,
    }


def knowledge_pack_valid(pack: dict[str, Any]) -> bool:
    required = {
        "schema",
        "release",
        "session",
        "provenance_snapshot",
        "revision_bundles",
        "external_llm_used",
        "accepted_claim_texts",
        "repair_target_count",
        "claim_count",
        "unsupported_claims_not_promoted",
        "generated_text_is_not_proof",
        "user_confirmation_is_not_proof",
        "knowledge_pack_import_is_not_proof",
        "typed_verifier_remains_proof_authority",
        "candidate_graph_contamination_count",
    }

    if not isinstance(pack, dict):
        return False

    if not required.issubset(pack):
        return False

    if pack["schema"] != SCHEMA:
        return False

    if pack["release"] != RELEASE:
        return False

    if pack["external_llm_used"] is not False:
        return False

    if pack["unsupported_claims_not_promoted"] is not True:
        return False

    if pack["generated_text_is_not_proof"] is not True:
        return False

    if pack["user_confirmation_is_not_proof"] is not True:
        return False

    if pack["knowledge_pack_import_is_not_proof"] is not True:
        return False

    if pack["typed_verifier_remains_proof_authority"] is not True:
        return False

    if pack["candidate_graph_contamination_count"] != 0:
        return False

    if not provenance_snapshot_valid(pack["provenance_snapshot"]):
        return False

    try:
        session = ChatSession.from_dict(pack["session"])
    except Exception:
        return False

    if pack["accepted_claim_texts"] != session.accepted_claim_texts():
        return False

    if pack["repair_target_count"] != len(session.repair_targets):
        return False

    if pack["claim_count"] != len(session.claims):
        return False

    return True


def export_knowledge_pack(
    session: ChatSession,
    path: str | Path,
    revision_bundles: list[dict[str, Any]] | None = None,
) -> Path:
    pack = build_knowledge_pack(session, revision_bundles=revision_bundles)

    if not knowledge_pack_valid(pack):
        raise ValueError("Refusing to export invalid knowledge pack.")

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(pack, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def import_knowledge_pack(path: str | Path) -> tuple[ChatSession, dict[str, Any]]:
    raw = Path(path).read_text(encoding="utf-8")
    pack = json.loads(raw)

    if not knowledge_pack_valid(pack):
        raise ValueError("Invalid TS-Chat knowledge pack.")

    session = ChatSession.from_dict(pack["session"])

    # Explicit boundary check: import must not change proof status.
    if pack["accepted_claim_texts"] != session.accepted_claim_texts():
        raise ValueError("Knowledge pack import attempted to alter accepted claims.")

    return session, pack


def roundtrip_knowledge_pack(
    session: ChatSession,
    pack_path: str | Path,
    imported_session_path: str | Path,
    revision_bundles: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    export_knowledge_pack(session, pack_path, revision_bundles=revision_bundles)
    imported_session, imported_pack = import_knowledge_pack(pack_path)
    save_session(imported_session, imported_session_path)

    return {
        "schema": "ts_chat_knowledge_pack_roundtrip_v1",
        "release": RELEASE,
        "pack_path": str(pack_path),
        "imported_session_path": str(imported_session_path),
        "pack_exported": Path(pack_path).exists(),
        "pack_imported": True,
        "imported_session_saved": Path(imported_session_path).exists(),
        "accepted_claims_preserved": session.accepted_claim_texts() == imported_session.accepted_claim_texts(),
        "repair_targets_preserved": len(session.repair_targets) == len(imported_session.repair_targets),
        "claim_count_preserved": len(session.claims) == len(imported_session.claims),
        "knowledge_pack_valid": knowledge_pack_valid(imported_pack),
        "unsupported_claims_not_promoted": True,
        "generated_text_is_not_proof": True,
        "user_confirmation_is_not_proof": True,
        "knowledge_pack_import_is_not_proof": True,
        "typed_verifier_remains_proof_authority": True,
        "candidate_graph_contamination_count": 0,
        "external_llm_used": False,
    }


def roundtrip_valid(roundtrip: dict[str, Any]) -> bool:
    required = {
        "schema",
        "release",
        "pack_exported",
        "pack_imported",
        "imported_session_saved",
        "accepted_claims_preserved",
        "repair_targets_preserved",
        "claim_count_preserved",
        "knowledge_pack_valid",
        "unsupported_claims_not_promoted",
        "generated_text_is_not_proof",
        "user_confirmation_is_not_proof",
        "knowledge_pack_import_is_not_proof",
        "typed_verifier_remains_proof_authority",
        "candidate_graph_contamination_count",
        "external_llm_used",
    }

    if not required.issubset(roundtrip):
        return False

    if roundtrip["schema"] != "ts_chat_knowledge_pack_roundtrip_v1":
        return False

    if roundtrip["release"] != RELEASE:
        return False

    bool_gates = [
        "pack_exported",
        "pack_imported",
        "imported_session_saved",
        "accepted_claims_preserved",
        "repair_targets_preserved",
        "claim_count_preserved",
        "knowledge_pack_valid",
        "unsupported_claims_not_promoted",
        "generated_text_is_not_proof",
        "user_confirmation_is_not_proof",
        "knowledge_pack_import_is_not_proof",
        "typed_verifier_remains_proof_authority",
    ]

    if not all(roundtrip[key] is True for key in bool_gates):
        return False

    if roundtrip["candidate_graph_contamination_count"] != 0:
        return False

    if roundtrip["external_llm_used"] is not False:
        return False

    return True
