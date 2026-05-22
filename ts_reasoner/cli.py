"""Console entry point for TS-Reasoner-v0."""

from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import run_reasoner
from .tension_agents import TensionCoordinator
from .trace import write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the TS-Reasoner-v0 toy pipeline.")
    parser.add_argument("--question", required=True, help="Question to reason about.")
    parser.add_argument(
        "--premise",
        action="append",
        default=None,
        help="Optional explicit premise. Can be passed more than once.",
    )
    parser.add_argument(
        "--trace",
        default="artifacts/latest_trace.json",
        help="Path for JSON trace output.",
    )
    parser.add_argument(
        "--coupling-matrix",
        default=None,
        help="Optional learned coupling matrix JSON artifact.",
    )
    args = parser.parse_args()

    coordinator = TensionCoordinator.from_json(args.coupling_matrix) if args.coupling_matrix else None
    output = run_reasoner(args.question, args.premise, tension_coordinator=coordinator)
    trace_path = write_json(output, Path(args.trace))

    print("TS-Reasoner-v0")
    print(f"Question: {output.question}")
    if output.premises:
        print("Premises:")
        for premise in output.premises:
            print(f"  - {premise}")
    print(f"Answer: {output.final_answer}")
    print(f"Selected chain: {output.selected_chain.chain_id}")
    print(f"Global tension: {output.tension_score.global_tension:.4f}")
    if output.tension_score.issues:
        print("Issues:")
        for issue in output.tension_score.issues:
            print(f"  - {issue.kind} at {issue.step_id}: {issue.message}")
    if output.repairs:
        print("Repairs:")
        for repair in output.repairs:
            print(f"  - {repair.issue_kind}: {repair.proposed_text}")
    print(f"Trace: {trace_path}")
    return 0


__all__ = ["main"]
