#!/usr/bin/env python3
"""Evaluate candidate-proposal coverage for v0.3."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ts_reasoner.generator import (
    DeterministicHeuristicGenerator,
    LearnedCandidateGenerator,
    RandomCandidateProposer,
    train_learned_candidate_generator,
)
from ts_reasoner.synthetic_data import candidate_dataset_rows, synthetic_tasks, train_eval_split


ARTIFACTS = ROOT / "artifacts"


def main() -> int:
    ARTIFACTS.mkdir(exist_ok=True)
    rows = candidate_dataset_rows()
    train_rows, _eval_rows = train_eval_split(rows)
    learned_safe = train_learned_candidate_generator(train_rows)
    learned_raw = LearnedCandidateGenerator(
        template_weights=learned_safe.template_weights,
        threshold=learned_safe.threshold,
        min_candidates=0,
        safety_fallback=False,
    )
    generators = [
        ("deterministic_generator", DeterministicHeuristicGenerator()),
        ("learned_generator", learned_raw),
        ("learned_generator_plus_safety_fallback", learned_safe),
        ("random_candidate_proposer", RandomCandidateProposer()),
    ]
    tasks = synthetic_tasks()
    table = [evaluate_generator(name, generator, tasks) for name, generator in generators]
    summary = {
        "comparison": "v0.3_candidate_generator_coverage",
        "tasks": len(tasks),
        "coverage_table": table,
        "metrics": [
            "average_candidates_proposed_per_task",
            "stable_candidate_included_rate",
            "adversarial_confident_suppressed_rate",
            "contradiction_aware_included_when_needed_rate",
        ],
        "caveat": "This evaluates learned candidate selection/proposal over toy chain families, not open-ended reasoning generation.",
    }
    (ARTIFACTS / "candidate_generator_coverage.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def evaluate_generator(name: str, generator, tasks: List[Dict[str, object]]) -> Dict[str, object]:
    total_candidates = 0
    stable_included = 0
    adversarial_tasks = 0
    adversarial_suppressed = 0
    contradiction_tasks = 0
    contradiction_included = 0
    for task in tasks:
        chains = generator.generate(str(task["question"]), task.get("premises") or None)
        ids = {chain.chain_id for chain in chains}
        total_candidates += len(chains)
        stable_ids = stable_candidate_ids(task)
        if ids.intersection(stable_ids):
            stable_included += 1
        if task.get("adversarial"):
            adversarial_tasks += 1
            if "candidate_adversarial_confident" not in ids:
                adversarial_suppressed += 1
        if str(task["id"]).startswith("contradiction"):
            contradiction_tasks += 1
            if "candidate_a_contradiction_aware" in ids:
                contradiction_included += 1
    return {
        "generator": name,
        "average_candidates_proposed_per_task": round(total_candidates / max(1, len(tasks)), 4),
        "stable_candidate_included_rate": round(stable_included / max(1, len(tasks)), 4),
        "adversarial_confident_suppressed_rate": round(adversarial_suppressed / max(1, adversarial_tasks), 4),
        "contradiction_aware_included_when_needed_rate": round(
            contradiction_included / max(1, contradiction_tasks), 4
        ),
    }


def stable_candidate_ids(task: Dict[str, object]) -> set[str]:
    task_id = str(task["id"])
    if task_id.startswith("contradiction"):
        return {"candidate_a_contradiction_aware"}
    return {"candidate_cautious"}


if __name__ == "__main__":
    raise SystemExit(main())
