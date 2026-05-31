from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.provenance_weighted_repair import (
    ProvenanceRepairInput,
    ProvenanceSource,
    decide_provenance_weighted_repair,
    evaluate_provenance_cases,
)


ROOT = Path(__file__).resolve().parents[1]


class ProvenanceWeightedRepairTests(unittest.TestCase):
    def test_canonical_beats_correlated_hostile_sources(self) -> None:
        decision = decide_provenance_weighted_repair(
            ProvenanceRepairInput(
                case_id="canonical_beats_correlated_hostile",
                accepted_claim="no external llm was used",
                incoming_claim="external llm was used",
                claim_type="identity",
                sources=[
                    ProvenanceSource("release_authority", "no external llm was used", 0.95, "canonical", "authority"),
                    ProvenanceSource("hostile_a", "external llm was used", 0.2, "hostile_cluster", "candidate"),
                    ProvenanceSource("hostile_b", "external llm was used", 0.2, "hostile_cluster", "candidate"),
                ],
            )
        )

        self.assertEqual(decision.winning_claim, "no external llm was used")
        self.assertEqual(decision.action, "reject_and_quarantine")
        self.assertTrue(decision.dependency_penalty_applied)
        self.assertTrue(decision.accepted_claim_preserved)
        self.assertFalse(decision.incoming_claim_accepted)
        self.assertEqual(decision.candidate_graph_contamination_count, 0)

    def test_independent_trusted_revision_branches(self) -> None:
        decision = decide_provenance_weighted_repair(
            ProvenanceRepairInput(
                case_id="trusted_independent_revision_branches",
                accepted_claim="all birds fly",
                incoming_claim="some birds do not fly",
                claim_type="taxonomy",
                sources=[
                    ProvenanceSource("old_rule", "all birds fly", 0.6, "legacy", "accepted"),
                    ProvenanceSource("trusted_observation", "some birds do not fly", 0.9, "field_observation", "revision"),
                ],
            )
        )

        self.assertEqual(decision.winning_claim, "some birds do not fly")
        self.assertEqual(decision.action, "branch_worlds")
        self.assertFalse(decision.dependency_penalty_applied)
        self.assertTrue(decision.accepted_claim_preserved)
        self.assertFalse(decision.incoming_claim_accepted)

    def test_dataset_eval_passes(self) -> None:
        cases = [
            json.loads(line)
            for line in (ROOT / "data" / "v8_3" / "provenance_weighted_repair_cases.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        report = evaluate_provenance_cases(cases)

        self.assertTrue(report["all_gates_passed"])
        self.assertEqual(report["provenance_decision_accuracy"], 1.0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)
        self.assertTrue(report["incoming_claims_not_auto_accepted"])

    def test_script_generates_receipt(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/v8_3/evaluate_provenance_weighted_repair.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        receipt = json.loads((ROOT / "artifacts" / "provenance_weighted_repair_receipt.json").read_text(encoding="utf-8"))

        self.assertEqual(receipt["release"], "v8.3.0")
        self.assertTrue(receipt["all_gates_passed"])
        self.assertEqual(receipt["candidate_graph_contamination_count"], 0)
        self.assertTrue(receipt["correlated_sources_are_downweighted"])
        self.assertTrue(receipt["typed_verifier_support_remains_proof_boundary"])


if __name__ == "__main__":
    unittest.main()
