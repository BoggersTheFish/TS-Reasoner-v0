"""End-to-end TS-Reasoner-v0 pipeline."""

from __future__ import annotations

from typing import Iterable, Optional

from .cig_checker import CIGChecker
from .generator import DeterministicHeuristicGenerator, infer_premises_from_question
from .ranker import HeuristicTensionRanker
from .repair import TensionRepairer
from .types import ReasonerOutput


class TSReasoner:
    """Generate, score, check, repair, and select a reasoning chain."""

    def __init__(self) -> None:
        self.generator = DeterministicHeuristicGenerator()
        self.cig_checker = CIGChecker()
        self.ranker = HeuristicTensionRanker()
        self.repairer = TensionRepairer()

    def run(self, question: str, premises: Optional[Iterable[str]] = None) -> ReasonerOutput:
        premise_list = [p.strip() for p in premises] if premises is not None else infer_premises_from_question(question)
        candidates = self.generator.generate(question, premise_list)
        scored = []
        for chain in candidates:
            cig = self.cig_checker.check(chain)
            score = self.ranker.score(chain, cig)
            scored.append((chain, cig, score))
        selected_chain, selected_cig, selected_score = min(
            scored,
            key=lambda item: (item[2].global_tension, -item[2].stability, item[0].chain_id),
        )
        repairs = self.repairer.suggest(selected_chain, selected_score)
        trace = {
            "pipeline": "TS-Reasoner-v0",
            "generator": self.generator.name,
            "selection": {
                "selected_chain_id": selected_chain.chain_id,
                "criterion": "lowest_global_tension_then_highest_stability",
            },
            "candidate_scores": [
                {
                    "chain_id": chain.chain_id,
                    "global_tension": score.global_tension,
                    "stability": score.stability,
                    "issue_kinds": [issue.kind for issue in score.issues],
                }
                for chain, _cig, score in scored
            ],
            "graph_view": {
                "nodes": [step.step_id for step in selected_chain.steps],
                "edges": [
                    {"from": dep, "to": step.step_id}
                    for step in selected_chain.steps
                    for dep in step.dependencies
                ],
                "claim_count": len(selected_cig.claims),
                "contradiction_count": len(selected_cig.contradiction_pairs),
            },
        }
        return ReasonerOutput(
            question=question,
            premises=premise_list,
            candidates=[chain for chain, _cig, _score in scored],
            selected_chain=selected_chain,
            tension_score=selected_score,
            cig_check=selected_cig,
            repairs=repairs,
            final_answer=selected_chain.final_answer,
            trace=trace,
        )


def run_reasoner(question: str, premises: Optional[Iterable[str]] = None) -> ReasonerOutput:
    return TSReasoner().run(question, premises)

