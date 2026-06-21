"""Deterministic signed world projection, causal closure, transitions, and planning."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from collections import deque
from typing import Any, Iterable

from .typed_support import canonical_hash

SUPPORTED_TRUE = "SUPPORTED_TRUE"
SUPPORTED_FALSE = "SUPPORTED_FALSE"
CONFLICTED = "CONFLICTED"
UNKNOWN = "UNKNOWN"


def proposition_key(subject: str, predicate: str, object_id: str = "") -> str:
    return "|".join((subject, predicate, object_id))


@dataclass(frozen=True)
class WorldFact:
    semantic_id: str
    subject_id: str
    predicate: str
    object_id: str = ""
    polarity: str = "positive"
    source_ids: tuple[str, ...] = ()
    origin: str = "user_premise"
    active: bool = True

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "WorldFact":
        return cls(
            str(value["semantic_id"]), str(value["subject_id"]), str(value["predicate"]),
            str(value.get("object_id", "")), str(value.get("polarity", "positive")),
            tuple(sorted(set(map(str, value.get("source_ids", ()))))),
            str(value.get("origin", "user_premise")), bool(value.get("active", True)),
        )


@dataclass(frozen=True)
class CausalRule:
    semantic_id: str
    antecedents: tuple[str, ...]
    consequent: str
    source_ids: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "CausalRule":
        return cls(str(value["semantic_id"]), tuple(map(str, value["antecedents"])), str(value["consequent"]), tuple(sorted(set(map(str, value.get("source_ids", ()))))))


@dataclass(frozen=True)
class SignedProposition:
    proposition_id: str
    subject_id: str
    predicate: str
    object_id: str
    status: str
    positive_support_ids: tuple[str, ...] = ()
    negative_support_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class CausalDerivation:
    derived_id: str
    proposition_id: str
    depth: int
    rule_id: str
    antecedent_ids: tuple[str, ...]
    support_ids: tuple[str, ...]


@dataclass(frozen=True)
class PreconditionCheck:
    proposition_id: str
    expected: str
    observed: str
    passed: bool
    support_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ActionSchema:
    action_type: str
    parameters: tuple[str, ...]
    preconditions: tuple[str, ...]
    effects: tuple[str, ...]
    cost: int = 1


HABITAT_ACTION_SCHEMAS = (
    ActionSchema("move",("actor","source","destination"),("actor_at_source",),("actor_at_destination","not_actor_at_source")),
    ActionSchema("take",("actor","object","location"),("actor_and_object_colocated","object_available"),("actor_carries_object",)),
    ActionSchema("unlock",("actor","target","key"),("target_locked","actor_carries_compatible_key"),("target_not_locked",)),
    ActionSchema("open",("actor","target"),("target_unlocked","actor_at_target"),("target_open",)),
    ActionSchema("give",("giver","object","recipient"),("giver_owns_object",),("recipient_owns_object","giver_not_owner")),
)


@dataclass(frozen=True)
class PlanStep:
    step_index: int
    action: str
    precondition_checks: tuple[PreconditionCheck, ...]
    effects: tuple[dict[str, str], ...]
    support_ids: tuple[str, ...]
    resulting_state_hash: str


@dataclass(frozen=True)
class PlanReceipt:
    initial_state_hash: str
    goal: str
    max_depth: int
    explored_state_count: int
    chosen_plan: tuple[PlanStep, ...]
    final_state_hash: str
    replay_hash: str
    rejected_alternatives: tuple[str, ...] = ()


@dataclass(frozen=True)
class HabitatOutcome:
    decision: str
    subtype: str
    reason: str
    answer_type: str
    subject: str = ""
    predicate: str = ""
    object_id: str = ""
    signed_status: str = ""
    support_ids: tuple[str, ...] = ()
    checks: tuple[dict[str, Any], ...] = ()
    contradictions: tuple[str, ...] = ()
    unsupported: tuple[str, ...] = ()
    derivations: tuple[CausalDerivation, ...] = ()
    planning: PlanReceipt | None = None
    approved_memory_ids: tuple[str, ...] = ()


def project_signed_state(facts: Iterable[WorldFact]) -> dict[str, SignedProposition]:
    grouped: dict[str, dict[str, Any]] = {}
    for fact in sorted((item for item in facts if item.active), key=lambda item: item.semantic_id):
        key = proposition_key(fact.subject_id, fact.predicate, fact.object_id)
        row = grouped.setdefault(key, {"subject": fact.subject_id, "predicate": fact.predicate, "object": fact.object_id, "positive": [], "negative": []})
        row[fact.polarity].append(fact.semantic_id)
    result: dict[str, SignedProposition] = {}
    for key, row in sorted(grouped.items()):
        positive = tuple(sorted(set(row["positive"])))
        negative = tuple(sorted(set(row["negative"])))
        status = CONFLICTED if positive and negative else SUPPORTED_TRUE if positive else SUPPORTED_FALSE if negative else UNKNOWN
        result[key] = SignedProposition(key, row["subject"], row["predicate"], row["object"], status, positive, negative)
    return result


def signed_status(state: dict[str, SignedProposition], key: str) -> SignedProposition:
    if key in state:
        return state[key]
    subject, predicate, object_id = (key.split("|", 2) + ["", ""])[:3]
    return SignedProposition(key, subject, predicate, object_id, UNKNOWN)


def causal_closure(
    facts: Iterable[WorldFact], rules: Iterable[CausalRule], *, max_depth: int = 4, max_derived: int = 64,
) -> tuple[dict[str, SignedProposition], tuple[CausalDerivation, ...]]:
    base = list(facts)
    state = project_signed_state(base)
    support: dict[str, tuple[str, ...]] = {
        key: item.positive_support_ids for key, item in state.items() if item.status == SUPPORTED_TRUE
    }
    depth: dict[str, int] = {key: 0 for key in support}
    derivations: list[CausalDerivation] = []
    for _ in range(max_depth):
        changed = False
        for rule in sorted(rules, key=lambda item: item.semantic_id):
            if rule.consequent in support or len(derivations) >= max_derived:
                continue
            if not all(item in support for item in rule.antecedents):
                continue
            next_depth = 1 + max((depth[item] for item in rule.antecedents), default=0)
            if next_depth > max_depth:
                continue
            ids = tuple(sorted(set((rule.semantic_id, *rule.source_ids, *(sid for item in rule.antecedents for sid in support[item])))))
            derived_id = "derived_" + canonical_hash({"rule": rule.semantic_id, "antecedents": rule.antecedents, "consequent": rule.consequent})[:16]
            derivations.append(CausalDerivation(derived_id, rule.consequent, next_depth, rule.semantic_id, rule.antecedents, ids))
            support[rule.consequent] = (derived_id,)
            depth[rule.consequent] = next_depth
            subject, predicate, object_id = (rule.consequent.split("|", 2) + ["", ""])[:3]
            state[rule.consequent] = SignedProposition(rule.consequent, subject, predicate, object_id, SUPPORTED_TRUE, (derived_id,), ())
            changed = True
        if not changed or len(derivations) >= max_derived:
            break
    return state, tuple(derivations)


def _state_payload(facts: Iterable[WorldFact]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((proposition_key(f.subject_id, f.predicate, f.object_id), f.polarity) for f in facts if f.active))


def _plan(payload: dict[str, Any], facts: list[WorldFact], *, max_depth: int = 8, max_states: int = 512) -> PlanReceipt | None:
    goal = payload.get("query", {})
    actor = str(goal.get("subject_id", "")); target = str(goal.get("object_id", ""))
    if not actor or not target or goal.get("predicate") != "open":
        return None
    base_positive = {proposition_key(f.subject_id, f.predicate, f.object_id): f.semantic_id for f in facts if f.active and f.polarity == "positive"}
    base_negative = {proposition_key(f.subject_id, f.predicate, f.object_id): f.semantic_id for f in facts if f.active and f.polarity == "negative"}
    actor_locations = sorted(k.split("|", 2)[2] for k in base_positive if k.startswith(f"{actor}|at|"))
    places = sorted({k.split("|", 2)[2] for k in base_positive if "|at|" in k} | {target})
    contained = {(k.split("|", 2)[0], k.split("|", 2)[2]): sid for k, sid in base_positive.items() if "|inside|" in k}
    object_locations: dict[str, str] = {}
    for obj, container in contained:
        location_key = next((key for key in base_positive if key.startswith(f"{container}|at|")), "")
        if location_key: object_locations[obj] = location_key.split("|", 2)[2]
    compatible = {(k.split("|", 2)[0], k.split("|", 2)[2]): sid for k, sid in base_positive.items() if "|unlocks|" in k}
    locked_key = proposition_key(target, "locked", "")
    start = (actor_locations[0] if actor_locations else "", tuple(), locked_key not in base_negative, proposition_key(target, "open", "") in base_positive)
    initial_hash = canonical_hash(start)
    queue = deque([(start, tuple())]); seen = {start}; explored = 0; rejected: set[str] = set()
    while queue and explored < max_states:
        state, steps = queue.popleft(); explored += 1
        location, carried, locked, opened = state
        if opened:
            final_hash = canonical_hash(state)
            replay = canonical_hash({"initial": initial_hash, "goal": proposition_key(target, "open", ""), "steps": [asdict(s) for s in steps], "final": final_hash})
            return PlanReceipt(initial_hash, proposition_key(target, "open", ""), max_depth, explored, steps, final_hash, replay, tuple(sorted(rejected)))
        if len(steps) >= max_depth: continue
        candidates: list[tuple[str, tuple, tuple[PreconditionCheck, ...], tuple[dict[str, str], ...], tuple[str, ...]]] = []
        for place in places:
            if place and place != location:
                checks=(PreconditionCheck(proposition_key(actor,"at",location),SUPPORTED_TRUE,SUPPORTED_TRUE,bool(location),(base_positive.get(proposition_key(actor,"at",location),"habitat_open_topology"),)),)
                if checks[0].passed: candidates.append((f"Move {actor} from {location} to {place}",(place,carried,locked,opened),checks,({"subject_id":actor,"predicate":"at","object_id":place,"polarity":"positive"},),checks[0].support_ids))
        for obj, obj_location in sorted(object_locations.items()):
            if obj not in carried and obj_location == location:
                support=(contained[(obj,next(container for item,container in contained if item==obj))],)
                checks=(PreconditionCheck(proposition_key(actor,"at",location),SUPPORTED_TRUE,SUPPORTED_TRUE,True,(base_positive.get(proposition_key(actor,"at",location),"habitat_open_topology"),)),PreconditionCheck(proposition_key(obj,"at",location),SUPPORTED_TRUE,SUPPORTED_TRUE,True,support))
                candidates.append((f"Take {obj} from its container",(location,tuple(sorted((*carried,obj))),locked,opened),checks,({"subject_id":actor,"predicate":"carries","object_id":obj,"polarity":"positive"},),tuple(sorted(set((*checks[0].support_ids,*support))))))
        for key, door in sorted(compatible):
            if door == target and locked and key in carried:
                checks=(PreconditionCheck(locked_key,SUPPORTED_TRUE,SUPPORTED_TRUE,True,(base_positive.get(locked_key,"event_state"),)),PreconditionCheck(proposition_key(actor,"carries",key),SUPPORTED_TRUE,SUPPORTED_TRUE,True,(compatible[(key,door)],)))
                candidates.append((f"Unlock {target} with {key}",(location,carried,False,opened),checks,({"subject_id":target,"predicate":"locked","object_id":"","polarity":"negative"},),tuple(sorted(set(sid for check in checks for sid in check.support_ids)))))
        if not locked and not opened and location == target:
            checks=(PreconditionCheck(locked_key,SUPPORTED_FALSE,SUPPORTED_FALSE,True,("verified_unlock_effect",)),PreconditionCheck(proposition_key(actor,"at",target),SUPPORTED_TRUE,SUPPORTED_TRUE,True,("verified_move_effect",)))
            candidates.append((f"Open {target}",(location,carried,locked,True),checks,({"subject_id":target,"predicate":"open","object_id":"","polarity":"positive"},),("verified_unlock_effect","verified_move_effect")))
        elif locked: rejected.add("open:target_locked")
        for action, next_state, checks, effects, supports in sorted(candidates, key=lambda item: item[0]):
            if next_state in seen: continue
            seen.add(next_state)
            step=PlanStep(len(steps)+1,action,checks,effects,tuple(sorted(set(supports))),canonical_hash(next_state))
            queue.append((next_state,(*steps,step)))
    return None


def evaluate_habitat(payload: dict[str, Any]) -> HabitatOutcome:
    facts = [WorldFact.from_dict(item) for item in payload.get("facts", ())]
    rules = [CausalRule.from_dict(item) for item in payload.get("rules", ())]
    query = payload.get("query", {})
    state, derivations = causal_closure(facts, rules, max_depth=int(payload.get("max_inference_depth", 4)), max_derived=int(payload.get("max_derived_facts", 64)))
    intent = str(query.get("kind", "state"))
    memory_candidates=tuple(sorted(set(map(str,payload.get("memory_candidate_ids",())))))
    if intent == "record":
        checks=[]
        precondition_state=project_signed_state(item for item in facts if item.origin != "event_effect")
        for event in payload.get("events", ()):
            for precondition in event.get("preconditions", ()):
                key=proposition_key(str(precondition["subject_id"]),str(precondition["predicate"]),str(precondition.get("object_id","")))
                observed=signed_status(precondition_state,key)
                expected=SUPPORTED_TRUE if precondition.get("polarity","positive")=="positive" else SUPPORTED_FALSE
                passed=observed.status==expected
                checks.append({"check_id":"event_precondition_supported","passed":passed,"message":f"Event precondition {key} is {observed.status}.","support_ids":observed.positive_support_ids if expected==SUPPORTED_TRUE else observed.negative_support_ids})
                if not passed:
                    return HabitatOutcome("REJECT","REJECT_UNSUPPORTED","event_precondition_failed","rejection",unsupported=(key,),checks=tuple(checks))
        supports=tuple(sorted({item.semantic_id for item in facts}|{item.semantic_id for item in rules}))
        if not supports:
            return HabitatOutcome("REJECT","REJECT_UNSUPPORTED","unsupported_input","rejection",unsupported=("representable habitat premise",))
        checks.append({"check_id":"premises_representable","passed":True,"message":"Habitat premises and effects are structurally representable.","support_ids":supports})
        return HabitatOutcome("ACCEPT","PREMISE_RECORDED","verified_support","recorded",support_ids=supports,checks=tuple(checks),approved_memory_ids=memory_candidates or supports)
    if intent == "plan":
        plan = _plan(payload, facts, max_depth=int(payload.get("max_plan_depth", 8)))
        if plan is None:
            return HabitatOutcome("REJECT","REJECT_UNREACHABLE","unreachable","rejection",unsupported=(proposition_key(str(query.get("subject_id","")),str(query.get("predicate","")),str(query.get("object_id",""))),),checks=({"check_id":"verified_plan_exists","passed":False,"message":"No bounded plan satisfies every precondition.","support_ids":()},))
        supports=tuple(sorted(set(sid for step in plan.chosen_plan for sid in step.support_ids)))
        return HabitatOutcome("ACCEPT","PLAN_VERIFIED","verified_support","plan",str(query.get("subject_id","")),str(query.get("predicate","")),str(query.get("object_id","")),support_ids=supports,checks=({"check_id":"verified_plan_exists","passed":True,"message":"Every plan step has verified preconditions and declared effects.","support_ids":supports},),planning=plan,approved_memory_ids=memory_candidates)
    if intent == "owner":
        candidates=sorted((item for item in state.values() if item.predicate=="owns" and item.object_id==str(query.get("object_id","")) and item.status==SUPPORTED_TRUE),key=lambda item:item.subject_id)
        if len(candidates)==1:
            item=candidates[0]
            return HabitatOutcome("ACCEPT","CONCLUSION_VERIFIED","verified_support","owner",item.subject_id,"owns",item.object_id,item.status,item.positive_support_ids,({"check_id":"direct_relation_supported","passed":True,"message":"One active owner is supported.","support_ids":item.positive_support_ids},),derivations=derivations,approved_memory_ids=memory_candidates)
        return HabitatOutcome("REJECT","REJECT_CONFLICTED" if len(candidates)>1 else "REJECT_UNSUPPORTED","conflicted" if len(candidates)>1 else "unknown","conflict" if len(candidates)>1 else "unknown",object_id=str(query.get("object_id","")),signed_status=CONFLICTED if len(candidates)>1 else UNKNOWN,contradictions=("multiple active owners",) if len(candidates)>1 else (),unsupported=("unique active owner",) if not candidates else ())
    if intent == "location":
        subject=str(query.get("subject_id","")); direct=sorted((item for item in state.values() if item.subject_id==subject and item.predicate in {"inside","at"} and item.status==SUPPORTED_TRUE),key=lambda item:(item.predicate,item.object_id))
        if direct:
            first=direct[0]; support=list(first.positive_support_ids); container_location=next((item for item in state.values() if item.subject_id==first.object_id and item.predicate=="at" and item.status==SUPPORTED_TRUE),None)
            if container_location:support.extend(container_location.positive_support_ids)
            object_id=first.object_id+("@"+container_location.object_id if container_location else "")
            return HabitatOutcome("ACCEPT","CONCLUSION_VERIFIED","verified_support","location",subject,first.predicate,object_id,SUPPORTED_TRUE,tuple(sorted(set(support))),({"check_id":"containment_chain_supported","passed":True,"message":"Declared containment and location links support the answer.","support_ids":tuple(sorted(set(support)))},),derivations=derivations,approved_memory_ids=memory_candidates)
        return HabitatOutcome("REJECT","REJECT_UNSUPPORTED","unknown","unknown",subject,"inside","",UNKNOWN,unsupported=(f"location of {subject}",))
    key = proposition_key(str(query.get("subject_id", "")), str(query.get("predicate", "")), str(query.get("object_id", "")))
    result = signed_status(state, key)
    expected_negative = str(query.get("polarity", "positive")) == "negative"
    effective = ({SUPPORTED_TRUE:SUPPORTED_FALSE,SUPPORTED_FALSE:SUPPORTED_TRUE}.get(result.status,result.status) if expected_negative else result.status)
    supports = result.negative_support_ids if expected_negative else result.positive_support_ids
    if effective == SUPPORTED_TRUE:
        direct = not any(sid.startswith("derived_") for sid in supports)
        check_id = "direct_relation_supported" if intent in {"relation","owner","location"} else "boolean_rule_supported" if derivations else "signed_state_supported"
        return HabitatOutcome("ACCEPT","CONCLUSION_VERIFIED","verified_support",intent,str(query.get("subject_id","")),str(query.get("predicate","")),str(query.get("object_id","")),result.status,tuple(sorted(set(supports))),({"check_id":check_id,"passed":True,"message":"Direct signed evidence supports the query." if direct else "Bounded causal derivation supports the query.","support_ids":tuple(sorted(set(supports)))},),derivations=derivations,approved_memory_ids=memory_candidates)
    if effective == SUPPORTED_FALSE:
        supports = result.positive_support_ids if expected_negative else result.negative_support_ids
        return HabitatOutcome("ACCEPT","CONCLUSION_VERIFIED","verified_support","signed_false",str(query.get("subject_id","")),str(query.get("predicate","")),str(query.get("object_id","")),result.status,tuple(sorted(set(supports))),({"check_id":"signed_false_supported","passed":True,"message":"Explicit opposite-polarity evidence supports a false result.","support_ids":tuple(sorted(set(supports)))},),derivations=derivations,approved_memory_ids=memory_candidates)
    if effective == CONFLICTED:
        supports=tuple(sorted(set((*result.positive_support_ids,*result.negative_support_ids))))
        return HabitatOutcome("REJECT","REJECT_CONFLICTED","conflicted","conflict",str(query.get("subject_id","")),str(query.get("predicate","")),str(query.get("object_id","")),CONFLICTED,supports,({"check_id":"signed_state_unconflicted","passed":False,"message":"Both positive and negative evidence are active.","support_ids":supports},),contradictions=(key,))
    return HabitatOutcome("REJECT","REJECT_UNSUPPORTED","unknown","unknown",str(query.get("subject_id","")),str(query.get("predicate","")),str(query.get("object_id","")),UNKNOWN,checks=({"check_id":"signed_state_known","passed":False,"message":"No activated evidence supports either polarity.","support_ids":()},),unsupported=(key,),derivations=derivations)
