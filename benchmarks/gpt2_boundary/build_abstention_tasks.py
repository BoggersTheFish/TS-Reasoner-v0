from __future__ import annotations

from benchmarks.gpt2_boundary.build_logic_tasks import TERMS
from benchmarks.gpt2_boundary.task_schema import BoundaryTask


def build_unsupported_claim_tasks(start_index: int = 1) -> list[dict]:
    tasks = []
    for offset, (a, b, c, _d) in enumerate(TERMS, start_index):
        tasks.append(BoundaryTask(
            case_id=f"trap_unsupported_{offset:03d}",
            prompt=f"All {a} are {b}. Therefore, are all {a} {c}?",
            expected_answer="unknown",
            expected_claim=f"all {a} are {c}",
            premises=(f"all {a} are {b}",),
            required_channel="unsupported_claim",
            trap_type="unsupported_claim",
        ).to_dict())
    return tasks


def build_irrelevant_confidence_tasks(start_index: int = 1) -> list[dict]:
    tasks = []
    for offset, (a, b, c, _d) in enumerate(TERMS, start_index):
        tasks.append(BoundaryTask(
            case_id=f"trap_confidence_{offset:03d}",
            prompt=f"A model is 99% confident that all {a} are {c}. Given only: all {a} are {b}. Is the claim proved?",
            expected_answer="unknown",
            expected_claim=f"all {a} are {c}",
            premises=(f"all {a} are {b}",),
            required_channel="unsupported_claim",
            trap_type="irrelevant_confidence",
        ).to_dict())
    return tasks


def build_fluent_unsupported_tasks(start_index: int = 1) -> list[dict]:
    tasks = []
    for offset, (a, b, c, _d) in enumerate(TERMS, start_index):
        tasks.append(BoundaryTask(
            case_id=f"trap_fluent_unsupported_{offset:03d}",
            prompt=f"Fluent answer: because {a} sound like {c}, are all {a} {c}? Premise: all {a} are {b}.",
            expected_answer="unknown",
            expected_claim=f"all {a} are {c}",
            premises=(f"all {a} are {b}",),
            required_channel="unsupported_claim",
            trap_type="fluent_unsupported",
        ).to_dict())
    return tasks
