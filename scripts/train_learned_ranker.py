#!/usr/bin/env python3
"""Train the tiny v1 learned tension ranker."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ts_reasoner.learned_ranker import train_logistic_ranker
from ts_reasoner.synthetic_data import candidate_dataset_rows, train_eval_split


ARTIFACTS = ROOT / "artifacts"
DATA = ROOT / "data"


def main() -> int:
    ARTIFACTS.mkdir(exist_ok=True)
    DATA.mkdir(exist_ok=True)
    rows = candidate_dataset_rows()
    train_rows, eval_rows = train_eval_split(rows)
    ranker = train_logistic_ranker(train_rows)
    no_cig_ranker = train_logistic_ranker(train_rows, without_cig=True)
    no_issue_ranker = train_logistic_ranker(train_rows, without_issue_kinds=True)
    model_path = ranker.to_json(
        ARTIFACTS / "learned_ranker_v1.json",
        metadata={
            "training_rows": len(train_rows),
            "eval_rows": len(eval_rows),
            "label_source": "synthetic answer-quality target; label=1 means candidate should rank lower",
            "schema_note": "Learned ranker returns the same TensionScore schema as HeuristicTensionRanker.",
        },
    )
    no_cig_path = no_cig_ranker.to_json(
        ARTIFACTS / "learned_ranker_v1_no_cig.json",
        metadata={
            "training_rows": len(train_rows),
            "eval_rows": len(eval_rows),
            "ablation": "CIG-derived features zeroed during training and prediction.",
        },
    )
    no_issue_path = no_issue_ranker.to_json(
        ARTIFACTS / "learned_ranker_v1_no_issue_kinds.json",
        metadata={
            "training_rows": len(train_rows),
            "eval_rows": len(eval_rows),
            "ablation": "Issue-kind features zeroed during training and prediction.",
        },
    )
    summary = {
        "model_path": str(model_path.relative_to(ROOT)),
        "no_cig_model_path": str(no_cig_path.relative_to(ROOT)),
        "no_issue_kind_model_path": str(no_issue_path.relative_to(ROOT)),
        "training_rows": len(train_rows),
        "eval_rows": len(eval_rows),
        "positive_training_labels": sum(int(row["label"]) for row in train_rows),
        "negative_training_labels": sum(1 - int(row["label"]) for row in train_rows),
        "train_template_family": "symbolic",
        "heldout_template_family": "heldout_natural",
    }
    (ARTIFACTS / "learned_ranker_training_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
