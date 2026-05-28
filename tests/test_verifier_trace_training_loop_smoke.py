from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class VerifierTraceTrainingLoopSmokeTests(unittest.TestCase):
    def test_training_loop_smoke_script_writes_model_and_report(self) -> None:
        subprocess.check_call([sys.executable, "scripts/train_from_verifier_trace_smoke.py"], cwd=ROOT)

        model_path = ROOT / "artifacts/verifier_trace_status_model_v28.json"
        report_path = ROOT / "artifacts/verifier_trace_training_loop_smoke_report.json"

        self.assertTrue(model_path.exists())
        self.assertTrue(report_path.exists())

        report = json.loads(report_path.read_text())
        metrics = report["metrics"]

        self.assertEqual(report["row_count"], 91)
        self.assertEqual(report["train_rows"], 35)
        self.assertEqual(report["eval_rows"], 56)
        self.assertEqual(metrics["train_accuracy"], 1.0)
        self.assertEqual(metrics["eval_accuracy"], 1.0)
        self.assertGreater(metrics["learned_beats_majority_margin"], 0.0)
        self.assertGreater(metrics["learned_beats_confidence_margin"], 0.0)

    def test_model_boundary_is_explicit(self) -> None:
        subprocess.check_call([sys.executable, "scripts/train_from_verifier_trace_smoke.py"], cwd=ROOT)

        model = json.loads((ROOT / "artifacts/verifier_trace_status_model_v28.json").read_text())
        self.assertEqual(model["model_type"], "verifier_trace_status_linear_smoke")
        self.assertIn("not proof authority", model["metadata"]["boundary"])

        report = json.loads((ROOT / "artifacts/verifier_trace_training_loop_smoke_report.json").read_text())
        self.assertEqual(report["boundary"]["proof_role"], "trained model is not proof authority")
        self.assertEqual(report["boundary"]["verifier_role"], "typed verifier traces define target labels")


if __name__ == "__main__":
    unittest.main()
