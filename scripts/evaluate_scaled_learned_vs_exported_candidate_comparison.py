#!/usr/bin/env python3
"""v2.3 scaled learned-vs-exported candidate comparison."""

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

from scripts.evaluate_learned_vs_exported_candidate_comparison import evaluate_comparison


def git_value(args: list[str], default: str = "unknown") -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return default


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_receipt(report: dict[str, Any], data_path: Path, model_path: Path, report_path: Path) -> dict[str, Any]:
    metrics = report["metrics"]
    return {
        "project": "TS-Reasoner-v0",
        "version": "v2.3.0-scaled-learned-vs-exported-candidate-comparison",
        "commit": git_value(["rev-parse", "--short", "HEAD"]),
        "date": datetime.now(timezone.utc).isoformat(),
        "claim": (
            "The learned-vs-exported candidate comparison scales from the v2.2 seed "
            "set to a deterministic 15-case benchmark surface while preserving typed "
            "verification authority."
        ),
        "scope": (
            "Deterministic structured scaled comparison set generated inside this repo; "
            "no live TensionLM runtime and no additional model training."
        ),
        "commands_run": [
            "python3 scripts/build_scaled_comparison_set.py",
            "python3 scripts/evaluate_scaled_learned_vs_exported_candidate_comparison.py",
            "python3 -m unittest discover -q",
        ],
        "inputs": [
            str(data_path.relative_to(ROOT)),
            str(model_path.relative_to(ROOT)),
        ],
        "benchmarks": metrics,
        "artifacts": [
            {"path": str(report_path.relative_to(ROOT)), "sha256": sha256(report_path)},
            {"path": str(data_path.relative_to(ROOT)), "sha256": sha256(data_path)},
            {"path": str(model_path.relative_to(ROOT)), "sha256": sha256(model_path)},
        ],
        "boundary": {
            "learned_model_role": "rank candidates by learned structured features",
            "exported_baseline_role": "rank candidates by input/export confidence",
            "verifier_role": "typed channels decide accept/reject/abstain for both arms",
            "candidate_graph_contamination_count": metrics["candidate_graph_contamination_count"],
            "accepted_without_typed_support_count": metrics["accepted_without_typed_support_count"],
        },
        "known_limitations": [
            "Structured synthetic scaled cases, not broad natural-language evaluation.",
            "Exported arm is a confidence-ordering baseline, not a fresh live TensionLM generation run.",
            "No live TensionLM runtime is loaded.",
            "No additional training is performed.",
            "The result measures proposal/ranking quality under typed verification on this shaped benchmark surface.",
        ],
        "public_claim_level": "experimental",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/scaled_learned_vs_exported_candidate_comparison.jsonl")
    parser.add_argument("--model", default="artifacts/learned_candidate_model.json")
    parser.add_argument("--report", default="artifacts/scaled_learned_vs_exported_candidate_comparison_report.json")
    parser.add_argument("--receipt", default="artifacts/scaled_learned_vs_exported_candidate_comparison_receipt.json")
    args = parser.parse_args()

    data_path = ROOT / args.data
    model_path = ROOT / args.model
    report_path = ROOT / args.report
    receipt_path = ROOT / args.receipt

    report = evaluate_comparison(model_path, data_path)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt_path.write_text(
        json.dumps(build_receipt(report, data_path, model_path, report_path), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
