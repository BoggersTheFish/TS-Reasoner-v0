#!/usr/bin/env python3
"""Build Candidate Model v2 data from the v2.5 benchmark harness."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.learned_model.dataset import candidate, label_case
from ts_reasoner.nl_claim_parser import parse_natural_language_claim


BENCHMARK_FILES = [
    "data/benchmarks/syllogism_train.jsonl",
    "data/benchmarks/syllogism_dev.jsonl",
    "data/benchmarks/syllogism_test.jsonl",
    "data/benchmarks/rule_deduction_train.jsonl",
    "data/benchmarks/rule_deduction_dev.jsonl",
    "data/benchmarks/rule_deduction_test.jsonl",
    "data/benchmarks/adversarial_invalid_test.jsonl",
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def build_case(row: dict[str, Any]) -> dict[str, Any]:
    parsed = parse_natural_language_claim(row["input_text"])
    candidates = []

    if parsed.candidate_claim is not None:
        candidates.append(candidate("candidate_expected_query", parsed.candidate_claim, 0.55))

    if row.get("expected_claim") and row["expected_claim"] != parsed.candidate_claim:
        candidates.append(candidate("candidate_expected_label", row["expected_claim"], 0.52))

    if parsed.candidate_claim:
        reverse = reverse_claim(parsed.candidate_claim)
        if reverse and reverse != parsed.candidate_claim:
            candidates.append(candidate("candidate_reverse_trap", reverse, 0.94))

        unsupported = unsupported_claim(parsed.candidate_claim)
        if unsupported and unsupported != parsed.candidate_claim:
            candidates.append(candidate("candidate_unsupported_trap", unsupported, 0.86))

        identity = identity_claim(parsed.candidate_claim)
        if identity:
            candidates.append(candidate("candidate_identity_trap", identity, 0.83))

    candidates.append(candidate("candidate_malformed_trap", "therefore probably yes", 0.78))

    # Deduplicate by claim while preserving order.
    seen_claims = set()
    unique_candidates = []
    for item in candidates:
        key = item["claim"].lower()
        if key in seen_claims:
            continue
        seen_claims.add(key)
        unique_candidates.append(item)

    built = {
        "split": split_for(row),
        "case_id": "v2_" + row["case_id"],
        "input_text": row["input_text"],
        "candidates": unique_candidates,
        "tags": [row["category"], row["split"], *extra_tags(row, parsed)],
    }
    return label_case(built)


def split_for(row: dict[str, Any]) -> str:
    if row["split"] == "train":
        return "train"
    if row["split"] == "dev":
        return "eval"
    return "stress"


def extra_tags(row: dict[str, Any], parsed: Any) -> list[str]:
    tags = []
    if row.get("invalid_case"):
        tags.append("invalid")
    if not parsed.parse_success:
        tags.append("malformed_input")
    if "All " in row["input_text"] and row["input_text"].count("All ") >= 2:
        tags.append("multi_premise")
    return tags


def reverse_claim(claim: str) -> str | None:
    parts = claim.split()
    if len(parts) >= 4 and parts[0].lower() in {"all", "some", "no"} and parts[2].lower() == "are":
        return f"{parts[0]} {parts[3]} are {parts[1]}"
    return None


def unsupported_claim(claim: str) -> str | None:
    parts = claim.split()
    if len(parts) >= 4 and parts[0].lower() in {"all", "some", "no"} and parts[2].lower() == "are":
        return f"{parts[0]} {parts[1]} are unsupported_target"
    return None


def identity_claim(claim: str) -> str | None:
    parts = claim.split()
    if len(parts) >= 4 and parts[0].lower() in {"all", "some", "no"} and parts[2].lower() == "are":
        return f"{parts[1]} equals {parts[3]}"
    return None


def main() -> None:
    rows = []
    for relative in BENCHMARK_FILES:
        rows.extend(load_jsonl(ROOT / relative))

    built = [build_case(row) for row in rows]

    train = [row for row in built if row["split"] == "train"]
    eval_rows = [row for row in built if row["split"] == "eval"]
    stress = [row for row in built if row["split"] == "stress"]

    write_jsonl(ROOT / "data/candidate_model_v2_train.jsonl", train)
    write_jsonl(ROOT / "data/candidate_model_v2_eval.jsonl", eval_rows)
    write_jsonl(ROOT / "data/candidate_model_v2_stress.jsonl", stress)

    summary = {
        "source": "v2.5 benchmark harness",
        "case_count": len(built),
        "train_cases": len(train),
        "eval_cases": len(eval_rows),
        "stress_cases": len(stress),
        "candidate_count": sum(len(row["candidates"]) for row in built),
        "labelled": all("labels" in row for row in built),
    }
    path = ROOT / "artifacts/candidate_model_v2_dataset_summary.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
