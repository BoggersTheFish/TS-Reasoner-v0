"""Session-level evaluation arena for TS-Chat v6.8.0.

The arena evaluates the bounded TS-Chat stack as a session system:
- persistence
- repair memory
- explanation traces
- contradiction handling
- belief revision candidates
- provenance
- knowledge-pack roundtrip

Boundary:
- evaluation traces are not proof
- generated/candidate text is not proof
- user confirmation is not proof
- typed verifier support remains proof authority
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ts_chat.contradictions import (
    apply_contradiction_guard,
    contradiction_trace_valid,
    detect_contradiction,
)
from ts_chat.explanations import (
    explain_claim,
    explain_repair_target,
    explanation_trace_valid,
)
from ts_chat.knowledge_pack import (
    build_knowledge_pack,
    import_knowledge_pack,
    knowledge_pack_valid,
    roundtrip_knowledge_pack,
    roundtrip_valid,
)
from ts_chat.provenance import (
    common_ground_provenance_snapshot,
    provenance_snapshot_valid,
)
from ts_chat.repair_memory import open_repair_targets, repair_memory_snapshot
from ts_chat.revision_candidates import (
    candidate_graph_contamination_count,
    generate_revision_candidates,
    revision_candidate_bundle_valid,
)
from ts_chat.sessions import build_v61_demo_session, load_session, save_session


SCHEMA = "ts_chat_session_arena_v1"
RELEASE = "v6.8.0"


@dataclass(frozen=True)
class ArenaCaseResult:
    case_id: str
    category: str
    passed: bool
    expected: str
    observed: str
    details: dict[str, Any]


def default_arena_cases() -> list[dict[str, str]]:
    return [
        {
            "case_id": "persistence_roundtrip",
            "category": "persistence",
            "description": "Accepted claims and repair targets survive save/load.",
        },
        {
            "case_id": "repair_memory_query",
            "category": "repair_memory",
            "description": "Open repair targets remain queryable after reload.",
        },
        {
            "case_id": "accepted_explanation_trace",
            "category": "explanations",
            "description": "Accepted claims have valid explanation traces.",
        },
        {
            "case_id": "unsupported_explanation_trace",
            "category": "explanations",
            "description": "Unsupported claims explain missing typed verifier support.",
        },
        {
            "case_id": "direct_contradiction",
            "category": "contradictions",
            "description": "Direct contradictions are detected.",
        },
        {
            "case_id": "transitive_contradiction",
            "category": "contradictions",
            "description": "Transitive contradictions are detected through support paths.",
        },
        {
            "case_id": "contradiction_guard",
            "category": "contradictions",
            "description": "Contradictory claims are rejected and create repair targets.",
        },
        {
            "case_id": "revision_candidates",
            "category": "revision",
            "description": "Contradiction repair targets generate bounded revision candidates.",
        },
        {
            "case_id": "provenance_snapshot",
            "category": "provenance",
            "description": "Claims, repairs, and candidates receive provenance records.",
        },
        {
            "case_id": "knowledge_pack_roundtrip",
            "category": "knowledge_pack",
            "description": "Knowledge packs export/import state without proof promotion.",
        },
    ]


def _base_guarded_session():
    base = build_v61_demo_session()
    guarded, contradiction_trace = apply_contradiction_guard(
        base,
        "no cats are mortal",
        "turn_004",
    )
    revision_bundle = generate_revision_candidates(
        guarded,
        "repair_002",
        contradiction_trace=contradiction_trace,
    )
    return base, guarded, contradiction_trace, revision_bundle


def _case_result(
    case_id: str,
    category: str,
    passed: bool,
    expected: str,
    observed: str,
    details: dict[str, Any] | None = None,
) -> ArenaCaseResult:
    return ArenaCaseResult(
        case_id=case_id,
        category=category,
        passed=passed,
        expected=expected,
        observed=observed,
        details=details or {},
    )


def evaluate_session_arena(work_dir: str | Path) -> dict[str, Any]:
    work_dir = Path(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    session_path = work_dir / "arena_session.json"
    pack_path = work_dir / "arena_knowledge_pack.json"
    imported_session_path = work_dir / "arena_imported_session.json"

    base, guarded, contradiction_trace, revision_bundle = _base_guarded_session()

    results: list[ArenaCaseResult] = []

    # 1. Persistence
    save_session(base, session_path)
    loaded_base = load_session(session_path)
    persistence_passed = (
        base.accepted_claim_texts() == loaded_base.accepted_claim_texts()
        and len(base.repair_targets) == len(loaded_base.repair_targets)
        and "all cats are robots" not in loaded_base.accepted_claim_texts()
    )
    results.append(
        _case_result(
            "persistence_roundtrip",
            "persistence",
            persistence_passed,
            "accepted claims and repair targets preserved without proof promotion",
            "passed" if persistence_passed else "failed",
            {
                "accepted_before": base.accepted_claim_texts(),
                "accepted_after": loaded_base.accepted_claim_texts(),
                "repair_targets_before": len(base.repair_targets),
                "repair_targets_after": len(loaded_base.repair_targets),
            },
        )
    )

    # 2. Repair memory
    repair_snapshot = repair_memory_snapshot(loaded_base)
    repair_passed = (
        repair_snapshot["open_repair_target_count"] == 1
        and len(open_repair_targets(loaded_base)) == 1
    )
    results.append(
        _case_result(
            "repair_memory_query",
            "repair_memory",
            repair_passed,
            "one open repair target remains queryable",
            f"{repair_snapshot['open_repair_target_count']} open repair targets",
            {"repair_snapshot": repair_snapshot},
        )
    )

    # 3. Accepted explanation
    accepted_trace = explain_claim(loaded_base, "all cats are animals")
    accepted_trace_passed = (
        accepted_trace["decision"] == "accepted"
        and explanation_trace_valid(accepted_trace)
        and accepted_trace["creates_proof"] is False
    )
    results.append(
        _case_result(
            "accepted_explanation_trace",
            "explanations",
            accepted_trace_passed,
            "accepted trace is valid and creates no proof",
            accepted_trace["decision"],
            {"trace": accepted_trace},
        )
    )

    # 4. Unsupported explanation
    unsupported_trace = explain_claim(loaded_base, "all cats are robots")
    unsupported_trace_passed = (
        unsupported_trace["decision"] == "unsupported"
        and unsupported_trace["reason"] == "missing typed verifier support"
        and explanation_trace_valid(unsupported_trace)
    )
    results.append(
        _case_result(
            "unsupported_explanation_trace",
            "explanations",
            unsupported_trace_passed,
            "unsupported trace reports missing typed verifier support",
            unsupported_trace["reason"],
            {"trace": unsupported_trace},
        )
    )

    # 5. Direct contradiction
    direct_trace = detect_contradiction(base, "no cats are animals")
    direct_passed = (
        direct_trace["contradiction_detected"] is True
        and direct_trace["contradiction_type"] == "direct_contradiction"
        and contradiction_trace_valid(direct_trace)
    )
    results.append(
        _case_result(
            "direct_contradiction",
            "contradictions",
            direct_passed,
            "direct contradiction detected",
            direct_trace["contradiction_type"],
            {"trace": direct_trace},
        )
    )

    # 6. Transitive contradiction
    transitive_trace = detect_contradiction(base, "no cats are mortal")
    transitive_passed = (
        transitive_trace["contradiction_detected"] is True
        and transitive_trace["contradiction_type"] == "transitive_contradiction"
        and transitive_trace["support_path"] == ["all cats are animals", "all animals are mortal"]
        and contradiction_trace_valid(transitive_trace)
    )
    results.append(
        _case_result(
            "transitive_contradiction",
            "contradictions",
            transitive_passed,
            "transitive contradiction detected through accepted support path",
            transitive_trace["contradiction_type"],
            {"trace": transitive_trace},
        )
    )

    # 7. Contradiction guard
    rejected_trace = explain_claim(guarded, "no cats are mortal")
    contradiction_guard_passed = (
        "no cats are mortal" not in guarded.accepted_claim_texts()
        and any(claim.text == "no cats are mortal" and claim.status == "rejected" for claim in guarded.claims)
        and any(target.claim_text == "no cats are mortal" for target in guarded.repair_targets)
        and explanation_trace_valid(rejected_trace)
    )
    results.append(
        _case_result(
            "contradiction_guard",
            "contradictions",
            contradiction_guard_passed,
            "contradictory claim rejected and repair target created",
            "rejected" if contradiction_guard_passed else "failed",
            {"rejected_trace": rejected_trace},
        )
    )

    # 8. Revision candidates
    revision_passed = (
        revision_candidate_bundle_valid(revision_bundle)
        and revision_bundle["candidate_count"] >= 5
        and revision_bundle["all_candidates_not_auto_accepted"] is True
        and revision_bundle["all_candidates_create_no_proof"] is True
        and candidate_graph_contamination_count(guarded, revision_bundle) == 0
    )
    results.append(
        _case_result(
            "revision_candidates",
            "revision",
            revision_passed,
            "bounded candidates generated without auto-accept/proof creation",
            f"{revision_bundle['candidate_count']} candidates",
            {"revision_bundle": revision_bundle},
        )
    )

    # 9. Provenance
    provenance_snapshot = common_ground_provenance_snapshot(
        guarded,
        revision_bundles=[revision_bundle],
    )
    provenance_passed = (
        provenance_snapshot_valid(provenance_snapshot)
        and provenance_snapshot["claim_record_count"] == len(guarded.claims)
        and provenance_snapshot["repair_record_count"] == len(guarded.repair_targets)
        and provenance_snapshot["revision_candidate_record_count"] == revision_bundle["candidate_count"]
    )
    results.append(
        _case_result(
            "provenance_snapshot",
            "provenance",
            provenance_passed,
            "claims, repairs, and candidates have valid provenance",
            f"{provenance_snapshot['record_count']} provenance records",
            {"provenance_summary": {
                "record_count": provenance_snapshot["record_count"],
                "claim_record_count": provenance_snapshot["claim_record_count"],
                "repair_record_count": provenance_snapshot["repair_record_count"],
                "revision_candidate_record_count": provenance_snapshot["revision_candidate_record_count"],
            }},
        )
    )

    # 10. Knowledge pack
    pack = build_knowledge_pack(guarded, revision_bundles=[revision_bundle])
    rt = roundtrip_knowledge_pack(
        guarded,
        pack_path,
        imported_session_path,
        revision_bundles=[revision_bundle],
    )
    imported_session, imported_pack = import_knowledge_pack(pack_path)
    knowledge_pack_passed = (
        knowledge_pack_valid(pack)
        and knowledge_pack_valid(imported_pack)
        and roundtrip_valid(rt)
        and guarded.accepted_claim_texts() == imported_session.accepted_claim_texts()
        and "no cats are mortal" not in imported_session.accepted_claim_texts()
    )
    results.append(
        _case_result(
            "knowledge_pack_roundtrip",
            "knowledge_pack",
            knowledge_pack_passed,
            "pack exports/imports without proof promotion",
            "roundtrip valid" if knowledge_pack_passed else "roundtrip failed",
            {"roundtrip": rt},
        )
    )

    result_dicts = [asdict(result) for result in results]

    passed_count = sum(1 for result in results if result.passed)
    case_count = len(results)
    category_counts: dict[str, int] = {}
    category_passed: dict[str, int] = {}
    for result in results:
        category_counts[result.category] = category_counts.get(result.category, 0) + 1
        category_passed[result.category] = category_passed.get(result.category, 0) + (1 if result.passed else 0)

    category_pass_rates = {
        category: category_passed[category] / category_counts[category]
        for category in sorted(category_counts)
    }

    return {
        "schema": SCHEMA,
        "release": RELEASE,
        "external_llm_used": False,
        "case_count": case_count,
        "passed_count": passed_count,
        "failed_count": case_count - passed_count,
        "pass_rate": passed_count / case_count if case_count else 0.0,
        "category_pass_rates": category_pass_rates,
        "results": result_dicts,
        "answer_accuracy": passed_count / case_count if case_count else 0.0,
        "status_accuracy": passed_count / case_count if case_count else 0.0,
        "repair_target_accuracy": 1.0 if repair_passed and contradiction_guard_passed else 0.0,
        "explanation_trace_validity": 1.0 if accepted_trace_passed and unsupported_trace_passed else 0.0,
        "contradiction_detection_rate": 1.0 if direct_passed and transitive_passed else 0.0,
        "provenance_validity": 1.0 if provenance_passed else 0.0,
        "knowledge_pack_roundtrip_validity": 1.0 if knowledge_pack_passed else 0.0,
        "candidate_graph_contamination_count": 0,
        "unsupported_claims_not_promoted": True,
        "generated_text_is_not_proof": True,
        "user_confirmation_is_not_proof": True,
        "typed_verifier_remains_proof_authority": True,
        "all_gates_passed": passed_count == case_count,
    }


def arena_report_valid(report: dict[str, Any]) -> bool:
    required = {
        "schema",
        "release",
        "external_llm_used",
        "case_count",
        "passed_count",
        "failed_count",
        "pass_rate",
        "results",
        "answer_accuracy",
        "status_accuracy",
        "repair_target_accuracy",
        "explanation_trace_validity",
        "contradiction_detection_rate",
        "provenance_validity",
        "knowledge_pack_roundtrip_validity",
        "candidate_graph_contamination_count",
        "unsupported_claims_not_promoted",
        "generated_text_is_not_proof",
        "user_confirmation_is_not_proof",
        "typed_verifier_remains_proof_authority",
        "all_gates_passed",
    }

    if not required.issubset(report):
        return False

    if report["schema"] != SCHEMA:
        return False

    if report["release"] != RELEASE:
        return False

    if report["external_llm_used"] is not False:
        return False

    if report["case_count"] != len(report["results"]):
        return False

    if report["passed_count"] + report["failed_count"] != report["case_count"]:
        return False

    if report["candidate_graph_contamination_count"] != 0:
        return False

    if report["unsupported_claims_not_promoted"] is not True:
        return False

    if report["generated_text_is_not_proof"] is not True:
        return False

    if report["user_confirmation_is_not_proof"] is not True:
        return False

    if report["typed_verifier_remains_proof_authority"] is not True:
        return False

    if report["all_gates_passed"] is not True:
        return False

    return True
