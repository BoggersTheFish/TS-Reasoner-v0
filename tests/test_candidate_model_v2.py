from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from scripts.evaluate_candidate_model_v2 import evaluate_split
from ts_reasoner.learned_model.dataset import load_cases
from ts_reasoner.learned_model.model import TinyCandidateModel


ROOT = Path(__file__).resolve().parents[1]


class CandidateModelV2Tests(unittest.TestCase):
    def test_dataset_builder_writes_expected_splits(self) -> None:
        subprocess.check_call([sys.executable, "scripts/build_candidate_model_v2_dataset.py"], cwd=ROOT)
        train = load_cases(ROOT / "data/candidate_model_v2_train.jsonl")
        eval_rows = load_cases(ROOT / "data/candidate_model_v2_eval.jsonl")
        stress = load_cases(ROOT / "data/candidate_model_v2_stress.jsonl")
        self.assertEqual(len(train), 9)
        self.assertEqual(len(eval_rows), 7)
        self.assertEqual(len(stress), 12)
        self.assertTrue(all("labels" in row for row in train + eval_rows + stress))

    def test_candidate_model_v2_metrics_hit_gate(self) -> None:
        subprocess.check_call([sys.executable, "scripts/train_candidate_model_v2.py"], cwd=ROOT)
        model = TinyCandidateModel.load(ROOT / "artifacts/candidate_model_v2.json")
        cases = load_cases(ROOT / "data/candidate_model_v2_eval.jsonl") + load_cases(
            ROOT / "data/candidate_model_v2_stress.jsonl"
        )
        report = evaluate_split(model, cases)
        metrics = report["metrics"]
        self.assertEqual(metrics["candidate_ranking_accuracy"], 1.0)
        self.assertGreaterEqual(metrics["learned_beats_confidence_baseline_margin"], 0.5)
        self.assertEqual(metrics["multi_premise_ranking_success_rate"], 1.0)
        self.assertEqual(metrics["invalid_query_rejection_or_abstention_rate"], 1.0)
        self.assertEqual(metrics["supported_alternative_recovery_rate"], 1.0)
        self.assertEqual(metrics["malformed_input_non_accept_rate"], 1.0)
        self.assertEqual(metrics["accepted_without_typed_support_count"], 0)
        self.assertEqual(metrics["candidate_graph_contamination_count"], 0)
        self.assertEqual(metrics["trace_schema_validity"], 1.0)

    def test_evaluator_script_writes_report_and_receipt(self) -> None:
        subprocess.check_call([sys.executable, "scripts/evaluate_candidate_model_v2.py"], cwd=ROOT)
        self.assertTrue((ROOT / "artifacts/candidate_model_v2_report.json").exists())
        self.assertTrue((ROOT / "artifacts/candidate_model_v2_receipt.json").exists())


if __name__ == "__main__":
    unittest.main()
