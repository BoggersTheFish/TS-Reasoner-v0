import json
import tempfile
import unittest
from pathlib import Path

from ts_chat.session_arena import (
    arena_report_valid,
    default_arena_cases,
    evaluate_session_arena,
)


class TestTSChatSessionArena(unittest.TestCase):
    def test_default_arena_cases(self):
        cases = default_arena_cases()

        self.assertEqual(len(cases), 10)
        self.assertEqual(cases[0]["case_id"], "persistence_roundtrip")
        self.assertTrue(any(case["case_id"] == "knowledge_pack_roundtrip" for case in cases))

    def test_evaluate_session_arena(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = evaluate_session_arena(Path(tmp))

            self.assertEqual(report["schema"], "ts_chat_session_arena_v1")
            self.assertEqual(report["release"], "v6.8.0")
            self.assertEqual(report["case_count"], 10)
            self.assertEqual(report["passed_count"], 10)
            self.assertEqual(report["failed_count"], 0)
            self.assertEqual(report["pass_rate"], 1.0)
            self.assertEqual(report["answer_accuracy"], 1.0)
            self.assertEqual(report["status_accuracy"], 1.0)
            self.assertEqual(report["repair_target_accuracy"], 1.0)
            self.assertEqual(report["explanation_trace_validity"], 1.0)
            self.assertEqual(report["contradiction_detection_rate"], 1.0)
            self.assertEqual(report["provenance_validity"], 1.0)
            self.assertEqual(report["knowledge_pack_roundtrip_validity"], 1.0)
            self.assertEqual(report["candidate_graph_contamination_count"], 0)
            self.assertTrue(report["all_gates_passed"])
            self.assertTrue(arena_report_valid(report))

    def test_arena_writes_roundtrip_artifacts_in_workdir(self):
        with tempfile.TemporaryDirectory() as tmp:
            work_dir = Path(tmp)
            report = evaluate_session_arena(work_dir)

            self.assertTrue((work_dir / "arena_session.json").exists())
            self.assertTrue((work_dir / "arena_knowledge_pack.json").exists())
            self.assertTrue((work_dir / "arena_imported_session.json").exists())
            self.assertTrue(arena_report_valid(report))

    def test_each_result_has_required_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = evaluate_session_arena(Path(tmp))

            for result in report["results"]:
                self.assertIn("case_id", result)
                self.assertIn("category", result)
                self.assertIn("passed", result)
                self.assertIn("expected", result)
                self.assertIn("observed", result)
                self.assertIn("details", result)
                self.assertTrue(result["passed"])

    def test_arena_report_invalid_if_contaminated(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = evaluate_session_arena(Path(tmp))
            report["candidate_graph_contamination_count"] = 1

            self.assertFalse(arena_report_valid(report))

    def test_arena_dataset_file_exists_and_matches_case_count(self):
        path = Path("data/ts_chat_session_arena_v68.jsonl")
        self.assertTrue(path.exists())

        rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        self.assertEqual(len(rows), 10)
        self.assertEqual(rows[0]["case_id"], "persistence_roundtrip")


if __name__ == "__main__":
    unittest.main()
