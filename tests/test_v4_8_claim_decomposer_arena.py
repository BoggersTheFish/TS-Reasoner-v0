import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.claim_decomposer import decompose_candidate_answer
from ts_reasoner.decomposed_answer_arena import evaluate_decomposed_arena_cases, load_jsonl


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/v4_8/claim_decomposer_arena_cases.jsonl"


class TestV48ClaimDecomposerArena(unittest.TestCase):
    def test_direct_relation_extraction(self):
        claim = decompose_candidate_answer("Yes, all dogs are animals.")
        self.assertEqual(claim.answer_type, "yes")
        self.assertIsNotNone(claim.extracted_relation)
        self.assertEqual(claim.extracted_relation.subject, "dogs")
        self.assertEqual(claim.extracted_relation.object, "animals")

    def test_question_relation_fallback(self):
        claim = decompose_candidate_answer("Yes.", question="Are all robins living things?")
        self.assertEqual(claim.answer_type, "yes")
        self.assertEqual(claim.extraction_status, "question_relation_fallback")
        self.assertIsNotNone(claim.extracted_relation)
        self.assertEqual(claim.extracted_relation.subject, "robins")
        self.assertEqual(claim.extracted_relation.object, "living things")

    def test_abstention_extracts_no_positive_claim(self):
        claim = decompose_candidate_answer("Cannot determine.")
        self.assertEqual(claim.answer_type, "abstain")
        self.assertIsNone(claim.extracted_relation)

    def test_decomposed_arena_report_gates(self):
        report = evaluate_decomposed_arena_cases(load_jsonl(DATA))

        self.assertEqual(report["version"], "v4.8-claim-decomposer-answer-arena")
        self.assertEqual(report["case_count"], 8)
        self.assertEqual(report["candidate_count"], 24)
        self.assertGreaterEqual(report["claim_extraction_rate"], 0.5)
        self.assertEqual(report["arena_selection_accuracy"], 1.0)
        self.assertLess(report["confidence_top_accuracy"], report["arena_selection_accuracy"])
        self.assertGreater(report["verifier_overrode_confidence_count"], 0)
        self.assertEqual(report["wrong_accept_count"], 0)
        self.assertEqual(report["accepted_without_typed_support_count"], 0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)
        self.assertTrue(report["gates"]["all_gates_passed"])

    def test_evaluator_script_writes_receipt(self):
        result = subprocess.run(
            [sys.executable, "scripts/v4_8/evaluate_claim_decomposer_arena.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn('"all_gates_passed": true', result.stdout)
        self.assertTrue((ROOT / "artifacts/v4_8_claim_decomposer_arena_report.json").exists())


if __name__ == "__main__":
    unittest.main()
