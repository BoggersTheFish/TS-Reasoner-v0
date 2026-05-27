from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ts_reasoner.candidate_bridge import CandidateClaim, verify_candidate_claim
from ts_reasoner.learned_model.dataset import build_cases, label_case, load_cases, write_split_files
from ts_reasoner.learned_model.evaluate import evaluate_cases
from ts_reasoner.learned_model.infer import verify_scored_case
from ts_reasoner.learned_model.train import train_model


class LearnedCandidateModelTests(unittest.TestCase):
    def test_dataset_builds_labelled_splits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_split_files(root)
            train_rows = load_cases(root / "data/learned_candidate_model_train.jsonl")
            eval_rows = load_cases(root / "data/learned_candidate_model_eval.jsonl")
            stress_rows = load_cases(root / "data/learned_candidate_model_stress.jsonl")

        self.assertGreater(len(train_rows), 0)
        self.assertGreater(len(eval_rows), 0)
        self.assertGreater(len(stress_rows), 0)
        self.assertTrue(all("labels" in row for row in train_rows + eval_rows + stress_rows))

    def test_identity_candidate_is_typed_rejection(self) -> None:
        result = verify_candidate_claim(
            "All A are B. All B are C. All C are D. Are all A D?",
            ["All A are B", "All B are C", "All C are D"],
            CandidateClaim(
                claim="A equals D",
                source="learned_candidate_model",
                confidence=0.88,
                candidate_id="identity_a_d",
            ),
        )

        self.assertEqual(result.status, "rejected")
        self.assertIn("identity_preservation", result.channels)

    def test_demo_boundary_accepts_valid_and_rejects_bad_candidates(self) -> None:
        demo = label_case(
            {
                "split": "demo",
                "case_id": "demo",
                "input_text": "All A are B. All B are C. All C are D. Are all A D?",
                "candidates": [
                    {
                        "candidate_id": "valid",
                        "claim": "All A are D",
                        "source": "learned_candidate_dataset",
                        "confidence": 0.55,
                    },
                    {
                        "candidate_id": "reverse",
                        "claim": "All D are A",
                        "source": "learned_candidate_dataset",
                        "confidence": 0.96,
                    },
                    {
                        "candidate_id": "identity",
                        "claim": "A equals D",
                        "source": "learned_candidate_dataset",
                        "confidence": 0.88,
                    },
                ],
                "tags": ["deeper_chain", "grant_demo"],
            }
        )
        model = train_model([row for row in map(label_case, build_cases()) if row["split"] == "train"])
        payload = verify_scored_case(model, demo)
        by_id = {item["candidate_id"]: item for item in payload["verification"]["candidate_results"]}

        self.assertEqual(by_id["valid"]["status"], "accepted")
        self.assertIn("logic_transitivity", by_id["valid"]["channels"])
        self.assertEqual(by_id["reverse"]["status"], "rejected")
        self.assertIn("directionality", by_id["reverse"]["channels"])
        self.assertEqual(by_id["identity"]["status"], "rejected")
        self.assertIn("identity_preservation", by_id["identity"]["channels"])

    def test_evaluation_preserves_verifier_boundary(self) -> None:
        rows = [label_case(row) for row in build_cases()]
        train_rows = [row for row in rows if row["split"] == "train"]
        eval_rows = [row for row in rows if row["split"] == "eval"]
        model = train_model(train_rows)
        report = evaluate_cases(model, eval_rows)

        self.assertEqual(report["metrics"]["candidate_graph_contamination_count"], 0)
        self.assertEqual(report["metrics"]["bad_candidate_rejection_rate"], 1.0)
        self.assertEqual(report["metrics"]["accepted_candidate_support_rate"], 1.0)
        self.assertEqual(report["metrics"]["trace_schema_validity"], 1.0)


if __name__ == "__main__":
    unittest.main()
