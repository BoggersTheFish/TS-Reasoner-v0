from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.trace_training_data import (
    export_training_rows_from_candidate_report,
    summarize_training_rows,
)


ROOT = Path(__file__).resolve().parents[1]


class VerifierTraceTrainingDataTests(unittest.TestCase):
    def test_export_rows_from_candidate_model_v2_report(self) -> None:
        report = json.loads((ROOT / "artifacts/candidate_model_v2_report.json").read_text())
        rows = export_training_rows_from_candidate_report(report)
        summary = summarize_training_rows(rows)

        self.assertEqual(summary["row_count"], 91)
        self.assertEqual(summary["accepted_rows"], 13)
        self.assertEqual(summary["rejected_rows"], 40)
        self.assertEqual(summary["abstained_rows"], 38)
        self.assertTrue(summary["has_model_features"])
        self.assertTrue(summary["has_verifier_targets"])
        self.assertTrue(summary["has_boundary"])

    def test_exported_rows_contain_training_targets_and_verifier_context(self) -> None:
        report = json.loads((ROOT / "artifacts/candidate_model_v2_report.json").read_text())
        rows = export_training_rows_from_candidate_report(report)

        first = rows[0]
        self.assertEqual(first["training_schema_version"], "v2.7.0")
        self.assertIn("model_features", first)
        self.assertIn("model_prediction", first)
        self.assertIn("verifier", first)
        self.assertIn("training_target", first)
        self.assertIn("boundary", first)
        self.assertIn(first["training_target"]["target_status"], {"accepted", "rejected", "abstained"})

    def test_training_targets_cover_accept_reject_abstain(self) -> None:
        report = json.loads((ROOT / "artifacts/candidate_model_v2_report.json").read_text())
        rows = export_training_rows_from_candidate_report(report)
        statuses = {row["training_target"]["target_status"] for row in rows}
        self.assertEqual(statuses, {"accepted", "rejected", "abstained"})

    def test_export_script_writes_jsonl_summary_and_receipt(self) -> None:
        subprocess.check_call([sys.executable, "scripts/export_verifier_trace_training_data.py"], cwd=ROOT)
        self.assertTrue((ROOT / "data/verifier_trace_training_data_v27.jsonl").exists())
        self.assertTrue((ROOT / "artifacts/verifier_trace_training_data_summary.json").exists())
        self.assertTrue((ROOT / "artifacts/verifier_trace_training_data_receipt.json").exists())


if __name__ == "__main__":
    unittest.main()
