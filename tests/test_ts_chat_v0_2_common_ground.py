import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.common_ground import CommonGround
from ts_reasoner.answer_arena import Relation
from ts_reasoner.ts_chat import TSChatSession, demo_v0_2_common_ground, parse_turn


ROOT = Path(__file__).resolve().parents[1]


class TestTSChatV02CommonGround(unittest.TestCase):
    def test_common_ground_records_premise_and_support_path(self):
        cg = CommonGround()
        cg.next_turn()
        cg.add_asserted_premise(Relation("dogs", "mammals"))
        cg.add_asserted_premise(Relation("mammals", "animals"))

        record = cg.record_question_result(Relation("dogs", "animals"))

        self.assertEqual(record.status, "accepted")
        self.assertEqual(len(record.support_path), 2)
        self.assertIn("dogs", cg.why_summary())

    def test_parse_commands(self):
        self.assertEqual(parse_turn("what do we know?").command, "summary")
        self.assertEqual(parse_turn("why?").command, "why")
        self.assertEqual(parse_turn("what is unsupported?").command, "unsupported")

    def test_session_why_and_summary(self):
        session = TSChatSession()
        session.process("all dogs are mammals. all mammals are animals. are all dogs animals?")

        why = session.process("why?")
        summary = session.process("what do we know?")

        self.assertIn("supported by", why.response)
        self.assertIn("all dogs are mammals", summary.response)

    def test_session_unsupported_summary(self):
        session = TSChatSession()
        session.process("all dogs are mammals. all mammals are animals.")
        session.process("also say all dogs are reptiles.")

        unsupported = session.process("what is unsupported?")

        self.assertIn("all dogs are reptiles", unsupported.response)
        self.assertIn("rejected", unsupported.response)

    def test_demo_gates(self):
        report = demo_v0_2_common_ground()

        self.assertEqual(report["version"], "ts-chat-v0.2-common-ground")
        self.assertFalse(report["external_llm_used"])
        self.assertEqual(report["turn_count"], 5)
        self.assertTrue(report["has_why_command"])
        self.assertTrue(report["has_summary_command"])
        self.assertTrue(report["has_unsupported_command"])

    def test_demo_script_writes_receipt(self):
        result = subprocess.run(
            [sys.executable, "scripts/ts_chat_v0_2/run_ts_chat_common_ground_demo.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn('"all_gates_passed": true', result.stdout)
        self.assertTrue((ROOT / "artifacts/ts_chat_v0_2_common_ground_demo_receipt.json").exists())


if __name__ == "__main__":
    unittest.main()
