import json
import unittest
from pathlib import Path

from ts_reasoner.calibration.calibrator import TypedChannelCalibrator
from scripts.evaluate_typed_channel_calibrator_stress import compute_metrics, evaluate_case


ROOT = Path(__file__).resolve().parents[1]


class TypedChannelCalibratorStressTests(unittest.TestCase):
    def test_stress_evaluator_reports_required_metrics(self):
        calibrator = TypedChannelCalibrator.from_json(ROOT / "artifacts" / "typed_channel_calibrator.json")
        case = {
            "task_id": "stress_variable_renaming_001",
            "task_type": "variable_renaming",
            "question": "If all X are Y and all Y are Z, are all X Z?",
            "premises": ["All X are Y.", "All Y are Z."],
            "expected_answer_contains": "all X are Z",
            "expected_channels": {
                "logic_transitivity": True,
                "identity_preservation": True,
                "surface_structure": True,
                "confidence_abstention": True,
            },
            "expected_resolutions": {
                "logic_transitivity": "added_inferred_edge",
                "identity_preservation": "preserved_distinct_nodes",
                "surface_structure": "tagged_premise_inferred_candidate_edges",
                "confidence_abstention": "abstained_or_answered",
            },
        }
        result = evaluate_case(case, calibrator)
        metrics = compute_metrics([result])
        self.assertIn("heldout_channel_activation_accuracy", metrics)
        self.assertIn("trace_schema_validity", metrics)
        json.dumps(metrics)


if __name__ == "__main__":
    unittest.main()
