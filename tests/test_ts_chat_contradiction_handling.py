import tempfile
import unittest
from pathlib import Path

from ts_chat.contradictions import (
    apply_contradiction_guard,
    contradiction_trace_valid,
    detect_contradiction,
    find_positive_support_path,
    parse_bounded_claim,
)
from ts_chat.sessions import ChatClaim, ChatSession, RepairTarget, build_v61_demo_session, load_session, save_session


class TestTSChatContradictionHandling(unittest.TestCase):
    def test_parse_all_claim(self):
        parsed = parse_bounded_claim("all cats are animals")

        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.quantifier, "all")
        self.assertEqual(parsed.subject, "cats")
        self.assertEqual(parsed.object, "animals")
        self.assertEqual(parsed.polarity, "positive")

    def test_parse_no_claim(self):
        parsed = parse_bounded_claim("no cats are animals")

        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.quantifier, "no")
        self.assertEqual(parsed.subject, "cats")
        self.assertEqual(parsed.object, "animals")
        self.assertEqual(parsed.polarity, "negative")

    def test_unparsed_claim_not_contradiction(self):
        session = build_v61_demo_session()
        trace = detect_contradiction(session, "cats probably do vibes")

        self.assertFalse(trace["parsed"])
        self.assertFalse(trace["contradiction_detected"])
        self.assertEqual(trace["contradiction_type"], "unparsed")
        self.assertTrue(contradiction_trace_valid(trace))

    def test_direct_contradiction_detected(self):
        session = build_v61_demo_session()
        trace = detect_contradiction(session, "no cats are animals")

        self.assertTrue(trace["contradiction_detected"])
        self.assertEqual(trace["contradiction_type"], "direct_contradiction")
        self.assertEqual(trace["support_path"], ["all cats are animals"])
        self.assertTrue(contradiction_trace_valid(trace))

    def test_transitive_contradiction_detected(self):
        session = build_v61_demo_session()
        trace = detect_contradiction(session, "no cats are mortal")

        self.assertTrue(trace["contradiction_detected"])
        self.assertEqual(trace["contradiction_type"], "transitive_contradiction")
        self.assertEqual(trace["support_path"], ["all cats are animals", "all animals are mortal"])
        self.assertTrue(contradiction_trace_valid(trace))

    def test_safe_claim_not_flagged(self):
        session = build_v61_demo_session()
        trace = detect_contradiction(session, "all cats are mammals")

        self.assertFalse(trace["contradiction_detected"])
        self.assertEqual(trace["contradiction_type"], "none")
        self.assertTrue(contradiction_trace_valid(trace))

    def test_positive_support_path(self):
        session = build_v61_demo_session()
        path = find_positive_support_path(session, "cats", "mortal")

        self.assertEqual(path, ["all cats are animals", "all animals are mortal"])

    def test_apply_contradiction_guard_rejects_claim(self):
        session = build_v61_demo_session()
        updated, trace = apply_contradiction_guard(session, "no cats are mortal", "turn_004")

        self.assertTrue(trace["contradiction_detected"])
        self.assertNotIn("no cats are mortal", updated.accepted_claim_texts())
        self.assertTrue(any(claim.text == "no cats are mortal" and claim.status == "rejected" for claim in updated.claims))
        self.assertTrue(any(target.claim_text == "no cats are mortal" for target in updated.repair_targets))
        self.assertFalse(updated.external_llm_used)

    def test_contradiction_survives_save_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.json"
            session = build_v61_demo_session()
            updated, _ = apply_contradiction_guard(session, "no cats are mortal", "turn_004")

            save_session(updated, path)
            loaded = load_session(path)

            self.assertNotIn("no cats are mortal", loaded.accepted_claim_texts())
            self.assertTrue(any(claim.text == "no cats are mortal" and claim.status == "rejected" for claim in loaded.claims))
            self.assertTrue(any(target.claim_text == "no cats are mortal" for target in loaded.repair_targets))

    def test_positive_claim_conflicts_with_negative_common_ground(self):
        session = ChatSession(
            session_id="negative_ground",
            claims=[
                ChatClaim(
                    claim_id="claim_001",
                    text="no cats are robots",
                    status="accepted",
                    source="user",
                    turn_id="turn_001",
                    support_paths=[],
                    verifier_channels=["user_asserted_common_ground"],
                )
            ],
            repair_targets=[],
            external_llm_used=False,
        )

        trace = detect_contradiction(session, "all cats are robots")

        self.assertTrue(trace["contradiction_detected"])
        self.assertEqual(trace["contradiction_type"], "direct_contradiction")
        self.assertEqual(trace["support_path"], ["no cats are robots"])
        self.assertTrue(contradiction_trace_valid(trace))


if __name__ == "__main__":
    unittest.main()
