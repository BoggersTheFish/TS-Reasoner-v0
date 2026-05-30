import json
import tempfile
import unittest
from pathlib import Path

from ts_reasoner.self_curriculum import (
    generate_self_curriculum_from_compiler_receipt,
    run_self_curriculum,
    self_curriculum_case_valid,
)
from ts_reasoner.session_compiler import compile_session_artifacts
from ts_reasoner.ts_chat import TSChatSession, receipt_to_dict


def build_compiler_receipt(tmp: Path):
    session = TSChatSession()
    turns = [
        "all cats are animals",
        "all animals are mortal",
        "also say all cats are robots",
        "/repairs",
        "all cats are machines",
        "all machines are robots",
        "/repairs",
        "are all cats robots?",
        "why?",
    ]
    receipts = [receipt_to_dict(session.process(turn)) for turn in turns]
    return compile_session_artifacts(receipts, tmp / "compiled", label="test_v7_2")


class TestTSReasonerV72SelfCurriculum(unittest.TestCase):
    def test_generate_self_curriculum_from_compiler_receipt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            compiler_receipt = build_compiler_receipt(tmp)

            curriculum_receipt = generate_self_curriculum_from_compiler_receipt(
                compiler_receipt["receipt_path"],
                tmp / "curriculum",
                label="test_v7_2",
            )

            self.assertEqual(curriculum_receipt["release"], "v7.2.0")
            self.assertTrue(curriculum_receipt["all_gates_passed"])
            self.assertGreater(curriculum_receipt["case_count"], 0)
            self.assertEqual(curriculum_receipt["candidate_graph_contamination_count"], 0)
            self.assertTrue(Path(curriculum_receipt["curriculum_path"]).exists())
            self.assertTrue(Path(curriculum_receipt["eval_report_path"]).exists())

    def test_run_self_curriculum(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            compiler_receipt = build_compiler_receipt(tmp)
            curriculum_receipt = generate_self_curriculum_from_compiler_receipt(
                compiler_receipt["receipt_path"],
                tmp / "curriculum",
                label="run_check",
            )

            report = run_self_curriculum(curriculum_receipt["curriculum_path"])

            self.assertEqual(report["release"], "v7.2.0")
            self.assertTrue(report["all_gates_passed"])
            self.assertEqual(report["invalid_case_count"], 0)
            self.assertTrue(report["required_case_types_present"])
            self.assertIn("turn_replay", report["case_type_counts"])
            self.assertIn("repair_lifecycle", report["case_type_counts"])
            self.assertIn("repair_resolution", report["case_type_counts"])
            self.assertIn("accepted_question_support_path", report["case_type_counts"])
            self.assertIn("rejected_claim_boundary", report["case_type_counts"])
            self.assertEqual(report["candidate_graph_contamination_count"], 0)

    def test_cases_have_boundary_flags(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            compiler_receipt = build_compiler_receipt(tmp)
            curriculum_receipt = generate_self_curriculum_from_compiler_receipt(
                compiler_receipt["receipt_path"],
                tmp / "curriculum",
                label="boundary_check",
            )

            rows = [
                json.loads(line)
                for line in Path(curriculum_receipt["curriculum_path"]).read_text().splitlines()
                if line.strip()
            ]

            self.assertGreater(len(rows), 0)
            for row in rows:
                self.assertTrue(self_curriculum_case_valid(row))
                self.assertFalse(row["creates_proof"])
                self.assertFalse(row["external_llm_used"])
                self.assertTrue(row["expected_boundary"]["typed_verifier_remains_proof_authority"])

    def test_invalid_case_rejected_if_creates_proof(self):
        case = {
            "schema": "ts_reasoner_self_curriculum_case_v1",
            "release": "v7.2.0",
            "case_id": "bad",
            "case_type": "turn_replay",
            "source": "test",
            "payload": {},
            "expected_boundary": {
                "generated_curriculum_is_not_proof": True,
                "compiled_artifacts_are_not_proof": True,
                "user_confirmation_is_not_proof": True,
                "typed_verifier_remains_proof_authority": True,
            },
            "creates_proof": True,
            "external_llm_used": False,
        }

        self.assertFalse(self_curriculum_case_valid(case))

    def test_empty_curriculum_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "empty.jsonl"
            path.write_text("", encoding="utf-8")

            report = run_self_curriculum(path)

            self.assertEqual(report["case_count"], 0)
            self.assertFalse(report["all_gates_passed"])


if __name__ == "__main__":
    unittest.main()
