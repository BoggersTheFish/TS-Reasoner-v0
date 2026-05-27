import unittest

from scripts.evaluate_tensionlm_export_set import evaluate_row
from ts_reasoner.tensionlm_adapter import load_tensionlm_export_jsonl


class TensionLMExportSetTests(unittest.TestCase):
    def test_export_set_rows_load_from_real_source_artifact(self):
        rows = load_tensionlm_export_jsonl("data/tensionlm_export_set_cases.jsonl")

        self.assertGreaterEqual(len(rows), 5)
        self.assertEqual(rows[0].model, "TensionLM-117M-curriculum-eval-seed42")
        self.assertEqual(rows[0].raw["source_artifact"], "logs/eval/117m_transitivity_seed42.json")
        self.assertEqual(rows[0].candidates[0].source, "tensionlm_eval_export")

    def test_high_confidence_bad_candidate_loses_to_verifier(self):
        row = load_tensionlm_export_jsonl("data/tensionlm_export_set_cases.jsonl")[0]

        result = evaluate_row(row)

        self.assertTrue(result["all_expected_ok"])
        self.assertTrue(result["verifier_beats_candidate_confidence"])
        self.assertEqual(result["candidate_graph_contamination_count"], 0)
        self.assertEqual(result["accepted_with_typed_support"], [True])

    def test_export_set_preserves_failure_reasons(self):
        rows = load_tensionlm_export_jsonl("data/tensionlm_export_set_cases.jsonl")
        results = {row.row_id: evaluate_row(row) for row in rows}

        malformed = results["export_set_malformed_node_completion_rejected"]

        self.assertEqual(malformed["failure_reasons"][0]["status"], "rejected")
        self.assertEqual(malformed["failure_reasons"][0]["normalization_status"], "unparsed")


if __name__ == "__main__":
    unittest.main()
