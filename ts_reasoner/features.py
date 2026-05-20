"""Feature extraction for candidate-chain tension ranking."""

from __future__ import annotations

from typing import Dict

from .generator import extract_relations
from .types import CIGCheck, ReasoningChain


FEATURE_NAMES = [
    "bias",
    "step_count",
    "premise_count",
    "claim_count",
    "dependency_edge_count",
    "contradiction_count",
    "unsupported_claim_count",
    "circular_step_count",
    "conclusion_all_count",
    "conclusion_some_count",
    "premise_some_count",
    "premise_no_count",
    "missing_premise_flag",
    "insufficiency_answer_flag",
    "contradiction_answer_flag",
    "direct_candidate_flag",
    "cautious_candidate_flag",
]


def extract_chain_features(chain: ReasoningChain, cig_check: CIGCheck) -> Dict[str, float]:
    """Extract deterministic numeric features for learned ranker experiments."""
    conclusion_relations = [
        relation
        for step in chain.steps
        if step.kind == "conclusion"
        for relation in extract_relations(step.text)
    ]
    premise_relations = [
        relation
        for premise in chain.premises
        for relation in extract_relations(premise)
    ]
    final_lower = chain.final_answer.lower()
    return {
        "bias": 1.0,
        "step_count": float(len(chain.steps)),
        "premise_count": float(len(chain.premises)),
        "claim_count": float(len(cig_check.claims)),
        "dependency_edge_count": float(sum(len(step.dependencies) for step in chain.steps)),
        "contradiction_count": float(len(cig_check.contradiction_pairs)),
        "unsupported_claim_count": float(len(cig_check.unsupported_claim_ids)),
        "circular_step_count": float(len(cig_check.circular_step_ids)),
        "conclusion_all_count": float(sum(1 for relation in conclusion_relations if relation.quantifier == "all")),
        "conclusion_some_count": float(sum(1 for relation in conclusion_relations if relation.quantifier == "some")),
        "premise_some_count": float(sum(1 for relation in premise_relations if relation.quantifier == "some")),
        "premise_no_count": float(sum(1 for relation in premise_relations if relation.quantifier == "no")),
        "missing_premise_flag": 1.0 if not chain.premises else 0.0,
        "insufficiency_answer_flag": 1.0 if "not enough" in final_lower or "more information" in final_lower else 0.0,
        "contradiction_answer_flag": 1.0 if "contradiction" in final_lower else 0.0,
        "direct_candidate_flag": 1.0 if "direct" in chain.chain_id else 0.0,
        "cautious_candidate_flag": 1.0 if "cautious" in chain.chain_id else 0.0,
    }


def vectorize_features(features: Dict[str, float]) -> list[float]:
    return [float(features.get(name, 0.0)) for name in FEATURE_NAMES]

