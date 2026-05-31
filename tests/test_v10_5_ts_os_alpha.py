from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.ts_os import run_alpha_scenario


ROOT = Path(__file__).resolve().parents[1]


class TSOSAlphaTests(unittest.TestCase):
    def test_alpha_scenario_passes_zero_contamination_gate(self) -> None:
        scenario = json.loads((ROOT / "data" / "v10_5" / "ts_os_alpha_scenario.json").read_text())
        payload = run_alpha_scenario(scenario)
        self.assertTrue(payload["all_gates_passed"])
        self.assertEqual(payload["candidate_graph_contamination_count"], 0)
        self.assertEqual(payload["receipt"]["release"], "v10.5")
        self.assertIn("untrusted userspace proposers", payload["receipt"]["claim"])

    def test_alpha_cli(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ts_reasoner.runtime_os_cli",
                "alpha",
                "--scenario",
                "@data/v10_5/ts_os_alpha_scenario.json",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["action"], "ts_os_alpha_completed")
        self.assertEqual(payload["candidate_graph_contamination_count"], 0)


if __name__ == "__main__":
    unittest.main()
