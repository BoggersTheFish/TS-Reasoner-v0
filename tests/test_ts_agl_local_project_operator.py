import unittest
from pathlib import Path

from ts_agl.arena.local_project_operator import (
    PROJECT_OPERATOR_NOTE_PATH,
    LocalProjectOperator,
    run_local_project_operator,
)


class TestTSAGLLocalProjectOperator(unittest.TestCase):
    def test_operator_builds_inspection_moves(self):
        operator = LocalProjectOperator()
        moves = operator.build_inspection_moves("inspect project")
        hints = {(move.domain_hint, move.operation_hint) for move in moves}

        self.assertIn(("git_repo", "git_status"), hints)
        self.assertIn(("git_repo", "current_tag"), hints)
        self.assertIn(("filesystem", "list_files"), hints)

    def test_safe_note_requires_confirmation(self):
        operator = LocalProjectOperator()
        move = operator.build_safe_note_move("stage note")
        call = operator.router.route(move)

        self.assertEqual(call.system, "filesystem")
        self.assertEqual(call.operation, "write_text_file")
        self.assertEqual(call.risk, "reversible_write")
        self.assertTrue(call.requires_confirmation)

    def test_project_operator_gates_pass(self):
        result = run_local_project_operator()
        payload = result.to_dict()

        self.assertTrue(payload["all_gates_passed"], payload)
        self.assertTrue(payload["repo_inspected"])
        self.assertTrue(payload["filesystem_inspected"])
        self.assertTrue(payload["router_stack_used"])
        self.assertTrue(payload["unconfirmed_write_blocked"])
        self.assertTrue(payload["confirmed_write_executed"])
        self.assertFalse(payload["external_side_effect_performed"])
        self.assertFalse(payload["external_llm_used"])
        self.assertEqual(payload["candidate_graph_contamination_count"], 0)
        self.assertTrue(Path(PROJECT_OPERATOR_NOTE_PATH).exists())

    def test_project_operator_uses_expected_operations(self):
        payload = run_local_project_operator().to_dict()
        operations = set(payload["operations"])

        self.assertIn("git_repo.git_status", operations)
        self.assertIn("git_repo.current_tag", operations)
        self.assertIn("filesystem.list_files", operations)
        self.assertIn("filesystem.write_text_file", operations)


if __name__ == "__main__":
    unittest.main()
