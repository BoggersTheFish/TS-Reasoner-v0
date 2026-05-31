from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.adversarial_state_fuzzer import (
    evaluate_state_fuzzer_cases,
    run_state_fuzz_case,
)


ROOT = Path(__file__).resolve().parents[1]


class AdversarialStateFuzzerTests(unittest.TestCase):
    def test_hostile_identity_flip_quarantined(self) -> None:
        result = run_state_fuzz_case(
            {
                "case_id": "hostile_identity_flip",
                "initial_state": {
                    "accepted_claims": ["no external llm was used"],
                    "branch_worlds": [],
                    "repair_targets": [],
                    "quarantined_claims": [],
                    "patches": [],
                },
                "mutation": {
                    "type": "claim_injection",
                    "claim": "external llm was used",
                    "source": "hostile_candidate",
                },
            }
        )

        self.assertEqual(result.action, "quarantine")
        self.assertEqual(result.accepted_claims, ["no external llm was used"])
        self.assertEqual(result.quarantined_claims, ["external llm was used"])
        self.assertEqual(result.candidate_graph_contamination_count, 0)

    def test_trusted_revision_branches_without_mutating_base(self) -> None:
        result = run_state_fuzz_case(
            {
                "case_id": "trusted_revision_branch",
                "initial_state": {
                    "accepted_claims": ["all birds fly"],
                    "branch_worlds": [],
                    "repair_targets": [],
                    "quarantined_claims": [],
                    "patches": [],
                },
                "mutation": {
                    "type": "trusted_revision",
                    "claim": "some birds do not fly",
                    "source": "trusted_observation",
                },
            }
        )

        self.assertEqual(result.action, "branch_world")
        self.assertEqual(result.accepted_claims, ["all birds fly"])
        self.assertEqual(len(result.branch_worlds), 1)
        self.assertEqual(result.candidate_graph_contamination_count, 0)

    def test_dataset_eval_passes(self) -> None:
        cases = [
            json.loads(line)
            for line in (ROOT / "data" / "v8_8" / "adversarial_state_fuzzer_cases.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        report = evaluate_state_fuzzer_cases(cases)

        self.assertTrue(report["all_gates_passed"])
        self.assertEqual(report["adversarial_state_fuzzer_accuracy"], 1.0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)

    def test_script_generates_receipt(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/v8_8/evaluate_adversarial_state_fuzzer.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        receipt = json.loads((ROOT / "artifacts" / "adversarial_state_fuzzer_receipt.json").read_text(encoding="utf-8"))

        self.assertEqual(receipt["release"], "v8.8.0")
        self.assertTrue(receipt["all_gates_passed"])
        self.assertEqual(receipt["candidate_graph_contamination_count"], 0)
        self.assertTrue(receipt["hostile_mutations_do_not_contaminate_common_ground"])


if __name__ == "__main__":
    unittest.main()
