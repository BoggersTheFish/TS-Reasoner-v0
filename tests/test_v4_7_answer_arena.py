import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.answer_arena import (
    classify_answer,
    evaluate_arena_cases,
    load_jsonl,
    relation_supported,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/v4_7/answer_arena_cases.jsonl"


class TestV47AnswerArena(unittest.TestCase):
    def test_relation_support_uses_transitive_premises(self):
        self.assertTrue(
            relation_supported(
                "Are all dogs animals?",
                ["all dogs are mammals", "all mammals are animals"],
            )
        )

    def test_relation_support_does_not_cross_components(self):
        self.assertFalse(
            relation_supported(
                "Are all cats vehicles?",
                ["all cats are animals", "all cars are vehicles"],
            )
        )

    def test_answer_classifier(self):
        self.assertEqual(classify_answer("Yes, all dogs are animals."), "yes")
        self.assertEqual(classify_answer("No, dogs are not animals."), "no")
        self.assertEqual(classify_answer("Cannot determine."), "abstain")
        self.assertEqual(classify_answer("All whales are animals."), "yes")

    def test_arena_report_gates(self):
        report = evaluate_arena_cases(load_jsonl(DATA))

        self.assertEqual(report["version"], "v4.7-verifier-first-answer-arena")
        self.assertEqual(report["case_count"], 8)
        self.assertEqual(report["candidate_count"], 24)
        self.assertEqual(report["arena_selection_accuracy"], 1.0)
        self.assertLess(report["confidence_top_accuracy"], report["arena_selection_accuracy"])
        self.assertGreater(report["verifier_overrode_confidence_count"], 0)
        self.assertEqual(report["wrong_accept_count"], 0)
        self.assertEqual(report["accepted_without_typed_support_count"], 0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)
        self.assertTrue(report["gates"]["all_gates_passed"])

    def test_evaluator_script_writes_receipt(self):
        result = subprocess.run(
            [sys.executable, "scripts/v4_7/evaluate_answer_arena.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn('"all_gates_passed": true', result.stdout)
        self.assertTrue((ROOT / "artifacts/v4_7_answer_arena_report.json").exists())


if __name__ == "__main__":
    unittest.main()
