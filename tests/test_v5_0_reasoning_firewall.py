import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.firewall_receipt import firewall_summary, load_firewall_receipt


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "artifacts/v5_0_reasoning_firewall_receipt.json"


class TestV50ReasoningFirewall(unittest.TestCase):
    def test_generator_writes_firewall_receipt(self):
        result = subprocess.run(
            [sys.executable, "scripts/v5_0/generate_reasoning_firewall_receipt.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn('"all_gates_passed": true', result.stdout)
        self.assertTrue(RECEIPT.exists())

    def test_firewall_receipt_gates(self):
        data = json.loads(RECEIPT.read_text())

        self.assertEqual(data["version"], "v5.0-verifier-first-reasoning-firewall")
        self.assertEqual(data["input_report_count"], 3)
        self.assertEqual(data["wrong_accept_total"], 0)
        self.assertEqual(data["accepted_without_typed_support_total"], 0)
        self.assertEqual(data["accepted_with_unsupported_claims_total"], 0)
        self.assertEqual(data["candidate_graph_contamination_total"], 0)
        self.assertGreater(data["total_unsupported_claim_candidate_count"], 0)
        self.assertTrue(data["gates"]["all_gates_passed"])

    def test_firewall_summary_boundary(self):
        summary = firewall_summary(load_firewall_receipt())

        self.assertIn("TS-Reasoner Verifier-First Reasoning Firewall", summary)
        self.assertIn("confidence is not proof: True", summary)
        self.assertIn("generated text is not proof: True", summary)
        self.assertIn("candidate source is not proof: True", summary)
        self.assertIn("typed verifier is proof authority: True", summary)
        self.assertIn("all gates passed: True", summary)

    def test_cli_firewall_command_prints_receipt(self):
        result = subprocess.run(
            [sys.executable, "-m", "ts_reasoner.cli", "firewall"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn("TS-Reasoner Verifier-First Reasoning Firewall", result.stdout)
        self.assertIn("wrong accepts: 0", result.stdout)
        self.assertIn("accepted with unsupported claims: 0", result.stdout)


if __name__ == "__main__":
    unittest.main()
