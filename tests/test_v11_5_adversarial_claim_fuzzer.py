from __future__ import annotations

import unittest

from benchmarks.gpt2_boundary.adversarial_fuzzer import (
    FuzzerConfig,
    build_and_evaluate,
    generate_adversarial_cases,
)


class AdversarialClaimFuzzerV115Tests(unittest.TestCase):
    def test_deterministic_generation(self) -> None:
        config = FuzzerConfig(seed=115, source_task_count=120, fuzzed_case_count=160, entity_count=180)
        first = generate_adversarial_cases(config)
        second = generate_adversarial_cases(config)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 160)

    def test_all_mutation_types_present(self) -> None:
        config = FuzzerConfig(seed=116, source_task_count=120, fuzzed_case_count=160, entity_count=180)
        rows = generate_adversarial_cases(config)
        mutation_types = {row["mutation_type"] for row in rows}
        self.assertIn("confidence_bait_prefix", mutation_types)
        self.assertIn("contradiction_injection", mutation_types)
        self.assertIn("malformed_claim_injection", mutation_types)
        self.assertIn("paragraph_noise_wrapper", mutation_types)

    def test_fuzzer_report_gates_on_small_run(self) -> None:
        config = FuzzerConfig(seed=117, source_task_count=120, fuzzed_case_count=160, entity_count=180)
        report = build_and_evaluate(config)["report"]
        self.assertEqual(report["fuzzed_case_count"], 160)
        self.assertEqual(report["behavior_accuracy"], 1.0)
        self.assertEqual(report["wrong_accept_count"], 0)
        self.assertEqual(report["accepted_without_typed_support_count"], 0)
        self.assertEqual(report["candidate_graph_contamination_count"], 0)
        self.assertEqual(report["parser_crash_count"], 0)
        self.assertTrue(report["deterministic_rebuild_hash_match"])
        self.assertTrue(report["all_gates_passed"])


if __name__ == "__main__":
    unittest.main()
