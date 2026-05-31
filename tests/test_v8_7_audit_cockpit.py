from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.audit_cockpit import audit_state, evaluate_audit_cockpit_cases


ROOT = Path(__file__).resolve().parents[1]


class AuditCockpitTests(unittest.TestCase):
    def test_status_summary_counts_state(self) -> None:
        result = audit_state(
            command="status",
            state={
                "accepted_claims": ["all cats are animals"],
                "repair_targets": [],
                "branch_worlds": [],
                "quarantined_claims": [],
                "patches": [],
            },
            case_id="status_summary",
        )

        self.assertEqual(result.output["accepted_claim_count"], 1)
        self.assertEqual(result.output["repair_target_count"], 0)
        self.assertEqual(result.candidate_graph_contamination_count, 0)

    def test_full_audit_does_not_mutate_state(self) -> None:
        state = {
            "accepted_claims": ["all cats are animals"],
            "repair_targets": [{"target_claim": "all cats are mortal", "repair_type": "missing_bridge"}],
            "branch_worlds": [{"world_id": "main__branch__cats", "parent_world_id": "main"}],
            "quarantined_claims": ["all cats are robots"],
            "patches": [{"patch_type": "repair_opened", "target_claim": "all cats are mortal"}],
        }

        before = json.dumps(state, sort_keys=True)
        result = audit_state(command="audit", state=state, case_id="full_audit_summary")
        after = json.dumps(state, sort_keys=True)

        self.assertEqual(before, after)
        self.assertEqual(result.output["accepted_claim_count"], 1)
        self.assertEqual(result.output["repair_target_count"], 1)
        self.assertEqual(result.output["branch_world_count"], 1)
        self.assertEqual(result.output["quarantined_claim_count"], 1)
        self.assertEqual(result.output["patch_count"], 1)
        self.assertEqual(result.candidate_graph_contamination_count, 0)

    def test_dataset_eval_passes(self) -> None:
        cases = [
            json.loads(line)
            for line in (ROOT / "data" / "v8_7" / "audit_cockpit_cases.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        report = evaluate_audit_cockpit_cases(cases)

        self.assertTrue(report["all_gates_passed"])
        self.assertEqual(report["audit_cockpit_accuracy"], 1.0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)

    def test_script_generates_receipt(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/v8_7/evaluate_audit_cockpit.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        receipt = json.loads((ROOT / "artifacts" / "audit_cockpit_receipt.json").read_text(encoding="utf-8"))

        self.assertEqual(receipt["release"], "v8.7.0")
        self.assertTrue(receipt["all_gates_passed"])
        self.assertEqual(receipt["candidate_graph_contamination_count"], 0)
        self.assertTrue(receipt["audit_reports_do_not_mutate_state"])


if __name__ == "__main__":
    unittest.main()
