"""TS-Chat v0.2.

Scratch TS-native bounded chat loop with a common-ground manager.

No external LLM is used.

This version models conversation as common-ground updates:
- user assertions become accepted premises
- questions become query records
- requested claims become accepted/rejected records
- "why?" explains the latest accepted support path
- "what do we know?" summarizes common ground
- "what is unsupported?" summarizes rejected/abstained claims
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ts_reasoner.answer_arena import Relation, extract_all_relation, extract_question_relation, normalize_term
from ts_reasoner.common_ground import CommonGround, human_relation


ASK_RE = re.compile(r"\b(?:are|is)\s+all\s+.+?[?]", re.IGNORECASE)
REQUEST_RE = re.compile(
    r"\b(?:say|claim|also say|include)\s+(?:that\s+)?(?:all\s+)?(.+?)\s+(?:are|is)\s+(.+?)(?:[.?!,;:]|$)",
    re.IGNORECASE,
)
DISCOURSE_MARKERS = ["also", "but", "so", "therefore", "actually", "maybe", "probably"]


@dataclass
class ParsedTurn:
    raw_text: str
    command: str | None = None
    premises: list[Relation] = field(default_factory=list)
    questions: list[Relation] = field(default_factory=list)
    requested_claims: list[Relation] = field(default_factory=list)
    discourse_markers: list[str] = field(default_factory=list)
    parse_warnings: list[str] = field(default_factory=list)


@dataclass
class ChatTurnReceipt:
    turn_id: int
    user_text: str
    command: str | None
    parsed_premises: list[dict[str, str]]
    parsed_questions: list[dict[str, str]]
    requested_claims: list[dict[str, str]]
    discourse_markers: list[str]
    records_created: list[dict[str, Any]]
    response: str
    common_ground: dict[str, Any]
    parse_warnings: list[str]

    @property
    def decisions(self) -> list[dict[str, Any]]:
        """v0.1 compatibility alias.

        TS-Chat v0.1 called these response records "decisions".
        v0.2 stores richer common-ground records, but old tests/scripts can
        still read them as decisions.
        """
        return self.records_created

    @property
    def graph_edge_count(self) -> int:
        """v0.1 compatibility alias."""
        return int(self.common_ground.get("accepted_edge_count", 0))


def relation_to_dict(relation: Relation) -> dict[str, str]:
    return {"subject": relation.subject, "object": relation.object}


def receipt_to_dict(receipt: ChatTurnReceipt) -> dict[str, Any]:
    return {
        "turn_id": receipt.turn_id,
        "user_text": receipt.user_text,
        "command": receipt.command,
        "parsed_premises": receipt.parsed_premises,
        "parsed_questions": receipt.parsed_questions,
        "requested_claims": receipt.requested_claims,
        "discourse_markers": receipt.discourse_markers,
        "records_created": receipt.records_created,
        "decisions": receipt.records_created,
        "response": receipt.response,
        "common_ground": receipt.common_ground,
        "graph_edge_count": receipt.graph_edge_count,
        "parse_warnings": receipt.parse_warnings,
    }


class TSChatSession:
    """Stateful chat session backed by a common-ground graph."""

    def __init__(self) -> None:
        self.common_ground = CommonGround()
        self.turn_receipts: list[ChatTurnReceipt] = []

    @property
    def edges(self) -> set[tuple[str, str]]:
        return self.common_ground.accepted_edges

    def process(self, user_text: str) -> ChatTurnReceipt:
        turn_id = self.common_ground.next_turn()
        parsed = parse_turn(user_text)
        created_records: list[dict[str, Any]] = []

        if parsed.command == "summary":
            response = self.common_ground.summary()
        elif parsed.command == "unsupported":
            response = self.common_ground.unsupported_summary()
        elif parsed.command == "why":
            response = self.common_ground.why_summary()
        elif parsed.command == "graph":
            response = json.dumps(self.common_ground.to_dict(), indent=2, sort_keys=True)
        elif parsed.command == "clear":
            self.common_ground = CommonGround()
            self.common_ground.turn_id = turn_id
            response = "Common ground cleared."
        else:
            for premise in parsed.premises:
                record = self.common_ground.add_asserted_premise(
                    premise,
                    discourse_markers=parsed.discourse_markers,
                )
                created_records.append(record_to_dict(record))

            for question in parsed.questions:
                record = self.common_ground.record_question_result(
                    question,
                    discourse_markers=parsed.discourse_markers,
                )
                created_records.append(record_to_dict(record))

            for requested in parsed.requested_claims:
                record = self.common_ground.record_requested_claim(
                    requested,
                    discourse_markers=parsed.discourse_markers,
                )
                created_records.append(record_to_dict(record))

            response = compose_response(parsed, created_records)

        receipt = ChatTurnReceipt(
            turn_id=turn_id,
            user_text=user_text,
            command=parsed.command,
            parsed_premises=[relation_to_dict(r) for r in parsed.premises],
            parsed_questions=[relation_to_dict(r) for r in parsed.questions],
            requested_claims=[relation_to_dict(r) for r in parsed.requested_claims],
            discourse_markers=parsed.discourse_markers,
            records_created=created_records,
            response=response,
            common_ground=self.common_ground.to_dict(),
            parse_warnings=parsed.parse_warnings,
        )
        self.turn_receipts.append(receipt)
        return receipt

    def save_receipts(self, path: str | Path) -> Path:
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps([receipt_to_dict(r) for r in self.turn_receipts], indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return out


def record_to_dict(record: Any) -> dict[str, Any]:
    return {
        "claim_id": record.claim_id,
        "relation": relation_to_dict(record.relation),
        "status": record.status,
        "kind": record.kind,
        "source": record.source,
        "turn_id": record.turn_id,
        "support_path": record.support_path,
        "discourse_markers": record.discourse_markers,
        "reason": record.reason,
    }


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.?!])\s+", text.strip())
    return [part.strip() for part in parts if part.strip()]


def detect_command(text: str) -> str | None:
    lowered = text.strip().lower()
    if lowered in {"what do we know?", "what do we know", "/known", "/summary"}:
        return "summary"
    if lowered in {"what is unsupported?", "what is unsupported", "/unsupported"}:
        return "unsupported"
    if lowered in {"why?", "why", "/why"}:
        return "why"
    if lowered in {"/graph", "show graph", "show graph?"}:
        return "graph"
    if lowered in {"/clear", "clear", "clear graph"}:
        return "clear"
    return None


def detect_discourse_markers(text: str) -> list[str]:
    lowered = text.lower()
    return [marker for marker in DISCOURSE_MARKERS if re.search(rf"\b{re.escape(marker)}\b", lowered)]


def parse_requested_claim(sentence: str) -> Relation | None:
    match = REQUEST_RE.search(sentence)
    if not match:
        return None
    return Relation(normalize_term(match.group(1)), normalize_term(match.group(2)))


def parse_turn(user_text: str) -> ParsedTurn:
    parsed = ParsedTurn(raw_text=user_text)
    parsed.command = detect_command(user_text)
    parsed.discourse_markers = detect_discourse_markers(user_text)

    if parsed.command:
        return parsed

    sentences = split_sentences(user_text)

    for sentence in sentences:
        question = extract_question_relation(sentence) if "?" in sentence or ASK_RE.search(sentence) else None
        if question:
            parsed.questions.append(question)
            continue

        requested = parse_requested_claim(sentence)
        if requested:
            parsed.requested_claims.append(requested)
            continue

        premise = extract_all_relation(sentence)
        if premise:
            parsed.premises.append(premise)
            continue

        lowered = sentence.lower()
        if lowered in {"exit", "quit", "q"}:
            continue

        parsed.parse_warnings.append(f"Could not parse bounded TS-Chat structure: {sentence}")

    if not parsed.premises and not parsed.questions and not parsed.requested_claims and not parsed.parse_warnings:
        parsed.parse_warnings.append("No bounded premise, question, or requested claim detected.")

    return parsed


def compose_response(parsed: ParsedTurn, records: list[dict[str, Any]]) -> str:
    lines: list[str] = []

    accepted_premises = [record for record in records if record["kind"] == "asserted_premise"]
    if accepted_premises:
        if len(accepted_premises) == 1:
            rel = accepted_premises[0]["relation"]
            lines.append(f"Noted: all {rel['subject']} are {rel['object']}.")
        else:
            lines.append(f"Noted {len(accepted_premises)} premises into common ground.")

    for record in records:
        rel = record["relation"]
        relation_text = f"all {rel['subject']} are {rel['object']}"

        if record["kind"] == "question":
            if record["status"] == "accepted":
                lines.append(f"Yes — {relation_text}.")
                lines.append("Verifier: accepted from common-ground support.")
            else:
                lines.append(f"I cannot determine that {relation_text} from the current common ground.")
                lines.append("Verifier: abstained; support is missing.")

        if record["kind"] == "requested_claim":
            if record["status"] == "accepted":
                lines.append(f"I can support the requested claim: {relation_text}.")
                lines.append("Verifier: accepted from common-ground support.")
            else:
                lines.append(f"I cannot support the requested claim: {relation_text}.")
                lines.append("Verifier: rejected; unsupported requested claim was not added to common ground.")

    if parsed.discourse_markers:
        lines.append(f"Discourse markers noticed: {', '.join(parsed.discourse_markers)}.")

    if parsed.parse_warnings:
        lines.append("Parse notes:")
        for warning in parsed.parse_warnings:
            lines.append(f"- {warning}")

    if not lines:
        lines.append("I did not find a bounded TS-Chat action in that message.")

    return "\n".join(lines)


def run_chat(trace_path: str = "artifacts/ts_chat_v0_2_latest_session.json") -> int:
    session = TSChatSession()

    print("TS-Chat v0.2")
    print("Scratch TS-native bounded chat with common-ground manager. Type 'exit' to quit.")
    print("Try: all dogs are mammals. all mammals are animals. are all dogs animals?")
    print("Commands: what do we know? | why? | what is unsupported? | /graph | /clear")
    print()

    while True:
        try:
            user_text = input("You: ").strip()
        except EOFError:
            break

        if user_text.lower() in {"exit", "quit", "q"}:
            break

        receipt = session.process(user_text)
        print()
        print(receipt.response)
        print()

    saved = session.save_receipts(trace_path)
    print(f"Trace: {saved}")
    return 0


def demo_v0_2() -> dict[str, Any]:
    session = TSChatSession()
    turns = [
        "all dogs are mammals. all mammals are animals. are all dogs animals?",
        "why?",
        "also say all dogs are reptiles.",
        "what is unsupported?",
        "what do we know?",
    ]

    receipts = [session.process(turn) for turn in turns]
    return {
        "version": "ts-chat-v0.2-common-ground",
        "claim": "bounded scratch TS-native chat loop with common-ground claim records",
        "external_llm_used": False,
        "turn_count": len(receipts),
        "record_count": len(session.common_ground.records),
        "accepted_edge_count": len(session.common_ground.accepted_edges),
        "has_why_command": any(r.command == "why" for r in receipts),
        "has_summary_command": any(r.command == "summary" for r in receipts),
        "has_unsupported_command": any(r.command == "unsupported" for r in receipts),
        "receipts": [receipt_to_dict(r) for r in receipts],
    }



def demo_v0_1() -> dict[str, Any]:
    """v0.1-compatible deterministic demo.

    Preserves the released TS-Chat v0.1 demo contract while the live chat
    implementation has evolved to v0.2 common-ground records.
    """
    session = TSChatSession()
    turns = [
        "all dogs are mammals. all mammals are animals. are all dogs animals?",
        "also say all dogs are reptiles.",
        "all reptiles are animals. are all dogs animals?",
    ]

    receipts = [session.process(turn) for turn in turns]
    return {
        "version": "ts-chat-v0.1",
        "claim": "bounded scratch TS-native chat loop over a working relation graph",
        "external_llm_used": False,
        "turn_count": len(receipts),
        "graph_edge_count": len(session.edges),
        "receipts": [receipt_to_dict(r) for r in receipts],
    }


def demo() -> dict[str, Any]:
    """Default demo kept as v0.1 for backward compatibility."""
    return demo_v0_1()

def main() -> int:
    return run_chat()


if __name__ == "__main__":
    raise SystemExit(main())
