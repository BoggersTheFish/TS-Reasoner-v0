from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "artifacts" / "ts_reasoner_vs_gpt2_boundary_report.json"
RECEIPT = ROOT / "artifacts" / "v11_0_gpt2_boundary_arena_receipt.json"


class GPT2BoundaryArenaV110Tests(unittest.TestCase):
    def test_v11_arena_gates(self) -> None:
        subprocess.run([sys.executable, "scripts/v11_0/evaluate_gpt2_boundary_arena.py"], cwd=ROOT, check=True)
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        self.assertEqual(report["release"], "v11.0.0")
        self.assertEqual(report["task_count"], 100)
        self.assertTrue(report["ts_reasoner_beats_gpt2_small_on_answer_accuracy"])
        self.assertTrue(report["ts_reasoner_beats_gpt2_small_on_claim_accuracy"])
        self.assertTrue(report["ts_reasoner_beats_gpt2_small_on_support_path_accuracy"])
        self.assertTrue(report["ts_reasoner_beats_gpt2_small_on_contradiction_rejection"])
        self.assertTrue(report["ts_reasoner_beats_gpt2_small_on_unsupported_abstention"])
        self.assertEqual(report["ts_reasoner_support_path_accuracy"], 1.0)
        self.assertEqual(report["ts_reasoner_contradiction_rejection_rate"], 1.0)
        self.assertEqual(report["ts_reasoner_unsupported_abstention_rate"], 1.0)
        self.assertEqual(report["ts_reasoner_wrong_accept_count"], 0)
        self.assertEqual(report["ts_reasoner_accepted_without_typed_support_count"], 0)
        self.assertEqual(report["ts_reasoner_candidate_graph_contamination_count"], 0)
        self.assertTrue(report["all_gates_passed"])
        self.assertTrue(receipt["boundary"]["verifier_first_reasoning_boundary_result"])


if __name__ == "__main__":
    unittest.main()
