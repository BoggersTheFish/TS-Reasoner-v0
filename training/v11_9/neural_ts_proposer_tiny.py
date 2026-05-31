from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from training.v11_8.ts_proposer_mini import featurize, load_trace_splits, maybe_limit, verifier_gate


DEFAULT_LABELS = {
    "answer": ("abstain", "no", "yes"),
    "status": ("abstained", "accepted", "rejected"),
}


@dataclass(frozen=True)
class NeuralTinyConfig:
    dim: int = 2048
    hidden: int = 32
    epochs: int = 4
    learning_rate: float = 0.035
    seed: int = 119
    train_limit: int = 1800
    valid_limit: int = 300
    test_limit: int = 300


def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def label_for(row: dict[str, Any], target_key: str) -> str:
    return str(row["target"][target_key])


def _tanh(x: float) -> float:
    if x > 20:
        return 1.0
    if x < -20:
        return -1.0
    return math.tanh(x)


def _softmax(logits: list[float]) -> list[float]:
    peak = max(logits)
    exps = [math.exp(x - peak) for x in logits]
    total = sum(exps)
    return [x / total for x in exps]


@dataclass
class TinyNeuralClassifier:
    labels: list[str]
    dim: int
    hidden: int
    input_weights: list[list[float]]
    output_weights: list[list[float]]
    output_bias: list[float]

    @classmethod
    def fresh(cls, labels: list[str], dim: int, hidden: int, seed: int) -> "TinyNeuralClassifier":
        rng = random.Random(seed)
        # Store input weights as hidden x dim. Tiny hidden/dim keeps artifact sane.
        input_weights = [
            [rng.uniform(-0.015, 0.015) for _ in range(dim)]
            for _ in range(hidden)
        ]
        output_weights = [
            [rng.uniform(-0.015, 0.015) for _ in range(hidden)]
            for _ in labels
        ]
        output_bias = [0.0 for _ in labels]
        return cls(
            labels=list(labels),
            dim=dim,
            hidden=hidden,
            input_weights=input_weights,
            output_weights=output_weights,
            output_bias=output_bias,
        )

    def forward_features(self, features: dict[int, float]) -> tuple[list[float], list[float], list[float]]:
        hidden_raw = []
        hidden_act = []

        for h in range(self.hidden):
            weights = self.input_weights[h]
            raw = sum(weights[idx] * value for idx, value in features.items())
            hidden_raw.append(raw)
            hidden_act.append(_tanh(raw))

        logits = []
        for label_index in range(len(self.labels)):
            row = self.output_weights[label_index]
            logits.append(
                self.output_bias[label_index]
                + sum(row[h] * hidden_act[h] for h in range(self.hidden))
            )

        probs = _softmax(logits)
        return hidden_act, logits, probs

    def predict_features(self, features: dict[int, float]) -> str:
        _hidden, _logits, probs = self.forward_features(features)
        best = max(range(len(self.labels)), key=lambda idx: (probs[idx], self.labels[idx]))
        return self.labels[best]

    def predict_row(self, row: dict[str, Any]) -> str:
        return self.predict_features(featurize(row, self.dim))

    def train_row(self, row: dict[str, Any], gold: str, lr: float) -> float:
        features = featurize(row, self.dim)
        hidden_act, _logits, probs = self.forward_features(features)
        gold_index = self.labels.index(gold)

        loss = -math.log(max(probs[gold_index], 1e-12))

        # Output deltas: p - y
        output_delta = probs[:]
        output_delta[gold_index] -= 1.0

        # Backprop to hidden before mutating output weights.
        hidden_delta = [0.0 for _ in range(self.hidden)]
        for label_index, delta in enumerate(output_delta):
            for h in range(self.hidden):
                hidden_delta[h] += delta * self.output_weights[label_index][h]

        for h in range(self.hidden):
            hidden_delta[h] *= (1.0 - hidden_act[h] * hidden_act[h])

        # Update output layer.
        for label_index, delta in enumerate(output_delta):
            self.output_bias[label_index] -= lr * delta
            for h in range(self.hidden):
                self.output_weights[label_index][h] -= lr * delta * hidden_act[h]

        # Update sparse input layer.
        for h in range(self.hidden):
            delta = hidden_delta[h]
            if delta == 0.0:
                continue
            weights = self.input_weights[h]
            for idx, value in features.items():
                weights[idx] -= lr * delta * value

        return loss

    def to_dict(self) -> dict[str, Any]:
        return {
            "labels": self.labels,
            "dim": self.dim,
            "hidden": self.hidden,
            "input_weights": self.input_weights,
            "output_weights": self.output_weights,
            "output_bias": self.output_bias,
        }


def _labels_for(rows: list[dict[str, Any]], target_key: str) -> list[str]:
    observed = sorted({label_for(row, target_key) for row in rows})
    labels = list(DEFAULT_LABELS.get(target_key, tuple(observed)))
    for label in observed:
        if label not in labels:
            labels.append(label)
    return labels


def train_classifier(
    rows: list[dict[str, Any]],
    target_key: str,
    config: NeuralTinyConfig,
    seed_offset: int,
) -> tuple[TinyNeuralClassifier, dict[str, Any]]:
    labels = _labels_for(rows, target_key)
    model = TinyNeuralClassifier.fresh(
        labels=labels,
        dim=config.dim,
        hidden=config.hidden,
        seed=config.seed + seed_offset,
    )

    epoch_losses = []
    for _epoch in range(config.epochs):
        total_loss = 0.0
        for row in rows:
            total_loss += model.train_row(row, label_for(row, target_key), config.learning_rate)
        epoch_losses.append(total_loss / len(rows) if rows else 0.0)

    return model, {
        "target_key": target_key,
        "labels": labels,
        "epoch_losses": epoch_losses,
        "loss_decreased": epoch_losses[-1] <= epoch_losses[0] if epoch_losses else False,
    }


def evaluate_split(
    rows: list[dict[str, Any]],
    answer_model: TinyNeuralClassifier,
    status_model: TinyNeuralClassifier,
    channel_model: TinyNeuralClassifier,
) -> dict[str, Any]:
    answer_correct = 0
    status_correct = 0
    channel_correct = 0
    gated_answer_correct = 0
    raw_wrong_yes_count = 0
    gated_wrong_accept_count = 0
    verifier_gate_blocked_wrong_yes_count = 0
    accepted_without_typed_support_count = 0

    samples = []

    for row in rows:
        gold_answer = row["target"]["answer"]
        gold_status = row["target"]["status"]
        gold_channel = row["target"]["support_channel"]

        pred_answer = answer_model.predict_row(row)
        pred_status = status_model.predict_row(row)
        pred_channel = channel_model.predict_row(row)

        gate = verifier_gate(row, pred_answer)
        gated_answer = gate["gated_answer"]

        answer_correct += int(pred_answer == gold_answer)
        status_correct += int(pred_status == gold_status)
        channel_correct += int(pred_channel == gold_channel)
        gated_answer_correct += int(gated_answer == gold_answer)

        raw_wrong_yes = pred_answer == "yes" and gold_answer != "yes"
        gated_wrong_accept = gated_answer == "yes" and gold_answer != "yes"

        raw_wrong_yes_count += int(raw_wrong_yes)
        gated_wrong_accept_count += int(gated_wrong_accept)

        if raw_wrong_yes and gated_answer != "yes":
            verifier_gate_blocked_wrong_yes_count += 1

        if gated_answer == "yes" and not gate["accepted_with_typed_support"]:
            accepted_without_typed_support_count += 1

        if len(samples) < 50:
            samples.append({
                "row_id": row["row_id"],
                "gold_answer": gold_answer,
                "pred_answer": pred_answer,
                "gated_answer": gated_answer,
                "gold_status": gold_status,
                "pred_status": pred_status,
                "gold_channel": gold_channel,
                "pred_channel": pred_channel,
                "verifier_status": gate["verifier_status"],
                "verifier_channel_or_reason": gate["verifier_channel_or_reason"],
            })

    total = len(rows)
    return {
        "row_count": total,
        "answer_accuracy": answer_correct / total if total else 0.0,
        "status_accuracy": status_correct / total if total else 0.0,
        "channel_accuracy": channel_correct / total if total else 0.0,
        "gated_answer_accuracy": gated_answer_correct / total if total else 0.0,
        "raw_wrong_yes_count": raw_wrong_yes_count,
        "gated_wrong_accept_count": gated_wrong_accept_count,
        "verifier_gate_blocked_wrong_yes_count": verifier_gate_blocked_wrong_yes_count,
        "accepted_without_typed_support_count": accepted_without_typed_support_count,
        "samples": samples,
    }


def train_and_evaluate(
    root: Path,
    config: NeuralTinyConfig | None = None,
) -> dict[str, Any]:
    config = config or NeuralTinyConfig()
    splits = load_trace_splits(root)

    train_rows = maybe_limit(splits["train"], config.train_limit)
    valid_rows = maybe_limit(splits["valid"], config.valid_limit)
    test_rows = maybe_limit(splits["test"], config.test_limit)

    answer_model, answer_train = train_classifier(train_rows, "answer", config, seed_offset=11)
    status_model, status_train = train_classifier(train_rows, "status", config, seed_offset=22)
    channel_model, channel_train = train_classifier(train_rows, "support_channel", config, seed_offset=33)

    valid_metrics = evaluate_split(valid_rows, answer_model, status_model, channel_model)
    test_metrics = evaluate_split(test_rows, answer_model, status_model, channel_model)

    model_payload = {
        "model_type": "neural_ts_proposer_tiny_stdlib_mlp",
        "release": "v11.9.0",
        "config": asdict(config),
        "answer_model": answer_model.to_dict(),
        "status_model": status_model.to_dict(),
        "channel_model": channel_model.to_dict(),
    }

    training_summary = {
        "answer": answer_train,
        "status": status_train,
        "channel": channel_train,
    }

    report = {
        "release": "v11.9.0",
        "claim": "A tiny pure-stdlib neural proposer can learn verifier-labelled traces while verifier gating preserves zero wrong accepts.",
        "config": asdict(config),
        "train_row_count": len(train_rows),
        "training_summary": training_summary,
        "valid": valid_metrics,
        "test": test_metrics,
    }

    report["all_gates_passed"] = (
        len(train_rows) > 0
        and valid_metrics["row_count"] > 0
        and test_metrics["row_count"] > 0
        and test_metrics["answer_accuracy"] >= 0.55
        and test_metrics["status_accuracy"] >= 0.55
        and test_metrics["channel_accuracy"] >= 0.35
        and test_metrics["gated_wrong_accept_count"] == 0
        and test_metrics["accepted_without_typed_support_count"] == 0
        and valid_metrics["gated_wrong_accept_count"] == 0
        and valid_metrics["accepted_without_typed_support_count"] == 0
        and answer_train["loss_decreased"]
        and status_train["loss_decreased"]
    )

    return {
        "model": model_payload,
        "report": report,
    }
