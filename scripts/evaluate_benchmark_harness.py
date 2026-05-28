#!/usr/bin/env python3
"""Evaluate the v2.5 reusable benchmark harness."""

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

from ts_reasoner.benchmark_harness import load_benchmark_cases, run_benchmark_cases


DEFAULT_BENCHMARKS = [
    "data/benchmarks/syllogism_train.jsonl",
    "data/benchmarks/syllogism_dev.jsonl",
    "data/benchmarks/syllogism_test.jsonl",
    "data/benchmarks/rule_deduction_train.jsonl",
    "data/benchmarks/rule_deduction_dev.jsonl",
    "data/benchmarks/rule_deduction_test.jsonl",
    "data/benchmarks/adversarial_invalid_test.jsonl",
]


def git_value(args: list[str], default: str = "unknown") -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return default


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate(paths: list[str]) -> dict[str, Any]:
    resolved = [ROOT / path for path in paths]
    cases = load_benchmark_cases(resolved)
    report = run_benchmark_cases(cases)
    report.update(
        {
            "version": "v2.5.0-benchmark-harness",
            "claim": (
                "A reusable train/dev/test benchmark harness evaluates TS-Reasoner across "
                "syllogism, rule-deduction, and adversarial-invalid reasoning surfaces."
            ),
            "scope": (
                "Bounded natural-language and canonical relation-shaped reasoning prompts; "
                "not broad NLP, not live TensionLM, and not neural training."
            ),
            "benchmark_files": paths,
        }
    )
    return report


def build_receipt(report: dict[str, Any], benchmark_paths: list[Path], report_path: Path) -> dict[str, Any]:
    metrics = report["metrics"]
    return {
        "project": "TS-Reasoner-v0",
        "version": "v2.5.0-benchmark-harness",
        "commit": git_value(["rev-parse", "--short", "HEAD"]),
        "date": datetime.now(timezone.utc).isoformat(),
        "claim": report["claim"],
        "scope": report["scope"],
        "commands_run": [
            "python3 scripts/evaluate_benchmark_harness.py",
            "python3 -m unittest discover -q",
        ],
        "benchmarks": metrics,
        "splits": report["splits"],
        "categories": report["categories"],
        "artifacts": [
            {"path": str(report_path.relative_to(ROOT)), "sha256": sha256(report_path)},
            *[
                {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
                for path in benchmark_paths
            ],
        ],
        "boundary": {
            "benchmark_role": "reusable train/dev/test evaluation surface",
            "parser_role": "bounded natural-language to candidate graph claim",
            "verifier_role": "typed channels decide accept/reject/abstain",
            "candidate_graph_contamination_count": metrics["candidate_graph_contamination_count"],
            "accepted_without_typed_support_count": metrics["accepted_without_typed_support_count"],
        },
        "known_limitations": [
            "Benchmark is still bounded and synthetic.",
            "It is a reusable harness, not an external benchmark victory claim.",
            "No TensionLM runtime is loaded.",
            "No neural training is performed.",
            "Natural-language coverage remains deliberately narrow.",
        ],
        "public_claim_level": "experimental",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmarks", nargs="*", default=DEFAULT_BENCHMARKS)
    parser.add_argument("--report", default="artifacts/benchmark_harness_report.json")
    parser.add_argument("--receipt", default="artifacts/benchmark_harness_receipt.json")
    args = parser.parse_args()

    report_path = ROOT / args.report
    receipt_path = ROOT / args.receipt
    benchmark_paths = [ROOT / path for path in args.benchmarks]

    report = evaluate(args.benchmarks)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt_path.write_text(
        json.dumps(build_receipt(report, benchmark_paths, report_path), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report["metrics"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
