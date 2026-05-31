import unittest

from ts_agl.core.types import AGLTrace, LanguageMove, ResultPacket, TSCall


class TestTSAGLCore(unittest.TestCase):
    def test_language_move_to_dict(self):
        move = LanguageMove(move_type="INSPECT", raw_text="check repo", operation_hint="git_status")
        data = move.to_dict()
        self.assertEqual(data["move_type"], "INSPECT")
        self.assertEqual(data["operation_hint"], "git_status")

    def test_tscall_gets_stable_id(self):
        call = TSCall(system="git_repo", operation="git_status")
        self.assertTrue(call.call_id.startswith("call_"))

    def test_trace_gates_pass_for_read_only(self):
        move = LanguageMove(move_type="INSPECT", raw_text="check repo")
        call = TSCall(system="git_repo", operation="git_status", source_move=move.to_dict())
        result = ResultPacket(status="success", system="git_repo", operation="git_status", mutated_state=False)
        trace = AGLTrace(
            raw_text="check repo",
            moves=[move],
            calls=[call],
            results=[result],
            rendered_reply="Repo is clean.",
        )
        data = trace.to_dict()
        self.assertTrue(data["all_gates_passed"])
        self.assertFalse(data["external_llm_used"])


if __name__ == "__main__":
    unittest.main()
