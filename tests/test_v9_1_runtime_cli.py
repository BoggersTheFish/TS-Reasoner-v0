from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.runtime_cli import process_event


ROOT = Path(__file__).resolve().parents[1]


class RuntimeCliTests(unittest.TestCase):
    def test_process_event_function_routes_to_kernel(self) -> None:
        exit_code, payload = process_event(
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
            case_id="cli_hostile_identity",
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["action"], "quarantine")
        self.assertEqual(payload["candidate_graph_contamination_count"], 0)

    def test_invalid_input_rejected_safely(self) -> None:
        exit_code, payload = process_event(
            event="not-json-object",
            state={
                "accepted_claims": [],
                "branch_worlds": [],
                "repair_targets": [],
                "quarantined_claims": [],
                "patches": [],
            },
            case_id="cli_bad_json_rejected",
        )

        self.assertEqual(exit_code, 2)
        self.assertEqual(payload["action"], "invalid_input")
        self.assertEqual(payload["candidate_graph_contamination_count"], 0)

    def test_cli_subprocess_outputs_json(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ts_reasoner.runtime_cli",
                "process-event",
                "--event",
                json.dumps({
                    "event_type": "trusted_revision",
                    "claim": "some birds do not fly",
                    "source": "trusted_observation",
                    "trust": 0.9,
                }),
                "--state",
                json.dumps({
                    "accepted_claims": ["all birds fly"],
                    "branch_worlds": [],
                    "repair_targets": [],
                    "quarantined_claims": [],
                    "patches": [],
                }),
                "--case-id",
                "cli_trusted_revision",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["action"], "branch_world")
        self.assertEqual(payload["candidate_graph_contamination_count"], 0)

    def test_evaluator_generates_receipt(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/v9_1/evaluate_runtime_cli.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        receipt = json.loads((ROOT / "artifacts" / "runtime_cli_receipt.json").read_text(encoding="utf-8"))

        self.assertEqual(receipt["release"], "v9.1.0")
        self.assertTrue(receipt["all_gates_passed"])
        self.assertEqual(receipt["candidate_graph_contamination_count"], 0)
        self.assertTrue(receipt["cli_routes_events_to_kernel"])
        self.assertTrue(receipt["invalid_cli_input_rejected_safely"])


if __name__ == "__main__":
    unittest.main()
