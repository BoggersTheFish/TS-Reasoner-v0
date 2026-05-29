import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "artifacts" / "gpt2_baseline_comparison_v44_report.json"
RECEIPT = ROOT / "artifacts" / "gpt2_baseline_comparison_v44_receipt.json"
TRACES = ROOT / "artifacts" / "gpt2_baseline_comparison_v44_traces.jsonl"


class TestGpt2BaselineComparisonV44(unittest.TestCase):
    def test_gpt2_baseline_comparison_gates(self):
        subprocess.run(
            [sys.executable, "scripts/v4_4/evaluate_gpt2_baseline_comparison_v44.py"],
            cwd=ROOT,
            check=True,
        )

        report = json.loads(REPORT.read_text(encoding="utf-8"))
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        traces = [json.loads(line) for line in TRACES.read_text(encoding="utf-8").splitlines() if line.strip()]

        self.assertGreater(report["comparison_case_count"], 0)
        self.assertEqual(len(traces), report["comparison_case_count"])
        self.assertEqual(report["ts_wrong_accept_count"], 0)
        self.assertEqual(report["ts_accepted_without_typed_support_count"], 0)
        self.assertEqual(report["ts_candidate_graph_contamination_count"], 0)
        self.assertEqual(report["trace_schema_validity"], 1.0)
        self.assertTrue(report["gpt2_comparison_claim_is_bounded"])
        self.assertFalse(report["broad_gpt2_superiority_claim"])
        self.assertTrue(report["confidence_is_not_proof"])
        self.assertTrue(all(receipt["gates"].values()))


if __name__ == "__main__":
    unittest.main()
