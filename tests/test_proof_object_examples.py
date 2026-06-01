from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.proof_object_examples import build_proof_object_examples


ROOT = Path(__file__).resolve().parents[1]


class ProofObjectExamplesTests(unittest.TestCase):
    def test_examples_cover_accept_reject_abstain(self) -> None:
        payload = build_proof_object_examples()
        self.assertTrue(payload["all_gates_passed"], payload)
        self.assertGreaterEqual(payload["accepted_count"], 1)
        self.assertGreaterEqual(payload["rejected_count"], 1)
        self.assertGreaterEqual(payload["abstained_count"], 1)
        for example in payload["examples"]:
            self.assertIn("claim", example)
            self.assertIn("normalized_claim", example)
            self.assertIn("support_path", example)
            self.assertIn("typed_channel", example)
            self.assertIn("verifier_decision", example)
            self.assertIn("why_accepted_rejected_or_abstained", example)
            self.assertTrue(example["confidence_ignored"])

    def test_script_writes_artifact(self) -> None:
        subprocess.run([sys.executable, "scripts/show_proof_object_examples.py"], cwd=ROOT, check=True)
        payload = json.loads((ROOT / "artifacts/proof_object_examples.json").read_text(encoding="utf-8"))
        self.assertTrue(payload["all_gates_passed"], payload)


if __name__ == "__main__":
    unittest.main()
