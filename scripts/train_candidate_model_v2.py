#!/usr/bin/env python3
"""Train Candidate Model v2 on the v2.5 benchmark-derived dataset."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.learned_model.dataset import load_cases
from ts_reasoner.learned_model.train import train_model


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", default="data/candidate_model_v2_train.jsonl")
    parser.add_argument("--model", default="artifacts/candidate_model_v2.json")
    parser.add_argument("--epochs", type=int, default=120)
    parser.add_argument("--learning-rate", type=float, default=0.25)
    args = parser.parse_args()

    train_path = ROOT / args.train
    model_path = ROOT / args.model

    cases = load_cases(train_path)
    model = train_model(cases, epochs=args.epochs, learning_rate=args.learning_rate)
    model.metadata.update(
        {
            "version": "candidate-model-v2",
            "train_dataset": str(train_path.relative_to(ROOT)),
            "source": "v2.5 benchmark harness derived candidate set",
            "claim": (
                "Candidate Model v2 learns to rank candidate graph claims on a benchmark-derived "
                "surface while typed verifier channels remain proof authority."
            ),
            "non_claims": [
                "not a verifier",
                "not proof authority",
                "not broad NLP",
                "not a chatbot",
                "not a TensionLM runtime",
            ],
        }
    )
    model.save(model_path)
    print(f"saved {model_path}")


if __name__ == "__main__":
    main()
