from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V3VerifierGuidedModelTests(unittest.TestCase):
    def test_v3_train_and_eval_scripts_write_artifacts(self) -> None:
        subprocess.check_call([sys.executable, "scripts/v3/build_v3_training_dataset.py"], cwd=ROOT)
        subprocess.check_call([sys.executable, "scripts/v3/train_v3_verifier_guided_model.py"], cwd=ROOT)
        subprocess.check_call([sys.executable, "scripts/v3/evaluate_v3_verifier_guided_model.py"], cwd=ROOT)

        self.assertTrue((ROOT / "artifacts/v3/verifier_guided_candidate_model.json").exists())
        self.assertTrue((ROOT / "artifacts/v3/verifier_guided_candidate_model_report.json").exists())
        self.assertTrue((ROOT / "artifacts/v3/verifier_guided_candidate_model_receipt.json").exists())
        self.assertTrue((ROOT / "artifacts/v3/v3_eval_predictions.jsonl").exists())

    def test_v3_model_metadata_preserves_boundary(self) -> None:
        subprocess.check_call([sys.executable, "scripts/v3/build_v3_training_dataset.py"], cwd=ROOT)
        subprocess.check_call([sys.executable, "scripts/v3/train_v3_verifier_guided_model.py"], cwd=ROOT)

        model = json.loads((ROOT / "artifacts/v3/verifier_guided_candidate_model.json").read_text())

        self.assertEqual(model["model_type"], "VerifierGuidedCandidateModel")
        self.assertEqual(model["version"], "v3.0.0")
        self.assertEqual(model["metadata"]["boundary"]["proof_role"], "model is not proof authority")
        self.assertEqual(
            model["metadata"]["boundary"]["verifier_role"],
            "typed verifier channels remain proof authority",
        )

    def test_v3_eval_gates_pass(self) -> None:
        subprocess.check_call([sys.executable, "scripts/v3/build_v3_training_dataset.py"], cwd=ROOT)
        subprocess.check_call([sys.executable, "scripts/v3/train_v3_verifier_guided_model.py"], cwd=ROOT)
        subprocess.check_call([sys.executable, "scripts/v3/evaluate_v3_verifier_guided_model.py"], cwd=ROOT)

        report = json.loads((ROOT / "artifacts/v3/verifier_guided_candidate_model_report.json").read_text())
        metrics = report["metrics"]
        gates = report["gates"]

        self.assertEqual(metrics["status_accuracy"], 1.0)
        self.assertGreaterEqual(metrics["channel_prediction_accuracy"], 0.98)
        self.assertGreaterEqual(metrics["beats_majority_margin"], 0.20)
        self.assertGreaterEqual(metrics["beats_confidence_margin"], 0.20)
        self.assertEqual(metrics["accepted_without_typed_support_count"], 0)
        self.assertEqual(metrics["candidate_graph_contamination_count"], 0)
        self.assertEqual(metrics["trace_schema_validity"], 1.0)
        self.assertTrue(gates["all_gates_passed"])


if __name__ == "__main__":
    unittest.main()
