import unittest

from ts_agl.parser import parse_language_moves
from ts_agl.registry import DomainRegistry
from ts_agl.router import OperationRouter


class TestTSAGLRouting(unittest.TestCase):
    def setUp(self):
        self.registry = DomainRegistry().load()
        self.router = OperationRouter(self.registry)

    def _assert_route(self, text, expected_system, expected_operation):
        moves = parse_language_moves(text)
        calls = self.router.route_many(moves)
        pairs = {(c.system, c.operation) for c in calls}
        self.assertIn((expected_system, expected_operation), pairs)

    def test_repo_status_routes(self):
        self._assert_route("check if the repo is clean", "git_repo", "git_status")

    def test_current_tag_routes(self):
        self._assert_route("what version are we on?", "git_repo", "current_tag")

    def test_next_safe_action_routes(self):
        self._assert_route("tell me the next safe action", "git_repo", "next_safe_release_action")

    def test_support_missing_slot(self):
        moves = parse_language_moves("does that follow?")
        calls = self.router.route_many(moves)
        support_calls = [c for c in calls if c.operation == "check_support"]
        self.assertEqual(len(support_calls), 1)
        self.assertEqual(support_calls[0].missing_slots, ["claim"])

    def test_support_with_claim(self):
        moves = parse_language_moves("can we prove A implies C")
        calls = self.router.route_many(moves)
        support_calls = [c for c in calls if c.operation == "check_support"]
        self.assertEqual(len(support_calls), 1)
        self.assertEqual(support_calls[0].missing_slots, [])
        self.assertIn("claim", support_calls[0].args)

    def test_rejection_explanation_routes(self):
        self._assert_route("why did you reject it?", "ts_reasoner", "explain_rejection")

    def test_summary_routes(self):
        self._assert_route("what do we know so far?", "ts_reasoner", "summarize_session")


if __name__ == "__main__":
    unittest.main()
