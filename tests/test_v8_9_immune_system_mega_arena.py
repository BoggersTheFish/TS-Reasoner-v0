from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.immune_system_mega_arena import (
    evaluate_mega_arena_cases,
    run_mega_arena_case,
)


ROOT = Path(__file__).resolve().parents[1]


class ImmuneSystemMegaArenaTests(unittest.TestCase):
    def test_hostile_identity_attack_quarantined(self) -> None:
        result = run_mega_arena_case(
            {
                "case_id": "hostile_identity_full_stack",
                "scenario_type": "identity_attack",
                "accepted_claims": ["no external llm was used"],
                "incoming_claim": "external llm was used",
            }
        )

        self.assertEqual(result.action, "quarantine")
        self.assertEqual(result.accepted_claims, ["no external llm was used"])
        self.assertEqual(result.quarantined_claims, ["external llm was used"])
        self.assertEqual(len(result.patches), 1)
        self.assertEqual(result.candidate_graph_contamination_count, 0)

    def test_trusted_revision_branches_without_auto_merge(self) -> None:
        result = run_mega_arena_case(
            {
                "case_id": "trusted_revision_world_branch",
                "scenario_type": "trusted_revision",
                "accepted_claims": ["all birds fly"],
                "incoming_claim": "some birds do not fly",
            }
        )

        self.assertEqual(result.action, "branch_world")
        self.assertEqual(result.accepted_claims, ["all birds fly"])
        self.assertEqual(len(result.branch_worlds), 1)
        self.assertFalse(result.branch_worlds[0]["auto_merge_allowed"])
        self.assertEqual(result.candidate_graph_contamination_count, 0)

    def test_dataset_eval_passes(self) -> None:
        cases = [
            json.loads(line)
            for line in (ROOT / "data" / "v8_9" / "immune_system_mega_arena_cases.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        report = evaluate_mega_arena_cases(cases)

        self.assertTrue(report["all_gates_passed"])
        self.assertEqual(report["mega_arena_accuracy"], 1.0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)

    def test_script_generates_receipt(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/v8_9/evaluate_immune_system_mega_arena.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        receipt = json.loads((ROOT / "artifacts" / "immune_system_mega_arena_receipt.json").read_text(encoding="utf-8"))

        self.assertEqual(receipt["release"], "v8.9.0")
        self.assertTrue(receipt["all_gates_passed"])
        self.assertEqual(receipt["candidate_graph_contamination_count"], 0)
        self.assertTrue(receipt["hostile_inputs_do_not_contaminate_common_ground"])
        self.assertTrue(receipt["branches_do_not_auto_merge"])
        self.assertTrue(receipt["repair_targets_are_not_proof"])
        self.assertTrue(receipt["patches_are_audit_records_not_proof"])


if __name__ == "__main__":
    unittest.main()
