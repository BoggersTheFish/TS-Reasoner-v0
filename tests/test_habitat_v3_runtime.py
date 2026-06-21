import unittest

from ts_reasoner.agent_control import Goal, GoalStatus, GoalStore, goal_id
from ts_reasoner.agent_runtime import (
    ActionProposal, AgentLimits, AgentState, Effect, EnvironmentEvent, EnvironmentSnapshot,
    HabitatAgentLoop, HabitatV3Verifier, Precondition, SymbolicEnvironment, TrustedWorld, schedule_agents,
)
from ts_reasoner.habitat import WorldFact
from ts_reasoner.topology import Connection, ConnectionEvidence, ConnectionStatus, connection_id


def fact(identity, subject, predicate, object_id="", polarity="positive"):
    return WorldFact(identity, subject, predicate, object_id, polarity, (identity,), "fixture", True)


def edge(a, b, identity):
    cid = connection_id(a, b)
    return Connection(cid, a, b, status=ConnectionStatus.OPEN, source_ids=(identity,), evidence=(ConnectionEvidence(identity, ConnectionStatus.OPEN, (identity,)),))


def goal_store(subject="north_door", predicate="open", object_id="", priority=100, owner="alice"):
    store = GoalStore()
    identity = goal_id(owner, predicate, subject, object_id)
    goal = Goal(identity, owner, "state_goal", predicate, subject, object_id, status=GoalStatus.PROPOSED, priority=priority, created_turn=1, updated_turn=1, source_ids=("goal_source",))
    store.propose(goal); store.transition(identity, GoalStatus.ACTIVE, turn=1)
    return store


def base_snapshot(*, mismatch=(), events=()):
    facts = (
        fact("alice_hall", "alice", "at", "hall"),
        fact("box_kitchen", "box", "at", "kitchen"),
        fact("key_box", "red_key", "inside", "box"),
        fact("door_locked", "north_door", "locked"),
        fact("key_unlocks", "red_key", "unlocks", "north_door"),
    )
    topology = (edge("hall", "kitchen", "hk"), edge("kitchen", "north_door", "kd"))
    agents = (AgentState("alice", "Alice", "hall"), AgentState("bob", "Bob", "kitchen"))
    return EnvironmentSnapshot(facts, topology, agents, 0, tuple(events), (), tuple(mismatch))


class HabitatV3RuntimeTests(unittest.TestCase):
    def test_complete_verified_action_cycle(self):
        loop = HabitatAgentLoop(SymbolicEnvironment(base_snapshot()), goal_store(), limits=AgentLimits(max_loop_iterations=20))
        self.assertEqual(loop.run_bounded(20), "COMPLETE")
        self.assertEqual(len(loop.run.action_transactions), 5)
        self.assertTrue(all(row["committed"] for row in loop.run.action_transactions))
        self.assertTrue(all("WORLD_COMMITTED" in row["lifecycle"] for row in loop.run.action_transactions))
        self.assertEqual(next(iter(loop.goals.goals.values())).status, GoalStatus.SATISFIED)

    def test_effect_mismatch_does_not_commit_expected_effect(self):
        loop = HabitatAgentLoop(SymbolicEnvironment(base_snapshot(mismatch=("take",))), goal_store(), limits=AgentLimits(max_loop_iterations=6, max_replans=1))
        loop.run_bounded(6)
        mismatch = next(row for row in loop.run.action_transactions if not row["committed"])
        self.assertEqual(mismatch["effect_verification"]["reason"], "ACTION_EFFECT_MISMATCH")
        self.assertEqual(mismatch["post_state_hash"], mismatch["pre_state_hash"])

    def test_exogenous_object_movement_invalidates_plan(self):
        event = EnvironmentEvent("event:bob_takes_key", "before_action_type", "take", (
            Effect("red_key", "inside", "box", "negative"), Effect("bob", "carries", "red_key"),
        ), source_ids=("event_source",), provenance_ids=("event_prov",), actor_id="bob")
        loop = HabitatAgentLoop(SymbolicEnvironment(base_snapshot(events=(event,))), goal_store(), limits=AgentLimits(max_loop_iterations=8, max_replans=2))
        loop.run_bounded(8)
        self.assertTrue(loop.run.environment_events)
        self.assertTrue(loop.run.replanning)
        self.assertFalse(any(row["committed"] and row["action_id"] == loop.run.plans[0].actions[1].action_id for row in loop.run.action_transactions))

    def test_blocked_connection_is_never_executed(self):
        snapshot = base_snapshot()
        blocked = Connection(connection_id("hall", "kitchen"), "hall", "kitchen", status=ConnectionStatus.BLOCKED, source_ids=("blocked",), evidence=(ConnectionEvidence("blocked", ConnectionStatus.BLOCKED, ("blocked",)),))
        snapshot = EnvironmentSnapshot(snapshot.facts, (blocked, snapshot.topology[1]), snapshot.agents, 0, (), ())
        loop = HabitatAgentLoop(SymbolicEnvironment(snapshot), goal_store())
        self.assertEqual(loop.run_bounded(4), "UNREACHABLE")
        self.assertEqual(loop.actions_executed, 0)

    def test_multi_agent_schedule_is_deterministic(self):
        stores = GoalStore()
        for owner, priority in (("bob", 100), ("alice", 100)):
            goal = Goal(goal_id(owner, "open", "door"), owner, "state_goal", "open", "door", status=GoalStatus.PROPOSED, priority=priority, created_turn=1, updated_turn=1, source_ids=(owner,))
            stores.propose(goal); stores.transition(goal.goal_id, GoalStatus.ACTIVE, turn=1)
        agents = (AgentState("bob", "Bob"), AgentState("alice", "Alice"))
        self.assertEqual([x.agent_id for x in schedule_agents(stores, {}, agents)], ["alice", "bob"])

    def test_competing_goals_are_preserved_and_conflicted(self):
        stores=GoalStore()
        for owner,polarity in (("alice","negative"),("bob","positive")):
            goal=Goal(goal_id(owner,"open","north_door",polarity=polarity),owner,"state_goal","open","north_door",desired_polarity=polarity,status=GoalStatus.PROPOSED,created_turn=1,updated_turn=1,source_ids=(owner,))
            stores.propose(goal);stores.transition(goal.goal_id,GoalStatus.ACTIVE,turn=1)
        loop=HabitatAgentLoop(SymbolicEnvironment(base_snapshot()),stores)
        self.assertEqual(loop.run_bounded(2),"BLOCKED")
        self.assertTrue(all(goal.status==GoalStatus.CONFLICTED for goal in stores.goals.values()))

    def test_unauthorized_take_is_rejected(self):
        snapshot=base_snapshot();snapshot=EnvironmentSnapshot((*snapshot.facts,fact("owned","alice","owns","red_key")),snapshot.topology,snapshot.agents,0,(),())
        env=SymbolicEnvironment(snapshot);world=TrustedWorld();world.install_observation(env.observe(),limits=AgentLimits())
        stores=goal_store(owner="bob");goal=next(iter(stores.goals.values()))
        proposal=ActionProposal("take","take","bob",object_id="red_key",source_location_id="kitchen",preconditions=(Precondition("bob","at","kitchen"),Precondition("red_key","inside","box")),expected_effects=(Effect("bob","carries","red_key"),),support_ids=("owned",))
        verified,checks,reason=HabitatV3Verifier().verify_action(proposal,world,goal)
        self.assertIsNone(verified)
        self.assertTrue(any(row.get("check_id")=="ownership_permission" and not row["passed"] for row in checks))

    def test_lessons_are_inert_until_verified_approval(self):
        loop = HabitatAgentLoop(SymbolicEnvironment(base_snapshot(mismatch=("take",))), goal_store(), limits=AgentLimits(max_loop_iterations=4))
        loop.run_bounded(4)
        lesson = next(iter(loop.run.lessons.values()))
        self.assertEqual(lesson.status, "PROPOSED")
        receipt = loop.approve_lesson(lesson.lesson_id)
        self.assertTrue(receipt["approved"])
        self.assertEqual(loop.run.lessons[lesson.lesson_id].status, "APPROVED")

    def test_replay_hash_is_deterministic(self):
        def run():
            loop = HabitatAgentLoop(SymbolicEnvironment(base_snapshot()), goal_store(), limits=AgentLimits(max_loop_iterations=20), repository_shas={"reasoner": "sha", "tslc": "sha"})
            loop.run_bounded(20)
            return loop.run.final_replay_hash
        self.assertEqual(run(), run())


if __name__ == "__main__":
    unittest.main()
