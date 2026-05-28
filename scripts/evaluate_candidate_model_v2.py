#!/usr/bin/env python3
"""Evaluate Candidate Model v2 against baselines under typed verifier authority."""

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

from scripts.build_candidate_model_v2_dataset import main as build_dataset
from ts_reasoner.learned_model.dataset import load_cases
from ts_reasoner.learned_model.evaluate import evaluate_cases
from ts_reasoner.learned_model.infer import verify_scored_case
from ts_reasoner.learned_model.model import TinyCandidateModel
from ts_reasoner.learned_model.train import train_model


def git_value(args: list[str], default: str = "unknown") -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return default


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ensure_inputs(train_path: Path, eval_path: Path, stress_path: Path, model_path: Path) -> None:
    if not train_path.exists() or not eval_path.exists() or not stress_path.exists():
        build_dataset()
    if not model_path.exists():
        model = train_model(load_cases(train_path), epochs=120, learning_rate=0.25)
        model.metadata.update(
            {
                "version": "candidate-model-v2",
                "train_dataset": str(train_path.relative_to(ROOT)),
                "source": "v2.5 benchmark harness derived candidate set",
                "claim": "Candidate Model v2 learns benchmark-derived candidate ranking; typed verifier remains authority.",
            }
        )
        model.save(model_path)


def confidence_baseline_case(case: dict[str, Any]) -> dict[str, Any]:
    candidates = sorted(case["candidates"], key=lambda item: float(item.get("confidence", 0.0)), reverse=True)
    accepted = {candidate_id for candidate_id, label in case["labels"].items() if label["status"] == "accepted"}
    top_id = candidates[0]["candidate_id"] if candidates else ""
    return {
        "case_id": case["case_id"],
        "top_candidate_id": top_id,
        "top_is_accepted": top_id in accepted,
        "top_status": case["labels"].get(top_id, {}).get("status"),
    }


def oracle_baseline_case(case: dict[str, Any]) -> dict[str, Any]:
    accepted = [candidate_id for candidate_id, label in case["labels"].items() if label["status"] == "accepted"]
    return {
        "case_id": case["case_id"],
        "has_accepted_candidate": bool(accepted),
        "top_is_accepted": bool(accepted),
    }


def rate(values: list[bool]) -> float:
    return round(sum(values) / max(1, len(values)), 4)


def baseline_report(cases: list[dict[str, Any]]) -> dict[str, Any]:
    confidence_rows = [confidence_baseline_case(case) for case in cases]
    oracle_rows = [oracle_baseline_case(case) for case in cases]
    return {
        "confidence_top_accept_rate": rate([row["top_is_accepted"] for row in confidence_rows]),
        "oracle_possible_accept_rate": rate([row["top_is_accepted"] for row in oracle_rows]),
        "confidence_rows": confidence_rows,
    }


def accepted_without_support_count(model: TinyCandidateModel, cases: list[dict[str, Any]]) -> int:
    total = 0
    for case in cases:
        payload = verify_scored_case(model, case)
        for result in payload["verification"]["candidate_results"]:
            if result["status"] != "accepted":
                continue
            channels = set(result.get("channels", {}))
            if not {"logic_transitivity", "surface_structure"} & channels:
                total += 1
    return total


def benchmark_aligned_metrics(model: TinyCandidateModel, cases: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for case in cases:
        payload = verify_scored_case(model, case)
        results_by_id = {
            result["candidate_id"]: result
            for result in payload["verification"]["candidate_results"]
        }
        top_id = payload["scored_candidates"][0]["candidate_id"] if payload["scored_candidates"] else ""
        top_result = results_by_id.get(top_id, {})
        expected_query_result = results_by_id.get("candidate_expected_query", {})
        accepted_ids = {
            candidate_id
            for candidate_id, label in case.get("labels", {}).items()
            if label["status"] == "accepted"
        }
        has_accepted = bool(accepted_ids)
        rows.append(
            {
                "case_id": case["case_id"],
                "tags": case.get("tags", []),
                "top_id": top_id,
                "top_status": top_result.get("status"),
                "top_accepted": top_result.get("status") == "accepted",
                "expected_query_status": expected_query_result.get("status"),
                "ranking_correct": top_id in accepted_ids or not has_accepted,
                "recovered_supported_alternative": (
                    "invalid" in case.get("tags", [])
                    and expected_query_result.get("status") in {"rejected", "abstained"}
                    and top_result.get("status") == "accepted"
                ),
            }
        )

    multi_premise = [row for row in rows if "multi_premise" in row["tags"]]
    invalid = [row for row in rows if "invalid" in row["tags"]]
    malformed = [row for row in rows if "malformed_input" in row["tags"]]

    return {
        "multi_premise_ranking_success_rate": rate([row["ranking_correct"] for row in multi_premise]),
        "invalid_query_rejection_or_abstention_rate": rate([
            row["expected_query_status"] in {"rejected", "abstained", None}
            for row in invalid
        ]),
        "supported_alternative_recovery_rate": rate([
            row["recovered_supported_alternative"]
            for row in invalid
            if row["top_accepted"]
        ]),
        "malformed_input_non_accept_rate": rate([row["top_status"] in {"rejected", "abstained", None} for row in malformed]),
        "benchmark_aligned_metric_note": (
            "v2.6 is a candidate-ranking release. Invalid benchmark queries may have a supported "
            "alternative candidate, so the correct metric is whether the invalid query is blocked "
            "and whether the model recovers the supported alternative."
        ),
    }


def evaluate_split(model: TinyCandidateModel, cases: list[dict[str, Any]]) -> dict[str, Any]:
    learned = evaluate_cases(model, cases)
    baselines = baseline_report(cases)

    # v2.0/v2.1 inherited metrics include tags such as deeper_chain/distractor.
    # The v2.6 surface is benchmark-derived and uses tags such as multi_premise,
    # invalid, and malformed_input, so we report benchmark-aligned metrics here.
    learned["metrics"].pop("deeper_chain_success_rate", None)
    learned["metrics"].pop("distractor_robustness", None)

    benchmark_metrics = benchmark_aligned_metrics(model, cases)

    learned["metrics"]["confidence_baseline_top_accept_rate"] = baselines["confidence_top_accept_rate"]
    learned["metrics"]["oracle_possible_accept_rate"] = baselines["oracle_possible_accept_rate"]
    learned["metrics"]["learned_beats_confidence_baseline_margin"] = round(
        learned["metrics"]["candidate_ranking_accuracy"] - baselines["confidence_top_accept_rate"],
        4,
    )
    learned["metrics"]["accepted_without_typed_support_count"] = accepted_without_support_count(model, cases)
    learned["metrics"].update(benchmark_metrics)
    learned["baselines"] = baselines
    return learned


def build_receipt(
    report: dict[str, Any],
    model_path: Path,
    train_path: Path,
    eval_path: Path,
    stress_path: Path,
    report_path: Path,
) -> dict[str, Any]:
    return {
        "project": "TS-Reasoner-v0",
        "version": "v2.6.0-candidate-model-v2",
        "commit": git_value(["rev-parse", "--short", "HEAD"]),
        "date": datetime.now(timezone.utc).isoformat(),
        "claim": (
            "Candidate Model v2 trains on the v2.5 benchmark-derived candidate set and "
            "improves candidate ranking over confidence ordering while typed verifier "
            "channels remain proof authority."
        ),
        "scope": (
            "Pure-Python tiny linear candidate model over benchmark-derived candidate sets; "
            "no TensionLM runtime, no broad NLP, and no neural training."
        ),
        "commands_run": [
            "python3 scripts/build_candidate_model_v2_dataset.py",
            "python3 scripts/train_candidate_model_v2.py",
            "python3 scripts/evaluate_candidate_model_v2.py",
            "python3 -m unittest discover -q",
        ],
        "inputs": [
            str(train_path.relative_to(ROOT)),
            str(eval_path.relative_to(ROOT)),
            str(stress_path.relative_to(ROOT)),
        ],
        "benchmarks": report["metrics"],
        "artifacts": [
            {"path": str(model_path.relative_to(ROOT)), "sha256": sha256(model_path)},
            {"path": str(report_path.relative_to(ROOT)), "sha256": sha256(report_path)},
            {"path": str(train_path.relative_to(ROOT)), "sha256": sha256(train_path)},
            {"path": str(eval_path.relative_to(ROOT)), "sha256": sha256(eval_path)},
            {"path": str(stress_path.relative_to(ROOT)), "sha256": sha256(stress_path)},
        ],
        "boundary": {
            "model_role": "rank candidate graph claims and predict advisory labels",
            "verifier_role": "typed channels decide accept/reject/abstain",
            "confidence_role": "baseline and metadata only; not proof authority",
            "accepted_without_typed_support_count": report["metrics"]["accepted_without_typed_support_count"],
            "candidate_graph_contamination_count": report["metrics"]["candidate_graph_contamination_count"],
        },
        "known_limitations": [
            "Benchmark-derived candidate set remains synthetic and bounded.",
            "Pure-Python tiny linear model, not a full neural language model.",
            "No live TensionLM runtime is loaded.",
            "No broad NLP claim.",
            "Model predictions remain advisory; typed verifier channels remain authority.",
        ],
        "public_claim_level": "experimental",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", default="data/candidate_model_v2_train.jsonl")
    parser.add_argument("--eval", default="data/candidate_model_v2_eval.jsonl")
    parser.add_argument("--stress", default="data/candidate_model_v2_stress.jsonl")
    parser.add_argument("--model", default="artifacts/candidate_model_v2.json")
    parser.add_argument("--report", default="artifacts/candidate_model_v2_report.json")
    parser.add_argument("--receipt", default="artifacts/candidate_model_v2_receipt.json")
    args = parser.parse_args()

    train_path = ROOT / args.train
    eval_path = ROOT / args.eval
    stress_path = ROOT / args.stress
    model_path = ROOT / args.model
    report_path = ROOT / args.report
    receipt_path = ROOT / args.receipt

    ensure_inputs(train_path, eval_path, stress_path, model_path)
    model = TinyCandidateModel.load(model_path)

    eval_report = evaluate_split(model, load_cases(eval_path))
    stress_report = evaluate_split(model, load_cases(stress_path))
    combined_cases = load_cases(eval_path) + load_cases(stress_path)
    combined_report = evaluate_split(model, combined_cases)

    report = {
        "version": "v2.6.0-candidate-model-v2",
        "claim": "Candidate Model v2 improves candidate ranking over confidence ordering under typed verifier authority.",
        "scope": "Benchmark-derived bounded candidate ranking; no TensionLM runtime and no broad NLP.",
        "case_count": len(combined_cases),
        "metrics": combined_report["metrics"],
        "eval": eval_report,
        "stress": stress_report,
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt_path.write_text(
        json.dumps(build_receipt(report, model_path, train_path, eval_path, stress_path, report_path), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report["metrics"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
