import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.ts_chat import TSChatSession, demo_v0_3_repair_targets


ROOT = Path(__file__).resolve().parents[1]


class TestTSChatV03RepairTargets(unittest.TestCase):
    def test_unsupported_claim_creates_repair_target(self):
        session = TSChatSession()
        session.process("all dogs are mammals. all mammals are animals.")
        receipt = session.process("also say all dogs are reptiles.")

        self.assertIn("Repair targets:", receipt.response)
        self.assertGreaterEqual(len(session.common_ground.repair_targets), 1)
        self.assertEqual(session.common_ground.repair_targets[0].kind, "missing_support")

    def test_parse_failure_creates_repair_target(self):
        session = TSChatSession()
        receipt = session.process("penguin banana sideways")

        self.assertIn("Repair targets:", receipt.response)
        self.assertGreaterEqual(len(session.common_ground.repair_targets), 1)
        self.assertEqual(session.common_ground.repair_targets[0].kind, "parse_failure")

    def test_repairs_command(self):
        session = TSChatSession()
        session.process("all dogs are mammals.")
        session.process("also say all dogs are reptiles.")
        receipt = session.process("/repairs")

        self.assertIn("Open repair targets:", receipt.response)
        self.assertIn("all dogs are reptiles", receipt.response)

    def test_demo_v03_gates_shape(self):
        report = demo_v0_3_repair_targets()

        self.assertEqual(report["version"], "ts-chat-v0.3-repair-targets")
        self.assertFalse(report["external_llm_used"])
        self.assertEqual(report["turn_count"], 7)
        self.assertGreaterEqual(report["repair_target_count"], 2)
        self.assertTrue(report["has_repairs_command"])

    def test_demo_script_writes_receipt(self):
        result = subprocess.run(
            [sys.executable, "scripts/ts_chat_v0_3/run_ts_chat_repair_demo.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn('"all_gates_passed": true', result.stdout)
        self.assertTrue((ROOT / "artifacts/ts_chat_v0_3_repair_targets_demo_receipt.json").exists())


if __name__ == "__main__":
    unittest.main()
