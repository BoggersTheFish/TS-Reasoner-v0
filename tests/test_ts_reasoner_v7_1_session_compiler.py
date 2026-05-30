import json
import tempfile
import unittest
from pathlib import Path

from ts_reasoner.session_compiler import (
    compile_session_artifacts,
    compile_session_file,
    load_session_receipts,
)
from ts_reasoner.ts_chat import TSChatSession, receipt_to_dict


def build_demo_receipts():
    session = TSChatSession()
    turns = [
        "all cats are animals",
        "all animals are mortal",
        "also say all cats are robots",
        "/repairs",
        "all cats are machines",
        "all machines are robots",
        "/repairs",
        "are all cats robots?",
        "why?",
    ]
    return [receipt_to_dict(session.process(turn)) for turn in turns]


class TestTSReasonerV71SessionCompiler(unittest.TestCase):
    def test_compile_session_artifacts(self):
        receipts = build_demo_receipts()

        with tempfile.TemporaryDirectory() as tmp:
            receipt = compile_session_artifacts(receipts, tmp, label="test_session")

            self.assertEqual(receipt["release"], "v7.1.0")
            self.assertEqual(receipt["turn_count"], len(receipts))
            self.assertEqual(receipt["replay_row_count"], len(receipts))
            self.assertGreaterEqual(receipt["repair_curriculum_row_count"], 1)
            self.assertGreaterEqual(receipt["provenance_record_count"], 1)
            self.assertGreaterEqual(receipt["resolved_repair_count"], 1)
            self.assertGreaterEqual(receipt["rejected_record_count"], 1)
            self.assertEqual(receipt["candidate_graph_contamination_count"], 0)
            self.assertTrue(receipt["all_gates_passed"])

            self.assertTrue(Path(receipt["replay_path"]).exists())
            self.assertTrue(Path(receipt["repair_curriculum_path"]).exists())
            self.assertTrue(Path(receipt["provenance_path"]).exists())
            self.assertTrue(Path(receipt["knowledge_pack_path"]).exists())

    def test_compile_session_file(self):
        receipts = build_demo_receipts()

        with tempfile.TemporaryDirectory() as tmp:
            session_path = Path(tmp) / "session.json"
            session_path.write_text(json.dumps(receipts), encoding="utf-8")

            loaded = load_session_receipts(session_path)
            self.assertEqual(len(loaded), len(receipts))

            receipt = compile_session_file(session_path, Path(tmp) / "compiled", label="loaded_session")
            self.assertTrue(receipt["all_gates_passed"])
            self.assertEqual(receipt["external_llm_used"], False)

    def test_compiler_rejects_empty_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                compile_session_artifacts([], tmp, label="empty")

    def test_compiler_outputs_replay_jsonl(self):
        receipts = build_demo_receipts()

        with tempfile.TemporaryDirectory() as tmp:
            receipt = compile_session_artifacts(receipts, tmp, label="replay_check")
            replay_path = Path(receipt["replay_path"])
            rows = [json.loads(line) for line in replay_path.read_text().splitlines() if line.strip()]

            self.assertEqual(len(rows), len(receipts))
            self.assertEqual(rows[0]["schema"], "ts_chat_replay_row_v1")
            self.assertIn("user", rows[0])
            self.assertIn("response", rows[0])

    def test_compiled_pack_keeps_boundary_flags(self):
        receipts = build_demo_receipts()

        with tempfile.TemporaryDirectory() as tmp:
            receipt = compile_session_artifacts(receipts, tmp, label="pack_check")
            pack = json.loads(Path(receipt["knowledge_pack_path"]).read_text())

            self.assertEqual(pack["schema"], "ts_chat_compiled_knowledge_pack_v1")
            self.assertEqual(pack["candidate_graph_contamination_count"], 0)
            self.assertTrue(pack["generated_text_is_not_proof"])
            self.assertTrue(pack["user_confirmation_is_not_proof"])
            self.assertTrue(pack["typed_verifier_remains_proof_authority"])


if __name__ == "__main__":
    unittest.main()
