from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.runtime_state_ledger import evaluate_runtime_ledger_cases, run_runtime_ledger


ROOT = Path(__file__).resolve().parents[1]


class RuntimeStateLedgerTests(unittest.TestCase):
    def test_ledger_records_identity_then_repair(self) -> None:
        result = run_runtime_ledger(
            case_id="ledger_identity_then_repair",
            initial_state={
                "accepted_claims": ["no external llm was used", "all cats are animals"],
                "branch_worlds": [],
                "repair_targets": [],
                "quarantined_claims": [],
                "patches": [],
            },
            events=[
                {"event_type": "claim", "claim": "external llm was used", "source": "hostile_candidate", "trust": 0.2},
                {"event_type": "claim", "claim": "all cats are mortal", "source": "generated_text", "trust": 0.5},
            ],
        )

        self.assertEqual(result.actions, ["quarantine", "open_repair"])
        self.assertEqual(len(result.ledger), 2)
        self.assertTrue(result.append_only)
        self.assertEqual(result.ledger[0].index, 0)
        self.assertEqual(result.ledger[1].index, 1)
        self.assertEqual(result.candidate_graph_contamination_count, 0)

    def test_empty_session_is_safe(self) -> None:
        result = run_runtime_ledger(
            case_id="ledger_empty_session_safe",
            initial_state={
                "accepted_claims": ["all fish are animals"],
                "branch_worlds": [],
                "repair_targets": [],
                "quarantined_claims": [],
                "patches": [],
            },
            events=[],
        )

        self.assertEqual(result.actions, [])
        self.assertEqual(len(result.ledger), 0)
        self.assertTrue(result.append_only)
        self.assertEqual(result.candidate_graph_contamination_count, 0)

    def test_dataset_eval_passes(self) -> None:
        cases = [
            json.loads(line)
            for line in (ROOT / "data" / "v9_4" / "runtime_state_ledger_cases.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        report = evaluate_runtime_ledger_cases(cases)

        self.assertTrue(report["all_gates_passed"])
        self.assertEqual(report["runtime_state_ledger_accuracy"], 1.0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)

    def test_evaluator_generates_receipt(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/v9_4/evaluate_runtime_state_ledger.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        receipt = json.loads((ROOT / "artifacts" / "runtime_state_ledger_receipt.json").read_text(encoding="utf-8"))

        self.assertEqual(receipt["release"], "v9.4.0")
        self.assertTrue(receipt["all_gates_passed"])
        self.assertEqual(receipt["candidate_graph_contamination_count"], 0)
        self.assertTrue(receipt["ledger_is_append_only"])
        self.assertTrue(receipt["ledger_records_event_receipts"])


if __name__ == "__main__":
    unittest.main()
