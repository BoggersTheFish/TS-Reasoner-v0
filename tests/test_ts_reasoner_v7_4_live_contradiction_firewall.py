import unittest

from ts_reasoner.live_contradiction_firewall import (
    contradiction_trace_from_record,
    live_contradiction_trace_valid,
    parse_no_relation,
    record_negative_claim_result,
)
from ts_reasoner.ts_chat import TSChatSession


class TestTSReasonerV74LiveContradictionFirewall(unittest.TestCase):
    def test_parse_no_relation(self):
        relation = parse_no_relation("no cats are mortal")

        self.assertIsNotNone(relation)
        self.assertEqual(relation.subject, "cats")
        self.assertEqual(relation.object, "mortal")

    def test_parse_no_relation_rejects_non_negative(self):
        self.assertIsNone(parse_no_relation("all cats are mortal"))

    def test_live_contradiction_rejected_with_support_path(self):
        session = TSChatSession()
        session.process("all cats are animals")
        session.process("all animals are mortal")
        receipt = session.process("no cats are mortal")

        records = receipt.records_created
        contradiction = [r for r in records if r.get("kind") == "contradiction_claim"]
        repairs = [r["repair_target"] for r in records if "repair_target" in r]

        self.assertEqual(len(contradiction), 1)
        self.assertEqual(contradiction[0]["status"], "rejected")
        self.assertEqual(
            contradiction[0]["support_path"],
            [
                {"subject": "cats", "object": "animals"},
                {"subject": "animals", "object": "mortal"},
            ],
        )
        self.assertEqual(len(repairs), 1)
        self.assertEqual(repairs[0]["kind"], "contradiction")
        self.assertNotIn(("cats", "mortal"), session.common_ground.accepted_edges)

    def test_negative_claim_without_positive_support_abstains(self):
        session = TSChatSession()
        receipt = session.process("no cats are robots")

        records = receipt.records_created
        negative = [r for r in records if r.get("kind") == "negative_claim"]

        self.assertEqual(len(negative), 1)
        self.assertEqual(negative[0]["status"], "abstained")
        self.assertEqual(negative[0]["support_path"], [])
        self.assertEqual(len(session.common_ground.repair_targets), 0)

    def test_contradiction_trace_valid(self):
        session = TSChatSession()
        session.process("all cats are animals")
        session.process("all animals are mortal")
        session.process("no cats are mortal")

        contradiction_records = [
            record for record in session.common_ground.records
            if record.kind == "contradiction_claim"
        ]
        self.assertEqual(len(contradiction_records), 1)

        trace = contradiction_trace_from_record(contradiction_records[0])
        self.assertTrue(live_contradiction_trace_valid(trace))
        self.assertFalse(trace["creates_proof"])
        self.assertFalse(trace["external_llm_used"])

    def test_record_negative_claim_result_directly(self):
        session = TSChatSession()
        session.process("all cats are animals")
        session.process("all animals are mortal")

        session.common_ground.next_turn()
        relation = parse_no_relation("no cats are mortal")
        record, repair = record_negative_claim_result(session.common_ground, relation)

        self.assertEqual(record.status, "rejected")
        self.assertEqual(record.kind, "contradiction_claim")
        self.assertIsNotNone(repair)
        self.assertEqual(repair.kind, "contradiction")


if __name__ == "__main__":
    unittest.main()
