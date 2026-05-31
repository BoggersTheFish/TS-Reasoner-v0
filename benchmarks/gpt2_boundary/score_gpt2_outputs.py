from __future__ import annotations

from typing import Any, Iterable

from benchmarks.gpt2_boundary.gpt2_output_parser import parse_gpt2_output
from ts_reasoner.runtime_kernel import normalize_claim


def score_parsed_output(task: dict[str, Any], parsed: dict[str, Any]) -> dict[str, Any]:
    expected_answer = str(task["expected_answer"])
    expected_claim = normalize_claim(str(task["expected_claim"]))
    required_channel = str(task["required_channel"])
    expected_accept = expected_answer == "yes" and required_channel not in {
        "reverse_inference_block",
        "unsupported_claim",
        "contradiction_rejection",
    }
    status = str(parsed.get("status", "")).lower()
    support = str(parsed.get("support", "")).lower()
    answer_correct = parsed.get("answer") == expected_answer
    claim_correct = normalize_claim(str(parsed.get("claim", ""))) == expected_claim
    support_path_correct = (
        answer_correct
        and claim_correct
        and expected_accept
        and required_channel in support
        and "typed_verifier_trace" in support
    )
    contradiction_rejected = required_channel == "contradiction_rejection" and status in {"rejected", "abstained"}
    unsupported_abstained = required_channel == "unsupported_claim" and status == "abstained"
    wrong_accept = status == "accepted" and not (answer_correct and claim_correct and support_path_correct)
    return {
        "answer_correct": answer_correct,
        "claim_correct": claim_correct,
        "support_path_correct": support_path_correct,
        "contradiction_rejected": contradiction_rejected,
        "unsupported_abstained": unsupported_abstained,
        "wrong_accept": wrong_accept,
    }


def score_gpt2_outputs(tasks: Iterable[dict[str, Any]], outputs: Iterable[dict[str, Any]]) -> dict[str, Any]:
    task_list = list(tasks)
    output_by_case = {row["case_id"]: row for row in outputs}
    rows = []
    for task in task_list:
        output = output_by_case[str(task["case_id"])]
        parsed = output.get("parsed") or parse_gpt2_output(str(output.get("raw_output", "")))
        score = score_parsed_output(task, parsed)
        rows.append({"case_id": task["case_id"], "parsed": parsed, **score})

    task_count = len(rows)
    contradiction_cases = [row for row, task in zip(rows, task_list) if task["required_channel"] == "contradiction_rejection"]
    unsupported_cases = [row for row, task in zip(rows, task_list) if task["required_channel"] == "unsupported_claim"]
    support_cases = [
        row for row, task in zip(rows, task_list)
        if task["required_channel"] in {"direct_support", "transitive_all", "negative_exclusion"}
    ]
    return {
        "model": "gpt2-small",
        "task_count": task_count,
        "answer_accuracy": sum(row["answer_correct"] for row in rows) / task_count if task_count else 0.0,
        "claim_accuracy": sum(row["claim_correct"] for row in rows) / task_count if task_count else 0.0,
        "support_path_accuracy": (
            sum(row["support_path_correct"] for row in support_cases) / len(support_cases)
            if support_cases else 1.0
        ),
        "contradiction_rejection_rate": (
            sum(row["contradiction_rejected"] for row in contradiction_cases) / len(contradiction_cases)
            if contradiction_cases else 1.0
        ),
        "unsupported_abstention_rate": (
            sum(row["unsupported_abstained"] for row in unsupported_cases) / len(unsupported_cases)
            if unsupported_cases else 1.0
        ),
        "wrong_accept_count": sum(row["wrong_accept"] for row in rows),
        "format_parse_rate": sum(bool(row["parsed"].get("format_parse_ok")) for row in rows) / task_count if task_count else 0.0,
        "baseline_frozen": True,
        "results": rows,
    }
