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
    model_path = ranker.to_json(
        ARTIFACTS / "learned_ranker_v1.json",
        metadata={
            "training_rows": len(train_rows),
            "eval_rows": len(eval_rows),
            "label_source": "synthetic answer-quality target; label=1 means candidate should rank lower",
            "schema_note": "Learned ranker returns the same TensionScore schema as HeuristicTensionRanker.",
        },
    )
    summary = {
        "model_path": str(model_path.relative_to(ROOT)),
        "training_rows": len(train_rows),
        "eval_rows": len(eval_rows),
        "positive_training_labels": sum(int(row["label"]) for row in train_rows),
        "negative_training_labels": sum(1 - int(row["label"]) for row in train_rows),
    }
    (ARTIFACTS / "learned_ranker_training_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
