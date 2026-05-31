from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_reasoner.knowledge_pack_contracts import (
    evaluate_knowledge_pack_cases,
    import_knowledge_pack,
)


ROOT = Path(__file__).resolve().parents[1]


class KnowledgePackContractsTests(unittest.TestCase):
    def test_unsupported_claim_quarantined(self) -> None:
        result = import_knowledge_pack(
            {
                "case_id": "unsupported_claim_quarantined",
                "pack_schema_version": "1.0",
                "accepted_claims": ["all cats are animals"],
                "branch_worlds": [],
                "repair_targets": [],
                "provenance_records": [],
                "unsupported_claims": ["all cats are robots"],
            }
        )

        self.assertTrue(result.imported)
        self.assertTrue(result.quarantined)
        self.assertEqual(result.accepted_claims, ["all cats are animals"])
        self.assertEqual(result.quarantined_claims, ["all cats are robots"])
        self.assertEqual(result.unsupported_claims_promoted_count, 0)
        self.assertEqual(result.candidate_graph_contamination_count, 0)

    def test_invalid_schema_quarantined(self) -> None:
        result = import_knowledge_pack(
            {
                "case_id": "invalid_schema_quarantined",
                "pack_schema_version": "bad",
                "accepted_claims": ["all dogs are animals"],
                "branch_worlds": [],
                "repair_targets": [],
                "provenance_records": [],
                "unsupported_claims": ["all dogs are robots"],
            }
        )

        self.assertFalse(result.imported)
        self.assertTrue(result.quarantined)
        self.assertEqual(result.accepted_claims, [])
        self.assertEqual(result.quarantined_claims, ["all dogs are robots"])
        self.assertEqual(result.candidate_graph_contamination_count, 0)

    def test_dataset_eval_passes(self) -> None:
        cases = [
            json.loads(line)
            for line in (ROOT / "data" / "v8_5" / "knowledge_pack_contract_cases.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        report = evaluate_knowledge_pack_cases(cases)

        self.assertTrue(report["all_gates_passed"])
        self.assertEqual(report["knowledge_pack_contract_accuracy"], 1.0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)
        self.assertEqual(report["unsupported_claims_promoted_count"], 0)

    def test_script_generates_receipt(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/v8_5/evaluate_knowledge_pack_contracts.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        receipt = json.loads((ROOT / "artifacts" / "knowledge_pack_contracts_receipt.json").read_text(encoding="utf-8"))

        self.assertEqual(receipt["release"], "v8.5.0")
        self.assertTrue(receipt["all_gates_passed"])
        self.assertEqual(receipt["candidate_graph_contamination_count"], 0)
        self.assertEqual(receipt["unsupported_claims_promoted_count"], 0)
        self.assertTrue(receipt["knowledge_pack_import_is_not_proof"])


if __name__ == "__main__":
    unittest.main()
