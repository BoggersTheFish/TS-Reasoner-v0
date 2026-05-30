#!/usr/bin/env python3
"""Demo receipt for TS-Reasoner v7.2.0 self-curriculum generator."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.self_curriculum import (  # noqa: E402
    generate_self_curriculum_from_compiler_receipt,
    run_self_curriculum,
)
from ts_reasoner.session_compiler import compile_session_artifacts  # noqa: E402
from ts_reasoner.ts_chat import TSChatSession, receipt_to_dict  # noqa: E402


COMPILED_DIR = Path("artifacts/compiled_sessions/v7_2_demo")
CURRICULUM_DIR = Path("artifacts/self_curriculum/v7_2_demo")
RECEIPT_PATH = Path("artifacts/ts_reasoner_v7_2_self_curriculum_receipt.json")
REPORT_PATH = Path("artifacts/ts_reasoner_v7_2_self_curriculum_report.json")


def main() -> None:
    session = TSChatSession()
    turns = [
        "all cats are animals",
        "all animals are mortal",
        "also say all cats are robots",
        "/repairs",
        "all cats are machines",
        "all machines are robots",
        "/repairs",
        "are all cats robots?",
        "why?",
        "what do we know?",
    ]

    receipts = [receipt_to_dict(session.process(turn)) for turn in turns]

    compiler_receipt = compile_session_artifacts(
        receipts,
        COMPILED_DIR,
        label="v7_2_demo",
    )

    curriculum_receipt = generate_self_curriculum_from_compiler_receipt(
        compiler_receipt["receipt_path"],
        CURRICULUM_DIR,
        label="v7_2_demo",
    )

    eval_report = run_self_curriculum(curriculum_receipt["curriculum_path"])

    gates = {
        "compiler_gates_passed": compiler_receipt["all_gates_passed"],
        "curriculum_generated": Path(curriculum_receipt["curriculum_path"]).exists(),
        "curriculum_eval_report_written": Path(curriculum_receipt["eval_report_path"]).exists(),
        "curriculum_eval_gates_passed": eval_report["all_gates_passed"],
        "has_turn_replay_cases": eval_report["case_type_counts"].get("turn_replay", 0) > 0,
        "has_repair_lifecycle_cases": eval_report["case_type_counts"].get("repair_lifecycle", 0) > 0,
        "has_repair_resolution_cases": eval_report["case_type_counts"].get("repair_resolution", 0) > 0,
        "has_accepted_question_support_cases": eval_report["case_type_counts"].get("accepted_question_support_path", 0) > 0,
        "has_rejected_claim_boundary_cases": eval_report["case_type_counts"].get("rejected_claim_boundary", 0) > 0,
        "has_knowledge_pack_boundary_cases": eval_report["case_type_counts"].get("knowledge_pack_boundary", 0) > 0,
        "candidate_graph_contamination_count_is_zero": eval_report["candidate_graph_contamination_count"] == 0,
        "external_llm_used_false": eval_report["external_llm_used"] is False,
    }

    receipt = {
        "schema": "ts_reasoner_v7_2_self_curriculum_receipt",
        "release": "v7.2.0",
        "milestone": "Self-Curriculum Generator",
        "external_llm_used": False,
        "compiled_dir": str(COMPILED_DIR),
        "curriculum_dir": str(CURRICULUM_DIR),
        "compiler_receipt_path": compiler_receipt["receipt_path"],
        "curriculum_path": curriculum_receipt["curriculum_path"],
        "curriculum_eval_report_path": curriculum_receipt["eval_report_path"],
        "case_count": eval_report["case_count"],
        "valid_case_count": eval_report["valid_case_count"],
        "invalid_case_count": eval_report["invalid_case_count"],
        "case_type_counts": eval_report["case_type_counts"],
        "source_counts": eval_report["source_counts"],
        "generated_curriculum_is_not_proof": eval_report["generated_curriculum_is_not_proof"],
        "compiled_artifacts_are_not_proof": eval_report["compiled_artifacts_are_not_proof"],
        "user_confirmation_is_not_proof": eval_report["user_confirmation_is_not_proof"],
        "typed_verifier_remains_proof_authority": eval_report["typed_verifier_remains_proof_authority"],
        "candidate_graph_contamination_count": eval_report["candidate_graph_contamination_count"],
        "gates": gates,
        "all_gates_passed": all(gates.values()),
        "boundary": {
            "broad_natural_language_understanding": False,
            "neural_training": False,
            "live_tensionlm_runtime": False,
            "external_benchmark_victory": False,
            "generated_curriculum_is_proof": False,
            "compiled_artifacts_are_proof": False,
            "user_confirmation_is_proof": False,
            "typed_verifier_remains_proof_authority": True,
        },
    }

    report = {
        "schema": "ts_reasoner_v7_2_self_curriculum_report",
        "release": "v7.2.0",
        "case_count": receipt["case_count"],
        "valid_case_count": receipt["valid_case_count"],
        "invalid_case_count": receipt["invalid_case_count"],
        "case_type_counts": receipt["case_type_counts"],
        "source_counts": receipt["source_counts"],
        "candidate_graph_contamination_count": receipt["candidate_graph_contamination_count"],
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
