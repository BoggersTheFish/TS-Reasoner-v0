from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Iterable


@dataclass
class WorldState:
    world_id: str
    claims: list[str]
    parent_world_id: str | None = None
    branch_reason: str | None = None
    auto_merge_allowed: bool = False


@dataclass
class BranchingWorldsResult:
    case_id: str
    world_count: int
    base_world_id: str
    branch_world_id: str | None
    base_preserved: bool
    branch_contains_incoming: bool
    auto_merge: bool
    candidate_graph_contamination_count: int
    worlds: list[WorldState] = field(default_factory=list)
    explanation: str = ""

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["worlds"] = [asdict(world) for world in self.worlds]
        return data


def normalize_claim(text: str) -> str:
    return " ".join(text.lower().strip().split())


def make_world(world_id: str, claims: Iterable[str], parent_world_id: str | None = None, branch_reason: str | None = None) -> WorldState:
    return WorldState(
        world_id=world_id,
        claims=[normalize_claim(claim) for claim in claims],
        parent_world_id=parent_world_id,
        branch_reason=branch_reason,
        auto_merge_allowed=False,
    )


def apply_branching_policy(
    case_id: str,
    base_world_id: str,
    base_claims: list[str],
    incoming_claim: str,
    branch_reason: str,
) -> BranchingWorldsResult:
    incoming = normalize_claim(incoming_claim)
    base_world = make_world(base_world_id, base_claims)
    base_claim_set = set(base_world.claims)

    if branch_reason == "identity_violation":
        return BranchingWorldsResult(
            case_id=case_id,
            world_count=1,
            base_world_id=base_world.world_id,
            branch_world_id=None,
            base_preserved=True,
            branch_contains_incoming=False,
            auto_merge=False,
            candidate_graph_contamination_count=0,
            worlds=[base_world],
            explanation="Identity violation is quarantined instead of branched into accepted world state.",
        )

    if incoming in base_claim_set:
        return BranchingWorldsResult(
            case_id=case_id,
            world_count=1,
            base_world_id=base_world.world_id,
            branch_world_id=None,
            base_preserved=True,
            branch_contains_incoming=True,
            auto_merge=False,
            candidate_graph_contamination_count=0,
            worlds=[base_world],
            explanation="Incoming claim already exists in base world, so no branch is created.",
        )

    if branch_reason in {"trusted_revision_contradiction", "missing_support_repair"}:
        branch_world_id = f"{base_world_id}__branch__{case_id}"
        branch_world = make_world(
            world_id=branch_world_id,
            claims=[*base_world.claims, incoming],
            parent_world_id=base_world.world_id,
            branch_reason=branch_reason,
        )

        return BranchingWorldsResult(
            case_id=case_id,
            world_count=2,
            base_world_id=base_world.world_id,
            branch_world_id=branch_world.world_id,
            base_preserved=True,
            branch_contains_incoming=incoming in branch_world.claims,
            auto_merge=False,
            candidate_graph_contamination_count=0,
            worlds=[base_world, branch_world],
            explanation="Incoming claim is isolated into a branch world. Base common ground remains preserved and no automatic merge occurs.",
        )

    return BranchingWorldsResult(
        case_id=case_id,
        world_count=1,
        base_world_id=base_world.world_id,
        branch_world_id=None,
        base_preserved=True,
        branch_contains_incoming=False,
        auto_merge=False,
        candidate_graph_contamination_count=0,
        worlds=[base_world],
        explanation="No safe branch rule matched, so incoming claim is not inserted into world state.",
    )


def evaluate_branching_world_cases(cases: Iterable[dict[str, object]]) -> dict[str, object]:
    results = []
    passed = 0
    total = 0
    contamination = 0

    for raw in cases:
        total += 1

        result = apply_branching_policy(
            case_id=str(raw["case_id"]),
            base_world_id=str(raw["base_world_id"]),
            base_claims=[str(claim) for claim in raw["base_claims"]],
            incoming_claim=str(raw["incoming_claim"]),
            branch_reason=str(raw["branch_reason"]),
        )

        expected_world_count = int(raw["expected_world_count"])
        expected_base_preserved = bool(raw["expected_base_preserved"])
        expected_branch_contains_incoming = bool(raw["expected_branch_contains_incoming"])
        expected_auto_merge = bool(raw["expected_auto_merge"])

        case_passed = (
            result.world_count == expected_world_count
            and result.base_preserved == expected_base_preserved
            and result.branch_contains_incoming == expected_branch_contains_incoming
            and result.auto_merge == expected_auto_merge
            and result.candidate_graph_contamination_count == 0
        )

        if case_passed:
            passed += 1

        contamination += result.candidate_graph_contamination_count

        row = result.to_dict()
        row["expected_world_count"] = expected_world_count
        row["expected_base_preserved"] = expected_base_preserved
        row["expected_branch_contains_incoming"] = expected_branch_contains_incoming
        row["expected_auto_merge"] = expected_auto_merge
        row["passed"] = case_passed
        results.append(row)

    return {
        "release": "v8.4.0",
        "case_count": total,
        "passed_cases": passed,
        "failed_cases": total - passed,
        "branching_world_accuracy": passed / total if total else 0.0,
        "candidate_graph_contamination_count": contamination,
        "base_worlds_preserved": all(row["base_preserved"] for row in results),
        "auto_merge_count": sum(1 for row in results if row["auto_merge"]),
        "all_gates_passed": total > 0 and passed == total and contamination == 0,
        "results": results,
    }
