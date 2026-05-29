import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "artifacts" / "external_benchmark_translation_pack_v38_report.json"
RECEIPT = ROOT / "artifacts" / "external_benchmark_translation_pack_v38_receipt.json"
TRACES = ROOT / "artifacts" / "external_benchmark_translation_pack_v38_traces.jsonl"
TRANSLATED = ROOT / "artifacts" / "external_benchmark_translation_pack_v38_translated_cases.jsonl"


class TestExternalBenchmarkTranslationPackV38(unittest.TestCase):
    def test_external_benchmark_translation_pack_gates(self):
        subprocess.run(
            [sys.executable, "scripts/v3_8/evaluate_external_benchmark_translation_pack_v38.py"],
            cwd=ROOT,
            check=True,
        )

        report = json.loads(REPORT.read_text(encoding="utf-8"))
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        trace_lines = [line for line in TRACES.read_text(encoding="utf-8").splitlines() if line.strip()]
        translated_lines = [line for line in TRANSLATED.read_text(encoding="utf-8").splitlines() if line.strip()]

        self.assertEqual(report["wrong_accept_count"], 0)
        self.assertEqual(report["accepted_without_typed_support_count"], 0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)
        self.assertEqual(report["source_metadata_preservation_rate"], 1.0)
        self.assertEqual(report["trace_schema_validity"], 1.0)
        self.assertFalse(report["external_benchmark_victory_claim"])
        self.assertFalse(report["live_tensionlm_runtime_loaded"])
        self.assertEqual(len(trace_lines), report["translated_case_count"])
        self.assertEqual(len(translated_lines), report["translated_case_count"])
        self.assertTrue(all(receipt["gates"].values()))


if __name__ == "__main__":
    unittest.main()
