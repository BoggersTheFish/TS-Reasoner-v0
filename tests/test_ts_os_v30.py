from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TSOSV30Tests(unittest.TestCase):
    def test_v30_evaluator_composes_all_surfaces(self) -> None:
        subprocess.run([sys.executable, "scripts/evaluate_ts_os_chat_loop.py"], cwd=ROOT, check=True)
        subprocess.run([sys.executable, "scripts/show_proof_object_examples.py"], cwd=ROOT, check=True)
        subprocess.run([sys.executable, "scripts/demo_first_contact.py"], cwd=ROOT, check=True)
        subprocess.run([sys.executable, "scripts/build_ts_evidence_dashboard.py"], cwd=ROOT, check=True)
        subprocess.run([sys.executable, "scripts/evaluate_ts_os_v30.py"], cwd=ROOT, check=True)
        report = json.loads((ROOT / "artifacts/ts_os_v30_report.json").read_text(encoding="utf-8"))
        self.assertTrue(report["all_gates_passed"], report)
        self.assertTrue(report["checks"]["destructive_request_abstains"])
        self.assertTrue(report["checks"]["external_side_effect_blocked"])
        self.assertTrue(report["checks"]["unconfirmed_write_blocked"])
        self.assertEqual(report["external_side_effect_performed_count"], 0)
        self.assertEqual(report["network_call_performed_count"], 0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)


if __name__ == "__main__":
    unittest.main()
