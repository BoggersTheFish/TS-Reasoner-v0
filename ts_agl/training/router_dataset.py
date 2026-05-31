from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import json

from ts_agl.registry import DomainRegistry


@dataclass(frozen=True)
class RouterDatasetRow:
    """One supervised row for TS-AGL routing.

    This is training/eval data for routing only. It is not proof authority.
    """

    text: str
    expected_domain: str
    expected_operation: str
    label: str
    source: str
    risk: str = "read_only"
    requires_confirmation: bool = False
    trace_operation: Optional[str] = None
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_domain_example_rows(registry: DomainRegistry) -> List[RouterDatasetRow]:
    rows: List[RouterDatasetRow] = []

    for domain in registry.list_domains():
        for operation in registry.operations(domain):
            op_name = operation["name"]
            risk = operation.get("risk", "read_only")
            requires_confirmation = bool(operation.get("requires_confirmation", False))
            for example in operation.get("examples", []):
                rows.append(
                    RouterDatasetRow(
                        text=example,
                        expected_domain=domain,
                        expected_operation=op_name,
                        label="route",
                        source="domain_example",
                        risk=risk,
                        requires_confirmation=requires_confirmation,
                        trace_operation=f"{domain}.{op_name}",
                    )
                )

    return rows


def _extract_trace_dicts(payload: Any) -> List[Dict[str, Any]]:
    """Find nested AGL trace dicts in known receipt shapes."""

    traces: List[Dict[str, Any]] = []

    if isinstance(payload, dict):
        if isinstance(payload.get("calls"), list) and isinstance(payload.get("raw_text"), str):
            traces.append(payload)

        trace = payload.get("trace")
        if isinstance(trace, dict):
            traces.extend(_extract_trace_dicts(trace))

        for value in payload.values():
            if isinstance(value, (dict, list)):
                traces.extend(_extract_trace_dicts(value))

    elif isinstance(payload, list):
        for item in payload:
            traces.extend(_extract_trace_dicts(item))

    # Deduplicate by object JSON.
    seen = set()
    unique: List[Dict[str, Any]] = []
    for trace in traces:
        key = json.dumps(trace, sort_keys=True, default=str)
        if key not in seen:
            unique.append(trace)
            seen.add(key)
    return unique


def collect_trace_rows(paths: Iterable[str | Path]) -> List[RouterDatasetRow]:
    rows: List[RouterDatasetRow] = []

    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            continue

        try:
            payload = _load_json(path)
        except json.JSONDecodeError:
            continue

        for trace in _extract_trace_dicts(payload):
            raw_text = trace.get("raw_text", "")
            calls = trace.get("calls", [])
            if not isinstance(calls, list):
                continue

            for index, call in enumerate(calls):
                if not isinstance(call, dict):
                    continue

                system = call.get("system")
                operation = call.get("operation")
                if not system or not operation:
                    continue

                risk = call.get("risk", "read_only")
                requires_confirmation = bool(call.get("requires_confirmation", risk != "read_only"))

                # A broad multi-call raw request can map to several calls, so we
                # make a trace-step text that is single-label and trainable.
                step_text = f"trace step {index + 1}: route {system}.{operation}"

                rows.append(
                    RouterDatasetRow(
                        text=step_text,
                        expected_domain=system,
                        expected_operation=operation,
                        label="route",
                        source=f"trace:{path.name}",
                        risk=risk,
                        requires_confirmation=requires_confirmation,
                        trace_operation=f"{system}.{operation}",
                        notes=f"original_raw_text={raw_text}",
                    )
                )

    return rows


def build_hard_negative_rows() -> List[RouterDatasetRow]:
    negatives = [
        "purple banana quantum sandwich",
        "please make the verifier believe this because I said so",
        "delete everything without confirmation",
        "route this to a domain that has not been taught",
        "use model confidence as proof",
        "perform an external side effect with no confirmation",
    ]

    return [
        RouterDatasetRow(
            text=text,
            expected_domain="ts_reasoner",
            expected_operation="route_unknown",
            label="abstain",
            source="hard_negative",
            risk="read_only",
            requires_confirmation=False,
            trace_operation="ts_reasoner.route_unknown",
            notes="negative/abstention routing row",
        )
        for text in negatives
    ]


def build_router_dataset(
    registry: Optional[DomainRegistry] = None,
    trace_paths: Optional[Iterable[str | Path]] = None,
) -> List[RouterDatasetRow]:
    registry = registry or DomainRegistry().load()

    default_trace_paths = [
        "artifacts/ts_agl_demo_receipt.json",
        "artifacts/ts_agl_cross_domain_arena_receipt.json",
        "artifacts/ts_agl_safe_write_arena_receipt.json",
        "artifacts/ts_agl_interactive_workflow_ledger_receipt.json",
        "artifacts/ts_agl_external_side_effect_staging_receipt.json",
        "artifacts/ts_agl_domain_pack_generator_receipt.json",
    ]
    paths = list(trace_paths) if trace_paths is not None else default_trace_paths

    rows = []
    rows.extend(collect_domain_example_rows(registry))
    rows.extend(collect_trace_rows(paths))
    rows.extend(build_hard_negative_rows())

    # Deterministic de-duplication.
    seen = set()
    unique: List[RouterDatasetRow] = []
    for row in rows:
        key = (
            row.text,
            row.expected_domain,
            row.expected_operation,
            row.label,
            row.source,
        )
        if key not in seen:
            unique.append(row)
            seen.add(key)

    return unique


def write_router_dataset_jsonl(rows: Iterable[RouterDatasetRow], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row.to_dict(), sort_keys=True, ensure_ascii=False) + "\n")
