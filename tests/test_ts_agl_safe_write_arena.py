import unittest
from pathlib import Path

from ts_agl.arena.safe_write_arena import SAFE_WRITE_PATH, SafeWriteArena, run_safe_write_arena


class TestTSAGLSafeWriteArena(unittest.TestCase):
    def test_safe_write_call_is_reversible_and_requires_confirmation(self):
        arena = SafeWriteArena()
        move = arena.build_move()
        call = arena.router.route(move)

        self.assertEqual(call.system, "filesystem")
        self.assertEqual(call.operation, "write_text_file")
        self.assertEqual(call.risk, "reversible_write")
        self.assertTrue(call.requires_confirmation)
        self.assertEqual(call.missing_slots, [])

    def test_unconfirmed_write_is_blocked(self):
        arena = SafeWriteArena()
        call = arena.router.route(arena.build_move())
        result = arena.dispatcher.dispatch(call, confirmed=False)

        self.assertEqual(result.status, "needs_confirmation")
        self.assertFalse(result.mutated_state)

    def test_confirmed_write_executes_inside_artifacts(self):
        result = run_safe_write_arena()
        payload = result.to_dict()

        self.assertTrue(payload["all_gates_passed"], payload)
        self.assertTrue(payload["unconfirmed_blocked"])
        self.assertTrue(payload["confirmed_executed"])
        self.assertEqual(payload["wrong_unconfirmed_mutation_count"], 0)
        self.assertEqual(payload["confirmed_mutation_count"], 1)
        self.assertTrue(Path(SAFE_WRITE_PATH).exists())

    def test_adapter_refuses_write_outside_artifacts(self):
        arena = SafeWriteArena()
        move = arena.build_move()
        move = type(move)(
            move_type=move.move_type,
            raw_text=move.raw_text,
            target="../bad.txt",
            slots={"path": "../bad.txt", "content": "bad"},
            operation_hint=move.operation_hint,
            domain_hint=move.domain_hint,
            confidence=move.confidence,
        )
        call = arena.router.route(move)
        result = arena.dispatcher.dispatch(call, confirmed=True)

        self.assertEqual(result.status, "failed")
        self.assertIn("Refusing to write outside artifacts", result.error)


if __name__ == "__main__":
    unittest.main()
