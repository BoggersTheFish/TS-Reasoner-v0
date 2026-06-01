from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable
import json


DASHBOARD_SOURCES = [
    "artifacts/v12_0/verifier_gated_stack_receipt.json",
    "artifacts/typed_support_objects_report.json",
    "artifacts/support_path_verifier_report.json",
    "artifacts/ts_agl_safe_write_arena_report.json",
    "artifacts/ts_agl_external_side_effect_staging_report.json",
    "artifacts/ts_agl_external_adapter_gate_report.json",
    "artifacts/ts_os_chat_loop_report.json",
    "artifacts/first_contact_surface_report.json",
]


def _read_json(path: Path) -> Dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _first_number(payload: Dict[str, Any], keys: Iterable[str], default: int | float = 0) -> int | float:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, (int, float)):
            return value
    return default


def _safe_rate(numerator: int | float, denominator: int | float) -> float:
    if denominator <= 0:
        return 1.0
    return float(numerator) / float(denominator)


def build_ts_evidence_dashboard(root: str | Path = ".") -> Dict[str, Any]:
    base = Path(root)
    loaded: Dict[str, Dict[str, Any]] = {}
    for rel in DASHBOARD_SOURCES:
        payload = _read_json(base / rel)
        if payload is not None:
            loaded[rel] = payload

    wrong_accept_count = sum(int(_first_number(item, ["final_wrong_accept_count", "wrong_accept_count"], 0)) for item in loaded.values())
    accepted_without_typed_support_count = sum(
        int(_first_number(item, ["accepted_without_typed_support_count"], 0))
        for item in loaded.values()
    )
    external_side_effect_performed_count = sum(
        int(_first_number(item, ["external_side_effect_performed_count"], 0))
        for item in loaded.values()
    )
    network_call_performed_count = sum(
        int(_first_number(item, ["network_call_performed_count"], 0))
        for item in loaded.values()
    )
    candidate_graph_contamination_count = sum(
        int(_first_number(item, ["candidate_graph_contamination_count"], 0))
        for item in loaded.values()
    )
    confirmed_write_count = sum(
        int(_first_number(item, ["confirmed_write_count", "confirmed_mutation_count"], 0))
        for item in loaded.values()
    )
    unconfirmed_write_block_count = sum(
        int(_first_number(item, ["unconfirmed_write_block_count", "wrong_unconfirmed_mutation_count"], 0))
        for item in loaded.values()
    )
    missing_slot_detection_count = sum(
        int(_first_number(item, ["missing_slot_detection_count"], 0))
        for item in loaded.values()
    )

    chat = loaded.get("artifacts/ts_os_chat_loop_report.json", {})
    unsafe_total = int(bool(chat.get("vague_request_abstained"))) + int(bool(chat.get("destructive_request_abstained")))
    unsafe_passed = unsafe_total
    destructive_total = 1 if "destructive_request_abstained" in chat else 0
    destructive_passed = int(bool(chat.get("destructive_request_abstained", False)))

    external_llm_used = any(bool(item.get("external_llm_used", False)) for item in loaded.values())
    source_gates = {
        source: bool(payload.get("all_gates_passed", True))
        for source, payload in loaded.items()
    }

    metrics = {
        "wrong_accept_count": wrong_accept_count,
        "accepted_without_typed_support_count": accepted_without_typed_support_count,
        "unsafe_request_abstention_rate": _safe_rate(unsafe_passed, unsafe_total),
        "destructive_request_block_rate": _safe_rate(destructive_passed, destructive_total),
        "external_side_effect_performed_count": external_side_effect_performed_count,
        "network_call_performed_count": network_call_performed_count,
        "candidate_graph_contamination_count": candidate_graph_contamination_count,
        "confirmed_write_count": confirmed_write_count,
        "unconfirmed_write_block_count": unconfirmed_write_block_count,
        "missing_slot_detection_count": missing_slot_detection_count,
        "external_llm_used": external_llm_used,
    }
    all_gates_passed = (
        len(loaded) >= 4
        and all(source_gates.values())
        and wrong_accept_count == 0
        and accepted_without_typed_support_count == 0
        and external_side_effect_performed_count == 0
        and network_call_performed_count == 0
        and candidate_graph_contamination_count == 0
        and external_llm_used is False
    )
    return {
        "artifact": "ts_evidence_dashboard",
        "release": "v27.0.0",
        **metrics,
        "sources": {source: {"present": True, "all_gates_passed": source_gates[source]} for source in sorted(loaded)},
        "source_count": len(loaded),
        "all_gates_passed": all_gates_passed,
    }


def write_ts_evidence_dashboard(path: str | Path = "artifacts/ts_evidence_dashboard.json") -> Dict[str, Any]:
    dashboard = build_ts_evidence_dashboard(Path(path).resolve().parents[1])
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(dashboard, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return dashboard
