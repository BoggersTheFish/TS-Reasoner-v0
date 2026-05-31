import unittest

from ts_agl.arena.external_side_effect_arena import (
    ExternalSideEffectArena,
    run_external_side_effect_arena,
)


class TestTSAGLExternalSideEffectArena(unittest.TestCase):
    def test_call_is_external_side_effect_and_requires_confirmation(self):
        arena = ExternalSideEffectArena()
        call = arena.router.route(arena.build_move())

        self.assertEqual(call.system, "external_service")
        self.assertEqual(call.operation, "send_notification_dry_run")
        self.assertEqual(call.risk, "external_side_effect")
        self.assertTrue(call.requires_confirmation)
        self.assertEqual(call.missing_slots, [])

    def test_missing_confirmation_is_blocked(self):
        arena = ExternalSideEffectArena()
        call = arena.router.route(arena.build_move())
        pending = arena.ledger.stage_call(call)

        result = arena.ledger.attempt_execute(pending.action_id, arena.dispatcher, confirmation_token=None)

        self.assertEqual(result.status, "needs_confirmation")
        self.assertFalse(result.mutated_state)

    def test_wrong_confirmation_is_blocked(self):
        arena = ExternalSideEffectArena()
        call = arena.router.route(arena.build_move())
        pending = arena.ledger.stage_call(call)

        result = arena.ledger.attempt_execute(pending.action_id, arena.dispatcher, confirmation_token="wrong-token")

        self.assertEqual(result.status, "needs_confirmation")
        self.assertFalse(result.mutated_state)

    def test_confirmed_dry_run_executes_without_network(self):
        arena = ExternalSideEffectArena()
        call = arena.router.route(arena.build_move())
        pending = arena.ledger.stage_call(call)

        result = arena.ledger.attempt_execute(
            pending.action_id,
            arena.dispatcher,
            confirmation_token=pending.confirmation_token,
        )

        self.assertEqual(result.status, "success")
        self.assertFalse(result.mutated_state)
        self.assertTrue(result.data["external_side_effect_declared"])
        self.assertTrue(result.data["dry_run"])
        self.assertFalse(result.data["network_call_performed"])

    def test_external_side_effect_arena_gates_pass(self):
        result = run_external_side_effect_arena()
        payload = result.to_dict()

        self.assertTrue(payload["all_gates_passed"], payload)
        self.assertTrue(payload["missing_confirmation_blocked"])
        self.assertTrue(payload["wrong_confirmation_blocked"])
        self.assertTrue(payload["confirmed_execution_succeeded"])
        self.assertTrue(payload["external_side_effect_declared"])
        self.assertTrue(payload["dry_run"])
        self.assertFalse(payload["network_call_performed"])
        self.assertEqual(payload["wrong_unconfirmed_mutation_count"], 0)
        self.assertEqual(payload["confirmed_mutation_count"], 0)
        self.assertEqual(payload["candidate_graph_contamination_count"], 0)
        self.assertFalse(payload["external_llm_used"])


if __name__ == "__main__":
    unittest.main()
