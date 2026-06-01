from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List
import json
import time

from ts_agl.core.types import stable_id
from ts_agl.shell import ShellCommandResult, run_shell_command


SESSION_SCHEMA_VERSION = "ts_os_session_ledger_v1"


@dataclass
class TSOSSessionEvent:
    """One persisted TS-OS shell/session event."""

    event_id: str
    index: int
    raw_text: str
    mode: str
    rendered_reply: str
    payload: Dict[str, Any]
    created_at: float = field(default_factory=time.time)

    @classmethod
    def from_shell_result(cls, index: int, result: ShellCommandResult) -> "TSOSSessionEvent":
        payload = result.to_dict()
        event_id = stable_id(
            "session_event",
            {
                "index": index,
                "raw_text": result.raw_text,
                "mode": result.mode,
                "payload": payload,
            },
        )
        return cls(
            event_id=event_id,
            index=index,
            raw_text=result.raw_text,
            mode=result.mode,
            rendered_reply=result.rendered_reply,
            payload=payload,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TSOSSessionEvent":
        return cls(
            event_id=str(data["event_id"]),
            index=int(data["index"]),
            raw_text=str(data["raw_text"]),
            mode=str(data["mode"]),
            rendered_reply=str(data["rendered_reply"]),
            payload=dict(data["payload"]),
            created_at=float(data.get("created_at", time.time())),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "index": self.index,
            "raw_text": self.raw_text,
            "mode": self.mode,
            "rendered_reply": self.rendered_reply,
            "payload": self.payload,
            "created_at": self.created_at,
        }


@dataclass
class TSOSSessionLedger:
    """Persistent shell/session ledger for the TS-OS runway.

    v23.0.0 proves that shell commands can be saved, reloaded, replayed as a
    summary, and continued without treating shell output as proof authority.
    """

    session_id: str
    events: List[TSOSSessionEvent] = field(default_factory=list)
    schema_version: str = SESSION_SCHEMA_VERSION
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    @classmethod
    def new(cls, seed: str = "default") -> "TSOSSessionLedger":
        return cls(
            session_id=stable_id(
                "ts_os_session",
                {
                    "seed": seed,
                    "schema": SESSION_SCHEMA_VERSION,
                },
            )
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TSOSSessionLedger":
        return cls(
            session_id=str(data["session_id"]),
            events=[
                TSOSSessionEvent.from_dict(event)
                for event in data.get("events", [])
            ],
            schema_version=str(data.get("schema_version", SESSION_SCHEMA_VERSION)),
            created_at=float(data.get("created_at", time.time())),
            updated_at=float(data.get("updated_at", time.time())),
        )

    def append_shell_command(self, raw_text: str) -> TSOSSessionEvent:
        result = run_shell_command(raw_text)
        event = TSOSSessionEvent.from_shell_result(len(self.events), result)
        self.events.append(event)
        self.updated_at = time.time()
        return event

    def replay_summary(self) -> Dict[str, Any]:
        mode_counts: Dict[str, int] = {}
        command_history: List[str] = []
        all_payloads_passed = True
        external_llm_used = False
        external_side_effect_performed = False
        candidate_graph_contamination_count = 0

        for event in self.events:
            mode_counts[event.mode] = mode_counts.get(event.mode, 0) + 1
            command_history.append(event.raw_text)

            payload = event.payload.get("payload", {})
            if isinstance(payload, dict):
                all_payloads_passed = all_payloads_passed and bool(payload.get("all_gates_passed", True))
                external_llm_used = external_llm_used or bool(payload.get("external_llm_used", False))
                external_side_effect_performed = external_side_effect_performed or bool(
                    payload.get("external_side_effect_performed", False)
                )
                candidate_graph_contamination_count += int(
                    payload.get("candidate_graph_contamination_count", 0)
                )

        return {
            "session_id": self.session_id,
            "schema_version": self.schema_version,
            "event_count": len(self.events),
            "mode_counts": dict(sorted(mode_counts.items())),
            "command_history": command_history,
            "can_resume": True,
            "all_payloads_passed": all_payloads_passed,
            "external_llm_used": external_llm_used,
            "external_side_effect_performed": external_side_effect_performed,
            "candidate_graph_contamination_count": candidate_graph_contamination_count,
            "all_gates_passed": (
                len(self.events) > 0
                and all_payloads_passed
                and external_llm_used is False
                and external_side_effect_performed is False
                and candidate_graph_contamination_count == 0
            ),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact": "ts_os_session_ledger",
            "schema_version": self.schema_version,
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "events": [event.to_dict() for event in self.events],
            "replay_summary": self.replay_summary(),
            "boundary": {
                "session_output_is_not_proof_authority": True,
                "shell_confidence_is_not_proof": True,
                "external_llm_used": False,
                "candidate_graph_contamination_count": 0,
            },
        }

    def save(self, path: str | Path) -> None:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "TSOSSessionLedger":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def load_or_create_session(path: str | Path, seed: str = "default") -> TSOSSessionLedger:
    session_path = Path(path)
    if session_path.exists():
        return TSOSSessionLedger.load(session_path)
    return TSOSSessionLedger.new(seed=seed)
