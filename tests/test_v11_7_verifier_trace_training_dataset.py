from __future__ import annotations

import unittest

from training.v11_7.build_trace_training_data import (
    TraceDatasetConfig,
    build_trace_rows,
    replay_row,
    split_rows,
    summarize_dataset,
)


class VerifierTraceTrainingDatasetV117Tests(unittest.TestCase):
    def test_build_small_trace_dataset(self) -> None:
        config = TraceDatasetConfig(
            seed=117,
            procedural_task_count=120,
            adversarial_case_count=80,
            target_row_count=160,
        )
        rows = build_trace_rows(config)
        self.assertEqual(len(rows), 160)
        self.assertTrue(all("input" in row for row in rows))
        self.assertTrue(all("target" in row for row in rows))
        self.assertTrue(all(row["target"]["answer"] in {"yes", "no", "abstain"} for row in rows))

    def test_rows_replay_through_verifier(self) -> None:
        config = TraceDatasetConfig(
            seed=118,
            procedural_task_count=120,
            adversarial_case_count=80,
            target_row_count=120,
        )
        rows = build_trace_rows(config)
        self.assertTrue(all(replay_row(row) for row in rows))

    def test_summary_gates_small_dataset(self) -> None:
        config = TraceDatasetConfig(
            seed=119,
            procedural_task_count=160,
            adversarial_case_count=120,
            target_row_count=200,
        )
        rows = build_trace_rows(config)
        splits = split_rows(rows, config)
        summary = summarize_dataset(splits)

        self.assertEqual(summary["row_count"], 200)
        self.assertEqual(summary["label_verifier_replay_rate"], 1.0)
        self.assertEqual(summary["trace_hash_validity"], 1.0)
        self.assertEqual(summary["accepted_without_typed_support_count"], 0)
        self.assertTrue(summary["class_balance_valid"])
        self.assertTrue(summary["leakage_check_passed"])
        self.assertTrue(summary["all_gates_passed"])


if __name__ == "__main__":
    unittest.main()
