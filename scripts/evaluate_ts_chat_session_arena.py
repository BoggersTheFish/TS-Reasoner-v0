#!/usr/bin/env python3
"""Session-level evaluation arena for TS-Reasoner v6.8.0."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_chat.session_arena import arena_report_valid, evaluate_session_arena  # noqa: E402


WORK_DIR = Path("artifacts/ts_chat_session_arena_v68")
RECEIPT_PATH = Path("artifacts/ts_chat_v1_8_session_arena_demo_receipt.json")
REPORT_PATH = Path("artifacts/ts_chat_v1_8_session_arena_eval_report.json")


def main() -> None:
    report = evaluate_session_arena(WORK_DIR)
    report_valid = arena_report_valid(report)

    receipt = {
        "release": "v6.8.0",
        "milestone": "Session Evaluation Arena",
        "schema": "ts_chat_v1_8_session_arena_receipt",
        "external_llm_used": False,
        "arena_work_dir": str(WORK_DIR),
        "case_count": report["case_count"],
        "passed_count": report["passed_count"],
        "failed_count": report["failed_count"],
        "pass_rate": report["pass_rate"],
        "category_pass_rates": report["category_pass_rates"],
        "answer_accuracy": report["answer_accuracy"],
        "status_accuracy": report["status_accuracy"],
        "repair_target_accuracy": report["repair_target_accuracy"],
        "explanation_trace_validity": report["explanation_trace_validity"],
        "contradiction_detection_rate": report["contradiction_detection_rate"],
        "provenance_validity": report["provenance_validity"],
        "knowledge_pack_roundtrip_validity": report["knowledge_pack_roundtrip_validity"],
        "candidate_graph_contamination_count": report["candidate_graph_contamination_count"],
        "unsupported_claims_not_promoted": report["unsupported_claims_not_promoted"],
        "generated_text_is_not_proof": report["generated_text_is_not_proof"],
        "user_confirmation_is_not_proof": report["user_confirmation_is_not_proof"],
        "typed_verifier_remains_proof_authority": report["typed_verifier_remains_proof_authority"],
        "report_valid": report_valid,
        "all_gates_passed": report_valid and report["all_gates_passed"],
        "boundary": {
            "broad_natural_language_understanding": False,
            "neural_training": False,
            "live_tensionlm_runtime": False,
            "external_benchmark_victory": False,
            "arena_report_is_proof": False,
            "knowledge_pack_import_is_proof": False,
            "provenance_record_is_proof": False,
            "revision_candidate_is_proof": False,
            "repair_target_is_proof": False,
            "generated_text_is_proof": False,
            "user_confirmation_is_proof": False,
            "typed_verifier_remains_proof_authority": True,
        },
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(receipt, indent=2, sort_keys=True))

    if not receipt["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
