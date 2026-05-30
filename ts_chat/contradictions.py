"""Bounded contradiction handling for TS-Chat v6.4.0.

Scope:
- bounded all-X-are-Y / no-X-are-Y claims
- direct contradiction: all A are B vs no A are B
- transitive contradiction: all A are B, all B are C vs no A are C

Boundary:
- contradiction detection is not broad NLP
- rejected contradiction claims do not become proof
- repair targets are not proof
- typed verifier/common-ground support remains proof authority
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from ts_chat.sessions import ChatClaim, ChatSession, RepairTarget


SCHEMA = "ts_chat_contradiction_trace_v1"
RELEASE = "v6.4.0"


@dataclass(frozen=True)
class ParsedClaim:
    original_text: str
    quantifier: str
    subject: str
    object: str
    polarity: str


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower().rstrip(".!?"))


def parse_bounded_claim(text: str) -> ParsedClaim | None:
    normalized = _normalize_text(text)
    match = re.match(r"^(all|no)\s+(.+?)\s+are\s+(.+)$", normalized)
    if not match:
        return None

    quantifier, subject, object_ = match.groups()
    polarity = "positive" if quantifier == "all" else "negative"

    return ParsedClaim(
        original_text=text,
        quantifier=quantifier,
        subject=subject.strip(),
        object=object_.strip(),
        polarity=polarity,
    )


def _accepted_parsed_claims(session: ChatSession) -> list[tuple[ChatClaim, ParsedClaim]]:
    parsed: list[tuple[ChatClaim, ParsedClaim]] = []

    for claim in session.claims:
        if claim.status != "accepted":
            continue

        parsed_claim = parse_bounded_claim(claim.text)
        if parsed_claim is not None:
            parsed.append((claim, parsed_claim))

    return parsed


def _positive_edges(session: ChatSession) -> list[tuple[str, str, str]]:
    edges: list[tuple[str, str, str]] = []

    for claim, parsed in _accepted_parsed_claims(session):
        if parsed.polarity == "positive":
            edges.append((parsed.subject, parsed.object, claim.text))

    return edges


def _negative_edges(session: ChatSession) -> list[tuple[str, str, str]]:
    edges: list[tuple[str, str, str]] = []

    for claim, parsed in _accepted_parsed_claims(session):
        if parsed.polarity == "negative":
            edges.append((parsed.subject, parsed.object, claim.text))

    return edges


def find_positive_support_path(session: ChatSession, subject: str, object_: str) -> list[str]:
    """Find a bounded positive all/all path from subject to object.

    This is deliberately small but supports multi-hop paths.
    """
    edges = _positive_edges(session)
    frontier: list[tuple[str, list[str]]] = [(subject, [])]
    visited = {subject}

    while frontier:
        node, path = frontier.pop(0)

        for edge_subject, edge_object, claim_text in edges:
            if edge_subject != node:
                continue

            next_path = path + [claim_text]

            if edge_object == object_:
                return next_path

            if edge_object not in visited:
                visited.add(edge_object)
                frontier.append((edge_object, next_path))

    return []


def find_direct_negative_support(session: ChatSession, subject: str, object_: str) -> list[str]:
    for edge_subject, edge_object, claim_text in _negative_edges(session):
        if edge_subject == subject and edge_object == object_:
            return [claim_text]
    return []


def detect_contradiction(session: ChatSession, claim_text: str) -> dict[str, Any]:
    parsed = parse_bounded_claim(claim_text)

    if parsed is None:
        return {
            "schema": SCHEMA,
            "release": RELEASE,
            "claim_text": claim_text,
            "parsed": False,
            "contradiction_detected": False,
            "contradiction_type": "unparsed",
            "reason": "claim is outside bounded all/no X are Y form",
            "support_path": [],
            "creates_proof": False,
            "proof_authority": "typed_verifier",
            "external_llm_used": False,
        }

    if parsed.polarity == "negative":
        positive_path = find_positive_support_path(session, parsed.subject, parsed.object)
        if positive_path:
            contradiction_type = "transitive_contradiction" if len(positive_path) > 1 else "direct_contradiction"
            return {
                "schema": SCHEMA,
                "release": RELEASE,
                "claim_text": claim_text,
                "parsed": True,
                "parsed_claim": {
                    "quantifier": parsed.quantifier,
                    "subject": parsed.subject,
                    "object": parsed.object,
                    "polarity": parsed.polarity,
                },
                "contradiction_detected": True,
                "contradiction_type": contradiction_type,
                "reason": "negative claim conflicts with accepted positive support path",
                "support_path": positive_path,
                "creates_proof": False,
                "proof_authority": "typed_verifier",
                "external_llm_used": False,
            }

    if parsed.polarity == "positive":
        negative_path = find_direct_negative_support(session, parsed.subject, parsed.object)
        if negative_path:
            return {
                "schema": SCHEMA,
                "release": RELEASE,
                "claim_text": claim_text,
                "parsed": True,
                "parsed_claim": {
                    "quantifier": parsed.quantifier,
                    "subject": parsed.subject,
                    "object": parsed.object,
                    "polarity": parsed.polarity,
                },
                "contradiction_detected": True,
                "contradiction_type": "direct_contradiction",
                "reason": "positive claim conflicts with accepted negative claim",
                "support_path": negative_path,
                "creates_proof": False,
                "proof_authority": "typed_verifier",
                "external_llm_used": False,
            }

    return {
        "schema": SCHEMA,
        "release": RELEASE,
        "claim_text": claim_text,
        "parsed": True,
        "parsed_claim": {
            "quantifier": parsed.quantifier,
            "subject": parsed.subject,
            "object": parsed.object,
            "polarity": parsed.polarity,
        },
        "contradiction_detected": False,
        "contradiction_type": "none",
        "reason": "no contradiction found against accepted common ground",
        "support_path": [],
        "creates_proof": False,
        "proof_authority": "typed_verifier",
        "external_llm_used": False,
    }


def apply_contradiction_guard(session: ChatSession, claim_text: str, source_turn_id: str) -> tuple[ChatSession, dict[str, Any]]:
    """Reject contradictory claims and create repair targets.

    Non-contradictory claims are returned as candidate/unsupported memory,
    not accepted proof.
    """
    trace = detect_contradiction(session, claim_text)
    next_claim_index = len(session.claims) + 1
    next_repair_index = len(session.repair_targets) + 1

    if trace["contradiction_detected"]:
        rejected_claim = ChatClaim(
            claim_id=f"claim_{next_claim_index:03d}",
            text=claim_text,
            status="rejected",
            source="user",
            turn_id=source_turn_id,
            support_paths=[trace["support_path"]],
            verifier_channels=["contradiction"],
        )

        repair_target = RepairTarget(
            repair_id=f"repair_{next_repair_index:03d}",
            claim_text=claim_text,
            reason=f"contradiction detected: {trace['contradiction_type']}",
            source_turn_id=source_turn_id,
            status="open",
        )

        updated = ChatSession(
            session_id=session.session_id,
            claims=list(session.claims) + [rejected_claim],
            repair_targets=list(session.repair_targets) + [repair_target],
            external_llm_used=False,
        )

        return updated, trace

    candidate_claim = ChatClaim(
        claim_id=f"claim_{next_claim_index:03d}",
        text=claim_text,
        status="unsupported",
        source="user",
        turn_id=source_turn_id,
        support_paths=[],
        verifier_channels=[],
    )

    updated = ChatSession(
        session_id=session.session_id,
        claims=list(session.claims) + [candidate_claim],
        repair_targets=list(session.repair_targets),
        external_llm_used=False,
    )

    return updated, trace


def contradiction_trace_valid(trace: dict[str, Any]) -> bool:
    required = {
        "schema",
        "release",
        "claim_text",
        "parsed",
        "contradiction_detected",
        "contradiction_type",
        "reason",
        "support_path",
        "creates_proof",
        "proof_authority",
        "external_llm_used",
    }

    if not required.issubset(trace):
        return False

    if trace["schema"] != SCHEMA:
        return False

    if trace["release"] != RELEASE:
        return False

    if trace["creates_proof"] is not False:
        return False

    if trace["proof_authority"] != "typed_verifier":
        return False

    if trace["external_llm_used"] is not False:
        return False

    if not isinstance(trace["support_path"], list):
        return False

    return True


def contradictory_claims_not_accepted(session: ChatSession) -> bool:
    for claim in session.claims:
        if claim.status == "rejected" and claim.text in session.accepted_claim_texts():
            return False
    return True
