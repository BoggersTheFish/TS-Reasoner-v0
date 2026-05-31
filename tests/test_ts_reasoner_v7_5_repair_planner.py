import tempfile
import unittest
from pathlib import Path

from ts_reasoner.repair_planner import generate_repair_plans, repair_plan_bundle_valid, render_repair_plan_bundle
from ts_reasoner.repair_planner_demo import run_repair_planner_demo
from ts_reasoner.ts_chat import TSChatSession


class TestTSReasonerV75RepairPlanner(unittest.TestCase):
    def test_missing_support_plans(self):
        session = TSChatSession()
        session.process("all cats are animals")
        session.process("also say all cats are robots")

        bundle = generate_repair_plans(session.common_ground, "repair_0001")

        self.assertTrue(repair_plan_bundle_valid(bundle))
        self.assertEqual(bundle["repair_kind"], "missing_support")
        self.assertTrue(any(plan["strategy"] == "direct_support" for plan in bundle["plans"]))
        self.assertTrue(any(plan["strategy"] == "bridge_support" for plan in bundle["plans"]))
        self.assertTrue(any(plan["strategy"] == "keep_open" for plan in bundle["plans"]))
        self.assertEqual(bundle["candidate_graph_contamination_count"], 0)

    def test_contradiction_plans(self):
        session = TSChatSession()
        session.process("all cats are animals")
        session.process("all animals are mortal")
        session.process("no cats are mortal")

        bundle = generate_repair_plans(session.common_ground, "repair_0001")

        self.assertTrue(repair_plan_bundle_valid(bundle))
        self.assertEqual(bundle["repair_kind"], "contradiction")
        self.assertTrue(any(plan["strategy"] == "keep_negative_rejected" for plan in bundle["plans"]))
        self.assertTrue(any(plan["strategy"] == "dispute_support_premise" for plan in bundle["plans"]))
        self.assertTrue(any(plan["strategy"] == "split_or_refine" for plan in bundle["plans"]))
        self.assertEqual(bundle["candidate_graph_contamination_count"], 0)

    def test_render_repair_plan_bundle(self):
        session = TSChatSession()
        session.process("also say all cats are robots")
        bundle = generate_repair_plans(session.common_ground, "repair_0001")
        rendered = render_repair_plan_bundle(bundle)

        self.assertIn("Repair plans for repair_0001", rendered)
        self.assertIn("Boundary: repair plans are candidates, not proof.", rendered)

    def test_chat_plan_command(self):
        session = TSChatSession()
        session.process("also say all cats are robots")
        receipt = session.process("/plan repair_0001")

        self.assertIn("Repair plans for repair_0001", receipt.response)
        self.assertIn("repair plans are candidates, not proof", receipt.response)

    def test_unknown_repair_plan(self):
        session = TSChatSession()
        receipt = session.process("/plan repair_9999")

        self.assertIn("No repair target found", receipt.response)

    def test_demo_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = run_repair_planner_demo(Path(tmp))

            self.assertTrue(receipt["all_gates_passed"])
            self.assertGreaterEqual(receipt["missing_support_plan_count"], 3)
            self.assertGreaterEqual(receipt["contradiction_plan_count"], 3)
            self.assertEqual(receipt["candidate_graph_contamination_count"], 0)


if __name__ == "__main__":
    unittest.main()
