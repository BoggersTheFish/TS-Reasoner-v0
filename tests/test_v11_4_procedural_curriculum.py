from __future__ import annotations

import unittest

from benchmarks.gpt2_boundary.procedural_curriculum import (
    CurriculumConfig,
    build_and_validate,
    curriculum_hash,
    generate_curriculum,
    validate_task_label,
)


class ProceduralCurriculumV114Tests(unittest.TestCase):
    def test_deterministic_generation(self) -> None:
        config = CurriculumConfig(seed=114, task_count=120, entity_count=120, distractor_count=1)
        first = generate_curriculum(config)
        second = generate_curriculum(config)
        self.assertEqual(curriculum_hash(first), curriculum_hash(second))
        self.assertEqual(len(first), 120)
        self.assertEqual(len({task["prompt"] for task in first}), 120)

    def test_label_validity_on_small_curriculum(self) -> None:
        config = CurriculumConfig(seed=115, task_count=120, entity_count=140, distractor_count=1)
        tasks = generate_curriculum(config)
        validations = [validate_task_label(task) for task in tasks]
        self.assertTrue(all(row["passed"] for row in validations))

    def test_full_report_gates_on_small_curriculum(self) -> None:
        config = CurriculumConfig(seed=116, task_count=120, entity_count=160, distractor_count=1)
        report = build_and_validate(config)["report"]
        self.assertEqual(report["task_count"], 120)
        self.assertEqual(report["duplicate_task_count"], 0)
        self.assertEqual(report["label_validity"], 1.0)
        self.assertTrue(report["deterministic_rebuild_hash_match"])
        self.assertEqual(report["arena_candidate_graph_contamination_count"], 0)
        self.assertEqual(report["arena_accepted_without_typed_support_count"], 0)


if __name__ == "__main__":
    unittest.main()
