#!/usr/bin/env python3
"""Stress-test typed-channel calibrator generalization on heldout structures."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner import run_reasoner
from ts_reasoner.calibration.calibrator import TypedChannelCalibrator
from ts_reasoner.calibration.features import CHANNELS, extract_case_features


DEFAULT_RESOLVERS = {
    "logic_transitivity": "added_inferred_edge",
    "identity_preservation": "preserved_distinct_nodes",
    "directionality": "blocked_reverse_inference",
    "surface_structure": "tagged_premise_inferred_candidate_edges",
    "confidence_abstention": "abstained_or_answered",
    "contradiction": "flagged_contradiction",
    "quantifier_scope": "blocked_some_to_all_upgrade",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_value(args: list[str], default: str = "unknown") -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return default


def evaluate_case(case: dict[str, Any], calibrator: TypedChannelCalibrator) -> dict[str, Any]:
    output = run_reasoner(case["question"], case.get("premises", []))
    expected_channels = case.get("expected_channels", {})
    expected_resolutions = case.get("expected_resolutions", {})
    channel_rows = []
    for channel in CHANNELS:
        expected_active = bool(expected_channels.get(channel, False))
        expected_resolution = expected_resolutions.get(
            channel,
            DEFAULT_RESOLVERS[channel] if expected_active else "not_activated",
        )
        features = extract_case_features(case, output, channel)
        predicted_active = calibrator.predicts_activation(channel, features)
        predicted_resolution = calibrator.resolver_for(channel, predicted_active)
        channel_rows.append(
            {
                "channel": channel,
                "expected_active": expected_active,
                "predicted_active": predicted_active,
                "activation_ok": predicted_active == expected_active,
                "expected_resolution": expected_resolution,
                "predicted_resolution": predicted_resolution,
                "resolver_ok": predicted_resolution == expected_resolution,
                "predicted_weight": calibrator.channel_weight(channel) if predicted_active else 0.0,
            }
        )
    answer_ok = case["expected_answer_contains"].lower() in output.final_answer.lower()
    return {
        "task_id": case["task_id"],
        "task_type": case["task_type"],
        "question": case["question"],
        "answer": output.final_answer,
        "expected_answer_contains": case["expected_answer_contains"],
        "answer_ok": answer_ok,
        "trace_schema_valid": "tension_channels" in output.trace and "typed_runtime" in output.trace,
        "channel_rows": channel_rows,
    }


def main() -> int:
    data_path = ROOT / "data" / "typed_channel_calibrator_stress.jsonl"
    model_path = ROOT / "artifacts" / "typed_channel_calibrator.json"
    if not model_path.exists():
        raise SystemExit("missing calibrator artifact; run scripts/train_typed_channel_calibrator.py first")
    calibrator = TypedChannelCalibrator.from_json(model_path)
    cases = load_jsonl(data_path)
    results = [evaluate_case(case, calibrator) for case in cases]
    metrics = compute_metrics(results)
    report = {
        "headline": "Typed-Channel Calibrator Generalization Stress",
        "goal": "Test whether the typed-channel calibrator generalizes beyond the exact trace surface it was trained on.",
        "stress_dataset": str(data_path.relative_to(ROOT)),
        "model_path": str(model_path.relative_to(ROOT)),
        "case_count": len(results),
        "metrics": metrics,
        "outcome": classify_outcome(metrics),
        "possible_outcomes": {
            "A": "Calibrator generalizes cleanly; strong evidence that typed trace supervision is reusable.",
            "B": "Calibrator works on renaming but fails deeper chains; next channel/features need work.",
            "C": "Calibrator overfits current trace surface; receipt detects overfit instead of hiding it.",
        },
        "results": results,
    }
    report_path = ROOT / "artifacts" / "typed_channel_calibrator_stress_report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt = {
        "project": "TS-Reasoner-v0",
        "version": "typed-channel-calibrator-generalization-stress-v0",
        "commit": git_value(["rev-parse", "--short", "HEAD"]),
        "date": datetime.now(timezone.utc).isoformat(),
        "claim": "Typed-channel calibrator generalization is stress-tested against heldout structure instead of assumed from training metrics.",
        "scope": "Heldout synthetic stress cases for variable renaming, depth, distractors, quantifiers, contradiction placement, adversarial reverse/identity queries, heldout relation forms, and noisy surface forms.",
        "inputs": [str(data_path.relative_to(ROOT)), str(model_path.relative_to(ROOT))],
        "commands_run": ["python3 scripts/evaluate_typed_channel_calibrator_stress.py"],
        "tests": {},
        "benchmarks": metrics,
        "artifacts": [{"path": str(report_path.relative_to(ROOT)), "sha256": sha256(report_path)}],
        "known_limitations": [
            "Stress cases are synthetic and small.",
            "The calibrator is not retrained on the stress set.",
            "Failures are expected to expose feature/channel limits, not hidden.",
            "TensionLM remains out of scope.",
        ],
        "tensions_detected": ["calibrator training metrics may overstate heldout robustness"],
        "tensions_resolved": ["added heldout generalization stress receipt"],
        "unresolved_tensions": ["feature/channel revisions depend on observed stress failures"],
        "public_claim_level": "experimental",
    }
    receipt_path = ROOT / "artifacts" / "typed_channel_calibrator_stress_receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def compute_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
    channel_rows = [row for result in results for row in result["channel_rows"]]
    activation_accuracy = sum(row["activation_ok"] for row in channel_rows) / max(1, len(channel_rows))
    resolver_accuracy = sum(row["resolver_ok"] for row in channel_rows) / max(1, len(channel_rows))
    answer_accuracy = sum(result["answer_ok"] for result in results) / max(1, len(results))
    return {
        "heldout_answer_accuracy": round(answer_accuracy, 4),
        "heldout_channel_activation_accuracy": round(activation_accuracy, 4),
        "heldout_resolver_accuracy": round(resolver_accuracy, 4),
        "depth_generalization_accuracy": round(_case_type_accuracy(results, "deeper_chain"), 4),
        "distractor_robustness": round(_case_type_accuracy(results, "distractor_premises"), 4),
        "variable_renaming_accuracy": round(_case_type_accuracy(results, "variable_renaming"), 4),
        "reverse_fallacy_count": _miss_count(results, "reverse_adversarial", "directionality"),
        "identity_collapse_count": _miss_count(results, "identity_adversarial", "identity_preservation"),
        "quantifier_trap_failure_count": _miss_count(results, "quantifier_trap", "quantifier_scope"),
        "contradiction_miss_count": _miss_count(results, "contradiction_placement", "contradiction"),
        "trace_schema_validity": round(sum(result["trace_schema_valid"] for result in results) / max(1, len(results)), 4),
    }


def _case_type_accuracy(results: list[dict[str, Any]], task_type: str) -> float:
    subset = [result for result in results if result["task_type"] == task_type]
    if not subset:
        return 0.0
    return sum(result["answer_ok"] and all(row["activation_ok"] for row in result["channel_rows"]) for result in subset) / len(subset)


def _miss_count(results: list[dict[str, Any]], task_type: str, channel: str) -> int:
    count = 0
    for result in results:
        if result["task_type"] != task_type:
            continue
        row = next(item for item in result["channel_rows"] if item["channel"] == channel)
        if not row["predicted_active"]:
            count += 1
    return count


def classify_outcome(metrics: dict[str, Any]) -> dict[str, str]:
    if (
        metrics["heldout_channel_activation_accuracy"] >= 0.9
        and metrics["heldout_resolver_accuracy"] >= 0.9
        and metrics["depth_generalization_accuracy"] >= 0.9
        and metrics["distractor_robustness"] >= 0.9
    ):
        return {"label": "Outcome A", "meaning": "Calibrator generalizes cleanly on this stress surface."}
    if metrics["variable_renaming_accuracy"] >= 0.9 and metrics["depth_generalization_accuracy"] < 0.9:
        return {"label": "Outcome B", "meaning": "Calibrator handles renaming but exposes depth/feature limits."}
    return {"label": "Outcome C", "meaning": "Calibrator overfits current trace surface; receipt exposes the limit."}


if __name__ == "__main__":
    raise SystemExit(main())
