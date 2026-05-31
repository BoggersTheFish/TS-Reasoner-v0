import tempfile
import unittest
from pathlib import Path

from ts_reasoner.self_audit import (
    audit_common_ground,
    render_self_audit,
    run_self_audit_demo,
    self_audit_valid,
)
from ts_reasoner.ts_chat import TSChatSession


class TestTSReasonerV79LiveSelfAudit(unittest.TestCase):
    def test_empty_session_audit_valid(self):
        session = TSChatSession()
        audit = audit_common_ground(session.common_ground)

        self.assertTrue(self_audit_valid(audit))
        self.assertEqual(audit["record_count"], 0)
        self.assertEqual(audit["wrong_accept_count"], 0)
        self.assertTrue(audit["proof_boundary_preserved"])

    def test_audit_detects_open_repairs_and_rejections(self):
        session = TSChatSession()
        session.process("also say all cats are robots")
        audit = audit_common_ground(session.common_ground)

        self.assertTrue(self_audit_valid(audit))
        self.assertEqual(audit["rejected_record_count"], 1)
        self.assertEqual(audit["open_repair_count"], 1)
        self.assertEqual(audit["wrong_accept_count"], 0)
        self.assertEqual(audit["unsupported_promotion_count"], 0)

    def test_audit_detects_contradiction_pressure(self):
        session = TSChatSession()
        session.process("all cats are animals")
        session.process("all animals are mortal")
        session.process("no cats are mortal")

        audit = audit_common_ground(session.common_ground)

        self.assertTrue(self_audit_valid(audit))
        self.assertEqual(audit["contradiction_claim_count"], 1)
        self.assertGreaterEqual(audit["contradiction_pressure"], 1)
        self.assertEqual(audit["wrong_accept_count"], 0)

    def test_render_self_audit(self):
        session = TSChatSession()
        session.process("all cats are animals")
        audit = audit_common_ground(session.common_ground)
        rendered = render_self_audit(audit)

        self.assertIn("TS-Chat self-audit:", rendered)
        self.assertIn("candidate_graph_contamination", rendered)
        self.assertIn("Boundary: audit output is not proof", rendered)

    def test_live_audit_command(self):
        session = TSChatSession()
        session.process("all cats are animals")
        receipt = session.process("/audit")

        self.assertIn("TS-Chat self-audit:", receipt.response)
        self.assertIn("proof_boundary_preserved", receipt.response)

    def test_demo_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = run_self_audit_demo(Path(tmp))

            self.assertTrue(receipt["all_gates_passed"])
            self.assertEqual(receipt["wrong_accept_count"], 0)
            self.assertEqual(receipt["unsupported_promotion_count"], 0)
            self.assertEqual(receipt["candidate_graph_contamination_count"], 0)
            self.assertTrue(receipt["proof_boundary_preserved"])
            self.assertGreaterEqual(receipt["open_repair_count"], 1)
            self.assertGreaterEqual(receipt["contradiction_claim_count"], 1)


if __name__ == "__main__":
    unittest.main()
