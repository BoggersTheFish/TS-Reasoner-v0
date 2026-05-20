#!/usr/bin/env python3
"""Compare LearnedTensionRanker against HeuristicTensionRanker."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ts_reasoner.cig_checker import CIGChecker
from ts_reasoner.generator import DeterministicHeuristicGenerator
from ts_reasoner.learned_ranker import LearnedTensionRanker, train_logistic_ranker
from ts_reasoner.ranker import HeuristicTensionRanker
from ts_reasoner.synthetic_data import candidate_dataset_rows, synthetic_tasks, train_eval_split


ARTIFACTS = ROOT / "artifacts"


def main() -> int:
    ARTIFACTS.mkdir(exist_ok=True)
    rows = candidate_dataset_rows()
    train_rows, eval_rows = train_eval_split(rows)
    ranker_path = ARTIFACTS / "learned_ranker_v1.json"
    if ranker_path.exists():
        learned = LearnedTensionRanker.from_json(ranker_path)
    else:
        learned = train_logistic_ranker(train_rows)
        learned.to_json(ranker_path)

    row_metrics = compare_rows(learned, eval_rows)
    selection_metrics = compare_selection(learned)
    summary = {
        "comparison": "LearnedTensionRanker_vs_HeuristicTensionRanker",
        "eval_rows": len(eval_rows),
        "learned_label_accuracy": row_metrics["learned_label_accuracy"],
        "heuristic_label_accuracy": row_metrics["heuristic_label_accuracy"],
        "mean_absolute_tension_error": row_metrics["mean_absolute_tension_error"],
        "mean_absolute_label_error": row_metrics["mean_absolute_label_error"],
        "selection_tasks": selection_metrics["selection_tasks"],
        "selection_agreement": selection_metrics["selection_agreement"],
        "output_schema_identical": True,
        "notes": [
            "Labels are answer-quality ranking targets over synthetic variants, not benchmark ground truth.",
            "v1 learns the tension field interface, not a general reasoning model.",
            "Both rankers return TensionScore and can be used by TSReasoner without changing ReasonerOutput.",
        ],
    }
    (ARTIFACTS / "ranker_comparison.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def compare_rows(learned: LearnedTensionRanker, eval_rows):
    learned_correct = 0
    heuristic_correct = 0
    total_error = 0.0
    total_label_error = 0.0
    for row in eval_rows:
        probability = learned.predict_probability(row["features"])
        learned_label = 1 if probability >= learned.threshold else 0
        heuristic_label = 1 if float(row["heuristic_global_tension"]) >= 0.15 else 0
        label = int(row["label"])
        learned_correct += 1 if learned_label == label else 0
        heuristic_correct += 1 if heuristic_label == label else 0
        total_error += abs(probability - float(row["heuristic_global_tension"]))
        total_label_error += abs(probability - label)
    count = max(1, len(eval_rows))
    return {
        "learned_label_accuracy": round(learned_correct / count, 4),
        "heuristic_label_accuracy": round(heuristic_correct / count, 4),
        "mean_absolute_tension_error": round(total_error / count, 4),
        "mean_absolute_label_error": round(total_label_error / count, 4),
    }


def compare_selection(learned: LearnedTensionRanker):
    generator = DeterministicHeuristicGenerator()
    checker = CIGChecker()
    heuristic = HeuristicTensionRanker()
    agreements = 0
    tasks = synthetic_tasks()
    for task in tasks:
        candidates = generator.generate(str(task["question"]), task.get("premises") or None)
        scored_heuristic = []
        scored_learned = []
        for chain in candidates:
            cig = checker.check(chain)
            scored_heuristic.append((chain.chain_id, heuristic.score(chain, cig)))
            scored_learned.append((chain.chain_id, learned.score(chain, cig)))
        h_selected = min(scored_heuristic, key=lambda item: (item[1].global_tension, -item[1].stability, item[0]))[0]
        l_selected = min(scored_learned, key=lambda item: (item[1].global_tension, -item[1].stability, item[0]))[0]
        agreements += 1 if h_selected == l_selected else 0
    return {
        "selection_tasks": len(tasks),
        "selection_agreement": round(agreements / max(1, len(tasks)), 4),
    }


if __name__ == "__main__":
    raise SystemExit(main())
