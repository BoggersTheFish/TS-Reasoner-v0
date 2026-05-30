#!/usr/bin/env python3
"""Demo receipt for TS-Reasoner v6.5.0 belief revision candidates."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_chat.contradictions import apply_contradiction_guard  # noqa: E402
from ts_chat.explanations import explain_repair_target, explanation_trace_valid  # noqa: E402
from ts_chat.revision_candidates import (  # noqa: E402
    candidate_graph_contamination_count,
    generate_revision_candidates,
    revision_candidate_bundle_valid,
    revision_candidates_do_not_accept_claim,
)
from ts_chat.sessions import build_v61_demo_session, load_session, save_session  # noqa: E402


SESSION_PATH = Path("artifacts/ts_chat_sessions/ts_chat_v1_5_belief_revision_candidates_session.json")
RECEIPT_PATH = Path("artifacts/ts_chat_v1_5_belief_revision_candidates_demo_receipt.json")
REPORT_PATH = Path("artifacts/ts_chat_v1_5_belief_revision_candidates_eval_report.json")


def main() -> None:
    original = build_v61_demo_session()

    guarded, contradiction_trace = apply_contradiction_guard(
        original,
        "no cats are mortal",
        "turn_004",
    )

    # v6.1 demo starts with repair_001 for unsupported cats->robots.
    # The contradiction guard creates repair_002 for no cats->mortal.
    repair_id = "repair_002"

    revision_bundle = generate_revision_candidates(
        guarded,
        repair_id,
        contradiction_trace=contradiction_trace,
    )

    repair_trace = explain_repair_target(guarded, repair_id)

    save_session(guarded, SESSION_PATH)
    loaded = load_session(SESSION_PATH)
    loaded_revision_bundle = generate_revision_candidates(
        loaded,
        repair_id,
        contradiction_trace=contradiction_trace,
    )

    bundle_valid = revision_candidate_bundle_valid(revision_bundle)
    loaded_bundle_valid = revision_candidate_bundle_valid(loaded_revision_bundle)

    candidates_generated = revision_bundle["candidate_count"] >= 5
    support_path_preserved = revision_bundle["support_path"] == [
        "all cats are animals",
        "all animals are mortal",
    ]
    revision_candidates_not_auto_accepted = revision_bundle["all_candidates_not_auto_accepted"]
    revision_candidates_create_no_proof = revision_bundle["all_candidates_create_no_proof"]
    revision_candidates_require_user_confirmation = revision_bundle["all_candidates_require_user_confirmation"]
    revision_candidates_require_typed_verifier = revision_bundle["all_candidates_require_typed_verifier"]
    contradictory_claim_not_accepted = revision_candidates_do_not_accept_claim(guarded, revision_bundle)
    loaded_contradictory_claim_not_accepted = revision_candidates_do_not_accept_claim(loaded, loaded_revision_bundle)
    repair_trace_valid = explanation_trace_valid(repair_trace)
    contamination_count = candidate_graph_contamination_count(guarded, revision_bundle)

    gates = {
        "session_saved": SESSION_PATH.exists(),
        "session_loaded": loaded.session_id == guarded.session_id,
        "candidates_generated": candidates_generated,
        "bundle_valid": bundle_valid,
        "loaded_bundle_valid": loaded_bundle_valid,
        "support_path_preserved": support_path_preserved,
        "revision_candidates_not_auto_accepted": revision_candidates_not_auto_accepted,
        "revision_candidates_create_no_proof": revision_candidates_create_no_proof,
        "revision_candidates_require_user_confirmation": revision_candidates_require_user_confirmation,
        "revision_candidates_require_typed_verifier": revision_candidates_require_typed_verifier,
        "contradictory_claim_not_accepted": contradictory_claim_not_accepted,
        "loaded_contradictory_claim_not_accepted": loaded_contradictory_claim_not_accepted,
        "repair_trace_valid": repair_trace_valid,
        "candidate_graph_contamination_count_is_zero": contamination_count == 0,
        "external_llm_used_false": loaded.external_llm_used is False,
    }

    receipt = {
        "release": "v6.5.0",
        "milestone": "Belief Revision Candidates",
        "schema": "ts_chat_v1_5_belief_revision_candidates_receipt",
        "external_llm_used": False,
        "session_path": str(SESSION_PATH),
        "contradiction_trace": contradiction_trace,
        "repair_trace": repair_trace,
        "revision_bundle": revision_bundle,
        "loaded_revision_bundle": loaded_revision_bundle,
        "candidates_generated": candidates_generated,
        "support_path_preserved": support_path_preserved,
        "revision_candidates_not_auto_accepted": revision_candidates_not_auto_accepted,
        "revision_candidates_create_no_proof": revision_candidates_create_no_proof,
        "revision_candidates_require_user_confirmation": revision_candidates_require_user_confirmation,
        "revision_candidates_require_typed_verifier": revision_candidates_require_typed_verifier,
        "contradictory_claim_not_accepted": contradictory_claim_not_accepted,
        "candidate_graph_contamination_count": contamination_count,
        "gates": gates,
        "all_gates_passed": all(gates.values()),
        "boundary": {
            "broad_natural_language_understanding": False,
            "neural_training": False,
            "live_tensionlm_runtime": False,
            "external_benchmark_victory": False,
            "revision_candidate_is_proof": False,
            "repair_target_is_proof": False,
            "generated_text_is_proof": False,
            "user_confirmation_is_proof": False,
            "typed_verifier_remains_proof_authority": True,
        },
    }

    report = {
        "release": "v6.5.0",
        "case_count": 1,
        "revision_candidate_count": revision_bundle["candidate_count"],
        "candidate_bundle_validity": 1.0 if bundle_valid and loaded_bundle_valid else 0.0,
        "support_path_preservation_rate": 1.0 if support_path_preserved else 0.0,
        "auto_accept_count": 0 if revision_candidates_not_auto_accepted else 1,
        "candidate_graph_contamination_count": contamination_count,
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
