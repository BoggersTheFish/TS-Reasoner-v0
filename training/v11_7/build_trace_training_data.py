from __future__ import annotations

import hashlib
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from benchmarks.gpt2_boundary.adversarial_fuzzer import FuzzerConfig, generate_adversarial_cases
from benchmarks.gpt2_boundary.procedural_curriculum import CurriculumConfig, generate_curriculum
from ts_reasoner.paragraph_decomposer import decompose_paragraph
from ts_reasoner.support_path_verifier import verify_support_path


@dataclass(frozen=True)
class TraceDatasetConfig:
    seed: int = 117
    procedural_task_count: int = 5000
    adversarial_case_count: int = 3000
    target_row_count: int = 8000
    train_ratio: float = 0.8
    valid_ratio: float = 0.1
    test_ratio: float = 0.1


def _sha(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _answer_for_status(status: str) -> str:
    if status == "accepted":
        return "yes"
    if status == "rejected":
        return "no"
    return "abstain"


def _verifier_label(premises: list[str], claim: str) -> dict[str, Any]:
    result = verify_support_path(premises, claim)

    support = result.get("support", {})
    channel_or_reason = support.get("channel") if support else result.get("reason", "")

    return {
        "status": result["status"],
        "answer": _answer_for_status(result["status"]),
        "claim": claim,
        "support_channel": channel_or_reason,
        "support_premises": support.get("premises", []),
        "trace_hash": support.get("trace_hash", ""),
        "verifier_passed": bool(support.get("verifier_passed", False)) if result["status"] == "accepted" else False,
        "raw_result": result,
    }


def _make_input(prompt: str, premises: list[str], claim: str) -> str:
    return (
        "Reason over the premises. Answer yes, no, or abstain, and provide the verifier claim.\n"
        f"Prompt: {prompt}\n"
        f"Premises: {json.dumps(premises, sort_keys=True)}\n"
        f"Candidate claim: {claim}"
    )


def _row_from_task(task: dict[str, Any], source: str) -> dict[str, Any] | None:
    premises = list(task.get("premises", []))
    claim = str(task.get("expected_claim", ""))

    if not claim:
        return None

    label = _verifier_label(premises, claim)
    prompt = str(task.get("prompt", ""))

    return {
        "row_id": "",
        "source": source,
        "source_case_id": task.get("case_id", ""),
        "input": _make_input(prompt, premises, claim),
        "prompt": prompt,
        "premises": premises,
        "target": {
            "answer": label["answer"],
            "status": label["status"],
            "claim": label["claim"],
            "support_channel": label["support_channel"],
            "support_premises": label["support_premises"],
            "trace_hash": label["trace_hash"],
            "verifier_passed": label["verifier_passed"],
        },
        "verifier_result": label["raw_result"],
    }


def _row_from_paragraph_case(task: dict[str, Any], source: str) -> dict[str, Any] | None:
    prompt = str(task.get("prompt", ""))
    decomposed = decompose_paragraph(prompt)

    if decomposed["status"] != "parsed" or not decomposed["candidate_claim"]:
        return None

    premises = list(decomposed["premises"])
    claim = str(decomposed["candidate_claim"])
    label = _verifier_label(premises, claim)

    return {
        "row_id": "",
        "source": source,
        "source_case_id": task.get("case_id", ""),
        "input": _make_input(prompt, premises, claim),
        "prompt": prompt,
        "premises": premises,
        "target": {
            "answer": label["answer"],
            "status": label["status"],
            "claim": label["claim"],
            "support_channel": label["support_channel"],
            "support_premises": label["support_premises"],
            "trace_hash": label["trace_hash"],
            "verifier_passed": label["verifier_passed"],
        },
        "verifier_result": label["raw_result"],
        "decomposition": decomposed,
    }


def build_trace_rows(config: TraceDatasetConfig | None = None) -> list[dict[str, Any]]:
    config = config or TraceDatasetConfig()

    procedural = generate_curriculum(
        CurriculumConfig(
            seed=config.seed,
            task_count=config.procedural_task_count,
            entity_count=900,
            distractor_count=1,
        )
    )
    adversarial = generate_adversarial_cases(
        FuzzerConfig(
            seed=config.seed + 1,
            source_task_count=max(240, min(config.procedural_task_count, 2000)),
            fuzzed_case_count=config.adversarial_case_count,
            entity_count=900,
        )
    )

    rows: list[dict[str, Any]] = []

    for task in procedural:
        row = _row_from_task(task, "procedural_curriculum")
        if row is not None:
            rows.append(row)

        if str(task.get("family", "")).startswith("paragraph_"):
            paragraph_row = _row_from_paragraph_case(task, "paragraph_decomposition")
            if paragraph_row is not None:
                rows.append(paragraph_row)

    for task in adversarial:
        row = _row_from_task(task, "adversarial_fuzzer")
        if row is not None:
            rows.append(row)

    # Deterministic dedupe by actual training input + target.
    deduped: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = _sha({"input": row["input"], "target": row["target"]})
        deduped.setdefault(key, row)

    rows = list(deduped.values())
    rng = random.Random(config.seed)
    rng.shuffle(rows)

    rows = rows[: config.target_row_count]

    for index, row in enumerate(rows):
        row["row_id"] = f"trace_{index:06d}_{_sha(row)[:12]}"

    return rows


def split_rows(rows: list[dict[str, Any]], config: TraceDatasetConfig | None = None) -> dict[str, list[dict[str, Any]]]:
    config = config or TraceDatasetConfig()
    total = len(rows)
    train_end = int(total * config.train_ratio)
    valid_end = train_end + int(total * config.valid_ratio)

    return {
        "train": rows[:train_end],
        "valid": rows[train_end:valid_end],
        "test": rows[valid_end:],
    }


def replay_row(row: dict[str, Any]) -> bool:
    result = verify_support_path(list(row["premises"]), str(row["target"]["claim"]))
    expected = row["target"]
    channel_or_reason = result.get("support", {}).get("channel") if result.get("support") else result.get("reason", "")

    return (
        result["status"] == expected["status"]
        and _answer_for_status(result["status"]) == expected["answer"]
        and channel_or_reason == expected["support_channel"]
    )


def summarize_dataset(splits: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    all_rows = [row for split in splits.values() for row in split]
    replay_ok = sum(1 for row in all_rows if replay_row(row))

    status_counts: dict[str, int] = {}
    channel_counts: dict[str, int] = {}
    source_counts: dict[str, int] = {}

    accepted_without_typed_support = 0
    for row in all_rows:
        status = row["target"]["status"]
        channel = row["target"]["support_channel"]
        source = row["source"]

        status_counts[status] = status_counts.get(status, 0) + 1
        channel_counts[channel] = channel_counts.get(channel, 0) + 1
        source_counts[source] = source_counts.get(source, 0) + 1

        if status == "accepted" and not row["target"]["trace_hash"]:
            accepted_without_typed_support += 1

    split_counts = {name: len(rows) for name, rows in splits.items()}

    train_ids = {row["row_id"] for row in splits["train"]}
    valid_ids = {row["row_id"] for row in splits["valid"]}
    test_ids = {row["row_id"] for row in splits["test"]}

    leakage_check_passed = not (
        train_ids & valid_ids or train_ids & test_ids or valid_ids & test_ids
    )

    row_count = len(all_rows)
    dataset_hash = _sha(all_rows)

    summary = {
        "release": "v11.7.0",
        "row_count": row_count,
        "split_counts": split_counts,
        "status_counts": status_counts,
        "channel_counts": channel_counts,
        "source_counts": source_counts,
        "label_verifier_replay_rate": replay_ok / row_count if row_count else 0.0,
        "trace_hash_validity": (
            sum(1 for row in all_rows if row["target"]["status"] != "accepted" or bool(row["target"]["trace_hash"])) / row_count
            if row_count else 0.0
        ),
        "accepted_without_typed_support_count": accepted_without_typed_support,
        "class_balance_valid": all(status_counts.get(status, 0) > 0 for status in ["accepted", "rejected", "abstained"]),
        "leakage_check_passed": leakage_check_passed,
        "dataset_hash": dataset_hash,
    }

    summary["all_gates_passed"] = (
        row_count > 0
        and summary["label_verifier_replay_rate"] == 1.0
        and summary["trace_hash_validity"] == 1.0
        and accepted_without_typed_support == 0
        and summary["class_balance_valid"]
        and leakage_check_passed
        and split_counts["train"] > 0
        and split_counts["valid"] > 0
        and split_counts["test"] > 0
    )

    return summary


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )
