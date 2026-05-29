import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "artifacts" / "scaled_proposer_boundary_v36_report.json"
RECEIPT = ROOT / "artifacts" / "scaled_proposer_boundary_v36_receipt.json"
TRACES = ROOT / "artifacts" / "scaled_proposer_boundary_v36_traces.jsonl"


class TestScaledProposerBoundaryV36(unittest.TestCase):
    def test_scaled_proposer_boundary_gates(self):
        subprocess.run(
            [sys.executable, "scripts/v3_6/evaluate_scaled_proposer_boundary_v36.py"],
            cwd=ROOT,
            check=True,
        )

        report = json.loads(REPORT.read_text(encoding="utf-8"))
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        trace_lines = [line for line in TRACES.read_text(encoding="utf-8").splitlines() if line.strip()]

        self.assertEqual(report["wrong_accept_count"], 0)
        self.assertEqual(report["accepted_without_typed_support_count"], 0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)
        self.assertEqual(report["trace_schema_validity"], 1.0)
        self.assertFalse(report["live_tensionlm_runtime_loaded"])
        self.assertEqual(len(trace_lines), report["case_count"])
        self.assertTrue(all(receipt["gates"].values()))


if __name__ == "__main__":
    unittest.main()
