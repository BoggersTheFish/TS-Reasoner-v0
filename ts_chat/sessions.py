"""Persistent TS-Chat session storage for v6.1.0.

This module is intentionally small and conservative:
- plain JSON only
- no external LLM
- no proof promotion on load
- loaded candidate/unsupported data remains candidate/unsupported data
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


SCHEMA = "ts_chat_session_v1"
RELEASE = "v6.1.0"


@dataclass(frozen=True)
class ChatClaim:
    claim_id: str
    text: str
    status: str
    source: str
    turn_id: str
    support_paths: list[list[str]] = field(default_factory=list)
    verifier_channels: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RepairTarget:
    repair_id: str
    claim_text: str
    reason: str
    source_turn_id: str
    status: str = "open"


@dataclass
class ChatSession:
    session_id: str
    claims: list[ChatClaim] = field(default_factory=list)
    repair_targets: list[RepairTarget] = field(default_factory=list)
    external_llm_used: bool = False

    def accepted_claim_texts(self) -> list[str]:
        return [claim.text for claim in self.claims if claim.status == "accepted"]

    def unsupported_or_candidate_claim_texts(self) -> list[str]:
        return [
            claim.text
            for claim in self.claims
            if claim.status in {"unsupported", "candidate", "rejected", "abstained"}
        ]

    def candidate_graph_contamination_count(self) -> int:
        """Count unsupported/candidate/rejected/abstained claims incorrectly accepted.

        The invariant is simple: non-proof statuses must not be promoted to accepted.
        """
        bad_statuses = {"unsupported", "candidate", "rejected", "abstained"}
        return sum(1 for claim in self.claims if claim.status in bad_statuses and claim.status == "accepted")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "release": RELEASE,
            "session_id": self.session_id,
            "external_llm_used": self.external_llm_used,
            "claims": [asdict(claim) for claim in self.claims],
            "repair_targets": [asdict(target) for target in self.repair_targets],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ChatSession":
        if not isinstance(payload, dict):
            raise ValueError("Session payload must be a JSON object.")

        if payload.get("schema") != SCHEMA:
            raise ValueError(f"Unsupported session schema: {payload.get('schema')!r}")

        if payload.get("external_llm_used") is True:
            raise ValueError("Refusing to load session marked as using an external LLM.")

        claims: list[ChatClaim] = []
        for raw in payload.get("claims", []):
            status = raw.get("status")
            if status not in {"accepted", "unsupported", "candidate", "rejected", "abstained"}:
                raise ValueError(f"Unsupported claim status: {status!r}")

            claims.append(
                ChatClaim(
                    claim_id=str(raw["claim_id"]),
                    text=str(raw["text"]),
                    status=str(status),
                    source=str(raw.get("source", "unknown")),
                    turn_id=str(raw.get("turn_id", "unknown")),
                    support_paths=list(raw.get("support_paths", [])),
                    verifier_channels=list(raw.get("verifier_channels", [])),
                )
            )

        repair_targets: list[RepairTarget] = []
        for raw in payload.get("repair_targets", []):
            status = raw.get("status", "open")
            if status not in {"open", "resolved", "rejected"}:
                raise ValueError(f"Unsupported repair target status: {status!r}")

            repair_targets.append(
                RepairTarget(
                    repair_id=str(raw["repair_id"]),
                    claim_text=str(raw["claim_text"]),
                    reason=str(raw["reason"]),
                    source_turn_id=str(raw.get("source_turn_id", "unknown")),
                    status=str(status),
                )
            )

        return cls(
            session_id=str(payload["session_id"]),
            claims=claims,
            repair_targets=repair_targets,
            external_llm_used=False,
        )


def save_session(session: ChatSession, path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(session.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def load_session(path: str | Path) -> ChatSession:
    raw = Path(path).read_text(encoding="utf-8")
    payload = json.loads(raw)
    return ChatSession.from_dict(payload)


def build_v61_demo_session() -> ChatSession:
    return ChatSession(
        session_id="ts_chat_v1_1_demo_session",
        claims=[
            ChatClaim(
                claim_id="claim_001",
                text="all cats are animals",
                status="accepted",
                source="user",
                turn_id="turn_001",
                support_paths=[],
                verifier_channels=["user_asserted_common_ground"],
            ),
            ChatClaim(
                claim_id="claim_002",
                text="all animals are mortal",
                status="accepted",
                source="user",
                turn_id="turn_002",
                support_paths=[],
                verifier_channels=["user_asserted_common_ground"],
            ),
            ChatClaim(
                claim_id="claim_003",
                text="all cats are robots",
                status="unsupported",
                source="user",
                turn_id="turn_003",
                support_paths=[],
                verifier_channels=[],
            ),
        ],
        repair_targets=[
            RepairTarget(
                repair_id="repair_001",
                claim_text="all cats are robots",
                reason="missing typed verifier support",
                source_turn_id="turn_003",
                status="open",
            )
        ],
        external_llm_used=False,
    )
