"""Bounded structured request authority for the TSLC vertical slice."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .typed_support import canonical_hash


@dataclass(frozen=True)
class StructuredEntity:
    entity_id: str
    name: str
    entity_type: str = "thing"


@dataclass(frozen=True)
class StructuredRelation:
    relation_id: str
    subject_id: str
    predicate: str
    object_id: str
    kind: str = "fact"  # fact, query, possibility
    polarity: str = "positive"
    source_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class StructuredClaim:
    claim_id: str
    subject_id: str
    predicate: str
    object_id: str = ""
    polarity: str = "positive"
    modality: str = "asserted"
    source_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class StructuredConstraint:
    constraint_id: str
    kind: str
    operands: tuple[str, ...]
    consequent: str = ""
    source_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class Ambiguity:
    code: str
    message: str
    options: tuple[str, ...] = ()
    blocking: bool = True
    question: str = ""


@dataclass(frozen=True)
class ProvenanceRecord:
    provenance_id: str
    source_type: str
    source_id: str
    rule_id: str = ""
    original_span: str = ""


@dataclass(frozen=True)
class ReasoningRequest:
    request_id: str
    original_text: str
    intent: str
    claims: tuple[StructuredClaim, ...] = ()
    entities: tuple[StructuredEntity, ...] = ()
    relations: tuple[StructuredRelation, ...] = ()
    constraints: tuple[StructuredConstraint, ...] = ()
    ambiguities: tuple[Ambiguity, ...] = ()
    provenance: tuple[ProvenanceRecord, ...] = ()
    requested_output: str = "response"
    bridge_warnings: tuple[str, ...] = ()
    repair_actions: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def canonical_hash(self) -> str:
        payload = self.to_dict()
        payload["request_id"] = ""
        return canonical_hash(payload)


@dataclass(frozen=True)
class VerifierCheck:
    check_id: str
    passed: bool
    message: str
    support_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class StructuredAnswer:
    answer_type: str
    subject: str = ""
    predicate: str = ""
    object: str = ""
    property: str = ""
    claim: str = ""
    clarification: str = ""
    support_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class VerifierDecision:
    decision: str
    reason: str
    checks: tuple[VerifierCheck, ...]
    answer: StructuredAnswer
    unsupported_claims: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    ambiguities: tuple[str, ...] = ()
    repair_attempted: bool = False
    repair_actions: tuple[str, ...] = ()
    repair_result: str | None = None
    approved_memory_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class StructuredRequestVerifier:
    """Verifier authority for five explicitly bounded reasoning families."""

    TRANSITIVE = frozenset({"older_than"})
    FUNCTIONAL = frozenset({"opens"})

    def verify(self, request: ReasoningRequest) -> VerifierDecision:
        checks = [VerifierCheck("request_schema_valid", True, "Structured request loaded.")]
        blocking = [item for item in request.ambiguities if item.blocking]
        if blocking:
            question = blocking[0].question or blocking[0].message
            checks.append(VerifierCheck("ambiguity_resolved", False, blocking[0].message))
            return VerifierDecision(
                decision="REPAIR",
                reason="unresolved_ambiguity",
                checks=tuple(checks),
                answer=StructuredAnswer("clarification", clarification=question),
                ambiguities=tuple(item.message for item in blocking),
                repair_attempted=True,
                repair_actions=request.repair_actions,
                repair_result="REPAIR_NEEDS_USER",
            )
        if any(warning.startswith("BLOCKING:") for warning in request.bridge_warnings):
            checks.append(VerifierCheck("bridge_complete", False, "Bridge reported information loss."))
            return self._reject(request, checks, "bridge_information_loss")

        contradictions = self._contradictions(request)
        if contradictions:
            checks.append(VerifierCheck("no_blocking_contradiction", False, contradictions[0]))
            return self._reject(request, checks, "contradiction", contradictions=contradictions)
        checks.append(VerifierCheck("no_blocking_contradiction", True, "No blocking contradiction found."))

        if request.intent == "assert":
            facts = (
                *(r.relation_id for r in request.relations if r.kind == "fact" and r.source_ids),
                *(c.claim_id for c in request.claims if c.modality == "asserted" and c.source_ids),
                *(c.constraint_id for c in request.constraints if c.source_ids),
            )
            checks.append(VerifierCheck("premises_representable", bool(facts), "User premises are structurally representable.", facts))
            if not facts:
                return self._reject(request, checks, "unsupported_input")
            answer = StructuredAnswer("recorded", support_ids=facts)
            return self._finish(request, checks, answer, facts)
        if request.intent == "relational_query":
            return self._verify_relation(request, checks)
        if request.intent == "ordering_query":
            return self._verify_ordering(request, checks)
        if request.intent == "boolean_query":
            return self._verify_boolean(request, checks)
        if request.intent == "planning_query":
            return self._verify_plan(request, checks)
        return self._reject(request, checks, "unsupported_intent")

    def _finish(self, request, checks, answer, approved=()) -> VerifierDecision:
        repair = bool(request.repair_actions)
        checks.append(VerifierCheck("renderer_support_available", True, "Approved structured answer has support IDs.", answer.support_ids))
        return VerifierDecision(
            decision="REPAIR" if repair else "ACCEPT",
            reason="verified_support",
            checks=tuple(checks),
            answer=answer,
            repair_attempted=repair,
            repair_actions=request.repair_actions,
            repair_result="REPAIR_ACCEPTED" if repair else None,
            approved_memory_ids=tuple(approved),
        )

    def _reject(self, request, checks, reason, *, unsupported=(), contradictions=()) -> VerifierDecision:
        return VerifierDecision(
            decision="REJECT", reason=reason, checks=tuple(checks),
            answer=StructuredAnswer("rejection", claim=self._query_claim(request)),
            unsupported_claims=tuple(unsupported), contradictions=tuple(contradictions),
        )

    def _facts(self, request, predicate=None):
        return [r for r in request.relations if r.kind == "fact" and (predicate is None or r.predicate == predicate)]

    def _query(self, request):
        return next((r for r in request.relations if r.kind == "query"), None)

    def _verify_relation(self, request, checks):
        query = self._query(request)
        if query is None:
            return self._reject(request, checks, "missing_query")
        matches = [r for r in self._facts(request, query.predicate) if r.subject_id == query.subject_id and (not query.object_id or r.object_id == query.object_id)]
        if len(matches) == 1:
            relation = matches[0]
            checks.append(VerifierCheck("direct_relation_supported", True, "Direct relation found.", (relation.relation_id,)))
            return self._finish(request, checks, StructuredAnswer("fact", relation.subject_id, relation.predicate, relation.object_id, support_ids=(relation.relation_id,)))
        claim = self._query_claim(request)
        checks.append(VerifierCheck("direct_relation_supported", False, "No unique direct support path."))
        return self._reject(request, checks, "insufficient_support", unsupported=(claim,))

    def _verify_ordering(self, request, checks):
        query = self._query(request)
        facts = self._facts(request, "older_than")
        if query is None or query.predicate != "oldest":
            return self._reject(request, checks, "unsupported_ordering_query")
        nodes = {x for r in facts for x in (r.subject_id, r.object_id)}
        incoming = {node: 0 for node in nodes}
        for relation in facts:
            incoming[relation.object_id] += 1
        candidates = sorted(node for node, count in incoming.items() if count == 0)
        if len(candidates) != 1:
            checks.append(VerifierCheck("unique_ordering_answer", False, "Ordering has no unique maximum."))
            return self._reject(request, checks, "insufficient_support", unsupported=("unique oldest entity",))
        support = tuple(r.relation_id for r in facts)
        checks.append(VerifierCheck("relation_chain_supported", True, "Unique ordering maximum follows from the chain.", support))
        return self._finish(request, checks, StructuredAnswer("ordering", candidates[0], property="oldest", support_ids=support))

    def _verify_boolean(self, request, checks):
        facts = {c.predicate for c in request.claims if c.modality == "asserted" and c.polarity == "positive"}
        fact_ids = {c.predicate: c.claim_id for c in request.claims if c.modality == "asserted"}
        changed = True
        derived: dict[str, tuple[str, ...]] = {}
        while changed:
            changed = False
            for rule in request.constraints:
                if rule.kind != "boolean_rule" or not rule.consequent or rule.consequent in facts:
                    continue
                if all(item in facts for item in rule.operands):
                    facts.add(rule.consequent)
                    derived[rule.consequent] = (rule.constraint_id, *(fact_ids.get(x, x) for x in rule.operands))
                    changed = True
        query = next((c for c in request.claims if c.modality == "query"), None)
        if query and query.predicate in facts:
            support = derived.get(query.predicate, (fact_ids.get(query.predicate, query.claim_id),))
            checks.append(VerifierCheck("boolean_rule_supported", True, "All rule antecedents are supported.", support))
            return self._finish(request, checks, StructuredAnswer("boolean", query.subject_id, query.predicate, "true", support_ids=support))
        claim = query.predicate if query else "requested boolean conclusion"
        checks.append(VerifierCheck("boolean_rule_supported", False, "Required antecedent support is missing."))
        return self._reject(request, checks, "insufficient_support", unsupported=(claim,))

    def _verify_plan(self, request, checks):
        edges = [(c.operands[0], c.operands[1], c.constraint_id) for c in request.constraints if c.kind == "before" and len(c.operands) == 2]
        nodes = {x for a, b, _ in edges for x in (a, b)}
        incoming = {node: 0 for node in nodes}
        for _, b, _ in edges: incoming[b] += 1
        first = sorted(node for node, count in incoming.items() if count == 0)
        if len(first) != 1:
            checks.append(VerifierCheck("planning_order_supported", False, "No unique first action."))
            return self._reject(request, checks, "insufficient_support", unsupported=("unique first action",))
        support = tuple(edge[2] for edge in edges)
        checks.append(VerifierCheck("planning_order_supported", True, "Explicit ordering constraint identifies the first action.", support))
        target = next(b for a, b, _ in edges if a == first[0])
        return self._finish(request, checks, StructuredAnswer("plan", first[0], "before", target, support_ids=support))

    def _contradictions(self, request):
        facts = self._facts(request)
        problems = []
        positive = {(r.subject_id, r.predicate, r.object_id) for r in facts if r.polarity == "positive"}
        negative = {(r.subject_id, r.predicate, r.object_id) for r in facts if r.polarity == "negative"}
        for item in sorted(positive & negative): problems.append(f"Both positive and negative forms are asserted: {item}.")
        for predicate in self.FUNCTIONAL:
            grouped: dict[str, set[str]] = {}
            for r in facts:
                if r.predicate == predicate: grouped.setdefault(r.subject_id, set()).add(r.object_id)
            for subject, objects in grouped.items():
                if len(objects) > 1: problems.append(f"Conflicting {predicate} targets for {subject}: {sorted(objects)}.")
        older = {(r.subject_id, r.object_id) for r in facts if r.predicate == "older_than"}
        for a, b in older:
            if a == b or (b, a) in older: problems.append(f"Contradictory older-than relation between {a} and {b}.")
        return tuple(sorted(set(problems)))

    def _query_claim(self, request):
        query = self._query(request)
        if query: return " ".join(x for x in (query.subject_id, query.predicate, query.object_id) if x)
        claim = next((c for c in request.claims if c.modality == "query"), None)
        return claim.predicate if claim else request.original_text


def verify_reasoning_request(request: ReasoningRequest) -> VerifierDecision:
    return StructuredRequestVerifier().verify(request)
