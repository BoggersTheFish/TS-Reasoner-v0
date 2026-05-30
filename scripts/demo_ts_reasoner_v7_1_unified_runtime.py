#!/usr/bin/env python3
"""Demo receipt for TS-Reasoner v7.1.0 unified runtime + session compiler."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.session_compiler import compile_session_file  # noqa: E402
from ts_reasoner.ts_chat import TSChatSession, receipt_to_dict  # noqa: E402


SESSION_PATH = Path("artifacts/ts_chat_v7_1_live_surface_demo_session.json")
COMPILED_DIR = Path("artifacts/compiled_sessions/v7_1_demo")
RECEIPT_PATH = Path("artifacts/ts_reasoner_v7_1_unified_runtime_receipt.json")
REPORT_PATH = Path("artifacts/ts_reasoner_v7_1_unified_runtime_report.json")


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
        "/graph",
    ]

    receipts = [session.process(turn) for turn in turns]
    receipt_dicts = [receipt_to_dict(receipt) for receipt in receipts]

    SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    SESSION_PATH.write_text(json.dumps(receipt_dicts, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    compiler_receipt = compile_session_file(
        SESSION_PATH,
        COMPILED_DIR,
        label="v7_1_demo",
    )

    final_ground = receipt_dicts[-1]["common_ground"]
    repair_targets = final_ground.get("repair_targets", [])
    records = final_ground.get("records", [])

    rejected_requested_claims = [
        record for record in records
        if record.get("kind") == "requested_claim" and record.get("status") == "rejected"
    ]
    accepted_robot_question = [
        record for record in records
        if record.get("kind") == "question"
        and record.get("status") == "accepted"
        and record.get("relation", {}).get("subject") == "cats"
        and record.get("relation", {}).get("object") == "robots"
    ]
    resolved_repairs = [repair for repair in repair_targets if repair.get("status") == "resolved"]

    gates = {
        "session_written": SESSION_PATH.exists(),
        "compiler_gates_passed": compiler_receipt["all_gates_passed"],
        "unsupported_claim_rejected": len(rejected_requested_claims) >= 1,
        "repair_target_resolved": len(resolved_repairs) >= 1,
        "accepted_after_typed_repair": len(accepted_robot_question) >= 1,
        "compiled_replay_written": Path(compiler_receipt["replay_path"]).exists(),
        "compiled_curriculum_written": Path(compiler_receipt["repair_curriculum_path"]).exists(),
        "compiled_pack_written": Path(compiler_receipt["knowledge_pack_path"]).exists(),
        "candidate_graph_contamination_count_is_zero": compiler_receipt["candidate_graph_contamination_count"] == 0,
        "external_llm_used_false": compiler_receipt["external_llm_used"] is False,
    }

    receipt = {
        "schema": "ts_reasoner_v7_1_unified_runtime_receipt",
        "release": "v7.1.0",
        "milestone": "Unified Runtime + Session Compiler",
        "external_llm_used": False,
        "session_path": str(SESSION_PATH),
        "compiled_dir": str(COMPILED_DIR),
        "turn_count": len(receipt_dicts),
        "record_count": len(records),
        "repair_target_count": len(repair_targets),
        "resolved_repair_count": len(resolved_repairs),
        "rejected_requested_claim_count": len(rejected_requested_claims),
        "accepted_after_typed_repair_count": len(accepted_robot_question),
        "compiler_receipt": compiler_receipt,
        "candidate_graph_contamination_count": compiler_receipt["candidate_graph_contamination_count"],
        "generated_text_is_not_proof": True,
        "compiled_artifacts_are_not_proof": True,
        "user_confirmation_is_not_proof": True,
        "typed_verifier_remains_proof_authority": True,
        "gates": gates,
        "all_gates_passed": all(gates.values()),
        "boundary": {
            "broad_natural_language_understanding": False,
            "neural_training": False,
            "live_tensionlm_runtime": False,
            "external_benchmark_victory": False,
            "compiled_artifacts_are_proof": False,
            "generated_text_is_proof": False,
            "user_confirmation_is_proof": False,
            "typed_verifier_remains_proof_authority": True,
        },
    }

    report = {
        "schema": "ts_reasoner_v7_1_unified_runtime_report",
        "release": "v7.1.0",
        "turn_count": receipt["turn_count"],
        "record_count": receipt["record_count"],
        "repair_target_count": receipt["repair_target_count"],
        "resolved_repair_count": receipt["resolved_repair_count"],
        "rejected_requested_claim_count": receipt["rejected_requested_claim_count"],
        "accepted_after_typed_repair_count": receipt["accepted_after_typed_repair_count"],
        "compiled_replay_rows": compiler_receipt["replay_row_count"],
        "compiled_repair_curriculum_rows": compiler_receipt["repair_curriculum_row_count"],
        "compiled_provenance_records": compiler_receipt["provenance_record_count"],
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
