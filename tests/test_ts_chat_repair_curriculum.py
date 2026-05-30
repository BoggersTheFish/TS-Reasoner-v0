import tempfile
import unittest
from pathlib import Path

from ts_reasoner.ts_chat_repair_curriculum import (
    VERSION,
    evaluate_curriculum_entries,
    load_curriculum_jsonl,
    repair_targets_to_curriculum_entries,
    write_curriculum_jsonl,
)


class TestTSChatRepairCurriculum(unittest.TestCase):
    def _entries(self):
        repairs = [
            {
                "repair_target_id": "repair_missing_support_001",
                "source_turn_id": "turn_001",
                "repair_type": "missing_support",
                "original_user_text": "are all sparks lanterns?",
                "target_claim_text": "All sparks are lanterns",
                "status": "resolved",
            },
            {
                "repair_target_id": "repair_parse_failure_001",
                "source_turn_id": "turn_002",
                "repair_type": "parse_failure",
                "original_user_text": "sparks kinda lantern-vibe sideways??",
                "target_parse_text": "sparks kinda lantern-vibe sideways??",
                "status": "open",
            },
        ]
        return repair_targets_to_curriculum_entries(
            session_id="session_test",
            repair_targets=repairs,
            turn_text_by_id={},
        )

    def test_curriculum_entry_schema(self):
        entry = self._entries()[0].to_dict()
        required = {
            "curriculum_entry_id",
            "source_session_id",
            "source_turn_id",
            "repair_target_id",
            "repair_type",
            "original_user_text",
            "target_claim_text",
            "target_parse_text",
            "expected_status",
            "expected_resolution_status",
            "created_by_version",
            "verifier_boundary_note",
        }
        self.assertTrue(required.issubset(entry.keys()))
        self.assertEqual(entry["created_by_version"], VERSION)

    def test_export_and_load_jsonl(self):
        entries = self._entries()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "curriculum.jsonl"
            write_curriculum_jsonl(entries, path)
            loaded = load_curriculum_jsonl(path)
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]["repair_type"], "missing_support")

    def test_evaluation_gates_pass(self):
        entries = [entry.to_dict() for entry in self._entries()]
        metrics = evaluate_curriculum_entries(entries)
        self.assertTrue(metrics["all_gates_passed"])
        self.assertEqual(metrics["source_turn_link_rate"], 1.0)
        self.assertEqual(metrics["repair_target_link_rate"], 1.0)

    def test_missing_support_does_not_become_proof(self):
        entries = [entry.to_dict() for entry in self._entries()]
        metrics = evaluate_curriculum_entries(entries)
        self.assertTrue(metrics["unsupported_claims_do_not_become_proof"])

    def test_parse_failure_remains_repairable(self):
        entries = [entry.to_dict() for entry in self._entries()]
        metrics = evaluate_curriculum_entries(entries)
        self.assertTrue(metrics["parse_failures_remain_repairable"])

    def test_no_candidate_graph_contamination(self):
        entries = [entry.to_dict() for entry in self._entries()]
        metrics = evaluate_curriculum_entries(entries)
        self.assertEqual(metrics["candidate_graph_contamination_count"], 0)


if __name__ == "__main__":
    unittest.main()
