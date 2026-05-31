from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.contradiction_repair_policy import (
    RepairPolicyInput,
    decide_repair_policy,
    evaluate_policy_cases,
)


ROOT = Path(__file__).resolve().parents[1]


class ContradictionRepairPolicyTests(unittest.TestCase):
    def test_core_identity_violation_is_quarantined(self) -> None:
        decision = decide_repair_policy(
            RepairPolicyInput(
                case_id="core_identity_violation_external_llm",
                accepted_claim="no external llm was used",
                incoming_claim="external llm was used",
                claim_type="identity",
                incoming_source="hostile_candidate",
                source_trust="low",
            )
        )

        self.assertEqual(decision.action, "reject_and_quarantine")
        self.assertTrue(decision.repair_target_created)
        self.assertTrue(decision.accepted_claim_preserved)
        self.assertFalse(decision.incoming_claim_accepted)
        self.assertTrue(decision.quarantine_incoming)
        self.assertEqual(decision.candidate_graph_contamination_count, 0)

    def test_trusted_contradiction_branches_worlds(self) -> None:
        decision = decide_repair_policy(
            RepairPolicyInput(
                case_id="trusted_revision_candidate",
                accepted_claim="all birds fly",
                incoming_claim="some birds do not fly",
                claim_type="taxonomy",
                incoming_source="trusted_user_revision",
                source_trust="high",
            )
        )

        self.assertEqual(decision.action, "branch_worlds")
        self.assertTrue(decision.branch_created)
        self.assertTrue(decision.accepted_claim_preserved)
        self.assertFalse(decision.incoming_claim_accepted)
        self.assertEqual(decision.candidate_graph_contamination_count, 0)

    def test_dataset_policy_eval_passes(self) -> None:
        cases = [
            json.loads(line)
            for line in (ROOT / "data" / "v8_1" / "contradiction_repair_policy_cases.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        report = evaluate_policy_cases(cases)

        self.assertTrue(report["all_gates_passed"])
        self.assertEqual(report["policy_accuracy"], 1.0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)

    def test_script_generates_receipt(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/v8_1/evaluate_contradiction_repair_policy.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        receipt = json.loads((ROOT / "artifacts" / "contradiction_repair_policy_receipt.json").read_text(encoding="utf-8"))

        self.assertEqual(receipt["release"], "v8.1.0")
        self.assertTrue(receipt["all_gates_passed"])
        self.assertEqual(receipt["candidate_graph_contamination_count"], 0)
        self.assertTrue(receipt["typed_verifier_support_remains_proof_boundary"])


if __name__ == "__main__":
    unittest.main()
