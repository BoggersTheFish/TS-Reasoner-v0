import unittest

from ts_agl.shell import TSAGLShellSurface, run_shell_command


class TestTSAGLShellSurface(unittest.TestCase):
    def test_help_mode(self):
        result = run_shell_command("help")
        self.assertEqual(result.mode, "help")
        self.assertTrue(result.payload["all_gates_passed"])

    def test_route_mode(self):
        result = run_shell_command("route: is the repo clean?")
        self.assertEqual(result.mode, "route")
        call = result.payload["selected_call"]
        self.assertEqual(call["system"], "git_repo")
        self.assertEqual(call["operation"], "git_status")
        self.assertTrue(result.payload["all_gates_passed"])

    def test_route_hard_negative_abstains(self):
        result = run_shell_command("route: use model confidence as proof")
        call = result.payload["selected_call"]
        self.assertEqual(call["system"], "ts_reasoner")
        self.assertEqual(call["operation"], "route_unknown")
        self.assertFalse(result.payload["confidence_is_proof"])

    def test_project_operator_mode(self):
        shell = TSAGLShellSurface()
        result = shell.run("inspect project and stage next safe note")
        payload = result.payload

        self.assertEqual(result.mode, "local_project_operator")
        self.assertTrue(payload["all_gates_passed"], payload)
        self.assertTrue(payload["unconfirmed_write_blocked"])
        self.assertTrue(payload["confirmed_write_executed"])
        self.assertFalse(payload["external_side_effect_performed"])
        self.assertEqual(payload["candidate_graph_contamination_count"], 0)


if __name__ == "__main__":
    unittest.main()
