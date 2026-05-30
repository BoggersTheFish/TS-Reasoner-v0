import tempfile
import unittest
from pathlib import Path

from ts_chat.repair_memory import (
    get_repair_target,
    mark_repair_target_resolved,
    open_repair_targets,
    repair_memory_snapshot,
    repair_targets_not_proof,
    revisit_repair_target,
)
from ts_chat.sessions import build_v61_demo_session, load_session, save_session


class TestTSChatRepairMemory(unittest.TestCase):
    def test_open_repairs_listed(self):
        session = build_v61_demo_session()
        open_repairs = open_repair_targets(session)

        self.assertEqual(len(open_repairs), 1)
        self.assertEqual(open_repairs[0].repair_id, "repair_001")
        self.assertEqual(open_repairs[0].claim_text, "all cats are robots")

    def test_repair_memory_snapshot_has_schema(self):
        session = build_v61_demo_session()
        snapshot = repair_memory_snapshot(session)

        self.assertEqual(snapshot["schema"], "ts_chat_repair_memory_v1")
        self.assertEqual(snapshot["release"], "v6.2.0")
        self.assertEqual(snapshot["open_repair_target_count"], 1)
        self.assertEqual(snapshot["external_llm_used"], False)

    def test_repair_targets_survive_save_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.json"
            original = build_v61_demo_session()

            save_session(original, path)
            loaded = load_session(path)

            before = repair_memory_snapshot(original)
            after = repair_memory_snapshot(loaded)

            self.assertEqual(before["open_repair_targets"], after["open_repair_targets"])

    def test_revisit_repair_target_is_candidate_only(self):
        session = build_v61_demo_session()
        revisit = revisit_repair_target(session, "repair_001")

        self.assertEqual(revisit["repair_id"], "repair_001")
        self.assertEqual(revisit["claim_text"], "all cats are robots")
        self.assertFalse(revisit["creates_proof"])
        self.assertTrue(all(action["creates_proof_without_verifier"] is False for action in revisit["candidate_actions"]))

    def test_get_missing_repair_raises(self):
        session = build_v61_demo_session()

        with self.assertRaises(KeyError):
            get_repair_target(session, "missing_repair")

    def test_open_repair_target_not_proof(self):
        session = build_v61_demo_session()

        self.assertTrue(repair_targets_not_proof(session))
        self.assertNotIn("all cats are robots", session.accepted_claim_texts())

    def test_mark_repair_target_resolved_does_not_accept_claim(self):
        session = build_v61_demo_session()
        updated = mark_repair_target_resolved(session, "repair_001")

        self.assertEqual(len(open_repair_targets(updated)), 0)
        self.assertEqual(updated.repair_targets[0].status, "resolved")
        self.assertNotIn("all cats are robots", updated.accepted_claim_texts())
        self.assertFalse(updated.external_llm_used)


if __name__ == "__main__":
    unittest.main()
