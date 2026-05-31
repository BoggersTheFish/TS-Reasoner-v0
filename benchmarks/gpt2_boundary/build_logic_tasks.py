from __future__ import annotations

from benchmarks.gpt2_boundary.task_schema import BoundaryTask


TERMS = [
    ("A", "B", "C", "D"),
    ("cats", "mammals", "animals", "living things"),
    ("sparks", "signals", "events", "records"),
    ("proofs", "traces", "evidence", "receipts"),
    ("nodes", "clusters", "graphs", "systems"),
    ("claims", "candidates", "objects", "states"),
    ("routers", "devices", "machines", "assets"),
    ("students", "people", "humans", "organisms"),
    ("notes", "documents", "artifacts", "archives"),
    ("waves", "fields", "patterns", "structures"),
]


def build_direct_support_tasks(start_index: int = 1) -> list[dict]:
    tasks = []
    for offset, (a, b, _c, _d) in enumerate(TERMS, start_index):
        claim = f"all {a} are {b}"
        tasks.append(BoundaryTask(
            case_id=f"logic_direct_{offset:03d}",
            prompt=f"All {a} are {b}. Therefore, are all {a} {b}?",
            expected_answer="yes",
            expected_claim=claim,
            premises=(claim,),
            required_channel="direct_support",
            trap_type="none",
        ).to_dict())
    return tasks


def build_two_hop_transitive_tasks(start_index: int = 1) -> list[dict]:
    tasks = []
    for offset, (a, b, c, _d) in enumerate(TERMS, start_index):
        tasks.append(BoundaryTask(
            case_id=f"logic_transitive_2hop_{offset:03d}",
            prompt=f"All {a} are {b}. All {b} are {c}. Therefore, are all {a} {c}?",
            expected_answer="yes",
            expected_claim=f"all {a} are {c}",
            premises=(f"all {a} are {b}", f"all {b} are {c}"),
            required_channel="transitive_all",
            trap_type="none",
        ).to_dict())
    return tasks


def build_three_hop_transitive_tasks(start_index: int = 1) -> list[dict]:
    tasks = []
    for offset, (a, b, c, d) in enumerate(TERMS, start_index):
        tasks.append(BoundaryTask(
            case_id=f"logic_transitive_3hop_{offset:03d}",
            prompt=f"All {a} are {b}. All {b} are {c}. All {c} are {d}. Therefore, are all {a} {d}?",
            expected_answer="yes",
            expected_claim=f"all {a} are {d}",
            premises=(f"all {a} are {b}", f"all {b} are {c}", f"all {c} are {d}"),
            required_channel="transitive_all",
            trap_type="none",
        ).to_dict())
    return tasks


def build_negative_exclusion_tasks(start_index: int = 1) -> list[dict]:
    tasks = []
    for offset, (a, b, c, _d) in enumerate(TERMS, start_index):
        tasks.append(BoundaryTask(
            case_id=f"logic_negative_{offset:03d}",
            prompt=f"All {a} are {b}. No {b} are {c}. Therefore, are no {a} {c}?",
            expected_answer="yes",
            expected_claim=f"no {a} are {c}",
            premises=(f"all {a} are {b}", f"no {b} are {c}"),
            required_channel="negative_exclusion",
            trap_type="none",
        ).to_dict())
    return tasks
