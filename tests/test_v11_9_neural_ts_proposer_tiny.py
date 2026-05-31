from __future__ import annotations

import unittest
from pathlib import Path

from training.v11_9.neural_ts_proposer_tiny import NeuralTinyConfig, TinyNeuralClassifier, train_and_evaluate
from training.v11_8.ts_proposer_mini import featurize, load_trace_splits


ROOT = Path(__file__).resolve().parents[1]


class NeuralTSProposerTinyV119Tests(unittest.TestCase):
    def test_forward_predict_contract(self) -> None:
        rows = load_trace_splits(ROOT)["train"]
        labels = ["abstain", "no", "yes"]
        model = TinyNeuralClassifier.fresh(labels=labels, dim=128, hidden=8, seed=119)
        features = featurize(rows[0], dim=128)
        hidden, logits, probs = model.forward_features(features)
        self.assertEqual(len(hidden), 8)
        self.assertEqual(len(logits), len(labels))
        self.assertAlmostEqual(sum(probs), 1.0, places=6)
        self.assertIn(model.predict_features(features), labels)

    def test_small_neural_train_and_gate(self) -> None:
        result = train_and_evaluate(
            ROOT,
            NeuralTinyConfig(
                dim=256,
                hidden=12,
                epochs=2,
                learning_rate=0.035,
                seed=120,
                train_limit=300,
                valid_limit=80,
                test_limit=80,
            ),
        )
        report = result["report"]
        self.assertGreaterEqual(report["test"]["answer_accuracy"], 0.30)
        self.assertEqual(report["test"]["gated_wrong_accept_count"], 0)
        self.assertEqual(report["test"]["accepted_without_typed_support_count"], 0)


if __name__ == "__main__":
    unittest.main()
