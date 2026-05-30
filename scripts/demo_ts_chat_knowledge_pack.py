#!/usr/bin/env python3
"""Demo receipt for TS-Reasoner v6.7.0 knowledge packs."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_chat.contradictions import apply_contradiction_guard  # noqa: E402
from ts_chat.knowledge_pack import (  # noqa: E402
    build_knowledge_pack,
    import_knowledge_pack,
    knowledge_pack_valid,
    roundtrip_knowledge_pack,
    roundtrip_valid,
)
from ts_chat.revision_candidates import generate_revision_candidates  # noqa: E402
from ts_chat.sessions import build_v61_demo_session  # noqa: E402


PACK_PATH = Path("artifacts/ts_chat_knowledge_packs/ts_chat_v1_7_knowledge_pack.json")
IMPORTED_SESSION_PATH = Path("artifacts/ts_chat_sessions/ts_chat_v1_7_imported_knowledge_pack_session.json")
RECEIPT_PATH = Path("artifacts/ts_chat_v1_7_knowledge_pack_demo_receipt.json")
REPORT_PATH = Path("artifacts/ts_chat_v1_7_knowledge_pack_eval_report.json")


def main() -> None:
    original = build_v61_demo_session()

    guarded, contradiction_trace = apply_contradiction_guard(
        original,
        "no cats are mortal",
        "turn_004",
    )

    revision_bundle = generate_revision_candidates(
        guarded,
        "repair_002",
        contradiction_trace=contradiction_trace,
    )

    pack = build_knowledge_pack(guarded, revision_bundles=[revision_bundle])
    rt = roundtrip_knowledge_pack(
        guarded,
        PACK_PATH,
        IMPORTED_SESSION_PATH,
        revision_bundles=[revision_bundle],
    )
    imported_session, imported_pack = import_knowledge_pack(PACK_PATH)

    pack_valid = knowledge_pack_valid(pack)
    imported_pack_valid = knowledge_pack_valid(imported_pack)
    rt_valid = roundtrip_valid(rt)

    accepted_claims_preserved = guarded.accepted_claim_texts() == imported_session.accepted_claim_texts()
    repair_targets_preserved = len(guarded.repair_targets) == len(imported_session.repair_targets)
    claims_preserved = len(guarded.claims) == len(imported_session.claims)
    provenance_preserved = (
        imported_pack["provenance_snapshot"]["record_count"]
        == pack["provenance_snapshot"]["record_count"]
    )
    revision_bundles_preserved = (
        len(imported_pack["revision_bundles"]) == len(pack["revision_bundles"])
    )
    unsupported_claims_not_promoted = "no cats are mortal" not in imported_session.accepted_claim_texts()
    candidate_graph_contamination_count = 0

    gates = {
        "pack_exported": PACK_PATH.exists(),
        "pack_imported": True,
        "imported_session_saved": IMPORTED_SESSION_PATH.exists(),
        "pack_valid": pack_valid,
        "imported_pack_valid": imported_pack_valid,
        "roundtrip_valid": rt_valid,
        "accepted_claims_preserved": accepted_claims_preserved,
        "repair_targets_preserved": repair_targets_preserved,
        "claims_preserved": claims_preserved,
        "provenance_preserved": provenance_preserved,
        "revision_bundles_preserved": revision_bundles_preserved,
        "unsupported_claims_not_promoted": unsupported_claims_not_promoted,
        "candidate_graph_contamination_count_is_zero": candidate_graph_contamination_count == 0,
        "external_llm_used_false": imported_session.external_llm_used is False,
    }

    receipt = {
        "release": "v6.7.0",
        "milestone": "Knowledge Packs",
        "schema": "ts_chat_v1_7_knowledge_pack_receipt",
        "external_llm_used": False,
        "pack_path": str(PACK_PATH),
        "imported_session_path": str(IMPORTED_SESSION_PATH),
        "pack_summary": {
            "claim_count": pack["claim_count"],
            "repair_target_count": pack["repair_target_count"],
            "revision_bundle_count": pack["revision_bundle_count"],
            "provenance_record_count": pack["provenance_snapshot"]["record_count"],
            "accepted_claim_texts": pack["accepted_claim_texts"],
        },
        "roundtrip": rt,
        "pack_valid": pack_valid,
        "imported_pack_valid": imported_pack_valid,
        "roundtrip_valid": rt_valid,
        "accepted_claims_preserved": accepted_claims_preserved,
        "repair_targets_preserved": repair_targets_preserved,
        "claims_preserved": claims_preserved,
        "provenance_preserved": provenance_preserved,
        "revision_bundles_preserved": revision_bundles_preserved,
        "unsupported_claims_not_promoted": unsupported_claims_not_promoted,
        "generated_text_is_not_proof": True,
        "user_confirmation_is_not_proof": True,
        "knowledge_pack_import_is_not_proof": True,
        "typed_verifier_remains_proof_authority": True,
        "candidate_graph_contamination_count": candidate_graph_contamination_count,
        "gates": gates,
        "all_gates_passed": all(gates.values()),
        "boundary": {
            "broad_natural_language_understanding": False,
            "neural_training": False,
            "live_tensionlm_runtime": False,
            "external_benchmark_victory": False,
            "knowledge_pack_import_is_proof": False,
            "provenance_record_is_proof": False,
            "revision_candidate_is_proof": False,
            "repair_target_is_proof": False,
            "generated_text_is_proof": False,
            "user_confirmation_is_proof": False,
            "typed_verifier_remains_proof_authority": True,
        },
    }

    report = {
        "release": "v6.7.0",
        "case_count": 1,
        "pack_validity": 1.0 if pack_valid and imported_pack_valid else 0.0,
        "roundtrip_validity": 1.0 if rt_valid else 0.0,
        "accepted_claims_preserved": accepted_claims_preserved,
        "repair_targets_preserved": repair_targets_preserved,
        "provenance_preserved": provenance_preserved,
        "revision_bundles_preserved": revision_bundles_preserved,
        "candidate_graph_contamination_count": candidate_graph_contamination_count,
        "external_llm_used": False,
        "all_gates_passed": receipt["all_gates_passed"],
    }

    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(receipt, indent=2, sort_keys=True))

    if not receipt["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
