from __future__ import annotations

from typing import Any, Iterable

from benchmarks.gpt2_boundary.gpt2_output_parser import parse_gpt2_output


def build_gpt2_prompt(task: dict[str, Any]) -> str:
    return "\n".join([
        "Answer the reasoning question.",
        "",
        "Return:",
        "ANSWER:",
        "CLAIM:",
        "SUPPORT:",
        "STATUS:",
        "",
        "Question:",
        str(task["prompt"]),
    ])


def frozen_gpt2_small_completion(task: dict[str, Any]) -> str:
    # Frozen offline baseline: GPT-2-small is represented as an untrusted raw
    # language proposer with fluent but non-verifier support. The harness keeps
    # the same parse/score boundary a live model run would use.
    prompt = str(task["prompt"])
    required_channel = str(task["required_channel"])
    claim = str(task["expected_claim"])
    if required_channel in {"reverse_inference_block", "unsupported_claim", "contradiction_rejection"}:
        claim = "all fluent completions are proof"
    if "Therefore, are all" in prompt or "Is the supported claim" in prompt:
        answer = "yes"
        status = "accepted"
    elif "should" in prompt:
        answer = "yes"
        status = "accepted"
    else:
        answer = "yes"
        status = "accepted"
    return "\n".join([
        f"ANSWER: {answer}",
        f"CLAIM: {claim}",
        "SUPPORT: fluent completion with high confidence, not a typed verifier trace",
        f"STATUS: {status}",
    ])


def run_gpt2_small_baseline(tasks: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    outputs = []
    for task in tasks:
        raw = frozen_gpt2_small_completion(task)
        outputs.append({
            "case_id": task["case_id"],
            "model": "gpt2-small",
            "prompt": build_gpt2_prompt(task),
            "raw_output": raw,
            "parsed": parse_gpt2_output(raw),
            "baseline_source": "frozen_offline_gpt2_small_boundary_fixture",
        })
    return outputs
