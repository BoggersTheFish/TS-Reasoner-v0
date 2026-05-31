import tempfile
import unittest
from pathlib import Path

from ts_reasoner.knowledge_pack_library import (
    KnowledgePackLibrary,
    create_pack_from_edges,
    knowledge_pack_library_state_valid,
    pack_accepted_edges,
    pack_rejected_relations,
    run_knowledge_pack_library_demo,
)
from ts_reasoner.ts_chat import TSChatSession


class TestTSReasonerV76KnowledgePackLibrary(unittest.TestCase):
    def test_create_pack_edges(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pack.json"
            pack = create_pack_from_edges(
                path,
                label="test",
                accepted_edges=[("cats", "animals")],
                rejected_relations=[("cats", "robots")],
            )

            self.assertTrue(path.exists())
            self.assertIn(("cats", "animals"), pack_accepted_edges(pack))
            self.assertIn(("cats", "robots"), pack_rejected_relations(pack))

    def test_register_and_list_packs(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pack_path = tmp_path / "pack.json"
            create_pack_from_edges(pack_path, label="animals", accepted_edges=[("cats", "animals")])

            library = KnowledgePackLibrary(tmp_path / "library")
            receipt = library.register_pack("animals", pack_path)
            listing = library.list_packs()

            self.assertEqual(receipt["label"], "animals")
            self.assertEqual(listing["pack_count"], 1)
            self.assertTrue(knowledge_pack_library_state_valid(listing))

    def test_compare_packs(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            a = tmp_path / "a.json"
            b = tmp_path / "b.json"
            create_pack_from_edges(a, label="a", accepted_edges=[("cats", "animals")])
            create_pack_from_edges(b, label="b", accepted_edges=[("cats", "animals"), ("animals", "mortal")])

            library = KnowledgePackLibrary(tmp_path / "library")
            library.register_pack("a", a)
            library.register_pack("b", b)
            compare = library.compare_packs("a", "b")

            self.assertEqual(len(compare["shared_edges"]), 1)
            self.assertEqual(len(compare["only_right_edges"]), 1)
            self.assertEqual(compare["candidate_graph_contamination_count"], 0)

    def test_unsafe_pack_merge_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pack_path = tmp_path / "unsafe.json"
            create_pack_from_edges(pack_path, label="unsafe", accepted_edges=[("cats", "robots")])

            library = KnowledgePackLibrary(tmp_path / "library")
            library.register_pack("unsafe", pack_path)

            session = TSChatSession()
            session.process("also say all cats are robots")

            merge = library.merge_pack_into_session("unsafe", session)

            self.assertTrue(merge["blocked"])
            self.assertFalse(merge["merged"])
            self.assertEqual(merge["candidate_graph_contamination_count"], 0)

    def test_safe_pack_merge_answers_question(self):
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

            session = TSChatSession()
            session.process("also say all cats are robots")

            merge = library.merge_pack_into_session("machines", session)
            question = session.process("are all cats robots?")

            self.assertTrue(merge["merged"])
            self.assertFalse(merge["blocked"])
            self.assertEqual(merge["merged_edge_count"], 2)
            self.assertTrue(any(
                record.get("kind") == "question" and record.get("status") == "accepted"
                for record in question.records_created
            ))

    def test_demo_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = run_knowledge_pack_library_demo(Path(tmp))

            self.assertTrue(receipt["all_gates_passed"])
            self.assertEqual(receipt["pack_count"], 3)
            self.assertTrue(receipt["unsafe_merge_blocked"])
            self.assertTrue(receipt["safe_merge_allowed"])
            self.assertTrue(receipt["post_merge_answer_accepted"])
            self.assertEqual(receipt["candidate_graph_contamination_count"], 0)


if __name__ == "__main__":
    unittest.main()
