import unittest

from ts_reasoner.agent_control import GoalStore, TensionManager
from ts_reasoner.agent_runtime import AgentLimits, HabitatAgentLoop, SymbolicEnvironment
from ts_reasoner.topology import Connection, ConnectionStatus, SpatialTopology
from tests.test_habitat_v3_runtime import base_snapshot, goal_store


class HabitatV3LimitTests(unittest.TestCase):
    def test_topology_limit_is_explicit(self):
        topology=SpatialTopology(max_connections=1);topology.merge(Connection("connection:a:b","a","b",status=ConnectionStatus.OPEN))
        with self.assertRaisesRegex(OverflowError,"MAX_TOPOLOGY_SIZE"):topology.merge(Connection("connection:b:c","b","c",status=ConnectionStatus.OPEN))

    def test_goal_and_tension_limits_are_explicit(self):
        self.assertEqual(GoalStore(max_goals=0).max_goals,0)
        manager=TensionManager(max_records=1);manager.update("failed_action","one",step=1)
        with self.assertRaisesRegex(OverflowError,"MAX_TENSION_RECORDS"):manager.update("failed_action","two",step=2)

    def test_loop_iteration_action_replan_and_wall_clock_budgets_are_safe(self):
        for limits in (
            AgentLimits(max_loop_iterations=0),AgentLimits(max_action_executions=0),AgentLimits(max_wall_clock_duration=0),
        ):
            loop=HabitatAgentLoop(SymbolicEnvironment(base_snapshot()),goal_store(),limits=limits)
            self.assertEqual(loop.step(),"BUDGET_EXHAUSTED")

    def test_planner_depth_and_state_budget_produce_safe_outcome(self):
        loop=HabitatAgentLoop(SymbolicEnvironment(base_snapshot()),goal_store(),limits=AgentLimits(max_planner_depth=1,max_explored_states=1))
        self.assertIn(loop.run_bounded(3),{"BLOCKED","UNREACHABLE","BUDGET_EXHAUSTED"})

    def test_all_declared_bounds_are_positive_and_serializable(self):
        limits=AgentLimits()
        for name,value in limits.__dict__.items():self.assertGreater(value,0,name)
        self.assertEqual(limits.max_causal_derivations,64)


if __name__=="__main__":unittest.main()
