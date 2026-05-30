import tempfile
import unittest
from pathlib import Path

from ts_chat.contradictions import apply_contradiction_guard
from ts_chat.provenance import (
    claim_provenance_record,
    common_ground_provenance_snapshot,
    provenance_record_valid,
    provenance_snapshot_valid,
    repair_target_provenance_record,
    revision_candidate_provenance_record,
)
from ts_chat.revision_candidates import generate_revision_candidates
from ts_chat.sessions import build_v61_demo_session, load_session, save_session


class TestTSChatProvenance(unittest.TestCase):
    def _guarded_with_revision_bundle(self):
        session = build_v61_demo_session()
        guarded, trace = apply_contradiction_guard(session, "no cats are mortal", "turn_004")
        bundle = generate_revision_candidates(guarded, "repair_002", contradiction_trace=trace)
        return guarded, bundle

    def test_claim_provenance_record_valid(self):
        session = build_v61_demo_session()
        record = claim_provenance_record(session, session.claims[0])

        self.assertEqual(record["schema"], "ts_chat_provenance_record_v1")
        self.assertEqual(record["release"], "v6.6.0")
        self.assertEqual(record["record_type"], "claim")
        self.assertEqual(record["text"], "all cats are animals")
        self.assertEqual(record["source_turn_id"], "turn_001")
        self.assertTrue(record["is_accepted_common_ground"])
        self.assertFalse(record["creates_proof"])
        self.assertTrue(provenance_record_valid(record))

    def test_repair_target_provenance_record_valid(self):
        session = build_v61_demo_session()
        record = repair_target_provenance_record(session, session.repair_targets[0])

        self.assertEqual(record["record_type"], "repair_target")
        self.assertEqual(record["text"], "all cats are robots")
        self.assertFalse(record["is_accepted_common_ground"])
        self.assertFalse(record["creates_proof"])
        self.assertTrue(provenance_record_valid(record))

    def test_revision_candidate_provenance_record_valid(self):
        guarded, bundle = self._guarded_with_revision_bundle()
        candidate = bundle["candidates"][0]
        record = revision_candidate_provenance_record(guarded, candidate, bundle)

        self.assertEqual(record["record_type"], "revision_candidate")
        self.assertEqual(record["repair_id"], "repair_002")
        self.assertEqual(record["text"], "no cats are mortal")
        self.assertFalse(record["auto_accept"])
        self.assertFalse(record["is_accepted_common_ground"])
        self.assertFalse(record["creates_proof"])
        self.assertTrue(provenance_record_valid(record))

    def test_common_ground_snapshot_valid(self):
        guarded, bundle = self._guarded_with_revision_bundle()
        snapshot = common_ground_provenance_snapshot(guarded, revision_bundles=[bundle])

        self.assertEqual(snapshot["schema"], "ts_chat_provenance_snapshot_v1")
        self.assertEqual(snapshot["release"], "v6.6.0")
        self.assertEqual(snapshot["claim_record_count"], len(guarded.claims))
        self.assertEqual(snapshot["repair_record_count"], len(guarded.repair_targets))
        self.assertEqual(snapshot["revision_candidate_record_count"], bundle["candidate_count"])
        self.assertTrue(snapshot["all_records_have_provenance"])
        self.assertTrue(snapshot["all_accepted_claims_have_source_turns"])
        self.assertTrue(snapshot["candidate_and_repair_records_not_common_ground"])
        self.assertEqual(snapshot["candidate_graph_contamination_count"], 0)
        self.assertTrue(provenance_snapshot_valid(snapshot))

    def test_provenance_survives_save_load_regeneration(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.json"
            guarded, bundle = self._guarded_with_revision_bundle()

            save_session(guarded, path)
            loaded = load_session(path)
            loaded_bundle = generate_revision_candidates(loaded, "repair_002")
            snapshot = common_ground_provenance_snapshot(loaded, revision_bundles=[loaded_bundle])

            self.assertTrue(provenance_snapshot_valid(snapshot))
            self.assertNotIn("no cats are mortal", loaded.accepted_claim_texts())

    def test_invalid_provenance_record_rejected_if_creates_proof(self):
        session = build_v61_demo_session()
        record = claim_provenance_record(session, session.claims[0])
        record["creates_proof"] = True

        self.assertFalse(provenance_record_valid(record))

    def test_invalid_snapshot_rejected_if_candidate_contamination(self):
        guarded, bundle = self._guarded_with_revision_bundle()
        snapshot = common_ground_provenance_snapshot(guarded, revision_bundles=[bundle])
        snapshot["candidate_graph_contamination_count"] = 1

        self.assertFalse(provenance_snapshot_valid(snapshot))


if __name__ == "__main__":
    unittest.main()
