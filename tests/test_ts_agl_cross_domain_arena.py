import unittest

from ts_agl.arena.cross_domain_arena import (
    CrossDomainArena,
    run_cross_domain_arena,
    summarize_cross_domain_trace,
)


class TestTSAGLCrossDomainArena(unittest.TestCase):
    def test_plan_covers_three_domains(self):
        arena = CrossDomainArena()
        steps = arena.plan()
        domains = {step.move.domain_hint for step in steps}
        self.assertIn("git_repo", domains)
        self.assertIn("filesystem", domains)
        self.assertIn("ts_reasoner", domains)

    def test_run_cross_domain_arena_gates_pass(self):
        trace = run_cross_domain_arena()
        summary = summarize_cross_domain_trace(trace)
        self.assertTrue(summary["all_gates_passed"], summary)
        self.assertGreaterEqual(summary["domain_count"], 3)
        self.assertEqual(summary["wrong_state_mutation_count"], 0)
        self.assertEqual(summary["candidate_graph_contamination_count"], 0)
        self.assertFalse(summary["external_llm_used"])

    def test_cross_domain_operations_present(self):
        trace = run_cross_domain_arena()
        operations = {f"{call.system}.{call.operation}" for call in trace.calls}
        self.assertIn("git_repo.git_status", operations)
        self.assertIn("git_repo.current_tag", operations)
        self.assertIn("filesystem.list_files", operations)
        self.assertIn("ts_reasoner.summarize_session", operations)
        self.assertIn("git_repo.next_safe_release_action", operations)

    def test_all_calls_are_read_only(self):
        trace = run_cross_domain_arena()
        self.assertTrue(all(call.risk == "read_only" for call in trace.calls))


if __name__ == "__main__":
    unittest.main()
