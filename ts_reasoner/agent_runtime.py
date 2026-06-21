"""Bounded verifier-first Habitat v3 agent runtime.

Plans are proposals. Only effect-verified environment observations may be committed.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from enum import Enum
from time import monotonic
from typing import Any, Iterable, Mapping, Protocol

from .agent_control import Goal, GoalStatus, GoalStore, TensionManager
from .habitat import (
    CONFLICTED, SUPPORTED_FALSE, SUPPORTED_TRUE, UNKNOWN, SignedProposition,
    WorldFact, project_signed_state, proposition_key,
)
from .topology import Connection, ConnectionStatus, SpatialTopology
from .typed_support import canonical_hash


class LoopPhase(str, Enum):
    IDLE="IDLE"; OBSERVE="OBSERVE"; UPDATE_WORLD="UPDATE_WORLD"; EVALUATE_GOALS="EVALUATE_GOALS"
    COMPUTE_TENSION="COMPUTE_TENSION"; SELECT_GOAL="SELECT_GOAL"; ACTIVATE_CLUSTER="ACTIVATE_CLUSTER"
    PLAN="PLAN"; VERIFY_PLAN="VERIFY_PLAN"; PROPOSE_ACTION="PROPOSE_ACTION"
    VERIFY_ACTION_PRECONDITIONS="VERIFY_ACTION_PRECONDITIONS"; EXECUTE_ACTION="EXECUTE_ACTION"
    VERIFY_EFFECTS="VERIFY_EFFECTS"; UPDATE_GOAL="UPDATE_GOAL"; REFLECT="REFLECT"; REPLAN="REPLAN"
    COMPLETE="COMPLETE"; BLOCKED="BLOCKED"; UNREACHABLE="UNREACHABLE"
    BUDGET_EXHAUSTED="BUDGET_EXHAUSTED"; ERROR="ERROR"


class ActionStage(str, Enum):
    ACTION_PROPOSED="ACTION_PROPOSED"; PRECONDITIONS_VERIFIED="PRECONDITIONS_VERIFIED"
    ACTION_AUTHORIZED="ACTION_AUTHORIZED"; ENVIRONMENT_EXECUTED="ENVIRONMENT_EXECUTED"
    EFFECTS_OBSERVED="EFFECTS_OBSERVED"; EFFECTS_VERIFIED="EFFECTS_VERIFIED"
    WORLD_COMMITTED="WORLD_COMMITTED"; ACTION_REJECTED="ACTION_REJECTED"
    ACTION_FAILED="ACTION_FAILED"; EFFECT_MISMATCH="EFFECT_MISMATCH"; REPLAN_REQUIRED="REPLAN_REQUIRED"


STALE_CAUSES = frozenset({
    "WORLD_CHANGED", "PRECONDITION_LOST", "ROUTE_BLOCKED", "OBJECT_MOVED", "OWNERSHIP_CHANGED",
    "GOAL_CHANGED", "CONFLICT_INTRODUCED", "ACTION_EFFECT_MISMATCH", "AGENT_INTERFERENCE",
})


@dataclass(frozen=True)
class AgentState:
    agent_id: str
    name: str
    current_location_id: str = ""
    carried_object_ids: tuple[str, ...] = ()
    owned_object_ids: tuple[str, ...] = ()
    active_goal_ids: tuple[str, ...] = ()
    policy_ids: tuple[str, ...] = ()
    status: str = "ACTIVE"


@dataclass(frozen=True)
class AgentLimits:
    max_topology_size: int = 1024
    max_semantic_memory_items: int = 4096
    max_active_cluster_items: int = 512
    max_active_goals: int = 64
    max_tension_records: int = 256
    max_planner_depth: int = 12
    max_explored_states: int = 2048
    max_replans: int = 8
    max_loop_iterations: int = 64
    max_plans_per_goal: int = 8
    max_action_executions: int = 32
    max_causal_derivations: int = 64
    max_wall_clock_duration: float = 10.0
    max_receipt_size: int = 1_000_000
    max_environment_events: int = 128
    max_agents: int = 8


@dataclass(frozen=True)
class Effect:
    subject_id: str
    predicate: str
    object_id: str = ""
    polarity: str = "positive"

    @property
    def proposition_id(self) -> str:
        return proposition_key(self.subject_id, self.predicate, self.object_id)


@dataclass(frozen=True)
class Precondition:
    subject_id: str
    predicate: str
    object_id: str = ""
    expected_status: str = SUPPORTED_TRUE

    @property
    def proposition_id(self) -> str:
        return proposition_key(self.subject_id, self.predicate, self.object_id)


@dataclass(frozen=True)
class ActionProposal:
    action_id: str
    action_type: str
    actor_id: str
    target_id: str = ""
    object_id: str = ""
    source_location_id: str = ""
    destination_location_id: str = ""
    recipient_id: str = ""
    preconditions: tuple[Precondition, ...] = ()
    expected_effects: tuple[Effect, ...] = ()
    support_ids: tuple[str, ...] = ()
    cost: int = 1


@dataclass(frozen=True)
class VerifiedAction:
    proposal: ActionProposal
    authorization_id: str
    pre_state_hash: str
    checks: tuple[dict[str, Any], ...]
    support_ids: tuple[str, ...]


@dataclass(frozen=True)
class VerifiedPlan:
    plan_id: str
    originating_world_state_hash: str
    originating_relevant_cluster_hash: str
    goal_id: str
    actions: tuple[ActionProposal, ...]
    support_ids: tuple[str, ...]
    planning_limits: dict[str, int]
    expected_intermediate_state_hashes: tuple[str, ...]
    explored_state_count: int
    verification_id: str
    completed_action_ids: tuple[str, ...] = ()
    invalidated: bool = False
    stale_cause: str = ""


@dataclass(frozen=True)
class EnvironmentEvent:
    event_id: str
    trigger: str
    trigger_value: str
    effects: tuple[Effect, ...] = ()
    connection_id: str = ""
    connection_status: str = ""
    source_ids: tuple[str, ...] = ()
    provenance_ids: tuple[str, ...] = ()
    actor_id: str = ""


@dataclass(frozen=True)
class EnvironmentObservation:
    observation_id: str
    facts: tuple[WorldFact, ...]
    topology: tuple[Connection, ...]
    agents: tuple[AgentState, ...]
    environment_step: int
    source_ids: tuple[str, ...]
    state_hash: str


@dataclass(frozen=True)
class ExecutionResult:
    execution_id: str
    action_id: str
    success: bool
    observed_effects: tuple[Effect, ...]
    observation: EnvironmentObservation
    environment_event_receipts: tuple[dict[str, Any], ...] = ()
    failure_code: str = ""


@dataclass(frozen=True)
class EnvironmentSnapshot:
    facts: tuple[WorldFact, ...]
    topology: tuple[Connection, ...]
    agents: tuple[AgentState, ...]
    step: int
    scheduled_events: tuple[EnvironmentEvent, ...]
    fired_event_ids: tuple[str, ...]
    forced_mismatch_action_types: tuple[str, ...] = ()


class EnvironmentAdapter(Protocol):
    def observe(self) -> EnvironmentObservation: ...
    def execute(self, action: VerifiedAction) -> ExecutionResult: ...
    def inject_event(self, event: EnvironmentEvent) -> None: ...
    def snapshot(self) -> EnvironmentSnapshot: ...
    def restore_for_replay(self, snapshot: EnvironmentSnapshot) -> None: ...


@dataclass
class TrustedWorld:
    facts: dict[str, WorldFact] = field(default_factory=dict)
    topology: SpatialTopology = field(default_factory=SpatialTopology)
    agents: dict[str, AgentState] = field(default_factory=dict)
    last_observation_id: str = ""

    @property
    def signed_state(self) -> dict[str, SignedProposition]:
        return project_signed_state(self.facts.values())

    @property
    def hash(self) -> str:
        return canonical_hash({
            "facts": [asdict(value) for _, value in sorted(self.facts.items())],
            "topology": self.topology.to_dict(),
            "agents": [asdict(value) for _, value in sorted(self.agents.items())],
            "observation": self.last_observation_id,
        })

    def clone(self) -> "TrustedWorld":
        return TrustedWorld(dict(self.facts), self.topology.clone(), dict(self.agents), self.last_observation_id)

    def support_for(self, precondition: Precondition) -> tuple[bool, tuple[str, ...], str]:
        observed = self.signed_state.get(precondition.proposition_id)
        status = observed.status if observed else UNKNOWN
        supports = (
            observed.positive_support_ids if observed and precondition.expected_status == SUPPORTED_TRUE else
            observed.negative_support_ids if observed and precondition.expected_status == SUPPORTED_FALSE else ()
        )
        return status == precondition.expected_status, tuple(supports), status

    def install_observation(self, observation: EnvironmentObservation, *, limits: AgentLimits) -> None:
        if len(observation.facts) > limits.max_semantic_memory_items:
            raise OverflowError("MAX_SEMANTIC_MEMORY_ITEMS")
        if len(observation.agents) > limits.max_agents:
            raise OverflowError("MAX_AGENTS")
        topology = SpatialTopology(max_connections=limits.max_topology_size)
        for edge in sorted(observation.topology, key=lambda item: item.connection_id):
            topology.merge(edge)
        self.facts = {item.semantic_id: item for item in observation.facts}
        self.topology = topology
        self.agents = {item.agent_id: item for item in observation.agents}
        self.last_observation_id = observation.observation_id


FUNCTIONAL_PREDICATES = frozenset({"at", "inside", "owns", "carries", "open", "locked", "active"})


def _effect_fact(effect: Effect, source_id: str) -> WorldFact:
    identity = "env_fact:" + canonical_hash({"effect": asdict(effect), "source": source_id})[:20]
    return WorldFact(identity, effect.subject_id, effect.predicate, effect.object_id, effect.polarity, (source_id,), "environment_observation", True)


def _apply_effects(facts: Iterable[WorldFact], effects: Iterable[Effect], source_id: str) -> tuple[WorldFact, ...]:
    result = list(facts)
    for effect in effects:
        kept: list[WorldFact] = []
        for fact in result:
            same_exact = fact.subject_id == effect.subject_id and fact.predicate == effect.predicate and fact.object_id == effect.object_id
            functional_conflict = (
                effect.polarity == "positive" and fact.polarity == "positive" and effect.predicate in FUNCTIONAL_PREDICATES
                and fact.subject_id == effect.subject_id and fact.predicate == effect.predicate
                and (effect.predicate in {"at", "inside", "owns", "carries"} or fact.object_id == effect.object_id)
            )
            if same_exact or functional_conflict:
                continue
            kept.append(fact)
        result = kept
        result.append(_effect_fact(effect, source_id))
    return tuple(sorted(result, key=lambda item: item.semantic_id))


class SymbolicEnvironment:
    """Deterministic in-process simulation. Its state is untrusted until observed and verified."""

    def __init__(self, snapshot: EnvironmentSnapshot, *, limits: AgentLimits | None = None) -> None:
        self.limits = limits or AgentLimits()
        self.restore_for_replay(snapshot)

    def snapshot(self) -> EnvironmentSnapshot:
        return EnvironmentSnapshot(tuple(self.facts), tuple(self.topology.connections.values()), tuple(self.agents.values()), self.step, tuple(self.scheduled_events), tuple(sorted(self.fired_event_ids)), tuple(sorted(self.forced_mismatch_action_types)))

    def restore_for_replay(self, snapshot: EnvironmentSnapshot) -> None:
        self.facts = list(snapshot.facts)
        self.topology = SpatialTopology(max_connections=self.limits.max_topology_size)
        for edge in snapshot.topology:
            self.topology.merge(edge)
        self.agents = {item.agent_id: item for item in snapshot.agents}
        self.step = snapshot.step
        self.scheduled_events = list(snapshot.scheduled_events)
        self.fired_event_ids = set(snapshot.fired_event_ids)
        self.forced_mismatch_action_types = set(snapshot.forced_mismatch_action_types)

    def _state_hash(self) -> str:
        return canonical_hash({"facts": [asdict(item) for item in sorted(self.facts, key=lambda x:x.semantic_id)], "topology": self.topology.to_dict(), "agents": [asdict(value) for _, value in sorted(self.agents.items())], "step": self.step})

    def observe(self) -> EnvironmentObservation:
        signed=project_signed_state(self.facts)
        derived_agents={}
        for agent_id,current in self.agents.items():
            location=next((item.object_id for item in signed.values() if item.subject_id==agent_id and item.predicate=="at" and item.status==SUPPORTED_TRUE),current.current_location_id)
            carried=tuple(sorted(item.object_id for item in signed.values() if item.subject_id==agent_id and item.predicate=="carries" and item.status==SUPPORTED_TRUE))
            owned=tuple(sorted(item.object_id for item in signed.values() if item.subject_id==agent_id and item.predicate=="owns" and item.status==SUPPORTED_TRUE))
            derived_agents[agent_id]=replace(current,current_location_id=location,carried_object_ids=carried,owned_object_ids=owned)
        self.agents=derived_agents
        state_hash = self._state_hash()
        return EnvironmentObservation("observation:" + canonical_hash({"state": state_hash, "step": self.step})[:20], tuple(sorted(self.facts, key=lambda item:item.semantic_id)), tuple(self.topology.connections[key] for key in sorted(self.topology.connections)), tuple(self.agents[key] for key in sorted(self.agents)), self.step, ("environment:snapshot",), state_hash)

    def inject_event(self, event: EnvironmentEvent) -> None:
        if len(self.scheduled_events) >= self.limits.max_environment_events:
            raise OverflowError("MAX_ENVIRONMENT_EVENTS")
        self.scheduled_events.append(event)
        self.scheduled_events.sort(key=lambda item:item.event_id)

    def _fire_events(self, trigger: str, value: str) -> tuple[dict[str, Any], ...]:
        receipts=[]
        for event in self.scheduled_events:
            if event.event_id in self.fired_event_ids or event.trigger != trigger or event.trigger_value != value:
                continue
            before=self._state_hash()
            if event.effects:
                self.facts=list(_apply_effects(self.facts,event.effects,event.event_id))
            if event.connection_id and event.connection_status:
                self.topology.set_status(event.connection_id,ConnectionStatus(event.connection_status),evidence_id=event.event_id,source_ids=event.source_ids,provenance_ids=event.provenance_ids)
            self.fired_event_ids.add(event.event_id)
            receipts.append({"event_id":event.event_id,"trigger":trigger,"pre_state_hash":before,"post_state_hash":self._state_hash(),"effects":[asdict(x) for x in event.effects],"source_ids":event.source_ids,"provenance_ids":event.provenance_ids,"actor_id":event.actor_id})
        return tuple(receipts)

    def execute(self, action: VerifiedAction) -> ExecutionResult:
        proposal=action.proposal
        before_receipts=self._fire_events("before_action",proposal.action_id)+self._fire_events("before_action_type",proposal.action_type)
        signed=project_signed_state(self.facts)
        failed=next((pre for pre in proposal.preconditions if signed.get(pre.proposition_id,SignedProposition(pre.proposition_id,pre.subject_id,pre.predicate,pre.object_id,UNKNOWN)).status!=pre.expected_status),None)
        if failed:
            observation=self.observe()
            return ExecutionResult("execution:"+canonical_hash({"action":proposal.action_id,"failed":failed.proposition_id,"state":observation.state_hash})[:20],proposal.action_id,False,(),observation,before_receipts,"PRECONDITION_LOST")
        if proposal.action_type=="move":
            allowed,_,reason=self.topology.traversable(proposal.source_location_id,proposal.destination_location_id,supported_conditions=signed)
            if not allowed:
                observation=self.observe();return ExecutionResult("execution:"+canonical_hash({"action":proposal.action_id,"route":reason,"state":observation.state_hash})[:20],proposal.action_id,False,(),observation,before_receipts,reason)
        observed=() if proposal.action_type in self.forced_mismatch_action_types else proposal.expected_effects
        if observed:
            self.facts=list(_apply_effects(self.facts,observed,"execution:"+proposal.action_id))
        self.step+=1
        after_receipts=self._fire_events("after_step",str(self.step))+self._fire_events("after_action_type",proposal.action_type)+self._fire_events("after_enter",proposal.destination_location_id if proposal.action_type=="move" else "")
        observation=self.observe()
        return ExecutionResult("execution:"+canonical_hash({"action":proposal.action_id,"step":self.step,"state":observation.state_hash})[:20],proposal.action_id,True,tuple(observed),observation,before_receipts+after_receipts)


class HabitatV3Verifier:
    ACTION_TYPES = frozenset({"move","take","put","give","open","close","lock","unlock","activate","deactivate"})

    def verify_observation(self, observation: EnvironmentObservation, *, limits: AgentLimits) -> dict[str, Any]:
        unique_facts=len({item.semantic_id for item in observation.facts})==len(observation.facts)
        unique_agents=len({item.agent_id for item in observation.agents})==len(observation.agents)
        valid=unique_facts and unique_agents and len(observation.facts)<=limits.max_semantic_memory_items and len(observation.topology)<=limits.max_topology_size and len(observation.agents)<=limits.max_agents
        payload={"observation_id":observation.observation_id,"approved":valid,"checks":{"unique_facts":unique_facts,"unique_agents":unique_agents,"bounded":valid},"source_ids":observation.source_ids}
        return {**payload,"verification_id":"observation_verification:"+canonical_hash(payload)[:20]}

    def verify_action(self, proposal: ActionProposal, world: TrustedWorld, goal: Goal) -> tuple[VerifiedAction|None,tuple[dict[str,Any],...],str]:
        checks=[];supports=set(proposal.support_ids)
        if proposal.action_type not in self.ACTION_TYPES:
            return None,(),"UNSUPPORTED_ACTION_TYPE"
        schema_ok,schema_reason=self._schema_valid(proposal)
        checks.append({"check_id":"action_schema_valid","passed":schema_ok,"reason":schema_reason,"support_ids":()})
        if not schema_ok:return None,tuple(checks),schema_reason
        if goal.status!=GoalStatus.ACTIVE:
            return None,(),"GOAL_CHANGED"
        for pre in proposal.preconditions:
            passed,ids,status=world.support_for(pre);supports.update(ids)
            checks.append({"proposition_id":pre.proposition_id,"expected":pre.expected_status,"observed":status,"passed":passed,"support_ids":ids})
        if proposal.action_type=="take":
            owner=next((item.subject_id for item in world.signed_state.values() if item.predicate=="owns" and item.object_id==proposal.object_id and item.status==SUPPORTED_TRUE and item.subject_id!=proposal.actor_id),"")
            if owner:
                permission=world.signed_state.get(proposition_key(owner,"allows_use",proposal.actor_id+"@"+proposal.object_id))
                allowed=bool(permission and permission.status==SUPPORTED_TRUE);ids=permission.positive_support_ids if permission else ()
                checks.append({"check_id":"ownership_permission","passed":allowed,"owner_id":owner,"support_ids":ids});supports.update(ids)
        if proposal.action_type=="move":
            allowed,edge,reason=world.topology.traversable(proposal.source_location_id,proposal.destination_location_id,supported_conditions=world.signed_state)
            checks.append({"check_id":"connection_traversable","passed":allowed,"reason":reason,"support_ids":tuple(edge.source_ids if edge else ())})
            if edge:supports.add(edge.connection_id);supports.update(edge.source_ids)
        if not checks or not all(item["passed"] for item in checks):
            return None,tuple(checks),"PRECONDITION_LOST"
        if not supports:
            return None,tuple(checks),"MISSING_SUPPORT"
        payload={"action":asdict(proposal),"state":world.hash,"goal":goal.goal_id,"checks":checks,"support":sorted(supports)}
        verified=VerifiedAction(proposal,"action_authorization:"+canonical_hash(payload)[:20],world.hash,tuple(checks),tuple(sorted(supports)))
        return verified,tuple(checks),"AUTHORIZED"

    def _schema_valid(self,proposal:ActionProposal)->tuple[bool,str]:
        effects={(x.subject_id,x.predicate,x.object_id,x.polarity) for x in proposal.expected_effects}
        required={
            "move":(proposal.source_location_id and proposal.destination_location_id,(proposal.actor_id,"at",proposal.destination_location_id,"positive")),
            "take":(proposal.object_id,(proposal.actor_id,"carries",proposal.object_id,"positive")),
            "put":(proposal.object_id and proposal.target_id,(proposal.object_id,"inside",proposal.target_id,"positive")),
            "give":(proposal.object_id and proposal.recipient_id,(proposal.recipient_id,"owns",proposal.object_id,"positive")),
            "open":(proposal.target_id,(proposal.target_id,"open","","positive")),
            "close":(proposal.target_id,(proposal.target_id,"open","","negative")),
            "lock":(proposal.target_id,(proposal.target_id,"locked","","positive")),
            "unlock":(proposal.target_id and proposal.object_id,(proposal.target_id,"locked","","negative")),
            "activate":(proposal.target_id,(proposal.target_id,"active","","positive")),
            "deactivate":(proposal.target_id,(proposal.target_id,"active","","negative")),
        }[proposal.action_type]
        return (True,"ACTION_SCHEMA_VERIFIED") if bool(required[0]) and required[1] in effects and proposal.cost>=1 else (False,"ACTION_SCHEMA_MISMATCH")

    def verify_effects(self, action: VerifiedAction, result: ExecutionResult) -> dict[str, Any]:
        expected=tuple(sorted((x.subject_id,x.predicate,x.object_id,x.polarity) for x in action.proposal.expected_effects))
        observed=tuple(sorted((x.subject_id,x.predicate,x.object_id,x.polarity) for x in result.observed_effects))
        approved=result.success and expected==observed
        payload={"action_id":action.proposal.action_id,"execution_id":result.execution_id,"expected":expected,"observed":observed,"approved":approved}
        return {**payload,"verification_id":"effect_verification:"+canonical_hash(payload)[:20],"reason":"EFFECTS_MATCH" if approved else "ACTION_EFFECT_MISMATCH"}

    def verify_plan(self, plan: VerifiedPlan, world: TrustedWorld, goal: Goal) -> tuple[bool,tuple[dict[str,Any],...],str]:
        simulation=world.clone();checks=[]
        if plan.originating_world_state_hash!=world.hash:
            return False,(),"WORLD_CHANGED"
        if plan.goal_id!=goal.goal_id or goal.status!=GoalStatus.ACTIVE:
            return False,(),"GOAL_CHANGED"
        for action in plan.actions:
            verified,action_checks,reason=self.verify_action(action,simulation,goal)
            checks.append({"action_id":action.action_id,"approved":verified is not None,"reason":reason,"checks":action_checks})
            if not verified:return False,tuple(checks),reason
            simulation.facts={item.semantic_id:item for item in _apply_effects(simulation.facts.values(),action.expected_effects,"plan:"+action.action_id)}
        return True,tuple(checks),"PLAN_VERIFIED"

    def approve_lesson(self, lesson: "ProceduralLesson", receipt_ids: set[str]) -> tuple[bool,str]:
        allowed_types={"REVALIDATE_PRECONDITION","CHECK_ROUTE_BEFORE_MOVE","VERIFY_EFFECT_IMMEDIATELY"}
        allowed_ops={"verify_immediately_before_execution","check_topology_before_execution","verify_observed_effects_before_commit"}
        if lesson.lesson_type not in allowed_types:return False,"LESSON_TYPE_NOT_ALLOWED"
        if lesson.recommended_policy.get("operation") not in allowed_ops:return False,"POLICY_OPERATION_NOT_ALLOWED"
        if not lesson.evidence_receipt_ids or not set(lesson.evidence_receipt_ids)<=receipt_ids:return False,"MISSING_RECEIPT_EVIDENCE"
        return True,"LESSON_SCHEMA_AND_AUTHORITY_VERIFIED"


def _fact_support(world:TrustedWorld,subject:str,predicate:str,object_id:str="",status:str=SUPPORTED_TRUE)->tuple[str,...]:
    observed=world.signed_state.get(proposition_key(subject,predicate,object_id))
    if not observed or observed.status!=status:return ()
    return observed.positive_support_ids if status==SUPPORTED_TRUE else observed.negative_support_ids


def _action(action_type:str,actor:str,index:int,*,target:str="",obj:str="",source:str="",destination:str="",recipient:str="",pre:Iterable[Precondition]=(),effects:Iterable[Effect]=(),support:Iterable[str]=())->ActionProposal:
    payload={"type":action_type,"actor":actor,"index":index,"target":target,"object":obj,"source":source,"destination":destination,"recipient":recipient}
    return ActionProposal("action:"+canonical_hash(payload)[:20],action_type,actor,target,obj,source,destination,recipient,tuple(pre),tuple(effects),tuple(sorted(set(support))),1)


class BoundedPlanner:
    def build(self, world:TrustedWorld,goal:Goal,*,cluster_hash:str,max_depth:int,max_states:int)->tuple[VerifiedPlan|None,str,int]:
        actor=goal.owner_agent_id;actions=[];explored=0;support=set(goal.source_ids)
        location=next((item.object_id for item in world.signed_state.values() if item.subject_id==actor and item.predicate=="at" and item.status==SUPPORTED_TRUE),"")
        carried={item.object_id for item in world.signed_state.values() if item.subject_id==actor and item.predicate=="carries" and item.status==SUPPORTED_TRUE}
        def add_route(current:str,dest:str)->str:
            nonlocal explored
            path,ids,count=world.topology.route(current,dest,supported_conditions=world.signed_state,max_depth=max_depth,max_states=max_states);explored+=count
            if not path:return ""
            support.update(ids)
            for a,b in zip(path,path[1:]):
                actor_support=_fact_support(world,actor,"at",a) or tuple(ids)
                actions.append(_action("move",actor,len(actions)+1,source=a,destination=b,pre=(Precondition(actor,"at",a),),effects=(Effect(actor,"at",b),Effect(actor,"at",a,"negative")),support=(*ids,*actor_support)))
            return dest
        if goal.predicate=="at":
            if not location or not add_route(location,goal.object_id):return None,"UNREACHABLE_ROUTE",explored
        elif goal.predicate=="open" and goal.desired_polarity=="negative":
            target_location=goal.subject_id
            if location!=target_location:
                location=add_route(location,target_location)
            if not location:return None,"UNREACHABLE_ROUTE",explored
            ids=_fact_support(world,goal.subject_id,"open")
            actions.append(_action("close",actor,len(actions)+1,target=goal.subject_id,pre=(Precondition(goal.subject_id,"open"),Precondition(actor,"at",target_location)),effects=(Effect(goal.subject_id,"open",polarity="negative"),),support=(*ids,*_fact_support(world,actor,"at",target_location))))
        elif goal.predicate=="open":
            target=goal.subject_id;locked=world.signed_state.get(proposition_key(target,"locked",""))
            if locked and locked.status==SUPPORTED_TRUE:
                compatibility=next((item for item in world.signed_state.values() if item.predicate=="unlocks" and item.object_id==target and item.status==SUPPORTED_TRUE),None)
                if not compatibility:return None,"MISSING_COMPATIBLE_KEY",explored
                key=compatibility.subject_id
                if key not in carried:
                    key_location=next((item.object_id for item in world.signed_state.values() if item.subject_id==key and item.predicate in {"at","inside"} and item.status==SUPPORTED_TRUE),"")
                    container_location=next((item.object_id for item in world.signed_state.values() if item.subject_id==key_location and item.predicate=="at" and item.status==SUPPORTED_TRUE),"")
                    key_location=container_location or key_location
                    if not key_location:return None,"MISSING_KEY_LOCATION",explored
                    if location!=key_location:location=add_route(location,key_location)
                    if not location:return None,"UNREACHABLE_KEY",explored
                    key_support=tuple(compatibility.positive_support_ids)+_fact_support(world,key,"at",key_location)
                    if not key_support:
                        key_support=tuple(compatibility.positive_support_ids)+tuple(item.positive_support_ids for item in world.signed_state.values() if item.subject_id==key and item.predicate=="inside" and item.status==SUPPORTED_TRUE)[0]
                    actions.append(_action("take",actor,len(actions)+1,obj=key,source=key_location,pre=(Precondition(actor,"at",key_location),Precondition(key,"at",key_location) if _fact_support(world,key,"at",key_location) else Precondition(key,"inside",next((x.object_id for x in world.signed_state.values() if x.subject_id==key and x.predicate=="inside" and x.status==SUPPORTED_TRUE),""))),effects=(Effect(actor,"carries",key),Effect(key,"at",key_location,"negative")),support=key_support))
                    carried.add(key)
                if location!=target:location=add_route(location,target)
                if not location:return None,"UNREACHABLE_TARGET",explored
                actions.append(_action("unlock",actor,len(actions)+1,target=target,obj=key,pre=(Precondition(target,"locked"),Precondition(actor,"carries",key)),effects=(Effect(target,"locked",polarity="negative"),),support=(*locked.positive_support_ids,*compatibility.positive_support_ids)))
            if location!=target:location=add_route(location,target)
            if not location:return None,"UNREACHABLE_TARGET",explored
            actions.append(_action("open",actor,len(actions)+1,target=target,pre=(Precondition(target,"locked",expected_status=SUPPORTED_FALSE),Precondition(actor,"at",target)),effects=(Effect(target,"open"),),support=(*_fact_support(world,target,"locked",status=SUPPORTED_FALSE),*_fact_support(world,actor,"at",target),*support)))
        elif goal.predicate=="active":
            action_type="activate" if goal.desired_polarity=="positive" else "deactivate"
            actions.append(_action(action_type,actor,1,target=goal.subject_id,effects=(Effect(goal.subject_id,"active",polarity=goal.desired_polarity),),support=goal.source_ids))
        else:return None,"UNSUPPORTED_GOAL_TYPE",explored
        if not actions or len(actions)>max_depth:return None,"PLANNING_DEPTH_EXHAUSTED",explored
        intermediate=[];sim=world.clone()
        for action in actions:
            sim.facts={item.semantic_id:item for item in _apply_effects(sim.facts.values(),action.expected_effects,"plan:"+action.action_id)};intermediate.append(sim.hash)
        payload={"world":world.hash,"cluster":cluster_hash,"goal":goal.goal_id,"actions":[asdict(x) for x in actions],"limits":{"depth":max_depth,"states":max_states}}
        plan_id="plan:"+canonical_hash(payload)[:20]
        plan=VerifiedPlan(plan_id,world.hash,cluster_hash,goal.goal_id,tuple(actions),tuple(sorted(set((*support,*(sid for action in actions for sid in action.support_ids))))),{"max_depth":max_depth,"max_states":max_states},tuple(intermediate),explored,"plan_verification:pending")
        return plan,"PLAN_PROPOSED",explored


@dataclass(frozen=True)
class ProceduralLesson:
    lesson_id:str;lesson_type:str;condition:dict[str,str];recommended_policy:dict[str,str]
    evidence_receipt_ids:tuple[str,...];status:str="PROPOSED"


@dataclass(frozen=True)
class Reflection:
    reflection_id:str;trigger_type:str;trigger_receipt_ids:tuple[str,...];goal_id:str
    summary_code:str;causal_factors:tuple[str,...];successful_decisions:tuple[str,...]
    failed_assumptions:tuple[str,...];proposed_lessons:tuple[str,...];source_ids:tuple[str,...];status:str="RECORDED"


class ReflectionEngine:
    def reflect(self,trigger:str,receipt_ids:Iterable[str],goal_id:str,*,cause:str="")->tuple[Reflection,tuple[ProceduralLesson,...]]:
        receipts=tuple(sorted(set(receipt_ids)));lesson_type="";operation="";summary=cause or trigger
        if trigger in {"STALE_PLAN","ACTION_FAILED","EXTERNAL_EVENT"}:
            lesson_type="REVALIDATE_PRECONDITION";operation="verify_immediately_before_execution";summary="PRECONDITION_CHANGED_AFTER_PLANNING"
        elif trigger=="EFFECT_MISMATCH":lesson_type="VERIFY_EFFECT_IMMEDIATELY";operation="verify_observed_effects_before_commit";summary="EXPECTED_EFFECT_NOT_OBSERVED"
        lessons=()
        if lesson_type:
            lid="lesson:"+canonical_hash({"type":lesson_type,"goal":goal_id,"receipts":receipts})[:20]
            lessons=(ProceduralLesson(lid,lesson_type,{"action_type":"*","required_predicate":"current_preconditions"},{"operation":operation},receipts),)
        rid="reflection:"+canonical_hash({"trigger":trigger,"goal":goal_id,"receipts":receipts,"summary":summary})[:20]
        reflection=Reflection(rid,trigger,receipts,goal_id,summary,(cause,) if cause else (),(),(cause,) if cause else (),tuple(x.lesson_id for x in lessons),receipts)
        return reflection,lessons


@dataclass
class AgentRun:
    run_id:str;initial_snapshot_hash:str;configuration:AgentLimits;repository_shas:dict[str,str]
    loop_steps:list[dict[str,Any]]=field(default_factory=list);action_transactions:list[dict[str,Any]]=field(default_factory=list)
    environment_events:list[dict[str,Any]]=field(default_factory=list);replanning:list[dict[str,Any]]=field(default_factory=list)
    reflections:list[Reflection]=field(default_factory=list);lessons:dict[str,ProceduralLesson]=field(default_factory=dict)
    plans:list[VerifiedPlan]=field(default_factory=list);selected_goal_id:str="";outcome:str="IDLE";final_replay_hash:str=""


class HabitatAgentLoop:
    def __init__(self,environment:EnvironmentAdapter,goals:GoalStore,*,limits:AgentLimits|None=None,repository_shas:Mapping[str,str]|None=None)->None:
        self.environment=environment;self.goals=goals;self.limits=limits or AgentLimits();self.repository_shas=dict(repository_shas or {})
        self.world=TrustedWorld(topology=SpatialTopology(max_connections=self.limits.max_topology_size));self.tension=TensionManager(max_records=self.limits.max_tension_records)
        self.verifier=HabitatV3Verifier();self.planner=BoundedPlanner();self.reflection_engine=ReflectionEngine();self.current_plan:VerifiedPlan|None=None;self.plan_index=0;self.stop_requested=False
        snapshot=environment.snapshot();initial_hash=canonical_hash(asdict(snapshot));self.run_receipts:set[str]=set()
        self.run=AgentRun("run:"+initial_hash[:20],initial_hash,self.limits,self.repository_shas)
        self.iterations=self.replans=self.actions_executed=self.plans_created=0;self.started=monotonic()

    def _step_receipt(self,phase:LoopPhase,decision:str,*,goal:Goal|None=None,action:ActionProposal|None=None,pre_hash:str="",post_hash:str="",support:Iterable[str]=())->dict[str,Any]:
        payload={"loop_step_id":f"loop:{len(self.run.loop_steps)+1:04d}","phase":phase.value,"selected_goal_id":goal.goal_id if goal else self.run.selected_goal_id,"selected_plan_id":self.current_plan.plan_id if self.current_plan else "","selected_action_id":action.action_id if action else "","pre_state_hash":pre_hash,"post_state_hash":post_hash,"tension_before":{"total":self.tension.total()},"tension_after":{"total":self.tension.total()},"decision":decision,"support_ids":tuple(sorted(set(support)))}
        payload["receipt_id"]="loop_receipt:"+canonical_hash(payload)[:20];self.run.loop_steps.append(payload);self.run_receipts.add(payload["receipt_id"]);return payload

    def _budget_reason(self)->str:
        if self.stop_requested:return "STOP_REQUESTED"
        if self.iterations>=self.limits.max_loop_iterations:return "MAX_LOOP_ITERATIONS"
        if self.actions_executed>=self.limits.max_action_executions:return "MAX_ACTION_EXECUTIONS"
        if self.replans>self.limits.max_replans:return "MAX_REPLANS"
        if monotonic()-self.started>=self.limits.max_wall_clock_duration:return "MAX_WALL_CLOCK_DURATION"
        return ""

    def stop(self)->None:self.stop_requested=True

    def step(self)->str:
        budget=self._budget_reason()
        if budget:
            self.run.outcome="BUDGET_EXHAUSTED" if budget!="STOP_REQUESTED" else "BLOCKED";self._step_receipt(LoopPhase.BUDGET_EXHAUSTED,budget);self._reflect("BUDGET_EXHAUSTED",budget);self._finish_replay();return self.run.outcome
        self.iterations+=1
        pre=self.world.hash;observation=self.environment.observe();self._step_receipt(LoopPhase.OBSERVE,"OBSERVED",pre_hash=pre,post_hash=pre,support=observation.source_ids)
        verification=self.verifier.verify_observation(observation,limits=self.limits)
        if not verification["approved"]:
            self.run.outcome="ERROR";self._step_receipt(LoopPhase.UPDATE_WORLD,"OBSERVATION_REJECTED");self._finish_replay();return self.run.outcome
        self.world.install_observation(observation,limits=self.limits);self._step_receipt(LoopPhase.UPDATE_WORLD,"VERIFIED_OBSERVATION_COMMITTED",pre_hash=pre,post_hash=self.world.hash,support=observation.source_ids)
        conflicts=self._detect_goal_conflicts()
        if conflicts:
            self._step_receipt(LoopPhase.EVALUATE_GOALS,"COMPETING_GOALS_CONFLICTED",support=conflicts)
        evaluations=self.goals.evaluate(self.world.signed_state,turn=self.iterations);self._step_receipt(LoopPhase.EVALUATE_GOALS,"GOALS_EVALUATED",support=(sid for item in evaluations for sid in item.support_ids))
        for goal in self.goals.goals.values():
            if goal.status==GoalStatus.ACTIVE:self.tension.update("unsatisfied_goal",goal.goal_id,step=self.iterations,targets=(goal.proposition_id,),resolution_condition=goal.proposition_id+" supported")
            elif goal.status in {GoalStatus.SATISFIED,GoalStatus.ABANDONED}:self.tension.update("unsatisfied_goal",goal.goal_id,step=self.iterations,resolved=True)
        tier=self.tension.compute_tier();self._step_receipt(LoopPhase.COMPUTE_TENSION,"COMPUTE_TIER_"+tier.name)
        scores=self.tension.goal_scores();scheduled=schedule_agents(self.goals,scores,self.world.agents.values())
        selected,selection=self.goals.select(scores,owner_agent_id=scheduled[0].agent_id if scheduled else None);self.run.selected_goal_id=selected.goal_id if selected else "";self._step_receipt(LoopPhase.SELECT_GOAL,"SELECTED" if selected else "NO_ACTIVE_GOAL",goal=selected)
        if not selected:
            active_terminal=[g for g in self.goals.goals.values() if g.status==GoalStatus.SATISFIED]
            self.run.outcome="COMPLETE" if active_terminal else "BLOCKED";self._step_receipt(LoopPhase.COMPLETE if active_terminal else LoopPhase.BLOCKED,self.run.outcome);self._finish_replay();return self.run.outcome
        cluster_ids=self._cluster(selected,tier.cluster_depth);cluster_hash=canonical_hash(cluster_ids);self._step_receipt(LoopPhase.ACTIVATE_CLUSTER,"CLUSTER_ACTIVATED",goal=selected,support=cluster_ids)
        if self.current_plan and (self.current_plan.goal_id!=selected.goal_id or self.current_plan.invalidated):self.current_plan=None;self.plan_index=0
        if self.current_plan and self.plan_index<len(self.current_plan.actions):
            cause=self._stale_cause(self.current_plan,self.current_plan.actions[self.plan_index],selected)
            if cause:self._invalidate(cause,selected)
        if self.current_plan is None:
            if self.plans_created>=self.limits.max_plans_per_goal:
                self.goals.transition(selected.goal_id,GoalStatus.BUDGET_EXHAUSTED,turn=self.iterations);self.run.outcome="BUDGET_EXHAUSTED";self._step_receipt(LoopPhase.BUDGET_EXHAUSTED,"MAX_PLANS_PER_GOAL",goal=selected);self._finish_replay();return self.run.outcome
            plan,reason,_=self.planner.build(self.world,selected,cluster_hash=cluster_hash,max_depth=min(tier.planning_depth,self.limits.max_planner_depth),max_states=min(tier.state_budget,self.limits.max_explored_states));self._step_receipt(LoopPhase.PLAN,reason,goal=selected)
            if plan is None:
                terminal=GoalStatus.UNREACHABLE if reason in {"MISSING_COMPATIBLE_KEY","UNREACHABLE_ROUTE","UNREACHABLE_KEY","UNREACHABLE_TARGET","MISSING_KEY_LOCATION","UNSUPPORTED_GOAL_TYPE"} else GoalStatus.BLOCKED
                self.goals.transition(selected.goal_id,terminal,turn=self.iterations);self.tension.update("unreachable_route",selected.goal_id,step=self.iterations,targets=(selected.proposition_id,));self.run.outcome=terminal.value;self._step_receipt(LoopPhase.UNREACHABLE if terminal==GoalStatus.UNREACHABLE else LoopPhase.BLOCKED,reason,goal=selected);self._reflect(terminal.value,reason);self._finish_replay();return self.run.outcome
            valid,checks,reason=self.verifier.verify_plan(plan,self.world,selected);self._step_receipt(LoopPhase.VERIFY_PLAN,reason,goal=selected,support=plan.support_ids)
            if not valid:
                self.run.outcome="BLOCKED";self.goals.transition(selected.goal_id,GoalStatus.BLOCKED,turn=self.iterations);self._finish_replay();return self.run.outcome
            plan=replace(plan,verification_id="plan_verification:"+canonical_hash(checks)[:20]);self.current_plan=plan;self.run.plans.append(plan);self.plans_created+=1;self.plan_index=0
        action=self.current_plan.actions[self.plan_index];self._step_receipt(LoopPhase.PROPOSE_ACTION,"ACTION_PROPOSED",goal=selected,action=action,support=action.support_ids)
        verified,checks,reason=self.verifier.verify_action(action,self.world,selected);self._step_receipt(LoopPhase.VERIFY_ACTION_PRECONDITIONS,reason,goal=selected,action=action,support=action.support_ids)
        if not verified:
            self._invalidate("PRECONDITION_LOST",selected);return "REPLAN"
        pre_hash=self.world.hash;result=self.environment.execute(verified);self.actions_executed+=1;self.run.environment_events.extend(result.environment_event_receipts);self._step_receipt(LoopPhase.EXECUTE_ACTION,"ENVIRONMENT_EXECUTED" if result.success else "ACTION_FAILED",goal=selected,action=action,pre_hash=pre_hash,post_hash=pre_hash)
        effect_verification=self.verifier.verify_effects(verified,result);transaction={"transaction_id":"transaction:"+canonical_hash({"action":action.action_id,"execution":result.execution_id,"pre":pre_hash})[:20],"action_id":action.action_id,"lifecycle":[ActionStage.ACTION_PROPOSED.value,ActionStage.PRECONDITIONS_VERIFIED.value,ActionStage.ACTION_AUTHORIZED.value,ActionStage.ENVIRONMENT_EXECUTED.value,ActionStage.EFFECTS_OBSERVED.value],"pre_state_hash":pre_hash,"expected_effects":[asdict(x) for x in action.expected_effects],"observed_effects":[asdict(x) for x in result.observed_effects],"effect_verification":effect_verification,"committed":False,"post_state_hash":pre_hash,"support_ids":verified.support_ids,"provenance_ids":result.observation.source_ids}
        if not effect_verification["approved"]:
            observed_verification=self.verifier.verify_observation(result.observation,limits=self.limits)
            if observed_verification["approved"]:
                # Commit only the independently observed environment state, never the expected effects.
                self.world.install_observation(result.observation,limits=self.limits)
            transaction["lifecycle"].extend([ActionStage.EFFECT_MISMATCH.value,ActionStage.REPLAN_REQUIRED.value]);self.run.action_transactions.append(transaction);self.tension.update("failed_action",action.action_id,step=self.iterations,targets=(selected.proposition_id,));self._step_receipt(LoopPhase.VERIFY_EFFECTS,"EFFECT_MISMATCH",goal=selected,action=action);self._reflect("EFFECT_MISMATCH","ACTION_EFFECT_MISMATCH")
            interference=any(row.get("actor_id") and row.get("actor_id")!=selected.owner_agent_id for row in result.environment_event_receipts)
            cause="AGENT_INTERFERENCE" if interference else "ACTION_EFFECT_MISMATCH"
            self._invalidate(cause,selected);return "REPLAN"
        observed_verification=self.verifier.verify_observation(result.observation,limits=self.limits)
        if not observed_verification["approved"]:
            transaction["lifecycle"].append(ActionStage.ACTION_FAILED.value);self.run.action_transactions.append(transaction);self.run.outcome="ERROR";self._finish_replay();return self.run.outcome
        self.world.install_observation(result.observation,limits=self.limits);transaction["lifecycle"].extend([ActionStage.EFFECTS_VERIFIED.value,ActionStage.WORLD_COMMITTED.value]);transaction["committed"]=True;transaction["post_state_hash"]=self.world.hash;self.run.action_transactions.append(transaction);self._step_receipt(LoopPhase.VERIFY_EFFECTS,"WORLD_COMMITTED",goal=selected,action=action,pre_hash=pre_hash,post_hash=self.world.hash,support=verified.support_ids)
        completed=(*self.current_plan.completed_action_ids,action.action_id);self.current_plan=replace(self.current_plan,completed_action_ids=completed);self.plan_index+=1;self.tension.update("failed_action",action.action_id,step=self.iterations,resolved=True)
        updates=self.goals.evaluate(self.world.signed_state,turn=self.iterations);selected=self.goals.goals[selected.goal_id];self._step_receipt(LoopPhase.UPDATE_GOAL,selected.status.value,goal=selected,support=(sid for item in updates for sid in item.support_ids))
        if selected.status==GoalStatus.SATISFIED:
            self._reflect("GOAL_SATISFIED","");self.current_plan=None;self.plan_index=0
        self._finish_replay();return selected.status.value if selected.status!=GoalStatus.ACTIVE else "CONTINUE"

    def run_bounded(self,max_steps:int|None=None)->str:
        limit=min(max_steps if max_steps is not None else self.limits.max_loop_iterations,self.limits.max_loop_iterations)
        for _ in range(limit):
            result=self.step()
            if result in {"COMPLETE","BLOCKED","UNREACHABLE","BUDGET_EXHAUSTED","ERROR"}:break
        else:
            if self.run.outcome not in {"COMPLETE","BLOCKED","UNREACHABLE","ERROR"}:
                self.run.outcome="BUDGET_EXHAUSTED";self._step_receipt(LoopPhase.BUDGET_EXHAUSTED,"RUN_STEP_BUDGET");self._reflect("BUDGET_EXHAUSTED","RUN_STEP_BUDGET")
        self._finish_replay();return self.run.outcome

    def _cluster(self,goal:Goal,depth:int)->tuple[str,...]:
        seeds={goal.subject_id,goal.object_id,goal.owner_agent_id};items=[]
        for fact in sorted(self.world.facts.values(),key=lambda x:x.semantic_id):
            if {fact.subject_id,fact.object_id}&seeds:items.append(fact.semantic_id);seeds.update((fact.subject_id,fact.object_id))
            if len(items)>=self.limits.max_active_cluster_items:break
        for edge in sorted(self.world.topology.connections.values(),key=lambda x:x.connection_id):
            if {edge.source_location_id,edge.destination_location_id}&seeds:items.append(edge.connection_id)
            if len(items)>=self.limits.max_active_cluster_items:break
        return tuple(sorted(set(items)))

    def _detect_goal_conflicts(self)->tuple[str,...]:
        groups={};receipts=[]
        for goal in self.goals.goals.values():
            if goal.status==GoalStatus.ACTIVE:groups.setdefault(goal.proposition_id,[]).append(goal)
        for goals in groups.values():
            if {goal.desired_polarity for goal in goals}!={"positive","negative"}:continue
            for goal in sorted(goals,key=lambda item:item.goal_id):
                verification=self.goals.transition(goal.goal_id,GoalStatus.CONFLICTED,turn=self.iterations,support_ids=tuple(other.goal_id for other in goals if other.goal_id!=goal.goal_id));receipts.append(verification.verification_id);self.tension.update("competing_goal",goal.goal_id,step=self.iterations,targets=(goal.proposition_id,))
        return tuple(receipts)

    def _stale_cause(self,plan:VerifiedPlan,action:ActionProposal,goal:Goal)->str:
        if goal.status!=GoalStatus.ACTIVE:return "GOAL_CHANGED"
        for pre in action.preconditions:
            passed,_,status=self.world.support_for(pre)
            if not passed:return "CONFLICT_INTRODUCED" if status==CONFLICTED else "OBJECT_MOVED" if pre.predicate in {"at","inside"} and pre.subject_id!=action.actor_id else "OWNERSHIP_CHANGED" if pre.predicate=="owns" else "PRECONDITION_LOST"
        if action.action_type=="move" and not self.world.topology.traversable(action.source_location_id,action.destination_location_id,supported_conditions=self.world.signed_state)[0]:return "ROUTE_BLOCKED"
        return ""

    def _invalidate(self,cause:str,goal:Goal)->None:
        if cause not in STALE_CAUSES:cause="WORLD_CHANGED"
        if self.current_plan:self.current_plan=replace(self.current_plan,invalidated=True,stale_cause=cause)
        self.run.replanning.append({"replan_id":f"replan:{len(self.run.replanning)+1:04d}","goal_id":goal.goal_id,"invalidated_plan_id":self.current_plan.plan_id if self.current_plan else "","cause":cause,"completed_action_ids":self.current_plan.completed_action_ids if self.current_plan else (),"world_state_hash":self.world.hash})
        self.replans+=1;self.tension.update("stale_plan",goal.goal_id,step=self.iterations,targets=(goal.proposition_id,));self._step_receipt(LoopPhase.REPLAN,cause,goal=goal);self._reflect("STALE_PLAN",cause);self.current_plan=None;self.plan_index=0

    def _reflect(self,trigger:str,cause:str)->None:
        receipts=tuple(sorted(self.run_receipts))[-4:];reflection,lessons=self.reflection_engine.reflect(trigger,receipts,self.run.selected_goal_id,cause=cause);self.run.reflections.append(reflection)
        for lesson in lessons:self.run.lessons.setdefault(lesson.lesson_id,lesson)
        self._step_receipt(LoopPhase.REFLECT,reflection.summary_code)

    def approve_lesson(self,lesson_id:str)->dict[str,Any]:
        lesson=self.run.lessons[lesson_id];approved,reason=self.verifier.approve_lesson(lesson,self.run_receipts)
        if approved:self.run.lessons[lesson_id]=replace(lesson,status="APPROVED")
        receipt={"receipt_id":"lesson_approval:"+canonical_hash({"lesson":lesson_id,"approved":approved,"reason":reason})[:20],"lesson_id":lesson_id,"approved":approved,"reason":reason,"status":self.run.lessons[lesson_id].status};self.run_receipts.add(receipt["receipt_id"]);return receipt

    def reject_lesson(self,lesson_id:str)->dict[str,Any]:
        lesson=self.run.lessons[lesson_id];self.run.lessons[lesson_id]=replace(lesson,status="REJECTED");receipt={"receipt_id":"lesson_rejection:"+canonical_hash(lesson_id)[:20],"lesson_id":lesson_id,"approved":False,"reason":"EXPLICIT_REJECTION","status":"REJECTED"};self.run_receipts.add(receipt["receipt_id"]);return receipt

    def _finish_replay(self)->None:
        payload={"initial_snapshot_hash":self.run.initial_snapshot_hash,"repository_shas":self.repository_shas,"configuration":asdict(self.limits),"loop_steps":self.run.loop_steps,"transactions":self.run.action_transactions,"events":self.run.environment_events,"replanning":self.run.replanning,"reflections":[asdict(x) for x in self.run.reflections],"lessons":[asdict(self.run.lessons[x]) for x in sorted(self.run.lessons)],"outcome":self.run.outcome,"world_hash":self.world.hash}
        self.run.final_replay_hash=canonical_hash(payload)


def schedule_agents(goals:GoalStore,tensions:Mapping[str,float],agents:Iterable[AgentState])->tuple[AgentState,...]:
    rows=[]
    for agent in agents:
        goal,_=goals.select(tensions,owner_agent_id=agent.agent_id);priority=goal.priority if goal else -1;tension=tensions.get(goal.goal_id,0.0) if goal else 0.0;rows.append((agent,priority,tension))
    return tuple(row[0] for row in sorted(rows,key=lambda row:(-row[1],-row[2],row[0].agent_id)))
