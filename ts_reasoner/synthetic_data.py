"""Synthetic dataset generation for learned tension-ranker experiments."""

from __future__ import annotations

from typing import Dict, Iterable, List

from .cig_checker import CIGChecker
from .features import extract_chain_features
from .generator import DeterministicHeuristicGenerator
from .ranker import HeuristicTensionRanker


SYMBOL_TRIPLES = [
    ("A", "B", "C"),
    ("cats", "mammals", "animals"),
    ("pilots", "engineers", "careful"),
    ("robots", "tools", "useful"),
    ("students", "readers", "learners"),
    ("sparks", "fires", "hazards"),
    ("artists", "makers", "creators"),
    ("maps", "guides", "documents"),
]


def synthetic_tasks() -> List[Dict[str, object]]:
    tasks: List[Dict[str, object]] = []
    for index, (a, b, c) in enumerate(SYMBOL_TRIPLES, start=1):
        tasks.extend(
            [
                {
                    "id": f"valid_all_all_{index}",
                    "task_type": "valid",
                    "question": f"If all {a} are {b} and all {b} are {c}, are all {a} {c}?",
                    "premises": [f"All {a} are {b}.", f"All {b} are {c}."],
                },
                {
                    "id": f"invalid_some_all_{index}",
                    "task_type": "invalid",
                    "question": f"If some {a} are {b} and all {b} are {c}, are all {a} {c}?",
                    "premises": [f"Some {a} are {b}.", f"All {b} are {c}."],
                },
                {
                    "id": f"contradiction_{index}",
                    "task_type": "invalid",
                    "question": f"If all {a} are {c} and no {a} are {c}, are all {a} {c}?",
                    "premises": [f"All {a} are {c}.", f"No {a} are {c}."],
                },
                {
                    "id": f"missing_premise_{index}",
                    "task_type": "invalid",
                    "question": f"Are all {a} {c}?",
                    "premises": [],
                },
            ]
        )
    return tasks


def candidate_dataset_rows(tasks: Iterable[Dict[str, object]] | None = None) -> List[Dict[str, object]]:
    """Create candidate-chain rows labeled by synthetic answer-quality targets."""
    generator = DeterministicHeuristicGenerator()
    checker = CIGChecker()
    heuristic = HeuristicTensionRanker()
    rows: List[Dict[str, object]] = []
    for task in tasks or synthetic_tasks():
        candidates = generator.generate(str(task["question"]), task.get("premises") or None)
        for chain in candidates:
            cig = checker.check(chain)
            score = heuristic.score(chain, cig)
            rows.append(
                {
                    "task_id": task["id"],
                    "task_type": task["task_type"],
                    "chain_id": chain.chain_id,
                    "question": task["question"],
                    "premises": task.get("premises") or [],
                    "features": extract_chain_features(chain, cig),
                    "heuristic_global_tension": score.global_tension,
                    "label": _bad_candidate_label(task, chain.final_answer),
                    "issue_kinds": [issue.kind for issue in score.issues],
                }
            )
    return rows


def _bad_candidate_label(task: Dict[str, object], final_answer: str) -> int:
    """Return 1 for candidates the synthetic task says should rank lower."""
    answer = final_answer.lower()
    task_id = str(task["id"])
    if task_id.startswith("valid_all_all"):
        return 0 if "all" in answer and "not enough" not in answer else 1
    if task_id.startswith("invalid_some_all"):
        return 0 if "not enough" in answer or "do not force" in answer else 1
    if task_id.startswith("contradiction"):
        return 0 if "contradiction" in answer else 1
    if task_id.startswith("missing_premise"):
        return 0 if "not enough" in answer or "more information" in answer else 1
    return 1


def train_eval_split(rows: List[Dict[str, object]]) -> tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    train = []
    eval_rows = []
    for index, row in enumerate(rows):
        if index % 4 == 0:
            eval_rows.append(row)
        else:
            train.append(row)
    return train, eval_rows
