import tempfile
import unittest
from pathlib import Path

from ts_chat.explanations import (
    explain_claim,
    explain_last_claim,
    explain_repair_target,
    explanation_bundle,
    explanation_trace_valid,
)
from ts_chat.sessions import ChatSession, build_v61_demo_session, load_session, save_session


class TestTSChatExplanationTraces(unittest.TestCase):
    def test_accepted_claim_trace(self):
        session = build_v61_demo_session()
        trace = explain_claim(session, "all cats are animals")

        self.assertEqual(trace["decision"], "accepted")
        self.assertEqual(trace["claim_text"], "all cats are animals")
        self.assertFalse(trace["creates_proof"])
        self.assertTrue(explanation_trace_valid(trace))

    def test_unsupported_claim_trace(self):
        session = build_v61_demo_session()
        trace = explain_claim(session, "all cats are robots")

        self.assertEqual(trace["decision"], "unsupported")
        self.assertEqual(trace["reason"], "missing typed verifier support")
        self.assertFalse(trace["creates_proof"])
        self.assertTrue(explanation_trace_valid(trace))

    def test_missing_claim_abstains(self):
        session = build_v61_demo_session()
        trace = explain_claim(session, "all dragons are accountants")

        self.assertEqual(trace["trace_type"], "missing_claim")
        self.assertEqual(trace["decision"], "abstained")
        self.assertFalse(trace["creates_proof"])
        self.assertTrue(explanation_trace_valid(trace))

    def test_repair_target_trace(self):
        session = build_v61_demo_session()
        trace = explain_repair_target(session, "repair_001")

        self.assertEqual(trace["trace_type"], "repair_target")
        self.assertEqual(trace["repair_id"], "repair_001")
        self.assertEqual(trace["claim_text"], "all cats are robots")
        self.assertFalse(trace["creates_proof"])
        self.assertTrue(explanation_trace_valid(trace))

    def test_last_claim_trace(self):
        session = build_v61_demo_session()
        trace = explain_last_claim(session)

        self.assertEqual(trace["claim_text"], "all cats are robots")
        self.assertEqual(trace["decision"], "unsupported")
        self.assertTrue(explanation_trace_valid(trace))

    def test_empty_session_last_trace_abstains(self):
        session = ChatSession(session_id="empty")
        trace = explain_last_claim(session)

        self.assertEqual(trace["trace_type"], "empty_session")
        self.assertEqual(trace["decision"], "abstained")
        self.assertFalse(trace["creates_proof"])
        self.assertTrue(explanation_trace_valid(trace))

    def test_explanation_bundle_valid(self):
        session = build_v61_demo_session()
        bundle = explanation_bundle(session)

        self.assertEqual(bundle["schema"], "ts_chat_explanation_bundle_v1")
        self.assertEqual(bundle["release"], "v6.3.0")
        self.assertEqual(bundle["claim_trace_count"], 3)
        self.assertEqual(bundle["repair_trace_count"], 1)
        self.assertTrue(bundle["all_traces_valid"])
        self.assertTrue(bundle["all_traces_create_no_proof"])
        self.assertEqual(bundle["candidate_graph_contamination_count"], 0)

    def test_traces_survive_session_reload(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.json"
            original = build_v61_demo_session()

            save_session(original, path)
            loaded = load_session(path)

            trace = explain_claim(loaded, "all cats are robots")
            self.assertEqual(trace["decision"], "unsupported")
            self.assertTrue(explanation_trace_valid(trace))
            self.assertNotIn("all cats are robots", loaded.accepted_claim_texts())

    def test_invalid_trace_rejected(self):
        session = build_v61_demo_session()
        trace = explain_claim(session, "all cats are animals")
        trace["creates_proof"] = True

        self.assertFalse(explanation_trace_valid(trace))


if __name__ == "__main__":
    unittest.main()
