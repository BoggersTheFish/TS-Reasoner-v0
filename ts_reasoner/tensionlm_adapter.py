"""Adapter for exported TensionLM-style candidate outputs.

This module does not load model weights. It accepts JSONL rows that look like
real or exported model outputs, normalizes them into the v1.1 candidate bridge
contract, and delegates verification to TS-Reasoner typed channels.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .candidate_bridge import run_tensionlm_candidate_bridge
from .candidates import CandidateClaim


@dataclass(frozen=True)
class TensionLMExportRow:
    row_id: str
    input_text: str
    model: str
    candidates: list[CandidateClaim]
    premises: list[str] | None = None
    raw: dict[str, Any] | None = None


def load_tensionlm_export_jsonl(path: str | Path) -> list[TensionLMExportRow]:
    rows = []
    for index, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        rows.append(parse_tensionlm_export_row(json.loads(line), index))
    return rows


def parse_tensionlm_export_row(row: dict[str, Any], index: int = 1) -> TensionLMExportRow:
    input_text = str(row["input_text"])
    model = str(row.get("model", "unknown_model"))
    row_id = str(row.get("case_id", row.get("row_id", f"export_row_{index}")))
    candidates = [
        normalize_export_candidate(candidate, candidate_index, model, row_id)
        for candidate_index, candidate in enumerate(row.get("candidates", []), start=1)
    ]
    premises = row.get("premises")
    return TensionLMExportRow(
        row_id=row_id,
        input_text=input_text,
        model=model,
        candidates=candidates,
        premises=[str(premise).strip() for premise in premises if str(premise).strip()] if premises else None,
        raw=dict(row),
    )


def normalize_export_candidate(
    candidate: dict[str, Any],
    index: int,
    model: str,
    row_id: str,
) -> CandidateClaim:
    provenance = candidate.get("provenance", "")
    source = str(provenance) if provenance is not None else ""
    raw_text = candidate.get("raw_text", candidate.get("raw_output"))
    return CandidateClaim(
        candidate_id=str(candidate.get("candidate_id", f"{row_id}_candidate_{index}")),
        claim=str(candidate.get("claim", "")),
        source=source,
        confidence=float(candidate.get("confidence", 0.5)),
        raw_output=str(raw_text) if raw_text is not None else None,
        metadata={
            "model": model,
            "adapter": "real_tensionlm_export_jsonl",
            "row_id": row_id,
            "raw_candidate": dict(candidate),
        },
    )


def run_tensionlm_export_row(row: TensionLMExportRow) -> dict[str, Any]:
    payload = run_tensionlm_candidate_bridge(
        row.input_text,
        row.premises,
        mode="external",
        external_hook=lambda _text, _premises: row.candidates,
    )
    payload["adapter"] = {
        "name": "real_tensionlm_export_jsonl",
        "row_id": row.row_id,
        "model": row.model,
        "candidate_count": len(row.candidates),
        "input_format": "jsonl",
    }
    return payload


def run_tensionlm_export_rows(rows: Iterable[TensionLMExportRow]) -> list[dict[str, Any]]:
    return [run_tensionlm_export_row(row) for row in rows]


def run_tensionlm_export_jsonl(path: str | Path) -> list[dict[str, Any]]:
    return run_tensionlm_export_rows(load_tensionlm_export_jsonl(path))
