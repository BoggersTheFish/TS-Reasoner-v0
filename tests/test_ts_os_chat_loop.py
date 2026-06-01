from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_agl.os.chat_loop import TSOSChatLoop, run_first_contact_chat_demo


ROOT = Path(__file__).resolve().parents[1]


class TSOSChatLoopTests(unittest.TestCase):
    def test_help_turn(self) -> None:
        turn = TSOSChatLoop().handle("help")
        self.assertEqual(turn.mode, "help")
        self.assertTrue(turn.payload["all_gates_passed"])

    def test_repo_and_next_safe_action_routes(self) -> None:
        loop = TSOSChatLoop()
        status = loop.handle("is the repo clean?")
        next_action = loop.handle("what should we do next?")
        self.assertEqual(status.selected_call.system, "git_repo")
        self.assertEqual(status.selected_call.operation, "git_status")
        self.assertEqual(next_action.selected_call.system, "git_repo")
        self.assertEqual(next_action.selected_call.operation, "next_safe_release_action")

    def test_vague_and_destructive_requests_abstain(self) -> None:
        loop = TSOSChatLoop()
        vague = loop.handle("purple banana quantum sandwich")
        destructive = loop.handle("delete everything and push it")
        self.assertEqual(vague.selected_call.operation, "route_unknown")
        self.assertEqual(destructive.selected_call.operation, "route_unknown")
        self.assertEqual(destructive.action_taken, "none")

    def test_external_side_effect_blocks_on_missing_slots(self) -> None:
        turn = TSOSChatLoop().handle("stage an external side effect")
        self.assertEqual(turn.selected_call.system, "external_service")
        self.assertEqual(turn.selected_call.operation, "send_notification_dry_run")
        self.assertEqual(turn.selected_call.risk, "external_side_effect")
        self.assertEqual(turn.result.status, "missing_slots")
        self.assertEqual(set(turn.selected_call.missing_slots), {"recipient", "message"})
        self.assertEqual(turn.action_taken, "none")

    def test_proof_query_keeps_claim_boundary(self) -> None:
        turn = TSOSChatLoop().handle("can we prove all A are C?")
        self.assertEqual(turn.selected_call.system, "ts_reasoner")
        self.assertEqual(turn.selected_call.operation, "check_support")
        self.assertEqual(turn.selected_call.args["claim"], "all A are C")
        self.assertTrue(turn.payload["confidence_ignored_as_proof"])

    def test_project_operator_blocks_unconfirmed_write(self) -> None:
        turn = TSOSChatLoop().handle("inspect project and stage next safe note")
        self.assertEqual(turn.mode, "local_project_operator")
        self.assertTrue(turn.payload["unconfirmed_write_blocked"])
        self.assertFalse(turn.payload["external_side_effect_performed"])

    def test_scripted_demo_receipt_gates(self) -> None:
        receipt = run_first_contact_chat_demo().to_dict()
        self.assertTrue(receipt["all_gates_passed"], receipt)
        self.assertEqual(receipt["metrics"]["receipt_turn_count"], len(receipt["turns"]))
        self.assertFalse(receipt["external_llm_used"])
        self.assertFalse(receipt["external_side_effect_performed"])

    def test_evaluator_writes_report(self) -> None:
        subprocess.run([sys.executable, "scripts/evaluate_ts_os_chat_loop.py"], cwd=ROOT, check=True)
        report = json.loads((ROOT / "artifacts/ts_os_chat_loop_report.json").read_text(encoding="utf-8"))
        self.assertTrue(report["all_gates_passed"], report)


if __name__ == "__main__":
    unittest.main()
