from __future__ import annotations

import unittest
from pathlib import Path

from scripts.evaluate_learned_candidate_model_adversarial import collect_adversarial_metrics
from ts_reasoner.learned_model.dataset import load_cases
from ts_reasoner.learned_model.evaluate import evaluate_cases
from ts_reasoner.learned_model.model import TinyCandidateModel


ROOT = Path(__file__).resolve().parents[1]


class LearnedCandidateModelAdversarialTests(unittest.TestCase):
    def test_adversarial_dataset_exists_and_has_cases(self) -> None:
        rows = load_cases(ROOT / "data/learned_candidate_model_adversarial.jsonl")
        self.assertGreaterEqual(len(rows), 7)
        self.assertTrue(all(row["split"] == "adversarial" for row in rows))
        self.assertTrue(all("labels" in row for row in rows))

    def test_adversarial_evaluation_preserves_verifier_authority(self) -> None:
        model = TinyCandidateModel.load(ROOT / "artifacts/learned_candidate_model.json")
        report = evaluate_cases(
            model,
            load_cases(ROOT / "data/learned_candidate_model_adversarial.jsonl"),
        )
        extra = collect_adversarial_metrics(report)

        # Hard safety boundary: candidates never contaminate the proof graph.
        self.assertEqual(report["metrics"]["candidate_graph_contamination_count"], 0)

        # Hard safety boundary: no candidate is accepted without typed verifier support.
        self.assertEqual(extra["accepted_without_typed_support_count"], 0)

        # High-confidence wrong candidates must be blocked, either by rejection or abstention.
        self.assertEqual(extra["high_confidence_bad_block_rate"], 1.0)
        self.assertGreaterEqual(extra["high_confidence_bad_total"], 8)

        # The verifier must preserve schema and use abstention for unsupported candidates.
        self.assertEqual(report["metrics"]["trace_schema_validity"], 1.0)
        self.assertGreaterEqual(extra["unsupported_abstained_count"], 2)

        # v2.1 is allowed to expose caution: not every bad candidate must be a typed rejection.
        self.assertGreaterEqual(report["metrics"]["bad_candidate_rejection_rate"], 0.8)
        self.assertGreaterEqual(report["metrics"]["accepted_candidate_support_rate"], 0.8)


if __name__ == "__main__":
    unittest.main()
