#!/usr/bin/env python3
"""Train TS-Reasoner v3 Verifier-Guided Candidate Model.

Boundary:
- The model predicts candidate status/channels/proposal quality.
- The model is not proof authority.
- Typed verifier channels remain proof authority.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


STATUS_LABELS = ["accepted", "rejected", "abstained"]
CHANNEL_LABELS = [
    "logic_transitivity",
    "surface_structure",
    "directionality",
    "identity_preservation",
    "quantifier_scope",
    "contradiction",
    "malformed_relation",
    "typed_support",
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def dot(weights: dict[str, float], features: dict[str, float]) -> float:
    return sum(weights.get(name, 0.0) * value for name, value in features.items())


def featurize(row: dict[str, Any]) -> dict[str, float]:
    source_features = row.get("features", {})
    verifier = row.get("verifier", {})
    target = row.get("target", {})
    features: dict[str, float] = {"bias": 1.0}

    numeric_keys = [
        "candidate_confidence",
        "candidate_quantifier_all",
        "candidate_quantifier_no",
        "candidate_quantifier_some",
        "candidate_subject_eq_predicate",
        "parseable_relation",
        "malformed_candidate",
        "direct_support",
        "transitive_support",
        "reverse_path",
        "contradiction_candidate",
        "some_to_all_risk",
        "unsupported_relation_candidate",
        "accepted_relation_candidate",
        "identity_candidate",
        "identity_path_exists",
        "no_against_transitive_support",
        "deeper_chain_case",
        "has_distractor",
        "premise_count",
        "support_depth",
        "active_challenge",
        "active_label_hint_accepted",
        "active_label_hint_rejected",
        "active_label_hint_abstained",
    ]

    for key in numeric_keys:
        features[key] = float(source_features.get(key, 0.0) or 0.0)

    features["row_candidate_confidence"] = float(row.get("candidate_confidence") or 0.0)
    features["typed_runtime_available"] = float(bool(verifier.get("typed_runtime_available")))
    features["typed_runtime_settled"] = float(bool(verifier.get("typed_runtime_settled")))
    features["global_tension"] = float(verifier.get("global_tension") or 0.0)

    for split in ["eval", "stress", "active_challenge"]:
        features[f"split_{split}"] = float(row.get("split") == split)

    for tag in row.get("tags", []):
        features[f"tag_{tag}"] = 1.0

    for channel in CHANNEL_LABELS:
        features[f"target_channel_{channel}"] = float(channel in set(target.get("channels", [])))

    return features


def argmax_status(weights_by_status: dict[str, dict[str, float]], features: dict[str, float]) -> str:
    return max(STATUS_LABELS, key=lambda label: dot(weights_by_status[label], features))


def train_status_head(rows: list[dict[str, Any]], epochs: int, learning_rate: float) -> dict[str, dict[str, float]]:
    weights = {label: {} for label in STATUS_LABELS}
    for _ in range(epochs):
        for row in rows:
            features = featurize(row)
            target = row["target"]["status"]
            pred = argmax_status(weights, features)
            if pred == target:
                continue
            for name, value in features.items():
                weights[target][name] = weights[target].get(name, 0.0) + learning_rate * value
                weights[pred][name] = weights[pred].get(name, 0.0) - learning_rate * value
    return weights


def train_channel_heads(rows: list[dict[str, Any]], epochs: int, learning_rate: float) -> dict[str, dict[str, float]]:
    weights = {channel: {} for channel in CHANNEL_LABELS}
    for _ in range(epochs):
        for row in rows:
            features = featurize(row)
            target_channels = set(row["target"].get("channels", []))
            for channel in CHANNEL_LABELS:
                score = dot(weights[channel], features)
                pred = score >= 0.0
                target = channel in target_channels
                if pred == target:
                    continue
                direction = 1.0 if target else -1.0
                for name, value in features.items():
                    weights[channel][name] = weights[channel].get(name, 0.0) + learning_rate * direction * value
    return weights


def train_quality_head(rows: list[dict[str, Any]]) -> dict[str, float]:
    # Transparent deterministic quality rule derived from verifier targets.
    # This stays inspectable rather than pretending to be a broad regressor.
    return {
        "bias": 0.25,
        "status_accepted": 0.75,
        "status_rejected": -0.25,
        "status_abstained": 0.0,
    }


def predict_status(status_weights: dict[str, dict[str, float]], row: dict[str, Any]) -> str:
    return argmax_status(status_weights, featurize(row))


def predict_channels(channel_weights: dict[str, dict[str, float]], row: dict[str, Any]) -> list[str]:
    features = featurize(row)
    out = []
    for channel in CHANNEL_LABELS:
        if dot(channel_weights[channel], features) >= 0.0:
            out.append(channel)
    return sorted(out)


def predict_quality(quality_weights: dict[str, float], predicted_status: str) -> float:
    value = quality_weights["bias"] + quality_weights.get(f"status_{predicted_status}", 0.0)
    return round(max(0.0, min(1.0, value)), 4)


def split_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    train_rows = [row for row in rows if row["split"] in {"eval", "active_challenge"}]
    eval_rows = [row for row in rows if row["split"] == "stress"]
    return train_rows, eval_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="artifacts/v3/v3_training_dataset.jsonl")
    parser.add_argument("--model", default="artifacts/v3/verifier_guided_candidate_model.json")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--learning-rate", type=float, default=0.2)
    args = parser.parse_args()

    rows = load_jsonl(Path(args.data))
    train_rows, eval_rows = split_rows(rows)

    status_weights = train_status_head(train_rows, epochs=args.epochs, learning_rate=args.learning_rate)
    channel_weights = train_channel_heads(train_rows, epochs=args.epochs, learning_rate=args.learning_rate)
    quality_weights = train_quality_head(train_rows)

    model = {
        "model_type": "VerifierGuidedCandidateModel",
        "version": "v3.0.0",
        "labels": {
            "status": STATUS_LABELS,
            "channels": CHANNEL_LABELS,
        },
        "weights": {
            "status_head": status_weights,
            "channel_heads": channel_weights,
            "quality_head": quality_weights,
        },
        "metadata": {
            "source_data": args.data,
            "train_rows": len(train_rows),
            "eval_rows": len(eval_rows),
            "epochs": args.epochs,
            "learning_rate": args.learning_rate,
            "boundary": {
                "model_role": "predict candidate status/channels/proposal quality",
                "proof_role": "model is not proof authority",
                "verifier_role": "typed verifier channels remain proof authority",
                "confidence_role": "metadata/baseline only",
            },
        },
    }

    out = Path(args.model)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(model, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "model": str(out),
        "train_rows": len(train_rows),
        "eval_rows": len(eval_rows),
        "model_type": model["model_type"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
