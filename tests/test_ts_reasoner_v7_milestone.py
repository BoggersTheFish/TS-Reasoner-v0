import json
import tempfile
import unittest
from pathlib import Path

from ts_chat.v7_milestone import (
    CAPABILITY_LADDER,
    evaluate_v7_milestone,
    v7_milestone_report_valid,
)


class TestTSReasonerV7Milestone(unittest.TestCase):
    def test_capability_ladder(self):
        self.assertEqual(len(CAPABILITY_LADDER), 9)
        self.assertEqual(CAPABILITY_LADDER[0]["release"], "v6.1.0")
        self.assertEqual(CAPABILITY_LADDER[-1]["release"], "v6.9.0")

    def test_v7_milestone_report_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = evaluate_v7_milestone(Path(tmp), stress_cycles=8)

            self.assertEqual(report["schema"], "ts_reasoner_v7_milestone_report_v1")
            self.assertEqual(report["release"], "v7.0.0")
            self.assertEqual(report["milestone"], "Self-Improving Verifier-First Chat System")
            self.assertFalse(report["external_llm_used"])
            self.assertEqual(report["capability_count"], 9)

            self.assertEqual(report["arena"]["case_count"], 10)
            self.assertEqual(report["arena"]["passed_count"], 10)
            self.assertEqual(report["arena"]["failed_count"], 0)
            self.assertTrue(report["arena"]["valid"])

            self.assertEqual(report["stress"]["cycles"], 8)
            self.assertEqual(report["stress"]["passed_cycles"], 8)
            self.assertEqual(report["stress"]["failed_cycles"], 0)
            self.assertTrue(report["stress"]["valid"])

            self.assertEqual(report["combined"]["total_checks"], 18)
            self.assertEqual(report["combined"]["total_failed"], 0)
            self.assertEqual(report["combined"]["combined_pass_rate"], 1.0)
            self.assertTrue(report["combined"]["zero_wrong_accepts"])
            self.assertTrue(report["combined"]["zero_candidate_graph_contamination"])
            self.assertTrue(report["combined"]["proof_boundary_preserved"])

            self.assertTrue(report["claim"]["self_improving_loop_present"])
            self.assertTrue(report["claim"]["persistent_memory_present"])
            self.assertTrue(report["claim"]["repair_memory_present"])
            self.assertTrue(report["claim"]["explanation_traces_present"])
            self.assertTrue(report["claim"]["contradiction_handling_present"])
            self.assertTrue(report["claim"]["belief_revision_candidates_present"])
            self.assertTrue(report["claim"]["provenance_present"])
            self.assertTrue(report["claim"]["knowledge_packs_present"])
            self.assertTrue(report["claim"]["session_arena_present"])
            self.assertTrue(report["claim"]["long_run_stress_present"])

            self.assertTrue(report["all_gates_passed"])
            self.assertTrue(v7_milestone_report_valid(report))

    def test_v7_report_invalid_if_contaminated(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = evaluate_v7_milestone(Path(tmp), stress_cycles=3)
            report["combined"]["zero_candidate_graph_contamination"] = False

            self.assertFalse(v7_milestone_report_valid(report))

    def test_v7_manifest_exists(self):
        path = Path("data/ts_reasoner_v7_milestone_manifest.jsonl")
        self.assertTrue(path.exists())

        rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        self.assertEqual(len(rows), 10)
        self.assertEqual(rows[-1]["release"], "v7.0.0")


if __name__ == "__main__":
    unittest.main()
