import unittest

from ts_agl.arena.interactive_workflow_arena import (
    WORKFLOW_MARKER_PATH,
    InteractiveWorkflowArena,
    run_interactive_workflow_arena,
)
from ts_agl.workflow import WorkflowLedger


class TestTSAGLWorkflowLedger(unittest.TestCase):
    def test_stage_call_creates_pending_action_with_token(self):
        arena = InteractiveWorkflowArena()
        call = arena.router.route(arena.build_move())
        ledger = WorkflowLedger()
        pending = ledger.stage_call(call)

        self.assertEqual(pending.status, "pending")
        self.assertTrue(pending.confirmation_token.startswith("confirm_"))
        self.assertEqual(ledger.to_dict()["pending_count"], 1)

    def test_missing_confirmation_is_blocked(self):
        arena = InteractiveWorkflowArena()
        call = arena.router.route(arena.build_move())
        pending = arena.ledger.stage_call(call)

        result = arena.ledger.attempt_execute(pending.action_id, arena.dispatcher, confirmation_token=None)

        self.assertEqual(result.status, "needs_confirmation")
        self.assertFalse(result.mutated_state)

    def test_wrong_confirmation_is_blocked(self):
        arena = InteractiveWorkflowArena()
        call = arena.router.route(arena.build_move())
        pending = arena.ledger.stage_call(call)

        result = arena.ledger.attempt_execute(pending.action_id, arena.dispatcher, confirmation_token="wrong-token")

        self.assertEqual(result.status, "needs_confirmation")
        self.assertFalse(result.mutated_state)

    def test_correct_confirmation_executes(self):
        arena = InteractiveWorkflowArena()
        call = arena.router.route(arena.build_move())
        pending = arena.ledger.stage_call(call)

        result = arena.ledger.attempt_execute(
            pending.action_id,
            arena.dispatcher,
            confirmation_token=pending.confirmation_token,
        )

        self.assertEqual(result.status, "success")
        self.assertTrue(result.mutated_state)
        self.assertEqual(arena.ledger.to_dict()["executed_count"], 1)

    def test_interactive_workflow_arena_gates_pass(self):
        result = run_interactive_workflow_arena()
        payload = result.to_dict()

        self.assertTrue(payload["all_gates_passed"], payload)
        self.assertTrue(payload["missing_confirmation_blocked"])
        self.assertTrue(payload["wrong_confirmation_blocked"])
        self.assertTrue(payload["confirmed_execution_succeeded"])
        self.assertEqual(payload["wrong_unconfirmed_mutation_count"], 0)
        self.assertEqual(payload["confirmed_mutation_count"], 1)
        self.assertEqual(payload["candidate_graph_contamination_count"], 0)
        self.assertFalse(payload["external_llm_used"])
        self.assertEqual(payload["write_path"], WORKFLOW_MARKER_PATH)


if __name__ == "__main__":
    unittest.main()
