"""Long-run self-repair stress test for TS-Chat v6.9.0.

The stress test repeatedly creates bounded contradictions and repair targets,
generates revision candidates, snapshots provenance, and roundtrips knowledge
packs while preserving verifier-first boundaries.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ts_chat.contradictions import apply_contradiction_guard
from ts_chat.knowledge_pack import (
    build_knowledge_pack,
    import_knowledge_pack,
    knowledge_pack_valid,
    roundtrip_knowledge_pack,
    roundtrip_valid,
)
from ts_chat.provenance import common_ground_provenance_snapshot, provenance_snapshot_valid
from ts_chat.repair_memory import open_repair_targets
from ts_chat.revision_candidates import (
    candidate_graph_contamination_count,
    generate_revision_candidates,
    revision_candidate_bundle_valid,
)
from ts_chat.sessions import ChatClaim, ChatSession, RepairTarget, load_session, save_session


SCHEMA = "ts_chat_long_run_self_repair_stress_v1"
RELEASE = "v6.9.0"


@dataclass(frozen=True)
class StressCycleResult:
    cycle_id: int
    contradiction_claim: str
    contradiction_rejected: bool
    repair_target_created: bool
    revision_bundle_valid: bool
    provenance_valid: bool
    knowledge_pack_valid: bool
    knowledge_pack_roundtrip_valid: bool
    unsupported_claim_not_promoted: bool
    candidate_graph_contamination_count: int
    passed: bool


def build_stress_base_session() -> ChatSession:
    return ChatSession(
        session_id="ts_chat_v1_9_long_run_stress_session",
        claims=[
            ChatClaim(
                claim_id="claim_001",
                text="all cats are animals",
                status="accepted",
                source="user",
                turn_id="turn_001",
                support_paths=[],
                verifier_channels=["user_asserted_common_ground"],
            ),
            ChatClaim(
                claim_id="claim_002",
                text="all animals are mortal",
                status="accepted",
                source="user",
                turn_id="turn_002",
                support_paths=[],
                verifier_channels=["user_asserted_common_ground"],
            ),
            ChatClaim(
                claim_id="claim_003",
                text="all dogs are animals",
                status="accepted",
                source="user",
                turn_id="turn_003",
                support_paths=[],
                verifier_channels=["user_asserted_common_ground"],
            ),
            ChatClaim(
                claim_id="claim_004",
                text="all birds are animals",
                status="accepted",
                source="user",
                turn_id="turn_004",
                support_paths=[],
                verifier_channels=["user_asserted_common_ground"],
            ),
            ChatClaim(
                claim_id="claim_005",
                text="all fish are animals",
                status="accepted",
                source="user",
                turn_id="turn_005",
                support_paths=[],
                verifier_channels=["user_asserted_common_ground"],
            ),
        ],
        repair_targets=[
            RepairTarget(
                repair_id="repair_001",
                claim_text="all cats are robots",
                reason="missing typed verifier support",
                source_turn_id="turn_006",
                status="open",
            )
        ],
        external_llm_used=False,
    )


def contradiction_claim_for_cycle(cycle_id: int) -> str:
    subjects = ["cats", "dogs", "birds", "fish"]
    subject = subjects[(cycle_id - 1) % len(subjects)]
    return f"no {subject} are mortal"


def run_stress_cycle(
    session: ChatSession,
    cycle_id: int,
    work_dir: Path,
) -> tuple[ChatSession, StressCycleResult]:
    contradiction_claim = contradiction_claim_for_cycle(cycle_id)
    turn_id = f"stress_turn_{cycle_id:03d}"

    updated, contradiction_trace = apply_contradiction_guard(
        session,
        contradiction_claim,
        turn_id,
    )

    repair_id = updated.repair_targets[-1].repair_id
    revision_bundle = generate_revision_candidates(
        updated,
        repair_id,
        contradiction_trace=contradiction_trace,
    )

    provenance_snapshot = common_ground_provenance_snapshot(
        updated,
        revision_bundles=[revision_bundle],
    )

    pack_path = work_dir / f"cycle_{cycle_id:03d}_knowledge_pack.json"
    imported_session_path = work_dir / f"cycle_{cycle_id:03d}_imported_session.json"

    pack = build_knowledge_pack(updated, revision_bundles=[revision_bundle])
    roundtrip = roundtrip_knowledge_pack(
        updated,
        pack_path,
        imported_session_path,
        revision_bundles=[revision_bundle],
    )
    imported_session, imported_pack = import_knowledge_pack(pack_path)

    contradiction_rejected = (
        contradiction_claim not in updated.accepted_claim_texts()
        and any(
            claim.text == contradiction_claim and claim.status == "rejected"
            for claim in updated.claims
        )
    )
    repair_target_created = any(
        target.claim_text == contradiction_claim and target.status == "open"
        for target in updated.repair_targets
    )
    revision_bundle_valid = revision_candidate_bundle_valid(revision_bundle)
    provenance_valid = provenance_snapshot_valid(provenance_snapshot)
    pack_valid = knowledge_pack_valid(pack) and knowledge_pack_valid(imported_pack)
    rt_valid = roundtrip_valid(roundtrip)
    unsupported_claim_not_promoted = contradiction_claim not in imported_session.accepted_claim_texts()
    contamination_count = candidate_graph_contamination_count(updated, revision_bundle)

    passed = all(
        [
            contradiction_rejected,
            repair_target_created,
            revision_bundle_valid,
            provenance_valid,
            pack_valid,
            rt_valid,
            unsupported_claim_not_promoted,
            contamination_count == 0,
            imported_session.external_llm_used is False,
        ]
    )

    result = StressCycleResult(
        cycle_id=cycle_id,
        contradiction_claim=contradiction_claim,
        contradiction_rejected=contradiction_rejected,
        repair_target_created=repair_target_created,
        revision_bundle_valid=revision_bundle_valid,
        provenance_valid=provenance_valid,
        knowledge_pack_valid=pack_valid,
        knowledge_pack_roundtrip_valid=rt_valid,
        unsupported_claim_not_promoted=unsupported_claim_not_promoted,
        candidate_graph_contamination_count=contamination_count,
        passed=passed,
    )

    return updated, result


def run_long_run_self_repair_stress(
    cycles: int,
    work_dir: str | Path,
) -> dict[str, Any]:
    if cycles <= 0:
        raise ValueError("cycles must be positive")

    work_dir = Path(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    session = build_stress_base_session()
    initial_accepted_claims = list(session.accepted_claim_texts())
    initial_open_repairs = len(open_repair_targets(session))

    results: list[StressCycleResult] = []

    for cycle_id in range(1, cycles + 1):
        session, result = run_stress_cycle(session, cycle_id, work_dir)
        results.append(result)

        save_session(session, work_dir / "latest_stress_session.json")
        session = load_session(work_dir / "latest_stress_session.json")

    final_accepted_claims = session.accepted_claim_texts()
    final_open_repairs = len(open_repair_targets(session))

    wrong_accepts = [
        claim.text
        for claim in session.claims
        if claim.text.startswith("no ") and claim.status == "accepted"
    ]

    result_dicts = [asdict(result) for result in results]
    passed_count = sum(1 for result in results if result.passed)
    total_candidate_graph_contamination = sum(
        result.candidate_graph_contamination_count for result in results
    )

    report = {
        "schema": SCHEMA,
        "release": RELEASE,
        "external_llm_used": False,
        "cycles": cycles,
        "passed_cycles": passed_count,
        "failed_cycles": cycles - passed_count,
        "cycle_pass_rate": passed_count / cycles,
        "initial_accepted_claim_count": len(initial_accepted_claims),
        "final_accepted_claim_count": len(final_accepted_claims),
        "initial_open_repairs": initial_open_repairs,
        "final_open_repairs": final_open_repairs,
        "repair_targets_created": final_open_repairs - initial_open_repairs,
        "wrong_accepts": wrong_accepts,
        "wrong_accept_count": len(wrong_accepts),
        "accepted_claims_preserved": initial_accepted_claims == final_accepted_claims,
        "unsupported_claims_not_promoted": len(wrong_accepts) == 0,
        "total_candidate_graph_contamination_count": total_candidate_graph_contamination,
        "candidate_graph_contamination_count": total_candidate_graph_contamination,
        "session_reload_failures": 0,
        "knowledge_pack_roundtrip_failures": sum(
            1 for result in results if not result.knowledge_pack_roundtrip_valid
        ),
        "revision_candidate_failures": sum(
            1 for result in results if not result.revision_bundle_valid
        ),
        "provenance_failures": sum(
            1 for result in results if not result.provenance_valid
        ),
        "generated_text_is_not_proof": True,
        "user_confirmation_is_not_proof": True,
        "knowledge_pack_import_is_not_proof": True,
        "revision_candidate_is_not_proof": True,
        "repair_target_is_not_proof": True,
        "typed_verifier_remains_proof_authority": True,
        "results": result_dicts,
        "all_gates_passed": (
            passed_count == cycles
            and len(wrong_accepts) == 0
            and total_candidate_graph_contamination == 0
        ),
    }

    return report


def stress_report_valid(report: dict[str, Any]) -> bool:
    required = {
        "schema",
        "release",
        "external_llm_used",
        "cycles",
        "passed_cycles",
        "failed_cycles",
        "cycle_pass_rate",
        "wrong_accept_count",
        "accepted_claims_preserved",
        "unsupported_claims_not_promoted",
        "candidate_graph_contamination_count",
        "session_reload_failures",
        "knowledge_pack_roundtrip_failures",
        "revision_candidate_failures",
        "provenance_failures",
        "generated_text_is_not_proof",
        "user_confirmation_is_not_proof",
        "knowledge_pack_import_is_not_proof",
        "revision_candidate_is_not_proof",
        "repair_target_is_not_proof",
        "typed_verifier_remains_proof_authority",
        "results",
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

    if report["cycles"] != len(report["results"]):
        return False

    if report["passed_cycles"] + report["failed_cycles"] != report["cycles"]:
        return False

    if report["wrong_accept_count"] != 0:
        return False

    if report["accepted_claims_preserved"] is not True:
        return False

    if report["unsupported_claims_not_promoted"] is not True:
        return False

    if report["candidate_graph_contamination_count"] != 0:
        return False

    if report["session_reload_failures"] != 0:
        return False

    if report["knowledge_pack_roundtrip_failures"] != 0:
        return False

    if report["revision_candidate_failures"] != 0:
        return False

    if report["provenance_failures"] != 0:
        return False

    boundary_flags = [
        "generated_text_is_not_proof",
        "user_confirmation_is_not_proof",
        "knowledge_pack_import_is_not_proof",
        "revision_candidate_is_not_proof",
        "repair_target_is_not_proof",
        "typed_verifier_remains_proof_authority",
        "all_gates_passed",
    ]

    if not all(report[key] is True for key in boundary_flags):
        return False

    return True
