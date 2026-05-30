#!/usr/bin/env python3
"""Evaluate the v4.7 verifier-first answer arena."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.answer_arena import evaluate_arena_cases, load_jsonl


DATA = ROOT / "data/v4_7/answer_arena_cases.jsonl"
REPORT = ROOT / "artifacts/v4_7_answer_arena_report.json"


def main() -> int:
    cases = load_jsonl(DATA)
    report = evaluate_arena_cases(cases)

    if not report["gates"]["all_gates_passed"]:
        print(json.dumps(report["gates"], indent=2, sort_keys=True))
        return 1

    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    headline = {
        "version": report["version"],
        "case_count": report["case_count"],
        "candidate_count": report["candidate_count"],
        "arena_selection_accuracy": report["arena_selection_accuracy"],
        "confidence_top_accuracy": report["confidence_top_accuracy"],
        "verifier_overrode_confidence_count": report["verifier_overrode_confidence_count"],
        "wrong_accept_count": report["wrong_accept_count"],
        "accepted_without_typed_support_count": report["accepted_without_typed_support_count"],
        "candidate_graph_contamination_count": report["candidate_graph_contamination_count"],
        "all_gates_passed": report["gates"]["all_gates_passed"],
        "output": str(REPORT.relative_to(ROOT)),
    }
    print(json.dumps(headline, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
