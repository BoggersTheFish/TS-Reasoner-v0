from __future__ import annotations

import unittest

from benchmarks.gpt2_boundary.live_gpt2_adapter import (
    LiveGPT2Config,
    build_boundary_tasks,
    classify_completion,
    dependency_status,
    evaluate_live_gpt2_adapter,
    expected_answer,
    prompt_for_gpt2,
)


class LiveGPT2AdapterV116Tests(unittest.TestCase):
    def test_dependency_status_contract_without_live(self) -> None:
        status = dependency_status(run_live=False)
        self.assertFalse(status.live_requested)
        self.assertFalse(status.live_available)
        self.assertEqual(status.reason, "live_gpt2_not_requested")

    def test_completion_classifier(self) -> None:
        self.assertEqual(classify_completion(" yes, because it follows."), "yes")
        self.assertEqual(classify_completion(" no, this is invalid."), "no")
        self.assertEqual(classify_completion(" abstain, cannot determine."), "abstain")
        self.assertEqual(classify_completion(" purple banana"), "unclassified")

    def test_boundary_task_contract(self) -> None:
        tasks = build_boundary_tasks(task_count=12, seed=116)
        self.assertEqual(len(tasks), 12)
        for task in tasks:
            self.assertIn(expected_answer(task), {"yes", "no", "abstain"})
            self.assertIn("Answer:", prompt_for_gpt2(task))

    def test_adapter_contract_without_live_dependencies(self) -> None:
        report = evaluate_live_gpt2_adapter(
            LiveGPT2Config(task_count=12, seed=117, run_live=False)
        )
        self.assertTrue(report["adapter_contract_passed"])
        self.assertFalse(report["dependency_status"]["live_requested"])
        self.assertEqual(report["ts_reasoner_wrong_accept_count"], 0)
        self.assertEqual(report["ts_reasoner_accepted_without_typed_support_count"], 0)
        self.assertEqual(report["ts_reasoner_candidate_graph_contamination_count"], 0)
        self.assertTrue(report["all_gates_passed"])


if __name__ == "__main__":
    unittest.main()
