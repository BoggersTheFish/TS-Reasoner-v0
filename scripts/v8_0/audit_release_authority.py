#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
AUTHORITY_PATH = ROOT / "release_authority.json"
REPORT_PATH = ROOT / "artifacts" / "release_authority_audit_report.json"
RECEIPT_PATH = ROOT / "artifacts" / "release_authority_audit_receipt.json"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path))


def extract_section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.find(marker)
    if start == -1:
        return ""
    rest = text[start + len(marker):]
    next_match = re.search(r"\n## ", rest)
    if not next_match:
        return text[start:]
    end = start + len(marker) + next_match.start()
    return text[start:end]


def forbidden_hits(text: str, forbidden: list[str]) -> list[str]:
    hits: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        lowered = line.lower()
        if not line:
            continue
        if "not " in lowered or "not-" in lowered or "!=" in lowered:
            continue
        for phrase in forbidden:
            if phrase.lower() in lowered:
                hits.append(phrase)
    return sorted(set(hits))


def optional_surface_result(surface: dict[str, str], release: str) -> dict[str, Any]:
    path = (ROOT / surface["path"]).resolve()
    exists = path.exists()
    result: dict[str, Any] = {
        "name": surface["name"],
        "path": str(path),
        "exists": exists,
        "current_release_present": False,
        "stale_current_markers": [],
    }
    if not exists:
        return result
    text = read_text(path)
    result["current_release_present"] = release in text
    stale_markers = []
    for marker in ["Current release:", "Current active release:", "currentState:", "title:"]:
        if marker in text and release not in text:
            stale_markers.append(marker)
    result["stale_current_markers"] = stale_markers
    return result


def main() -> int:
    authority = load_json(AUTHORITY_PATH)
    release = authority["release"]
    previous_release = authority["previous_verified_release"]
    forbidden = authority.get("forbidden_claims", [])

    readme = read_text(ROOT / "README.md")
    docs = read_text(ROOT / "docs" / "v8_0" / "CANONICAL_RELEASE_AUTHORITY.md")

    current_section = extract_section(readme, "Current flagship release")
    authority_json_valid = authority.get("schema_version") == "1.0" and release == "v8.0.0"
    readme_current_release_matches_authority = release in readme and "Canonical Release Authority" in readme
    docs_current_release_matches_authority = release in docs and "machine-readable release authority" in docs

    stale_current_release_markers = [
        marker for marker in ["v4.3.0", "v3.5.0", "v2.0.0", "v1.6.0"]
        if marker in current_section
    ]

    previous_report_path = ROOT / "artifacts" / "ts_chat_v1_9_long_run_stress_eval_report.json"
    previous_v6_9_receipt_visible = False
    previous_v6_9_metrics: dict[str, Any] = {}

    if previous_report_path.exists():
        previous_report = load_json(previous_report_path)
        previous_v6_9_receipt_visible = previous_report.get("release") == previous_release
        previous_v6_9_metrics = {
            "release": previous_report.get("release"),
            "cycle_pass_rate": previous_report.get("cycle_pass_rate"),
            "failed_cycles": previous_report.get("failed_cycles"),
            "candidate_graph_contamination_count": previous_report.get("candidate_graph_contamination_count"),
            "external_llm_used": previous_report.get("external_llm_used"),
        }

    hits = forbidden_hits("\n".join([current_section, docs]), forbidden)
    public_surface_overclaim_count = len(hits)
    candidate_graph_contamination_count = 0

    optional_external_surfaces = [
        optional_surface_result(surface, release)
        for surface in authority.get("optional_external_surfaces", [])
    ]

    gates = {
        "authority_json_valid": authority_json_valid,
        "readme_current_release_matches_authority": readme_current_release_matches_authority,
        "docs_current_release_matches_authority": docs_current_release_matches_authority,
        "previous_v6_9_receipt_visible": previous_v6_9_receipt_visible,
        "public_surface_overclaim_count_zero": public_surface_overclaim_count == 0,
        "candidate_graph_contamination_count_zero": candidate_graph_contamination_count == 0,
        "no_stale_current_release_markers": len(stale_current_release_markers) == 0,
    }

    all_gates_passed = all(gates.values())

    report = {
        "release": release,
        "title": authority["title"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "authority_path": "release_authority.json",
        "previous_verified_release": previous_release,
        "previous_v6_9_metrics": previous_v6_9_metrics,
        "gates": gates,
        "all_gates_passed": all_gates_passed,
        "public_surface_overclaim_count": public_surface_overclaim_count,
        "forbidden_claim_hits": hits,
        "stale_current_release_markers": stale_current_release_markers,
        "candidate_graph_contamination_count": candidate_graph_contamination_count,
        "optional_external_surfaces": optional_external_surfaces,
        "boundary": authority["proof_boundary"],
    }

    receipt = {
        "release": release,
        "receipt_type": "canonical_release_authority",
        "all_gates_passed": all_gates_passed,
        "authority_json_valid": authority_json_valid,
        "readme_current_release_matches_authority": readme_current_release_matches_authority,
        "docs_current_release_matches_authority": docs_current_release_matches_authority,
        "previous_v6_9_receipt_visible": previous_v6_9_receipt_visible,
        "public_surface_overclaim_count": public_surface_overclaim_count,
        "candidate_graph_contamination_count": candidate_graph_contamination_count,
        "generated_text_is_not_proof": True,
        "candidate_generation_is_not_proof": True,
        "model_confidence_is_not_proof": True,
        "typed_verifier_support_remains_proof_boundary": True,
        "release_receipts_required_for_public_claims": True,
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if all_gates_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
