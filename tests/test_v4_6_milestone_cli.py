import subprocess
import sys
import unittest

from ts_reasoner.milestone import load_milestone_receipt, milestone_summary


class TestV46MilestoneCli(unittest.TestCase):
    def test_milestone_receipt_loads(self):
        data = load_milestone_receipt()

        self.assertEqual(data["version"], "v4.5-milestone-receipt-pack")
        self.assertEqual(data["input_report_count"], 8)
        self.assertEqual(data["total_known_cases"], 114)
        self.assertEqual(data["total_known_candidates"], 151)
        self.assertEqual(data["wrong_accept_total"], 0)
        self.assertEqual(data["accepted_without_typed_support_total"], 0)
        self.assertEqual(data["candidate_graph_contamination_total"], 0)
        self.assertTrue(data["gates"]["all_gates_passed"])

    def test_milestone_summary_contains_public_boundary(self):
        summary = milestone_summary(load_milestone_receipt())

        self.assertIn("confidence is not proof: True", summary)
        self.assertIn("generated text is not proof: True", summary)
        self.assertIn("typed verifier is proof authority: True", summary)
        self.assertIn("all gates passed: True", summary)

    def test_module_cli_prints_receipt(self):
        result = subprocess.run(
            [sys.executable, "-m", "ts_reasoner.milestone"],
            check=True,
            text=True,
            capture_output=True,
        )

        self.assertIn("TS-Reasoner Milestone Receipt", result.stdout)
        self.assertIn("input reports: 8", result.stdout)
        self.assertIn("known cases: 114", result.stdout)
        self.assertIn("known candidates: 151", result.stdout)
        self.assertIn("wrong accepts: 0", result.stdout)

    def test_main_cli_milestone_command_prints_receipt(self):
        result = subprocess.run(
            [sys.executable, "-m", "ts_reasoner.cli", "milestone"],
            check=True,
            text=True,
            capture_output=True,
        )

        self.assertIn("TS-Reasoner Milestone Receipt", result.stdout)
        self.assertIn("all gates passed: True", result.stdout)


if __name__ == "__main__":
    unittest.main()
