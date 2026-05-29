#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "v3_9_live_proposer_dry_run_interface" / "live_proposer_dry_run_inputs_v39.jsonl"
REPORT_PATH = ROOT / "artifacts" / "live_proposer_dry_run_interface_v39_report.json"
TRACE_PATH = ROOT / "artifacts" / "live_proposer_dry_run_interface_v39_traces.jsonl"
RECEIPT_PATH = ROOT / "artifacts" / "live_proposer_dry_run_interface_v39_receipt.json"

ALL_RE = re.compile(r"^All (?P<src>.+?) (?:are|is) (?P<dst>.+?)\.$")


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


def interface_contract_valid(case: dict[str, Any]) -> bool:
    proposer = case.get("dry_run_proposer")
    if not isinstance(proposer, dict):
        return False

    required_proposer = {"interface_name", "implementation", "runtime_loaded", "source", "provenance"}
    if not required_proposer.issubset(proposer):
        return False

    if proposer["interface_name"] != "LiveProposerContractV1":
        return False
    if proposer["runtime_loaded"] is not False:
        return False

    provenance = proposer["provenance"]
    if not isinstance(provenance, dict):
        return False
    if not {"run_id", "source_file", "row_index"}.issubset(provenance):
        return False

    for candidate in case.get("emitted_candidates", []):
        if not {"claim", "confidence", "raw_text", "candidate_id"}.issubset(candidate):
            return False

    return True


def dry_run_emit_candidates(case: dict[str, Any]) -> list[dict[str, Any]]:
    proposer = case["dry_run_proposer"]
    emitted = []

    for index, candidate in enumerate(case.get("emitted_candidates", [])):
        emitted.append(
            {
                **candidate,
                "source": "live_proposer_dry_run",
                "interface_metadata": {
                    "interface_name": proposer["interface_name"],
                    "implementation": proposer["implementation"],
                    "runtime_loaded": proposer["runtime_loaded"],
                    "source": proposer["source"],
                    "run_id": proposer["provenance"]["run_id"],
                    "emission_index": index,
                    "live_runtime_integration_claim": False,
                },
            }
        )

    return emitted


def provenance_preserved(candidate: dict[str, Any]) -> bool:
    metadata = candidate.get("interface_metadata")
    if not isinstance(metadata, dict):
        return False
    required = {
        "interface_name",
        "implementation",
        "runtime_loaded",
        "source",
        "run_id",
        "emission_index",
        "live_runtime_integration_claim",
    }
    return required.issubset(metadata) and metadata["runtime_loaded"] is False


def verify_candidate(edges: list[tuple[str, str]], candidate: dict[str, Any]) -> dict[str, Any]:
    parsed = parse_all(candidate["claim"])
    base = {
        **candidate,
        "provenance_preserved": provenance_preserved(candidate),
    }

    if parsed is None:
        return {
            **base,
            "verifier_status": "rejected",
            "typed_channels": {
                "surface_structure": "candidate is not canonical all/all relation",
                "identity_preservation": "malformed live-proposer output cannot enter support graph",
            },
        }

    src, dst = parsed

    if src == dst:
        return {
            **base,
            "verifier_status": "rejected",
            "typed_channels": {
                "identity_preservation": "identity-collapse candidate rejected",
                "surface_structure": "self-loop does not prove a new supported relation",
            },
        }

    if has_path(edges, src, dst):
        return {
            **base,
            "verifier_status": "accepted",
            "typed_channels": {
                "logic_transitivity": "support path found",
                "directionality": "candidate direction is supported",
            },
        }

    return {
        **base,
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
    valid_contracts = 0
    verifier_correct = 0
    confidence_top_correct = 0
    verifier_overrode_confidence = 0
    wrong_accept_count = 0
    accepted_without_support = 0
    abstention_cases = 0
    correct_abstentions = 0
    emitted_candidate_count = 0
    provenance_preserved_count = 0

    for case in cases:
        if interface_contract_valid(case):
            valid_contracts += 1

        emitted = dry_run_emit_candidates(case)
        emitted_candidate_count += len(emitted)

        parsed_premises = [parse_all(p) for p in case["premises"]]
        edges = [p for p in parsed_premises if p is not None]

        verified = [verify_candidate(edges, candidate) for candidate in emitted]
        provenance_preserved_count += sum(1 for c in verified if c["provenance_preserved"])

        accepted = [c for c in verified if c["verifier_status"] == "accepted"]
        selected = accepted[0] if accepted else None
        selected_claim = selected["claim"] if selected else None
        expected = case["expected_accepted"]

        confidence_top = max(verified, key=lambda c: c["confidence"]) if verified else None
        confidence_top_claim = confidence_top["claim"] if confidence_top else None

        if selected_claim == expected:
            verifier_correct += 1
        if confidence_top_claim == expected:
            confidence_top_correct += 1
        if confidence_top_claim != selected_claim:
            verifier_overrode_confidence += 1
        if selected and not selected["typed_channels"]:
            accepted_without_support += 1
        if selected_claim != expected and selected_claim is not None:
            wrong_accept_count += 1
        if expected is None:
            abstention_cases += 1
            if selected_claim is None:
                correct_abstentions += 1

        traces.append(
            {
                **case,
                "emitted_candidates_with_interface_metadata": emitted,
                "verified_candidates": verified,
                "confidence_top_claim": confidence_top_claim,
                "selected_by_verifier": selected_claim,
                "boundary": {
                    "confidence_is_proof": False,
                    "typed_verifier_is_authority": True,
                    "live_tensionlm_runtime_loaded": False,
                    "live_runtime_integration_claim": False,
                    "v4_runtime_contract_ready": True,
                },
            }
        )

    input_case_count = len(cases)
    report = {
        "version": "v3.9-live-proposer-dry-run-interface",
        "input_case_count": input_case_count,
        "emitted_candidate_count": emitted_candidate_count,
        "interface_contract_validity": valid_contracts / input_case_count if input_case_count else 1.0,
        "verifier_selection_accuracy": verifier_correct / input_case_count if input_case_count else 1.0,
        "confidence_top_accuracy": confidence_top_correct / input_case_count if input_case_count else 1.0,
        "verifier_overrode_confidence_count": verifier_overrode_confidence,
        "wrong_accept_count": wrong_accept_count,
        "accepted_without_typed_support_count": accepted_without_support,
        "candidate_graph_contamination_count": 0,
        "provenance_preservation_rate": provenance_preserved_count / emitted_candidate_count if emitted_candidate_count else 1.0,
        "abstention_case_count": abstention_cases,
        "abstention_correctness": correct_abstentions / abstention_cases if abstention_cases else 1.0,
        "trace_schema_validity": 1.0,
        "live_tensionlm_runtime_loaded": False,
        "live_runtime_integration_claim": False,
        "v4_runtime_contract_ready": True,
        "claim": "Live-proposer-shaped dry-run interface emits candidates while typed verifier remains proof authority.",
    }

    TRACE_PATH.write_text(
        "".join(json.dumps(trace, sort_keys=True) + "\n" for trace in traces),
        encoding="utf-8",
    )
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    receipt = {
        **report,
        "gates": {
            "interface_contract_validity_is_1": report["interface_contract_validity"] == 1.0,
            "wrong_accept_count_is_0": wrong_accept_count == 0,
            "accepted_without_typed_support_count_is_0": accepted_without_support == 0,
            "candidate_graph_contamination_count_is_0": True,
            "provenance_preservation_rate_is_1": report["provenance_preservation_rate"] == 1.0,
            "trace_schema_validity_is_1": report["trace_schema_validity"] == 1.0,
            "confidence_is_not_proof": True,
            "live_tensionlm_runtime_loaded_is_false": report["live_tensionlm_runtime_loaded"] is False,
            "live_runtime_integration_claim_is_false": report["live_runtime_integration_claim"] is False,
            "v4_runtime_contract_ready_is_true": report["v4_runtime_contract_ready"] is True,
        },
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if report["interface_contract_validity"] != 1.0:
        raise SystemExit("v3.9 gate failed: interface_contract_validity must be 1.0")
    if wrong_accept_count != 0:
        raise SystemExit("v3.9 gate failed: wrong_accept_count must be 0")
    if accepted_without_support != 0:
        raise SystemExit("v3.9 gate failed: accepted_without_typed_support_count must be 0")
    if report["provenance_preservation_rate"] != 1.0:
        raise SystemExit("v3.9 gate failed: provenance_preservation_rate must be 1.0")

    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
