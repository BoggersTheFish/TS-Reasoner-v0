from __future__ import annotations

import json
import subprocess
import sys
import unittest
from copy import deepcopy
from pathlib import Path

from ts_reasoner.tamper_evident_runtime_ledger import (
    build_tamper_evident_ledger,
    evaluate_tamper_evident_ledger_cases,
    verify_hash_chain,
)


ROOT = Path(__file__).resolve().parents[1]


class TamperEvidentRuntimeLedgerTests(unittest.TestCase):
    def test_hash_chain_valid_and_tamper_detected(self) -> None:
        result = build_tamper_evident_ledger(
            case_id="hash_chain_identity_then_repair",
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

        chain = [entry.to_dict() for entry in result.hashed_ledger]

        self.assertTrue(result.chain_valid)
        self.assertTrue(verify_hash_chain(chain))
        self.assertTrue(result.tamper_detected)
        self.assertEqual(result.actions, ["quarantine", "open_repair"])
        self.assertEqual(result.candidate_graph_contamination_count, 0)

        tampered = deepcopy(chain)
        tampered[0]["entry"]["action"] = "tampered_action"
        self.assertFalse(verify_hash_chain(tampered))

    def test_empty_session_chain_valid_without_tamper_probe(self) -> None:
        result = build_tamper_evident_ledger(
            case_id="hash_chain_empty_session",
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
        self.assertEqual(len(result.hashed_ledger), 0)
        self.assertTrue(result.chain_valid)
        self.assertFalse(result.tamper_detected)
        self.assertEqual(result.candidate_graph_contamination_count, 0)

    def test_dataset_eval_passes(self) -> None:
        cases = [
            json.loads(line)
            for line in (ROOT / "data" / "v9_5" / "tamper_evident_ledger_cases.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        report = evaluate_tamper_evident_ledger_cases(cases)

        self.assertTrue(report["all_gates_passed"])
        self.assertEqual(report["tamper_evident_ledger_accuracy"], 1.0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)

    def test_evaluator_generates_receipt(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/v9_5/evaluate_tamper_evident_runtime_ledger.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        receipt = json.loads((ROOT / "artifacts" / "tamper_evident_runtime_ledger_receipt.json").read_text(encoding="utf-8"))

        self.assertEqual(receipt["release"], "v9.5.0")
        self.assertTrue(receipt["all_gates_passed"])
        self.assertEqual(receipt["candidate_graph_contamination_count"], 0)
        self.assertTrue(receipt["ledger_is_hash_chained"])
        self.assertTrue(receipt["tampering_is_detected"])


if __name__ == "__main__":
    unittest.main()
