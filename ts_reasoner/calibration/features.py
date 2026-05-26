"""Feature extraction for typed-channel calibration.

The feature surface is intentionally small and auditable. It describes the
typed trace state and simple premise/query structure; it does not learn
reasoning behavior from raw text.
"""

from __future__ import annotations

import re
from typing import Any

from ts_reasoner.generator import extract_relations, infer_query_relation


CHANNELS = (
    "logic_transitivity",
    "identity_preservation",
    "directionality",
    "surface_structure",
    "confidence_abstention",
    "contradiction",
    "quantifier_scope",
)

FEATURE_NAMES = (
    "bias",
    "premise_count",
    "all_edge_count",
    "some_edge_count",
    "no_edge_count",
    "has_all_all_chain",
    "query_supported_directly",
    "query_supported_transitively",
    "query_reverse_of_chain",
    "query_is_identity",
    "has_some_all_upgrade",
    "has_direct_contradiction",
    "empty_premises",
    "answer_abstains",
    "channel_observed_initial_tension",
    "channel_observed_final_tension",
    "channel_logic_transitivity",
    "channel_identity_preservation",
    "channel_directionality",
    "channel_surface_structure",
    "channel_confidence_abstention",
    "channel_contradiction",
    "channel_quantifier_scope",
)


def extract_case_features(case: dict[str, Any], output: Any, channel: str) -> dict[str, float]:
    premises = [str(item) for item in case.get("premises", [])]
    relations = [relation for premise in premises for relation in extract_relations(premise)]
    query = infer_query_relation(str(case.get("question", "")))
    identity_match = re.search(
        r"\bis\s+(?P<subject>[A-Za-z][A-Za-z0-9_-]*)\s+identical\s+to\s+(?P<predicate>[A-Za-z][A-Za-z0-9_-]*)",
        str(case.get("question", "")),
        flags=re.IGNORECASE,
    )
    if identity_match:
        query_subject = identity_match.group("subject")
        query_predicate = identity_match.group("predicate")
        query_quantifier = "identity"
    elif query is not None:
        query_subject = query.subject
        query_predicate = query.predicate
        query_quantifier = query.quantifier
    else:
        query_subject = ""
        query_predicate = ""
        query_quantifier = ""

    all_edges = [relation for relation in relations if relation.quantifier == "all"]
    some_edges = [relation for relation in relations if relation.quantifier == "some"]
    no_edges = [relation for relation in relations if relation.quantifier == "no"]
    has_chain = _has_all_all_chain(all_edges)
    direct = _has_direct_relation(relations, query_subject, query_predicate, query_quantifier)
    transitive = _has_transitive_relation(all_edges, query_subject, query_predicate)
    reverse = _has_transitive_relation(all_edges, query_predicate, query_subject) and not direct
    some_all = _has_some_all_upgrade(some_edges, all_edges, query_subject, query_predicate, query_quantifier)
    contradiction = _has_direct_contradiction(relations)
    channel_trace = output.trace.get("tension_channels", {}).get(channel, {})

    features = {
        "bias": 1.0,
        "premise_count": float(len(premises)),
        "all_edge_count": float(len(all_edges)),
        "some_edge_count": float(len(some_edges)),
        "no_edge_count": float(len(no_edges)),
        "has_all_all_chain": float(has_chain),
        "query_supported_directly": float(direct),
        "query_supported_transitively": float(transitive),
        "query_reverse_of_chain": float(reverse),
        "query_is_identity": float(query_quantifier == "identity"),
        "has_some_all_upgrade": float(some_all),
        "has_direct_contradiction": float(contradiction),
        "empty_premises": float(len(premises) == 0),
        "answer_abstains": float("not enough" in output.final_answer.lower()),
        "channel_observed_initial_tension": float(channel_trace.get("initial_tension", 0.0)),
        "channel_observed_final_tension": float(channel_trace.get("final_tension", 0.0)),
    }
    for name in CHANNELS:
        features[f"channel_{name}"] = float(channel == name)
    return {name: float(features.get(name, 0.0)) for name in FEATURE_NAMES}


def _has_direct_relation(relations, subject: str, predicate: str, quantifier: str) -> bool:
    if not subject or not predicate:
        return False
    return any(
        relation.subject.lower() == subject.lower()
        and relation.predicate.lower() == predicate.lower()
        and relation.quantifier == quantifier
        for relation in relations
    )


def _has_all_all_chain(all_edges) -> bool:
    return any(
        left.predicate.lower() == right.subject.lower()
        for left in all_edges
        for right in all_edges
        if left is not right
    )


def _has_transitive_relation(all_edges, subject: str, predicate: str) -> bool:
    if not subject or not predicate:
        return False
    return any(
        left.subject.lower() == subject.lower()
        and left.predicate.lower() == right.subject.lower()
        and right.predicate.lower() == predicate.lower()
        for left in all_edges
        for right in all_edges
        if left is not right
    )


def _has_some_all_upgrade(some_edges, all_edges, subject: str, predicate: str, quantifier: str) -> bool:
    if quantifier != "all":
        return False
    return any(
        left.subject.lower() == subject.lower()
        and left.predicate.lower() == right.subject.lower()
        and right.predicate.lower() == predicate.lower()
        for left in some_edges
        for right in all_edges
    )


def _has_direct_contradiction(relations) -> bool:
    for left in relations:
        for right in relations:
            if left is right:
                continue
            same_pair = (
                left.subject.lower() == right.subject.lower()
                and left.predicate.lower() == right.predicate.lower()
            )
            if same_pair and {left.quantifier, right.quantifier} & {"no"} and {left.quantifier, right.quantifier} & {"all", "some"}:
                return True
    return False
