from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from scripts.evaluate_natural_language_claim_ingestion import evaluate_cases
from ts_reasoner.nl_claim_parser import parse_natural_language_claim, run_natural_language_claim_ingestion


ROOT = Path(__file__).resolve().parents[1]


class NaturalLanguageClaimIngestionTests(unittest.TestCase):
    def test_parser_extracts_premises_and_query_claim(self) -> None:
        parsed = parse_natural_language_claim(
            "All dogs are mammals. All mammals are animals. Are all dogs animals?"
        )
        self.assertTrue(parsed.parse_success)
        self.assertEqual(parsed.premises, ["All dogs are mammals", "All mammals are animals"])
        self.assertEqual(parsed.candidate_claim, "All dogs are animals")

    def test_valid_chain_is_accepted_through_typed_verifier(self) -> None:
        result = run_natural_language_claim_ingestion(
            "All dogs are mammals. All mammals are animals. Are all dogs animals?",
            case_id="unit_valid",
        )
        self.assertEqual(result["status"], "accepted")
        self.assertEqual(result["verification"]["accepted"], ["All dogs are animals"])
        self.assertEqual(result["verification"]["candidate_results"][0]["source"], "natural_language_claim_parser")

    def test_reverse_inference_is_rejected_not_accepted(self) -> None:
        result = run_natural_language_claim_ingestion(
            "All cats are animals. Are all animals cats?",
            case_id="unit_reverse",
        )
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["verification"]["accepted"], [])

    def test_malformed_input_safe_abstains_without_candidate(self) -> None:
        result = run_natural_language_claim_ingestion("Dogs maybe mammal vibes???", case_id="unit_bad")
        self.assertEqual(result["status"], "abstained")
        self.assertFalse(result["parser"]["parse_success"])
        self.assertEqual(result["trace_receipt"]["candidate_count"], 0)

    def test_dataset_metrics_hit_v24_gate(self) -> None:
        report = evaluate_cases(ROOT / "data/natural_language_claim_cases.jsonl")
        metrics = report["metrics"]
        self.assertEqual(report["case_count"], 10)
        self.assertGreaterEqual(metrics["parse_expectation_rate"], 0.95)
        self.assertGreaterEqual(metrics["status_expectation_rate"], 0.95)
        self.assertGreaterEqual(metrics["malformed_input_safe_abstain_rate"], 1.0)
        self.assertEqual(metrics["accepted_without_typed_support_count"], 0)
        self.assertEqual(metrics["candidate_graph_contamination_count"], 0)
        self.assertEqual(metrics["trace_schema_validity"], 1.0)

    def test_evaluator_script_writes_report_and_receipt(self) -> None:
        subprocess.check_call([sys.executable, "scripts/evaluate_natural_language_claim_ingestion.py"], cwd=ROOT)
        self.assertTrue((ROOT / "artifacts/natural_language_claim_ingestion_report.json").exists())
        self.assertTrue((ROOT / "artifacts/natural_language_claim_ingestion_receipt.json").exists())


if __name__ == "__main__":
    unittest.main()
