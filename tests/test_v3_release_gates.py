from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V3ReleaseGatesTests(unittest.TestCase):
    def test_v3_release_surface_exists_and_gates_pass(self) -> None:
        subprocess.check_call([sys.executable, "scripts/v3/build_v3_training_dataset.py"], cwd=ROOT)
        subprocess.check_call([sys.executable, "scripts/v3/train_v3_verifier_guided_model.py"], cwd=ROOT)
        subprocess.check_call([sys.executable, "scripts/v3/evaluate_v3_verifier_guided_model.py"], cwd=ROOT)

        for path in [
            "docs/v3/V3_MODEL_CARD.md",
            "docs/v3/V3_EVAL_REPORT.md",
            "docs/v3/V3_LIMITATIONS.md",
            "artifacts/v3/verifier_guided_candidate_model.json",
            "artifacts/v3/verifier_guided_candidate_model_report.json",
            "artifacts/v3/verifier_guided_candidate_model_receipt.json",
            "artifacts/v3/v3_eval_predictions.jsonl",
        ]:
            self.assertTrue((ROOT / path).exists(), path)

        report = json.loads((ROOT / "artifacts/v3/verifier_guided_candidate_model_report.json").read_text())
        self.assertTrue(report["gates"]["all_gates_passed"])

    def test_v3_demo_runs_and_preserves_boundary(self) -> None:
        subprocess.check_call([sys.executable, "scripts/v3/build_v3_training_dataset.py"], cwd=ROOT)
        subprocess.check_call([sys.executable, "scripts/v3/train_v3_verifier_guided_model.py"], cwd=ROOT)
        subprocess.check_call([sys.executable, "scripts/v3/evaluate_v3_verifier_guided_model.py"], cwd=ROOT)

        output = subprocess.check_output([sys.executable, "scripts/v3/run_v3_demo.py"], cwd=ROOT, text=True)
        payload = json.loads(output)

        self.assertEqual(payload["proof_boundary"]["verifier_role"], "typed verifier remains proof authority")
        self.assertEqual(payload["proof_boundary"]["proof_role"], "model prediction is not proof")
        self.assertIn(payload["predicted_status"], {"accepted", "rejected", "abstained"})


if __name__ == "__main__":
    unittest.main()
