from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.support_path_verifier import verify_support_path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "artifacts" / "support_path_verifier_report.json"


class SupportPathVerifierV107Tests(unittest.TestCase):
    def test_supported_channels_and_blocks(self) -> None:
        self.assertEqual(
            verify_support_path(["all A are B"], "all A are B")["support"]["channel"],
            "direct_support",
        )
        self.assertEqual(
            verify_support_path(["all A are B", "all B are C"], "all A are C")["support"]["channel"],
            "transitive_all",
        )
        self.assertEqual(
            verify_support_path(["all A are B", "no B are C"], "no A are C")["support"]["channel"],
            "negative_exclusion",
        )
        self.assertEqual(
            verify_support_path(["all A are B"], "all B are A")["reason"],
            "reverse_inference_block",
        )
        self.assertEqual(
            verify_support_path(["all A are A"], "all A are A")["reason"],
            "identity_block",
        )

    def test_v10_7_evaluation_gates(self) -> None:
        subprocess.run([sys.executable, "scripts/v10_7/evaluate_support_path_verifier.py"], cwd=ROOT, check=True)
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["case_count"], 40)
        self.assertEqual(report["direct_support_accuracy"], 1.0)
        self.assertEqual(report["transitive_support_accuracy"], 1.0)
        self.assertEqual(report["negative_exclusion_accuracy"], 1.0)
        self.assertEqual(report["wrong_reverse_rejection_rate"], 1.0)
        self.assertEqual(report["identity_collapse_count"], 0)
        self.assertEqual(report["accepted_without_typed_support_count"], 0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)
        self.assertTrue(report["all_gates_passed"])


if __name__ == "__main__":
    unittest.main()
