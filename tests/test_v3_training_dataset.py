from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V3TrainingDatasetTests(unittest.TestCase):
    def test_v3_dataset_builder_writes_outputs(self) -> None:
        subprocess.check_call([sys.executable, "scripts/v3/build_v3_training_dataset.py"], cwd=ROOT)

        dataset_path = ROOT / "artifacts/v3/v3_training_dataset.jsonl"
        summary_path = ROOT / "artifacts/v3/v3_dataset_summary.json"

        self.assertTrue(dataset_path.exists())
        self.assertTrue(summary_path.exists())

        rows = [json.loads(line) for line in dataset_path.read_text().splitlines() if line.strip()]
        summary = json.loads(summary_path.read_text())

        self.assertEqual(len(rows), 103)
        self.assertEqual(summary["row_count"], 103)
        self.assertEqual(summary["raw_row_count"], 150)
        self.assertEqual(summary["duplicate_removed_count"], 47)

    def test_v3_dataset_has_required_boundaries_features_and_targets(self) -> None:
        subprocess.check_call([sys.executable, "scripts/v3/build_v3_training_dataset.py"], cwd=ROOT)

        rows = [
            json.loads(line)
            for line in (ROOT / "artifacts/v3/v3_training_dataset.jsonl").read_text().splitlines()
            if line.strip()
        ]

        self.assertTrue(all(row["boundary"]["verifier_role"] == "typed verifier remains proof authority" for row in rows))
        self.assertTrue(all(row["features"] for row in rows))
        self.assertTrue(all(row["target"] for row in rows))
        self.assertEqual({row["v3_schema_version"] for row in rows}, {"v3.0.0-dataset"})

    def test_v3_dataset_statuses_and_splits_are_present(self) -> None:
        subprocess.check_call([sys.executable, "scripts/v3/build_v3_training_dataset.py"], cwd=ROOT)

        summary = json.loads((ROOT / "artifacts/v3/v3_dataset_summary.json").read_text())

        self.assertEqual(summary["status_counts"], {
            "abstained": 42,
            "accepted": 17,
            "rejected": 44,
        })
        self.assertEqual(summary["split_counts"], {
            "active_challenge": 12,
            "eval": 35,
            "stress": 56,
        })
        self.assertEqual(summary["source_counts"], {
            "v27_verifier_trace": 91,
            "v29_active_challenge": 12,
        })
        self.assertEqual(summary["raw_source_counts"], {
            "v27_verifier_trace": 91,
            "v29_active_augmented": 47,
            "v29_active_challenge": 12,
        })


if __name__ == "__main__":
    unittest.main()
