import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "data" / "v4_1_external_jsonl_backend_proof" / "external_backend_candidates_v41.jsonl"
REPORT = ROOT / "artifacts" / "live_proposer_sandbox_v40_report.json"
RECEIPT = ROOT / "artifacts" / "live_proposer_sandbox_v40_receipt.json"
TRACES = ROOT / "artifacts" / "live_proposer_sandbox_v40_traces.jsonl"


class TestExternalJsonlBackendV41(unittest.TestCase):
    def test_external_jsonl_backend_path(self):
        subprocess.run(
            [
                sys.executable,
                "scripts/v4_0/run_live_proposer_sandbox_v40.py",
                "--external-jsonl-backend",
                str(BACKEND),
            ],
            cwd=ROOT,
            check=True,
        )

        report = json.loads(REPORT.read_text(encoding="utf-8"))
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        trace_lines = [line for line in TRACES.read_text(encoding="utf-8").splitlines() if line.strip()]

        self.assertEqual(report["backend_kind"], "external_jsonl")
        self.assertEqual(report["backend_name"], "external_jsonl_proposer_backend_v1")
        self.assertTrue(report["live_proposer_sandbox_executed"])
        self.assertEqual(report["backend_contract_validity"], 1.0)
        self.assertEqual(report["wrong_accept_count"], 0)
        self.assertEqual(report["accepted_without_typed_support_count"], 0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)
        self.assertEqual(report["provenance_preservation_rate"], 1.0)
        self.assertEqual(report["trace_schema_validity"], 1.0)
        self.assertTrue(report["confidence_is_not_proof"])
        self.assertFalse(report["live_tensionlm_runtime_loaded"])
        self.assertFalse(report["production_runtime_claim"])
        self.assertEqual(len(trace_lines), report["sandbox_case_count"])
        self.assertTrue(all(receipt["gates"].values()))


if __name__ == "__main__":
    unittest.main()
