#!/usr/bin/env python3
"""Build the v3 unified verifier-guided candidate dataset.

v3 combines:
- v2.7 verifier trace training rows
- v2.9 active-learning challenge rows
- v2.9 active-learning augmented training rows

Boundary: these rows are supervised training examples derived from verifier
traces. They are not proof. Typed verifier channels remain proof authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_row(row: dict[str, Any], source: str, idx: int) -> dict[str, Any]:
    target = row["training_target"]
    verifier = row.get("verifier", {})
    model_features = row.get("model_features", {})

    return {
        "v3_schema_version": "v3.0.0-dataset",
        "v3_row_id": f"{source}:{idx:05d}:{row.get('case_id', 'unknown')}",
        "source_dataset": source,
        "source_release": row.get("source_release", "unknown"),
        "case_id": row.get("case_id"),
        "split": row.get("split"),
        "tags": row.get("tags", []),
        "input_claim": row.get("input_claim"),
        "candidate_id": row.get("candidate_id"),
        "candidate_confidence": row.get("candidate_confidence"),
        "candidate_source": row.get("candidate_source"),
        "features": model_features,
        "model_prediction": row.get("model_prediction", {}),
        "verifier": {
            "status": verifier.get("status"),
            "reason": verifier.get("reason"),
            "channels": verifier.get("channels", {}),
            "channel_names": verifier.get("channel_names", []),
            "typed_runtime_available": verifier.get("typed_runtime_available"),
            "typed_runtime_settled": verifier.get("typed_runtime_settled"),
            "global_tension": verifier.get("global_tension"),
            "context": verifier.get("context", {}),
        },
        "target": {
            "status": target["target_status"],
            "proposal_quality": target.get("proposal_quality"),
            "channels": target.get("target_channels", []),
            "should_accept": target.get("should_accept", False),
            "should_reject": target.get("should_reject", False),
            "should_abstain": target.get("should_abstain", False),
            "failure_reason": target.get("failure_reason"),
            "is_supported": target.get("is_supported", False),
            "is_reverse_error": target.get("is_reverse_error", False),
            "is_identity_error": target.get("is_identity_error", False),
            "is_quantifier_error": target.get("is_quantifier_error", False),
            "is_contradiction_error": target.get("is_contradiction_error", False),
            "is_malformed_error": target.get("is_malformed_error", False),
            "is_unsupported": target.get("is_unsupported", False),
        },
        "boundary": {
            "model_role": "predict/rank candidate status and channels",
            "verifier_role": "typed verifier remains proof authority",
            "proof_role": "dataset row is training signal, not proof",
            "confidence_role": "metadata/baseline only",
        },
    }


def dedupe_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # Deduplicate the same candidate row across source datasets. For v3, repeated
    # challenge rows should not silently become weighting unless a future release
    # explicitly introduces sample weights.
    seen: set[tuple[str | None, str | None]] = set()
    out: list[dict[str, Any]] = []
    for row in rows:
        key = (
            row.get("case_id"),
            row.get("candidate_id"),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def summarize(
    rows: list[dict[str, Any]],
    input_paths: list[Path],
    output_path: Path,
    raw_source_counts: dict[str, int],
    raw_row_count: int,
) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    source_counts: dict[str, int] = {}
    channel_counts: dict[str, int] = {}
    split_counts: dict[str, int] = {}

    for row in rows:
        status = row["target"]["status"]
        source = row["source_dataset"]
        split = row.get("split") or "unknown"

        status_counts[status] = status_counts.get(status, 0) + 1
        source_counts[source] = source_counts.get(source, 0) + 1
        split_counts[split] = split_counts.get(split, 0) + 1

        for channel in row["target"].get("channels", []):
            channel_counts[channel] = channel_counts.get(channel, 0) + 1

    return {
        "version": "v3.0.0-dataset",
        "row_count": len(rows),
        "raw_row_count": raw_row_count,
        "duplicate_removed_count": raw_row_count - len(rows),
        "status_counts": dict(sorted(status_counts.items())),
        "source_counts": dict(sorted(source_counts.items())),
        "raw_source_counts": dict(sorted(raw_source_counts.items())),
        "split_counts": dict(sorted(split_counts.items())),
        "channel_counts": dict(sorted(channel_counts.items())),
        "has_boundary": all(bool(row.get("boundary")) for row in rows),
        "has_features": all(bool(row.get("features")) for row in rows),
        "has_targets": all(bool(row.get("target")) for row in rows),
        "input_artifacts": [
            {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
            for path in input_paths
        ],
        "output_artifact": {
            "path": str(output_path.relative_to(ROOT)),
            "sha256": sha256(output_path),
        },
        "boundary": {
            "dataset_role": "unified supervised training signal",
            "model_role": "candidate prediction/ranking only",
            "verifier_role": "typed verifier remains proof authority",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verifier-traces", default="data/verifier_trace_training_data_v27.jsonl")
    parser.add_argument("--active-challenge", default="data/active_learning_challenge_v29.jsonl")
    parser.add_argument("--active-augmented", default="data/active_learning_augmented_training_v29.jsonl")
    parser.add_argument("--output", default="artifacts/v3/v3_training_dataset.jsonl")
    parser.add_argument("--summary", default="artifacts/v3/v3_dataset_summary.json")
    args = parser.parse_args()

    input_specs = [
        ("v27_verifier_trace", ROOT / args.verifier_traces),
        ("v29_active_challenge", ROOT / args.active_challenge),
        ("v29_active_augmented", ROOT / args.active_augmented),
    ]

    rows: list[dict[str, Any]] = []
    raw_source_counts: dict[str, int] = {}
    for source, path in input_specs:
        loaded = load_jsonl(path)
        raw_source_counts[source] = len(loaded)
        for idx, row in enumerate(loaded):
            rows.append(canonical_row(row, source, idx))

    raw_row_count = len(rows)
    rows = dedupe_rows(rows)

    output_path = ROOT / args.output
    summary_path = ROOT / args.summary

    write_jsonl(output_path, rows)
    summary = summarize(rows, [path for _, path in input_specs], output_path, raw_source_counts, raw_row_count)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
