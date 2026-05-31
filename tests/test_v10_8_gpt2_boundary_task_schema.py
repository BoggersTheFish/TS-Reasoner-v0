from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from benchmarks.gpt2_boundary.task_schema import validate_task


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "v10_8" / "gpt2_boundary_tasks.jsonl"
REPORT = ROOT / "artifacts" / "gpt2_boundary_task_schema_report.json"


class GPT2BoundaryTaskSchemaV108Tests(unittest.TestCase):
    def test_task_schema_gate(self) -> None:
        subprocess.run([sys.executable, "scripts/v10_8/evaluate_gpt2_boundary_task_schema.py"], cwd=ROOT, check=True)
        tasks = [json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip()]
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(len(tasks), 100)
        self.assertTrue(all(validate_task(task)["valid"] for task in tasks))
        self.assertEqual(report["task_count"], 100)
        self.assertEqual(report["schema_validity"], 1.0)
        self.assertEqual(report["expected_claim_parse_rate"], 1.0)
        self.assertEqual(report["trap_label_coverage"], 1.0)
        self.assertEqual(report["required_channel_coverage"], 1.0)
        self.assertTrue(report["all_gates_passed"])


if __name__ == "__main__":
    unittest.main()
