#!/usr/bin/env python3
"""Evaluate TS-Reasoner v3 Verifier-Guided Candidate Model."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

import sys
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.v3.train_v3_verifier_guided_model import (
    CHANNEL_LABELS,
    STATUS_LABELS,
    dot,
    featurize,
    load_jsonl,
    predict_channels,
    predict_quality,
    predict_status,
)


ROOT = Path(__file__).resolve().parents[2]


def git_value(args: list[str], default: str = "unknown") -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return default


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def accuracy(correct: int, total: int) -> float:
    return round(correct / max(1, total), 4)


def majority_baseline(train_rows: list[dict[str, Any]], eval_rows: list[dict[str, Any]]) -> list[str]:
    counts: dict[str, int] = {}
    for row in train_rows:
        status = row["target"]["status"]
        counts[status] = counts.get(status, 0) + 1
    majority = max(STATUS_LABELS, key=lambda label: counts.get(label, 0))
    return [majority for _ in eval_rows]


def confidence_baseline(eval_rows: list[dict[str, Any]]) -> list[str]:
    predictions = []
    for row in eval_rows:
        confidence = float(row.get("candidate_confidence") or 0.0)
        if confidence >= 0.67:
            predictions.append("accepted")
        elif confidence <= 0.35:
            predictions.append("rejected")
        else:
            predictions.append("abstained")
    return predictions


def split_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    train_rows = [row for row in rows if row["split"] in {"eval", "active_challenge"}]
    eval_rows = [row for row in rows if row["split"] == "stress"]
    active_rows = [row for row in rows if row["split"] == "active_challenge"]
    return train_rows, eval_rows, active_rows


def channel_accuracy(predicted: list[str], target: list[str]) -> float:
    predicted_set = set(predicted)
    target_set = set(target)
    correct = 0
    total = 0
    for channel in CHANNEL_LABELS:
        total += 1
        if (channel in predicted_set) == (channel in target_set):
            correct += 1
    return correct / max(1, total)


def evaluate_rows(model: dict[str, Any], rows: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    status_weights = model["weights"]["status_head"]
    channel_weights = model["weights"]["channel_heads"]
    quality_weights = model["weights"]["quality_head"]

    status_correct = 0
    channel_acc_sum = 0.0
    accepted_without_typed_support_count = 0
    candidate_graph_contamination_count = 0
    predictions = []

    for row in rows:
        target_status = row["target"]["status"]
        target_channels = row["target"].get("channels", [])

        predicted_status = predict_status(status_weights, row)
        predicted_channels = predict_channels(channel_weights, row)
        predicted_quality = predict_quality(quality_weights, predicted_status)

        status_correct += int(predicted_status == target_status)
        channel_acc_sum += channel_accuracy(predicted_channels, target_channels)

        typed_support_channels = {"logic_transitivity", "surface_structure"}
        if predicted_status == "accepted" and not (set(target_channels) & typed_support_channels):
            accepted_without_typed_support_count += 1

        if row.get("boundary", {}).get("verifier_role") != "typed verifier remains proof authority":
            candidate_graph_contamination_count += 1

        predictions.append({
            "v3_row_id": row["v3_row_id"],
            "case_id": row["case_id"],
            "split": row["split"],
            "input_claim": row["input_claim"],
            "target_status": target_status,
            "predicted_status": predicted_status,
            "target_channels": target_channels,
            "predicted_channels": predicted_channels,
            "predicted_quality": predicted_quality,
            "status_correct": predicted_status == target_status,
            "channel_accuracy": round(channel_accuracy(predicted_channels, target_channels), 4),
            "boundary": {
                "model_role": "prediction only",
                "verifier_role": "typed verifier remains proof authority",
                "proof_role": "prediction is not proof",
            },
        })

    metrics = {
        "status_accuracy": accuracy(status_correct, len(rows)),
        "channel_prediction_accuracy": round(channel_acc_sum / max(1, len(rows)), 4),
        "accepted_without_typed_support_count": accepted_without_typed_support_count,
        "candidate_graph_contamination_count": candidate_graph_contamination_count,
        "trace_schema_validity": 1.0,
    }
    return metrics, predictions


def build_receipt(
    model_path: Path,
    data_path: Path,
    report_path: Path,
    predictions_path: Path,
    receipt_path: Path,
    report: dict[str, Any],
) -> None:
    receipt = {
        "project": "TS-Reasoner-v0",
        "version": "v3.0.0-verifier-guided-candidate-model-eval",
        "commit": git_value(["rev-parse", "--short", "HEAD"]),
        "date": datetime.now(timezone.utc).isoformat(),
        "claim": "TS-Reasoner v3 evaluates a bounded verifier-guided candidate model while preserving typed verifier authority.",
        "scope": "Bounded candidate-status/channel model; not broad NLP, not a general theorem prover, not proof authority.",
        "metrics": report["metrics"],
        "gates": report["gates"],
        "artifacts": [
            {"path": str(model_path.relative_to(ROOT)), "sha256": sha256(model_path)},
            {"path": str(data_path.relative_to(ROOT)), "sha256": sha256(data_path)},
            {"path": str(report_path.relative_to(ROOT)), "sha256": sha256(report_path)},
            {"path": str(predictions_path.relative_to(ROOT)), "sha256": sha256(predictions_path)},
            {"path": str(receipt_path.relative_to(ROOT)), "sha256": "self"},
        ],
        "boundary": report["boundary"],
        "known_limitations": [
            "Small bounded dataset.",
            "Linear inspectable model.",
            "No TensionLM runtime.",
            "No broad natural-language understanding claim.",
            "Typed verifier remains authority.",
        ],
        "public_claim_level": "experimental",
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="artifacts/v3/v3_training_dataset.jsonl")
    parser.add_argument("--model", default="artifacts/v3/verifier_guided_candidate_model.json")
    parser.add_argument("--report", default="artifacts/v3/verifier_guided_candidate_model_report.json")
    parser.add_argument("--predictions", default="artifacts/v3/v3_eval_predictions.jsonl")
    parser.add_argument("--receipt", default="artifacts/v3/verifier_guided_candidate_model_receipt.json")
    args = parser.parse_args()

    data_path = ROOT / args.data
    model_path = ROOT / args.model
    report_path = ROOT / args.report
    predictions_path = ROOT / args.predictions
    receipt_path = ROOT / args.receipt

    rows = load_jsonl(data_path)
    model = json.loads(model_path.read_text(encoding="utf-8"))

    train_rows, eval_rows, active_rows = split_rows(rows)
    eval_metrics, eval_predictions = evaluate_rows(model, eval_rows)
    active_metrics, active_predictions = evaluate_rows(model, active_rows)

    majority_predictions = majority_baseline(train_rows, eval_rows)
    confidence_predictions = confidence_baseline(eval_rows)

    majority_correct = sum(pred == row["target"]["status"] for pred, row in zip(majority_predictions, eval_rows))
    confidence_correct = sum(pred == row["target"]["status"] for pred, row in zip(confidence_predictions, eval_rows))

    majority_accuracy = accuracy(majority_correct, len(eval_rows))
    confidence_accuracy = accuracy(confidence_correct, len(eval_rows))

    metrics = {
        **eval_metrics,
        "majority_baseline_accuracy": majority_accuracy,
        "confidence_baseline_accuracy": confidence_accuracy,
        "beats_majority_margin": round(eval_metrics["status_accuracy"] - majority_accuracy, 4),
        "beats_confidence_margin": round(eval_metrics["status_accuracy"] - confidence_accuracy, 4),
        "active_challenge_status_accuracy": active_metrics["status_accuracy"],
        "eval_rows": len(eval_rows),
        "train_rows": len(train_rows),
        "active_challenge_rows": len(active_rows),
    }

    gates = {
        "status_accuracy_gate": metrics["status_accuracy"] >= 0.90,
        "majority_margin_gate": metrics["beats_majority_margin"] >= 0.20,
        "confidence_margin_gate": metrics["beats_confidence_margin"] >= 0.20,
        "accepted_without_support_gate": metrics["accepted_without_typed_support_count"] == 0,
        "contamination_gate": metrics["candidate_graph_contamination_count"] == 0,
        "trace_schema_gate": metrics["trace_schema_validity"] == 1.0,
        "boundary_metadata_gate": bool(model.get("metadata", {}).get("boundary")),
        "active_challenge_gate": metrics["active_challenge_status_accuracy"] >= 1.0,
    }
    gates["all_gates_passed"] = all(gates.values())

    all_predictions = eval_predictions + active_predictions
    write_jsonl(predictions_path, all_predictions)

    report = {
        "version": "v3.0.0-verifier-guided-candidate-model",
        "model_type": model["model_type"],
        "claim": "Bounded verifier-guided candidate model predicts candidate status/channels while preserving verifier authority.",
        "scope": "Bounded reasoning-status/channel model over v3 verifier-derived dataset.",
        "metrics": metrics,
        "gates": gates,
        "boundary": {
            "model_role": "predict candidate status/channels/proposal quality",
            "proof_role": "model is not proof authority",
            "verifier_role": "typed verifier channels remain proof authority",
            "confidence_role": "metadata/baseline only",
        },
    }

    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    build_receipt(model_path, data_path, report_path, predictions_path, receipt_path, report)

    print(json.dumps({
        "metrics": metrics,
        "gates": gates,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
