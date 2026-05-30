import tempfile
import unittest
from pathlib import Path

from ts_reasoner.ts_chat_suggestion_confirmation import (
    VERSION,
    confirm_suggestions_demo_cases,
    evaluate_suggestion_confirmations,
    load_confirmations_jsonl,
    write_confirmations_jsonl,
)


class TestTSChatSuggestionConfirmation(unittest.TestCase):
    def _suggestions(self):
        return [
            {
                "suggestion_id": "suggestion_001_repair_missing_support_001",
                "curriculum_entry_id": "curriculum_001_repair_missing_support_001",
                "repair_target_id": "repair_missing_support_001",
                "repair_type": "missing_support",
                "source_turn_id": "turn_001",
                "original_user_text": "are all sparks lanterns?",
                "suggested_text": "Provide typed premises that support: All sparks are lanterns",
                "suggestion_status": "suggested_not_accepted",
            },
            {
                "suggestion_id": "suggestion_002_repair_parse_failure_001",
                "curriculum_entry_id": "curriculum_002_repair_parse_failure_001",
                "repair_target_id": "repair_parse_failure_001",
                "repair_type": "parse_failure",
                "source_turn_id": "turn_002",
                "original_user_text": "sparks kinda lantern-vibe sideways??",
                "suggested_text": "Did you mean: All sparks are lantern?",
                "suggestion_status": "suggested_not_accepted",
            },
        ]

    def _confirmations(self):
        return confirm_suggestions_demo_cases(self._suggestions())

    def test_confirmation_schema(self):
        row = self._confirmations()[0].to_dict()
        required = {
            "confirmation_id",
            "suggestion_id",
            "curriculum_entry_id",
            "repair_target_id",
            "source_turn_id",
            "repair_type",
            "original_user_text",
            "suggested_text",
            "confirmation_status",
            "candidate_claim_text",
            "verifier_status",
            "accepted_as_proof",
            "created_by_version",
            "verifier_boundary_note",
        }
        self.assertTrue(required.issubset(row.keys()))
        self.assertEqual(row["created_by_version"], VERSION)

    def test_confirmation_creates_candidate_not_automatic_proof(self):
        rows = [c.to_dict() for c in self._confirmations()]
        rejected = [r for r in rows if r["verifier_status"] == "verifier_rejected"]
        self.assertGreater(len(rejected), 0)
        self.assertTrue(all(r["accepted_as_proof"] is False for r in rejected))

    def test_accepted_requires_verifier_support(self):
        rows = [c.to_dict() for c in self._confirmations()]
        accepted = [r for r in rows if r["verifier_status"] == "verifier_accepted"]
        self.assertEqual(len(accepted), 1)
        self.assertTrue(accepted[0]["accepted_as_proof"])

    def test_export_and_load_jsonl(self):
        confirmations = self._confirmations()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "confirmations.jsonl"
            write_confirmations_jsonl(confirmations, path)
            loaded = load_confirmations_jsonl(path)
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]["created_by_version"], VERSION)

    def test_evaluation_gates_pass(self):
        rows = [c.to_dict() for c in self._confirmations()]
        metrics = evaluate_suggestion_confirmations(rows)
        self.assertTrue(metrics["all_gates_passed"])
        self.assertTrue(metrics["user_confirmation_is_not_proof"])
        self.assertEqual(metrics["candidate_graph_contamination_count"], 0)


if __name__ == "__main__":
    unittest.main()
