from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.runtime_replay import evaluate_runtime_replay_cases, replay_events


ROOT = Path(__file__).resolve().parents[1]


class RuntimeReplayTests(unittest.TestCase):
    def test_replay_identity_then_repair(self) -> None:
        result = replay_events(
            case_id="replay_identity_then_repair",
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
        self.assertEqual(result.audit["accepted_claim_count"], 2)
        self.assertEqual(result.audit["quarantined_claim_count"], 1)
        self.assertEqual(result.audit["repair_target_count"], 1)
        self.assertEqual(result.audit["patch_count"], 2)
        self.assertEqual(result.candidate_graph_contamination_count, 0)

    def test_replay_preserves_event_order(self) -> None:
        result = replay_events(
            case_id="replay_all_routes",
            initial_state={
                "accepted_claims": ["no external llm was used", "all cats are animals", "all birds fly"],
                "branch_worlds": [],
                "repair_targets": [],
                "quarantined_claims": [],
                "patches": [],
            },
            events=[
                {"event_type": "claim", "claim": "external llm was used", "source": "hostile_candidate", "trust": 0.2},
                {"event_type": "claim", "claim": "all cats are mortal", "source": "generated_text", "trust": 0.5},
                {"event_type": "trusted_revision", "claim": "some birds do not fly", "source": "trusted_observation", "trust": 0.9},
            ],
        )

        self.assertEqual(result.actions, ["quarantine", "open_repair", "branch_world"])
        self.assertEqual(len(result.receipts), 3)
        self.assertEqual(result.candidate_graph_contamination_count, 0)

    def test_dataset_eval_passes(self) -> None:
        cases = [
            json.loads(line)
            for line in (ROOT / "data" / "v9_2" / "runtime_replay_cases.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        report = evaluate_runtime_replay_cases(cases)

        self.assertTrue(report["all_gates_passed"])
        self.assertEqual(report["runtime_replay_accuracy"], 1.0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)

    def test_evaluator_generates_receipt(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/v9_2/evaluate_runtime_replay.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        receipt = json.loads((ROOT / "artifacts" / "runtime_replay_receipt.json").read_text(encoding="utf-8"))

        self.assertEqual(receipt["release"], "v9.2.0")
        self.assertTrue(receipt["all_gates_passed"])
        self.assertEqual(receipt["candidate_graph_contamination_count"], 0)
        self.assertTrue(receipt["multi_event_sessions_route_through_kernel"])
        self.assertTrue(receipt["replay_preserves_event_order"])


if __name__ == "__main__":
    unittest.main()
