import tempfile
import unittest
from pathlib import Path

from ts_agl.os import TSOSSessionLedger


class TestTSOSSessionLedger(unittest.TestCase):
    def test_append_shell_command_records_event(self):
        ledger = TSOSSessionLedger.new(seed="test")
        event = ledger.append_shell_command("help")

        self.assertEqual(event.index, 0)
        self.assertEqual(event.mode, "help")
        self.assertEqual(len(ledger.events), 1)
        self.assertTrue(ledger.replay_summary()["all_gates_passed"])

    def test_save_load_preserves_session(self):
        ledger = TSOSSessionLedger.new(seed="test")
        ledger.append_shell_command("help")

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.json"
            ledger.save(path)
            loaded = TSOSSessionLedger.load(path)

        self.assertEqual(loaded.session_id, ledger.session_id)
        self.assertEqual(len(loaded.events), 1)
        self.assertEqual(loaded.events[0].raw_text, "help")

    def test_resume_session_adds_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.json"

            ledger = TSOSSessionLedger.new(seed="resume")
            ledger.append_shell_command("help")
            ledger.save(path)

            loaded = TSOSSessionLedger.load(path)
            loaded.append_shell_command("route: is the repo clean?")
            loaded.save(path)

            reloaded = TSOSSessionLedger.load(path)

        self.assertEqual(len(reloaded.events), 2)
        self.assertEqual(reloaded.events[1].mode, "route")
        self.assertTrue(reloaded.replay_summary()["can_resume"])

    def test_project_operator_session_event_is_bounded(self):
        ledger = TSOSSessionLedger.new(seed="operator")
        event = ledger.append_shell_command("inspect project and stage next safe note")
        summary = ledger.replay_summary()

        self.assertEqual(event.mode, "local_project_operator")
        self.assertFalse(summary["external_llm_used"])
        self.assertFalse(summary["external_side_effect_performed"])
        self.assertEqual(summary["candidate_graph_contamination_count"], 0)
        self.assertTrue(summary["all_gates_passed"])


if __name__ == "__main__":
    unittest.main()
