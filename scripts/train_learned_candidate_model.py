#!/usr/bin/env python3
"""Train the tiny learned candidate model."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.learned_model.dataset import load_cases, write_split_files
from ts_reasoner.learned_model.train import train_model


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", default="data/learned_candidate_model_train.jsonl")
    parser.add_argument("--model", default="artifacts/learned_candidate_model.json")
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--learning-rate", type=float, default=0.35)
    args = parser.parse_args()

    train_path = ROOT / args.train
    if not train_path.exists():
        write_split_files(ROOT)
    model = train_model(
        load_cases(train_path),
        epochs=args.epochs,
        learning_rate=args.learning_rate,
    )
    model.metadata.update(
        {
            "train_dataset": str(train_path.relative_to(ROOT)),
            "claim": "Tiny learned candidate/channel model; typed verifier remains proof authority.",
            "non_claims": [
                "not an instruction model",
                "not a chatbot",
                "not a verifier",
                "not proof authority",
            ],
        }
    )
    model.save(ROOT / args.model)


if __name__ == "__main__":
    main()
