from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_metacompute.scheduler import MetacomputeScheduler, SchedulerTask
from ts_metacompute.spectral.evaluate import evaluate_spectral_cases
from ts_metacompute.spectral.repairs import rank_repair_candidates
from ts_metacompute.spectral.signed_graph import SignedGraph


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "spectral_cases.jsonl"
REPORT = ROOT / "artifacts" / "spectral_metacompute_report.json"
RECEIPT = ROOT / "artifacts" / "spectral_metacompute_receipt.json"


def load_cases() -> list[dict]:
    return [json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip()]


class SpectralMetacomputeTests(unittest.TestCase):
    def test_signed_graph_spectral_reader_detects_planted_bad_edge_without_accepting(self) -> None:
        case = next(row for row in load_cases() if row["case_id"] == "planted_bad_edge")
        graph = SignedGraph.from_dict(case)
        payload = MetacomputeScheduler().run(SchedulerTask(task_type="repair_ranking", graph=graph))

        self.assertTrue(payload["contradiction_detected"])
        self.assertEqual(payload["top_edge_id"], "bad_ac")
        self.assertEqual(payload["accepted_without_verifier_support_count"], 0)
        self.assertFalse(payload["accepted_truth"])

        repairs = rank_repair_candidates(graph)
        self.assertEqual(repairs[0].edge_id, "bad_ac")
        self.assertEqual(repairs[0].action, "flip_relation_candidate")
        self.assertEqual(repairs[0].proof_effect, "candidate_only")

    def test_ambiguous_frustrated_loop_abstains_from_unique_culprit(self) -> None:
        case = next(row for row in load_cases() if row["case_id"] == "contradiction_triangle")
        graph = SignedGraph.from_dict(case)
        payload = MetacomputeScheduler().run(SchedulerTask(task_type="repair_ranking", graph=graph))

        self.assertTrue(payload["contradiction_detected"])
        self.assertEqual(payload["reader_decision"], "abstain_no_unique_culprit")
        self.assertFalse(payload["unique_top_residual"])

    def test_dataset_eval_gates(self) -> None:
        report = evaluate_spectral_cases(load_cases())

        self.assertTrue(report["all_gates_passed"])
        metrics = report["metrics"]
        self.assertEqual(metrics["case_count"], 8)
        self.assertEqual(metrics["coherence_detection_rate"], 1.0)
        self.assertEqual(metrics["contradiction_detection_rate"], 1.0)
        self.assertEqual(metrics["planted_bad_edge_top1_rate"], 1.0)
        self.assertEqual(metrics["repair_relief_accuracy"], 1.0)
        self.assertEqual(metrics["ambiguous_loop_correct_abstention"], 1.0)
        self.assertEqual(metrics["wrong_accept_count"], 0)
        self.assertEqual(metrics["accepted_without_verifier_support_count"], 0)
        self.assertEqual(metrics["candidate_graph_contamination_count"], 0)
        self.assertEqual(metrics["receipt_schema_validity"], 1.0)

    def test_script_generates_report_and_receipt(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/evaluate_spectral_metacompute.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))

        self.assertTrue(report["all_gates_passed"])
        self.assertEqual(receipt["release"], "ts-spectralcompute-v0.1")
        self.assertTrue(receipt["all_gates_passed"])
        self.assertTrue(receipt["receipt_schema_valid"])
        self.assertEqual(receipt["proof_boundary"], "spectral_reader_suggests_verifier_decides")


if __name__ == "__main__":
    unittest.main()
