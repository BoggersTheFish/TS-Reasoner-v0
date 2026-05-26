import unittest

from ts_reasoner import run_reasoner


class TypedTensionChannelTests(unittest.TestCase):
    def test_transitivity_identity_surface_and_trace_shape(self):
        output = run_reasoner(
            "If all A are B and all B are C, are all A C?",
            ["All A are B.", "All B are C."],
        )
        channels = output.trace["tension_channels"]
        self.assertIn("logic_transitivity", channels)
        self.assertEqual(channels["logic_transitivity"]["resolution"], "added_inferred_edge")
        self.assertEqual(channels["logic_transitivity"]["final_tension"], 0.0)
        self.assertEqual(channels["identity_preservation"]["resolution"], "preserved_distinct_nodes")
        self.assertIn("A!=C", output.trace["typed_runtime"]["context"]["blocked_equalities"])
        self.assertIn("surface_structure", channels)
        self.assertIn("typed_runtime", output.trace)

    def test_reverse_query_is_blocked_by_directionality(self):
        output = run_reasoner(
            "If all A are B and all B are C, are all C A?",
            ["All A are B.", "All B are C."],
        )
        directionality = output.trace["tension_channels"]["directionality"]
        self.assertTrue(directionality["activated"])
        self.assertEqual(directionality["resolution"], "blocked_reverse_inference")
        self.assertIn("C->A", output.trace["typed_runtime"]["context"]["blocked_edges"])

    def test_some_all_upgrade_is_blocked(self):
        output = run_reasoner(
            "If some pilots are engineers and all engineers are careful, are all pilots careful?",
            ["Some pilots are engineers.", "All engineers are careful."],
        )
        quantifier = output.trace["tension_channels"]["quantifier_scope"]
        self.assertTrue(quantifier["activated"])
        self.assertEqual(quantifier["resolution"], "blocked_some_to_all_upgrade")
        self.assertTrue(output.trace["typed_runtime"]["context"]["quantifier_scope_blocked"])

    def test_low_support_abstention_is_traced(self):
        output = run_reasoner("Are all A C?", [])
        confidence = output.trace["tension_channels"]["confidence_abstention"]
        self.assertEqual(confidence["resolution"], "abstained_or_answered")
        self.assertTrue(output.trace["typed_runtime"]["context"]["abstention"])


if __name__ == "__main__":
    unittest.main()
