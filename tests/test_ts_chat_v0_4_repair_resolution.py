import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.ts_chat import TSChatSession, demo_v0_4_repair_resolution


ROOT = Path(__file__).resolve().parents[1]


class TestTSChatV04RepairResolution(unittest.TestCase):
    def test_missing_support_repair_resolves_when_support_added(self):
        session = TSChatSession()
        session.process("all dogs are mammals.")
        session.process("also say all dogs are reptiles.")

        self.assertEqual(session.common_ground.repair_targets[0].status, "open")

        receipt = session.process("all dogs are canines. all canines are reptiles.")

        self.assertEqual(session.common_ground.repair_targets[0].status, "resolved")
        self.assertIn("Resolved repair targets:", receipt.response)

    def test_parse_repair_message_not_duplicated(self):
        session = TSChatSession()
        receipt = session.process("penguin banana sideways")

        self.assertIn("Could not parse bounded TS-Chat structure: penguin banana sideways", receipt.response)
        self.assertNotIn(
            "Could not parse bounded TS-Chat structure: Could not parse bounded TS-Chat structure:",
            receipt.response,
        )

    def test_demo_v04_gates_shape(self):
        report = demo_v0_4_repair_resolution()

        self.assertEqual(report["version"], "ts-chat-v0.4-repair-resolution")
        self.assertFalse(report["external_llm_used"])
        self.assertEqual(report["turn_count"], 8)
        self.assertGreaterEqual(report["repair_target_count"], 2)

    def test_demo_script_writes_receipt(self):
        result = subprocess.run(
            [sys.executable, "scripts/ts_chat_v0_4/run_ts_chat_repair_resolution_demo.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn('"all_gates_passed": true', result.stdout)
        self.assertTrue((ROOT / "artifacts/ts_chat_v0_4_repair_resolution_demo_receipt.json").exists())


if __name__ == "__main__":
    unittest.main()
