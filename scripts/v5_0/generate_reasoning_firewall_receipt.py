#!/usr/bin/env python3
"""Generate TS-Reasoner v5.0 reasoning firewall receipt.

v5.0 is a milestone packaging release for the verifier-first answer arena line:
- v4.7 multi-proposer answer arena
- v4.8 bounded claim decomposer arena
- v4.9 unsupported claim audit

It does not claim broad NLP, general theorem proving, external benchmark victory,
or live TensionLM runtime integration.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

INPUTS = [
    {
        "name": "v4.7 verifier-first answer arena",
        "path": "artifacts/v4_7_answer_arena_report.json",
        "role": "Competing generated answers are selected/rejected/abstained by typed support rather than confidence.",
    },
    {
        "name": "v4.8 claim decomposer arena",
        "path": "artifacts/v4_8_claim_decomposer_arena_report.json",
        "role": "Messy generated answers are decomposed into bounded relation claims before verification.",
    },
    {
        "name": "v4.9 unsupported claim audit",
        "path": "artifacts/v4_9_unsupported_claim_audit_report.json",
        "role": "Generated explanations with unsupported bounded claims are rejected even if final answer is supported.",
    },
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def metric(data: dict[str, Any], key: str, default: Any = 0) -> Any:
    return data.get(key, default)


def main() -> int:
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
                "case_count": metric(data, "case_count"),
                "candidate_count": metric(data, "candidate_count"),
                "arena_selection_accuracy": data.get("arena_selection_accuracy"),
                "confidence_top_accuracy": data.get("confidence_top_accuracy"),
                "verifier_overrode_confidence_count": metric(data, "verifier_overrode_confidence_count"),
                "unsupported_claim_candidate_count": metric(data, "unsupported_claim_candidate_count"),
                "wrong_accept_count": metric(data, "wrong_accept_count"),
                "accepted_without_typed_support_count": metric(data, "accepted_without_typed_support_count"),
                "accepted_with_unsupported_claims_count": metric(data, "accepted_with_unsupported_claims_count"),
                "candidate_graph_contamination_count": metric(data, "candidate_graph_contamination_count"),
                "trace_schema_validity": data.get("trace_schema_validity"),
                "all_gates_passed": data.get("gates", {}).get("all_gates_passed"),
                "confidence_is_not_proof": data.get("confidence_is_not_proof"),
                "generated_text_is_not_proof": data.get("generated_text_is_not_proof"),
                "candidate_source_is_not_proof": data.get("candidate_source_is_not_proof"),
                "typed_verifier_is_proof_authority": data.get("typed_verifier_is_proof_authority"),
                "candidate_claims_do_not_contaminate_graph": data.get("candidate_claims_do_not_contaminate_graph"),
                "external_benchmark_victory_claim": data.get("external_benchmark_victory_claim"),
                "broad_nlp_claim": data.get("broad_nlp_claim"),
                "general_theorem_proving_claim": data.get("general_theorem_proving_claim"),
                "live_tensionlm_runtime_claim": data.get("live_tensionlm_runtime_claim"),
            }
        )

    if missing:
        raise SystemExit(f"Missing required report(s): {missing}")

    receipt = {
        "version": "v5.0-verifier-first-reasoning-firewall",
        "release_type": "milestone_pack",
        "claim": (
            "Generated answers are treated as candidate data. TS-Reasoner decomposes bounded claims, "
            "audits explanation support, rejects unsupported reasoning, and selects or abstains using "
            "typed verifier channels rather than confidence, fluency, or source identity."
        ),
        "new_capability_claim": False,
        "milestone_capability_summary": "bounded verifier-first generated reasoning firewall",
        "confidence_is_not_proof": True,
        "generated_text_is_not_proof": True,
        "candidate_source_is_not_proof": True,
        "typed_verifier_is_proof_authority": True,
        "candidate_claims_do_not_contaminate_graph": True,
        "external_benchmark_victory_claim": False,
        "broad_nlp_claim": False,
        "general_theorem_proving_claim": False,
        "live_tensionlm_runtime_claim": False,
        "input_report_count": len(reports),
        "reports": reports,
    }

    receipt["total_cases"] = sum(int(r["case_count"] or 0) for r in reports)
    receipt["total_candidates"] = sum(int(r["candidate_count"] or 0) for r in reports)
    receipt["total_verifier_overrides"] = sum(int(r["verifier_overrode_confidence_count"] or 0) for r in reports)
    receipt["total_unsupported_claim_candidate_count"] = sum(int(r["unsupported_claim_candidate_count"] or 0) for r in reports)
    receipt["wrong_accept_total"] = sum(int(r["wrong_accept_count"] or 0) for r in reports)
    receipt["accepted_without_typed_support_total"] = sum(
        int(r["accepted_without_typed_support_count"] or 0) for r in reports
    )
    receipt["accepted_with_unsupported_claims_total"] = sum(
        int(r["accepted_with_unsupported_claims_count"] or 0) for r in reports
    )
    receipt["candidate_graph_contamination_total"] = sum(
        int(r["candidate_graph_contamination_count"] or 0) for r in reports
    )

    receipt["gates"] = {
        "all_reports_present": len(reports) == len(INPUTS),
        "all_input_gates_passed": all(r["all_gates_passed"] is True for r in reports),
        "arena_selection_gate": all(r["arena_selection_accuracy"] == 1.0 for r in reports),
        "unsupported_claim_audit_present_gate": receipt["total_unsupported_claim_candidate_count"] > 0,
        "wrong_accept_gate": receipt["wrong_accept_total"] == 0,
        "accepted_without_support_gate": receipt["accepted_without_typed_support_total"] == 0,
        "accepted_with_unsupported_claims_gate": receipt["accepted_with_unsupported_claims_total"] == 0,
        "candidate_graph_contamination_gate": receipt["candidate_graph_contamination_total"] == 0,
        "trace_schema_gate": all(r["trace_schema_validity"] == 1.0 for r in reports),
        "claim_boundary_gate": (
            receipt["confidence_is_not_proof"]
            and receipt["generated_text_is_not_proof"]
            and receipt["candidate_source_is_not_proof"]
            and receipt["typed_verifier_is_proof_authority"]
            and receipt["candidate_claims_do_not_contaminate_graph"]
            and not receipt["external_benchmark_victory_claim"]
            and not receipt["broad_nlp_claim"]
            and not receipt["general_theorem_proving_claim"]
            and not receipt["live_tensionlm_runtime_claim"]
        ),
    }
    receipt["gates"]["all_gates_passed"] = all(receipt["gates"].values())

    if not receipt["gates"]["all_gates_passed"]:
        print(json.dumps(receipt["gates"], indent=2, sort_keys=True))
        return 1

    out = ROOT / "artifacts/v5_0_reasoning_firewall_receipt.json"
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "version": receipt["version"],
        "input_report_count": receipt["input_report_count"],
        "total_cases": receipt["total_cases"],
        "total_candidates": receipt["total_candidates"],
        "total_verifier_overrides": receipt["total_verifier_overrides"],
        "total_unsupported_claim_candidate_count": receipt["total_unsupported_claim_candidate_count"],
        "wrong_accept_total": receipt["wrong_accept_total"],
        "accepted_without_typed_support_total": receipt["accepted_without_typed_support_total"],
        "accepted_with_unsupported_claims_total": receipt["accepted_with_unsupported_claims_total"],
        "candidate_graph_contamination_total": receipt["candidate_graph_contamination_total"],
        "all_gates_passed": receipt["gates"]["all_gates_passed"],
        "output": str(out.relative_to(ROOT)),
    }, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
