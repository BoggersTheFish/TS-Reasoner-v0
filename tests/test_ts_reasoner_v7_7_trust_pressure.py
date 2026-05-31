import tempfile
import unittest
from pathlib import Path

from ts_reasoner.knowledge_pack_library import KnowledgePackLibrary, create_pack_from_edges
from ts_reasoner.trust_pressure import (
    TrustRegistry,
    audit_pack_merge_with_trust,
    compare_packs_with_trust,
    merge_pack_with_trust,
    run_trust_pressure_demo,
    trust_pressure_payload_valid,
)
from ts_reasoner.ts_chat import TSChatSession


class TestTSReasonerV77TrustPressure(unittest.TestCase):
    def test_trust_registry_valid(self):
        registry = TrustRegistry()
        registry.set_source("session", "high", source_type="live_session")
        registry.set_source("pack", "low", source_type="knowledge_pack")

        payload = registry.to_dict()

        self.assertTrue(trust_pressure_payload_valid(payload))
        self.assertEqual(payload["source_count"], 2)
        self.assertFalse(payload["trust_is_proof"])
        self.assertTrue(payload["typed_verifier_remains_proof_authority"])

    def test_unknown_source_defaults_low(self):
        registry = TrustRegistry()
        source = registry.get("missing")

        self.assertEqual(source.tier, "low")
        self.assertEqual(source.weight, 0.25)
        self.assertFalse(source.trust_is_proof)

    def test_low_trust_direct_conflict_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pack_path = tmp_path / "unsafe.json"
            create_pack_from_edges(pack_path, label="unsafe", accepted_edges=[("cats", "robots")])

            library = KnowledgePackLibrary(tmp_path / "library")
            library.register_pack("unsafe", pack_path)

            registry = TrustRegistry()
            registry.set_source("session", "high", source_type="live_session")
            registry.set_source("unsafe", "low", source_type="knowledge_pack")

            session = TSChatSession()
            session.process("also say all cats are robots")

            audit = audit_pack_merge_with_trust(library, "unsafe", session, registry)
            merge = merge_pack_with_trust(library, "unsafe", session, registry)

            self.assertTrue(audit["blocked"])
            self.assertFalse(audit["safe_to_merge"])
            self.assertEqual(audit["pressure_records"][0]["higher_pressure_side"], "rejected")
            self.assertTrue(merge["blocked"])
            self.assertFalse(merge["merged"])
            self.assertEqual(merge["candidate_graph_contamination_count"], 0)

    def test_compatible_pack_merge_still_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pack_path = tmp_path / "machines.json"
            create_pack_from_edges(
                pack_path,
                label="machines",
                accepted_edges=[("cats", "machines"), ("machines", "robots")],
            )

            library = KnowledgePackLibrary(tmp_path / "library")
            library.register_pack("machines", pack_path)

            registry = TrustRegistry()
            registry.set_source("session", "high", source_type="live_session")
            registry.set_source("machines", "medium", source_type="knowledge_pack")

            session = TSChatSession()
            session.process("also say all cats are robots")

            audit = audit_pack_merge_with_trust(library, "machines", session, registry)
            merge = merge_pack_with_trust(library, "machines", session, registry)
            question = session.process("are all cats robots?")

            self.assertFalse(audit["blocked"])
            self.assertTrue(audit["safe_to_merge"])
            self.assertTrue(merge["merged"])
            self.assertFalse(merge["blocked"])
            self.assertTrue(any(
                record.get("kind") == "question" and record.get("status") == "accepted"
                for record in question.records_created
            ))

    def test_compare_packs_with_trust(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            left = tmp_path / "left.json"
            right = tmp_path / "right.json"

            create_pack_from_edges(left, label="left", accepted_edges=[("cats", "machines")])
            create_pack_from_edges(
                right,
                label="right",
                accepted_edges=[("dogs", "animals")],
                rejected_relations=[("cats", "machines")],
            )

            library = KnowledgePackLibrary(tmp_path / "library")
            library.register_pack("left", left)
            library.register_pack("right", right)

            registry = TrustRegistry()
            registry.set_source("left", "medium", source_type="knowledge_pack")
            registry.set_source("right", "low", source_type="knowledge_pack")

            compare = compare_packs_with_trust(library, "left", "right", registry)

            self.assertEqual(compare["pressure_record_count"], 1)
            self.assertEqual(compare["candidate_graph_contamination_count"], 0)
            self.assertFalse(compare["trust_is_proof"])

    def test_demo_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = run_trust_pressure_demo(Path(tmp))

            self.assertTrue(receipt["all_gates_passed"])
            self.assertTrue(receipt["unsafe_pressure_detected"])
            self.assertTrue(receipt["unsafe_merge_blocked"])
            self.assertTrue(receipt["safe_merge_allowed"])
            self.assertTrue(receipt["post_merge_answer_accepted"])
            self.assertEqual(receipt["candidate_graph_contamination_count"], 0)


if __name__ == "__main__":
    unittest.main()
