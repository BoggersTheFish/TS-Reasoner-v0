import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "artifacts" / "natural_language_reasoning_shell_v43_report.json"
RECEIPT = ROOT / "artifacts" / "natural_language_reasoning_shell_v43_receipt.json"
TRACES = ROOT / "artifacts" / "natural_language_reasoning_shell_v43_traces.jsonl"


class TestNaturalLanguageReasoningShellV43(unittest.TestCase):
    def test_natural_language_reasoning_shell_gates(self):
        subprocess.run(
            [sys.executable, "scripts/v4_3/run_natural_language_reasoning_shell_v43.py"],
            cwd=ROOT,
            check=True,
        )

        report = json.loads(REPORT.read_text(encoding="utf-8"))
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        traces = [json.loads(line) for line in TRACES.read_text(encoding="utf-8").splitlines() if line.strip()]

        self.assertEqual(report["extraction_success_rate"], 1.0)
        self.assertEqual(report["wrong_accept_count"], 0)
        self.assertEqual(report["accepted_without_typed_support_count"], 0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)
        self.assertEqual(report["trace_schema_validity"], 1.0)
        self.assertFalse(report["gpt2_comparison_claim"])
        self.assertFalse(report["broad_nlp_claim"])
        self.assertTrue(report["confidence_is_not_proof"])
        self.assertEqual(len(traces), report["nl_case_count"])
        self.assertTrue(all(receipt["gates"].values()))


if __name__ == "__main__":
    unittest.main()
