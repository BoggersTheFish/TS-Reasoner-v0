#!/usr/bin/env python3
"""Generate TS-Reasoner v4.5 milestone receipt pack.

This release does not add proof authority to any proposer/model output.
It packages the existing verifier-first ladder into one cold-reader artifact.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

INPUTS = [
    {
        "name": "v3.6 scaled proposer boundary",
        "path": "artifacts/scaled_proposer_boundary_v36_report.json",
        "role": "Scaled confidence-is-not-proof proposer boundary stress.",
    },
    {
        "name": "v3.7 real exported candidate batch",
        "path": "artifacts/real_exported_candidate_batch_v37_report.json",
        "role": "Real-export-shaped candidate batch through typed verifier boundary.",
    },
    {
        "name": "v3.8 external benchmark translation pack",
        "path": "artifacts/external_benchmark_translation_pack_v38_report.json",
        "role": "External-format rows translated into typed verifier traces.",
    },
    {
        "name": "v3.9 live proposer dry-run interface",
        "path": "artifacts/live_proposer_dry_run_interface_v39_report.json",
        "role": "Live-proposer-shaped dry-run interface without runtime authority.",
    },
    {
        "name": "v4.0 live proposer sandbox",
        "path": "artifacts/live_proposer_sandbox_v40_report.json",
        "role": "Bounded backend execution while typed verifier remains proof authority.",
    },
    {
        "name": "v4.2 GPT-2 output fixture adapter",
        "path": "artifacts/gpt2_output_fixture_adapter_v42_report.json",
        "role": "GPT-2-style generated text adapted as candidate data, not proof.",
    },
    {
        "name": "v4.3 natural-language reasoning shell",
        "path": "artifacts/natural_language_reasoning_shell_v43_report.json",
        "role": "Bounded NL prompts extracted into relation candidates then verified.",
    },
    {
        "name": "v4.4 GPT-2 baseline comparison harness",
        "path": "artifacts/gpt2_baseline_comparison_v44_receipt.json",
        "role": "Bounded baseline comparison; GPT-2 outputs are not proof authority.",
    },
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def metric(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in data:
            return data[key]
    return default


def main() -> None:
    reports: list[dict[str, Any]] = []
    missing: list[str] = []

    for item in INPUTS:
        path = ROOT / item["path"]
        if not path.exists():
            missing.append(item["path"])
            continue

        data = load_json(path)
        reports.append(
            {
                "name": item["name"],
                "path": item["path"],
                "sha256": sha256_file(path),
                "role": item["role"],
                "version": data.get("version"),
                "claim": data.get("claim"),
                "case_count": metric(
                    data,
                    "case_count",
                    "input_case_count",
                    "sandbox_case_count",
                    "comparison_case_count",
                    "nl_case_count",
                    "source_case_count",
                    "gpt2_fixture_case_count",
                ),
                "candidate_count": metric(
                    data,
                    "candidate_count",
                    "emitted_candidate_count",
                    "adapted_candidate_count",
                ),
                "verifier_selection_accuracy": data.get("verifier_selection_accuracy"),
                "confidence_top_accuracy": data.get("confidence_top_accuracy"),
                "wrong_accept_count": metric(
                    data,
                    "wrong_accept_count",
                    "ts_wrong_accept_count",
                    default=0,
                ),
                "accepted_without_typed_support_count": metric(
                    data,
                    "accepted_without_typed_support_count",
                    "ts_accepted_without_typed_support_count",
                    default=0,
                ),
                "candidate_graph_contamination_count": metric(
                    data,
                    "candidate_graph_contamination_count",
                    "ts_candidate_graph_contamination_count",
                    default=0,
                ),
                "trace_schema_validity": data.get("trace_schema_validity"),
                "live_tensionlm_runtime_loaded": data.get("live_tensionlm_runtime_loaded"),
                "confidence_is_not_proof": data.get("confidence_is_not_proof"),
                "generated_text_is_not_proof": data.get("generated_text_is_not_proof"),
            }
        )

    if missing:
        raise SystemExit(f"Missing required report(s): {missing}")

    aggregate = {
        "version": "v4.5-milestone-receipt-pack",
        "claim": (
            "TS-Reasoner has a bounded verifier-first milestone stack: external/generated/"
            "natural-language proposer outputs can enter as candidate data, but typed verifier "
            "channels remain proof authority."
        ),
        "release_type": "milestone_pack",
        "new_capability_claim": False,
        "external_benchmark_victory_claim": False,
        "broad_nlp_claim": False,
        "gpt2_superiority_claim": False,
        "live_tensionlm_runtime_claim": False,
        "confidence_is_not_proof": True,
        "generated_text_is_not_proof": True,
        "typed_verifier_is_proof_authority": True,
        "input_report_count": len(reports),
        "reports": reports,
    }

    aggregate["total_known_cases"] = sum(
        int(r["case_count"]) for r in reports if isinstance(r.get("case_count"), int)
    )
    aggregate["total_known_candidates"] = sum(
        int(r["candidate_count"]) for r in reports if isinstance(r.get("candidate_count"), int)
    )
    aggregate["wrong_accept_total"] = sum(int(r["wrong_accept_count"] or 0) for r in reports)
    aggregate["accepted_without_typed_support_total"] = sum(
        int(r["accepted_without_typed_support_count"] or 0) for r in reports
    )
    aggregate["candidate_graph_contamination_total"] = sum(
        int(r["candidate_graph_contamination_count"] or 0) for r in reports
    )

    aggregate["gates"] = {
        "all_reports_present": len(reports) == len(INPUTS),
        "wrong_accept_gate": aggregate["wrong_accept_total"] == 0,
        "accepted_without_support_gate": aggregate["accepted_without_typed_support_total"] == 0,
        "candidate_graph_contamination_gate": aggregate["candidate_graph_contamination_total"] == 0,
        "trace_schema_gate": all(r.get("trace_schema_validity") == 1.0 for r in reports if r.get("trace_schema_validity") is not None),
        "claim_boundary_gate": (
            aggregate["confidence_is_not_proof"]
            and aggregate["generated_text_is_not_proof"]
            and aggregate["typed_verifier_is_proof_authority"]
            and not aggregate["external_benchmark_victory_claim"]
            and not aggregate["broad_nlp_claim"]
            and not aggregate["gpt2_superiority_claim"]
            and not aggregate["live_tensionlm_runtime_claim"]
        ),
    }
    aggregate["gates"]["all_gates_passed"] = all(aggregate["gates"].values())

    if not aggregate["gates"]["all_gates_passed"]:
        raise SystemExit(json.dumps(aggregate["gates"], indent=2))

    out_path = ROOT / "artifacts/v4_5_milestone_receipt_pack.json"
    out_path.write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "version": aggregate["version"],
        "input_report_count": aggregate["input_report_count"],
        "total_known_cases": aggregate["total_known_cases"],
        "total_known_candidates": aggregate["total_known_candidates"],
        "wrong_accept_total": aggregate["wrong_accept_total"],
        "accepted_without_typed_support_total": aggregate["accepted_without_typed_support_total"],
        "candidate_graph_contamination_total": aggregate["candidate_graph_contamination_total"],
        "all_gates_passed": aggregate["gates"]["all_gates_passed"],
        "output": str(out_path.relative_to(ROOT)),
    }, indent=2))


if __name__ == "__main__":
    main()
