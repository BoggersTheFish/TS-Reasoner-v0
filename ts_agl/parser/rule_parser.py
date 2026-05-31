from __future__ import annotations

from typing import Dict, List, Optional
import re

from ts_agl.core.types import LanguageMove


def _contains_any(text: str, patterns: List[str]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def _claim_after_marker(text: str) -> Optional[str]:
    markers = [
        r"does\s+(.+?)\s+follow",
        r"can\s+we\s+prove\s+(.+)",
        r"check\s+support\s+for\s+(.+)",
        r"add\s+(?:that\s+as\s+)?(?:a\s+)?premise\s*:?\s*(.+)",
        r"i\s+mean[t]?\s+(.+)",
    ]
    unresolved_references = {"that", "this", "it", "that?", "this?", "it?"}

    for pattern in markers:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            claim = match.group(1).strip(" .?!").strip()
            if claim.lower() in unresolved_references:
                return None
            return claim
    return None


def parse_language_moves(raw_text: str, context: Optional[Dict[str, str]] = None) -> List[LanguageMove]:
    """Parse messy user text into candidate LanguageMove objects.

    v0 intentionally uses transparent rules. This is not proof authority.
    """

    context = context or {}
    text = raw_text.strip()
    low = text.lower()
    moves: List[LanguageMove] = []

    if not text:
        return [
            LanguageMove(
                move_type="ASK",
                raw_text=raw_text,
                target=None,
                content=None,
                unresolved_slots=["utterance"],
                confidence=1.0,
            )
        ]

    # Correction / user says previous parse was wrong.
    if _contains_any(low, [r"\bno\b", r"\bnah\b", r"\bi meant\b", r"\bnot that\b"]):
        claim = _claim_after_marker(text)
        moves.append(
            LanguageMove(
                move_type="CORRECT",
                raw_text=text,
                target=context.get("last_candidate", "previous_candidate"),
                content=claim,
                slots={"replacement": claim} if claim else {},
                unresolved_slots=[] if claim else ["replacement"],
                operation_hint="correct_candidate",
                domain_hint="ts_reasoner",
                confidence=0.78,
            )
        )

    # Repo/git status.
    if _contains_any(low, [r"\brepo\b", r"\bgit\b", r"\bbranch\b", r"\bworktree\b", r"\bclean\b", r"\bstatus\b"]):
        moves.append(
            LanguageMove(
                move_type="INSPECT",
                raw_text=text,
                target="repo",
                slots={},
                operation_hint="git_status",
                domain_hint="git_repo",
                confidence=0.92,
            )
        )

    # Tag/release/version state.
    if _contains_any(low, [r"\brelease\b", r"\bversion\b", r"\btag\b", r"\bwhere are we\b"]):
        moves.append(
            LanguageMove(
                move_type="INSPECT",
                raw_text=text,
                target="release",
                slots={},
                operation_hint="current_tag",
                domain_hint="git_repo",
                confidence=0.86,
            )
        )

    # Planning / next safe action.
    if _contains_any(low, [r"\bnext safe action\b", r"\bnext action\b", r"\bwhat now\b", r"\bplan\b"]):
        moves.append(
            LanguageMove(
                move_type="PLAN",
                raw_text=text,
                target="current_project_state",
                slots={},
                operation_hint="next_safe_release_action",
                domain_hint="git_repo",
                confidence=0.83,
            )
        )

    # Support / proof query.
    if _contains_any(low, [r"\bdoes that follow\b", r"\bfollow from\b", r"\bcan we prove\b", r"\bcheck support\b"]):
        claim = _claim_after_marker(text) or context.get("current_focus_claim")
        moves.append(
            LanguageMove(
                move_type="CHECK",
                raw_text=text,
                target=claim or "current_focus_claim",
                content=claim,
                slots={"claim": claim} if claim else {},
                unresolved_slots=[] if claim else ["claim"],
                operation_hint="check_support",
                domain_hint="ts_reasoner",
                confidence=0.88 if claim else 0.65,
            )
        )

    # Explain rejection / trace.
    if _contains_any(low, [r"\bwhy\b.*\breject", r"\bexplain\b.*\breject", r"\bwhy did\b"]):
        moves.append(
            LanguageMove(
                move_type="EXPLAIN",
                raw_text=text,
                target=context.get("last_rejected_claim", "last_rejected_claim"),
                slots={"claim_id": context.get("last_rejected_claim", "last_rejected_claim")},
                operation_hint="explain_rejection",
                domain_hint="ts_reasoner",
                confidence=0.82,
            )
        )

    # Summary of current known state.
    if _contains_any(low, [r"\bwhat do we know\b", r"\bsummar", r"\bstate so far\b", r"\bwhere are we\b"]):
        moves.append(
            LanguageMove(
                move_type="SUMMARISE",
                raw_text=text,
                target="session",
                slots={},
                operation_hint="summarize_session",
                domain_hint="ts_reasoner",
                confidence=0.81,
            )
        )

    if not moves:
        moves.append(
            LanguageMove(
                move_type="ASK",
                raw_text=text,
                target=None,
                content=text,
                slots={"utterance": text},
                operation_hint="route_unknown",
                domain_hint="ts_reasoner",
                confidence=0.42,
            )
        )

    # Deduplicate same operation hints while preserving order.
    seen = set()
    deduped: List[LanguageMove] = []
    for move in moves:
        key = (move.move_type, move.domain_hint, move.operation_hint)
        if key not in seen:
            deduped.append(move)
            seen.add(key)
    return deduped
