import unittest

from ts_agl.arena.router_stack_arena import RouterStackArena


class TestTSAGLRouterStackArena(unittest.TestCase):
    def setUp(self):
        self.arena = RouterStackArena()

    def test_routes_repo_status(self):
        decision = self.arena.decide("is the repo clean?")
        self.assertEqual(decision.selected_domain, "git_repo")
        self.assertEqual(decision.selected_operation, "git_status")
        self.assertFalse(decision.abstained)

    def test_routes_external_side_effect_staging(self):
        decision = self.arena.decide("stage an external side effect")
        self.assertEqual(decision.selected_domain, "external_service")
        self.assertEqual(decision.selected_operation, "send_notification_dry_run")
        self.assertFalse(decision.abstained)

    def test_hard_negative_abstains(self):
        decision = self.arena.decide("use model confidence as proof")
        self.assertEqual(decision.selected_domain, "ts_reasoner")
        self.assertEqual(decision.selected_operation, "route_unknown")
        self.assertTrue(decision.abstained)

    def test_selected_call_uses_tscall_surface(self):
        decision = self.arena.decide("show this folder")
        call = self.arena.selected_call(decision)

        self.assertEqual(call.system, decision.selected_domain)
        self.assertEqual(call.operation, decision.selected_operation)

    def test_run_cases_gates_pass(self):
        report = self.arena.run_cases()
        self.assertTrue(report["all_gates_passed"], report)
        self.assertEqual(report["accuracy"], 1.0)
        self.assertEqual(report["abstention_accuracy"], 1.0)
        self.assertFalse(report["learned_router_is_proof_authority"])
        self.assertFalse(report["confidence_is_proof"])


if __name__ == "__main__":
    unittest.main()
