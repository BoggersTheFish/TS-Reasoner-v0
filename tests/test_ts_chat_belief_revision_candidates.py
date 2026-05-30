import tempfile
import unittest
from pathlib import Path

from ts_chat.contradictions import apply_contradiction_guard
from ts_chat.revision_candidates import (
    candidate_graph_contamination_count,
    generate_revision_candidates,
    revision_candidate_bundle_valid,
    revision_candidates_do_not_accept_claim,
)
from ts_chat.sessions import build_v61_demo_session, load_session, save_session


class TestTSChatBeliefRevisionCandidates(unittest.TestCase):
    def _guarded_session(self):
        session = build_v61_demo_session()
        guarded, trace = apply_contradiction_guard(session, "no cats are mortal", "turn_004")
        return guarded, trace

    def test_revision_candidates_generated_for_contradiction_repair(self):
        guarded, trace = self._guarded_session()
        bundle = generate_revision_candidates(guarded, "repair_002", contradiction_trace=trace)

        self.assertEqual(bundle["schema"], "ts_chat_revision_candidates_v1")
        self.assertEqual(bundle["release"], "v6.5.0")
        self.assertEqual(bundle["repair_id"], "repair_002")
        self.assertEqual(bundle["claim_text"], "no cats are mortal")
        self.assertGreaterEqual(bundle["candidate_count"], 5)
        self.assertTrue(revision_candidate_bundle_valid(bundle))

    def test_revision_candidates_are_not_proof(self):
        guarded, trace = self._guarded_session()
        bundle = generate_revision_candidates(guarded, "repair_002", contradiction_trace=trace)

        self.assertTrue(bundle["all_candidates_create_no_proof"])
        self.assertTrue(bundle["all_candidates_not_auto_accepted"])
        self.assertTrue(bundle["all_candidates_require_user_confirmation"])
        self.assertTrue(bundle["all_candidates_require_typed_verifier"])
        self.assertFalse(bundle["creates_proof"])

    def test_revision_candidates_do_not_accept_contradictory_claim(self):
        guarded, trace = self._guarded_session()
        bundle = generate_revision_candidates(guarded, "repair_002", contradiction_trace=trace)

        self.assertTrue(revision_candidates_do_not_accept_claim(guarded, bundle))
        self.assertNotIn("no cats are mortal", guarded.accepted_claim_texts())
        self.assertEqual(candidate_graph_contamination_count(guarded, bundle), 0)

    def test_support_path_preserved(self):
        guarded, trace = self._guarded_session()
        bundle = generate_revision_candidates(guarded, "repair_002", contradiction_trace=trace)

        self.assertEqual(bundle["support_path"], ["all cats are animals", "all animals are mortal"])
        self.assertEqual(bundle["contradiction_type"], "transitive_contradiction")

    def test_revision_candidates_survive_save_load_regeneration(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.json"
            guarded, trace = self._guarded_session()

            save_session(guarded, path)
            loaded = load_session(path)
            bundle = generate_revision_candidates(loaded, "repair_002", contradiction_trace=trace)

            self.assertTrue(revision_candidate_bundle_valid(bundle))
            self.assertTrue(revision_candidates_do_not_accept_claim(loaded, bundle))
            self.assertEqual(candidate_graph_contamination_count(loaded, bundle), 0)

    def test_missing_repair_raises(self):
        guarded, trace = self._guarded_session()

        with self.assertRaises(KeyError):
            generate_revision_candidates(guarded, "missing_repair", contradiction_trace=trace)

    def test_all_candidate_actions_are_bounded(self):
        guarded, trace = self._guarded_session()
        bundle = generate_revision_candidates(guarded, "repair_002", contradiction_trace=trace)

        actions = {candidate["action"] for candidate in bundle["candidates"]}

        self.assertIn("reject_new_claim", actions)
        self.assertIn("challenge_existing_support_path", actions)
        self.assertIn("split_or_refine_subject", actions)
        self.assertIn("request_typed_support", actions)
        self.assertIn("keep_open_repair_target", actions)


if __name__ == "__main__":
    unittest.main()
