#!/usr/bin/env python3
"""TS-Reasoner v7.0.0 milestone evaluator."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_chat.v7_milestone import evaluate_v7_milestone, v7_milestone_report_valid  # noqa: E402


WORK_DIR = Path("artifacts/ts_reasoner_v7_milestone")
RECEIPT_PATH = Path("artifacts/ts_reasoner_v7_0_self_improving_chat_receipt.json")
REPORT_PATH = Path("artifacts/ts_reasoner_v7_0_self_improving_chat_report.json")


def main() -> None:
    report = evaluate_v7_milestone(WORK_DIR, stress_cycles=40)
    report_valid = v7_milestone_report_valid(report)

    receipt = {
        "release": "v7.0.0",
        "milestone": "Self-Improving Verifier-First Chat System",
        "schema": "ts_reasoner_v7_0_self_improving_chat_receipt",
        "external_llm_used": False,
        "work_dir": str(WORK_DIR),
        "capability_count": report["capability_count"],
        "arena_case_count": report["arena"]["case_count"],
        "arena_pass_rate": report["arena"]["pass_rate"],
        "stress_cycles": report["stress"]["cycles"],
        "stress_cycle_pass_rate": report["stress"]["cycle_pass_rate"],
        "combined_total_checks": report["combined"]["total_checks"],
        "combined_total_passed": report["combined"]["total_passed"],
        "combined_total_failed": report["combined"]["total_failed"],
        "combined_pass_rate": report["combined"]["combined_pass_rate"],
        "wrong_accept_count": report["stress"]["wrong_accept_count"],
        "candidate_graph_contamination_count": (
            report["arena"]["candidate_graph_contamination_count"]
            + report["stress"]["candidate_graph_contamination_count"]
        ),
        "session_reload_failures": report["stress"]["session_reload_failures"],
        "knowledge_pack_roundtrip_failures": report["stress"]["knowledge_pack_roundtrip_failures"],
        "revision_candidate_failures": report["stress"]["revision_candidate_failures"],
        "provenance_failures": report["stress"]["provenance_failures"],
        "zero_wrong_accepts": report["combined"]["zero_wrong_accepts"],
        "zero_candidate_graph_contamination": report["combined"]["zero_candidate_graph_contamination"],
        "proof_boundary_preserved": report["combined"]["proof_boundary_preserved"],
        "persistent_memory_present": report["claim"]["persistent_memory_present"],
        "repair_memory_present": report["claim"]["repair_memory_present"],
        "explanation_traces_present": report["claim"]["explanation_traces_present"],
        "contradiction_handling_present": report["claim"]["contradiction_handling_present"],
        "belief_revision_candidates_present": report["claim"]["belief_revision_candidates_present"],
        "provenance_present": report["claim"]["provenance_present"],
        "knowledge_packs_present": report["claim"]["knowledge_packs_present"],
        "session_arena_present": report["claim"]["session_arena_present"],
        "long_run_stress_present": report["claim"]["long_run_stress_present"],
        "self_improving_loop_present": report["claim"]["self_improving_loop_present"],
        "report_valid": report_valid,
        "all_gates_passed": report_valid and report["all_gates_passed"],
        "boundary": report["boundary"],
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(receipt, indent=2, sort_keys=True))

    if not receipt["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
