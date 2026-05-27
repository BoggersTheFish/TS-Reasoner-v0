import unittest

from scripts.evaluate_real_exported_tensionlm_sample import evaluate_row
from ts_reasoner.tensionlm_adapter import load_tensionlm_export_jsonl


class RealExportedTensionLMSampleTests(unittest.TestCase):
    def test_sample_rows_load_with_source_evidence(self):
        rows = load_tensionlm_export_jsonl("data/real_exported_tensionlm_sample.jsonl")

        self.assertGreaterEqual(len(rows), 1)
        self.assertEqual(rows[0].model, "TensionLM-117M-curriculum-eval-seed42")
        self.assertEqual(rows[0].raw["source_artifact"], "logs/eval/117m_transitivity_seed42.json")
        self.assertEqual(rows[0].candidates[0].source, "tensionlm_eval_export")

    def test_real_exported_sample_keeps_verifier_boundary(self):
        row = load_tensionlm_export_jsonl("data/real_exported_tensionlm_sample.jsonl")[0]

        result = evaluate_row(row)

        self.assertTrue(result["all_expected_ok"])
        self.assertTrue(result["verifier_beats_candidate_confidence"])
        self.assertEqual(result["candidate_graph_contamination_count"], 0)
        self.assertEqual(result["accepted_with_typed_support"], [True])


if __name__ == "__main__":
    unittest.main()
