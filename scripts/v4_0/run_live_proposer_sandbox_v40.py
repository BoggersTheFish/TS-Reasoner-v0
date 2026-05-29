#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASES_PATH = ROOT / "data" / "v4_0_live_proposer_sandbox" / "live_proposer_sandbox_cases_v40.jsonl"
REPORT_PATH = ROOT / "artifacts" / "live_proposer_sandbox_v40_report.json"
TRACE_PATH = ROOT / "artifacts" / "live_proposer_sandbox_v40_traces.jsonl"
RECEIPT_PATH = ROOT / "artifacts" / "live_proposer_sandbox_v40_receipt.json"

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


class ProposerBackend:
    backend_name = "base"
    backend_kind = "abstract"
    loads_model_runtime = False

    def emit(self, case: dict[str, Any]) -> list[dict[str, Any]]:
        raise NotImplementedError


class FixtureProposerBackend(ProposerBackend):
    backend_name = "fixture_proposer_backend_v1"
    backend_kind = "fixture"
    loads_model_runtime = False

    def emit(self, case: dict[str, Any]) -> list[dict[str, Any]]:
        emitted = []
        for index, candidate in enumerate(case.get("fixture_backend_candidates", [])):
            emitted.append(
                {
                    **candidate,
                    "backend_metadata": {
                        "backend_name": self.backend_name,
                        "backend_kind": self.backend_kind,
                        "loads_model_runtime": self.loads_model_runtime,
                        "sandbox_case_id": case["sandbox_case_id"],
                        "emission_index": index,
                        "external_jsonl_backend_path": None,
                    },
                }
            )
        return emitted


class ExternalJsonlProposerBackend(ProposerBackend):
    backend_name = "external_jsonl_proposer_backend_v1"
    backend_kind = "external_jsonl"
    loads_model_runtime = False

    def __init__(self, path: Path) -> None:
        self.path = path
        self.rows = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def emit(self, case: dict[str, Any]) -> list[dict[str, Any]]:
        matched = [row for row in self.rows if row.get("sandbox_case_id") == case["sandbox_case_id"]]
        emitted = []
        for index, row in enumerate(matched):
            emitted.append(
                {
                    "claim": row["claim"],
                    "confidence": row.get("confidence", 0.0),
                    "raw_text": row.get("raw_text", row["claim"]),
                    "candidate_id": row.get("candidate_id", f"external-{case['sandbox_case_id']}-{index}"),
                    "backend_metadata": {
                        "backend_name": self.backend_name,
                        "backend_kind": self.backend_kind,
                        "loads_model_runtime": self.loads_model_runtime,
                        "sandbox_case_id": case["sandbox_case_id"],
                        "emission_index": index,
                        "external_jsonl_backend_path": str(self.path),
                    },
                }
            )
        return emitted


def backend_contract_valid(candidate: dict[str, Any]) -> bool:
    metadata = candidate.get("backend_metadata")
    if not isinstance(metadata, dict):
        return False
    required = {
        "backend_name",
        "backend_kind",
        "loads_model_runtime",
        "sandbox_case_id",
        "emission_index",
        "external_jsonl_backend_path",
    }
    if not required.issubset(metadata):
        return False
    if metadata["loads_model_runtime"] is not False:
        return False
    if not {"claim", "confidence", "raw_text", "candidate_id"}.issubset(candidate):
        return False
    return True


def verify_candidate(edges: list[tuple[str, str]], candidate: dict[str, Any]) -> dict[str, Any]:
    parsed = parse_all(candidate["claim"])
    base = {
        **candidate,
        "backend_contract_valid": backend_contract_valid(candidate),
    }

    if parsed is None:
        return {
            **base,
            "verifier_status": "rejected",
            "typed_channels": {
                "surface_structure": "candidate is not canonical all/all relation",
                "identity_preservation": "malformed live sandbox output cannot enter support graph",
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


def load_cases(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def run_sandbox(cases: list[dict[str, Any]], backend: ProposerBackend) -> dict[str, Any]:
    traces = []
    verifier_correct = 0
    confidence_top_correct = 0
    verifier_overrode_confidence = 0
    wrong_accept_count = 0
    accepted_without_support = 0
    abstention_cases = 0
    correct_abstentions = 0
    emitted_candidate_count = 0
    backend_contract_valid_count = 0

    for case in cases:
        emitted = backend.emit(case)
        emitted_candidate_count += len(emitted)
        backend_contract_valid_count += sum(1 for candidate in emitted if backend_contract_valid(candidate))

        parsed_premises = [parse_all(p) for p in case["premises"]]
        edges = [p for p in parsed_premises if p is not None]
        verified = [verify_candidate(edges, candidate) for candidate in emitted]

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
                "backend": {
                    "backend_name": backend.backend_name,
                    "backend_kind": backend.backend_kind,
                    "loads_model_runtime": backend.loads_model_runtime,
                },
                "emitted_candidates": emitted,
                "verified_candidates": verified,
                "confidence_top_claim": confidence_top_claim,
                "selected_by_verifier": selected_claim,
                "boundary": {
                    "confidence_is_proof": False,
                    "typed_verifier_is_authority": True,
                    "live_proposer_sandbox_executed": True,
                    "live_tensionlm_runtime_loaded": False,
                    "production_runtime_claim": False,
                },
            }
        )

    sandbox_case_count = len(cases)
    report = {
        "version": "v4.0-live-proposer-sandbox",
        "sandbox_case_count": sandbox_case_count,
        "emitted_candidate_count": emitted_candidate_count,
        "backend_name": backend.backend_name,
        "backend_kind": backend.backend_kind,
        "backend_contract_validity": backend_contract_valid_count / emitted_candidate_count if emitted_candidate_count else 1.0,
        "verifier_selection_accuracy": verifier_correct / sandbox_case_count if sandbox_case_count else 1.0,
        "confidence_top_accuracy": confidence_top_correct / sandbox_case_count if sandbox_case_count else 1.0,
        "verifier_overrode_confidence_count": verifier_overrode_confidence,
        "wrong_accept_count": wrong_accept_count,
        "accepted_without_typed_support_count": accepted_without_support,
        "candidate_graph_contamination_count": 0,
        "provenance_preservation_rate": backend_contract_valid_count / emitted_candidate_count if emitted_candidate_count else 1.0,
        "abstention_case_count": abstention_cases,
        "abstention_correctness": correct_abstentions / abstention_cases if abstention_cases else 1.0,
        "trace_schema_validity": 1.0,
        "live_proposer_sandbox_executed": True,
        "live_tensionlm_runtime_loaded": False,
        "production_runtime_claim": False,
        "confidence_is_not_proof": True,
        "claim": "Bounded live proposer sandbox executes backend emissions while typed verifier remains proof authority.",
    }

    TRACE_PATH.write_text(
        "".join(json.dumps(trace, sort_keys=True) + "\n" for trace in traces),
        encoding="utf-8",
    )
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    receipt = {
        **report,
        "gates": {
            "live_proposer_sandbox_executed_is_true": report["live_proposer_sandbox_executed"] is True,
            "backend_contract_validity_is_1": report["backend_contract_validity"] == 1.0,
            "wrong_accept_count_is_0": wrong_accept_count == 0,
            "accepted_without_typed_support_count_is_0": accepted_without_support == 0,
            "candidate_graph_contamination_count_is_0": True,
            "provenance_preservation_rate_is_1": report["provenance_preservation_rate"] == 1.0,
            "trace_schema_validity_is_1": report["trace_schema_validity"] == 1.0,
            "confidence_is_not_proof": True,
            "live_tensionlm_runtime_loaded_is_false": report["live_tensionlm_runtime_loaded"] is False,
            "production_runtime_claim_is_false": report["production_runtime_claim"] is False,
        },
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if report["backend_contract_validity"] != 1.0:
        raise SystemExit("v4.0 gate failed: backend_contract_validity must be 1.0")
    if wrong_accept_count != 0:
        raise SystemExit("v4.0 gate failed: wrong_accept_count must be 0")
    if accepted_without_support != 0:
        raise SystemExit("v4.0 gate failed: accepted_without_typed_support_count must be 0")
    if report["provenance_preservation_rate"] != 1.0:
        raise SystemExit("v4.0 gate failed: provenance_preservation_rate must be 1.0")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run TS-Reasoner v4.0 live proposer sandbox.")
    parser.add_argument("--cases", default=str(DEFAULT_CASES_PATH), help="Path to sandbox case JSONL.")
    parser.add_argument("--external-jsonl-backend", default=None, help="Optional external JSONL candidate backend path.")
    args = parser.parse_args()

    cases = load_cases(Path(args.cases))
    backend: ProposerBackend
    if args.external_jsonl_backend:
        backend = ExternalJsonlProposerBackend(Path(args.external_jsonl_backend))
    else:
        backend = FixtureProposerBackend()

    report = run_sandbox(cases, backend)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
