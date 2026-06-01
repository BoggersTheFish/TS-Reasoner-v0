from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_agl.os.first_contact_demo import run_first_contact_demo


ROOT = Path(__file__).resolve().parents[1]


class FirstContactDemoTests(unittest.TestCase):
    def test_demo_checks_pass(self) -> None:
        payload = run_first_contact_demo()
        self.assertTrue(payload["all_gates_passed"], payload)
        self.assertTrue(all(payload["checks"].values()))

    def test_script_prints_compact_pass_output(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/demo_first_contact.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("TS-Reasoner first-contact demo passed.", result.stdout)
        self.assertIn("Safe route: PASS", result.stdout)
        self.assertIn("Unsafe abstention: PASS", result.stdout)
        self.assertIn("External side effect blocked: PASS", result.stdout)
        self.assertIn("Typed proof boundary: PASS", result.stdout)
        self.assertIn("Receipt written: PASS", result.stdout)
        report = json.loads((ROOT / "artifacts/first_contact_demo_report.json").read_text(encoding="utf-8"))
        self.assertTrue(report["all_gates_passed"], report)


if __name__ == "__main__":
    unittest.main()
