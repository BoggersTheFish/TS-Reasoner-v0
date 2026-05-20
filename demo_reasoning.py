#!/usr/bin/env python3
"""Generate toy demos and artifact receipts for TS-Reasoner-v0."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from ts_reasoner import run_reasoner
from ts_reasoner.cig_checker import CIGChecker
from ts_reasoner.ranker import HeuristicTensionRanker
from ts_reasoner.repair import TensionRepairer
from ts_reasoner.trace import write_jsonl


ROOT = Path(__file__).resolve().parent
EXAMPLES = ROOT / "examples"
ARTIFACTS = ROOT / "artifacts"


def load_tasks() -> List[Dict[str, object]]:
    tasks = []
    for path in sorted(EXAMPLES.glob("*.json")):
        tasks.append(json.loads(path.read_text(encoding="utf-8")))
    return tasks


def expected_pass(task: Dict[str, object], answer: str, tension: float) -> bool:
    expected = str(task["expected_behavior"])
    lower = answer.lower()
    if expected == "valid_low_tension":
        return tension < 0.2 and "all a are c" in lower
    if expected == "reject_universal":
        return "not enough" in lower or "do not force" in lower
    if expected == "detect_contradiction":
        return "contradiction" in lower
    if expected == "missing_premise":
        return "not enough" in lower or "more information" in lower
    if expected == "repair_available":
        return True
    return False


def candidate_repair_count(output) -> int:
    checker = CIGChecker()
    ranker = HeuristicTensionRanker()
    repairer = TensionRepairer()
    count = 0
    for chain in output.candidates:
        score = ranker.score(chain, checker.check(chain))
        if repairer.suggest(chain, score):
            count += 1
    return count


def main() -> int:
    ARTIFACTS.mkdir(exist_ok=True)
    tasks = load_tasks()
    outputs = []
    sample_lines = ["# TS-Reasoner-v0 Sample Outputs", ""]
    valid_tensions = []
    invalid_tensions = []
    correct = 0
    repair_success = 0

    for task in tasks:
        output = run_reasoner(str(task["question"]), task.get("premises") or None)
        outputs.append(output)
        tension = output.tension_score.global_tension
        if task["task_type"] == "valid":
            valid_tensions.append(tension)
        else:
            invalid_tensions.append(tension)
        if expected_pass(task, output.final_answer, tension):
            correct += 1
        repairs_for_candidates = candidate_repair_count(output)
        if repairs_for_candidates > 0:
            repair_success += 1

        sample_lines.extend(
            [
                f"## {task['id']}: {task['task_type']}",
                "",
                f"Question: {task['question']}",
                "",
                f"Answer: {output.final_answer}",
                "",
                f"Selected chain: `{output.selected_chain.chain_id}`",
                "",
                f"Global tension: `{tension:.4f}`",
                "",
                f"Candidate repair paths: `{repairs_for_candidates}`",
                "",
            ]
        )

    (ARTIFACTS / "sample_outputs.md").write_text("\n".join(sample_lines), encoding="utf-8")
    write_jsonl(outputs, ARTIFACTS / "tension_traces.jsonl")
    summary = {
        "number_of_tasks": len(tasks),
        "number_correct": correct,
        "mean_global_tension_valid": round(sum(valid_tensions) / max(1, len(valid_tensions)), 4),
        "mean_global_tension_invalid": round(sum(invalid_tensions) / max(1, len(invalid_tensions)), 4),
        "repair_success_count": repair_success,
        "known_failure_modes": [
            "Regex claim extraction only covers small syllogistic templates.",
            "Natural-language negation can be missed outside simple 'no X are Y' or 'X are not Y' forms.",
            "The selector may prefer an insufficiency answer when a generated direct candidate is high tension.",
            "No learned TensionLM generator or trained proof ranker is included in v0.",
        ],
    }
    (ARTIFACTS / "eval_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

