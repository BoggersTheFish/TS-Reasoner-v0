"""TS-Chat v0.1.

Scratch TS-native chat loop.

This is deliberately not an LLM and does not call external models.
It is a bounded conversational interface over a small working meaning graph:

- parse simple all-X-are-Y premises
- parse simple all-X-are-Y questions
- parse requested extra claims
- verify typed support by transitive closure
- reject unsupported requested claims
- respond in natural-ish language
- emit inspectable receipts

The point is to expose failures rather than hide them.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ts_reasoner.answer_arena import (
    Relation,
    extract_all_relation,
    extract_question_relation,
    normalize_term,
    premise_edges,
    transitive_closure,
)


ASK_RE = re.compile(r"\b(?:are|is)\s+all\s+.+?[?]", re.IGNORECASE)
REQUEST_RE = re.compile(
    r"\b(?:say|claim|also say|include)\s+(?:that\s+)?(?:all\s+)?(.+?)\s+(?:are|is)\s+(.+?)(?:[.?!,;:]|$)",
    re.IGNORECASE,
)


@dataclass
class ParsedTurn:
    raw_text: str
    premises: list[Relation] = field(default_factory=list)
    questions: list[Relation] = field(default_factory=list)
    requested_claims: list[Relation] = field(default_factory=list)
    parse_warnings: list[str] = field(default_factory=list)


@dataclass
class ChatDecision:
    relation: Relation
    kind: str
    status: str
    typed_supported: bool
    reason: str


@dataclass
class ChatTurnReceipt:
    user_text: str
    parsed_premises: list[dict[str, str]]
    parsed_questions: list[dict[str, str]]
    requested_claims: list[dict[str, str]]
    decisions: list[dict[str, Any]]
    response: str
    graph_edge_count: int
    parse_warnings: list[str]


class TSChatSession:
    """Small stateful chat session backed by a working relation graph."""

    def __init__(self) -> None:
        self.edges: set[tuple[str, str]] = set()
        self.turn_receipts: list[ChatTurnReceipt] = []

    def closure(self) -> set[tuple[str, str]]:
        return transitive_closure(set(self.edges))

    def add_premise(self, relation: Relation) -> None:
        self.edges.add((relation.subject, relation.object))

    def relation_supported(self, relation: Relation) -> bool:
        return (relation.subject, relation.object) in self.closure()

    def process(self, user_text: str) -> ChatTurnReceipt:
        parsed = parse_turn(user_text)

        for premise in parsed.premises:
            self.add_premise(premise)

        decisions: list[ChatDecision] = []

        for question in parsed.questions:
            supported = self.relation_supported(question)
            decisions.append(
                ChatDecision(
                    relation=question,
                    kind="question",
                    status="accepted" if supported else "abstained",
                    typed_supported=supported,
                    reason=(
                        "typed transitive support exists"
                        if supported
                        else "no typed support exists in the current working graph"
                    ),
                )
            )

        for requested in parsed.requested_claims:
            supported = self.relation_supported(requested)
            decisions.append(
                ChatDecision(
                    relation=requested,
                    kind="requested_claim",
                    status="accepted" if supported else "rejected",
                    typed_supported=supported,
                    reason=(
                        "requested claim is supported by the working graph"
                        if supported
                        else "requested claim is unsupported and will not be asserted"
                    ),
                )
            )

        response = compose_response(parsed, decisions)

        receipt = ChatTurnReceipt(
            user_text=user_text,
            parsed_premises=[relation_to_dict(r) for r in parsed.premises],
            parsed_questions=[relation_to_dict(r) for r in parsed.questions],
            requested_claims=[relation_to_dict(r) for r in parsed.requested_claims],
            decisions=[decision_to_dict(d) for d in decisions],
            response=response,
            graph_edge_count=len(self.edges),
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


def relation_to_dict(relation: Relation) -> dict[str, str]:
    return {"subject": relation.subject, "object": relation.object}


def decision_to_dict(decision: ChatDecision) -> dict[str, Any]:
    return {
        "relation": relation_to_dict(decision.relation),
        "kind": decision.kind,
        "status": decision.status,
        "typed_supported": decision.typed_supported,
        "reason": decision.reason,
    }


def receipt_to_dict(receipt: ChatTurnReceipt) -> dict[str, Any]:
    return {
        "user_text": receipt.user_text,
        "parsed_premises": receipt.parsed_premises,
        "parsed_questions": receipt.parsed_questions,
        "requested_claims": receipt.requested_claims,
        "decisions": receipt.decisions,
        "response": receipt.response,
        "graph_edge_count": receipt.graph_edge_count,
        "parse_warnings": receipt.parse_warnings,
    }


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.?!])\s+", text.strip())
    return [part.strip() for part in parts if part.strip()]


def parse_requested_claim(sentence: str) -> Relation | None:
    match = REQUEST_RE.search(sentence)
    if not match:
        return None
    return Relation(normalize_term(match.group(1)), normalize_term(match.group(2)))


def parse_turn(user_text: str) -> ParsedTurn:
    parsed = ParsedTurn(raw_text=user_text)
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


def human_relation(relation: Relation) -> str:
    return f"all {relation.subject} are {relation.object}"


def compose_response(parsed: ParsedTurn, decisions: list[ChatDecision]) -> str:
    lines: list[str] = []

    if parsed.premises:
        if len(parsed.premises) == 1:
            lines.append(f"Noted: {human_relation(parsed.premises[0])}.")
        else:
            lines.append(f"Noted {len(parsed.premises)} premises.")

    for decision in decisions:
        relation_text = human_relation(decision.relation)

        if decision.kind == "question":
            if decision.status == "accepted":
                lines.append(f"Yes — {relation_text}.")
                lines.append(f"Verifier: accepted; {decision.reason}.")
            else:
                lines.append(f"I cannot determine that {relation_text} from the current premises.")
                lines.append(f"Verifier: abstained; {decision.reason}.")

        if decision.kind == "requested_claim":
            if decision.status == "accepted":
                lines.append(f"I can support the requested claim: {relation_text}.")
                lines.append(f"Verifier: accepted; {decision.reason}.")
            else:
                lines.append(f"I cannot support the requested claim: {relation_text}.")
                lines.append(f"Verifier: rejected; {decision.reason}.")

    if parsed.parse_warnings:
        lines.append("Parse notes:")
        for warning in parsed.parse_warnings:
            lines.append(f"- {warning}")

    if not lines:
        lines.append("I did not find a bounded TS-Chat action in that message.")

    return "\n".join(lines)


def run_chat(trace_path: str = "artifacts/ts_chat_v0_1_latest_session.json") -> int:
    session = TSChatSession()

    print("TS-Chat v0.1")
    print("Scratch TS-native bounded chat. Type 'exit' to quit.")
    print("Try: all dogs are mammals. all mammals are animals. are all dogs animals?")
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


def demo() -> dict[str, Any]:
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


def main() -> int:
    return run_chat()


if __name__ == "__main__":
    raise SystemExit(main())
