#!/usr/bin/env python3
"""Export verifier trace training data from Candidate Model v2 reports."""

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

from ts_reasoner.trace_training_data import (
    export_training_rows_from_candidate_report,
    summarize_training_rows,
)


def git_value(args: list[str], default: str = "unknown") -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return default


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def build_receipt(report_path: Path, output_path: Path, summary_path: Path, summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "project": "TS-Reasoner-v0",
        "version": "v2.7.0-verifier-trace-training-data",
        "commit": git_value(["rev-parse", "--short", "HEAD"]),
        "date": datetime.now(timezone.utc).isoformat(),
        "claim": (
            "Verifier outcomes from Candidate Model v2 can be exported into supervised "
            "training rows containing candidate features, model predictions, typed-channel "
            "verifier status, failure reasons, and training targets."
        ),
        "scope": (
            "Training-data export from existing verifier traces; no model training, no "
            "TensionLM runtime, and no claim that exported rows are proof themselves."
        ),
        "commands_run": [
            "python3 scripts/evaluate_candidate_model_v2.py",
            "python3 scripts/export_verifier_trace_training_data.py",
            "python3 -m unittest discover -q",
        ],
        "inputs": [str(report_path.relative_to(ROOT))],
        "benchmarks": summary,
        "artifacts": [
            {"path": str(output_path.relative_to(ROOT)), "sha256": sha256(output_path)},
            {"path": str(summary_path.relative_to(ROOT)), "sha256": sha256(summary_path)},
            {"path": str(report_path.relative_to(ROOT)), "sha256": sha256(report_path)},
        ],
        "boundary": {
            "export_role": "turn verifier traces into future training rows",
            "model_role": "candidate proposal/ranking signal only",
            "verifier_role": "typed channels define target labels",
            "proof_role": "exported rows are not proof; they are supervised training data",
        },
        "known_limitations": [
            "Rows are derived from bounded v2.6 candidate-model reports.",
            "No new model is trained in v2.7.",
            "No TensionLM runtime is loaded.",
            "The dataset is still synthetic/benchmark-derived.",
            "Future training loops must keep verifier authority separate from model confidence.",
        ],
        "public_claim_level": "experimental",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default="artifacts/candidate_model_v2_report.json")
    parser.add_argument("--output", default="data/verifier_trace_training_data_v27.jsonl")
    parser.add_argument("--summary", default="artifacts/verifier_trace_training_data_summary.json")
    parser.add_argument("--receipt", default="artifacts/verifier_trace_training_data_receipt.json")
    args = parser.parse_args()

    report_path = ROOT / args.report
    output_path = ROOT / args.output
    summary_path = ROOT / args.summary
    receipt_path = ROOT / args.receipt

    report = json.loads(report_path.read_text(encoding="utf-8"))
    rows = export_training_rows_from_candidate_report(report)
    summary = summarize_training_rows(rows)

    write_jsonl(output_path, rows)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt_path.write_text(
        json.dumps(build_receipt(report_path, output_path, summary_path, summary), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
