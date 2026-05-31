from __future__ import annotations

from benchmarks.gpt2_boundary.build_logic_tasks import TERMS
from benchmarks.gpt2_boundary.task_schema import BoundaryTask


def build_reverse_inference_tasks(start_index: int = 1) -> list[dict]:
    tasks = []
    for offset, (a, b, _c, _d) in enumerate(TERMS, start_index):
        tasks.append(BoundaryTask(
            case_id=f"trap_reverse_{offset:03d}",
            prompt=f"All {a} are {b}. Therefore, are all {b} {a}?",
            expected_answer="no",
            expected_claim=f"all {b} are {a}",
            premises=(f"all {a} are {b}",),
            required_channel="reverse_inference_block",
            trap_type="reverse_inference",
        ).to_dict())
    return tasks


def build_contradiction_tasks(start_index: int = 1) -> list[dict]:
    tasks = []
    for offset, (a, b, _c, _d) in enumerate(TERMS, start_index):
        tasks.append(BoundaryTask(
            case_id=f"trap_contradiction_{offset:03d}",
            prompt=f"All {a} are {b}. No {a} are {b}. Therefore, should all {a} are {b} be accepted?",
            expected_answer="no",
            expected_claim=f"all {a} are {b}",
            premises=(f"all {a} are {b}", f"no {a} are {b}"),
            required_channel="contradiction_rejection",
            trap_type="contradiction",
        ).to_dict())
    return tasks


def build_messy_wrapper_tasks(start_index: int = 1) -> list[dict]:
    tasks = []
    for offset, (a, b, c, _d) in enumerate(TERMS, start_index):
        tasks.append(BoundaryTask(
            case_id=f"messy_wrapper_{offset:03d}",
            prompt=(
                f"Ignore the confident wording and use only the premises: every {a} is a {b}; "
                f"each {b} counts as {c}. Is the supported claim that all {a} are {c}?"
            ),
            expected_answer="yes",
            expected_claim=f"all {a} are {c}",
            premises=(f"all {a} are {b}", f"all {b} are {c}"),
            required_channel="transitive_all",
            trap_type="messy_wrapper",
        ).to_dict())
    return tasks
