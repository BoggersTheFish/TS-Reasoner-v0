#!/usr/bin/env python3
"""Train a tiny status model from v2.7 verifier trace rows.

This is a smoke test: it proves verifier traces are usable supervised training
signal. It is not a broad model-training claim.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


STATUS_LABELS = ["accepted", "rejected", "abstained"]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def dot(weights: dict[str, float], features: dict[str, float]) -> float:
    return sum(weights.get(k, 0.0) * v for k, v in features.items())


def argmax(weights_by_label: dict[str, dict[str, float]], features: dict[str, float]) -> str:
    return max(STATUS_LABELS, key=lambda label: dot(weights_by_label[label], features))


def featurize(row: dict[str, Any]) -> dict[str, float]:
    model_features = row.get("model_features", {})
    verifier = row.get("verifier", {})
    channels = set(row.get("training_target", {}).get("target_channels", []))
    features: dict[str, float] = {"bias": 1.0}

    for key in [
        "candidate_confidence",
        "candidate_quantifier_all",
        "candidate_quantifier_no",
        "candidate_quantifier_some",
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
    ]:
        features[key] = float(model_features.get(key, 0.0) or 0.0)

    features["typed_runtime_available"] = float(bool(verifier.get("typed_runtime_available")))
    features["typed_runtime_settled"] = float(bool(verifier.get("typed_runtime_settled")))
    features["global_tension"] = float(verifier.get("global_tension") or 0.0)

    for channel in [
        "logic_transitivity",
        "surface_structure",
        "directionality",
        "identity_preservation",
        "quantifier_scope",
        "contradiction",
        "malformed_relation",
        "typed_support",
    ]:
        features[f"channel_{channel}"] = float(channel in channels)

    return features


def train(rows: list[dict[str, Any]], epochs: int, learning_rate: float) -> dict[str, dict[str, float]]:
    weights = {label: {} for label in STATUS_LABELS}
    for _ in range(epochs):
        for row in rows:
            features = featurize(row)
            target = row["training_target"]["target_status"]
            predicted = argmax(weights, features)
            if predicted == target:
                continue
            for name, value in features.items():
                weights[target][name] = weights[target].get(name, 0.0) + learning_rate * value
                weights[predicted][name] = weights[predicted].get(name, 0.0) - learning_rate * value
    return weights


def predict(weights: dict[str, dict[str, float]], row: dict[str, Any]) -> str:
    return argmax(weights, featurize(row))


def accuracy(predictions: list[str], rows: list[dict[str, Any]]) -> float:
    if not rows:
        return 0.0
    return round(
        sum(pred == row["training_target"]["target_status"] for pred, row in zip(predictions, rows)) / len(rows),
        4,
    )


def majority_baseline(train_rows: list[dict[str, Any]], eval_rows: list[dict[str, Any]]) -> list[str]:
    counts: dict[str, int] = {}
    for row in train_rows:
        status = row["training_target"]["target_status"]
        counts[status] = counts.get(status, 0) + 1
    majority = max(STATUS_LABELS, key=lambda label: counts.get(label, 0))
    return [majority for _ in eval_rows]


def confidence_baseline(rows: list[dict[str, Any]]) -> list[str]:
    preds = []
    for row in rows:
        confidence = float(row.get("candidate_confidence") or 0.0)
        if confidence >= 0.67:
            preds.append("accepted")
        elif confidence <= 0.35:
            preds.append("rejected")
        else:
            preds.append("abstained")
    return preds


def split_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    train_rows = [row for row in rows if row["split"] == "eval"]
    eval_rows = [row for row in rows if row["split"] == "stress"]
    return train_rows, eval_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/verifier_trace_training_data_v27.jsonl")
    parser.add_argument("--model", default="artifacts/verifier_trace_status_model_v28.json")
    parser.add_argument("--report", default="artifacts/verifier_trace_training_loop_smoke_report.json")
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--learning-rate", type=float, default=0.2)
    args = parser.parse_args()

    rows = load_jsonl(Path(args.data))
    train_rows, eval_rows = split_rows(rows)

    weights = train(train_rows, epochs=args.epochs, learning_rate=args.learning_rate)

    train_predictions = [predict(weights, row) for row in train_rows]
    eval_predictions = [predict(weights, row) for row in eval_rows]

    majority_predictions = majority_baseline(train_rows, eval_rows)
    confidence_predictions = confidence_baseline(eval_rows)

    report = {
        "version": "v2.8.0-training-loop-smoke",
        "claim": "v2.7 verifier trace rows can train a tiny supervised status model above simple baselines.",
        "scope": "Smoke-scale linear classifier over exported verifier trace rows; not a broad model-training claim.",
        "row_count": len(rows),
        "train_rows": len(train_rows),
        "eval_rows": len(eval_rows),
        "metrics": {
            "train_accuracy": accuracy(train_predictions, train_rows),
            "eval_accuracy": accuracy(eval_predictions, eval_rows),
            "majority_baseline_eval_accuracy": accuracy(majority_predictions, eval_rows),
            "confidence_baseline_eval_accuracy": accuracy(confidence_predictions, eval_rows),
            "learned_beats_majority_margin": round(
                accuracy(eval_predictions, eval_rows) - accuracy(majority_predictions, eval_rows), 4
            ),
            "learned_beats_confidence_margin": round(
                accuracy(eval_predictions, eval_rows) - accuracy(confidence_predictions, eval_rows), 4
            ),
        },
        "boundary": {
            "training_role": "smoke-test supervised status prediction from verifier traces",
            "proof_role": "trained model is not proof authority",
            "verifier_role": "typed verifier traces define target labels",
        },
    }

    model_payload = {
        "model_type": "verifier_trace_status_linear_smoke",
        "labels": STATUS_LABELS,
        "weights": weights,
        "metadata": {
            "source_data": args.data,
            "epochs": args.epochs,
            "learning_rate": args.learning_rate,
            "boundary": "status model trained from verifier traces; not proof authority",
        },
    }

    Path(args.model).parent.mkdir(parents=True, exist_ok=True)
    Path(args.model).write_text(json.dumps(model_payload, indent=2, sort_keys=True) + "\n")
    Path(args.report).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    print(json.dumps(report["metrics"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
