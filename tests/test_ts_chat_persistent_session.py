import json
import tempfile
import unittest
from pathlib import Path

from ts_chat.sessions import (
    SCHEMA,
    ChatClaim,
    ChatSession,
    RepairTarget,
    build_v61_demo_session,
    load_session,
    save_session,
)


class TestTSChatPersistentSession(unittest.TestCase):
    def test_save_load_roundtrip_preserves_accepted_claims(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.json"
            original = build_v61_demo_session()

            save_session(original, path)
            loaded = load_session(path)

            self.assertEqual(original.accepted_claim_texts(), loaded.accepted_claim_texts())

    def test_repair_targets_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.json"
            original = build_v61_demo_session()

            save_session(original, path)
            loaded = load_session(path)

            self.assertEqual(len(original.repair_targets), len(loaded.repair_targets))
            self.assertEqual(loaded.repair_targets[0].claim_text, "all cats are robots")
            self.assertEqual(loaded.repair_targets[0].status, "open")

    def test_unsupported_claim_not_promoted_to_proof(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.json"
            original = build_v61_demo_session()

            save_session(original, path)
            loaded = load_session(path)

            self.assertNotIn("all cats are robots", loaded.accepted_claim_texts())
            self.assertIn("all cats are robots", loaded.unsupported_or_candidate_claim_texts())

    def test_schema_field_exists(self):
        session = build_v61_demo_session()
        payload = session.to_dict()

        self.assertEqual(payload["schema"], SCHEMA)
        self.assertEqual(payload["release"], "v6.1.0")

    def test_external_llm_session_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad_session.json"
            payload = build_v61_demo_session().to_dict()
            payload["external_llm_used"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_session(path)

    def test_bad_schema_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad_schema.json"
            payload = build_v61_demo_session().to_dict()
            payload["schema"] = "wrong_schema"
            path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_session(path)

    def test_invalid_claim_status_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad_status.json"
            payload = build_v61_demo_session().to_dict()
            payload["claims"][0]["status"] = "magically_accepted_lol"
            path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_session(path)

    def test_manual_session_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manual.json"
            session = ChatSession(
                session_id="manual",
                claims=[
                    ChatClaim(
                        claim_id="c1",
                        text="all fish are swimmers",
                        status="accepted",
                        source="user",
                        turn_id="t1",
                        verifier_channels=["user_asserted_common_ground"],
                    )
                ],
                repair_targets=[
                    RepairTarget(
                        repair_id="r1",
                        claim_text="all fish are robots",
                        reason="missing typed verifier support",
                        source_turn_id="t2",
                    )
                ],
            )

            save_session(session, path)
            loaded = load_session(path)

            self.assertEqual(loaded.session_id, "manual")
            self.assertEqual(loaded.accepted_claim_texts(), ["all fish are swimmers"])
            self.assertEqual(len(loaded.repair_targets), 1)
            self.assertFalse(loaded.external_llm_used)


if __name__ == "__main__":
    unittest.main()
