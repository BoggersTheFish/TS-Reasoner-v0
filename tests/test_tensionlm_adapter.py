import json
import unittest

from ts_reasoner.tensionlm_adapter import (
    normalize_candidate_claim_text,
    parse_tensionlm_export_row,
    run_tensionlm_export_row,
)


class TensionLMAdapterTests(unittest.TestCase):
    def test_export_row_normalizes_model_provenance(self):
        row = parse_tensionlm_export_row(
            {
                "case_id": "adapter_case",
                "input_text": "All A are B. All B are C. Are all A C?",
                "model": "TensionLM-export-fixture",
                "candidates": [
                    {
                        "claim": "All A are C",
                        "confidence": 0.72,
                        "provenance": "model_output",
                        "raw_text": "A is therefore C",
                    }
                ],
            }
        )

        candidate = row.candidates[0]
        self.assertEqual(candidate.source, "model_output")
        self.assertEqual(candidate.raw_output, "A is therefore C")
        self.assertEqual(candidate.metadata["model"], "TensionLM-export-fixture")
        self.assertEqual(candidate.metadata["adapter"], "real_tensionlm_export_jsonl")

    def test_adapter_keeps_high_confidence_bad_output_under_verifier(self):
        row = parse_tensionlm_export_row(
            {
                "case_id": "confidence_boundary",
                "input_text": "All A are B. All B are C. Are all A C?",
                "model": "TensionLM-export-fixture",
                "candidates": [
                    {
                        "candidate_id": "valid",
                        "claim": "All A are C",
                        "confidence": 0.2,
                        "provenance": "model_output",
                    },
                    {
                        "candidate_id": "bad",
                        "claim": "All C are A",
                        "confidence": 0.99,
                        "provenance": "model_output",
                    },
                ],
            }
        )
        payload = run_tensionlm_export_row(row)

        self.assertEqual(_result(payload, "All A are C")["status"], "accepted")
        bad = _result(payload, "All C are A")
        self.assertEqual(bad["status"], "rejected")
        self.assertEqual(bad["channels"]["directionality"], "blocked reverse inference")
        self.assertGreater(bad["confidence"], _result(payload, "All A are C")["confidence"])

    def test_malformed_and_missing_provenance_outputs_are_rejected(self):
        row = parse_tensionlm_export_row(
            {
                "case_id": "bad_exports",
                "input_text": "All A are B. All B are C. Are all A C?",
                "model": "TensionLM-export-fixture",
                "candidates": [
                    {"candidate_id": "malformed", "claim": "A therefore C maybe", "provenance": "model_output"},
                    {"candidate_id": "missing", "claim": "All A are C", "confidence": 0.7},
                ],
            }
        )
        payload = run_tensionlm_export_row(row)

        self.assertEqual(
            _result(payload, "A therefore C maybe")["channels"]["malformed_relation"],
            "rejected unparsable graph claim",
        )
        self.assertEqual(
            _result(payload, "All A are C")["channels"]["provenance"],
            "rejected missing candidate source",
        )

    def test_adapter_payload_is_json_serializable(self):
        row = parse_tensionlm_export_row(
            {
                "input_text": "All A are B. All B are C. Are all A C?",
                "model": "TensionLM-export-fixture",
                "candidates": [{"claim": "All A are C", "provenance": "model_output"}],
            }
        )

        json.dumps(run_tensionlm_export_row(row))

    def test_messy_paraphrase_normalizes_without_granting_proof_authority(self):
        claim, status = normalize_candidate_claim_text("Side note: all clouds are vapor. Final: every A is C.")

        self.assertEqual(claim, "All A are C")
        self.assertEqual(status, "messy_paraphrase")

    def test_partial_messy_claim_stays_malformed(self):
        claim, status = normalize_candidate_claim_text("A therefore C, probably.")

        self.assertEqual(claim, "A therefore C, probably.")
        self.assertEqual(status, "unparsed")

    def test_bad_confidence_defaults_but_candidate_still_verifies(self):
        row = parse_tensionlm_export_row(
            {
                "input_text": "All A are B. All B are C. Are all A C?",
                "model": "TensionLM-export-fixture",
                "candidates": [
                    {
                        "candidate_id": "bad_confidence_valid",
                        "claim": "Every A falls under C.",
                        "confidence": "very high",
                        "provenance": "model_output",
                    }
                ],
            }
        )
        candidate = row.candidates[0]
        payload = run_tensionlm_export_row(row)

        self.assertEqual(candidate.confidence, 0.5)
        self.assertEqual(candidate.metadata["confidence_status"], "invalid_defaulted")
        self.assertEqual(candidate.metadata["normalization_status"], "messy_paraphrase")
        self.assertEqual(_result(payload, "All A are C")["status"], "accepted")


def _result(payload, claim):
    for result in payload["verification"]["candidate_results"]:
        if result["claim"] == claim:
            return result
    raise AssertionError(f"missing result for {claim}")


if __name__ == "__main__":
    unittest.main()
