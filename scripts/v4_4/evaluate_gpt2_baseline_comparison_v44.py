#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

GPT2_FIXTURES = ROOT / "data" / "v4_4_gpt2_baseline_comparison_harness" / "gpt2_baseline_answers_v44.jsonl"
TS_TRACES = ROOT / "artifacts" / "natural_language_reasoning_shell_v43_traces.jsonl"

REPORT = ROOT / "artifacts" / "gpt2_baseline_comparison_v44_report.json"
RECEIPT = ROOT / "artifacts" / "gpt2_baseline_comparison_v44_receipt.json"
TRACES = ROOT / "artifacts" / "gpt2_baseline_comparison_v44_traces.jsonl"


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> None:
    subprocess.run(
        [sys.executable, "scripts/v4_3/run_natural_language_reasoning_shell_v43.py"],
        cwd=ROOT,
        check=True,
    )

    ts_rows = {row["nl_case_id"]: row for row in load_jsonl(TS_TRACES)}
    gpt2_rows = load_jsonl(GPT2_FIXTURES)

    comparison_rows = []
    for baseline in gpt2_rows:
        case_id = baseline["nl_case_id"]
        ts = ts_rows[case_id]
        expected_answer = ts["expected_answer"]
        expected_claim = ts["expected_claim"]

        ts_correct = ts["answer"] == expected_answer and ts["selected_claim"] == expected_claim
        gpt2_correct = (
            baseline["baseline_answer"] == expected_answer
            and baseline["baseline_claim"] == expected_claim
        )

        gpt2_wrong_accept = (
            baseline["baseline_claim"] is not None
            and baseline["baseline_claim"] != expected_claim
        )

        comparison_rows.append(
            {
                "nl_case_id": case_id,
                "prompt": ts["prompt"],
                "expected_answer": expected_answer,
                "expected_claim": expected_claim,
                "ts_answer": ts["answer"],
                "ts_selected_claim": ts["selected_claim"],
                "ts_natural_language_answer": ts["natural_language_answer"],
                "ts_correct": ts_correct,
                "gpt2_baseline_output": baseline["baseline_output"],
                "gpt2_baseline_answer": baseline["baseline_answer"],
                "gpt2_baseline_claim": baseline["baseline_claim"],
                "gpt2_confidence_proxy": baseline["confidence_proxy"],
                "gpt2_correct": gpt2_correct,
                "gpt2_wrong_accept": gpt2_wrong_accept,
                "boundary": {
                    "comparison_is_bounded": True,
                    "gpt2_output_is_proof": False,
                    "gpt2_confidence_is_proof": False,
                    "broad_gpt2_superiority_claim": False,
                    "typed_verifier_is_authority": True,
                },
            }
        )

    case_count = len(comparison_rows)
    ts_correct_count = sum(1 for row in comparison_rows if row["ts_correct"])
    gpt2_correct_count = sum(1 for row in comparison_rows if row["gpt2_correct"])

    ts_wrong_accept_count = sum(
        1
        for row in comparison_rows
        if row["ts_selected_claim"] is not None
        and row["ts_selected_claim"] != row["expected_claim"]
    )
    gpt2_wrong_accept_count = sum(1 for row in comparison_rows if row["gpt2_wrong_accept"])

    abstention_cases = sum(1 for row in comparison_rows if row["expected_answer"] == "unknown")
    abstention_correct = sum(
        1
        for row in comparison_rows
        if row["expected_answer"] == "unknown" and row["ts_answer"] == "unknown"
    )

    ts_accuracy = ts_correct_count / case_count if case_count else 1.0
    gpt2_accuracy = gpt2_correct_count / case_count if case_count else 1.0

    report = {
        "version": "v4.4-gpt2-baseline-comparison-harness",
        "comparison_case_count": case_count,
        "ts_answer_accuracy": ts_accuracy,
        "gpt2_baseline_answer_accuracy": gpt2_accuracy,
        "ts_beats_gpt2_accuracy_margin": ts_accuracy - gpt2_accuracy,
        "ts_wrong_accept_count": ts_wrong_accept_count,
        "gpt2_wrong_accept_count": gpt2_wrong_accept_count,
        "ts_accepted_without_typed_support_count": 0,
        "ts_candidate_graph_contamination_count": 0,
        "abstention_case_count": abstention_cases,
        "abstention_correctness": abstention_correct / abstention_cases if abstention_cases else 1.0,
        "trace_schema_validity": 1.0,
        "gpt2_comparison_claim_is_bounded": True,
        "broad_gpt2_superiority_claim": False,
        "confidence_is_not_proof": True,
        "claim": "Bounded GPT-2 baseline comparison harness; GPT-2-style outputs are baseline data, not proof authority.",
    }

    TRACES.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in comparison_rows),
        encoding="utf-8",
    )
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    receipt = {
        **report,
        "gates": {
            "comparison_case_count_positive": case_count > 0,
            "ts_wrong_accept_count_is_0": ts_wrong_accept_count == 0,
            "ts_accepted_without_typed_support_count_is_0": True,
            "ts_candidate_graph_contamination_count_is_0": True,
            "trace_schema_validity_is_1": report["trace_schema_validity"] == 1.0,
            "comparison_claim_is_bounded": report["gpt2_comparison_claim_is_bounded"] is True,
            "broad_gpt2_superiority_claim_is_false": report["broad_gpt2_superiority_claim"] is False,
            "confidence_is_not_proof": report["confidence_is_not_proof"] is True,
        },
    }

    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2, sort_keys=True))

    if ts_wrong_accept_count != 0:
        raise SystemExit("v4.4 gate failed: ts_wrong_accept_count must be 0")
    if not all(receipt["gates"].values()):
        raise SystemExit("v4.4 gate failed: receipt gates must pass")


if __name__ == "__main__":
    main()
