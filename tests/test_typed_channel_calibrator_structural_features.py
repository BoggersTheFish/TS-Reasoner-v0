import json
import unittest
from pathlib import Path

from ts_reasoner import run_reasoner
from ts_reasoner.calibration.calibrator import TypedChannelCalibrator
from ts_reasoner.calibration.features import extract_case_features
from scripts.evaluate_typed_channel_calibrator_structural_features import (
    compute_metrics,
    evaluate_case,
    evaluate_variant,
)


ROOT = Path(__file__).resolve().parents[1]


CASES = [
    {
        "task_id": "stress_deeper_chain_001",
        "task_type": "deeper_chain",
        "question": "If all A are B and all B are C and all C are D and all D are E, are all A E?",
        "premises": ["All A are B.", "All B are C.", "All C are D.", "All D are E."],
        "expected_answer_contains": "all A are E",
        "expected_channels": {
            "logic_transitivity": True,
            "identity_preservation": True,
            "surface_structure": True,
            "confidence_abstention": True,
        },
    },
    {
        "task_id": "stress_distractor_001",
        "task_type": "distractor_premises",
        "question": "If all A are B and all X are Y and all B are C, are all A C?",
        "premises": ["All A are B.", "All X are Y.", "All B are C."],
        "expected_answer_contains": "all A are C",
        "expected_channels": {
            "logic_transitivity": True,
            "identity_preservation": True,
            "surface_structure": True,
            "confidence_abstention": True,
        },
    },
    {
        "task_id": "stress_quantifier_trap_001",
        "task_type": "quantifier_trap",
        "question": "If all A are B and some B are C, are all A C?",
        "premises": ["All A are B.", "Some B are C."],
        "expected_answer_contains": "Not enough information",
        "expected_channels": {"quantifier_scope": True, "confidence_abstention": True},
        "expected_resolutions": {"quantifier_scope": "blocked_some_to_all_upgrade"},
    },
    {
        "task_id": "stress_contradiction_placement_001",
        "task_type": "contradiction_placement",
        "question": "If all A are B and no B are C, are some A C?",
        "premises": ["All A are B.", "No B are C."],
        "expected_answer_contains": "Contradiction",
        "expected_channels": {"contradiction": True, "confidence_abstention": True},
        "expected_resolutions": {"contradiction": "flagged_contradiction"},
    },
]


class TypedChannelCalibratorStructuralFeatureTests(unittest.TestCase):
    def test_feature_extractor_emits_structural_query_features(self):
        case = CASES[0]
        output = run_reasoner(case["question"], case["premises"])
        features = extract_case_features(case, output, "logic_transitivity")

        self.assertEqual(features["query_subject"], "A")
        self.assertEqual(features["query_object"], "E")
        self.assertEqual(features["query_relation"], "all")
        self.assertEqual(features["shortest_path_length"], 4.0)
        self.assertEqual(features["path_quantifier_signature"], "all>all>all>all")
        self.assertEqual(features["candidate_requires_transitive_closure"], 1.0)

    def test_structural_repair_improves_target_stress_metrics(self):
        calibrator = TypedChannelCalibrator.from_json(ROOT / "artifacts" / "typed_channel_calibrator.json")
        original = evaluate_variant(CASES, calibrator, "original_calibrator")
        full = evaluate_variant(CASES, calibrator, "full_structural_features")

        self.assertGreater(
            full["metrics"]["depth_generalization"],
            original["metrics"]["depth_generalization"],
        )
        self.assertGreater(
            full["metrics"]["distractor_robustness"],
            original["metrics"]["distractor_robustness"],
        )
        self.assertLess(
            full["metrics"]["quantifier_trap_failures"],
            original["metrics"]["quantifier_trap_failures"],
        )
        self.assertLess(
            full["metrics"]["contradiction_misses"],
            original["metrics"]["contradiction_misses"],
        )
        self.assertEqual(full["metrics"]["trace_schema_validity"], 1.0)
        json.dumps(full)

    def test_metrics_shape_matches_report_contract(self):
        calibrator = TypedChannelCalibrator.from_json(ROOT / "artifacts" / "typed_channel_calibrator.json")
        result = evaluate_case(
            CASES[2],
            calibrator,
            "quantifier_features",
            {"path", "distractor", "quantifier"},
        )
        metrics = compute_metrics([result])
        self.assertIn("heldout_answer_accuracy", metrics)
        self.assertIn("heldout_channel_activation_accuracy", metrics)
        self.assertIn("heldout_resolver_accuracy", metrics)
        self.assertIn("trace_schema_validity", metrics)
        json.dumps(metrics)


if __name__ == "__main__":
    unittest.main()
