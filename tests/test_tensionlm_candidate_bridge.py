import json
import unittest

from ts_reasoner.candidate_bridge import (
    ExternalTensionLMCandidateProposer,
    run_tensionlm_candidate_bridge,
)


class TensionLMCandidateBridgeTests(unittest.TestCase):
    def test_mock_bridge_accepts_transitive_claim_and_rejects_reverse(self):
        payload = run_tensionlm_candidate_bridge("All A are B. All B are C. Are all A C?")

        self.assertIn("All A are C", payload["verification"]["accepted"])
        self.assertIn("All C are A", payload["verification"]["rejected"])
        channels = payload["verification"]["channels"]
        self.assertEqual(channels["logic_transitivity"], "accepted inferred edge")
        self.assertEqual(channels["directionality"], "blocked reverse inference")
        reverse = _result(payload, "All C are A")
        self.assertEqual(reverse["status"], "rejected")
        self.assertEqual(reverse["source"], "candidate_bridge")
        self.assertTrue(reverse["provenance"]["source"])

    def test_bridge_abstains_when_no_typed_support_exists(self):
        payload = run_tensionlm_candidate_bridge("All A are B. Are all A C?")

        self.assertIn("All A are C", payload["verification"]["abstained"])
        result = _result(payload, "All A are C")
        self.assertEqual(result["status"], "abstained")
        self.assertIn("typed", result["reason"])

    def test_quantifier_scope_rejects_some_to_all_candidate(self):
        payload = run_tensionlm_candidate_bridge(
            "Some pilots are engineers. All engineers are careful. Are all pilots careful?"
        )

        result = _result(payload, "All pilots are careful")
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["channels"]["quantifier_scope"], "blocked some-to-all upgrade")

    def test_external_hook_preserves_candidate_provenance(self):
        proposer = ExternalTensionLMCandidateProposer(
            lambda _text, _premises: [
                {"claim": "All A are C", "source": "external_fixture", "confidence": 0.77}
            ]
        )
        candidates = proposer.propose("All A are B. All B are C. Are all A C?")

        self.assertEqual(candidates[0].source, "external_fixture")
        self.assertEqual(candidates[0].confidence, 0.77)

    def test_payload_is_json_serializable(self):
        payload = run_tensionlm_candidate_bridge("All A are B. All B are C. Are all A C?")

        json.dumps(payload)

    def test_high_confidence_bad_candidate_does_not_override_verifier(self):
        payload = run_tensionlm_candidate_bridge(
            "All A are B. All B are C. Are all A C?",
            mode="external",
            external_hook=lambda _text, _premises: [
                {"candidate_id": "valid", "claim": "All A are C", "source": "fixture", "confidence": 0.21},
                {"candidate_id": "bad", "claim": "All C are A", "source": "fixture", "confidence": 0.99},
            ],
        )

        self.assertEqual(_result(payload, "All A are C")["status"], "accepted")
        bad = _result(payload, "All C are A")
        self.assertEqual(bad["status"], "rejected")
        self.assertGreater(bad["confidence"], _result(payload, "All A are C")["confidence"])
        self.assertEqual(bad["channels"]["directionality"], "blocked reverse inference")

    def test_missing_provenance_and_malformed_claims_are_rejected(self):
        missing = run_tensionlm_candidate_bridge(
            "All A are B. All B are C. Are all A C?",
            mode="external",
            external_hook=lambda _text, _premises: [
                {"candidate_id": "missing", "claim": "All A are C", "source": "", "confidence": 0.93}
            ],
        )
        malformed = run_tensionlm_candidate_bridge(
            "All A are B. All B are C. Are all A C?",
            mode="external",
            external_hook=lambda _text, _premises: [
                {"candidate_id": "malformed", "claim": "A therefore C probably", "source": "fixture"}
            ],
        )

        self.assertEqual(_result(missing, "All A are C")["channels"]["provenance"], "rejected missing candidate source")
        self.assertEqual(
            _result(malformed, "A therefore C probably")["channels"]["malformed_relation"],
            "rejected unparsable graph claim",
        )

    def test_candidate_contradiction_rejected_without_support_contamination(self):
        payload = run_tensionlm_candidate_bridge(
            "All A are B. Are all A B?",
            mode="external",
            external_hook=lambda _text, _premises: [
                {"candidate_id": "supported", "claim": "All A are B", "source": "fixture", "confidence": 0.72},
                {"candidate_id": "contradiction", "claim": "No A are B", "source": "fixture", "confidence": 0.91},
            ],
        )

        self.assertEqual(_result(payload, "All A are B")["status"], "accepted")
        bad = _result(payload, "No A are B")
        self.assertEqual(bad["status"], "rejected")
        self.assertEqual(bad["channels"]["contradiction"], "rejected candidate contradicts premise edge")
        surface_tags = bad["typed_runtime"]["context"]["surface_tags"]
        self.assertNotIn("candidate", set(surface_tags.values()))


def _result(payload, claim):
    for result in payload["verification"]["candidate_results"]:
        if result["claim"] == claim:
            return result
    raise AssertionError(f"missing result for {claim}")


if __name__ == "__main__":
    unittest.main()
