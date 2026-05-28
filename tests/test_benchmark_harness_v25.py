from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from scripts.evaluate_benchmark_harness import DEFAULT_BENCHMARKS, evaluate
from ts_reasoner.benchmark_harness import load_benchmark_cases, run_benchmark_cases


ROOT = Path(__file__).resolve().parents[1]


class BenchmarkHarnessV25Tests(unittest.TestCase):
    def test_loads_all_benchmark_splits(self) -> None:
        cases = load_benchmark_cases([ROOT / path for path in DEFAULT_BENCHMARKS])
        self.assertEqual(len(cases), 28)
        self.assertEqual({case.split for case in cases}, {"train", "dev", "test"})
        self.assertEqual(
            {case.category for case in cases},
            {"syllogism", "rule_deduction", "adversarial_invalid"},
        )

    def test_benchmark_metrics_hit_v25_gate(self) -> None:
        report = evaluate(DEFAULT_BENCHMARKS)
        metrics = report["metrics"]
        self.assertEqual(report["case_count"], 28)
        self.assertGreaterEqual(metrics["status_accuracy"], 0.95)
        self.assertGreaterEqual(metrics["claim_accuracy"], 0.95)
        self.assertGreaterEqual(metrics["invalid_rejection_or_abstention_rate"], 0.95)
        self.assertEqual(metrics["accepted_without_typed_support_count"], 0)
        self.assertEqual(metrics["candidate_graph_contamination_count"], 0)
        self.assertEqual(metrics["trace_schema_validity"], 1.0)

    def test_group_metrics_exist_for_splits_and_categories(self) -> None:
        report = evaluate(DEFAULT_BENCHMARKS)
        self.assertIn("train", report["splits"])
        self.assertIn("dev", report["splits"])
        self.assertIn("test", report["splits"])
        self.assertIn("syllogism", report["categories"])
        self.assertIn("rule_deduction", report["categories"])
        self.assertIn("adversarial_invalid", report["categories"])

    def test_harness_rejects_or_abstains_invalid_cases(self) -> None:
        cases = load_benchmark_cases([ROOT / "data/benchmarks/adversarial_invalid_test.jsonl"])
        report = run_benchmark_cases(cases)
        self.assertEqual(report["metrics"]["invalid_rejection_or_abstention_rate"], 1.0)
        self.assertEqual(report["metrics"]["accepted_without_typed_support_count"], 0)

    def test_evaluator_script_writes_report_and_receipt(self) -> None:
        subprocess.check_call([sys.executable, "scripts/evaluate_benchmark_harness.py"], cwd=ROOT)
        self.assertTrue((ROOT / "artifacts/benchmark_harness_report.json").exists())
        self.assertTrue((ROOT / "artifacts/benchmark_harness_receipt.json").exists())


if __name__ == "__main__":
    unittest.main()
