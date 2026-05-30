import json
import tempfile
import unittest
from pathlib import Path

from ts_reasoner.ts_chat_closed_repair_loop import (
    VERSION,
    evaluate_closed_repair_loop_receipt,
    load_closed_repair_loop_receipt,
    run_closed_repair_loop,
    write_closed_repair_loop_receipt,
)


class TestTSChatClosedRepairLoop(unittest.TestCase):
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
                "expected_resolution_status": "open",
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

    def test_closed_loop_receipt_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._fixture_paths(tmp)
            receipt = run_closed_repair_loop(
                curriculum_path=paths[0],
                suggestions_path=paths[1],
                confirmations_path=paths[2],
            ).to_dict()

        required = {
            "release",
            "name",
            "created_by_version",
            "case_count",
            "initial_open_repairs",
            "final_open_repairs",
            "repairs_closed_this_run",
            "accepted_with_verifier_support",
            "rejected_without_contamination",
            "ledger_updated",
            "zero_candidate_graph_contamination",
            "improvement_detected",
            "all_gates_passed",
            "boundary",
            "cases",
        }
        self.assertTrue(required.issubset(receipt.keys()))
        self.assertEqual(receipt["created_by_version"], VERSION)

    def test_closed_loop_improves_open_repairs(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._fixture_paths(tmp)
            receipt = run_closed_repair_loop(
                curriculum_path=paths[0],
                suggestions_path=paths[1],
                confirmations_path=paths[2],
            ).to_dict()

        self.assertEqual(receipt["initial_open_repairs"], 2)
        self.assertEqual(receipt["final_open_repairs"], 1)
        self.assertEqual(receipt["repairs_closed_this_run"], 1)
        self.assertTrue(receipt["improvement_detected"])

    def test_rejected_candidate_does_not_contaminate_graph(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._fixture_paths(tmp)
            receipt = run_closed_repair_loop(
                curriculum_path=paths[0],
                suggestions_path=paths[1],
                confirmations_path=paths[2],
            ).to_dict()

        self.assertEqual(receipt["rejected_without_contamination"], 1)
        self.assertTrue(receipt["zero_candidate_graph_contamination"])

    def test_write_and_load_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._fixture_paths(tmp)
            receipt = run_closed_repair_loop(
                curriculum_path=paths[0],
                suggestions_path=paths[1],
                confirmations_path=paths[2],
            )
            output = Path(tmp) / "closed_loop_receipt.json"
            write_closed_repair_loop_receipt(receipt, output)
            loaded = load_closed_repair_loop_receipt(output)

        self.assertEqual(loaded["created_by_version"], VERSION)
        self.assertEqual(loaded["case_count"], 2)

    def test_evaluation_gates_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._fixture_paths(tmp)
            receipt = run_closed_repair_loop(
                curriculum_path=paths[0],
                suggestions_path=paths[1],
                confirmations_path=paths[2],
            ).to_dict()

        metrics = evaluate_closed_repair_loop_receipt(receipt)
        self.assertTrue(metrics["all_gates_passed"])
        self.assertEqual(metrics["initial_open_repairs"], 2)
        self.assertEqual(metrics["final_open_repairs"], 1)
        self.assertTrue(metrics["zero_candidate_graph_contamination"])


if __name__ == "__main__":
    unittest.main()
