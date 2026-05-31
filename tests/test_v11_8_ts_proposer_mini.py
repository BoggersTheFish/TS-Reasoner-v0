from __future__ import annotations

import unittest
from pathlib import Path

from training.v11_8.ts_proposer_mini import (
    ProposerMiniConfig,
    featurize,
    load_trace_splits,
    train_and_evaluate,
)


ROOT = Path(__file__).resolve().parents[1]


class TSProposerMiniV118Tests(unittest.TestCase):
    def test_trace_splits_available(self) -> None:
        splits = load_trace_splits(ROOT)
        self.assertGreater(len(splits["train"]), 0)
        self.assertGreater(len(splits["valid"]), 0)
        self.assertGreater(len(splits["test"]), 0)

    def test_featurizer_has_structural_features(self) -> None:
        row = load_trace_splits(ROOT)["train"][0]
        features = featurize(row, dim=256)
        self.assertGreater(len(features), 0)
        self.assertTrue(all(0 <= idx < 256 for idx in features))

    def test_small_train_and_gate(self) -> None:
        result = train_and_evaluate(
            ROOT,
            ProposerMiniConfig(
                dim=1024,
                epochs=3,
                learning_rate=1.0,
                train_limit=600,
                valid_limit=120,
                test_limit=120,
            ),
        )
        report = result["report"]
        self.assertGreaterEqual(report["test"]["answer_accuracy"], 0.55)
        self.assertEqual(report["test"]["gated_wrong_accept_count"], 0)
        self.assertEqual(report["test"]["accepted_without_typed_support_count"], 0)


if __name__ == "__main__":
    unittest.main()
