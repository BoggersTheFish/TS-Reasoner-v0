from __future__ import annotations

import unittest
from pathlib import Path

from ts_reasoner.proposer_stack import (
    StackConfig,
    _question_for_claim,
    build_stack_cases,
    evaluate_stack,
    run_stack_on_paragraph,
    train_stack_models,
)


ROOT = Path(__file__).resolve().parents[1]


class VerifierGatedProposerStackV120Tests(unittest.TestCase):
    def test_question_for_claim(self) -> None:
        self.assertEqual(_question_for_claim("all fish are animals"), "Are all fish animals?")
        self.assertEqual(_question_for_claim("no fish are machines"), "Are fish not machines?")

    def test_build_stack_cases(self) -> None:
        cases = build_stack_cases(StackConfig(case_count=12, train_limit=60))
        self.assertEqual(len(cases), 12)
        self.assertTrue(all("paragraph" in case for case in cases))
        self.assertTrue(all(case["expected_answer"] in {"yes", "no", "abstain"} for case in cases))

    def test_single_stack_runtime_blocks_wrong_accepts(self) -> None:
        config = StackConfig(
            seed=121,
            train_limit=120,
            case_count=8,
            dim=256,
            hidden=8,
            epochs=1,
            learning_rate=0.035,
        )
        models = train_stack_models(ROOT, config)

        result = run_stack_on_paragraph(
            "Generated text counts as candidate data. Is generated text proof?",
            models["answer_model"],
            models["status_model"],
            models["channel_model"],
        )

        self.assertEqual(result["decomposition_status"], "parsed")
        self.assertEqual(result["final"]["answer"], "abstain")
        self.assertFalse(result["final"]["accepted_with_typed_support"])

    def test_small_stack_evaluation_gates(self) -> None:
        result = evaluate_stack(
            ROOT,
            StackConfig(
                seed=122,
                train_limit=160,
                case_count=16,
                dim=256,
                hidden=8,
                epochs=1,
                learning_rate=0.035,
            ),
        )
        report = result["report"]
        self.assertEqual(report["case_count"], 16)
        self.assertEqual(report["decomposition_success_rate"], 1.0)
        self.assertEqual(report["final_wrong_accept_count"], 0)
        self.assertEqual(report["accepted_without_typed_support_count"], 0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)
        self.assertTrue(report["all_gates_passed"])


if __name__ == "__main__":
    unittest.main()
