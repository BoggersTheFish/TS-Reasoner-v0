import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "artifacts" / "live_proposer_dry_run_interface_v39_report.json"
RECEIPT = ROOT / "artifacts" / "live_proposer_dry_run_interface_v39_receipt.json"
TRACES = ROOT / "artifacts" / "live_proposer_dry_run_interface_v39_traces.jsonl"


class TestLiveProposerDryRunInterfaceV39(unittest.TestCase):
    def test_live_proposer_dry_run_interface_gates(self):
        subprocess.run(
            [sys.executable, "scripts/v3_9/evaluate_live_proposer_dry_run_interface_v39.py"],
            cwd=ROOT,
            check=True,
        )

        report = json.loads(REPORT.read_text(encoding="utf-8"))
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        trace_lines = [line for line in TRACES.read_text(encoding="utf-8").splitlines() if line.strip()]

        self.assertEqual(report["interface_contract_validity"], 1.0)
        self.assertEqual(report["wrong_accept_count"], 0)
        self.assertEqual(report["accepted_without_typed_support_count"], 0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)
        self.assertEqual(report["provenance_preservation_rate"], 1.0)
        self.assertEqual(report["trace_schema_validity"], 1.0)
        self.assertFalse(report["live_tensionlm_runtime_loaded"])
        self.assertFalse(report["live_runtime_integration_claim"])
        self.assertTrue(report["v4_runtime_contract_ready"])
        self.assertEqual(len(trace_lines), report["input_case_count"])
        self.assertTrue(all(receipt["gates"].values()))


if __name__ == "__main__":
    unittest.main()
