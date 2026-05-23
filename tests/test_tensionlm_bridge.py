import unittest

from ts_reasoner.tensionlm_bridge import StaticCompletionProposer, run_tensionlm_bridge


class TensionLMBridgeTests(unittest.TestCase):
    def test_bridge_adds_neural_generation_trace_without_schema_break(self):
        output = run_tensionlm_bridge(
            question="If all mammals are animals and all whales are mammals, are all whales animals?",
            premises=["All mammals are animals.", "All whales are mammals."],
            proposer=StaticCompletionProposer(["Therefore all whales are animals."]),
            proposal_count=1,
        )

        self.assertEqual(output.final_answer, "all whales are animals.")
        self.assertIn("neural_generation", output.trace)
        neural_trace = output.trace["neural_generation"]
        self.assertEqual(neural_trace["proposal_count"], 1)
        self.assertEqual(neural_trace["proposals"][0]["parse_status"], "parsed_relation")
        self.assertIn("verifier_status", neural_trace["proposals"][0])

    def test_bridge_records_unparsed_neural_tension(self):
        output = run_tensionlm_bridge(
            question="If all A are B and all B are C, are all A C?",
            premises=["All A are B.", "All B are C."],
            proposer=StaticCompletionProposer(["waves of certainty with no relation syntax"]),
            proposal_count=1,
        )

        proposal = output.trace["neural_generation"]["proposals"][0]
        self.assertEqual(proposal["parse_status"], "unparsed")
        self.assertIn("overconfidence", proposal["issue_kinds"])
        self.assertNotEqual(proposal["verifier_status"], "accepted_selected")


if __name__ == "__main__":
    unittest.main()
