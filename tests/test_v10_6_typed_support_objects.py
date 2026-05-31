from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.typed_support import make_typed_support, validate_typed_support


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "artifacts" / "typed_support_objects_report.json"
RECEIPT = ROOT / "artifacts" / "typed_support_objects_receipt.json"


class TypedSupportObjectsV106Tests(unittest.TestCase):
    def test_hash_checked_support_object_accepts_and_fake_support_rejects(self) -> None:
        support = make_typed_support(
            channel="transitive_all",
            premises=["all A are B", "all B are C"],
            derived_claim="all A are C",
        )
        self.assertTrue(validate_typed_support("all A are C", support)["accepted"])
        fake = dict(support)
        fake["trace_hash"] = "fake"
        self.assertFalse(validate_typed_support("all A are C", fake)["accepted"])
        self.assertFalse(validate_typed_support("all A are D", support)["accepted"])
        self.assertFalse(validate_typed_support("all A are C", [])["accepted"])

    def test_v10_6_evaluation_gates(self) -> None:
        subprocess.run([sys.executable, "scripts/v10_6/evaluate_typed_support_objects.py"], cwd=ROOT, check=True)
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        self.assertEqual(report["case_count"], 20)
        self.assertEqual(report["valid_support_acceptance_rate"], 1.0)
        self.assertEqual(report["fake_support_rejection_rate"], 1.0)
        self.assertEqual(report["mismatched_claim_rejection_rate"], 1.0)
        self.assertEqual(report["empty_support_rejection_rate"], 1.0)
        self.assertEqual(report["accepted_without_typed_support_count"], 0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)
        self.assertTrue(report["all_gates_passed"])
        self.assertTrue(receipt["all_gates_passed"])


if __name__ == "__main__":
    unittest.main()
