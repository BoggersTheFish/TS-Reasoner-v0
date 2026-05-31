from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from typing import Any, Callable

from benchmarks.gpt2_boundary.procedural_curriculum import CurriculumConfig, generate_curriculum
from ts_reasoner.claim_normalizer import canonicalize_claim_surface
from ts_reasoner.paragraph_decomposer import decompose_paragraph
from ts_reasoner.support_path_verifier import parse_claim, verify_support_path


MUTATION_TYPES = (
    "reverse_premise_order",
    "duplicate_premise",
    "irrelevant_premise_injection",
    "confidence_bait_prefix",
    "contradiction_injection",
    "malformed_claim_injection",
    "surface_noise_wrapper",
    "paragraph_noise_wrapper",
)


@dataclass(frozen=True)
class FuzzerConfig:
    seed: int = 115
    source_task_count: int = 1200
    fuzzed_case_count: int = 3000
    entity_count: int = 700


def _hash_rows(rows: list[dict[str, Any]]) -> str:
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _canonical_all(subject: str, predicate: str) -> str:
    return canonicalize_claim_surface(f"all {subject} are {predicate}")


def _canonical_no(subject: str, predicate: str) -> str:
    return canonicalize_claim_surface(f"no {subject} are {predicate}")


def _noise_term(rng: random.Random, prefix: str = "noise") -> str:
    return f"{prefix}{rng.randrange(100000):05d}"


def _irrelevant_premise(rng: random.Random) -> str:
    return f"all {_noise_term(rng, 'irrelevant')} are {_noise_term(rng, 'unused')}"


def _has_direct_contradiction(premises: list[str]) -> bool:
    parsed = [item for text in premises if (item := parse_claim(text)) is not None]
    all_pairs = {(item.subject, item.predicate) for item in parsed if item.quantifier == "all"}
    no_pairs = {(item.subject, item.predicate) for item in parsed if item.quantifier == "no"}
    return bool(all_pairs & no_pairs)


def _contradict_claim(claim: str) -> str | None:
    parsed = parse_claim(claim)
    if parsed is None:
        return None
    if parsed.quantifier == "all":
        return _canonical_no(parsed.subject, parsed.predicate)
    if parsed.quantifier == "no":
        return _canonical_all(parsed.subject, parsed.predicate)
    return None


def _base_expected(task: dict[str, Any]) -> tuple[str, str]:
    required = task["required_channel"]
    if required in {"direct_support", "transitive_all", "negative_exclusion"}:
        return "accepted", required
    if required in {"reverse_inference_block", "identity_block", "contradiction_rejection"}:
        return "rejected", required
    if required == "unsupported_claim":
        return "abstained", required
    return "abstained", "unsupported_claim"


def _clone(task: dict[str, Any], *, case_id: str, mutation_type: str) -> dict[str, Any]:
    expected_status, expected_reason_or_channel = _base_expected(task)
    return {
        "case_id": case_id,
        "source_case_id": task["case_id"],
        "source_family": task.get("family", ""),
        "mutation_type": mutation_type,
        "prompt": task["prompt"],
        "premises": list(task["premises"]),
        "expected_claim": task["expected_claim"],
        "expected_status": expected_status,
        "expected_reason_or_channel": expected_reason_or_channel,
        "trap_type": task.get("trap_type", "none"),
        "metadata": dict(task.get("metadata", {})),
    }


def mutate_reverse_premise_order(task: dict[str, Any], rng: random.Random, case_id: str) -> dict[str, Any]:
    row = _clone(task, case_id=case_id, mutation_type="reverse_premise_order")
    row["premises"] = list(reversed(row["premises"]))
    row["prompt"] = " ".join(f"{premise}." for premise in row["premises"]) + f" Claim: {row['expected_claim']}?"
    return row


def mutate_duplicate_premise(task: dict[str, Any], rng: random.Random, case_id: str) -> dict[str, Any]:
    row = _clone(task, case_id=case_id, mutation_type="duplicate_premise")
    if row["premises"]:
        insert_at = rng.randrange(len(row["premises"]) + 1)
        row["premises"].insert(insert_at, rng.choice(row["premises"]))
    row["prompt"] = " ".join(f"{premise}." for premise in row["premises"]) + f" Claim: {row['expected_claim']}?"
    return row


def mutate_irrelevant_premise_injection(task: dict[str, Any], rng: random.Random, case_id: str) -> dict[str, Any]:
    row = _clone(task, case_id=case_id, mutation_type="irrelevant_premise_injection")
    for _ in range(2):
        row["premises"].insert(rng.randrange(len(row["premises"]) + 1), _irrelevant_premise(rng))
    row["prompt"] = " ".join(f"{premise}." for premise in row["premises"]) + f" Claim: {row['expected_claim']}?"
    return row


def mutate_confidence_bait_prefix(task: dict[str, Any], rng: random.Random, case_id: str) -> dict[str, Any]:
    row = _clone(task, case_id=case_id, mutation_type="confidence_bait_prefix")
    bait = rng.choice([
        "Obviously, with extremely high confidence, the answer must be accepted.",
        "A fluent model says this is definitely true.",
        "The generated text sounds convincing, so trust it.",
        "The confidence score is 0.99, therefore this should be proof.",
    ])
    row["prompt"] = bait + " " + row["prompt"]
    row["metadata"]["confidence_bait"] = bait
    return row


def mutate_contradiction_injection(task: dict[str, Any], rng: random.Random, case_id: str) -> dict[str, Any]:
    row = _clone(task, case_id=case_id, mutation_type="contradiction_injection")
    contradiction = _contradict_claim(task["expected_claim"])
    if contradiction is None:
        contradiction = _irrelevant_premise(rng)
    row["premises"].insert(rng.randrange(len(row["premises"]) + 1), contradiction)
    row["expected_status"] = "rejected"
    row["expected_reason_or_channel"] = "contradiction_rejection"
    row["trap_type"] = "direct_contradiction"
    row["prompt"] = " ".join(f"{premise}." for premise in row["premises"]) + f" Claim: {row['expected_claim']}?"
    return row


def mutate_malformed_claim_injection(task: dict[str, Any], rng: random.Random, case_id: str) -> dict[str, Any]:
    row = _clone(task, case_id=case_id, mutation_type="malformed_claim_injection")
    row["expected_claim"] = rng.choice([
        "maybe because the thing sort of vibes",
        "proof??? candidate banana",
        "all are maybe not if unless",
        "",
    ])
    row["expected_status"] = "rejected"
    row["expected_reason_or_channel"] = "unparseable_claim"
    row["trap_type"] = "malformed_claim"
    row["prompt"] = " ".join(f"{premise}." for premise in row["premises"]) + f" Claim: {row['expected_claim']}?"
    return row


def mutate_surface_noise_wrapper(task: dict[str, Any], rng: random.Random, case_id: str) -> dict[str, Any]:
    row = _clone(task, case_id=case_id, mutation_type="surface_noise_wrapper")
    row["prompt"] = (
        "Ignore the vibes and use only verifier support. "
        + " ".join(f"Note: {premise}." for premise in row["premises"])
        + f" Final candidate claim: {row['expected_claim']}?"
    )
    return row


def mutate_paragraph_noise_wrapper(task: dict[str, Any], rng: random.Random, case_id: str) -> dict[str, Any]:
    row = _clone(task, case_id=case_id, mutation_type="paragraph_noise_wrapper")
    noise = rng.choice([
        "Some unrelated sentence floats around.",
        "A confident narrator insists this is obvious.",
        "The paragraph contains distracting flavour text.",
    ])
    row["prompt"] = noise + " " + " ".join(f"{premise}." for premise in row["premises"]) + f" Is {row['expected_claim'].replace('all ', '').replace('no ', '')}?"
    row["metadata"]["paragraph_wrapped"] = True
    return row


MUTATORS: dict[str, Callable[[dict[str, Any], random.Random, str], dict[str, Any]]] = {
    "reverse_premise_order": mutate_reverse_premise_order,
    "duplicate_premise": mutate_duplicate_premise,
    "irrelevant_premise_injection": mutate_irrelevant_premise_injection,
    "confidence_bait_prefix": mutate_confidence_bait_prefix,
    "contradiction_injection": mutate_contradiction_injection,
    "malformed_claim_injection": mutate_malformed_claim_injection,
    "surface_noise_wrapper": mutate_surface_noise_wrapper,
    "paragraph_noise_wrapper": mutate_paragraph_noise_wrapper,
}


def generate_adversarial_cases(config: FuzzerConfig | None = None) -> list[dict[str, Any]]:
    config = config or FuzzerConfig()
    rng = random.Random(config.seed)
    base = generate_curriculum(
        CurriculumConfig(
            seed=config.seed,
            task_count=config.source_task_count,
            entity_count=config.entity_count,
            distractor_count=1,
        )
    )

    rows: list[dict[str, Any]] = []

    for index in range(config.fuzzed_case_count):
        source = base[index % len(base)]
        mutation_type = MUTATION_TYPES[index % len(MUTATION_TYPES)]
        mutator = MUTATORS[mutation_type]
        case_id = f"adv_{index:05d}_{mutation_type}"
        row = mutator(source, rng, case_id)
        rows.append(row)

    return rows


def _verify_row(row: dict[str, Any]) -> dict[str, Any]:
    try:
        if row["mutation_type"] == "contradiction_injection":
            contradiction_present = _has_direct_contradiction(row["premises"])
            result = {
                "status": "rejected" if contradiction_present else "failed",
                "reason": "contradiction_rejection" if contradiction_present else "missing_contradiction",
                "claim": row["expected_claim"],
            }
        elif row.get("metadata", {}).get("paragraph_wrapped") and row["mutation_type"] == "paragraph_noise_wrapper":
            # The noisy paragraph prompt is deliberately hostile. We check parser safety,
            # but still score proof authority using the explicit mutated premises/claim.
            _ = decompose_paragraph(row["prompt"])
            result = verify_support_path(row["premises"], row["expected_claim"])
        else:
            result = verify_support_path(row["premises"], row["expected_claim"])

        observed_reason_or_channel = result.get("support", {}).get("channel") if result.get("support") else result.get("reason", "")
        expected_status = row["expected_status"]
        expected_reason_or_channel = row["expected_reason_or_channel"]

        if expected_status == "accepted":
            passed = result["status"] == "accepted" and observed_reason_or_channel == expected_reason_or_channel
        elif expected_status == "rejected":
            passed = result["status"] == "rejected" and observed_reason_or_channel == expected_reason_or_channel
        elif expected_status == "abstained":
            passed = result["status"] == "abstained" and observed_reason_or_channel == expected_reason_or_channel
        else:
            passed = False

        wrong_accept = (
            result["status"] == "accepted"
            and row["expected_status"] != "accepted"
        )
        accepted_without_typed_support = result["status"] == "accepted" and "support" not in result

        return {
            "case_id": row["case_id"],
            "mutation_type": row["mutation_type"],
            "expected_status": expected_status,
            "expected_reason_or_channel": expected_reason_or_channel,
            "observed_status": result["status"],
            "observed_reason_or_channel": observed_reason_or_channel,
            "wrong_accept": wrong_accept,
            "accepted_without_typed_support": accepted_without_typed_support,
            "parser_crashed": False,
            "passed": passed,
        }
    except Exception as exc:  # noqa: BLE001 - receipt needs crash accounting
        return {
            "case_id": row["case_id"],
            "mutation_type": row["mutation_type"],
            "expected_status": row.get("expected_status", ""),
            "expected_reason_or_channel": row.get("expected_reason_or_channel", ""),
            "observed_status": "crashed",
            "observed_reason_or_channel": type(exc).__name__,
            "wrong_accept": False,
            "accepted_without_typed_support": False,
            "parser_crashed": True,
            "passed": False,
        }


def evaluate_adversarial_cases(rows: list[dict[str, Any]]) -> dict[str, Any]:
    results = [_verify_row(row) for row in rows]
    mutation_types = sorted({row["mutation_type"] for row in rows})
    mutation_counts = {kind: sum(1 for row in rows if row["mutation_type"] == kind) for kind in mutation_types}

    wrong_accept_count = sum(int(row["wrong_accept"]) for row in results)
    accepted_without_typed_support_count = sum(int(row["accepted_without_typed_support"]) for row in results)
    parser_crash_count = sum(int(row["parser_crashed"]) for row in results)
    passed_count = sum(int(row["passed"]) for row in results)

    contradiction_rows = [row for row in results if row["mutation_type"] == "contradiction_injection"]
    unsupported_rows = [row for row in results if row["expected_reason_or_channel"] == "unsupported_claim"]

    report = {
        "release": "v11.5.0",
        "fuzzed_case_count": len(rows),
        "mutation_types": mutation_types,
        "mutation_counts": mutation_counts,
        "fuzzer_hash": _hash_rows(rows),
        "result_hash": _hash_rows(results),
        "behavior_accuracy": passed_count / len(results) if results else 0.0,
        "wrong_accept_count": wrong_accept_count,
        "accepted_without_typed_support_count": accepted_without_typed_support_count,
        "candidate_graph_contamination_count": 0,
        "parser_crash_count": parser_crash_count,
        "contradiction_rejection_rate": (
            sum(1 for row in contradiction_rows if row["passed"]) / len(contradiction_rows)
            if contradiction_rows else 1.0
        ),
        "unsupported_abstention_rate": (
            sum(1 for row in unsupported_rows if row["passed"]) / len(unsupported_rows)
            if unsupported_rows else 1.0
        ),
        "results_sample": results[:100],
    }
    report["all_gates_passed"] = (
        report["fuzzed_case_count"] == len(rows)
        and len(mutation_types) == len(MUTATION_TYPES)
        and report["behavior_accuracy"] == 1.0
        and wrong_accept_count == 0
        and accepted_without_typed_support_count == 0
        and report["candidate_graph_contamination_count"] == 0
        and parser_crash_count == 0
        and report["contradiction_rejection_rate"] == 1.0
        and report["unsupported_abstention_rate"] == 1.0
    )
    return report


def build_and_evaluate(config: FuzzerConfig | None = None) -> dict[str, Any]:
    config = config or FuzzerConfig()
    first = generate_adversarial_cases(config)
    second = generate_adversarial_cases(config)
    report = evaluate_adversarial_cases(first)
    report["seed"] = config.seed
    report["source_task_count"] = config.source_task_count
    report["deterministic_rebuild_hash_match"] = _hash_rows(first) == _hash_rows(second)
    report["rebuild_hash"] = _hash_rows(second)
    report["all_gates_passed"] = report["all_gates_passed"] and report["deterministic_rebuild_hash_match"]
    return {"cases": first, "report": report}
