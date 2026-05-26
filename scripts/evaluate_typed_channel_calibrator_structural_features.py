#!/usr/bin/env python3
"""Evaluate structural feature repair for typed-channel calibration."""

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

VARIANTS = {
    "original_calibrator": {
        "label": "original_calibrator",
        "feature_groups": [],
    },
    "path_features": {
        "label": "+ path features",
        "feature_groups": ["path"],
    },
    "distractor_features": {
        "label": "+ distractor features",
        "feature_groups": ["path", "distractor"],
    },
    "quantifier_features": {
        "label": "+ quantifier features",
        "feature_groups": ["path", "distractor", "quantifier"],
    },
    "contradiction_placement_features": {
        "label": "+ contradiction-placement features",
        "feature_groups": ["path", "distractor", "contradiction"],
    },
    "full_structural_features": {
        "label": "full_structural_features",
        "feature_groups": ["path", "distractor", "quantifier", "contradiction"],
    },
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


def evaluate_variant(
    cases: list[dict[str, Any]],
    calibrator: TypedChannelCalibrator,
    variant_name: str,
) -> dict[str, Any]:
    variant = VARIANTS[variant_name]
    feature_groups = set(variant["feature_groups"])
    results = [
        evaluate_case(case, calibrator, variant_name, feature_groups)
        for case in cases
    ]
    return {
        "label": variant["label"],
        "enabled_feature_groups": sorted(feature_groups),
        "metrics": compute_metrics(results),
        "results": results,
    }


def evaluate_case(
    case: dict[str, Any],
    calibrator: TypedChannelCalibrator,
    variant_name: str,
    feature_groups: set[str],
) -> dict[str, Any]:
    output = run_reasoner(case["question"], case.get("premises", []))
    expected_channels = case.get("expected_channels", {})
    expected_resolutions = case.get("expected_resolutions", {})
    channel_rows = []
    feature_snapshot = None

    for channel in CHANNELS:
        expected_active = bool(expected_channels.get(channel, False))
        expected_resolution = expected_resolutions.get(
            channel,
            DEFAULT_RESOLVERS[channel] if expected_active else "not_activated",
        )
        features = extract_case_features(case, output, channel)
        if feature_snapshot is None:
            feature_snapshot = _feature_snapshot(features)
        predicted_active, activation_source = predict_activation(
            channel,
            features,
            calibrator,
            feature_groups,
        )
        predicted_resolution = predict_resolution(
            channel,
            predicted_active,
            activation_source,
            calibrator,
            feature_groups,
        )
        channel_rows.append(
            {
                "channel": channel,
                "expected_active": expected_active,
                "predicted_active": predicted_active,
                "activation_ok": predicted_active == expected_active,
                "activation_source": activation_source,
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
        "variant": variant_name,
        "question": case["question"],
        "answer": output.final_answer,
        "expected_answer_contains": case["expected_answer_contains"],
        "answer_ok": answer_ok,
        "trace_schema_valid": "tension_channels" in output.trace and "typed_runtime" in output.trace,
        "feature_snapshot": feature_snapshot,
        "channel_rows": channel_rows,
    }


def predict_activation(
    channel: str,
    features: dict[str, Any],
    calibrator: TypedChannelCalibrator,
    feature_groups: set[str],
) -> tuple[bool, str]:
    base_active = calibrator.predicts_activation(channel, features)
    if base_active or not feature_groups:
        return base_active, "original_calibrator"

    if "path" in feature_groups and _path_repair_activates(channel, features, allow_distractors=False):
        return True, "path_features"
    if "distractor" in feature_groups and _path_repair_activates(channel, features, allow_distractors=True):
        return True, "distractor_features"
    if "quantifier" in feature_groups and _quantifier_repair_activates(channel, features):
        return True, "quantifier_features"
    if "contradiction" in feature_groups and _contradiction_repair_activates(channel, features):
        return True, "contradiction_placement_features"
    return False, "original_calibrator"


def predict_resolution(
    channel: str,
    active: bool,
    activation_source: str,
    calibrator: TypedChannelCalibrator,
    feature_groups: set[str],
) -> str:
    if not active:
        return "not_activated"
    if activation_source != "original_calibrator":
        return DEFAULT_RESOLVERS[channel]
    if "contradiction" in feature_groups and channel == "contradiction":
        return DEFAULT_RESOLVERS[channel]
    return calibrator.resolver_for(channel, active)


def compute_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
    channel_rows = [row for result in results for row in result["channel_rows"]]
    activation_accuracy = sum(row["activation_ok"] for row in channel_rows) / max(1, len(channel_rows))
    resolver_accuracy = sum(row["resolver_ok"] for row in channel_rows) / max(1, len(channel_rows))
    answer_accuracy = sum(result["answer_ok"] for result in results) / max(1, len(results))
    return {
        "heldout_answer_accuracy": round(answer_accuracy, 4),
        "heldout_channel_activation_accuracy": round(activation_accuracy, 4),
        "heldout_resolver_accuracy": round(resolver_accuracy, 4),
        "depth_generalization": round(_case_type_accuracy(results, "deeper_chain"), 4),
        "distractor_robustness": round(_case_type_accuracy(results, "distractor_premises"), 4),
        "quantifier_trap_failures": _miss_count(results, "quantifier_trap", "quantifier_scope"),
        "contradiction_misses": _miss_count(results, "contradiction_placement", "contradiction"),
        "trace_schema_validity": round(sum(result["trace_schema_valid"] for result in results) / max(1, len(results)), 4),
    }


def classify_outcome(variants: dict[str, dict[str, Any]]) -> dict[str, str]:
    original = variants["original_calibrator"]["metrics"]
    full = variants["full_structural_features"]["metrics"]
    improved = (
        full["depth_generalization"] > original["depth_generalization"]
        or full["distractor_robustness"] > original["distractor_robustness"]
        or full["quantifier_trap_failures"] < original["quantifier_trap_failures"]
        or full["contradiction_misses"] < original["contradiction_misses"]
    )
    if full["trace_schema_validity"] == 1.0 and improved:
        return {
            "label": "targeted_structural_repair_improved",
            "meaning": "Query-relevant structural features reduce the stress failures without changing trace schema validity.",
        }
    return {
        "label": "structural_repair_limit_exposed",
        "meaning": "The repair did not reduce the target stress failures; further channel/features are needed.",
    }


def main() -> int:
    data_path = ROOT / "data" / "typed_channel_calibrator_stress.jsonl"
    model_path = ROOT / "artifacts" / "typed_channel_calibrator.json"
    if not model_path.exists():
        raise SystemExit("missing calibrator artifact; run scripts/train_typed_channel_calibrator.py first")

    calibrator = TypedChannelCalibrator.from_json(model_path)
    cases = load_jsonl(data_path)
    variants = {
        name: evaluate_variant(cases, calibrator, name)
        for name in VARIANTS
    }
    report = {
        "headline": "Structural Feature Repair for Typed-Channel Calibration",
        "claim": "Generalization stress showed the calibrator handled renaming but failed on depth, distractors, quantifier traps, and contradiction placement. This branch adds query-relevant graph features to test whether those failures are structural-feature gaps rather than failures of the typed-channel approach.",
        "stress_dataset": str(data_path.relative_to(ROOT)),
        "model_path": str(model_path.relative_to(ROOT)),
        "case_count": len(cases),
        "variants": variants,
        "outcome": classify_outcome(variants),
        "old_failure_preserved": "artifacts/typed_channel_calibrator_stress_report.json",
    }
    report_path = ROOT / "artifacts" / "typed_channel_calibrator_structural_features_report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    receipt = {
        "project": "TS-Reasoner-v0",
        "version": "typed-channel-calibrator-structural-features-v0",
        "commit": git_value(["rev-parse", "--short", "HEAD"]),
        "date": datetime.now(timezone.utc).isoformat(),
        "claim": report["claim"],
        "scope": "Structural feature repair over the existing heldout calibrator stress dataset; TensionLM remains out of scope.",
        "inputs": [str(data_path.relative_to(ROOT)), str(model_path.relative_to(ROOT))],
        "commands_run": ["python3 scripts/evaluate_typed_channel_calibrator_structural_features.py"],
        "tests": {},
        "benchmarks": {
            name: item["metrics"]
            for name, item in variants.items()
        },
        "artifacts": [{"path": str(report_path.relative_to(ROOT)), "sha256": sha256(report_path)}],
        "known_limitations": [
            "The stress dataset is synthetic and small.",
            "This evaluates structural feature repair against the existing calibrator artifact.",
            "The evaluator does not claim broad natural-language generalization.",
            "Existing reasoner answers are reported separately from channel/resolver repair metrics.",
        ],
        "tensions_detected": [
            "original calibrator overfit shallow premise counts and missed query-relevant structural paths",
            "quantifier and contradiction placement failures required explicit path-local features",
        ],
        "tensions_resolved": [
            "added shortest-path, distractor, quantifier-signature, contradiction-placement, and candidate-operation features",
            "added ablation report comparing original and structural repair variants",
        ],
        "unresolved_tensions": [
            "future work should train a model directly over the structural feature surface",
            "heldout relation shapes remain intentionally unsupported unless explicit channel semantics are added",
        ],
        "public_claim_level": "experimental",
    }
    receipt_path = ROOT / "artifacts" / "typed_channel_calibrator_structural_features_receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def _path_repair_activates(channel: str, features: dict[str, Any], allow_distractors: bool) -> bool:
    if not allow_distractors and float(features["distractor_ratio"]) > 0.0:
        return False
    if features["query_relation"] != "all":
        return False
    if not bool(features["path_all_subset_chain_valid"]):
        return False
    if not bool(features["candidate_requires_transitive_closure"]):
        return False
    if bool(features["candidate_requires_quantifier_upgrade"]) or bool(features["contradiction_blocks_answer"]):
        return False
    return channel in {
        "logic_transitivity",
        "identity_preservation",
        "surface_structure",
        "confidence_abstention",
    }


def _quantifier_repair_activates(channel: str, features: dict[str, Any]) -> bool:
    if not bool(features["candidate_requires_quantifier_upgrade"]):
        return False
    return channel in {"quantifier_scope", "confidence_abstention"}


def _contradiction_repair_activates(channel: str, features: dict[str, Any]) -> bool:
    if not bool(features["contradiction_blocks_answer"]):
        return False
    return channel in {"contradiction", "confidence_abstention"}


def _case_type_accuracy(results: list[dict[str, Any]], task_type: str) -> float:
    subset = [result for result in results if result["task_type"] == task_type]
    if not subset:
        return 0.0
    return sum(
        result["answer_ok"] and all(row["activation_ok"] for row in result["channel_rows"])
        for result in subset
    ) / len(subset)


def _miss_count(results: list[dict[str, Any]], task_type: str, channel: str) -> int:
    count = 0
    for result in results:
        if result["task_type"] != task_type:
            continue
        row = next(item for item in result["channel_rows"] if item["channel"] == channel)
        if not row["predicted_active"]:
            count += 1
    return count


def _feature_snapshot(features: dict[str, Any]) -> dict[str, Any]:
    names = (
        "query_subject",
        "query_object",
        "query_relation",
        "shortest_path_exists",
        "shortest_path_length",
        "num_paths_between_query_nodes",
        "has_direct_edge",
        "has_inferred_edge",
        "has_reverse_edge",
        "reverse_path_exists",
        "query_relevant_edge_count",
        "distractor_edge_count",
        "distractor_ratio",
        "path_quantifier_signature",
        "path_contains_some",
        "path_contains_no",
        "path_all_subset_chain_valid",
        "contradiction_on_query_path",
        "contradiction_off_query_path",
        "contradiction_blocks_answer",
        "identity_evidence_exists",
        "identity_claim_without_evidence",
        "candidate_requires_transitive_closure",
        "candidate_requires_reverse_inference",
        "candidate_requires_identity_collapse",
        "candidate_requires_quantifier_upgrade",
    )
    return {name: features[name] for name in names}


if __name__ == "__main__":
    raise SystemExit(main())
