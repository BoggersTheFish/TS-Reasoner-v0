from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from benchmarks.gpt2_boundary.gpt2_output_parser import parse_gpt2_output


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "artifacts" / "gpt2_small_baseline_report.json"
OUTPUTS = ROOT / "artifacts" / "gpt2_small_baseline_outputs.jsonl"


class GPT2SmallBaselineV109Tests(unittest.TestCase):
    def test_parser_handles_strict_labels(self) -> None:
        parsed = parse_gpt2_output("ANSWER: yes\nCLAIM: all A are C\nSUPPORT: fluent\nSTATUS: accepted\n")
        self.assertEqual(parsed["answer"], "yes")
        self.assertEqual(parsed["claim"], "all a are c")
        self.assertTrue(parsed["format_parse_ok"])

    def test_v10_9_baseline_harness(self) -> None:
        subprocess.run([sys.executable, "scripts/v10_9/evaluate_gpt2_small_baseline.py"], cwd=ROOT, check=True)
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        outputs = [json.loads(line) for line in OUTPUTS.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(report["model"], "gpt2-small")
        self.assertEqual(report["task_count"], 100)
        self.assertEqual(len(outputs), 100)
        self.assertTrue(report["baseline_frozen"])
        self.assertIn("answer_accuracy", report)
        self.assertIn("support_path_accuracy", report)
        self.assertIn("format_parse_rate", report)


if __name__ == "__main__":
    unittest.main()
