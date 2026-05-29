import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADAPTER_REPORT = ROOT / "artifacts" / "gpt2_output_fixture_adapter_v42_report.json"
ADAPTER_RECEIPT = ROOT / "artifacts" / "gpt2_output_fixture_adapter_v42_receipt.json"
BACKEND = ROOT / "data" / "v4_2_gpt2_output_fixture_adapter" / "adapted_gpt2_external_backend_candidates_v42.jsonl"
SANDBOX_REPORT = ROOT / "artifacts" / "live_proposer_sandbox_v40_report.json"
SANDBOX_RECEIPT = ROOT / "artifacts" / "live_proposer_sandbox_v40_receipt.json"


class TestGpt2OutputFixtureAdapterV42(unittest.TestCase):
    def test_gpt2_fixture_adapter_and_external_backend(self):
        subprocess.run(
            [sys.executable, "scripts/v4_2/adapt_gpt2_output_fixtures_v42.py"],
            cwd=ROOT,
            check=True,
        )

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

        adapter_report = json.loads(ADAPTER_REPORT.read_text(encoding="utf-8"))
        adapter_receipt = json.loads(ADAPTER_RECEIPT.read_text(encoding="utf-8"))
        sandbox_report = json.loads(SANDBOX_REPORT.read_text(encoding="utf-8"))
        sandbox_receipt = json.loads(SANDBOX_RECEIPT.read_text(encoding="utf-8"))

        self.assertEqual(adapter_report["adapter_success_rate"], 1.0)
        self.assertFalse(adapter_report["gpt2_comparison_claim"])
        self.assertTrue(adapter_report["confidence_is_not_proof"])
        self.assertTrue(adapter_report["generated_text_is_not_proof"])
        self.assertTrue(all(adapter_receipt["gates"].values()))

        self.assertEqual(sandbox_report["backend_kind"], "external_jsonl")
        self.assertEqual(sandbox_report["backend_contract_validity"], 1.0)
        self.assertEqual(sandbox_report["wrong_accept_count"], 0)
        self.assertEqual(sandbox_report["accepted_without_typed_support_count"], 0)
        self.assertEqual(sandbox_report["candidate_graph_contamination_count"], 0)
        self.assertEqual(sandbox_report["provenance_preservation_rate"], 1.0)
        self.assertEqual(sandbox_report["trace_schema_validity"], 1.0)
        self.assertTrue(sandbox_report["confidence_is_not_proof"])
        self.assertTrue(all(sandbox_receipt["gates"].values()))


if __name__ == "__main__":
    unittest.main()
