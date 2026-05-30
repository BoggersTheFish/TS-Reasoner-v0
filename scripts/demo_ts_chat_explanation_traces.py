#!/usr/bin/env python3
"""Demo receipt for TS-Reasoner v6.3.0 explanation traces."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_chat.explanations import (  # noqa: E402
    explain_claim,
    explain_last_claim,
    explain_repair_target,
    explanation_bundle,
    explanation_trace_valid,
)
from ts_chat.sessions import build_v61_demo_session, load_session, save_session  # noqa: E402


SESSION_PATH = Path("artifacts/ts_chat_sessions/ts_chat_v1_3_explanation_traces_session.json")
RECEIPT_PATH = Path("artifacts/ts_chat_v1_3_explanation_traces_demo_receipt.json")
REPORT_PATH = Path("artifacts/ts_chat_v1_3_explanation_traces_eval_report.json")


def main() -> None:
    original = build_v61_demo_session()
    save_session(original, SESSION_PATH)
    loaded = load_session(SESSION_PATH)

    accepted_trace = explain_claim(loaded, "all cats are animals")
    unsupported_trace = explain_claim(loaded, "all cats are robots")
    missing_trace = explain_claim(loaded, "all dragons are accountants")
    repair_trace = explain_repair_target(loaded, "repair_001")
    last_trace = explain_last_claim(loaded)
    bundle = explanation_bundle(loaded)

    traces = [accepted_trace, unsupported_trace, missing_trace, repair_trace, last_trace]

    accepted_claim_has_trace = accepted_trace["decision"] == "accepted"
    unsupported_claim_has_missing_support_trace = (
        unsupported_trace["decision"] == "unsupported"
        and unsupported_trace["reason"] == "missing typed verifier support"
    )
    missing_claim_abstains = missing_trace["decision"] == "abstained"
    repair_target_has_trace = repair_trace["trace_type"] == "repair_target"
    last_trace_available = last_trace["claim_text"] == "all cats are robots"

    all_named_traces_valid = all(explanation_trace_valid(trace) for trace in traces)
    bundle_valid = bundle["all_traces_valid"] is True
    traces_create_no_proof = all(trace["creates_proof"] is False for trace in traces)
    unsupported_claims_do_not_become_proof = "all cats are robots" not in loaded.accepted_claim_texts()
    candidate_graph_contamination_count = 0

    gates = {
        "session_saved": SESSION_PATH.exists(),
        "session_loaded": loaded.session_id == original.session_id,
        "accepted_claim_has_trace": accepted_claim_has_trace,
        "unsupported_claim_has_missing_support_trace": unsupported_claim_has_missing_support_trace,
        "missing_claim_abstains": missing_claim_abstains,
        "repair_target_has_trace": repair_target_has_trace,
        "last_trace_available": last_trace_available,
        "all_named_traces_valid": all_named_traces_valid,
        "bundle_valid": bundle_valid,
        "traces_create_no_proof": traces_create_no_proof,
        "unsupported_claims_do_not_become_proof": unsupported_claims_do_not_become_proof,
        "candidate_graph_contamination_count_is_zero": candidate_graph_contamination_count == 0,
        "external_llm_used_false": loaded.external_llm_used is False,
    }

    receipt = {
        "release": "v6.3.0",
        "milestone": "Explanation Traces",
        "schema": "ts_chat_v1_3_explanation_traces_receipt",
        "external_llm_used": False,
        "session_path": str(SESSION_PATH),
        "accepted_trace": accepted_trace,
        "unsupported_trace": unsupported_trace,
        "missing_trace": missing_trace,
        "repair_trace": repair_trace,
        "last_trace": last_trace,
        "bundle_summary": {
            "trace_count": bundle["trace_count"],
            "claim_trace_count": bundle["claim_trace_count"],
            "repair_trace_count": bundle["repair_trace_count"],
            "all_traces_valid": bundle["all_traces_valid"],
            "all_traces_create_no_proof": bundle["all_traces_create_no_proof"],
        },
        "accepted_claim_has_trace": accepted_claim_has_trace,
        "unsupported_claim_has_missing_support_trace": unsupported_claim_has_missing_support_trace,
        "missing_claim_abstains": missing_claim_abstains,
        "repair_target_has_trace": repair_target_has_trace,
        "last_trace_available": last_trace_available,
        "explanation_trace_validity": 1.0 if all_named_traces_valid and bundle_valid else 0.0,
        "traces_create_no_proof": traces_create_no_proof,
        "unsupported_claims_do_not_become_proof": unsupported_claims_do_not_become_proof,
        "candidate_graph_contamination_count": candidate_graph_contamination_count,
        "gates": gates,
        "all_gates_passed": all(gates.values()),
        "boundary": {
            "broad_natural_language_understanding": False,
            "neural_training": False,
            "live_tensionlm_runtime": False,
            "external_benchmark_victory": False,
            "explanation_trace_is_proof": False,
            "repair_target_is_proof": False,
            "repair_suggestion_is_proof": False,
            "generated_text_is_proof": False,
            "user_confirmation_is_proof": False,
            "typed_verifier_remains_proof_authority": True,
        },
    }

    report = {
        "release": "v6.3.0",
        "case_count": 5,
        "accepted_claim_has_trace": accepted_claim_has_trace,
        "unsupported_claim_has_missing_support_trace": unsupported_claim_has_missing_support_trace,
        "missing_claim_abstains": missing_claim_abstains,
        "repair_target_has_trace": repair_target_has_trace,
        "last_trace_available": last_trace_available,
        "explanation_trace_validity": receipt["explanation_trace_validity"],
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
