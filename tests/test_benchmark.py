import unittest
from pathlib import Path

from ts_reasoner.benchmark import BenchmarkRunner, answer_matches, load_benchmark
from ts_reasoner.tension_agents import TensionCoordinator


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "external_benchmark_v08.jsonl"
DATA_V1 = ROOT / "data" / "external_benchmark_v1.jsonl"
COUPLING = ROOT / "artifacts" / "learned_coupling_matrix_v05.json"


class BenchmarkHarnessTests(unittest.TestCase):
    def test_loads_externalized_v08_tasks(self):
        tasks = load_benchmark(DATA)
        categories = {task.category for task in tasks}

        self.assertEqual(len(tasks), 10)
        self.assertEqual(
            categories,
            {
                "boolean_word_problem",
                "contradiction_detection",
                "repair_needed",
                "small_proof_chain",
                "syllogism_variant",
            },
        )
        self.assertTrue(all(task.question for task in tasks))
        self.assertTrue(all(task.acceptable_answers for task in tasks))

    def test_answer_matching_normalizes_surface_form(self):
        self.assertTrue(answer_matches("Therefore all cats are animals.", ["all cats are animals"]))
        self.assertFalse(answer_matches("Not enough information.", ["all cats are animals"]))

    def test_v09_transitive_bridge_closes_v08_loop_gap(self):
        tasks = load_benchmark(DATA)
        coordinator = TensionCoordinator.from_json(COUPLING)
        report = BenchmarkRunner(tension_coordinator=coordinator).evaluate(tasks)

        self.assertEqual(report["task_count"], 10)
        self.assertEqual(set(report["baselines"]), {"direct", "random_selector", "ranker_only", "full_control_loop"})
        self.assertEqual(report["baselines"]["direct"]["correct"], 4)
        self.assertEqual(report["baselines"]["random_selector"]["correct"], 6)
        self.assertEqual(report["baselines"]["ranker_only"]["correct"], 10)
        self.assertEqual(report["baselines"]["full_control_loop"]["correct"], 10)
        self.assertEqual(report["baselines"]["full_control_loop"]["settled_rate"], 1.0)

        proof_chain = report["by_category"]["small_proof_chain"]
        self.assertEqual(proof_chain["direct"]["correct"], 2)
        self.assertEqual(proof_chain["full_control_loop"]["correct"], 2)

    def test_v1_suite_includes_expected_passes_and_known_failures(self):
        tasks = load_benchmark(DATA_V1)
        statuses = {task.expected_status for task in tasks}
        coordinator = TensionCoordinator.from_json(COUPLING)
        report = BenchmarkRunner(tension_coordinator=coordinator).evaluate(tasks)

        self.assertEqual(len(tasks), 20)
        self.assertEqual(statuses, {"expected_pass", "known_failure"})
        self.assertIn("adversarial_known_limit", report["by_category"])
        self.assertIn("abstention_insufficient", report["by_category"])
        self.assertIn("multi_step_symbolic_proof", report["by_category"])
        self.assertIn("noisy_candidate_repair", report["by_category"])
        self.assertIn("provenance_weighted_reasoning", report["by_category"])
        self.assertIn("graph_consistency", report["by_category"])
        self.assertIn("refusal_to_settle", report["by_category"])
        self.assertIn("known_failure", report["by_expected_status"])
        self.assertEqual(report["by_expected_status"]["expected_pass"]["full_control_loop"]["correct"], 16)


if __name__ == "__main__":
    unittest.main()
