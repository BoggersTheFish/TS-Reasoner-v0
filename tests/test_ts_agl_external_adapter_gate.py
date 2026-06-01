import os
import unittest

from ts_agl.external import EXTERNAL_LIVE_ENV_VAR, ExternalAdapterGate, ExternalAdapterRequest


class TestExternalAdapterGate(unittest.TestCase):
    def setUp(self):
        self.old_env = os.environ.pop(EXTERNAL_LIVE_ENV_VAR, None)
        self.gate = ExternalAdapterGate()
        self.request = ExternalAdapterRequest(
            service="github",
            operation="create_issue",
            payload={"repo": "BoggersTheFish/TS-Reasoner-v0", "title": "test"},
            mode="dry_run",
        )

    def tearDown(self):
        if self.old_env is None:
            os.environ.pop(EXTERNAL_LIVE_ENV_VAR, None)
        else:
            os.environ[EXTERNAL_LIVE_ENV_VAR] = self.old_env

    def test_missing_confirmation_is_blocked(self):
        result = self.gate.evaluate(self.request, confirmation_token=None)
        self.assertEqual(result.status, "needs_confirmation")
        self.assertFalse(result.mutated_state)
        self.assertFalse(result.data["network_call_performed"])

    def test_wrong_confirmation_is_blocked(self):
        result = self.gate.evaluate(self.request, confirmation_token="wrong-token")
        self.assertEqual(result.status, "needs_confirmation")
        self.assertFalse(result.mutated_state)
        self.assertFalse(result.data["external_side_effect_performed"])

    def test_dry_run_confirmed_performs_no_network_call(self):
        result = self.gate.evaluate(self.request, confirmation_token=self.request.confirmation_token)
        self.assertEqual(result.status, "success")
        self.assertTrue(result.data["dry_run"])
        self.assertFalse(result.data["network_call_performed"])
        self.assertFalse(result.data["external_side_effect_performed"])

    def test_live_mode_blocked_without_env_unlock(self):
        live_request = ExternalAdapterRequest(
            service="github",
            operation="create_issue",
            payload=self.request.payload,
            mode="live",
        )
        result = self.gate.evaluate(live_request, confirmation_token=live_request.confirmation_token)
        self.assertEqual(result.status, "external_live_blocked")
        self.assertFalse(result.data["live_gate_open"])
        self.assertFalse(result.data["network_call_performed"])

    def test_live_mode_env_unlock_authorizes_gate_but_does_not_execute_network(self):
        live_request = ExternalAdapterRequest(
            service="github",
            operation="create_issue",
            payload=self.request.payload,
            mode="live",
        )
        os.environ[EXTERNAL_LIVE_ENV_VAR] = "1"
        result = self.gate.evaluate(live_request, confirmation_token=live_request.confirmation_token)

        self.assertEqual(result.status, "live_gate_authorized")
        self.assertTrue(result.data["live_gate_open"])
        self.assertFalse(result.data["gate_performs_network_call"])
        self.assertFalse(result.data["network_call_performed"])
        self.assertFalse(result.data["external_side_effect_performed"])


if __name__ == "__main__":
    unittest.main()
