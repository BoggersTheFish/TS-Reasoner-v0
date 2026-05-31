from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReleaseAuthorityV80Tests(unittest.TestCase):
    def test_release_authority_json_shape(self) -> None:
        authority = json.loads((ROOT / "release_authority.json").read_text(encoding="utf-8"))

        self.assertEqual(authority["schema_version"], "1.0")
        self.assertEqual(authority["release"], "v8.0.0")
        self.assertEqual(authority["title"], "Canonical Release Authority")
        self.assertFalse(authority["proof_boundary"]["candidate_generation_is_proof"])
        self.assertFalse(authority["proof_boundary"]["model_confidence_is_proof"])
        self.assertFalse(authority["proof_boundary"]["generated_text_is_proof"])
        self.assertTrue(authority["proof_boundary"]["typed_verifier_support_remains_proof_boundary"])

    def test_readme_current_release_surface_mentions_v8(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("v8.0.0", readme)
        self.assertIn("Canonical Release Authority", readme)

    def test_release_authority_audit_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/v8_0/check_release_authority_sync.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        receipt = json.loads(
            (ROOT / "artifacts" / "release_authority_audit_receipt.json").read_text(encoding="utf-8")
        )
        self.assertTrue(receipt["all_gates_passed"])
        self.assertEqual(receipt["candidate_graph_contamination_count"], 0)
        self.assertEqual(receipt["public_surface_overclaim_count"], 0)


if __name__ == "__main__":
    unittest.main()
