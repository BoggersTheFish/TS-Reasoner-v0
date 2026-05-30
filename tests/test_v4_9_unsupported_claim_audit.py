import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.claim_audit import (
    audit_candidate_claims,
    evaluate_claim_audit_cases,
    extract_audit_relations,
    load_jsonl,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/v4_9/unsupported_claim_audit_cases.jsonl"


class TestV49UnsupportedClaimAudit(unittest.TestCase):
    def test_extracts_multiple_claims(self):
        relations = extract_audit_relations(
            "Yes, all dogs are animals. Also, all dogs are reptiles."
        )
        self.assertEqual(len(relations), 2)
        self.assertEqual(relations[0].subject, "dogs")
        self.assertEqual(relations[0].object, "animals")
        self.assertEqual(relations[1].subject, "dogs")
        self.assertEqual(relations[1].object, "reptiles")

    def test_audit_detects_unsupported_extra_claim(self):
        audit = audit_candidate_claims(
            "Yes, all dogs are animals. Also, all dogs are reptiles.",
            ["all dogs are mammals", "all mammals are animals"],
        )

        self.assertEqual(audit["unsupported_claim_count"], 1)
        self.assertEqual(audit["unsupported_claims"][0]["subject"], "dogs")
        self.assertEqual(audit["unsupported_claims"][0]["object"], "reptiles")

    def test_audit_accepts_clean_supported_explanation(self):
        audit = audit_candidate_claims(
            "Yes, all dogs are mammals. All mammals are animals. All dogs are animals.",
            ["all dogs are mammals", "all mammals are animals"],
        )

        self.assertEqual(audit["unsupported_claim_count"], 0)

    def test_v49_report_gates(self):
        report = evaluate_claim_audit_cases(load_jsonl(DATA))

        self.assertEqual(report["version"], "v4.9-unsupported-claim-audit")
        self.assertEqual(report["case_count"], 8)
        self.assertEqual(report["candidate_count"], 24)
        self.assertGreater(report["unsupported_claim_candidate_count"], 0)
        self.assertEqual(report["arena_selection_accuracy"], 1.0)
        self.assertEqual(report["wrong_accept_count"], 0)
        self.assertEqual(report["accepted_without_typed_support_count"], 0)
        self.assertEqual(report["accepted_with_unsupported_claims_count"], 0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)
        self.assertTrue(report["gates"]["all_gates_passed"])

    def test_evaluator_script_writes_receipt(self):
        result = subprocess.run(
            [sys.executable, "scripts/v4_9/evaluate_unsupported_claim_audit.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn('"all_gates_passed": true', result.stdout)
        self.assertTrue((ROOT / "artifacts/v4_9_unsupported_claim_audit_report.json").exists())


if __name__ == "__main__":
    unittest.main()
