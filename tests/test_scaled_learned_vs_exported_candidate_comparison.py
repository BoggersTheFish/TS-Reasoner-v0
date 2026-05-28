from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from scripts.evaluate_learned_vs_exported_candidate_comparison import evaluate_comparison


ROOT = Path(__file__).resolve().parents[1]


class ScaledLearnedVsExportedComparisonTests(unittest.TestCase):
    def test_scaled_dataset_builder_writes_expected_case_count(self) -> None:
        subprocess.check_call([sys.executable, "scripts/build_scaled_comparison_set.py"], cwd=ROOT)
        path = ROOT / "data/scaled_learned_vs_exported_candidate_comparison.jsonl"
        rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(len(rows), 15)

    def test_scaled_comparison_preserves_boundary_and_learned_ranking_wins(self) -> None:
        report = evaluate_comparison(
            ROOT / "artifacts/learned_candidate_model.json",
            ROOT / "data/scaled_learned_vs_exported_candidate_comparison.jsonl",
        )
        metrics = report["metrics"]
        self.assertEqual(report["case_count"], 15)
        self.assertEqual(metrics["learned_top_accept_rate"], 1.0)
        self.assertEqual(metrics["exported_confidence_top_accept_rate"], 0.0)
        self.assertEqual(metrics["learned_top_beats_exported_confidence_top_rate"], 1.0)
        self.assertEqual(metrics["exported_high_confidence_bad_block_rate"], 1.0)
        self.assertEqual(metrics["accepted_without_typed_support_count"], 0)
        self.assertEqual(metrics["candidate_graph_contamination_count"], 0)
        self.assertEqual(metrics["trace_schema_validity"], 1.0)


if __name__ == "__main__":
    unittest.main()
