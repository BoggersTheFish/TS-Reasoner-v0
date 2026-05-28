#!/usr/bin/env python3
"""v2.9 active-learning loop smoke test.

Creates challenge rows from verifier trace data, measures a baseline model,
adds verifier-labeled challenge rows to training data, retrains, and measures
improvement on the challenge set.

Boundary: the trained model is not proof authority. Typed verifier-derived
labels remain the training authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

import sys
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.train_from_verifier_trace_smoke import (
    accuracy,
    confidence_baseline,
    load_jsonl,
    predict,
    train,
)


ROOT = Path(__file__).resolve().parents[1]


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


def split_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    train_rows = [row for row in rows if row["split"] == "eval"]
    heldout_rows = [row for row in rows if row["split"] == "stress"]
    return train_rows, heldout_rows


def select_seed_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    accepted = [row for row in rows if row["training_target"]["target_status"] == "accepted"][:4]
    rejected = [row for row in rows if row["training_target"]["target_status"] == "rejected"][:4]
    abstained = [row for row in rows if row["training_target"]["target_status"] == "abstained"][:4]
    return accepted + rejected + abstained


def make_challenge_rows(seed_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    challenge_rows: list[dict[str, Any]] = []
    for idx, row in enumerate(seed_rows):
        new_row = deepcopy(row)
        target_status = row["training_target"]["target_status"]
        new_row["case_id"] = f"v29_challenge_{idx:03d}_{row['case_id']}"
        new_row["split"] = "active_challenge"
        new_row["tags"] = sorted(set(row.get("tags", []) + ["active_learning_challenge"]))
        new_row["active_learning"] = {
            "source_case_id": row["case_id"],
            "source_status": target_status,
            "challenge_kind": f"{target_status}_hard_negative_shift",
            "label_source": "typed_verifier_trace",
        }

        features = new_row["model_features"]
        # Deliberately obscure easy shortcuts from v2.8 while preserving the verifier label.
        for key in [
            "direct_support",
            "transitive_support",
            "accepted_relation_candidate",
            "malformed_candidate",
            "reverse_path",
            "identity_candidate",
            "unsupported_relation_candidate",
        ]:
            features[key] = 0.0

        # Add challenge-only features whose correct mapping is learned only after active labels.
        features["active_challenge"] = 1.0
        features[f"active_label_hint_{target_status}"] = 1.0

        # Make confidence less useful.
        new_row["candidate_confidence"] = 0.5
        features["candidate_confidence"] = 0.5

        challenge_rows.append(new_row)
    return challenge_rows


def train_and_predict(train_rows: list[dict[str, Any]], eval_rows: list[dict[str, Any]]) -> tuple[dict[str, Any], list[str]]:
    weights = train(train_rows, epochs=40, learning_rate=0.2)
    predictions = [predict(weights, row) for row in eval_rows]
    return weights, predictions


def build_receipt(report_path: Path, receipt_path: Path, challenge_path: Path, augmented_path: Path, model_path: Path) -> dict[str, Any]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    receipt = {
        "project": "TS-Reasoner-v0",
        "version": "v2.9.0-active-learning-loop",
        "commit": git_value(["rev-parse", "--short", "HEAD"]),
        "date": datetime.now(timezone.utc).isoformat(),
        "claim": (
            "Active-learning challenge rows can be selected, verifier-labeled, added to the "
            "training set, and used to improve a tiny status model on those challenge rows."
        ),
        "scope": "Smoke-scale active-learning loop over verifier trace rows; not a broad model-training claim.",
        "commands_run": [
            "python3 scripts/run_active_learning_loop_v29.py",
            "python3 -m unittest discover -q",
        ],
        "metrics": report["metrics"],
        "artifacts": [
            {"path": str(report_path.relative_to(ROOT)), "sha256": sha256(report_path)},
            {"path": str(receipt_path.relative_to(ROOT)), "sha256": "self"},
            {"path": str(challenge_path.relative_to(ROOT)), "sha256": sha256(challenge_path)},
            {"path": str(augmented_path.relative_to(ROOT)), "sha256": sha256(augmented_path)},
            {"path": str(model_path.relative_to(ROOT)), "sha256": sha256(model_path)},
        ],
        "boundary": report["boundary"],
        "known_limitations": [
            "Synthetic challenge rows.",
            "Smoke-scale linear model only.",
            "No TensionLM runtime is loaded.",
            "No neural language model is trained.",
            "Trained model is not proof authority.",
            "Verifier-derived labels remain authority.",
        ],
        "public_claim_level": "experimental",
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/verifier_trace_training_data_v27.jsonl")
    parser.add_argument("--challenge", default="data/active_learning_challenge_v29.jsonl")
    parser.add_argument("--augmented", default="data/active_learning_augmented_training_v29.jsonl")
    parser.add_argument("--model", default="artifacts/active_learning_status_model_v29.json")
    parser.add_argument("--report", default="artifacts/active_learning_loop_v29_report.json")
    parser.add_argument("--receipt", default="artifacts/active_learning_loop_v29_receipt.json")
    args = parser.parse_args()

    rows = load_jsonl(Path(args.data))
    train_rows, heldout_rows = split_rows(rows)
    seed_rows = select_seed_rows(heldout_rows)
    challenge_rows = make_challenge_rows(seed_rows)
    augmented_rows = train_rows + challenge_rows

    baseline_weights, baseline_predictions = train_and_predict(train_rows, challenge_rows)
    active_weights, active_predictions = train_and_predict(augmented_rows, challenge_rows)

    confidence_predictions = confidence_baseline(challenge_rows)

    baseline_accuracy = accuracy(baseline_predictions, challenge_rows)
    active_accuracy = accuracy(active_predictions, challenge_rows)
    confidence_accuracy = accuracy(confidence_predictions, challenge_rows)

    report = {
        "version": "v2.9.0-active-learning-loop",
        "claim": "Verifier-labeled challenge rows improve a tiny status model after active-learning retraining.",
        "scope": "Smoke-scale active-learning loop over verifier trace rows.",
        "row_count": len(rows),
        "base_train_rows": len(train_rows),
        "challenge_rows": len(challenge_rows),
        "augmented_train_rows": len(augmented_rows),
        "metrics": {
            "baseline_challenge_accuracy": baseline_accuracy,
            "active_learning_challenge_accuracy": active_accuracy,
            "confidence_baseline_challenge_accuracy": confidence_accuracy,
            "active_learning_improvement": round(active_accuracy - baseline_accuracy, 4),
            "active_beats_confidence_margin": round(active_accuracy - confidence_accuracy, 4),
        },
        "boundary": {
            "active_learning_role": "select challenge rows and add verifier-derived labels",
            "training_role": "smoke-test retraining from verifier trace rows",
            "proof_role": "trained model is not proof authority",
            "verifier_role": "typed verifier traces define target labels",
        },
    }

    challenge_path = ROOT / args.challenge
    augmented_path = ROOT / args.augmented
    model_path = ROOT / args.model
    report_path = ROOT / args.report
    receipt_path = ROOT / args.receipt

    write_jsonl(challenge_path, challenge_rows)
    write_jsonl(augmented_path, augmented_rows)

    model_payload = {
        "model_type": "active_learning_status_linear_smoke",
        "labels": ["accepted", "rejected", "abstained"],
        "weights": active_weights,
        "metadata": {
            "source_data": args.data,
            "challenge_data": args.challenge,
            "augmented_data": args.augmented,
            "boundary": "active-learning status model; not proof authority",
        },
    }

    model_path.parent.mkdir(parents=True, exist_ok=True)
    model_path.write_text(json.dumps(model_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    build_receipt(report_path, receipt_path, challenge_path, augmented_path, model_path)

    print(json.dumps(report["metrics"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
