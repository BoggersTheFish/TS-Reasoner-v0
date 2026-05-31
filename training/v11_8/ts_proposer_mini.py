from __future__ import annotations

import hashlib
import json
import math
import re
from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ts_reasoner.support_path_verifier import parse_claim, verify_support_path


TOKEN_RE = re.compile(r"[a-z0-9_]+")
DEFAULT_LABELS = {
    "answer": ("abstain", "no", "yes"),
    "status": ("abstained", "accepted", "rejected"),
}


@dataclass(frozen=True)
class ProposerMiniConfig:
    dim: int = 4096
    epochs: int = 4
    learning_rate: float = 1.0
    train_limit: int = 0
    valid_limit: int = 0
    test_limit: int = 0


def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def feature_index(feature: str, dim: int) -> int:
    return int(stable_hash(feature)[:12], 16) % dim


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_trace_splits(root: Path) -> dict[str, list[dict[str, Any]]]:
    base = root / "artifacts" / "v11_7"
    return {
        "train": load_jsonl(base / "verifier_trace_train.jsonl"),
        "valid": load_jsonl(base / "verifier_trace_valid.jsonl"),
        "test": load_jsonl(base / "verifier_trace_test.jsonl"),
    }


def maybe_limit(rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    if limit and limit > 0:
        return rows[:limit]
    return rows


def _token_features(text: str) -> list[str]:
    tokens = TOKEN_RE.findall(text.lower())
    features: list[str] = []

    for token in tokens:
        features.append(f"tok={token}")

    for a, b in zip(tokens, tokens[1:]):
        features.append(f"bi={a}_{b}")

    for a, b, c in zip(tokens, tokens[1:], tokens[2:]):
        features.append(f"tri={a}_{b}_{c}")

    return features


def _parsed_premises(row: dict[str, Any]) -> list[Any]:
    parsed = []
    for premise in row.get("premises", []):
        claim = parse_claim(str(premise))
        if claim is not None:
            parsed.append(claim)
    return parsed


def _all_path_length(subject: str, predicate: str, all_edges: set[tuple[str, str]]) -> int | None:
    if subject == predicate:
        return 0

    graph: dict[str, list[str]] = {}
    for left, right in all_edges:
        graph.setdefault(left, []).append(right)

    queue: deque[tuple[str, int]] = deque([(subject, 0)])
    seen = {subject}

    while queue:
        node, depth = queue.popleft()
        for nxt in graph.get(node, []):
            if nxt == predicate:
                return depth + 1
            if nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, depth + 1))

    return None


def structural_features(row: dict[str, Any]) -> list[str]:
    features: list[str] = []
    premises = _parsed_premises(row)
    target = row.get("target", {})
    claim_text = str(target.get("claim", row.get("candidate_claim", "")))
    claim = parse_claim(claim_text)

    features.append(f"premise_count={min(len(premises), 8)}")
    features.append(f"source={row.get('source', 'unknown')}")

    if claim is None:
        features.append("claim=parse_none")
        return features

    features.append(f"claim_quantifier={claim.quantifier}")

    if claim.subject == claim.predicate:
        features.append("claim_identity=true")

    all_edges = {(item.subject, item.predicate) for item in premises if item.quantifier == "all"}
    no_edges = {(item.subject, item.predicate) for item in premises if item.quantifier == "no"}

    if all_edges & no_edges:
        features.append("premise_direct_contradiction=true")

    if (claim.subject, claim.predicate) in all_edges and claim.quantifier == "all":
        features.append("direct_support=all")
    if (claim.subject, claim.predicate) in no_edges and claim.quantifier == "no":
        features.append("direct_support=no")

    if claim.quantifier == "all" and (claim.predicate, claim.subject) in all_edges:
        features.append("reverse_inference_trap=true")

    if claim.quantifier == "all":
        path_len = _all_path_length(claim.subject, claim.predicate, all_edges)
        if path_len is not None:
            features.append("all_path_exists=true")
            features.append(f"all_path_len={min(path_len, 8)}")
        else:
            features.append("all_path_exists=false")

    if claim.quantifier == "no":
        if (claim.subject, claim.predicate) in no_edges:
            features.append("negative_direct_exists=true")
        for mid, blocked in no_edges:
            if blocked != claim.predicate:
                continue
            path_len = _all_path_length(claim.subject, mid, all_edges)
            if path_len is not None:
                features.append("negative_exclusion_exists=true")
                features.append(f"negative_exclusion_path_len={min(path_len, 8)}")

    if not any(feature.startswith(("direct_support=", "all_path_exists=true", "negative_direct_exists=true", "negative_exclusion_exists=true")) for feature in features):
        features.append("support_missing=true")

    return features


def featurize(row: dict[str, Any], dim: int) -> dict[int, float]:
    raw_features = ["bias"]
    raw_features.extend(_token_features(str(row.get("input", ""))))
    raw_features.extend(structural_features(row))

    vector: dict[int, float] = {}
    for feature in raw_features:
        idx = feature_index(feature, dim)
        vector[idx] = vector.get(idx, 0.0) + 1.0

    # Squash repeated text features so long prompts do not dominate structure.
    for idx, value in list(vector.items()):
        vector[idx] = 1.0 + math.log(value)

    return vector


@dataclass
class LinearClassifier:
    labels: list[str]
    dim: int
    weights: dict[str, list[float]]
    bias: dict[str, float]

    @classmethod
    def fresh(cls, labels: list[str], dim: int) -> "LinearClassifier":
        return cls(
            labels=list(labels),
            dim=dim,
            weights={label: [0.0] * dim for label in labels},
            bias={label: 0.0 for label in labels},
        )

    def score(self, features: dict[int, float], label: str) -> float:
        weights = self.weights[label]
        return self.bias[label] + sum(weights[idx] * value for idx, value in features.items())

    def predict_features(self, features: dict[int, float]) -> str:
        return max(self.labels, key=lambda label: (self.score(features, label), label))

    def predict_row(self, row: dict[str, Any]) -> str:
        return self.predict_features(featurize(row, self.dim))

    def update(self, features: dict[int, float], gold: str, pred: str, lr: float) -> None:
        if gold == pred:
            return

        self.bias[gold] += lr
        self.bias[pred] -= lr

        gold_weights = self.weights[gold]
        pred_weights = self.weights[pred]
        for idx, value in features.items():
            delta = lr * value
            gold_weights[idx] += delta
            pred_weights[idx] -= delta

    def to_dict(self) -> dict[str, Any]:
        return {
            "labels": self.labels,
            "dim": self.dim,
            "weights": self.weights,
            "bias": self.bias,
        }


def label_for(row: dict[str, Any], target_key: str) -> str:
    return str(row["target"][target_key])


def train_classifier(
    rows: list[dict[str, Any]],
    target_key: str,
    config: ProposerMiniConfig,
) -> LinearClassifier:
    observed_labels = sorted({label_for(row, target_key) for row in rows})
    labels = list(DEFAULT_LABELS.get(target_key, tuple(observed_labels)))
    for label in observed_labels:
        if label not in labels:
            labels.append(label)

    model = LinearClassifier.fresh(labels, config.dim)

    for _epoch in range(config.epochs):
        for row in rows:
            gold = label_for(row, target_key)
            features = featurize(row, config.dim)
            pred = model.predict_features(features)
            model.update(features, gold, pred, config.learning_rate)

    return model


def verifier_gate(row: dict[str, Any], predicted_answer: str) -> dict[str, Any]:
    claim = str(row["target"]["claim"])
    result = verify_support_path(list(row["premises"]), claim)

    if predicted_answer == "yes":
        if result["status"] == "accepted":
            gated_answer = "yes"
        elif result["status"] == "rejected":
            gated_answer = "no"
        else:
            gated_answer = "abstain"
    else:
        gated_answer = predicted_answer

    return {
        "gated_answer": gated_answer,
        "verifier_status": result["status"],
        "verifier_channel_or_reason": (
            result.get("support", {}).get("channel") if result.get("support") else result.get("reason", "")
        ),
        "accepted_with_typed_support": bool(result.get("support", {}).get("verifier_passed", False)),
    }


def evaluate_split(
    rows: list[dict[str, Any]],
    answer_model: LinearClassifier,
    status_model: LinearClassifier,
    channel_model: LinearClassifier,
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
    config: ProposerMiniConfig | None = None,
) -> dict[str, Any]:
    config = config or ProposerMiniConfig()
    splits = load_trace_splits(root)

    train_rows = maybe_limit(splits["train"], config.train_limit)
    valid_rows = maybe_limit(splits["valid"], config.valid_limit)
    test_rows = maybe_limit(splits["test"], config.test_limit)

    answer_model = train_classifier(train_rows, "answer", config)
    status_model = train_classifier(train_rows, "status", config)
    channel_model = train_classifier(train_rows, "support_channel", config)

    valid_metrics = evaluate_split(valid_rows, answer_model, status_model, channel_model)
    test_metrics = evaluate_split(test_rows, answer_model, status_model, channel_model)

    model_payload = {
        "model_type": "ts_proposer_mini_hashed_perceptron",
        "release": "v11.8.0",
        "config": asdict(config),
        "answer_model": answer_model.to_dict(),
        "status_model": status_model.to_dict(),
        "channel_model": channel_model.to_dict(),
    }

    report = {
        "release": "v11.8.0",
        "claim": "A tiny stdlib proposer baseline can learn verifier-labelled answer/status/channel predictions while verifier gating preserves zero wrong accepts.",
        "config": asdict(config),
        "train_row_count": len(train_rows),
        "valid": valid_metrics,
        "test": test_metrics,
    }

    report["all_gates_passed"] = (
        len(train_rows) > 0
        and valid_metrics["row_count"] > 0
        and test_metrics["row_count"] > 0
        and test_metrics["answer_accuracy"] >= 0.75
        and test_metrics["status_accuracy"] >= 0.75
        and test_metrics["channel_accuracy"] >= 0.65
        and test_metrics["gated_wrong_accept_count"] == 0
        and test_metrics["accepted_without_typed_support_count"] == 0
        and valid_metrics["gated_wrong_accept_count"] == 0
        and valid_metrics["accepted_without_typed_support_count"] == 0
    )

    return {
        "model": model_payload,
        "report": report,
    }
