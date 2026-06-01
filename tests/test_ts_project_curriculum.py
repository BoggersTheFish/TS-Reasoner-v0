from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_agl.registry import DomainRegistry
from ts_agl.registry.manifest_validator import validate_manifest
from ts_agl.router import Dispatcher, OperationRouter
from ts_agl.router.example_router import TeachingExampleRouter


ROOT = Path(__file__).resolve().parents[1]


class TSProjectCurriculumTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = DomainRegistry().load()
        self.router = TeachingExampleRouter(self.registry)

    def test_ts_project_domain_pack_is_valid(self) -> None:
        manifest = self.registry.get_domain("ts_project")
        report = validate_manifest(manifest)

        self.assertTrue(report.valid, report.to_dict())
        self.assertEqual(manifest["curriculum_contract"]["release"], "v31.0.0")
        self.assertTrue(manifest["curriculum_contract"]["bounded_curriculum_learning"])
        self.assertFalse(manifest["curriculum_contract"]["open_ended_self_learning"])
        for node_type in [
            "repo",
            "release",
            "artifact",
            "receipt",
            "claim",
            "proof_boundary",
            "unsafe_overclaim",
            "next_safe_action",
            "stale_public_surface",
            "missing_receipt",
        ]:
            self.assertIn(node_type, manifest["node_types"])

    def test_domain_examples_route_to_project_operations(self) -> None:
        expectations = {
            "inspect TS-Reasoner project state": "inspect_project_state",
            "find missing receipts": "find_missing_receipts",
            "find stale public surface": "detect_stale_public_surface",
            "what is built and not fully built?": "inspect_proof_boundary",
            "suggest next safe release action": "suggest_next_safe_release_action",
            "are we ready for free self-learning?": "summarize_curriculum_boundary",
        }
        for text, operation in expectations.items():
            with self.subTest(text=text):
                call = self.router.call_from_example(text)
                self.assertEqual(call.system, "ts_project")
                self.assertEqual(call.operation, operation)

    def test_overclaim_rejection_uses_typed_call_boundary(self) -> None:
        operation_router = OperationRouter(self.registry)
        move = self.router.move_from_example("is this now a freely self-learning brain?")
        call = operation_router.route(
            move.__class__(
                **{
                    **move.to_dict(),
                    "slots": {"claim": "TS-Reasoner is now a freely self-learning brain."},
                }
            )
        )
        result = Dispatcher().dispatch(call)

        self.assertEqual(call.system, "ts_project")
        self.assertEqual(call.operation, "reject_unsafe_overclaim")
        self.assertEqual(result.status, "rejected")
        self.assertTrue(result.data["unsafe_overclaim_detected"])
        self.assertFalse(result.mutated_state)

    def test_unconfirmed_lesson_promotion_is_blocked(self) -> None:
        operation_router = OperationRouter(self.registry)
        move = self.router.move_from_example("learn this forever")
        call = operation_router.route(
            move.__class__(
                **{
                    **move.to_dict(),
                    "slots": {
                        "lesson_id": "bounded_curriculum_learning_only",
                        "evidence_path": "artifacts/ts_project_curriculum_receipt.json",
                    },
                }
            )
        )
        self.assertEqual(call.system, "ts_project")
        self.assertEqual(call.operation, "promote_lesson_candidate")
        self.assertEqual(call.risk, "reversible_write")

        result = Dispatcher().dispatch(call, confirmed=False)
        self.assertEqual(result.status, "needs_confirmation")
        self.assertFalse(result.mutated_state)

    def test_v31_evaluator_writes_report_and_receipt(self) -> None:
        subprocess.run([sys.executable, "scripts/evaluate_ts_project_curriculum.py"], cwd=ROOT, check=True)
        report = json.loads((ROOT / "artifacts/ts_project_curriculum_report.json").read_text(encoding="utf-8"))
        receipt = json.loads((ROOT / "artifacts/ts_project_curriculum_receipt.json").read_text(encoding="utf-8"))

        self.assertTrue(report["all_gates_passed"], report)
        self.assertTrue(report["checks"]["manifest_valid"])
        self.assertTrue(report["checks"]["missing_receipt_detected"])
        self.assertTrue(report["checks"]["unsafe_overclaim_rejected"])
        self.assertTrue(report["checks"]["bounded_curriculum_not_free_self_learning"])
        self.assertTrue(report["checks"]["unconfirmed_lesson_promotion_blocked"])
        self.assertEqual(report["external_side_effect_performed_count"], 0)
        self.assertEqual(report["network_call_performed_count"], 0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)
        self.assertEqual(receipt["release"], "v31.0.0")


if __name__ == "__main__":
    unittest.main()
