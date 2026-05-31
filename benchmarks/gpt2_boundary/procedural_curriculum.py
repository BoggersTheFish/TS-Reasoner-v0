from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from typing import Any, Iterable

from benchmarks.gpt2_boundary.run_ts_reasoner_arena import run_ts_reasoner_arena
from ts_reasoner.claim_normalizer import canonicalize_claim_surface
from ts_reasoner.paragraph_decomposer import decompose_paragraph
from ts_reasoner.support_path_verifier import parse_claim, verify_support_path


TASK_FAMILIES = (
    "direct_support",
    "transitive_2",
    "transitive_3",
    "transitive_5",
    "negative_exclusion",
    "reverse_inference_trap",
    "identity_trap",
    "unsupported_target",
    "direct_contradiction",
    "paragraph_transitive",
    "paragraph_unsupported",
    "paragraph_reverse",
)

SURFACE_FORMS = (
    "all_are",
    "every_is",
    "belongs_to",
    "counts_as",
    "kind_of",
    "type_of",
)


@dataclass(frozen=True)
class CurriculumConfig:
    seed: int = 114
    task_count: int = 5000
    entity_count: int = 700
    distractor_count: int = 1


def _term(index: int) -> str:
    return f"class{index:04d}"


def _surface_all(subject: str, predicate: str, variant: str) -> str:
    if variant == "all_are":
        return f"all {subject} are {predicate}"
    if variant == "every_is":
        return f"every {subject} is {predicate}"
    if variant == "belongs_to":
        return f"{subject} belongs to {predicate}"
    if variant == "counts_as":
        return f"{subject} counts as {predicate}"
    if variant == "kind_of":
        return f"{subject} is a kind of {predicate}"
    if variant == "type_of":
        return f"{subject} is a type of {predicate}"
    raise ValueError(f"unknown surface variant: {variant}")


def _surface_no(subject: str, predicate: str, variant: str) -> str:
    if variant in {"all_are", "every_is", "belongs_to"}:
        return f"no {subject} are {predicate}"
    if variant == "counts_as":
        return f"{subject} cannot be {predicate}"
    if variant == "kind_of":
        return f"{subject} excludes {predicate}"
    if variant == "type_of":
        return f"{subject} can not be {predicate}"
    raise ValueError(f"unknown surface variant: {variant}")


def _question_for_claim(claim: str) -> str:
    parsed = parse_claim(claim)
    if parsed is None:
        return f"Can this be proven: {claim}?"
    if parsed.quantifier == "all":
        return f"Are all {parsed.subject} {parsed.predicate}?"
    if parsed.quantifier == "no":
        return f"Are {parsed.subject} not {parsed.predicate}?"
    return f"Can this be proven: {claim}?"


def _prompt(premises: Iterable[str], claim: str, *, paragraph: bool = False) -> str:
    premises = list(premises)
    if paragraph:
        return ". ".join(premises) + ". " + _question_for_claim(claim)
    return " ".join(f"{premise}." for premise in premises) + " " + _question_for_claim(claim)


def _canonical_all(subject: str, predicate: str) -> str:
    return canonicalize_claim_surface(f"all {subject} are {predicate}")


def _canonical_no(subject: str, predicate: str) -> str:
    return canonicalize_claim_surface(f"no {subject} are {predicate}")


def _make_task(
    *,
    case_id: str,
    family: str,
    premises: list[str],
    expected_claim: str,
    required_channel: str,
    expected_answer: str,
    trap_type: str,
    paragraph: bool = False,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "family": family,
        "prompt": _prompt(premises, expected_claim, paragraph=paragraph),
        "expected_answer": expected_answer,
        "expected_claim": expected_claim,
        "premises": premises,
        "required_channel": required_channel,
        "trap_type": trap_type,
        "metadata": metadata or {},
    }


def _choose_chain(rng: random.Random, config: CurriculumConfig, depth: int) -> list[str]:
    start = rng.randrange(0, config.entity_count - depth - 10)
    # stride avoids accidental repeated local terms.
    stride = rng.randrange(1, 5)
    nodes = [_term(start + i * stride) for i in range(depth + 1)]
    if len(set(nodes)) != len(nodes):
        return _choose_chain(rng, config, depth)
    return nodes


def _distractors(rng: random.Random, config: CurriculumConfig, count: int, variant: str) -> list[str]:
    rows = []
    for _ in range(count):
        a, b = rng.sample(range(config.entity_count), 2)
        rows.append(_surface_all(_term(a), _term(b), variant))
    return rows


def _direct_support(index: int, rng: random.Random, config: CurriculumConfig) -> dict[str, Any]:
    a, b = _choose_chain(rng, config, 1)
    variant = rng.choice(SURFACE_FORMS)
    premise = _surface_all(a, b, variant)
    claim = _canonical_all(a, b)
    premises = [premise, *_distractors(rng, config, config.distractor_count, rng.choice(SURFACE_FORMS))]
    return _make_task(
        case_id=f"proc_{index:05d}_direct_support",
        family="direct_support",
        premises=premises,
        expected_claim=claim,
        required_channel="direct_support",
        expected_answer="yes",
        trap_type="none",
        metadata={"surface_variant": variant},
    )


def _transitive(index: int, rng: random.Random, config: CurriculumConfig, depth: int) -> dict[str, Any]:
    nodes = _choose_chain(rng, config, depth)
    variants = [rng.choice(SURFACE_FORMS) for _ in range(depth)]
    premises = [
        _surface_all(nodes[i], nodes[i + 1], variants[i])
        for i in range(depth)
    ]
    premises += _distractors(rng, config, config.distractor_count, rng.choice(SURFACE_FORMS))
    claim = _canonical_all(nodes[0], nodes[-1])
    return _make_task(
        case_id=f"proc_{index:05d}_transitive_{depth}",
        family=f"transitive_{depth}",
        premises=premises,
        expected_claim=claim,
        required_channel="transitive_all",
        expected_answer="yes",
        trap_type="none",
        metadata={"depth": depth, "surface_variants": variants},
    )


def _negative_exclusion(index: int, rng: random.Random, config: CurriculumConfig) -> dict[str, Any]:
    a, b, c = _choose_chain(rng, config, 2)
    v1 = rng.choice(SURFACE_FORMS)
    v2 = rng.choice(SURFACE_FORMS)
    premises = [
        _surface_all(a, b, v1),
        _surface_no(b, c, v2),
        *_distractors(rng, config, config.distractor_count, rng.choice(SURFACE_FORMS)),
    ]
    claim = _canonical_no(a, c)
    return _make_task(
        case_id=f"proc_{index:05d}_negative_exclusion",
        family="negative_exclusion",
        premises=premises,
        expected_claim=claim,
        required_channel="negative_exclusion",
        expected_answer="yes",
        trap_type="none",
        metadata={"surface_variants": [v1, v2]},
    )


def _reverse_inference(index: int, rng: random.Random, config: CurriculumConfig) -> dict[str, Any]:
    a, b = _choose_chain(rng, config, 1)
    variant = rng.choice(SURFACE_FORMS)
    premises = [_surface_all(a, b, variant)]
    claim = _canonical_all(b, a)
    return _make_task(
        case_id=f"proc_{index:05d}_reverse_inference",
        family="reverse_inference_trap",
        premises=premises,
        expected_claim=claim,
        required_channel="reverse_inference_block",
        expected_answer="no",
        trap_type="reverse_inference",
        metadata={"surface_variant": variant},
    )


def _identity(index: int, rng: random.Random, config: CurriculumConfig) -> dict[str, Any]:
    a = _term(rng.randrange(config.entity_count))
    variant = rng.choice(("all_are", "every_is"))
    premises = [_surface_all(a, a, variant)]
    claim = _canonical_all(a, a)
    return _make_task(
        case_id=f"proc_{index:05d}_identity",
        family="identity_trap",
        premises=premises,
        expected_claim=claim,
        required_channel="identity_block",
        expected_answer="no",
        trap_type="identity",
        metadata={"surface_variant": variant},
    )


def _unsupported(index: int, rng: random.Random, config: CurriculumConfig) -> dict[str, Any]:
    a, b, c = _choose_chain(rng, config, 2)
    variant = rng.choice(SURFACE_FORMS)
    premises = [_surface_all(a, b, variant)]
    claim = _canonical_all(a, c)
    return _make_task(
        case_id=f"proc_{index:05d}_unsupported",
        family="unsupported_target",
        premises=premises,
        expected_claim=claim,
        required_channel="unsupported_claim",
        expected_answer="abstain",
        trap_type="unsupported",
        metadata={"surface_variant": variant},
    )


def _direct_contradiction(index: int, rng: random.Random, config: CurriculumConfig) -> dict[str, Any]:
    a, b = _choose_chain(rng, config, 1)
    v1 = rng.choice(SURFACE_FORMS)
    v2 = rng.choice(SURFACE_FORMS)
    premises = [
        _surface_all(a, b, v1),
        _surface_no(a, b, v2),
    ]
    claim = _canonical_all(a, b)
    return _make_task(
        case_id=f"proc_{index:05d}_direct_contradiction",
        family="direct_contradiction",
        premises=premises,
        expected_claim=claim,
        required_channel="contradiction_rejection",
        expected_answer="no",
        trap_type="direct_contradiction",
        metadata={"surface_variants": [v1, v2]},
    )


def _paragraph_transitive(index: int, rng: random.Random, config: CurriculumConfig) -> dict[str, Any]:
    task = _transitive(index, rng, config, depth=2)
    task["family"] = "paragraph_transitive"
    task["case_id"] = f"proc_{index:05d}_paragraph_transitive"
    task["prompt"] = _prompt(task["premises"], task["expected_claim"], paragraph=True)
    task["metadata"]["paragraph_wrapped"] = True
    return task


def _paragraph_unsupported(index: int, rng: random.Random, config: CurriculumConfig) -> dict[str, Any]:
    task = _unsupported(index, rng, config)
    task["family"] = "paragraph_unsupported"
    task["case_id"] = f"proc_{index:05d}_paragraph_unsupported"
    task["prompt"] = _prompt(task["premises"], task["expected_claim"], paragraph=True)
    task["metadata"]["paragraph_wrapped"] = True
    return task


def _paragraph_reverse(index: int, rng: random.Random, config: CurriculumConfig) -> dict[str, Any]:
    task = _reverse_inference(index, rng, config)
    task["family"] = "paragraph_reverse"
    task["case_id"] = f"proc_{index:05d}_paragraph_reverse"
    task["prompt"] = _prompt(task["premises"], task["expected_claim"], paragraph=True)
    task["metadata"]["paragraph_wrapped"] = True
    return task


BUILDERS = {
    "direct_support": _direct_support,
    "transitive_2": lambda i, r, c: _transitive(i, r, c, depth=2),
    "transitive_3": lambda i, r, c: _transitive(i, r, c, depth=3),
    "transitive_5": lambda i, r, c: _transitive(i, r, c, depth=5),
    "negative_exclusion": _negative_exclusion,
    "reverse_inference_trap": _reverse_inference,
    "identity_trap": _identity,
    "unsupported_target": _unsupported,
    "direct_contradiction": _direct_contradiction,
    "paragraph_transitive": _paragraph_transitive,
    "paragraph_unsupported": _paragraph_unsupported,
    "paragraph_reverse": _paragraph_reverse,
}


def generate_curriculum(config: CurriculumConfig | None = None) -> list[dict[str, Any]]:
    config = config or CurriculumConfig()
    rng = random.Random(config.seed)
    tasks: list[dict[str, Any]] = []
    seen_prompts: set[str] = set()
    attempts = 0

    while len(tasks) < config.task_count:
        family = TASK_FAMILIES[len(tasks) % len(TASK_FAMILIES)]
        builder = BUILDERS[family]
        task = builder(len(tasks), rng, config)
        attempts += 1

        # Avoid prompt duplicates while keeping deterministic build.
        if task["prompt"] in seen_prompts:
            if attempts > config.task_count * 20:
                raise RuntimeError("too many duplicate procedural curriculum prompts")
            continue

        seen_prompts.add(task["prompt"])
        tasks.append(task)

    return tasks


def curriculum_hash(tasks: list[dict[str, Any]]) -> str:
    payload = json.dumps(tasks, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _has_direct_contradiction(premises: list[str]) -> bool:
    parsed = [item for text in premises if (item := parse_claim(text)) is not None]
    all_pairs = {(item.subject, item.predicate) for item in parsed if item.quantifier == "all"}
    no_pairs = {(item.subject, item.predicate) for item in parsed if item.quantifier == "no"}
    return bool(all_pairs & no_pairs)


def validate_task_label(task: dict[str, Any]) -> dict[str, Any]:
    required = task["required_channel"]

    if required == "contradiction_rejection":
        passed = _has_direct_contradiction(list(task["premises"]))
        return {
            "case_id": task["case_id"],
            "family": task["family"],
            "expected_channel": required,
            "observed_status": "rejected" if passed else "failed",
            "observed_channel": "contradiction_rejection" if passed else "",
            "passed": passed,
        }

    if task["family"].startswith("paragraph_"):
        decomposed = decompose_paragraph(task["prompt"])
        result = verify_support_path(decomposed["premises"], decomposed["candidate_claim"]) if decomposed["status"] == "parsed" else {
            "status": "abstained",
            "reason": decomposed["reason"],
        }
    else:
        result = verify_support_path(task["premises"], task["expected_claim"])

    observed_channel = result.get("support", {}).get("channel") if result.get("support") else result.get("reason")

    if required in {"direct_support", "transitive_all", "negative_exclusion"}:
        passed = result["status"] == "accepted" and observed_channel == required
    elif required in {"reverse_inference_block", "identity_block"}:
        passed = result["status"] == "rejected" and observed_channel == required
    elif required == "unsupported_claim":
        passed = result["status"] == "abstained" and observed_channel == "unsupported_claim"
    else:
        passed = False

    return {
        "case_id": task["case_id"],
        "family": task["family"],
        "expected_channel": required,
        "observed_status": result["status"],
        "observed_channel": observed_channel,
        "passed": passed,
    }


def validate_curriculum(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    validations = [validate_task_label(task) for task in tasks]
    prompts = [task["prompt"] for task in tasks]
    families = sorted({task["family"] for task in tasks})
    channels = sorted({task["required_channel"] for task in tasks})
    traps = sorted({task["trap_type"] for task in tasks})

    duplicate_task_count = len(prompts) - len(set(prompts))
    label_valid_count = sum(1 for row in validations if row["passed"])

    arena_sample = [
        task for task in tasks
        if task["required_channel"] in {"contradiction_rejection", "unsupported_claim", "transitive_all", "direct_support", "negative_exclusion"}
    ][:120]
    arena_rows = run_ts_reasoner_arena(arena_sample)
    arena_contamination = sum(row["candidate_graph_contamination_count"] for row in arena_rows)
    arena_accepted_without_typed = sum(int(row["accepted_without_typed_support"]) for row in arena_rows)

    return {
        "task_count": len(tasks),
        "duplicate_task_count": duplicate_task_count,
        "duplicate_task_rate": duplicate_task_count / len(tasks) if tasks else 0.0,
        "label_validity": label_valid_count / len(tasks) if tasks else 0.0,
        "families": families,
        "channels": channels,
        "traps": traps,
        "family_coverage": len(families) / len(TASK_FAMILIES),
        "channel_coverage": len(channels),
        "trap_coverage": len(traps),
        "curriculum_hash": curriculum_hash(tasks),
        "arena_sample_count": len(arena_sample),
        "arena_candidate_graph_contamination_count": arena_contamination,
        "arena_accepted_without_typed_support_count": arena_accepted_without_typed,
        "validations_sample": validations[:50],
    }


def build_and_validate(config: CurriculumConfig | None = None) -> dict[str, Any]:
    config = config or CurriculumConfig()
    first = generate_curriculum(config)
    second = generate_curriculum(config)
    first_hash = curriculum_hash(first)
    second_hash = curriculum_hash(second)
    report = validate_curriculum(first)
    report.update({
        "release": "v11.4.0",
        "seed": config.seed,
        "entity_count": config.entity_count,
        "distractor_count": config.distractor_count,
        "deterministic_rebuild_hash_match": first_hash == second_hash,
        "rebuild_hash": second_hash,
    })
    report["all_gates_passed"] = (
        report["task_count"] == config.task_count
        and report["duplicate_task_count"] == 0
        and report["label_validity"] == 1.0
        and report["family_coverage"] == 1.0
        and report["trap_coverage"] >= 4
        and report["deterministic_rebuild_hash_match"]
        and report["arena_candidate_graph_contamination_count"] == 0
        and report["arena_accepted_without_typed_support_count"] == 0
    )
    return {"tasks": first, "report": report}
