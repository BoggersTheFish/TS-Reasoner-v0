from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.branching_worlds import apply_branching_policy, evaluate_branching_world_cases


ROOT = Path(__file__).resolve().parents[1]


class BranchingWorldsRuntimeTests(unittest.TestCase):
    def test_trusted_revision_creates_branch(self) -> None:
        result = apply_branching_policy(
            case_id="trusted_revision_branches_birds",
            base_world_id="main",
            base_claims=["all birds fly"],
            incoming_claim="some birds do not fly",
            branch_reason="trusted_revision_contradiction",
        )

        self.assertEqual(result.world_count, 2)
        self.assertTrue(result.base_preserved)
        self.assertTrue(result.branch_contains_incoming)
        self.assertFalse(result.auto_merge)
        self.assertEqual(result.candidate_graph_contamination_count, 0)
        self.assertEqual(result.worlds[1].parent_world_id, "main")

    def test_identity_violation_does_not_branch(self) -> None:
        result = apply_branching_policy(
            case_id="identity_violation_quarantines_not_branch",
            base_world_id="main",
            base_claims=["no external llm was used"],
            incoming_claim="external llm was used",
            branch_reason="identity_violation",
        )

        self.assertEqual(result.world_count, 1)
        self.assertTrue(result.base_preserved)
        self.assertFalse(result.branch_contains_incoming)
        self.assertEqual(result.candidate_graph_contamination_count, 0)

    def test_dataset_eval_passes(self) -> None:
        cases = [
            json.loads(line)
            for line in (ROOT / "data" / "v8_4" / "branching_worlds_cases.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        report = evaluate_branching_world_cases(cases)

        self.assertTrue(report["all_gates_passed"])
        self.assertEqual(report["branching_world_accuracy"], 1.0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)
        self.assertEqual(report["auto_merge_count"], 0)

    def test_script_generates_receipt(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/v8_4/evaluate_branching_worlds.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        receipt = json.loads((ROOT / "artifacts" / "branching_worlds_receipt.json").read_text(encoding="utf-8"))

        self.assertEqual(receipt["release"], "v8.4.0")
        self.assertTrue(receipt["all_gates_passed"])
        self.assertEqual(receipt["candidate_graph_contamination_count"], 0)
        self.assertEqual(receipt["auto_merge_count"], 0)
        self.assertTrue(receipt["branching_is_not_acceptance"])


if __name__ == "__main__":
    unittest.main()
