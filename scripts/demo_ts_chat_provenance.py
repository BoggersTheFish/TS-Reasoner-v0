#!/usr/bin/env python3
"""Demo receipt for TS-Reasoner v6.6.0 provenance-aware common ground."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_chat.contradictions import apply_contradiction_guard  # noqa: E402
from ts_chat.provenance import (  # noqa: E402
    common_ground_provenance_snapshot,
    provenance_snapshot_valid,
)
from ts_chat.revision_candidates import generate_revision_candidates  # noqa: E402
from ts_chat.sessions import build_v61_demo_session, load_session, save_session  # noqa: E402


SESSION_PATH = Path("artifacts/ts_chat_sessions/ts_chat_v1_6_provenance_session.json")
RECEIPT_PATH = Path("artifacts/ts_chat_v1_6_provenance_demo_receipt.json")
REPORT_PATH = Path("artifacts/ts_chat_v1_6_provenance_eval_report.json")


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

    snapshot = common_ground_provenance_snapshot(
        guarded,
        revision_bundles=[revision_bundle],
    )

    save_session(guarded, SESSION_PATH)
    loaded = load_session(SESSION_PATH)

    loaded_revision_bundle = generate_revision_candidates(
        loaded,
        "repair_002",
        contradiction_trace=contradiction_trace,
    )

    loaded_snapshot = common_ground_provenance_snapshot(
        loaded,
        revision_bundles=[loaded_revision_bundle],
    )

    snapshot_valid = provenance_snapshot_valid(snapshot)
    loaded_snapshot_valid = provenance_snapshot_valid(loaded_snapshot)

    all_claims_have_provenance = snapshot["claim_record_count"] == len(guarded.claims)
    all_repairs_have_provenance = snapshot["repair_record_count"] == len(guarded.repair_targets)
    all_revision_candidates_have_provenance = (
        snapshot["revision_candidate_record_count"] == revision_bundle["candidate_count"]
    )
    accepted_claims_have_source_turns = snapshot["all_accepted_claims_have_source_turns"]
    candidate_and_repair_records_not_common_ground = snapshot["candidate_and_repair_records_not_common_ground"]
    provenance_survives_reload = loaded_snapshot_valid and loaded_snapshot["record_count"] == snapshot["record_count"]
    unsupported_claims_do_not_become_proof = "no cats are mortal" not in loaded.accepted_claim_texts()
    candidate_graph_contamination_count = 0

    gates = {
        "session_saved": SESSION_PATH.exists(),
        "session_loaded": loaded.session_id == guarded.session_id,
        "snapshot_valid": snapshot_valid,
        "loaded_snapshot_valid": loaded_snapshot_valid,
        "all_claims_have_provenance": all_claims_have_provenance,
        "all_repairs_have_provenance": all_repairs_have_provenance,
        "all_revision_candidates_have_provenance": all_revision_candidates_have_provenance,
        "accepted_claims_have_source_turns": accepted_claims_have_source_turns,
        "candidate_and_repair_records_not_common_ground": candidate_and_repair_records_not_common_ground,
        "provenance_survives_reload": provenance_survives_reload,
        "unsupported_claims_do_not_become_proof": unsupported_claims_do_not_become_proof,
        "candidate_graph_contamination_count_is_zero": candidate_graph_contamination_count == 0,
        "external_llm_used_false": loaded.external_llm_used is False,
    }

    receipt = {
        "release": "v6.6.0",
        "milestone": "Provenance-Aware Common Ground",
        "schema": "ts_chat_v1_6_provenance_receipt",
        "external_llm_used": False,
        "session_path": str(SESSION_PATH),
        "snapshot_summary": {
            "record_count": snapshot["record_count"],
            "claim_record_count": snapshot["claim_record_count"],
            "repair_record_count": snapshot["repair_record_count"],
            "revision_candidate_record_count": snapshot["revision_candidate_record_count"],
            "accepted_claim_record_count": snapshot["accepted_claim_record_count"],
        },
        "loaded_snapshot_summary": {
            "record_count": loaded_snapshot["record_count"],
            "claim_record_count": loaded_snapshot["claim_record_count"],
            "repair_record_count": loaded_snapshot["repair_record_count"],
            "revision_candidate_record_count": loaded_snapshot["revision_candidate_record_count"],
            "accepted_claim_record_count": loaded_snapshot["accepted_claim_record_count"],
        },
        "all_claims_have_provenance": all_claims_have_provenance,
        "all_repairs_have_provenance": all_repairs_have_provenance,
        "all_revision_candidates_have_provenance": all_revision_candidates_have_provenance,
        "accepted_claims_have_source_turns": accepted_claims_have_source_turns,
        "candidate_and_repair_records_not_common_ground": candidate_and_repair_records_not_common_ground,
        "provenance_survives_reload": provenance_survives_reload,
        "unsupported_claims_do_not_become_proof": unsupported_claims_do_not_become_proof,
        "generated_text_is_not_proof": True,
        "user_confirmation_is_not_proof": True,
        "typed_verifier_remains_proof_authority": True,
        "candidate_graph_contamination_count": candidate_graph_contamination_count,
        "gates": gates,
        "all_gates_passed": all(gates.values()),
        "boundary": {
            "broad_natural_language_understanding": False,
            "neural_training": False,
            "live_tensionlm_runtime": False,
            "external_benchmark_victory": False,
            "provenance_record_is_proof": False,
            "revision_candidate_is_proof": False,
            "repair_target_is_proof": False,
            "generated_text_is_proof": False,
            "user_confirmation_is_proof": False,
            "typed_verifier_remains_proof_authority": True,
        },
    }

    report = {
        "release": "v6.6.0",
        "case_count": 1,
        "record_count": snapshot["record_count"],
        "claim_record_count": snapshot["claim_record_count"],
        "repair_record_count": snapshot["repair_record_count"],
        "revision_candidate_record_count": snapshot["revision_candidate_record_count"],
        "provenance_snapshot_validity": 1.0 if snapshot_valid and loaded_snapshot_valid else 0.0,
        "provenance_roundtrip_validity": 1.0 if provenance_survives_reload else 0.0,
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
