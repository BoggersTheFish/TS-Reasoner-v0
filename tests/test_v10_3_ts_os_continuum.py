from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.ts_os import run_continuum_scenario


ROOT = Path(__file__).resolve().parents[1]


class TSOSContinuumTests(unittest.TestCase):
    def test_infrastructure_grid_forks_and_evaluates_worlds(self) -> None:
        scenario = json.loads((ROOT / "data" / "v10_3" / "infrastructure_grid_scenario.json").read_text())
        report = run_continuum_scenario(scenario)

        self.assertTrue(report.all_gates_passed)
        self.assertEqual(report.contamination_count, 0)
        self.assertIn("world_contradiction", [item["world_id"] for item in report.fork_receipts])
        self.assertIn("world_supported_revision", report.merge_candidates)
        self.assertIn("world_water_shock", report.quarantined_worlds)

    def test_unsafe_merge_is_blocked_until_supported(self) -> None:
        report = run_continuum_scenario({
            "nodes": ["power", "hospital"],
            "edges": [{"from": "power", "to": "hospital"}],
            "events": [{"event_type": "missing_support", "world_id": "unsafe", "claims": ["hospital ok"], "affected": ["hospital"]}],
        })
        outcome = report.outcomes[0]
        self.assertEqual(outcome["outcome"], "quarantined")
        self.assertFalse(outcome["merge_allowed"])

    def test_continuum_cli_exposes_standard_contamination_gate(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ts_reasoner.runtime_os_cli",
                "run-continuum",
                "--scenario",
                "@data/v10_3/infrastructure_grid_scenario.json",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["candidate_graph_contamination_count"], 0)


if __name__ == "__main__":
    unittest.main()
