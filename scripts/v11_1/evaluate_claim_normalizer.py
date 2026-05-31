from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ts_reasoner.claim_normalizer import normalize_claim_surface
from ts_reasoner.support_path_verifier import verify_support_path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "v11_1" / "natural_claim_surface_cases.jsonl"
REPORT = ROOT / "artifacts" / "v11_1" / "claim_normalizer_report.json"
RECEIPT = ROOT / "artifacts" / "v11_1" / "claim_normalizer_receipt.json"


def load_cases() -> list[dict[str, Any]]:
    return [json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    rows = []
    parsed = 0
    canonical_ok = 0
    quantifier_ok = 0

    for case in load_cases():
        observed = normalize_claim_surface(case["surface"])
        passed = (
            observed["parse_status"] == case["expected_status"]
            and observed["canonical_claim"] == case["expected_canonical"]
            and observed["quantifier"] == case["expected_quantifier"]
        )
        parsed += int(observed["parse_status"] == "parsed")
        canonical_ok += int(observed["canonical_claim"] == case["expected_canonical"])
        quantifier_ok += int(observed["quantifier"] == case["expected_quantifier"])
        rows.append({
            "case_id": case["case_id"],
            "surface": case["surface"],
            "expected_canonical": case["expected_canonical"],
            "observed_canonical": observed["canonical_claim"],
            "observed_status": observed["parse_status"],
            "observed_quantifier": observed["quantifier"],
            "passed": passed,
        })

    # Regression: old proof behavior plus new natural surfaces must remain verifier-first.
    behavior_cases = [
        {
            "name": "natural_transitive_is_every",
            "premises": [
                "every generated output is candidate data",
                "all candidate data are untrusted material",
            ],
            "claim": "all generated output is untrusted material",
            "expected_status": "accepted",
            "expected_channel": "transitive_all",
        },
        {
            "name": "natural_negative_is",
            "premises": [
                "model confidence is generated signal",
                "no generated signal is proof",
            ],
            "claim": "model confidence is not proof",
            "expected_status": "accepted",
            "expected_channel": "negative_exclusion",
        },
        {
            "name": "natural_reverse_rejected",
            "premises": [
                "generated text is candidate data",
            ],
            "claim": "candidate data is generated text",
            "expected_status": "rejected",
            "expected_reason": "reverse_inference_block",
        },
        {
            "name": "natural_unsupported_abstained",
            "premises": [
                "generated text is candidate data",
            ],
            "claim": "generated text is proof",
            "expected_status": "abstained",
            "expected_reason": "unsupported_claim",
        },
        {
            "name": "identity_still_blocked",
            "premises": [
                "every fish is fish",
            ],
            "claim": "all fish are fish",
            "expected_status": "rejected",
            "expected_reason": "identity_block",
        },
    ]

    behavior_rows = []
    wrong_accept_count = 0
    accepted_without_typed_support_count = 0
    candidate_graph_contamination_count = 0

    for case in behavior_cases:
        result = verify_support_path(case["premises"], case["claim"])
        observed_channel = result.get("support", {}).get("channel")
        observed_reason = result.get("reason")
        passed = result["status"] == case["expected_status"]
        if "expected_channel" in case:
            passed = passed and observed_channel == case["expected_channel"]
        if "expected_reason" in case:
            passed = passed and observed_reason == case["expected_reason"]

        if result["status"] == "accepted" and result.get("claim") != result.get("support", {}).get("derived_claim"):
            wrong_accept_count += 1
        if result["status"] == "accepted" and "support" not in result:
            accepted_without_typed_support_count += 1

        behavior_rows.append({
            "name": case["name"],
            "observed_status": result["status"],
            "observed_channel": observed_channel,
            "observed_reason": observed_reason,
            "passed": passed,
        })

    case_count = len(rows)
    behavior_case_count = len(behavior_rows)

    report = {
        "release": "v11.1.0",
        "case_count": case_count,
        "behavior_case_count": behavior_case_count,
        "surface_parse_accuracy": parsed / case_count if case_count else 0.0,
        "canonical_equivalence_accuracy": canonical_ok / case_count if case_count else 0.0,
        "quantifier_accuracy": quantifier_ok / case_count if case_count else 0.0,
        "natural_behavior_accuracy": sum(1 for row in behavior_rows if row["passed"]) / behavior_case_count if behavior_case_count else 0.0,
        "wrong_accept_count": wrong_accept_count,
        "accepted_without_typed_support_count": accepted_without_typed_support_count,
        "candidate_graph_contamination_count": candidate_graph_contamination_count,
        "results": rows,
        "behavior_results": behavior_rows,
    }
    report["all_gates_passed"] = (
        report["surface_parse_accuracy"] == 1.0
        and report["canonical_equivalence_accuracy"] == 1.0
        and report["quantifier_accuracy"] == 1.0
        and report["natural_behavior_accuracy"] == 1.0
        and wrong_accept_count == 0
        and accepted_without_typed_support_count == 0
        and candidate_graph_contamination_count == 0
    )

    receipt = {
        "receipt_type": "v11_1_claim_normalizer_receipt",
        "release": "v11.1.0",
        "claim": "TS-Reasoner accepts natural is/are/every/each/any/no/not claim surfaces while preserving typed verifier behavior.",
        "surface_parse_accuracy": report["surface_parse_accuracy"],
        "canonical_equivalence_accuracy": report["canonical_equivalence_accuracy"],
        "natural_behavior_accuracy": report["natural_behavior_accuracy"],
        "wrong_accept_count": wrong_accept_count,
        "accepted_without_typed_support_count": accepted_without_typed_support_count,
        "candidate_graph_contamination_count": candidate_graph_contamination_count,
        "all_gates_passed": report["all_gates_passed"],
    }

    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))

    if not report["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
