#!/usr/bin/env python3
"""Evaluate v2.4 bounded natural-language claim ingestion."""

from __future__ import annotations

import argparse
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

from ts_reasoner.nl_claim_parser import run_natural_language_claim_ingestion


def git_value(args: list[str], default: str = "unknown") -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return default


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_cases(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def evaluate_cases(data_path: str | Path) -> dict[str, Any]:
    path = Path(data_path)
    cases = load_cases(path)
    results = []
    parse_matches = 0
    status_matches = 0
    claim_matches = 0
    malformed_total = 0
    malformed_safe_abstain = 0
    trace_valid = 0
    contamination = 0
    accepted_without_typed_support = 0

    for row in cases:
        case_id = row["case_id"]
        result = run_natural_language_claim_ingestion(row["input_text"], case_id=case_id)
        parser = result["parser"]
        verification = result["verification"]
        candidate_results = verification.get("candidate_results", [])
        actual_status = result["status"]
        actual_claim = parser.get("candidate_claim")
        expected_claim = row.get("expected_claim")

        parse_match = parser["parse_success"] == row["expected_parse_success"]
        status_match = actual_status == row["expected_status"]
        claim_match = actual_claim == expected_claim

        parse_matches += int(parse_match)
        status_matches += int(status_match)
        claim_matches += int(claim_match)

        if not row["expected_parse_success"]:
            malformed_total += 1
            malformed_safe_abstain += int(actual_status == "abstained" and not candidate_results)

        trace_valid += int(_trace_schema_valid(result))

        for candidate_result in candidate_results:
            runtime = candidate_result.get("typed_runtime", {})
            channel_trace = candidate_result.get("channel_trace", {})
            if candidate_result["status"] == "accepted" and not _has_typed_support(runtime, channel_trace):
                accepted_without_typed_support += 1
            provenance = candidate_result.get("provenance", {})
            if provenance.get("source") != "natural_language_claim_parser":
                contamination += 1

        results.append(
            {
                "case_id": case_id,
                "expected_parse_success": row["expected_parse_success"],
                "actual_parse_success": parser["parse_success"],
                "expected_status": row["expected_status"],
                "actual_status": actual_status,
                "expected_claim": expected_claim,
                "actual_claim": actual_claim,
                "parse_match": parse_match,
                "status_match": status_match,
                "claim_match": claim_match,
                "reason": result.get("reason"),
            }
        )

    case_count = len(cases)
    metrics = {
        "case_count": case_count,
        "parse_expectation_rate": parse_matches / case_count if case_count else 0.0,
        "status_expectation_rate": status_matches / case_count if case_count else 0.0,
        "claim_expectation_rate": claim_matches / case_count if case_count else 0.0,
        "malformed_input_safe_abstain_rate": malformed_safe_abstain / malformed_total if malformed_total else 1.0,
        "accepted_without_typed_support_count": accepted_without_typed_support,
        "candidate_graph_contamination_count": contamination,
        "trace_schema_validity": trace_valid / case_count if case_count else 0.0,
    }
    return {
        "version": "v2.4.0-natural-language-claim-ingestion",
        "claim": "Bounded natural-language reasoning prompts are parsed into candidate graph claims and verified by existing TS-Reasoner typed channels.",
        "scope": "Bounded syllogistic and relation-shaped natural language only; not general NLP or broad language understanding.",
        "case_count": case_count,
        "metrics": metrics,
        "results": results,
    }


def build_receipt(report: dict[str, Any], data_path: Path, report_path: Path) -> dict[str, Any]:
    metrics = report["metrics"]
    return {
        "project": "TS-Reasoner-v0",
        "version": "v2.4.0-natural-language-claim-ingestion",
        "commit": git_value(["rev-parse", "--short", "HEAD"]),
        "date": datetime.now(timezone.utc).isoformat(),
        "claim": (
            "v2.4 adds bounded natural-language claim ingestion: simple NL prompts are "
            "normalized into candidate graph claims, then verified by the existing typed "
            "candidate bridge."
        ),
        "scope": report["scope"],
        "commands_run": [
            "python3 scripts/evaluate_natural_language_claim_ingestion.py",
            "python3 -m unittest discover -q",
        ],
        "inputs": [str(data_path.relative_to(ROOT))],
        "benchmarks": metrics,
        "artifacts": [
            {"path": str(report_path.relative_to(ROOT)), "sha256": sha256(report_path)},
            {"path": str(data_path.relative_to(ROOT)), "sha256": sha256(data_path)},
        ],
        "boundary": {
            "parser_role": "extract bounded relation-shaped premises and candidate claim",
            "model_role": "none; no model loading or training in this release",
            "verifier_role": "typed TS-Reasoner channels decide accept/reject/abstain",
            "candidate_graph_contamination_count": metrics["candidate_graph_contamination_count"],
            "accepted_without_typed_support_count": metrics["accepted_without_typed_support_count"],
        },
        "known_limitations": [
            "Bounded parser only; no claim of general natural-language understanding.",
            "Single-token or underscore/hyphen concept names are the supported surface.",
            "The parser extracts candidate data only; proof authority remains with typed channels.",
            "No TensionLM runtime is loaded.",
            "No neural training is performed.",
        ],
        "public_claim_level": "experimental",
    }


def _trace_schema_valid(result: dict[str, Any]) -> bool:
    if "parser" not in result or "verification" not in result or "trace_receipt" not in result:
        return False
    receipt = result["trace_receipt"]
    return all(
        key in receipt
        for key in ["candidate_count", "accepted_count", "rejected_count", "abstained_count", "provenance_preserved"]
    )


def _has_typed_support(runtime: dict[str, Any], channel_trace: dict[str, Any]) -> bool:
    if not runtime.get("available"):
        return False
    if not channel_trace:
        return False
    transitivity = channel_trace.get("logic_transitivity", {})
    if transitivity.get("status") in {"relaxed", "settled"}:
        return True
    return bool(runtime.get("settled"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/natural_language_claim_cases.jsonl")
    parser.add_argument("--report", default="artifacts/natural_language_claim_ingestion_report.json")
    parser.add_argument("--receipt", default="artifacts/natural_language_claim_ingestion_receipt.json")
    args = parser.parse_args()

    data_path = ROOT / args.data
    report_path = ROOT / args.report
    receipt_path = ROOT / args.receipt

    report = evaluate_cases(data_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt_path.write_text(
        json.dumps(build_receipt(report, data_path, report_path), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report["metrics"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
