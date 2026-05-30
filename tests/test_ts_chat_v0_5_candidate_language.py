import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.candidate_language import generate_response_candidates, select_response_candidate
from ts_reasoner.ts_chat import TSChatSession, demo_v0_5_candidate_language_rules


ROOT = Path(__file__).resolve().parents[1]


class TestTSChatV05CandidateLanguage(unittest.TestCase):
    def test_candidate_generation_selects_supported_answer(self):
        candidates = generate_response_candidates(
            parsed_command=None,
            records=[
                {
                    "kind": "question",
                    "status": "accepted",
                    "relation": {"subject": "dogs", "object": "animals"},
                    "support_path": [
                        {"subject": "dogs", "object": "mammals"},
                        {"subject": "mammals", "object": "animals"},
                    ],
                }
            ],
            repair_records=[],
            parse_warnings=[],
            discourse_markers=[],
            fallback_text="fallback",
        )

        selected = select_response_candidate(candidates)

        self.assertIn(selected.rule_id, {"supported_answer_concise", "supported_answer_with_path"})
        self.assertIn("all dogs are animals", selected.text)

    def test_session_receipt_has_candidate_selection(self):
        session = TSChatSession()
        receipt = session.process("all dogs are mammals. all mammals are animals. are all dogs animals?")

        self.assertTrue(receipt.candidate_selection)
        self.assertIn("selected", receipt.candidate_selection)
        self.assertIn("rule_id", receipt.candidate_selection["selected"])

    def test_parse_failure_uses_parse_rule(self):
        session = TSChatSession()
        receipt = session.process("penguin banana sideways")

        self.assertEqual(receipt.candidate_selection["selected"]["rule_id"], "parse_failure_repair")

    def test_demo_v05_gates_shape(self):
        report = demo_v0_5_candidate_language_rules()

        self.assertEqual(report["version"], "ts-chat-v0.5-candidate-language-rules")
        self.assertFalse(report["external_llm_used"])
        self.assertEqual(report["turn_count"], 6)
        self.assertTrue(report["has_candidate_selection"])
        self.assertTrue(report["has_parse_rule"])

    def test_demo_script_writes_receipt(self):
        result = subprocess.run(
            [sys.executable, "scripts/ts_chat_v0_5/run_ts_chat_candidate_language_demo.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn('"all_gates_passed": true', result.stdout)
        self.assertTrue((ROOT / "artifacts/ts_chat_v0_5_candidate_language_demo_receipt.json").exists())


if __name__ == "__main__":
    unittest.main()
