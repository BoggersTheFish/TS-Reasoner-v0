"""TS-Reasoner v7.0.0 milestone package.

v7.0 packages the v6.x bounded TS-Chat stack into one milestone receipt:

- persistent sessions
- multi-turn repair memory
- explanation traces
- contradiction handling
- belief-revision candidates
- provenance-aware common ground
- knowledge packs
- session evaluation arena
- long-run self-repair stress test

Boundary:
- not broad NLP
- not neural training
- not live TensionLM runtime
- generated text is not proof
- user confirmation is not proof
- revision candidates are not proof
- repair targets are not proof
- typed verifier support remains proof authority
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ts_chat.repair_stress import run_long_run_self_repair_stress, stress_report_valid
from ts_chat.session_arena import arena_report_valid, evaluate_session_arena


SCHEMA = "ts_reasoner_v7_milestone_report_v1"
RELEASE = "v7.0.0"
MILESTONE = "Self-Improving Verifier-First Chat System"


CAPABILITY_LADDER = [
    {
        "release": "v6.1.0",
        "capability": "Persistent Session Memory",
        "claim": "TS-Chat sessions can be saved and reloaded without proof promotion.",
    },
    {
        "release": "v6.2.0",
        "capability": "Multi-Turn Repair Memory",
        "claim": "Open repair targets survive reload and remain queryable.",
    },
    {
        "release": "v6.3.0",
        "capability": "Explanation Traces",
        "claim": "Accepted, unsupported, missing, and repair decisions expose typed traces.",
    },
    {
        "release": "v6.4.0",
        "capability": "Contradiction Handling",
        "claim": "Direct and transitive contradictions are rejected and create repair targets.",
    },
    {
        "release": "v6.5.0",
        "capability": "Belief Revision Candidates",
        "claim": "Contradiction repairs generate bounded candidate actions that are not proof.",
    },
    {
        "release": "v6.6.0",
        "capability": "Provenance-Aware Common Ground",
        "claim": "Claims, repairs, and candidates receive provenance records.",
    },
    {
        "release": "v6.7.0",
        "capability": "Knowledge Packs",
        "claim": "Bounded session state can be exported/imported without proof promotion.",
    },
    {
        "release": "v6.8.0",
        "capability": "Session Evaluation Arena",
        "claim": "The session stack is tested as a reusable arena.",
    },
    {
        "release": "v6.9.0",
        "capability": "Long-Run Self-Repair Stress Test",
        "claim": "Repeated repair cycles preserve zero wrong accepts and zero contamination.",
    },
]


def evaluate_v7_milestone(
    work_dir: str | Path,
    stress_cycles: int = 40,
) -> dict[str, Any]:
    work_dir = Path(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    arena_work_dir = work_dir / "arena"
    stress_work_dir = work_dir / "stress"

    arena_report = evaluate_session_arena(arena_work_dir)
    stress_report = run_long_run_self_repair_stress(
        cycles=stress_cycles,
        work_dir=stress_work_dir,
    )

    arena_valid = arena_report_valid(arena_report)
    stress_valid = stress_report_valid(stress_report)

    zero_wrong_accepts = (
        stress_report["wrong_accept_count"] == 0
        and arena_report["candidate_graph_contamination_count"] == 0
        and stress_report["candidate_graph_contamination_count"] == 0
    )

    zero_candidate_graph_contamination = (
        arena_report["candidate_graph_contamination_count"] == 0
        and stress_report["candidate_graph_contamination_count"] == 0
    )

    proof_boundary_preserved = all(
        [
            arena_report["generated_text_is_not_proof"],
            arena_report["user_confirmation_is_not_proof"],
            arena_report["typed_verifier_remains_proof_authority"],
            stress_report["generated_text_is_not_proof"],
            stress_report["user_confirmation_is_not_proof"],
            stress_report["knowledge_pack_import_is_not_proof"],
            stress_report["revision_candidate_is_not_proof"],
            stress_report["repair_target_is_not_proof"],
            stress_report["typed_verifier_remains_proof_authority"],
        ]
    )

    report = {
        "schema": SCHEMA,
        "release": RELEASE,
        "milestone": MILESTONE,
        "external_llm_used": False,
        "capability_ladder": CAPABILITY_LADDER,
        "capability_count": len(CAPABILITY_LADDER),
        "arena": {
            "case_count": arena_report["case_count"],
            "passed_count": arena_report["passed_count"],
            "failed_count": arena_report["failed_count"],
            "pass_rate": arena_report["pass_rate"],
            "answer_accuracy": arena_report["answer_accuracy"],
            "status_accuracy": arena_report["status_accuracy"],
            "repair_target_accuracy": arena_report["repair_target_accuracy"],
            "explanation_trace_validity": arena_report["explanation_trace_validity"],
            "contradiction_detection_rate": arena_report["contradiction_detection_rate"],
            "provenance_validity": arena_report["provenance_validity"],
            "knowledge_pack_roundtrip_validity": arena_report["knowledge_pack_roundtrip_validity"],
            "candidate_graph_contamination_count": arena_report["candidate_graph_contamination_count"],
            "valid": arena_valid,
        },
        "stress": {
            "cycles": stress_report["cycles"],
            "passed_cycles": stress_report["passed_cycles"],
            "failed_cycles": stress_report["failed_cycles"],
            "cycle_pass_rate": stress_report["cycle_pass_rate"],
            "initial_open_repairs": stress_report["initial_open_repairs"],
            "final_open_repairs": stress_report["final_open_repairs"],
            "repair_targets_created": stress_report["repair_targets_created"],
            "wrong_accept_count": stress_report["wrong_accept_count"],
            "candidate_graph_contamination_count": stress_report["candidate_graph_contamination_count"],
            "session_reload_failures": stress_report["session_reload_failures"],
            "knowledge_pack_roundtrip_failures": stress_report["knowledge_pack_roundtrip_failures"],
            "revision_candidate_failures": stress_report["revision_candidate_failures"],
            "provenance_failures": stress_report["provenance_failures"],
            "valid": stress_valid,
        },
        "combined": {
            "total_arena_cases": arena_report["case_count"],
            "total_stress_cycles": stress_report["cycles"],
            "total_checks": arena_report["case_count"] + stress_report["cycles"],
            "total_passed": arena_report["passed_count"] + stress_report["passed_cycles"],
            "total_failed": arena_report["failed_count"] + stress_report["failed_cycles"],
            "combined_pass_rate": (
                (arena_report["passed_count"] + stress_report["passed_cycles"])
                / (arena_report["case_count"] + stress_report["cycles"])
            ),
            "zero_wrong_accepts": zero_wrong_accepts,
            "zero_candidate_graph_contamination": zero_candidate_graph_contamination,
            "proof_boundary_preserved": proof_boundary_preserved,
        },
        "claim": {
            "self_improving_loop_present": True,
            "persistent_memory_present": True,
            "repair_memory_present": True,
            "explanation_traces_present": True,
            "contradiction_handling_present": True,
            "belief_revision_candidates_present": True,
            "provenance_present": True,
            "knowledge_packs_present": True,
            "session_arena_present": True,
            "long_run_stress_present": True,
        },
        "boundary": {
            "broad_natural_language_understanding": False,
            "neural_training": False,
            "live_tensionlm_runtime": False,
            "external_benchmark_victory": False,
            "v7_report_is_proof": False,
            "arena_report_is_proof": False,
            "stress_report_is_proof": False,
            "knowledge_pack_import_is_proof": False,
            "provenance_record_is_proof": False,
            "revision_candidate_is_proof": False,
            "repair_target_is_proof": False,
            "generated_text_is_proof": False,
            "user_confirmation_is_proof": False,
            "typed_verifier_remains_proof_authority": True,
        },
        "all_gates_passed": all(
            [
                arena_valid,
                stress_valid,
                arena_report["all_gates_passed"],
                stress_report["all_gates_passed"],
                zero_wrong_accepts,
                zero_candidate_graph_contamination,
                proof_boundary_preserved,
            ]
        ),
    }

    return report


def v7_milestone_report_valid(report: dict[str, Any]) -> bool:
    required = {
        "schema",
        "release",
        "milestone",
        "external_llm_used",
        "capability_ladder",
        "capability_count",
        "arena",
        "stress",
        "combined",
        "claim",
        "boundary",
        "all_gates_passed",
    }

    if not required.issubset(report):
        return False

    if report["schema"] != SCHEMA:
        return False

    if report["release"] != RELEASE:
        return False

    if report["milestone"] != MILESTONE:
        return False

    if report["external_llm_used"] is not False:
        return False

    if report["capability_count"] != 9:
        return False

    if len(report["capability_ladder"]) != report["capability_count"]:
        return False

    if report["arena"]["valid"] is not True:
        return False

    if report["stress"]["valid"] is not True:
        return False

    if report["combined"]["zero_wrong_accepts"] is not True:
        return False

    if report["combined"]["zero_candidate_graph_contamination"] is not True:
        return False

    if report["combined"]["proof_boundary_preserved"] is not True:
        return False

    if report["combined"]["total_failed"] != 0:
        return False

    if report["boundary"]["typed_verifier_remains_proof_authority"] is not True:
        return False

    for key, value in report["boundary"].items():
        if key == "typed_verifier_remains_proof_authority":
            continue
        if value is not False:
            return False

    if report["all_gates_passed"] is not True:
        return False

    return True
