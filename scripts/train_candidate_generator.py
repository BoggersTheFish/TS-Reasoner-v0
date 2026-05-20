#!/usr/bin/env python3
"""Train the narrow v0.3 learned candidate-proposal model."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ts_reasoner.generator import train_learned_candidate_generator
from ts_reasoner.synthetic_data import candidate_dataset_rows, train_eval_split


ARTIFACTS = ROOT / "artifacts"


def main() -> int:
    ARTIFACTS.mkdir(exist_ok=True)
    rows = candidate_dataset_rows()
    train_rows, eval_rows = train_eval_split(rows)
    generator = train_learned_candidate_generator(train_rows)
    model_path = generator.to_json(
        ARTIFACTS / "learned_candidate_generator_v03.json",
        metadata={
            "training_rows": len(train_rows),
            "eval_rows": len(eval_rows),
            "scope": "learned template proposal only; existing CIG/ranker/repair pipeline verifies candidates",
            "not_a_full_llm": True,
        },
    )
    summary = {
        "model_path": str(model_path.relative_to(ROOT)),
        "training_rows": len(train_rows),
        "eval_rows": len(eval_rows),
        "template_weights": generator.template_weights,
        "claim": "v0.3.0 adds learned candidate proposal while preserving inspectable CIG/tension/repair verification.",
    }
    (ARTIFACTS / "learned_candidate_generator_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

