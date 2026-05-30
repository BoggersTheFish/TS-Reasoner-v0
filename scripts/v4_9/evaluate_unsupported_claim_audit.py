#!/usr/bin/env python3
"""Evaluate v4.9 unsupported-claim audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.claim_audit import evaluate_claim_audit_cases, load_jsonl


DATA = ROOT / "data/v4_9/unsupported_claim_audit_cases.jsonl"
REPORT = ROOT / "artifacts/v4_9_unsupported_claim_audit_report.json"


def main() -> int:
    cases = load_jsonl(DATA)
    report = evaluate_claim_audit_cases(cases)

    if not report["gates"]["all_gates_passed"]:
        print(json.dumps(report["gates"], indent=2, sort_keys=True))
        return 1

    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    headline = {
        "version": report["version"],
        "case_count": report["case_count"],
        "candidate_count": report["candidate_count"],
        "unsupported_claim_candidate_count": report["unsupported_claim_candidate_count"],
        "arena_selection_accuracy": report["arena_selection_accuracy"],
        "confidence_top_accuracy": report["confidence_top_accuracy"],
        "wrong_accept_count": report["wrong_accept_count"],
        "accepted_without_typed_support_count": report["accepted_without_typed_support_count"],
        "accepted_with_unsupported_claims_count": report["accepted_with_unsupported_claims_count"],
        "candidate_graph_contamination_count": report["candidate_graph_contamination_count"],
        "all_gates_passed": report["gates"]["all_gates_passed"],
        "output": str(REPORT.relative_to(ROOT)),
    }
    print(json.dumps(headline, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
