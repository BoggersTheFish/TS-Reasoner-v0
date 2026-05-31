import tempfile
import unittest
from pathlib import Path

from ts_reasoner.v8_milestone import (
    COMPONENTS,
    build_v8_milestone_payload,
    run_v8_milestone,
)


class TestTSReasonerV80Milestone(unittest.TestCase):
    def test_component_count(self):
        self.assertEqual(len(COMPONENTS), 9)

    def test_build_v8_payload(self):
        payload = build_v8_milestone_payload()

        self.assertEqual(payload["release"], "v8.0.0")
        self.assertEqual(payload["component_count"], 9)
        self.assertEqual(payload["component_gate_pass_count"], 9)
        self.assertEqual(payload["boundary_ok_count"], 9)
        self.assertEqual(payload["candidate_graph_contamination_count"], 0)
        self.assertFalse(payload["external_llm_used"])
        self.assertTrue(payload["typed_verifier_remains_proof_authority"])
        self.assertTrue(payload["all_gates_passed"])

    def test_v8_includes_all_major_capabilities(self):
        payload = build_v8_milestone_payload()

        self.assertTrue(payload["local_runtime_included"])
        self.assertTrue(payload["session_compiler_included"])
        self.assertTrue(payload["self_curriculum_included"])
        self.assertTrue(payload["branching_worlds_included"])
        self.assertTrue(payload["live_contradiction_firewall_included"])
        self.assertTrue(payload["repair_planner_included"])
        self.assertTrue(payload["knowledge_pack_library_included"])
        self.assertTrue(payload["trust_pressure_included"])
        self.assertTrue(payload["proof_repair_search_included"])
        self.assertTrue(payload["live_self_audit_included"])

    def test_v8_boundaries(self):
        payload = build_v8_milestone_payload()
        boundary = payload["boundary"]

        self.assertFalse(boundary["broad_natural_language_understanding"])
        self.assertFalse(boundary["neural_training"])
        self.assertFalse(boundary["live_tensionlm_runtime"])
        self.assertFalse(boundary["external_benchmark_victory"])
        self.assertFalse(boundary["milestone_pack_is_general_intelligence_claim"])
        self.assertFalse(boundary["generated_text_is_proof"])
        self.assertFalse(boundary["trust_is_proof"])
        self.assertFalse(boundary["audit_output_is_proof"])
        self.assertFalse(boundary["search_result_is_proof"])
        self.assertTrue(boundary["typed_verifier_remains_proof_authority"])

    def test_run_v8_milestone_writes_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = run_v8_milestone(Path(tmp))

            self.assertTrue(payload["all_gates_passed"])
            self.assertTrue(Path(payload["receipt_path"]).exists())
            self.assertTrue(Path(payload["report_path"]).exists())
            self.assertEqual(payload["candidate_graph_contamination_count"], 0)


if __name__ == "__main__":
    unittest.main()
