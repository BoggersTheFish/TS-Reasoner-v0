"""Verifier-gated goals and deterministic tension control for Habitat v3."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from enum import Enum
from typing import Any, Iterable, Mapping

from .habitat import CONFLICTED, SUPPORTED_FALSE, SUPPORTED_TRUE, UNKNOWN, SignedProposition, proposition_key
from .typed_support import canonical_hash


class GoalStatus(str, Enum):
    PROPOSED = "PROPOSED"
    ACTIVE = "ACTIVE"
    SATISFIED = "SATISFIED"
    BLOCKED = "BLOCKED"
    UNREACHABLE = "UNREACHABLE"
    PAUSED = "PAUSED"
    ABANDONED = "ABANDONED"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    CONFLICTED = "CONFLICTED"


@dataclass(frozen=True)
class Goal:
    goal_id: str
    owner_agent_id: str
    goal_type: str
    predicate: str
    subject_id: str
    object_id: str = ""
    desired_polarity: str = "positive"
    status: GoalStatus = GoalStatus.PROPOSED
    priority: int = 100
    created_turn: int = 0
    updated_turn: int = 0
    deadline_turn: int | None = None
    parent_goal_id: str | None = None
    depends_on_goal_ids: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()
    provenance_ids: tuple[str, ...] = ()
    resolution_support_ids: tuple[str, ...] = ()

    @property
    def proposition_id(self) -> str:
        return proposition_key(self.subject_id, self.predicate, self.object_id)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["status"] = self.status.value
        return value


@dataclass(frozen=True)
class GoalVerification:
    verification_id: str
    goal_id: str
    operation: str
    previous_status: str
    requested_status: str
    approved: bool
    reason: str
    support_ids: tuple[str, ...] = ()


def goal_id(owner: str, predicate: str, subject: str, object_id: str = "", polarity: str = "positive") -> str:
    slug = ":".join(value for value in (owner, subject, predicate, object_id, polarity) if value)
    return "goal:" + slug


class GoalStore:
    ALLOWED = {
        GoalStatus.PROPOSED: {GoalStatus.ACTIVE, GoalStatus.ABANDONED},
        GoalStatus.ACTIVE: {GoalStatus.SATISFIED, GoalStatus.BLOCKED, GoalStatus.UNREACHABLE, GoalStatus.PAUSED, GoalStatus.ABANDONED, GoalStatus.BUDGET_EXHAUSTED, GoalStatus.CONFLICTED},
        GoalStatus.BLOCKED: {GoalStatus.ACTIVE, GoalStatus.UNREACHABLE, GoalStatus.PAUSED, GoalStatus.ABANDONED, GoalStatus.BUDGET_EXHAUSTED},
        GoalStatus.PAUSED: {GoalStatus.ACTIVE, GoalStatus.ABANDONED},
        GoalStatus.CONFLICTED: {GoalStatus.ACTIVE, GoalStatus.PAUSED, GoalStatus.ABANDONED},
        GoalStatus.BUDGET_EXHAUSTED: {GoalStatus.ACTIVE, GoalStatus.ABANDONED},
        GoalStatus.SATISFIED: set(), GoalStatus.UNREACHABLE: set(), GoalStatus.ABANDONED: set(),
    }

    def __init__(self, *, max_goals: int = 64) -> None:
        self.max_goals = max_goals
        self.goals: dict[str, Goal] = {}
        self.verifications: list[GoalVerification] = []

    def to_dict(self) -> dict[str, Any]:
        return {key: item.to_dict() for key, item in sorted(self.goals.items())}

    @property
    def hash(self) -> str:
        return canonical_hash(self.to_dict())

    def propose(self, goal: Goal) -> GoalVerification:
        valid = (
            goal.goal_type == "state_goal" and goal.predicate != "" and goal.subject_id != ""
            and goal.desired_polarity in {"positive", "negative"} and 0 <= goal.priority <= 1000
        )
        duplicate = goal.goal_id in self.goals
        approved = valid and (duplicate or len(self.goals) < self.max_goals)
        reason = "GOAL_SCHEMA_VERIFIED" if approved else "DUPLICATE_GOAL" if duplicate else "GOAL_SCHEMA_REJECTED"
        if approved and not duplicate:
            self.goals[goal.goal_id] = goal
        return self._record(goal.goal_id, "create", "", GoalStatus.PROPOSED.value, approved, reason, goal.source_ids)

    def transition(
        self,
        goal_id_value: str,
        status: GoalStatus,
        *,
        turn: int,
        signed_state: Mapping[str, SignedProposition] | None = None,
        support_ids: Iterable[str] = (),
    ) -> GoalVerification:
        goal = self.goals[goal_id_value]
        supports = tuple(sorted(set(support_ids)))
        approved = status in self.ALLOWED[goal.status]
        reason = "GOAL_TRANSITION_ALLOWED" if approved else "GOAL_TRANSITION_DISALLOWED"
        if status == GoalStatus.SATISFIED:
            observed = (signed_state or {}).get(goal.proposition_id)
            desired = SUPPORTED_TRUE if goal.desired_polarity == "positive" else SUPPORTED_FALSE
            approved = bool(observed and observed.status == desired)
            supports = tuple(sorted(set(
                observed.positive_support_ids if observed and desired == SUPPORTED_TRUE else
                observed.negative_support_ids if observed else ()
            )))
            reason = "GOAL_TARGET_SUPPORTED" if approved else "GOAL_TARGET_NOT_SUPPORTED"
        if approved:
            self.goals[goal_id_value] = replace(goal, status=status, updated_turn=turn, resolution_support_ids=supports)
        return self._record(goal.goal_id, "transition", goal.status.value, status.value, approved, reason, supports)

    def evaluate(self, signed_state: Mapping[str, SignedProposition], *, turn: int) -> tuple[GoalVerification, ...]:
        results: list[GoalVerification] = []
        for goal in sorted(self.goals.values(), key=lambda item: item.goal_id):
            if goal.status not in {GoalStatus.ACTIVE, GoalStatus.BLOCKED, GoalStatus.CONFLICTED}:
                continue
            observed = signed_state.get(goal.proposition_id)
            if observed and observed.status == CONFLICTED and goal.status == GoalStatus.ACTIVE:
                results.append(self.transition(goal.goal_id, GoalStatus.CONFLICTED, turn=turn, signed_state=signed_state))
            elif observed and observed.status == (SUPPORTED_TRUE if goal.desired_polarity == "positive" else SUPPORTED_FALSE):
                if goal.status != GoalStatus.ACTIVE:
                    results.append(self.transition(goal.goal_id, GoalStatus.ACTIVE, turn=turn))
                results.append(self.transition(goal.goal_id, GoalStatus.SATISFIED, turn=turn, signed_state=signed_state))
        return tuple(results)

    def select(self, tensions: Mapping[str, float], *, owner_agent_id: str | None = None) -> tuple[Goal | None, tuple[dict[str, Any], ...]]:
        candidates = [
            item for item in self.goals.values()
            if item.status == GoalStatus.ACTIVE and (owner_agent_id is None or item.owner_agent_id == owner_agent_id)
        ]
        ranked = sorted(candidates, key=lambda item: (-item.priority, -tensions.get(item.goal_id, 0.0), item.created_turn, item.goal_id))
        evidence = tuple({"goal_id": item.goal_id, "priority": item.priority, "tension": tensions.get(item.goal_id, 0.0), "created_turn": item.created_turn, "rank": index + 1} for index, item in enumerate(ranked))
        return (ranked[0] if ranked else None), evidence

    def _record(self, goal_id_value: str, operation: str, previous: str, requested: str, approved: bool, reason: str, support_ids: Iterable[str]) -> GoalVerification:
        payload = {"goal": goal_id_value, "operation": operation, "previous": previous, "requested": requested, "approved": approved, "reason": reason, "support": tuple(sorted(set(support_ids)))}
        result = GoalVerification("goal_verification:" + canonical_hash(payload)[:16], goal_id_value, operation, previous, requested, approved, reason, payload["support"])
        self.verifications.append(result)
        return result


class TensionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    RELAXED = "RELAXED"


@dataclass(frozen=True)
class TensionRecord:
    tension_id: str
    source_type: str
    source_id: str
    target_semantic_ids: tuple[str, ...]
    raw_value: float
    propagated_value: float
    total_value: float
    created_step: int
    last_updated_step: int
    status: TensionStatus
    resolution_condition: str
    source_ids: tuple[str, ...] = ()
    propagation_receipts: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["status"] = self.status.value
        return value


TENSION_CONSTANTS: dict[str, float] = {
    "unsatisfied_goal": 0.50, "blocked_goal": 0.30, "failed_action": 0.40,
    "missing_precondition": 0.20, "conflicted_required_state": 0.35,
    "unexpected_environment_change": 0.30, "stale_plan": 0.25,
    "unreachable_route": 0.30, "competing_goal": 0.20, "ambiguous_world": 0.20,
    "repeated_repair": 0.15, "budget_pressure": 0.20,
}


@dataclass(frozen=True)
class ComputeTier:
    name: str
    cluster_depth: int
    planning_depth: int
    state_budget: int
    reason: str


class TensionManager:
    def __init__(self, *, max_records: int = 256, max_depth: int = 3, decay: float = 0.5, clamp: float = 1.0) -> None:
        self.max_records = max_records
        self.max_depth = max_depth
        self.decay = decay
        self.clamp = clamp
        self.records: dict[str, TensionRecord] = {}
        self.history: list[TensionRecord] = []

    def to_dict(self) -> dict[str, Any]:
        return {key: item.to_dict() for key, item in sorted(self.records.items())}

    def update(
        self,
        source_type: str,
        source_id: str,
        *,
        step: int,
        targets: Iterable[str] = (),
        resolution_condition: str = "",
        source_ids: Iterable[str] = (),
        graph: Mapping[str, Iterable[str]] | None = None,
        resolved: bool = False,
    ) -> TensionRecord:
        identity = f"tension:{source_type}:{source_id}"
        if identity not in self.records and len(self.records) >= self.max_records:
            raise OverflowError("MAX_TENSION_RECORDS")
        previous = self.records.get(identity)
        created = previous.created_step if previous else step
        raw = 0.0 if resolved else TENSION_CONSTANTS[source_type]
        propagation, receipts = self._propagate(tuple(sorted(set(targets))), raw, graph or {})
        propagated = sum(value for _, value in propagation.items())
        result = TensionRecord(identity, source_type, source_id, tuple(sorted(set(targets))), raw, round(propagated, 6), round(min(self.clamp, raw + propagated), 6), created, step, TensionStatus.RELAXED if resolved else TensionStatus.ACTIVE, resolution_condition, tuple(sorted(set(source_ids))), receipts)
        if previous:
            self.history.append(previous)
        self.records[identity] = result
        return result

    def _propagate(self, targets: tuple[str, ...], raw: float, graph: Mapping[str, Iterable[str]]) -> tuple[dict[str, float], tuple[dict[str, Any], ...]]:
        best: dict[str, float] = {}
        receipts: list[dict[str, Any]] = []
        frontier = [(target, 0, raw) for target in targets]
        seen_depth: dict[str, int] = {target: 0 for target in targets}
        while frontier:
            node, depth, value = frontier.pop(0)
            if depth >= self.max_depth:
                continue
            for other in sorted(set(graph.get(node, ()))):
                next_value = round(value * self.decay, 6)
                next_depth = depth + 1
                if next_value <= best.get(other, 0.0) or next_depth > self.max_depth:
                    continue
                best[other] = next_value
                receipts.append({"from": node, "to": other, "depth": next_depth, "value": next_value})
                if next_depth < seen_depth.get(other, self.max_depth + 1):
                    seen_depth[other] = next_depth
                    frontier.append((other, next_depth, next_value))
        return best, tuple(receipts)

    def goal_scores(self) -> dict[str, float]:
        scores: dict[str, float] = {}
        for item in self.records.values():
            if item.status == TensionStatus.ACTIVE:
                scores[item.source_id] = round(min(self.clamp, scores.get(item.source_id, 0.0) + item.total_value), 6)
        return scores

    def total(self) -> float:
        return round(min(self.clamp, sum(item.total_value for item in self.records.values() if item.status == TensionStatus.ACTIVE)), 6)

    def compute_tier(self) -> ComputeTier:
        total = self.total()
        if total < 0.4:
            return ComputeTier("LOW", 2, 4, 128, f"total_tension={total:.2f}<0.40")
        if total < 0.75:
            return ComputeTier("MEDIUM", 4, 8, 512, f"0.40<=total_tension={total:.2f}<0.75")
        return ComputeTier("HIGH", 6, 12, 2048, f"total_tension={total:.2f}>=0.75")
