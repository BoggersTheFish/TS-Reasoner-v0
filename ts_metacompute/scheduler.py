from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ts_metacompute.spectral.signed_graph import SignedGraph
from ts_metacompute.spectral.modes import read_spectral_tension


@dataclass(frozen=True)
class SchedulerTask:
    task_type: str
    graph: SignedGraph
    verifier_required: bool = True


class MetacomputeScheduler:
    """Minimal substrate scheduler for verifier-first metacompute.

    The v0.1 scheduler only has a spectral implementation. The interface is
    explicit so later phase/grid/field kernels can compete without inheriting
    proof authority.
    """

    def choose_substrate(self, task: SchedulerTask) -> str:
        if task.task_type in {
            "coherence_read",
            "contradiction_localization",
            "repair_ranking",
            "mode_read",
        }:
            return "spectral"
        return "symbolic_verifier"

    def run(self, task: SchedulerTask) -> dict[str, Any]:
        substrate = self.choose_substrate(task)
        if substrate == "spectral":
            read = read_spectral_tension(task.graph)
            payload = read.to_dict()
        else:
            payload = {
                "status": "abstained",
                "reason": "no_non_symbolic_substrate_selected",
                "accepted_truth": False,
            }

        payload["selected_substrate"] = substrate
        payload["verifier_required_for_acceptance"] = task.verifier_required
        payload["accepted_without_verifier_support_count"] = 0
        return payload
