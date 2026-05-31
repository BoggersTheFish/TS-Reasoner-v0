from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.runtime_recovery_drill import evaluate_recovery_drill_cases, run_recovery_drill


ROOT = Path(__file__).resolve().parents[1]


class RuntimeRecoveryDrillTests(unittest.TestCase):
    def test_recovery_drill_rejects_corruption_and_continues(self) -> None:
        result = run_recovery_drill(
            case_id="recovery_direct",
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
            continuation_events=[
                {"event_type": "trusted_revision", "claim": "some birds do not fly", "source": "trusted_observation", "trust": 0.9}
            ],
        )

        self.assertEqual(result.base_actions, ["quarantine", "open_repair"])
        self.assertEqual(result.continued_actions, ["branch_world"])
        self.assertTrue(result.checkpoint_valid)
        self.assertTrue(result.restore_valid)
        self.assertTrue(result.corrupt_checkpoint_rejected)
        self.assertTrue(result.reordered_ledger_rejected)
        self.assertTrue(result.missing_event_replay_diverged)
        self.assertTrue(result.restored_then_continued)
        self.assertEqual(result.candidate_graph_contamination_count, 0)

    def test_dataset_eval_passes(self) -> None:
        cases = [
            json.loads(line)
            for line in (ROOT / "data" / "v9_9" / "runtime_recovery_drill_cases.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        report = evaluate_recovery_drill_cases(cases)

        self.assertTrue(report["all_gates_passed"])
        self.assertEqual(report["runtime_recovery_drill_accuracy"], 1.0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)

    def test_evaluator_generates_receipt(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/v9_9/evaluate_runtime_recovery_drill.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        receipt = json.loads((ROOT / "artifacts" / "runtime_recovery_drill_receipt.json").read_text(encoding="utf-8"))

        self.assertEqual(receipt["release"], "v9.9.0")
        self.assertTrue(receipt["all_gates_passed"])
        self.assertTrue(receipt["corrupt_checkpoint_rejected"])
        self.assertTrue(receipt["restore_then_continue_supported"])
        self.assertEqual(receipt["candidate_graph_contamination_count"], 0)


if __name__ == "__main__":
    unittest.main()
