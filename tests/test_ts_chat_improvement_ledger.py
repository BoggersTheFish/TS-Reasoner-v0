import json
import tempfile
import unittest
from pathlib import Path

from ts_reasoner.ts_chat_improvement_ledger import (
    VERSION,
    build_improvement_ledger,
    evaluate_improvement_ledger,
    load_improvement_ledger,
    write_improvement_ledger,
)


class TestTSChatImprovementLedger(unittest.TestCase):
    def _write_jsonl(self, path, rows):
        with Path(path).open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, sort_keys=True) + "\n")

    def _fixture_paths(self, tmp):
        curriculum_path = Path(tmp) / "curriculum.jsonl"
        suggestions_path = Path(tmp) / "suggestions.jsonl"
        confirmations_path = Path(tmp) / "confirmations.jsonl"

        self._write_jsonl(curriculum_path, [
            {
                "curriculum_entry_id": "curriculum_001",
                "repair_target_id": "repair_001",
                "repair_type": "missing_support",
                "expected_resolution_status": "resolved",
            },
            {
                "curriculum_entry_id": "curriculum_002",
                "repair_target_id": "repair_002",
                "repair_type": "parse_failure",
                "expected_resolution_status": "open",
            },
        ])

        self._write_jsonl(suggestions_path, [
            {
                "suggestion_id": "suggestion_001",
                "curriculum_entry_id": "curriculum_001",
                "repair_target_id": "repair_001",
                "repair_type": "missing_support",
            },
            {
                "suggestion_id": "suggestion_002",
                "curriculum_entry_id": "curriculum_002",
                "repair_target_id": "repair_002",
                "repair_type": "parse_failure",
            },
        ])

        self._write_jsonl(confirmations_path, [
            {
                "confirmation_id": "confirmation_001",
                "suggestion_id": "suggestion_001",
                "confirmation_status": "user_confirmed_candidate",
                "verifier_status": "verifier_accepted",
                "accepted_as_proof": True,
            },
            {
                "confirmation_id": "confirmation_002",
                "suggestion_id": "suggestion_002",
                "confirmation_status": "user_confirmed_candidate",
                "verifier_status": "verifier_rejected",
                "accepted_as_proof": False,
            },
        ])

        return curriculum_path, suggestions_path, confirmations_path

    def test_ledger_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._fixture_paths(tmp)
            ledger = build_improvement_ledger(
                curriculum_path=paths[0],
                suggestions_path=paths[1],
                confirmations_path=paths[2],
            ).to_dict()

        required = {
            "ledger_id",
            "created_by_version",
            "curriculum_entry_count",
            "repair_suggestion_count",
            "confirmation_count",
            "confirmed_candidate_count",
            "verifier_accepted_count",
            "verifier_rejected_count",
            "open_repair_count",
            "resolved_repair_count",
            "measurable_loop_coverage_rate",
            "accepted_confirmation_rate",
            "zero_candidate_graph_contamination",
            "improvement_summary",
            "verifier_boundary_note",
        }
        self.assertTrue(required.issubset(ledger.keys()))
        self.assertEqual(ledger["created_by_version"], VERSION)

    def test_ledger_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._fixture_paths(tmp)
            ledger = build_improvement_ledger(
                curriculum_path=paths[0],
                suggestions_path=paths[1],
                confirmations_path=paths[2],
            ).to_dict()

        self.assertEqual(ledger["curriculum_entry_count"], 2)
        self.assertEqual(ledger["repair_suggestion_count"], 2)
        self.assertEqual(ledger["confirmation_count"], 2)
        self.assertEqual(ledger["verifier_accepted_count"], 1)
        self.assertEqual(ledger["verifier_rejected_count"], 1)
        self.assertEqual(ledger["measurable_loop_coverage_rate"], 1.0)
        self.assertEqual(ledger["accepted_confirmation_rate"], 0.5)

    def test_write_and_load_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._fixture_paths(tmp)
            ledger = build_improvement_ledger(
                curriculum_path=paths[0],
                suggestions_path=paths[1],
                confirmations_path=paths[2],
            )
            output_path = Path(tmp) / "ledger.json"
            write_improvement_ledger(ledger, output_path)
            loaded = load_improvement_ledger(output_path)

        self.assertEqual(loaded["created_by_version"], VERSION)
        self.assertEqual(loaded["confirmation_count"], 2)

    def test_evaluation_gates_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._fixture_paths(tmp)
            ledger = build_improvement_ledger(
                curriculum_path=paths[0],
                suggestions_path=paths[1],
                confirmations_path=paths[2],
            ).to_dict()

        metrics = evaluate_improvement_ledger(ledger)
        self.assertTrue(metrics["all_gates_passed"])
        self.assertTrue(metrics["zero_candidate_graph_contamination"])
        self.assertEqual(metrics["measurable_loop_coverage_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
