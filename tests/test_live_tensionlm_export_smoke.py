import json
import tempfile
import unittest
from pathlib import Path

from scripts.evaluate_live_tensionlm_export_smoke import evaluate_row, load_export


class LiveTensionLMExportSmokeTests(unittest.TestCase):
    def test_export_smoke_shape_can_be_loaded(self):
        payload = {
            "export_mode": "simulated_external_tensionlm_export",
            "rows": [
                {
                    "case_id": "shape",
                    "input_text": "All A are B. All B are C. Are all A C?",
                    "model": "fixture",
                    "candidates": [
                        {
                            "candidate_id": "valid",
                            "claim": "Every A belongs to C.",
                            "confidence": 0.62,
                            "provenance": "live_export_fixture",
                        }
                    ],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "smoke.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            loaded = load_export(path)

        self.assertEqual(loaded["export_mode"], "simulated_external_tensionlm_export")
        self.assertEqual(len(loaded["rows"]), 1)

    def test_live_export_smoke_keeps_verifier_authority(self):
        row = {
            "case_id": "authority",
            "input_text": "All A are B. All B are C. Are all A C?",
            "model": "fixture",
            "export_mode": "simulated_external_export",
            "candidates": [
                {
                    "candidate_id": "valid",
                    "claim": "Every A belongs to C.",
                    "confidence": 0.3,
                    "provenance": "live_export_fixture",
                },
                {
                    "candidate_id": "bad",
                    "claim": "Every C belongs to A.",
                    "confidence": 0.95,
                    "provenance": "live_export_fixture",
                },
            ],
            "expected_status": {"All A are C": "accepted", "All C are A": "rejected"},
            "parsed_candidate_ids": ["valid", "bad"],
            "bad_candidate_ids": ["bad"],
            "bad_high_confidence_candidate_ids": ["bad"],
            "valid_candidate_ids": ["valid"],
            "expected_verifier_beats_candidate_confidence": True,
        }

        result = evaluate_row(row, 1)

        self.assertTrue(result["all_expected_ok"])
        self.assertTrue(result["verifier_beats_candidate_confidence"])
        self.assertEqual(result["candidate_graph_contamination_count"], 0)
        self.assertEqual(result["accepted_with_typed_support"], [True])


if __name__ == "__main__":
    unittest.main()
