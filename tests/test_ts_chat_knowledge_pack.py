import json
import tempfile
import unittest
from pathlib import Path

from ts_chat.contradictions import apply_contradiction_guard
from ts_chat.knowledge_pack import (
    build_knowledge_pack,
    export_knowledge_pack,
    import_knowledge_pack,
    knowledge_pack_valid,
    roundtrip_knowledge_pack,
    roundtrip_valid,
)
from ts_chat.revision_candidates import generate_revision_candidates
from ts_chat.sessions import build_v61_demo_session


class TestTSChatKnowledgePack(unittest.TestCase):
    def _session_and_bundle(self):
        session = build_v61_demo_session()
        guarded, trace = apply_contradiction_guard(session, "no cats are mortal", "turn_004")
        bundle = generate_revision_candidates(guarded, "repair_002", contradiction_trace=trace)
        return guarded, bundle

    def test_build_knowledge_pack_valid(self):
        session, bundle = self._session_and_bundle()
        pack = build_knowledge_pack(session, revision_bundles=[bundle])

        self.assertEqual(pack["schema"], "ts_chat_knowledge_pack_v1")
        self.assertEqual(pack["release"], "v6.7.0")
        self.assertEqual(pack["claim_count"], len(session.claims))
        self.assertEqual(pack["repair_target_count"], len(session.repair_targets))
        self.assertEqual(pack["revision_bundle_count"], 1)
        self.assertTrue(pack["knowledge_pack_import_is_not_proof"])
        self.assertEqual(pack["candidate_graph_contamination_count"], 0)
        self.assertTrue(knowledge_pack_valid(pack))

    def test_export_import_knowledge_pack(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pack.json"
            session, bundle = self._session_and_bundle()

            export_knowledge_pack(session, path, revision_bundles=[bundle])
            imported_session, imported_pack = import_knowledge_pack(path)

            self.assertTrue(path.exists())
            self.assertTrue(knowledge_pack_valid(imported_pack))
            self.assertEqual(session.accepted_claim_texts(), imported_session.accepted_claim_texts())
            self.assertEqual(len(session.repair_targets), len(imported_session.repair_targets))
            self.assertNotIn("no cats are mortal", imported_session.accepted_claim_texts())

    def test_roundtrip_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            pack_path = Path(tmp) / "pack.json"
            session_path = Path(tmp) / "session.json"
            session, bundle = self._session_and_bundle()

            rt = roundtrip_knowledge_pack(
                session,
                pack_path,
                session_path,
                revision_bundles=[bundle],
            )

            self.assertTrue(roundtrip_valid(rt))
            self.assertTrue(pack_path.exists())
            self.assertTrue(session_path.exists())
            self.assertEqual(rt["candidate_graph_contamination_count"], 0)

    def test_invalid_pack_rejected_if_import_claims_changed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad_pack.json"
            session, bundle = self._session_and_bundle()
            pack = build_knowledge_pack(session, revision_bundles=[bundle])
            pack["accepted_claim_texts"] = ["no cats are mortal"]
            path.write_text(json.dumps(pack), encoding="utf-8")

            with self.assertRaises(ValueError):
                import_knowledge_pack(path)

    def test_invalid_pack_rejected_if_external_llm_true(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad_pack.json"
            session, bundle = self._session_and_bundle()
            pack = build_knowledge_pack(session, revision_bundles=[bundle])
            pack["external_llm_used"] = True
            path.write_text(json.dumps(pack), encoding="utf-8")

            with self.assertRaises(ValueError):
                import_knowledge_pack(path)

    def test_invalid_pack_rejected_if_contaminated(self):
        session, bundle = self._session_and_bundle()
        pack = build_knowledge_pack(session, revision_bundles=[bundle])
        pack["candidate_graph_contamination_count"] = 1

        self.assertFalse(knowledge_pack_valid(pack))

    def test_pack_preserves_provenance_snapshot(self):
        session, bundle = self._session_and_bundle()
        pack = build_knowledge_pack(session, revision_bundles=[bundle])
        snapshot = pack["provenance_snapshot"]

        self.assertGreater(snapshot["record_count"], 0)
        self.assertEqual(snapshot["candidate_graph_contamination_count"], 0)
        self.assertTrue(snapshot["all_records_have_provenance"])


if __name__ == "__main__":
    unittest.main()
