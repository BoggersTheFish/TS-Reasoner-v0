from __future__ import annotations

import importlib.util
import os
import re
from dataclasses import asdict, dataclass
from typing import Any

from benchmarks.gpt2_boundary.procedural_curriculum import CurriculumConfig, generate_curriculum
from benchmarks.gpt2_boundary.run_ts_reasoner_arena import run_ts_reasoner_arena


YES_RE = re.compile(r"\b(yes|true|accepted|valid|supported)\b", re.IGNORECASE)
NO_RE = re.compile(r"\b(no|false|rejected|invalid|unsupported|not supported)\b", re.IGNORECASE)


@dataclass(frozen=True)
class LiveGPT2Config:
    model_name: str = "gpt2"
    task_count: int = 48
    seed: int = 116
    max_new_tokens: int = 24
    temperature: float = 0.0
    run_live: bool = False


@dataclass(frozen=True)
class DependencyStatus:
    transformers_available: bool
    torch_available: bool
    live_requested: bool
    live_available: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def dependency_status(run_live: bool | None = None) -> DependencyStatus:
    if run_live is None:
        run_live = os.environ.get("TS_REASONER_RUN_LIVE_GPT2") == "1"

    transformers_available = importlib.util.find_spec("transformers") is not None
    torch_available = importlib.util.find_spec("torch") is not None
    live_available = bool(run_live and transformers_available and torch_available)

    if not run_live:
        reason = "live_gpt2_not_requested"
    elif not transformers_available:
        reason = "missing_transformers"
    elif not torch_available:
        reason = "missing_torch"
    else:
        reason = "live_gpt2_available"

    return DependencyStatus(
        transformers_available=transformers_available,
        torch_available=torch_available,
        live_requested=bool(run_live),
        live_available=live_available,
        reason=reason,
    )


def build_boundary_tasks(task_count: int = 48, seed: int = 116) -> list[dict[str, Any]]:
    tasks = generate_curriculum(
        CurriculumConfig(
            seed=seed,
            task_count=max(task_count * 2, 120),
            entity_count=240,
            distractor_count=1,
        )
    )

    # Keep the adapter comparison focused on answerable verifier-boundary tasks.
    allowed = {
        "direct_support",
        "transitive_2",
        "transitive_3",
        "negative_exclusion",
        "reverse_inference_trap",
        "unsupported_target",
        "direct_contradiction",
        "paragraph_transitive",
        "paragraph_unsupported",
        "paragraph_reverse",
    }
    filtered = [task for task in tasks if task.get("family") in allowed]
    return filtered[:task_count]


def prompt_for_gpt2(task: dict[str, Any]) -> str:
    return (
        "Answer the reasoning question with only one token: yes, no, or abstain.\n"
        f"Question: {task['prompt']}\n"
        "Answer:"
    )


def classify_completion(text: str) -> str:
    lowered = text.lower()
    if "abstain" in lowered or "unknown" in lowered or "cannot determine" in lowered:
        return "abstain"
    if NO_RE.search(lowered):
        return "no"
    if YES_RE.search(lowered):
        return "yes"
    return "unclassified"


def expected_answer(task: dict[str, Any]) -> str:
    raw = str(task.get("expected_answer", "")).strip().lower()
    if raw in {"yes", "no", "abstain"}:
        return raw

    channel = task.get("required_channel", "")
    if channel in {"direct_support", "transitive_all", "negative_exclusion"}:
        return "yes"
    if channel in {"reverse_inference_block", "identity_block", "contradiction_rejection"}:
        return "no"
    if channel == "unsupported_claim":
        return "abstain"
    return "abstain"


def run_contract_baseline(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    ts_rows = run_ts_reasoner_arena(tasks)
    wrong_accept_count = 0
    accepted_without_typed_support_count = 0
    contamination_count = 0

    for row in ts_rows:
        result = row["ts_reasoner_result"]
        if result["status"] == "accepted" and expected_answer(row["task"]) != "yes":
            wrong_accept_count += 1
        accepted_without_typed_support_count += int(row["accepted_without_typed_support"])
        contamination_count += int(row["candidate_graph_contamination_count"])

    return {
        "ts_reasoner_task_count": len(ts_rows),
        "ts_reasoner_wrong_accept_count": wrong_accept_count,
        "ts_reasoner_accepted_without_typed_support_count": accepted_without_typed_support_count,
        "ts_reasoner_candidate_graph_contamination_count": contamination_count,
    }


def run_live_gpt2(tasks: list[dict[str, Any]], config: LiveGPT2Config) -> dict[str, Any]:
    status = dependency_status(config.run_live)
    if not status.live_available:
        return {
            "live_gpt2_available": False,
            "live_gpt2_generation_completed_rate": 0.0,
            "live_gpt2_answer_accuracy": None,
            "live_gpt2_rows": [],
            "dependency_status": status.to_dict(),
        }

    # Import only inside the live path so CI and stdlib users are not forced
    # to install transformers/torch.
    import torch  # type: ignore
    from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore

    tokenizer = AutoTokenizer.from_pretrained(config.model_name)
    model = AutoModelForCausalLM.from_pretrained(config.model_name)
    model.eval()

    rows = []
    correct = 0

    for task in tasks:
        prompt = prompt_for_gpt2(task)
        encoded = tokenizer(prompt, return_tensors="pt")
        with torch.no_grad():
            if config.temperature <= 0:
                output = model.generate(
                    **encoded,
                    max_new_tokens=config.max_new_tokens,
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id,
                )
            else:
                output = model.generate(
                    **encoded,
                    max_new_tokens=config.max_new_tokens,
                    do_sample=True,
                    temperature=config.temperature,
                    pad_token_id=tokenizer.eos_token_id,
                )

        decoded = tokenizer.decode(output[0], skip_special_tokens=True)
        completion = decoded[len(prompt):].strip()
        observed = classify_completion(completion)
        expected = expected_answer(task)
        is_correct = observed == expected
        correct += int(is_correct)

        rows.append({
            "case_id": task["case_id"],
            "expected_answer": expected,
            "observed_answer": observed,
            "completion": completion[:240],
            "correct": is_correct,
        })

    return {
        "live_gpt2_available": True,
        "live_gpt2_generation_completed_rate": 1.0,
        "live_gpt2_answer_accuracy": correct / len(tasks) if tasks else 0.0,
        "live_gpt2_rows": rows,
        "dependency_status": status.to_dict(),
    }


def evaluate_live_gpt2_adapter(config: LiveGPT2Config | None = None) -> dict[str, Any]:
    config = config or LiveGPT2Config(
        run_live=os.environ.get("TS_REASONER_RUN_LIVE_GPT2") == "1"
    )
    tasks = build_boundary_tasks(task_count=config.task_count, seed=config.seed)
    status = dependency_status(config.run_live)
    contract = run_contract_baseline(tasks)
    live = run_live_gpt2(tasks, config)

    adapter_contract_passed = (
        len(tasks) == config.task_count
        and contract["ts_reasoner_wrong_accept_count"] == 0
        and contract["ts_reasoner_accepted_without_typed_support_count"] == 0
        and contract["ts_reasoner_candidate_graph_contamination_count"] == 0
    )

    live_gate_passed = True
    if status.live_requested:
        live_gate_passed = bool(live["live_gpt2_available"] and live["live_gpt2_generation_completed_rate"] == 1.0)

    report = {
        "release": "v11.6.0",
        "claim": "Optional live GPT-2-small adapter for verifier-first boundary comparison.",
        "model_name": config.model_name,
        "task_count": len(tasks),
        "adapter_contract_passed": adapter_contract_passed,
        "dependency_status": status.to_dict(),
        **contract,
        **live,
    }
    report["all_gates_passed"] = bool(adapter_contract_passed and live_gate_passed)
    return report
