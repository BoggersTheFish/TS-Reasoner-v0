import unittest

from ts_agl.os.ts_os_v1 import TSOSV1, run_ts_os_v1


class TestTSOSV1(unittest.TestCase):
    def test_ts_os_v1_gates_pass(self):
        payload = run_ts_os_v1().to_dict()

        self.assertTrue(payload["all_gates_passed"], payload)
        self.assertEqual(payload["network_call_performed_count"], 0)
        self.assertEqual(payload["external_side_effect_performed_count"], 0)
        self.assertFalse(payload["external_llm_used"])
        self.assertEqual(payload["candidate_graph_contamination_count"], 0)

    def test_shell_and_router_components_present(self):
        payload = TSOSV1().run().to_dict()
        components = payload["components"]

        self.assertIn("shell_surface", components)
        self.assertIn("shell_route", components)
        self.assertIn("router_stack", components)
        self.assertTrue(components["router_stack"]["all_gates_passed"])

    def test_session_and_project_components_present(self):
        payload = TSOSV1().run().to_dict()
        components = payload["components"]

        self.assertTrue(components["session_summary"]["all_gates_passed"])
        self.assertTrue(components["local_project_operator"]["all_gates_passed"])

    def test_external_gate_component_is_bounded(self):
        payload = TSOSV1().run().to_dict()
        external_gate = payload["components"]["external_adapter_gate"]

        self.assertTrue(external_gate["all_gates_passed"])
        self.assertTrue(external_gate["missing_confirmation_blocked"])
        self.assertTrue(external_gate["dry_run_confirmed"])
        self.assertTrue(external_gate["live_without_env_blocked"])
        self.assertTrue(external_gate["live_with_env_authorized"])
        self.assertFalse(external_gate["live_gate_authorization_is_execution"])
        self.assertEqual(external_gate["network_call_performed_count"], 0)
        self.assertEqual(external_gate["external_side_effect_performed_count"], 0)


if __name__ == "__main__":
    unittest.main()
