import unittest

from ts_reasoner.tensionproof_smoke import evaluate_tensionproof_smoke


class TensionProofSmokeTests(unittest.TestCase):
    def test_smoke_eval_reports_target_and_baselines(self):
        report = evaluate_tensionproof_smoke()

        self.assertEqual(report["target"], "TensionProofLM-22M")
        self.assertIn("tensionprooflm_smoke", report["baselines"])
        self.assertIn("generator_ranker_verifier_loop", report["baselines"])
        self.assertEqual(report["baselines"]["tensionprooflm_smoke"]["total"], 16)
        self.assertGreaterEqual(report["baselines"]["tensionprooflm_smoke"]["label_accuracy"], 0.75)
        self.assertEqual(report["scope"], "tiny smoke-training/eval artifact; not a trained 22M model")


if __name__ == "__main__":
    unittest.main()
