from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.runtime_kernel import (
    VerifierFirstRuntimeKernel,
    evaluate_runtime_kernel_cases,
)


ROOT = Path(__file__).resolve().parents[1]


class RuntimeKernelTests(unittest.TestCase):
    def test_hostile_identity_event_quarantined(self) -> None:
        kernel = VerifierFirstRuntimeKernel()
        result = kernel.process_event(
            event={
                "event_type": "claim",
                "claim": "external llm was used",
                "source": "hostile_candidate",
                "trust": 0.2,
            },
            state={
                "accepted_claims": ["no external llm was used"],
                "branch_worlds": [],
                "repair_targets": [],
                "quarantined_claims": [],
                "patches": [],
            },
            case_id="kernel_hostile_identity",
        )

        self.assertEqual(result.action, "quarantine")
        self.assertEqual(result.audit["accepted_claim_count"], 1)
        self.assertEqual(result.audit["quarantined_claim_count"], 1)
        self.assertEqual(result.audit["patch_count"], 1)
        self.assertEqual(result.candidate_graph_contamination_count, 0)
        self.assertFalse(result.receipt["accepted_common_ground_mutated_by_candidate"])

    def test_trusted_revision_branches(self) -> None:
        kernel = VerifierFirstRuntimeKernel()
        result = kernel.process_event(
            event={
                "event_type": "trusted_revision",
                "claim": "some birds do not fly",
                "source": "trusted_observation",
                "trust": 0.9,
            },
            state={
                "accepted_claims": ["all birds fly"],
                "branch_worlds": [],
                "repair_targets": [],
                "quarantined_claims": [],
                "patches": [],
            },
            case_id="kernel_trusted_revision",
        )

        self.assertEqual(result.action, "branch_world")
        self.assertEqual(result.audit["accepted_claim_count"], 1)
        self.assertEqual(result.audit["branch_world_count"], 1)
        self.assertEqual(result.audit["patch_count"], 1)
        self.assertEqual(result.candidate_graph_contamination_count, 0)

    def test_dataset_eval_passes(self) -> None:
        cases = [
            json.loads(line)
            for line in (ROOT / "data" / "v9_0" / "runtime_kernel_cases.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        report = evaluate_runtime_kernel_cases(cases)

        self.assertTrue(report["all_gates_passed"])
        self.assertEqual(report["runtime_kernel_accuracy"], 1.0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)

    def test_script_generates_receipt(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/v9_0/evaluate_runtime_kernel.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        receipt = json.loads((ROOT / "artifacts" / "runtime_kernel_receipt.json").read_text(encoding="utf-8"))

        self.assertEqual(receipt["release"], "v9.0.0")
        self.assertTrue(receipt["all_gates_passed"])
        self.assertEqual(receipt["candidate_graph_contamination_count"], 0)
        self.assertTrue(receipt["kernel_routes_events_to_safe_actions"])
        self.assertTrue(receipt["accepted_common_ground_not_mutated_by_candidates"])


if __name__ == "__main__":
    unittest.main()
