import unittest

from ts_reasoner.agent_control import Goal, GoalStatus, GoalStore, TensionManager, goal_id
from ts_reasoner.habitat import SignedProposition, SUPPORTED_TRUE


class HabitatV3AgentControlTests(unittest.TestCase):
    def make_goal(self, owner="alice", subject="door", predicate="open", priority=100, turn=1):
        identity = goal_id(owner, predicate, subject)
        return Goal(identity, owner, "state_goal", predicate, subject, status=GoalStatus.PROPOSED, priority=priority, created_turn=turn, updated_turn=turn, source_ids=("source",))

    def test_goal_satisfaction_requires_signed_support(self):
        store = GoalStore()
        goal = self.make_goal()
        self.assertTrue(store.propose(goal).approved)
        self.assertTrue(store.transition(goal.goal_id, GoalStatus.ACTIVE, turn=1).approved)
        self.assertFalse(store.transition(goal.goal_id, GoalStatus.SATISFIED, turn=2, signed_state={}).approved)
        signed = {goal.proposition_id: SignedProposition(goal.proposition_id, "door", "open", "", SUPPORTED_TRUE, ("fact",), ())}
        result = store.transition(goal.goal_id, GoalStatus.SATISFIED, turn=2, signed_state=signed)
        self.assertTrue(result.approved)
        self.assertEqual(result.support_ids, ("fact",))

    def test_selection_is_priority_tension_creation_id_order(self):
        store = GoalStore()
        low = self.make_goal(subject="alarm", priority=10, turn=1)
        high = self.make_goal(subject="door", priority=20, turn=2)
        for item in (low, high):
            store.propose(item); store.transition(item.goal_id, GoalStatus.ACTIVE, turn=2)
        selected, evidence = store.select({low.goal_id: 1.0, high.goal_id: 0.1})
        self.assertEqual(selected.goal_id, high.goal_id)
        self.assertEqual(evidence[0]["rank"], 1)

    def test_tension_propagation_is_bounded_cycle_safe_and_not_evidence(self):
        manager = TensionManager(max_depth=2, decay=0.5)
        record = manager.update("unsatisfied_goal", "goal:g", step=1, targets=("a",), graph={"a": ("b",), "b": ("a", "c"), "c": ("b",)})
        self.assertEqual(record.raw_value, 0.5)
        self.assertLessEqual(record.total_value, 1.0)
        self.assertTrue(all(row["depth"] <= 2 for row in record.propagation_receipts))
        self.assertEqual(record.source_ids, ())

    def test_relaxation_preserves_history(self):
        manager = TensionManager()
        manager.update("failed_action", "action:1", step=1)
        relaxed = manager.update("failed_action", "action:1", step=2, resolved=True)
        self.assertEqual(relaxed.total_value, 0.0)
        self.assertEqual(len(manager.history), 1)

    def test_compute_tiers(self):
        manager = TensionManager()
        self.assertEqual(manager.compute_tier().name, "LOW")
        manager.update("unsatisfied_goal", "goal:g", step=1)
        self.assertEqual(manager.compute_tier().name, "MEDIUM")
        manager.update("failed_action", "action:a", step=2)
        self.assertEqual(manager.compute_tier().name, "HIGH")


if __name__ == "__main__":
    unittest.main()
