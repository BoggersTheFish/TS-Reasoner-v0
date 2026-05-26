import json
import unittest

from scripts.generate_typed_channel_release_receipt import build_receipt


class TypedChannelReleaseReceiptTests(unittest.TestCase):
    def test_release_receipt_summarizes_full_progression(self):
        receipt = build_receipt(now="2026-05-26T00:00:00+00:00")

        self.assertEqual(receipt["project"], "TS-Reasoner-v0")
        self.assertEqual(receipt["public_claim_level"], "experimental")
        self.assertIn("typed_tension_channels", receipt["benchmarks"])
        self.assertIn("scoped_calibrator_full", receipt["benchmarks"])
        self.assertIn("generalization_stress", receipt["benchmarks"])
        self.assertIn("structural_repair", receipt["benchmarks"])

        scoped = receipt["benchmarks"]["scoped_calibrator_full"]
        self.assertEqual(scoped["answer_accuracy"], 1.0)
        self.assertEqual(scoped["channel_activation_accuracy"], 1.0)
        self.assertEqual(scoped["resolver_accuracy"], 1.0)

        stress = receipt["benchmarks"]["generalization_stress"]
        self.assertEqual(stress["outcome"]["label"], "Outcome B")

        repair = receipt["benchmarks"]["structural_repair"]
        self.assertEqual(repair["targeted_deltas"]["depth_generalization"], 1.0)
        self.assertEqual(repair["targeted_deltas"]["distractor_robustness"], 1.0)
        self.assertEqual(repair["targeted_deltas"]["quantifier_trap_failures"], 1)
        self.assertEqual(repair["targeted_deltas"]["contradiction_misses"], 1)
        self.assertEqual(repair["full_structural_features"]["trace_schema_validity"], 1.0)
        json.dumps(receipt)


if __name__ == "__main__":
    unittest.main()
