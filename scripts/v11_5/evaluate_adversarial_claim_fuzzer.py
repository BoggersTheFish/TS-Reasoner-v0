from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.gpt2_boundary.adversarial_fuzzer import FuzzerConfig, build_and_evaluate

CONFIG = ROOT / "data" / "v11_5" / "adversarial_fuzzer_config.json"
CASES = ROOT / "artifacts" / "v11_5" / "adversarial_fuzzer_cases.jsonl"
REPORT = ROOT / "artifacts" / "v11_5" / "adversarial_fuzzer_report.json"
RECEIPT = ROOT / "artifacts" / "v11_5" / "adversarial_fuzzer_receipt.json"


def main() -> None:
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    config = FuzzerConfig(**payload)
    built = build_and_evaluate(config)
    cases = built["cases"]
    report = built["report"]

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    CASES.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in cases) + "\n",
        encoding="utf-8",
    )
    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    receipt = {
        "receipt_type": "v11_5_adversarial_claim_fuzzer_receipt",
        "release": "v11.5.0",
        "claim": "TS-Reasoner adversarially mutates verifier-first reasoning tasks while preserving zero wrong accepts and zero parser crashes.",
        "fuzzed_case_count": report["fuzzed_case_count"],
        "mutation_types": report["mutation_types"],
        "behavior_accuracy": report["behavior_accuracy"],
        "wrong_accept_count": report["wrong_accept_count"],
        "accepted_without_typed_support_count": report["accepted_without_typed_support_count"],
        "candidate_graph_contamination_count": report["candidate_graph_contamination_count"],
        "parser_crash_count": report["parser_crash_count"],
        "contradiction_rejection_rate": report["contradiction_rejection_rate"],
        "unsupported_abstention_rate": report["unsupported_abstention_rate"],
        "deterministic_rebuild_hash_match": report["deterministic_rebuild_hash_match"],
        "fuzzer_hash": report["fuzzer_hash"],
        "all_gates_passed": report["all_gates_passed"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))

    if not report["all_gates_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
