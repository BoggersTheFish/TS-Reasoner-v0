#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "data" / "v4_2_gpt2_output_fixture_adapter" / "gpt2_output_fixtures_v42.jsonl"
OUTPUT = ROOT / "data" / "v4_2_gpt2_output_fixture_adapter" / "adapted_gpt2_external_backend_candidates_v42.jsonl"
REPORT = ROOT / "artifacts" / "gpt2_output_fixture_adapter_v42_report.json"
RECEIPT = ROOT / "artifacts" / "gpt2_output_fixture_adapter_v42_receipt.json"


def main() -> None:
    rows = [
        json.loads(line)
        for line in INPUT.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    adapted = []
    for row in rows:
        adapted.append(
            {
                "sandbox_case_id": row["sandbox_case_id"],
                "claim": row["candidate_claim"],
                "confidence": row["score"],
                "raw_text": row["generated_text"],
                "candidate_id": row["candidate_id"],
                "gpt2_fixture_metadata": {
                    "fixture_id": row["fixture_id"],
                    "source_model": row["source_model"],
                    "prompt": row["prompt"],
                    "score_is_proof": False,
                    "generated_text_is_proof": False,
                    "gpt2_comparison_claim": False,
                },
            }
        )

    OUTPUT.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in adapted),
        encoding="utf-8",
    )

    report = {
        "version": "v4.2-gpt2-output-fixture-adapter",
        "gpt2_fixture_case_count": len(rows),
        "adapted_candidate_count": len(adapted),
        "adapter_success_rate": 1.0 if len(rows) == len(adapted) else 0.0,
        "source_model": "gpt2_fixture",
        "output_path": str(OUTPUT.relative_to(ROOT)),
        "gpt2_comparison_claim": False,
        "confidence_is_not_proof": True,
        "generated_text_is_not_proof": True,
        "claim": "GPT-2-style generated outputs are adapted into external JSONL candidate rows without granting model fluency or score proof authority.",
    }

    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    receipt = {
        **report,
        "gates": {
            "adapter_success_rate_is_1": report["adapter_success_rate"] == 1.0,
            "gpt2_comparison_claim_is_false": report["gpt2_comparison_claim"] is False,
            "confidence_is_not_proof": report["confidence_is_not_proof"] is True,
            "generated_text_is_not_proof": report["generated_text_is_not_proof"] is True,
            "adapted_candidate_count_matches_fixture_count": len(rows) == len(adapted),
        },
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
