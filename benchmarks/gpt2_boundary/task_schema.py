from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from ts_reasoner.support_path_verifier import parse_claim
from ts_reasoner.runtime_kernel import normalize_claim


REQUIRED_FIELDS = (
    "case_id",
    "prompt",
    "expected_answer",
    "expected_claim",
    "premises",
    "required_channel",
    "trap_type",
)

ALLOWED_ANSWERS = {"yes", "no", "unknown"}
ALLOWED_CHANNELS = {
    "direct_support",
    "transitive_all",
    "negative_exclusion",
    "reverse_inference_block",
    "unsupported_claim",
    "contradiction_rejection",
}


@dataclass(frozen=True)
class BoundaryTask:
    case_id: str
    prompt: str
    expected_answer: str
    expected_claim: str
    premises: tuple[str, ...]
    required_channel: str
    trap_type: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "prompt": self.prompt,
            "expected_answer": self.expected_answer,
            "expected_claim": normalize_claim(self.expected_claim),
            "premises": [normalize_claim(item) for item in self.premises],
            "required_channel": self.required_channel,
            "trap_type": self.trap_type,
        }


def validate_task(task: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_FIELDS if field not in task]
    if missing:
        return {"valid": False, "reason": "missing_fields", "missing": missing}
    if str(task["expected_answer"]) not in ALLOWED_ANSWERS:
        return {"valid": False, "reason": "bad_expected_answer"}
    if str(task["required_channel"]) not in ALLOWED_CHANNELS:
        return {"valid": False, "reason": "bad_required_channel"}
    if not isinstance(task["premises"], list) or not all(isinstance(item, str) and item.strip() for item in task["premises"]):
        return {"valid": False, "reason": "bad_premises"}
    if parse_claim(str(task["expected_claim"])) is None:
        return {"valid": False, "reason": "expected_claim_parse_failed"}
    if not str(task["case_id"]).strip() or not str(task["prompt"]).strip():
        return {"valid": False, "reason": "empty_identity_or_prompt"}
    return {"valid": True, "reason": "schema_valid"}


def evaluate_task_schema(tasks: Iterable[dict[str, Any]]) -> dict[str, Any]:
    task_list = list(tasks)
    rows = []
    for task in task_list:
        result = validate_task(task)
        rows.append({"case_id": task.get("case_id"), **result})

    trap_types = {str(task["trap_type"]) for task in task_list}
    required_channels = {str(task["required_channel"]) for task in task_list}
    expected_traps = {
        "none",
        "reverse_inference",
        "unsupported_claim",
        "contradiction",
        "messy_wrapper",
        "irrelevant_confidence",
        "fluent_unsupported",
    }
    expected_channels = ALLOWED_CHANNELS
    valid_count = sum(1 for row in rows if row["valid"])
    parse_count = sum(1 for task in task_list if parse_claim(str(task.get("expected_claim", ""))) is not None)
    report = {
        "release": "v10.8.0",
        "task_count": len(task_list),
        "schema_validity": valid_count / len(task_list) if task_list else 0.0,
        "expected_claim_parse_rate": parse_count / len(task_list) if task_list else 0.0,
        "trap_label_coverage": len(expected_traps & trap_types) / len(expected_traps),
        "required_channel_coverage": len(expected_channels & required_channels) / len(expected_channels),
        "results": rows,
    }
    report["all_gates_passed"] = (
        report["task_count"] == 100
        and report["schema_validity"] == 1.0
        and report["expected_claim_parse_rate"] == 1.0
        and report["trap_label_coverage"] == 1.0
        and report["required_channel_coverage"] == 1.0
    )
    return report
