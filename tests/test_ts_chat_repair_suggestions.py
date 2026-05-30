import tempfile
import unittest
from pathlib import Path

from ts_reasoner.ts_chat_repair_suggestions import (
    VERSION,
    evaluate_repair_suggestions,
    load_suggestions_jsonl,
    suggestions_from_curriculum_entries,
    write_suggestions_jsonl,
)


class TestTSChatRepairSuggestions(unittest.TestCase):
    def _curriculum_entries(self):
        return [
            {
                "curriculum_entry_id": "curriculum_001_repair_missing_support_001",
                "source_session_id": "session_test",
                "source_turn_id": "turn_001",
                "repair_target_id": "repair_missing_support_001",
                "repair_type": "missing_support",
                "original_user_text": "are all sparks lanterns?",
                "target_claim_text": "All sparks are lanterns",
                "target_parse_text": None,
                "expected_status": "repair_target",
                "expected_resolution_status": "resolved",
                "created_by_version": "ts_chat_v0.6",
                "verifier_boundary_note": "Curriculum entries are not proof.",
            },
            {
                "curriculum_entry_id": "curriculum_002_repair_parse_failure_001",
                "source_session_id": "session_test",
                "source_turn_id": "turn_002",
                "repair_target_id": "repair_parse_failure_001",
                "repair_type": "parse_failure",
                "original_user_text": "sparks kinda lantern-vibe sideways??",
                "target_claim_text": None,
                "target_parse_text": "sparks kinda lantern-vibe sideways??",
                "expected_status": "repair_target",
                "expected_resolution_status": "open",
                "created_by_version": "ts_chat_v0.6",
                "verifier_boundary_note": "Curriculum entries are not proof.",
            },
        ]

    def _suggestions(self):
        return suggestions_from_curriculum_entries(self._curriculum_entries())

    def test_suggestion_schema(self):
        row = self._suggestions()[0].to_dict()
        required = {
            "suggestion_id",
            "curriculum_entry_id",
            "repair_target_id",
            "repair_type",
            "source_turn_id",
            "original_user_text",
            "suggested_text",
            "suggestion_status",
            "suggestion_rule_id",
            "created_by_version",
            "verifier_boundary_note",
        }
        self.assertTrue(required.issubset(row.keys()))
        self.assertEqual(row["created_by_version"], VERSION)

    def test_parse_failure_gets_bounded_suggestion(self):
        rows = [s.to_dict() for s in self._suggestions()]
        parse_rows = [r for r in rows if r["repair_type"] == "parse_failure"]
        self.assertEqual(len(parse_rows), 1)
        self.assertIn("Did you mean: All sparks are lantern", parse_rows[0]["suggested_text"])
        self.assertEqual(parse_rows[0]["suggestion_status"], "suggested_not_accepted")

    def test_missing_support_gets_premise_request(self):
        rows = [s.to_dict() for s in self._suggestions()]
        support_rows = [r for r in rows if r["repair_type"] == "missing_support"]
        self.assertEqual(len(support_rows), 1)
        self.assertIn("Provide typed premises", support_rows[0]["suggested_text"])
        self.assertEqual(support_rows[0]["suggestion_status"], "suggested_not_accepted")

    def test_export_and_load_jsonl(self):
        suggestions = self._suggestions()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "suggestions.jsonl"
            write_suggestions_jsonl(suggestions, path)
            loaded = load_suggestions_jsonl(path)
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]["created_by_version"], VERSION)

    def test_evaluation_gates_pass(self):
        rows = [s.to_dict() for s in self._suggestions()]
        metrics = evaluate_repair_suggestions(rows)
        self.assertTrue(metrics["all_gates_passed"])
        self.assertEqual(metrics["accepted_without_confirmation_count"], 0)
        self.assertEqual(metrics["candidate_graph_contamination_count"], 0)


if __name__ == "__main__":
    unittest.main()
