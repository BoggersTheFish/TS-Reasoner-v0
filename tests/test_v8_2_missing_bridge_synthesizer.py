from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.missing_bridge_synthesizer import (
    BridgeSynthesisInput,
    evaluate_bridge_cases,
    synthesize_missing_bridge,
)


ROOT = Path(__file__).resolve().parents[1]


class MissingBridgeSynthesizerTests(unittest.TestCase):
    def test_one_hop_bridge(self) -> None:
        result = synthesize_missing_bridge(
            BridgeSynthesisInput(
                case_id="one_hop_taxonomy_bridge",
                known_claims=["all cats are animals"],
                target_claim="all cats are mortal",
            )
        )

        self.assertFalse(result.already_supported)
        self.assertEqual(result.missing_bridges, ["all animals are mortal"])
        self.assertEqual(result.bridge_count, 1)
        self.assertEqual(result.candidate_graph_contamination_count, 0)

    def test_already_supported_transitive(self) -> None:
        result = synthesize_missing_bridge(
            BridgeSynthesisInput(
                case_id="already_supported_transitive",
                known_claims=["all cats are mammals", "all mammals are mortal"],
                target_claim="all cats are mortal",
            )
        )

        self.assertTrue(result.already_supported)
        self.assertEqual(result.missing_bridges, [])
        self.assertEqual(result.bridge_count, 0)

    def test_dataset_eval_passes(self) -> None:
        cases = [
            json.loads(line)
            for line in (ROOT / "data" / "v8_2" / "missing_bridge_synthesizer_cases.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        report = evaluate_bridge_cases(cases)

        self.assertTrue(report["all_gates_passed"])
        self.assertEqual(report["bridge_synthesis_accuracy"], 1.0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)

    def test_script_generates_receipt(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/v8_2/evaluate_missing_bridge_synthesizer.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        receipt = json.loads((ROOT / "artifacts" / "missing_bridge_synthesizer_receipt.json").read_text(encoding="utf-8"))

        self.assertEqual(receipt["release"], "v8.2.0")
        self.assertTrue(receipt["all_gates_passed"])
        self.assertEqual(receipt["candidate_graph_contamination_count"], 0)
        self.assertTrue(receipt["generated_bridges_are_not_proof"])


if __name__ == "__main__":
    unittest.main()
