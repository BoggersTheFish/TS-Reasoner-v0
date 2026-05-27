#!/usr/bin/env python3
"""Evaluate the learned candidate model under typed verifier authority."""

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

from ts_reasoner.learned_model.dataset import load_cases, write_split_files
from ts_reasoner.learned_model.evaluate import evaluate_cases
from ts_reasoner.learned_model.model import TinyCandidateModel
from ts_reasoner.learned_model.train import train_model


def git_value(args: list[str], default: str = "unknown") -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return default


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ensure_inputs(model_path: Path, eval_path: Path, stress_path: Path) -> None:
    if not eval_path.exists() or not stress_path.exists():
        write_split_files(ROOT)
    if not model_path.exists():
        train_path = ROOT / "data/learned_candidate_model_train.jsonl"
        if not train_path.exists():
            write_split_files(ROOT)
        train_model(load_cases(train_path)).save(model_path)


def build_receipt(
    eval_report: dict[str, Any],
    stress_report: dict[str, Any],
    model_path: Path,
    eval_report_path: Path,
    stress_report_path: Path,
) -> dict[str, Any]:
    return {
        "project": "TS-Reasoner-v0",
        "version": "v2.0.0-learned-candidate-model",
        "commit": git_value(["rev-parse", "--short", "HEAD"]),
        "date": datetime.now(timezone.utc).isoformat(),
        "claim": "A tiny learned candidate model can rank candidate claims and predict channel/resolver signals while TS-Reasoner typed channels remain proof authority.",
        "scope": "Pure-Python learned proposer/ranker over structured reasoning examples; no TensionLM loading or training.",
        "commands_run": [
            "python3 scripts/build_learned_candidate_dataset.py",
            "python3 scripts/train_learned_candidate_model.py",
            "python3 scripts/evaluate_learned_candidate_model.py",
        ],
        "inputs": [
            "data/learned_candidate_model_train.jsonl",
            "data/learned_candidate_model_eval.jsonl",
            "data/learned_candidate_model_stress.jsonl",
        ],
        "benchmarks": {
            "eval": eval_report["metrics"],
            "stress": stress_report["metrics"],
        },
        "artifacts": [
            {"path": str(model_path.relative_to(ROOT)), "sha256": sha256(model_path)},
            {"path": str(eval_report_path.relative_to(ROOT)), "sha256": sha256(eval_report_path)},
            {"path": str(stress_report_path.relative_to(ROOT)), "sha256": sha256(stress_report_path)},
        ],
        "boundary": {
            "learned_model_role": "candidate ranking and channel/resolver prediction",
            "verifier_role": "TS-Reasoner typed channels accept, reject, or abstain",
            "confidence_role": "metadata only; never proof authority",
            "candidate_graph_contamination_count": (
                eval_report["metrics"]["candidate_graph_contamination_count"]
                + stress_report["metrics"]["candidate_graph_contamination_count"]
            ),
        },
        "known_limitations": [
            "Synthetic, parser-controlled structured examples.",
            "Tiny linear model, not a full language model.",
            "No live TensionLM runtime is loaded.",
            "Model predictions are advisory; all accepted claims require typed-channel support.",
        ],
        "public_claim_level": "experimental",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="artifacts/learned_candidate_model.json")
    parser.add_argument("--eval", default="data/learned_candidate_model_eval.jsonl")
    parser.add_argument("--stress", default="data/learned_candidate_model_stress.jsonl")
    parser.add_argument("--report", default="artifacts/learned_candidate_model_report.json")
    parser.add_argument("--stress-report", default="artifacts/learned_candidate_model_stress_report.json")
    parser.add_argument("--receipt", default="artifacts/learned_candidate_model_receipt.json")
    args = parser.parse_args()

    model_path = ROOT / args.model
    eval_path = ROOT / args.eval
    stress_path = ROOT / args.stress
    ensure_inputs(model_path, eval_path, stress_path)
    model = TinyCandidateModel.load(model_path)
    eval_report = {
        "dataset": str(eval_path.relative_to(ROOT)),
        **evaluate_cases(model, load_cases(eval_path)),
    }
    stress_report = {
        "dataset": str(stress_path.relative_to(ROOT)),
        **evaluate_cases(model, load_cases(stress_path)),
    }
    report_path = ROOT / args.report
    stress_report_path = ROOT / args.stress_report
    receipt_path = ROOT / args.receipt
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(eval_report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    stress_report_path.write_text(json.dumps(stress_report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt_path.write_text(
        json.dumps(
            build_receipt(eval_report, stress_report, model_path, report_path, stress_report_path),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
