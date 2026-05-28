#!/usr/bin/env python3
"""Compare learned candidate ranking against exported-candidate confidence ordering.

v2.2 keeps typed verification as the proof authority. The comparison asks a
narrow question: when the same candidate set is viewed two ways, does the learned
candidate model rank the typed-supported candidate above the high-confidence
export-style distractors?
"""

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

from ts_reasoner.learned_model.dataset import load_cases
from ts_reasoner.learned_model.infer import verify_scored_case
from ts_reasoner.learned_model.model import TinyCandidateModel
from ts_reasoner.tensionlm_adapter import parse_tensionlm_export_row, run_tensionlm_export_row


def git_value(args: list[str], default: str = "unknown") -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return default


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rate(values: list[bool]) -> float:
    return round(sum(values) / max(1, len(values)), 4)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def ensure_comparison_dataset(source_path: Path, comparison_path: Path) -> None:
    if comparison_path.exists():
        return
    source_rows = load_jsonl(source_path)
    rows = []
    for row in source_rows:
        copied = dict(row)
        copied["split"] = "comparison"
        copied["source_dataset"] = str(source_path.relative_to(ROOT))
        copied["comparison_policy"] = {
            "learned_arm": "TinyCandidateModel ranking_score order",
            "exported_arm": "exported candidate confidence order",
            "authority": "typed verifier result, not either ranker",
        }
        rows.append(copied)
    write_jsonl(comparison_path, rows)


def trace_schema_valid(payload: dict[str, Any]) -> bool:
    verification = payload.get("verification", {})
    return all(key in payload for key in ("input_text", "verification", "trace_receipt")) and all(
        key in verification for key in ("accepted", "rejected", "abstained", "candidate_results")
    )


def result_has_typed_support(result: dict[str, Any]) -> bool:
    return bool({"logic_transitivity", "surface_structure"} & set(result.get("channels", [])))


def contamination_count(results: list[dict[str, Any]]) -> int:
    return sum(
        1
        for result in results
        for status in result.get("typed_runtime", {}).get("context", {}).get("surface_tags", {}).values()
        if status == "candidate"
    )


def exported_row_from_case(case: dict[str, Any]) -> Any:
    exported_candidates = []
    for candidate in case["candidates"]:
        exported_candidates.append(
            {
                "candidate_id": candidate["candidate_id"],
                "claim": candidate["claim"],
                "raw_text": candidate.get("raw_output", candidate["claim"]),
                "confidence": candidate.get("confidence", 0.5),
                "provenance": "tensionlm_eval_export",
            }
        )
    row = {
        "case_id": case["case_id"],
        "input_text": case["input_text"],
        "model": "exported_candidate_confidence_baseline",
        "candidates": exported_candidates,
        "source_dataset": case.get("source_dataset"),
    }
    if case.get("premises"):
        row["premises"] = case["premises"]
    return parse_tensionlm_export_row(row)


def evaluate_case(model: TinyCandidateModel, case: dict[str, Any]) -> dict[str, Any]:
    learned_payload = verify_scored_case(model, case)
    learned_results = learned_payload["verification"]["candidate_results"]
    learned_by_id = {item["candidate_id"]: item for item in learned_results}
    learned_top = learned_payload["scored_candidates"][0]
    learned_top_result = learned_by_id[learned_top["candidate_id"]]

    export_row = exported_row_from_case(case)
    exported_payload = run_tensionlm_export_row(export_row)
    exported_results = exported_payload["verification"]["candidate_results"]
    exported_by_id = {item["candidate_id"]: item for item in exported_results}
    exported_top_candidate = max(case["candidates"], key=lambda item: float(item.get("confidence", 0.0)))
    exported_top_result = exported_by_id[exported_top_candidate["candidate_id"]]

    labels = case.get("labels", {})
    accepted_ids = {candidate_id for candidate_id, label in labels.items() if label["status"] == "accepted"}
    high_confidence_bad_ids = {
        candidate["candidate_id"]
        for candidate in case["candidates"]
        if float(candidate.get("confidence", 0.0)) >= 0.9
        and labels.get(candidate["candidate_id"], {}).get("status") != "accepted"
    }

    exported_high_confidence_bad_checks = [
        exported_by_id[candidate_id]["status"] in {"rejected", "abstained"}
        for candidate_id in high_confidence_bad_ids
        if candidate_id in exported_by_id
    ]

    accepted_without_support = sum(
        1 for result in learned_results + exported_results
        if result["status"] == "accepted" and not result_has_typed_support(result)
    )

    learned_top_accepted = learned_top_result["status"] == "accepted"
    exported_top_accepted = exported_top_result["status"] == "accepted"

    return {
        "case_id": case["case_id"],
        "tags": case.get("tags", []),
        "accepted_candidate_ids": sorted(accepted_ids),
        "high_confidence_bad_candidate_ids": sorted(high_confidence_bad_ids),
        "learned": {
            "top_candidate_id": learned_top["candidate_id"],
            "top_claim": learned_top["claim"],
            "top_model_confidence": learned_top["prediction"]["model_confidence"],
            "top_ranking_score": learned_top["prediction"]["ranking_score"],
            "top_status": learned_top_result["status"],
            "top_channels": learned_top_result["channels"],
            "top_is_accepted": learned_top_accepted,
            "trace_schema_valid": trace_schema_valid(learned_payload),
        },
        "exported_confidence_baseline": {
            "top_candidate_id": exported_top_candidate["candidate_id"],
            "top_claim": exported_top_candidate["claim"],
            "top_input_confidence": exported_top_candidate.get("confidence"),
            "top_status": exported_top_result["status"],
            "top_channels": exported_top_result["channels"],
            "top_is_accepted": exported_top_accepted,
            "trace_schema_valid": trace_schema_valid(exported_payload),
        },
        "comparison": {
            "learned_top_beats_exported_confidence_top": learned_top_accepted and not exported_top_accepted,
            "same_top_candidate": learned_top["candidate_id"] == exported_top_candidate["candidate_id"],
            "exported_high_confidence_bad_block_checks": exported_high_confidence_bad_checks,
            "accepted_without_typed_support_count": accepted_without_support,
            "candidate_graph_contamination_count": contamination_count(learned_results) + contamination_count(exported_results),
        },
    }


def evaluate_comparison(model_path: Path, data_path: Path) -> dict[str, Any]:
    model = TinyCandidateModel.load(model_path)
    cases = load_cases(data_path)
    results = [evaluate_case(model, case) for case in cases]
    high_confidence_bad_checks = [
        check
        for row in results
        for check in row["comparison"]["exported_high_confidence_bad_block_checks"]
    ]
    return {
        "dataset": str(data_path.relative_to(ROOT)),
        "case_count": len(results),
        "metrics": {
            "learned_top_accept_rate": rate([row["learned"]["top_is_accepted"] for row in results]),
            "exported_confidence_top_accept_rate": rate([
                row["exported_confidence_baseline"]["top_is_accepted"] for row in results
            ]),
            "learned_top_beats_exported_confidence_top_rate": rate([
                row["comparison"]["learned_top_beats_exported_confidence_top"] for row in results
            ]),
            "same_top_candidate_rate": rate([row["comparison"]["same_top_candidate"] for row in results]),
            "exported_high_confidence_bad_block_rate": rate(high_confidence_bad_checks),
            "accepted_without_typed_support_count": sum(
                row["comparison"]["accepted_without_typed_support_count"] for row in results
            ),
            "candidate_graph_contamination_count": sum(
                row["comparison"]["candidate_graph_contamination_count"] for row in results
            ),
            "trace_schema_validity": rate([
                row["learned"]["trace_schema_valid"] and row["exported_confidence_baseline"]["trace_schema_valid"]
                for row in results
            ]),
        },
        "results": results,
    }


def build_receipt(report: dict[str, Any], model_path: Path, data_path: Path, report_path: Path) -> dict[str, Any]:
    metrics = report["metrics"]
    return {
        "project": "TS-Reasoner-v0",
        "version": "v2.2.0-learned-vs-exported-candidate-comparison",
        "commit": git_value(["rev-parse", "--short", "HEAD"]),
        "date": datetime.now(timezone.utc).isoformat(),
        "claim": (
            "On the same structured adversarial candidate cases, the learned candidate "
            "model is compared against exported-candidate confidence ordering while "
            "typed verification remains proof authority."
        ),
        "scope": (
            "Same-case comparison using the v2.0 learned candidate model and an "
            "exported-candidate confidence baseline generated through the existing "
            "TensionLM export adapter; no live TensionLM runtime is loaded."
        ),
        "commands_run": [
            "python3 scripts/evaluate_learned_vs_exported_candidate_comparison.py",
            "python3 -m unittest discover -q",
        ],
        "inputs": [
            str(model_path.relative_to(ROOT)),
            str(data_path.relative_to(ROOT)),
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
            "Structured synthetic adversarial cases, not broad natural-language evaluation.",
            "Exported arm is an export-adapter confidence baseline, not a fresh live TensionLM generation run.",
            "No live TensionLM runtime is loaded.",
            "The result measures proposal/ranking quality under typed verification, not general reasoning capability.",
        ],
        "public_claim_level": "experimental",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="data/learned_candidate_model_adversarial.jsonl")
    parser.add_argument("--data", default="data/learned_vs_exported_candidate_comparison.jsonl")
    parser.add_argument("--model", default="artifacts/learned_candidate_model.json")
    parser.add_argument("--report", default="artifacts/learned_vs_exported_candidate_comparison_report.json")
    parser.add_argument("--receipt", default="artifacts/learned_vs_exported_candidate_comparison_receipt.json")
    args = parser.parse_args()

    source_path = ROOT / args.source
    data_path = ROOT / args.data
    model_path = ROOT / args.model
    report_path = ROOT / args.report
    receipt_path = ROOT / args.receipt

    ensure_comparison_dataset(source_path, data_path)
    report = evaluate_comparison(model_path, data_path)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt_path.write_text(
        json.dumps(build_receipt(report, model_path, data_path, report_path), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
