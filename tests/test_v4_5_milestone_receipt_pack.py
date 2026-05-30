import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "artifacts/v4_5_milestone_receipt_pack.json"


class TestV45MilestoneReceiptPack(unittest.TestCase):
    def test_generator_runs_and_gates_pass(self):
        subprocess.run(
            [sys.executable, "scripts/v4_5_generate_milestone_receipt_pack.py"],
            cwd=ROOT,
            check=True,
        )

        data = json.loads(RECEIPT.read_text())

        self.assertEqual(data["version"], "v4.5-milestone-receipt-pack")
        self.assertEqual(data["input_report_count"], 8)
        self.assertEqual(data["wrong_accept_total"], 0)
        self.assertEqual(data["accepted_without_typed_support_total"], 0)
        self.assertEqual(data["candidate_graph_contamination_total"], 0)

        self.assertTrue(data["confidence_is_not_proof"])
        self.assertTrue(data["generated_text_is_not_proof"])
        self.assertTrue(data["typed_verifier_is_proof_authority"])

        self.assertFalse(data["external_benchmark_victory_claim"])
        self.assertFalse(data["broad_nlp_claim"])
        self.assertFalse(data["gpt2_superiority_claim"])
        self.assertFalse(data["live_tensionlm_runtime_claim"])

        self.assertTrue(data["gates"]["all_gates_passed"])


if __name__ == "__main__":
    unittest.main()
