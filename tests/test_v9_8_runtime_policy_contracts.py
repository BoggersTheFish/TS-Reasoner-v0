from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.runtime_kernel import VerifierFirstRuntimeKernel
from ts_reasoner.runtime_policy_contracts import (
    evaluate_policy_contract_cases,
    policy_contract_document,
    validate_runtime_action_contract,
)


ROOT = Path(__file__).resolve().parents[1]


class RuntimePolicyContractsTests(unittest.TestCase):
    def test_runtime_action_contract_validates_kernel_action(self) -> None:
        kernel = VerifierFirstRuntimeKernel()
        result = kernel.process_event(
            event={"event_type": "claim", "claim": "external llm was used", "source": "hostile_candidate"},
            state={
                "accepted_claims": ["no external llm was used"],
                "branch_worlds": [],
                "repair_targets": [],
                "quarantined_claims": [],
                "patches": [],
            },
            case_id="policy_contract_direct",
        )

        contract = validate_runtime_action_contract(
            case_id="policy_contract_direct",
            action=result.action,
            state=result.state,
            receipt=result.receipt,
            contamination=result.candidate_graph_contamination_count,
        )

        self.assertTrue(contract.contract_valid)
        self.assertEqual(contract.action, "quarantine")
        self.assertEqual(contract.candidate_graph_contamination_count, 0)

    def test_missing_contract_field_fails_validation(self) -> None:
        contract = validate_runtime_action_contract(
            case_id="policy_contract_missing",
            action="open_repair",
            state={"accepted_claims": []},
            receipt={"action": "open_repair"},
            contamination=0,
        )

        self.assertFalse(contract.contract_valid)
        self.assertIn("repair_targets", contract.missing_state_keys)
        self.assertIn("typed_verifier_support_remains_proof_boundary", contract.missing_receipt_keys)

    def test_policy_contract_document_contains_checkpoint_and_restore(self) -> None:
        document = policy_contract_document()

        self.assertEqual(document["schema"], "ts_reasoner_runtime_policy_contracts_v1")
        self.assertIn("checkpoint", document["contracts"])
        self.assertIn("restore", document["contracts"])
        self.assertTrue(document["proof_boundary"]["typed_verifier_support_remains_proof_boundary"])

    def test_dataset_eval_passes(self) -> None:
        cases = [
            json.loads(line)
            for line in (ROOT / "data" / "v9_8" / "runtime_policy_contract_cases.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        report = evaluate_policy_contract_cases(cases)

        self.assertTrue(report["all_gates_passed"])
        self.assertEqual(report["runtime_policy_contract_accuracy"], 1.0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)

    def test_evaluator_generates_receipt(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/v9_8/evaluate_runtime_policy_contracts.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        receipt = json.loads((ROOT / "artifacts" / "runtime_policy_contracts_receipt.json").read_text(encoding="utf-8"))

        self.assertEqual(receipt["release"], "v9.8.0")
        self.assertTrue(receipt["all_gates_passed"])
        self.assertTrue(receipt["runtime_actions_are_contract_defined"])
        self.assertEqual(receipt["candidate_graph_contamination_count"], 0)


if __name__ == "__main__":
    unittest.main()
