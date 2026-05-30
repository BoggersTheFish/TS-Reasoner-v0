import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.ts_chat import TSChatSession, demo, parse_turn


ROOT = Path(__file__).resolve().parents[1]


class TestTSChatV01(unittest.TestCase):
    def test_parse_premises_and_question(self):
        parsed = parse_turn("all dogs are mammals. all mammals are animals. are all dogs animals?")

        self.assertEqual(len(parsed.premises), 2)
        self.assertEqual(len(parsed.questions), 1)
        self.assertEqual(parsed.questions[0].subject, "dogs")
        self.assertEqual(parsed.questions[0].object, "animals")

    def test_session_answers_supported_question(self):
        session = TSChatSession()
        receipt = session.process("all dogs are mammals. all mammals are animals. are all dogs animals?")

        self.assertIn("Yes", receipt.response)
        self.assertTrue(any(d["kind"] == "question" and d["status"] == "accepted" for d in receipt.decisions))

    def test_session_rejects_unsupported_requested_claim(self):
        session = TSChatSession()
        session.process("all dogs are mammals. all mammals are animals.")
        receipt = session.process("also say all dogs are reptiles.")

        self.assertIn("cannot support", receipt.response)
        self.assertTrue(
            any(
                d["kind"] == "requested_claim"
                and d["status"] == "rejected"
                and d["relation"]["subject"] == "dogs"
                and d["relation"]["object"] == "reptiles"
                for d in receipt.decisions
            )
        )

    def test_demo_gates(self):
        report = demo()

        self.assertEqual(report["version"], "ts-chat-v0.1")
        self.assertFalse(report["external_llm_used"])
        self.assertEqual(report["turn_count"], 3)
        self.assertEqual(len(report["receipts"]), 3)

    def test_demo_script_writes_receipt(self):
        result = subprocess.run(
            [sys.executable, "scripts/ts_chat_v0_1/run_ts_chat_demo.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn('"all_gates_passed": true', result.stdout)
        self.assertTrue((ROOT / "artifacts/ts_chat_v0_1_demo_receipt.json").exists())


if __name__ == "__main__":
    unittest.main()
