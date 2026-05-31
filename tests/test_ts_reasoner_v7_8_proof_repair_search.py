import tempfile
import unittest
from pathlib import Path

from ts_reasoner.proof_repair_search import (
    contradiction_cut_search,
    missing_support_search,
    parse_relation_query,
    prove_relation,
    render_search_result,
    run_proof_repair_search_demo,
    search_result_valid,
)
from ts_reasoner.ts_chat import TSChatSession


class TestTSReasonerV78ProofRepairSearch(unittest.TestCase):
    def test_parse_relation_query(self):
        relation = parse_relation_query("all cats are mortal")
        self.assertEqual(relation.subject, "cats")
        self.assertEqual(relation.object, "mortal")

        negative = parse_relation_query("no cats are mortal")
        self.assertEqual(negative.subject, "cats")
        self.assertEqual(negative.object, "mortal")

    def test_prove_relation_finds_shortest_path(self):
        session = TSChatSession()
        session.process("all cats are animals")
        session.process("all animals are mortal")

        result = prove_relation(session.common_ground, parse_relation_query("all cats are mortal"))

        self.assertTrue(search_result_valid(result))
        self.assertEqual(result["status"], "supported")
        self.assertEqual(result["support_path_length"], 2)

    def test_missing_support_search_finds_partial_bridge(self):
        session = TSChatSession()
        session.process("all cats are machines")

        result = missing_support_search(session.common_ground, parse_relation_query("all cats are robots"))

        self.assertTrue(search_result_valid(result))
        self.assertEqual(result["status"], "missing_support")
        self.assertTrue(any(
            item["suggested_premise"] == "all machines are robots"
            for item in result["missing_edges"]
        ))

    def test_cut_search_suggests_support_premise_cuts(self):
        session = TSChatSession()
        session.process("all cats are animals")
        session.process("all animals are mortal")

        result = contradiction_cut_search(session.common_ground, parse_relation_query("no cats are mortal"))

        self.assertTrue(search_result_valid(result))
        self.assertTrue(result["positive_support_found"])
        self.assertEqual(result["cut_suggestion_count"], 2)

    def test_render_search_result(self):
        session = TSChatSession()
        session.process("all cats are animals")
        session.process("all animals are mortal")

        proof = prove_relation(session.common_ground, parse_relation_query("all cats are mortal"))
        rendered = render_search_result(proof)

        self.assertIn("Supported: all cats are mortal", rendered)
        self.assertIn("Shortest support path", rendered)

    def test_live_chat_commands(self):
        session = TSChatSession()
        session.process("all cats are animals")
        session.process("all animals are mortal")

        prove_receipt = session.process("/prove all cats are mortal")
        cut_receipt = session.process("/cut no cats are mortal")
        missing_receipt = session.process("/missing all cats are robots")

        self.assertIn("Supported: all cats are mortal", prove_receipt.response)
        self.assertIn("Cut search for contradiction: no cats are mortal", cut_receipt.response)
        self.assertIn("Missing search for: all cats are robots", missing_receipt.response)

    def test_demo_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = run_proof_repair_search_demo(Path(tmp))

            self.assertTrue(receipt["all_gates_passed"])
            self.assertGreaterEqual(receipt["prove_support_path_length"], 2)
            self.assertEqual(receipt["missing_status_after_repair"], "already_supported")
            self.assertGreaterEqual(receipt["cut_suggestion_count"], 2)
            self.assertEqual(receipt["candidate_graph_contamination_count"], 0)


if __name__ == "__main__":
    unittest.main()
