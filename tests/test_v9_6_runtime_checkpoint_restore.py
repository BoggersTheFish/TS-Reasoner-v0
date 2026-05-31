from __future__ import annotations

import json
import subprocess
import sys
import unittest
from copy import deepcopy
from pathlib import Path

from ts_reasoner.runtime_checkpoint_restore import (
    build_checkpoint,
    evaluate_runtime_checkpoint_cases,
    restore_checkpoint,
)


ROOT = Path(__file__).resolve().parents[1]


class RuntimeCheckpointRestoreTests(unittest.TestCase):
    def test_checkpoint_restore_valid(self) -> None:
        result = build_checkpoint(
            case_id="checkpoint_identity_then_repair_restore",
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
        self.assertTrue(result.checkpoint_valid)
        self.assertTrue(result.restore_valid)
        self.assertTrue(result.head_hash_present)
        self.assertEqual(result.restored_state, result.checkpoint["state"])
        self.assertEqual(result.candidate_graph_contamination_count, 0)

    def test_tampered_checkpoint_rejected(self) -> None:
        result = build_checkpoint(
            case_id="checkpoint_branch_pack_restore",
            initial_state={
                "accepted_claims": ["all birds fly", "all dogs are animals"],
                "branch_worlds": [],
                "repair_targets": [],
                "quarantined_claims": [],
                "patches": [],
            },
            events=[
                {"event_type": "trusted_revision", "claim": "some birds do not fly", "source": "trusted_observation", "trust": 0.9},
                {"event_type": "knowledge_pack", "pack_schema_version": "bad", "unsupported_claims": ["all dogs are robots"], "source": "bad_pack"},
            ],
        )

        tampered = deepcopy(result.checkpoint)
        tampered["ledger"][0]["entry"]["action"] = "tampered_action"

        with self.assertRaises(ValueError):
            restore_checkpoint(tampered)

    def test_dataset_eval_passes(self) -> None:
        cases = [
            json.loads(line)
            for line in (ROOT / "data" / "v9_6" / "runtime_checkpoint_restore_cases.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        report = evaluate_runtime_checkpoint_cases(cases)

        self.assertTrue(report["all_gates_passed"])
        self.assertEqual(report["runtime_checkpoint_restore_accuracy"], 1.0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)

    def test_evaluator_generates_receipt(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/v9_6/evaluate_runtime_checkpoint_restore.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        receipt = json.loads((ROOT / "artifacts" / "runtime_checkpoint_restore_receipt.json").read_text(encoding="utf-8"))

        self.assertEqual(receipt["release"], "v9.6.0")
        self.assertTrue(receipt["all_gates_passed"])
        self.assertEqual(receipt["candidate_graph_contamination_count"], 0)
        self.assertTrue(receipt["checkpoint_contains_state_ledger_and_head_hash"])
        self.assertTrue(receipt["checkpoint_restore_is_valid"])
        self.assertTrue(receipt["ledger_hash_chain_verified_before_restore"])


if __name__ == "__main__":
    unittest.main()
