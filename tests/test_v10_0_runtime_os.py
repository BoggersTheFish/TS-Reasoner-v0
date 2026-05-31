from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.runtime_os import RUNTIME_OS_SCHEMA, evaluate_runtime_os_cases, run_runtime_os_suite, run_runtime_session
from ts_reasoner.runtime_os_cli import run_session_payload, run_suite_payload


ROOT = Path(__file__).resolve().parents[1]


class RuntimeOSTests(unittest.TestCase):
    def test_runtime_session_unifies_replay_checkpoint_restore_and_receipt(self) -> None:
        result = run_runtime_session(
            case_id="v10_direct_session",
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

        self.assertEqual(result.schema, RUNTIME_OS_SCHEMA)
        self.assertEqual(result.actions, ["quarantine", "open_repair"])
        self.assertEqual(result.restored_state, result.final_state)
        self.assertTrue(result.receipt["unified_runtime_session"])
        self.assertEqual(result.candidate_graph_contamination_count, 0)

    def test_runtime_os_suite_passes_gates(self) -> None:
        suite = run_runtime_os_suite(
            case_id="v10_direct_suite",
            initial_state={
                "accepted_claims": ["all birds fly", "all dogs are animals"],
                "branch_worlds": [],
                "repair_targets": [],
                "quarantined_claims": [],
                "patches": [],
            },
            events=[
                {"event_type": "trusted_revision", "claim": "some birds do not fly", "source": "trusted_observation", "trust": 0.9},
                {"event_type": "knowledge_pack", "pack_schema_version": "bad", "unsupported_claims": ["all dogs are robots"]},
            ],
            continuation_events=[
                {"event_type": "knowledge_pack", "pack_schema_version": "1.0", "unsupported_claims": []}
            ],
        )

        self.assertTrue(suite["all_gates_passed"])
        self.assertEqual(suite["candidate_graph_contamination_count"], 0)
        self.assertIn("policy_contracts", suite)

    def test_cli_payload_helpers(self) -> None:
        session = json.loads((ROOT / "data" / "v10_0" / "runtime_os_session.json").read_text(encoding="utf-8"))

        exit_code, payload = run_session_payload(session)
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["action"], "runtime_session_completed")
        self.assertEqual(payload["candidate_graph_contamination_count"], 0)

        suite_code, suite_payload = run_suite_payload(session)
        self.assertEqual(suite_code, 0)
        self.assertEqual(suite_payload["action"], "runtime_os_suite_completed")
        self.assertTrue(suite_payload["all_gates_passed"])

    def test_subprocess_cli_suite(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ts_reasoner.runtime_os_cli",
                "suite",
                "--session",
                "@data/v10_0/runtime_os_session.json",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["action"], "runtime_os_suite_completed")
        self.assertTrue(payload["all_gates_passed"])
        self.assertEqual(payload["candidate_graph_contamination_count"], 0)

    def test_dataset_eval_passes(self) -> None:
        cases = [
            json.loads(line)
            for line in (ROOT / "data" / "v10_0" / "runtime_os_cases.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        report = evaluate_runtime_os_cases(cases)

        self.assertTrue(report["all_gates_passed"])
        self.assertEqual(report["runtime_os_accuracy"], 1.0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)

    def test_evaluator_generates_receipt(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/v10_0/evaluate_runtime_os.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        receipt = json.loads((ROOT / "artifacts" / "runtime_os_receipt.json").read_text(encoding="utf-8"))

        self.assertEqual(receipt["release"], "v10.0.0")
        self.assertTrue(receipt["all_gates_passed"])
        self.assertTrue(receipt["unified_runtime_session"])
        self.assertTrue(receipt["checkpoint_restore_available"])
        self.assertEqual(receipt["candidate_graph_contamination_count"], 0)


if __name__ == "__main__":
    unittest.main()
