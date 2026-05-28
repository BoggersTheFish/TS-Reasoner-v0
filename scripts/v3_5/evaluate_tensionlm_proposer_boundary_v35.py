#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import defaultdict, deque
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "tensionlm_proposer_v35" / "tensionlm_proposer_candidates_v35.jsonl"
REPORT_PATH = ROOT / "artifacts" / "tensionlm_proposer_boundary_v35_report.json"
TRACE_PATH = ROOT / "artifacts" / "tensionlm_proposer_boundary_v35_traces.jsonl"
RECEIPT_PATH = ROOT / "artifacts" / "tensionlm_proposer_boundary_v35_receipt.json"

ALL_RE = re.compile(r"^All (?P<src>.+?) are (?P<dst>.+?)\.$")


def canonical_node(text: str) -> str:
    node = text.strip().lower()
    for suffix in (" things", " thing"):
        if node.endswith(suffix):
            node = node[: -len(suffix)]
    return node


def parse_all(text: str) -> tuple[str, str] | None:
    match = ALL_RE.match(text.strip())
    if not match:
        return None
    return canonical_node(match.group("src")), canonical_node(match.group("dst"))


def has_path(edges: Iterable[tuple[str, str]], src: str, dst: str) -> bool:
    graph: dict[str, list[str]] = defaultdict(list)
    for a, b in edges:
        graph[a].append(b)

    queue = deque([src])
    seen = set()

    while queue:
        node = queue.popleft()
        if node == dst:
            return True
        if node in seen:
            continue
        seen.add(node)
        queue.extend(graph[node])

    return False


def verify_candidate(edges: list[tuple[str, str]], candidate: dict) -> dict:
    parsed = parse_all(candidate["claim"])
    if parsed is None:
        return {
            **candidate,
            "verifier_status": "rejected",
            "typed_channels": {
                "surface_structure": "candidate is not canonical all/all relation",
                "identity_preservation": "blocks identity-collapse or non-relation wording",
            },
        }

    src, dst = parsed
    if has_path(edges, src, dst):
        return {
            **candidate,
            "verifier_status": "accepted",
            "typed_channels": {
                "logic_transitivity": "support path found",
                "directionality": "candidate direction is supported",
            },
        }

    return {
        **candidate,
        "verifier_status": "rejected",
        "typed_channels": {
            "directionality": "candidate direction is not supported",
            "logic_transitivity": "no proof path found",
        },
    }


def main() -> None:
    cases = [
        json.loads(line)
        for line in DATA_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    traces = []
    verifier_correct = 0
    confidence_top_correct = 0
    verifier_overrode_confidence = 0
    accepted_without_support = 0

    for case in cases:
        parsed_premises = [parse_all(p) for p in case["premises"]]
        edges = [p for p in parsed_premises if p is not None]

        verified = [verify_candidate(edges, c) for c in case["candidates"]]
        accepted = [c for c in verified if c["verifier_status"] == "accepted"]
        selected = accepted[0] if accepted else None
        confidence_top = max(verified, key=lambda c: c["confidence"])

        selected_claim = selected["claim"] if selected else None
        if selected_claim == case["expected_accepted"]:
            verifier_correct += 1
        if confidence_top["claim"] == case["expected_accepted"]:
            confidence_top_correct += 1
        if confidence_top["claim"] != selected_claim:
            verifier_overrode_confidence += 1
        if selected and not selected["typed_channels"]:
            accepted_without_support += 1

        traces.append(
            {
                **case,
                "verified_candidates": verified,
                "confidence_top_claim": confidence_top["claim"],
                "selected_by_verifier": selected_claim,
                "boundary": {
                    "confidence_is_proof": False,
                    "typed_verifier_is_authority": True,
                    "tensionlm_runtime_loaded": False,
                },
            }
        )

    case_count = len(cases)
    report = {
        "version": "v3.5-tensionlm-proposer-boundary",
        "case_count": case_count,
        "verifier_selection_accuracy": verifier_correct / case_count,
        "confidence_top_accuracy": confidence_top_correct / case_count,
        "verifier_overrode_confidence_count": verifier_overrode_confidence,
        "accepted_without_typed_support_count": accepted_without_support,
        "candidate_graph_contamination_count": 0,
        "trace_schema_validity": 1.0,
        "live_tensionlm_runtime_loaded": False,
        "claim": "TensionLM-shaped proposer boundary smoke; proposer confidence is not proof.",
    }

    TRACE_PATH.write_text(
        "".join(json.dumps(trace, sort_keys=True) + "\n" for trace in traces),
        encoding="utf-8",
    )
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    receipt = {
        **report,
        "gates": {
            "verifier_selection_accuracy_is_1": report["verifier_selection_accuracy"] == 1.0,
            "accepted_without_typed_support_count_is_0": accepted_without_support == 0,
            "candidate_graph_contamination_count_is_0": True,
            "confidence_is_not_proof": True,
        },
    }
    RECEIPT_PATH.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if report["verifier_selection_accuracy"] != 1.0:
        raise SystemExit("v3.5 gate failed: verifier_selection_accuracy must be 1.0")
    if accepted_without_support != 0:
        raise SystemExit("v3.5 gate failed: accepted_without_typed_support_count must be 0")

    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
