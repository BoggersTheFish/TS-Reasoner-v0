import tempfile
import unittest
from pathlib import Path

from ts_reasoner.branching_worlds import (
    BranchingWorldManager,
    accepted_premise_edges,
    branching_worlds_state_valid,
    rejected_relations,
    run_branching_worlds_demo,
)


class TestTSReasonerV73BranchingWorlds(unittest.TestCase):
    def test_fork_preserves_common_ground(self):
        manager = BranchingWorldManager()
        manager.process("all cats are animals")
        manager.process("all animals are mortal")

        manager.fork("alt")

        self.assertIn("alt", manager.branch_names())
        self.assertEqual(
            accepted_premise_edges(manager.branches["main"]),
            accepted_premise_edges(manager.branches["alt"]),
        )

    def test_compare_branches(self):
        manager = BranchingWorldManager()
        manager.process("all cats are animals")
        manager.fork("machines")
        manager.process("all cats are machines", branch="machines")

        compare = manager.compare("main", "machines")

        self.assertEqual(compare["schema"], "ts_reasoner_branch_compare_v1")
        self.assertEqual(len(compare["shared_edges"]), 1)
        self.assertEqual(len(compare["only_right_edges"]), 1)
        self.assertEqual(compare["candidate_graph_contamination_count"], 0)

    def test_unsafe_merge_blocked_for_direct_rejected_edge(self):
        manager = BranchingWorldManager()
        manager.process("all cats are animals")
        manager.process("also say all cats are robots")
        manager.fork("direct_robots")
        manager.process("all cats are robots", branch="direct_robots")

        merge = manager.merge_if_consistent("direct_robots", target="main")

        self.assertTrue(merge["blocked"])
        self.assertFalse(merge["merged"])
        self.assertEqual(merge["candidate_graph_contamination_count"], 0)

    def test_safe_merge_resolves_repair_path(self):
        manager = BranchingWorldManager()
        manager.process("all cats are animals")
        manager.process("also say all cats are robots")
        manager.fork("machine_bridge")
        manager.process("all cats are machines", branch="machine_bridge")
        manager.process("all machines are robots", branch="machine_bridge")

        merge = manager.merge_if_consistent("machine_bridge", target="main")
        question = manager.process("are all cats robots?", branch="main")

        self.assertTrue(merge["merged"])
        self.assertFalse(merge["blocked"])
        self.assertGreaterEqual(merge["merged_edge_count"], 2)
        self.assertTrue(any(
            record.get("kind") == "question" and record.get("status") == "accepted"
            for record in question["records_created"]
        ))

    def test_rejected_relations_tracked(self):
        manager = BranchingWorldManager()
        manager.process("also say all cats are robots")

        self.assertIn(("cats", "robots"), rejected_relations(manager.branches["main"]))

    def test_state_valid(self):
        manager = BranchingWorldManager()
        manager.process("all cats are animals")
        manager.fork("alt")
        state = manager.to_dict()

        self.assertTrue(branching_worlds_state_valid(state))

    def test_demo_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = run_branching_worlds_demo(Path(tmp))

            self.assertTrue(receipt["all_gates_passed"])
            self.assertEqual(receipt["candidate_graph_contamination_count"], 0)
            self.assertTrue(receipt["unsafe_merge"]["blocked"])
            self.assertTrue(receipt["safe_merge"]["merged"])
            self.assertTrue(Path(receipt["state_path"]).exists())
            self.assertTrue(Path(receipt["report_path"]).exists())


if __name__ == "__main__":
    unittest.main()
