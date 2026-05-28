from __future__ import annotations

import unittest
from pathlib import Path

from scripts.evaluate_learned_vs_exported_candidate_comparison import (
    evaluate_comparison,
    ensure_comparison_dataset,
)


ROOT = Path(__file__).resolve().parents[1]


class LearnedVsExportedCandidateComparisonTests(unittest.TestCase):
    def test_comparison_dataset_can_be_created(self) -> None:
        source = ROOT / "data/learned_candidate_model_adversarial.jsonl"
        target = ROOT / "data/learned_vs_exported_candidate_comparison.jsonl"

        ensure_comparison_dataset(source, target)

        self.assertTrue(target.exists())
        rows = [line for line in target.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertGreaterEqual(len(rows), 7)

    def test_learned_model_beats_exported_confidence_baseline_without_graph_contamination(self) -> None:
        report = evaluate_comparison(
            ROOT / "artifacts/learned_candidate_model.json",
            ROOT / "data/learned_vs_exported_candidate_comparison.jsonl",
        )
        metrics = report["metrics"]

        self.assertGreater(metrics["learned_top_accept_rate"], metrics["exported_confidence_top_accept_rate"])
        self.assertGreaterEqual(metrics["learned_top_beats_exported_confidence_top_rate"], 0.7)
        self.assertEqual(metrics["accepted_without_typed_support_count"], 0)
        self.assertEqual(metrics["candidate_graph_contamination_count"], 0)
        self.assertEqual(metrics["trace_schema_validity"], 1.0)


if __name__ == "__main__":
    unittest.main()
