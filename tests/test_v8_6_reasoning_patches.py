from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.reasoning_patches import (
    evaluate_reasoning_patch_cases,
    make_reasoning_patch,
)


ROOT = Path(__file__).resolve().parents[1]


class ReasoningPatchLanguageTests(unittest.TestCase):
    def test_claim_added_patch_requires_verifier_support(self) -> None:
        patch = make_reasoning_patch(
            {
                "case_id": "accepted_claim_patch",
                "event_type": "claim_added",
                "before_claims": [],
                "after_claims": ["all cats are animals"],
                "payload": {"claim": "all cats are animals", "source": "typed_trace"},
            }
        )

        self.assertEqual(patch.patch_type, "claim_added")
        self.assertTrue(patch.state_changed)
        self.assertTrue(patch.requires_verifier_support)
        self.assertEqual(patch.candidate_graph_contamination_count, 0)

    def test_quarantine_patch_does_not_change_accepted_state(self) -> None:
        patch = make_reasoning_patch(
            {
                "case_id": "unsupported_claim_quarantine_patch",
                "event_type": "claim_quarantined",
                "before_claims": ["all cats are animals"],
                "after_claims": ["all cats are animals"],
                "payload": {"claim": "all cats are robots", "reason": "unsupported"},
            }
        )

        self.assertEqual(patch.patch_type, "claim_quarantined")
        self.assertFalse(patch.state_changed)
        self.assertFalse(patch.requires_verifier_support)
        self.assertEqual(patch.candidate_graph_contamination_count, 0)

    def test_dataset_eval_passes(self) -> None:
        cases = [
            json.loads(line)
            for line in (ROOT / "data" / "v8_6" / "reasoning_patch_cases.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        report = evaluate_reasoning_patch_cases(cases)

        self.assertTrue(report["all_gates_passed"])
        self.assertEqual(report["reasoning_patch_accuracy"], 1.0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)

    def test_script_generates_receipt(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/v8_6/evaluate_reasoning_patches.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        receipt = json.loads((ROOT / "artifacts" / "reasoning_patches_receipt.json").read_text(encoding="utf-8"))

        self.assertEqual(receipt["release"], "v8.6.0")
        self.assertTrue(receipt["all_gates_passed"])
        self.assertEqual(receipt["candidate_graph_contamination_count"], 0)
        self.assertTrue(receipt["patches_are_audit_records_not_proof"])


if __name__ == "__main__":
    unittest.main()
