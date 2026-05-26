import json
import tempfile
import unittest
from pathlib import Path

from ts_reasoner.calibration.calibrator import TypedChannelCalibrator
from ts_reasoner.calibration.train import build_rows, evaluate_ablations, train_calibrator


CASES = [
    {
        "task_id": "transitive_valid_001",
        "task_type": "transitive_valid",
        "question": "If all A are B and all B are C, are all A C?",
        "premises": ["All A are B.", "All B are C."],
        "expected_answer_contains": "all A are C",
        "expected_channels": {"logic_transitivity": True, "identity_preservation": True},
        "expected_resolutions": {
            "logic_transitivity": "added_inferred_edge",
            "identity_preservation": "preserved_distinct_nodes",
        },
    },
    {
        "task_id": "reverse_invalid_001",
        "task_type": "reverse_invalid",
        "question": "If all A are B and all B are C, are all C A?",
        "premises": ["All A are B.", "All B are C."],
        "expected_answer_contains": "Not enough information",
        "expected_channels": {"directionality": True},
        "expected_resolutions": {"directionality": "blocked_reverse_inference"},
    },
    {
        "task_id": "some_all_unsupported_001",
        "task_type": "some_all_unsupported",
        "question": "If some pilots are engineers and all engineers are careful, are all pilots careful?",
        "premises": ["Some pilots are engineers.", "All engineers are careful."],
        "expected_answer_contains": "Not enough information",
        "expected_channels": {"quantifier_scope": True, "confidence_abstention": True},
        "expected_resolutions": {"quantifier_scope": "blocked_some_to_all_upgrade"},
    },
]


class TypedChannelCalibratorTests(unittest.TestCase):
    def test_build_rows_and_train_calibrator(self):
        rows = build_rows(CASES)
        self.assertEqual(len(rows), 21)
        calibrator = train_calibrator(rows)
        transitivity = next(row for row in rows if row["channel"] == "logic_transitivity")
        self.assertTrue(calibrator.predicts_activation("logic_transitivity", transitivity["features"]))
        self.assertEqual(calibrator.resolver_for("logic_transitivity", True), "added_inferred_edge")

    def test_calibrator_json_roundtrip_and_ablations(self):
        rows = build_rows(CASES)
        calibrator = train_calibrator(rows)
        with tempfile.TemporaryDirectory() as tmp:
            path = calibrator.to_json(Path(tmp) / "calibrator.json")
            loaded = TypedChannelCalibrator.from_json(path)
        report = evaluate_ablations(rows, loaded)
        self.assertIn("full_calibrator", report["ablations"])
        self.assertIn("channel_activation_accuracy", report["ablations"]["full_calibrator"])
        json.dumps(report)


if __name__ == "__main__":
    unittest.main()
