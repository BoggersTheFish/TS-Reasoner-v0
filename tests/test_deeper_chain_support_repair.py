import unittest

from scripts.evaluate_deeper_chain_support_repair import evaluate_row
from ts_reasoner.tensionlm_adapter import load_tensionlm_export_jsonl


class DeeperChainSupportRepairTests(unittest.TestCase):
    def test_deeper_chain_candidate_is_accepted_with_typed_support(self):
        row = load_tensionlm_export_jsonl("data/deeper_chain_support_repair_cases.jsonl")[0]

        result = evaluate_row(row)

        self.assertTrue(result["deeper_chain_checks"]["repair_valid_a_to_d"])
        self.assertTrue(result["v1_6_failure_repair_checks"]["repair_valid_a_to_d"])
        self.assertEqual(result["candidate_graph_contamination_count"], 0)
        self.assertEqual(result["identity_collapse_count"], 0)

    def test_wrong_reverse_stays_rejected(self):
        row = load_tensionlm_export_jsonl("data/deeper_chain_support_repair_cases.jsonl")[0]

        result = evaluate_row(row)

        self.assertTrue(result["wrong_reverse_checks"]["repair_bad_reverse_d_to_a"])

    def test_four_hop_chain_is_supported(self):
        row = load_tensionlm_export_jsonl("data/deeper_chain_support_repair_cases.jsonl")[1]

        result = evaluate_row(row)

        self.assertTrue(result["deeper_chain_checks"]["repair_valid_m_to_q"])
        self.assertTrue(result["wrong_reverse_checks"]["repair_bad_reverse_q_to_m"])


if __name__ == "__main__":
    unittest.main()
