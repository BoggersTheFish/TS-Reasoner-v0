from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ActiveLearningLoopV29Tests(unittest.TestCase):
    def test_active_learning_script_writes_outputs(self) -> None:
        subprocess.check_call([sys.executable, "scripts/run_active_learning_loop_v29.py"], cwd=ROOT)

        self.assertTrue((ROOT / "artifacts/active_learning_loop_v29_report.json").exists())
        self.assertTrue((ROOT / "artifacts/active_learning_loop_v29_receipt.json").exists())
        self.assertTrue((ROOT / "artifacts/active_learning_status_model_v29.json").exists())
        self.assertTrue((ROOT / "data/active_learning_challenge_v29.jsonl").exists())
        self.assertTrue((ROOT / "data/active_learning_augmented_training_v29.jsonl").exists())

    def test_active_learning_improves_challenge_accuracy(self) -> None:
        subprocess.check_call([sys.executable, "scripts/run_active_learning_loop_v29.py"], cwd=ROOT)
        report = json.loads((ROOT / "artifacts/active_learning_loop_v29_report.json").read_text())
        metrics = report["metrics"]

        self.assertEqual(report["challenge_rows"], 12)
        self.assertEqual(report["base_train_rows"], 35)
        self.assertEqual(report["augmented_train_rows"], 47)
        self.assertGreater(metrics["active_learning_challenge_accuracy"], metrics["baseline_challenge_accuracy"])
        self.assertGreater(metrics["active_learning_improvement"], 0.0)
        self.assertGreater(metrics["active_beats_confidence_margin"], 0.0)

    def test_active_learning_boundary_is_explicit(self) -> None:
        subprocess.check_call([sys.executable, "scripts/run_active_learning_loop_v29.py"], cwd=ROOT)
        report = json.loads((ROOT / "artifacts/active_learning_loop_v29_report.json").read_text())
        model = json.loads((ROOT / "artifacts/active_learning_status_model_v29.json").read_text())

        self.assertEqual(report["boundary"]["proof_role"], "trained model is not proof authority")
        self.assertEqual(report["boundary"]["verifier_role"], "typed verifier traces define target labels")
        self.assertIn("not proof authority", model["metadata"]["boundary"])


if __name__ == "__main__":
    unittest.main()
