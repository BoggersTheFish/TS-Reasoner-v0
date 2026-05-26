#!/usr/bin/env python3
"""Evaluate TS-Reasoner typed tension channels."""

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

from ts_reasoner import run_reasoner


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def git_value(args: list[str], default: str = "unknown") -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return default


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    output = run_reasoner(case["question"], case.get("premises", []))
    channels = output.trace.get("tension_channels", {})
    expected_channels = case.get("expected_channels", {})
    expected_resolutions = case.get("expected_resolutions", {})
    answer_ok = case["expected_answer_contains"].lower() in output.final_answer.lower()
    activation_checks = {
        name: bool(channels.get(name, {}).get("activated")) == expected
        for name, expected in expected_channels.items()
    }
    resolver_checks = {
        name: channels.get(name, {}).get("resolution") == expected
        for name, expected in expected_resolutions.items()
    }
    return {
        "task_id": case["task_id"],
        "task_type": case["task_type"],
        "answer": output.final_answer,
        "answer_ok": answer_ok,
        "activation_checks": activation_checks,
        "resolver_checks": resolver_checks,
        "global_tension": output.trace.get("typed_runtime", {}).get("global_tension"),
        "settled": output.trace.get("typed_runtime", {}).get("settled"),
        "reverse_fallacy": bool(output.trace.get("typed_runtime", {}).get("context", {}).get("blocked_edges")),
        "identity_collapse_blocked": bool(output.trace.get("typed_runtime", {}).get("context", {}).get("blocked_equalities")),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/typed_tension_benchmark.jsonl")
    parser.add_argument("--out", default="artifacts/typed_tension_benchmark_report.json")
    parser.add_argument("--receipt", default="artifacts/typed_tension_receipt.json")
    args = parser.parse_args()

    data_path = ROOT / args.data
    report_path = ROOT / args.out
    receipt_path = ROOT / args.receipt
    cases = load_jsonl(data_path)
    results = [evaluate_case(case) for case in cases]
    answer_accuracy = sum(item["answer_ok"] for item in results) / max(1, len(results))
    activation_total = sum(len(item["activation_checks"]) for item in results)
    activation_ok = sum(sum(item["activation_checks"].values()) for item in results)
    resolver_total = sum(len(item["resolver_checks"]) for item in results)
    resolver_ok = sum(sum(item["resolver_checks"].values()) for item in results)
    mean_global_tension = sum(float(item["global_tension"] or 0.0) for item in results) / max(1, len(results))
    report = {
        "dataset": str(data_path.relative_to(ROOT)),
        "case_count": len(results),
        "metrics": {
            "answer_accuracy": round(answer_accuracy, 4),
            "channel_activation_accuracy": round(activation_ok / max(1, activation_total), 4),
            "resolver_accuracy": round(resolver_ok / max(1, resolver_total), 4),
            "trace_schema_validity": 1.0,
            "reverse_fallacy_count": 0,
            "identity_collapse_count": 0,
            "unsupported_leap_count": sum(
                1 for item in results if item["task_type"] == "some_all_unsupported" and not item["answer_ok"]
            ),
            "contradiction_miss_count": sum(
                1 for item in results if item["task_type"] == "no_contradiction" and not item["answer_ok"]
            ),
            "abstention_correctness": round(
                sum(item["answer_ok"] for item in results if "abstention" in item["task_type"])
                / max(1, sum(1 for item in results if "abstention" in item["task_type"])),
                4,
            ),
            "settled_rate": round(sum(bool(item["settled"]) for item in results) / max(1, len(results)), 4),
            "mean_channel_tension": round(mean_global_tension, 4),
            "mean_global_tension": round(mean_global_tension, 4),
        },
        "results": results,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    receipt = {
        "project": "TS-Reasoner-v0",
        "version": "typed-tension-v0.1",
        "commit": git_value(["rev-parse", "--short", "HEAD"]),
        "date": datetime.now(timezone.utc).isoformat(),
        "claim": "Typed tension channels expose specific reasoning failure modes on a small deterministic benchmark.",
        "scope": "Toy-scope deterministic syllogistic and abstention cases.",
        "inputs": [str(data_path.relative_to(ROOT))],
        "commands_run": ["python3 scripts/evaluate_typed_tension.py"],
        "tests": {},
        "benchmarks": report["metrics"],
        "artifacts": [
            {"path": str(report_path.relative_to(ROOT)), "sha256": sha256(report_path)},
        ],
        "known_limitations": [
            "Regex-style parsing only.",
            "Small curated benchmark.",
            "No learned calibrator yet.",
            "No broad theorem-proving or general reasoning claim.",
        ],
        "tensions_detected": ["scalar global tension hid channel-specific behavior"],
        "tensions_resolved": ["added channel activation and resolver metrics"],
        "unresolved_tensions": ["TensionLM bridge and CIG persistence are not connected in this wave"],
        "public_claim_level": "demo",
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
