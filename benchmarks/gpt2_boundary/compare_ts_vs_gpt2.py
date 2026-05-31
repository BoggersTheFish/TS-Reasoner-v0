from __future__ import annotations

from typing import Any, Iterable

from benchmarks.gpt2_boundary.score_gpt2_outputs import score_gpt2_outputs


def score_ts_outputs(ts_rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(ts_rows)
    scored = []
    for row in rows:
        task = row["task"]
        result = row["ts_reasoner_result"]
        required_channel = str(task["required_channel"])
        expected_answer = str(task["expected_answer"])
        accepted = result["status"] == "accepted"
        rejected = result["status"] == "rejected"
        abstained = result["status"] == "abstained"
        support = result.get("support", {})
        answer_correct = (
            (expected_answer == "yes" and accepted)
            or (expected_answer == "no" and rejected)
            or (expected_answer == "unknown" and abstained)
        )
        claim_correct = str(result.get("claim", "")) == str(task["expected_claim"])
        support_path_correct = accepted and support.get("channel") == required_channel
        contradiction_rejected = required_channel == "contradiction_rejection" and rejected
        unsupported_abstained = required_channel == "unsupported_claim" and abstained
        wrong_accept = accepted and not support_path_correct
        scored.append({
            "case_id": row["case_id"],
            "answer_correct": answer_correct,
            "claim_correct": claim_correct,
            "support_path_correct": support_path_correct,
            "contradiction_rejected": contradiction_rejected,
            "unsupported_abstained": unsupported_abstained,
            "wrong_accept": wrong_accept,
            "accepted_without_typed_support": bool(row["accepted_without_typed_support"]),
            "candidate_graph_contamination_count": row["candidate_graph_contamination_count"],
        })

    task_count = len(scored)
    contradiction_cases = [row for row, arena_row in zip(scored, rows) if arena_row["task"]["required_channel"] == "contradiction_rejection"]
    unsupported_cases = [row for row, arena_row in zip(scored, rows) if arena_row["task"]["required_channel"] == "unsupported_claim"]
    support_cases = [
        row for row, arena_row in zip(scored, rows)
        if arena_row["task"]["required_channel"] in {"direct_support", "transitive_all", "negative_exclusion"}
    ]
    return {
        "task_count": task_count,
        "answer_accuracy": sum(row["answer_correct"] for row in scored) / task_count if task_count else 0.0,
        "claim_accuracy": sum(row["claim_correct"] for row in scored) / task_count if task_count else 0.0,
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
        "wrong_accept_count": sum(row["wrong_accept"] for row in scored),
        "accepted_without_typed_support_count": sum(row["accepted_without_typed_support"] for row in scored),
        "candidate_graph_contamination_count": sum(row["candidate_graph_contamination_count"] for row in scored),
        "results": scored,
    }


def compare_ts_vs_gpt2(tasks: list[dict[str, Any]], gpt2_outputs: list[dict[str, Any]], ts_outputs: list[dict[str, Any]]) -> dict[str, Any]:
    gpt2 = score_gpt2_outputs(tasks, gpt2_outputs)
    ts = score_ts_outputs(ts_outputs)
    report = {
        "release": "v11.0.0",
        "claim": "TS-Reasoner beats GPT-2-small on verifier-first controlled reasoning.",
        "task_count": len(tasks),
        "gpt2_small_answer_accuracy": gpt2["answer_accuracy"],
        "ts_reasoner_answer_accuracy": ts["answer_accuracy"],
        "gpt2_small_claim_accuracy": gpt2["claim_accuracy"],
        "ts_reasoner_claim_accuracy": ts["claim_accuracy"],
        "gpt2_small_support_path_accuracy": gpt2["support_path_accuracy"],
        "ts_reasoner_support_path_accuracy": ts["support_path_accuracy"],
        "gpt2_small_contradiction_rejection_rate": gpt2["contradiction_rejection_rate"],
        "ts_reasoner_contradiction_rejection_rate": ts["contradiction_rejection_rate"],
        "gpt2_small_unsupported_abstention_rate": gpt2["unsupported_abstention_rate"],
        "ts_reasoner_unsupported_abstention_rate": ts["unsupported_abstention_rate"],
        "ts_reasoner_wrong_accept_count": ts["wrong_accept_count"],
        "ts_reasoner_accepted_without_typed_support_count": ts["accepted_without_typed_support_count"],
        "ts_reasoner_candidate_graph_contamination_count": ts["candidate_graph_contamination_count"],
        "gpt2_wrong_accept_count": gpt2["wrong_accept_count"],
        "ts_reasoner_beats_gpt2_small_on_answer_accuracy": ts["answer_accuracy"] > gpt2["answer_accuracy"],
        "ts_reasoner_beats_gpt2_small_on_claim_accuracy": ts["claim_accuracy"] > gpt2["claim_accuracy"],
        "ts_reasoner_beats_gpt2_small_on_support_path_accuracy": ts["support_path_accuracy"] > gpt2["support_path_accuracy"],
        "ts_reasoner_beats_gpt2_small_on_contradiction_rejection": ts["contradiction_rejection_rate"] > gpt2["contradiction_rejection_rate"],
        "ts_reasoner_beats_gpt2_small_on_unsupported_abstention": ts["unsupported_abstention_rate"] > gpt2["unsupported_abstention_rate"],
    }
    report["all_gates_passed"] = (
        report["task_count"] == 100
        and report["ts_reasoner_beats_gpt2_small_on_answer_accuracy"]
        and report["ts_reasoner_beats_gpt2_small_on_claim_accuracy"]
        and report["ts_reasoner_beats_gpt2_small_on_support_path_accuracy"]
        and report["ts_reasoner_beats_gpt2_small_on_contradiction_rejection"]
        and report["ts_reasoner_beats_gpt2_small_on_unsupported_abstention"]
        and report["ts_reasoner_wrong_accept_count"] == 0
        and report["ts_reasoner_accepted_without_typed_support_count"] == 0
        and report["ts_reasoner_candidate_graph_contamination_count"] == 0
    )
    return report
