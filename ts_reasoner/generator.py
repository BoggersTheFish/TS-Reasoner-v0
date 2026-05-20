"""Deterministic candidate-chain generation.

The generator is intentionally small and auditable. It makes candidate
constraint paths from the question and supplied premises, but does not call a
language model. The TensionLMGenerator class is a future plug-in interface.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple

from .types import ReasoningChain, ReasoningStep


RELATION_RE = re.compile(
    r"\b(?P<quantifier>all|some|no)\s+(?P<subject>[A-Za-z][A-Za-z0-9_-]*)\s+"
    r"(?:are|is)\s+(?P<predicate>[A-Za-z][A-Za-z0-9_-]*)\b",
    re.IGNORECASE,
)
QUERY_RE = re.compile(
    r"\b(?:are|is)\s+(?P<quantifier>all|some|no)?\s*"
    r"(?P<subject>[A-Za-z][A-Za-z0-9_-]*)\s+"
    r"(?P<predicate>[A-Za-z][A-Za-z0-9_-]*)\??",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ParsedRelation:
    quantifier: str
    subject: str
    predicate: str
    text: str

    @property
    def normalized(self) -> str:
        return f"{self.quantifier.lower()} {self.subject.lower()} are {self.predicate.lower()}"


def extract_relations(text: str) -> List[ParsedRelation]:
    relations: List[ParsedRelation] = []
    for match in RELATION_RE.finditer(text):
        relations.append(
            ParsedRelation(
                quantifier=match.group("quantifier").lower(),
                subject=match.group("subject"),
                predicate=match.group("predicate"),
                text=match.group(0),
            )
        )
    return relations


def infer_premises_from_question(question: str) -> List[str]:
    """Pull simple natural-language premises out of an if/then-style question."""
    premise_region = re.split(r",\s*(?:are|is)\b", question, maxsplit=1, flags=re.IGNORECASE)[0]
    relations = extract_relations(premise_region)
    return [relation.text for relation in relations]


def infer_query_relation(question: str) -> Optional[ParsedRelation]:
    matches = list(QUERY_RE.finditer(question))
    if matches:
        match = matches[-1]
        quantifier = (match.group("quantifier") or "all").lower()
        return ParsedRelation(
            quantifier=quantifier,
            subject=match.group("subject"),
            predicate=match.group("predicate"),
            text=match.group(0).rstrip("?"),
        )
    relations = extract_relations(question)
    if relations:
        return relations[-1]
    return None


def _step(step_id: str, text: str, kind: str, deps: Sequence[str], confidence: float) -> ReasoningStep:
    return ReasoningStep(
        step_id=step_id,
        text=text,
        kind=kind,
        dependencies=list(deps),
        confidence=confidence,
    )


class DeterministicHeuristicGenerator:
    """Create a small candidate set from symbolic-looking text patterns."""

    name = "DeterministicHeuristicGenerator"

    def generate(self, question: str, premises: Optional[Iterable[str]] = None) -> List[ReasoningChain]:
        premise_list = [p.strip() for p in premises or infer_premises_from_question(question) if p.strip()]
        query = infer_query_relation(question)
        premise_relations = [rel for premise in premise_list for rel in extract_relations(premise)]
        candidates = [
            self._candidate_direct(question, premise_list, premise_relations, query),
            self._candidate_cautious(question, premise_list, premise_relations, query),
        ]
        contradiction = self._candidate_contradiction(question, premise_list, premise_relations, query)
        if contradiction is not None:
            candidates.append(contradiction)
        return candidates

    def _premise_steps(self, premises: Sequence[str]) -> List[ReasoningStep]:
        return [
            _step(f"p{i + 1}", premise, "premise", [], 0.9)
            for i, premise in enumerate(premises)
        ]

    def _candidate_direct(
        self,
        question: str,
        premises: Sequence[str],
        relations: Sequence[ParsedRelation],
        query: Optional[ParsedRelation],
    ) -> ReasoningChain:
        steps = self._premise_steps(premises)
        deps = [step.step_id for step in steps]
        conclusion = self._direct_conclusion(relations, query)
        steps.append(_step("s1", conclusion, "conclusion", deps, 0.78))
        return ReasoningChain(
            chain_id="candidate_direct",
            question=question,
            premises=list(premises),
            steps=steps,
            final_answer=self._answer_from_conclusion(conclusion),
        )

    def _candidate_cautious(
        self,
        question: str,
        premises: Sequence[str],
        relations: Sequence[ParsedRelation],
        query: Optional[ParsedRelation],
    ) -> ReasoningChain:
        steps = self._premise_steps(premises)
        deps = [step.step_id for step in steps]
        if query is None:
            text = "The available premises are not enough to derive a definite answer."
        elif self._has_all_all_bridge(relations, query):
            text = f"Therefore all {query.subject} are {query.predicate}."
        else:
            text = (
                f"The premises do not force the requested universal relation between {query.subject} and {query.predicate}; "
                "more information is needed."
            )
        steps.append(_step("s1", text, "conclusion", deps, 0.64))
        return ReasoningChain(
            chain_id="candidate_cautious",
            question=question,
            premises=list(premises),
            steps=steps,
            final_answer=self._answer_from_conclusion(text),
        )

    def _candidate_contradiction(
        self,
        question: str,
        premises: Sequence[str],
        relations: Sequence[ParsedRelation],
        query: Optional[ParsedRelation],
    ) -> Optional[ReasoningChain]:
        if query is None:
            return None
        if not any(self._is_negative_pair(relation, query) for relation in relations):
            return None
        steps = self._premise_steps(premises)
        deps = [step.step_id for step in steps]
        text = (
            f"A contradiction touches {query.subject} and {query.predicate}, "
            "so the answer is unstable under the stated premises."
        )
        steps.append(_step("s1", text, "conclusion", deps, 0.45))
        return ReasoningChain(
            chain_id="candidate_a_contradiction_aware",
            question=question,
            premises=list(premises),
            steps=steps,
            final_answer="Contradiction detected; no stable answer follows.",
        )

    def _direct_conclusion(
        self, relations: Sequence[ParsedRelation], query: Optional[ParsedRelation]
    ) -> str:
        if query is None:
            return "Therefore the answer cannot be derived from the current premises."
        if self._has_all_all_bridge(relations, query):
            return f"Therefore all {query.subject} are {query.predicate}."
        if self._has_some_bridge(relations, query):
            return f"Therefore all {query.subject} are {query.predicate}."
        if any(self._same_relation(relation, query) for relation in relations):
            return f"Therefore {query.text}."
        return f"Therefore all {query.subject} are {query.predicate}."

    def _has_all_all_bridge(self, relations: Sequence[ParsedRelation], query: ParsedRelation) -> bool:
        for left in relations:
            for right in relations:
                if (
                    left.quantifier == "all"
                    and right.quantifier == "all"
                    and left.subject.lower() == query.subject.lower()
                    and left.predicate.lower() == right.subject.lower()
                    and right.predicate.lower() == query.predicate.lower()
                ):
                    return True
        return False

    def _has_some_bridge(self, relations: Sequence[ParsedRelation], query: ParsedRelation) -> bool:
        for left in relations:
            for right in relations:
                if (
                    left.quantifier == "some"
                    and right.quantifier == "all"
                    and left.subject.lower() == query.subject.lower()
                    and left.predicate.lower() == right.subject.lower()
                    and right.predicate.lower() == query.predicate.lower()
                ):
                    return True
        return False

    def _is_negative_pair(self, relation: ParsedRelation, query: ParsedRelation) -> bool:
        return (
            relation.quantifier == "no"
            and relation.subject.lower() == query.subject.lower()
            and relation.predicate.lower() == query.predicate.lower()
        )

    def _same_relation(self, relation: ParsedRelation, query: ParsedRelation) -> bool:
        return (
            relation.quantifier == query.quantifier
            and relation.subject.lower() == query.subject.lower()
            and relation.predicate.lower() == query.predicate.lower()
        )

    def _answer_from_conclusion(self, conclusion: str) -> str:
        lower = conclusion.lower()
        if "not force" in lower or "not enough" in lower or "cannot be derived" in lower:
            return "Not enough information."
        if "contradiction" in lower:
            return "Contradiction detected."
        if "therefore" in lower:
            return conclusion.replace("Therefore ", "", 1).strip()
        return conclusion


class TensionLMGenerator:
    """Future interface for plugging a learned TensionLM candidate generator."""

    name = "TensionLMGenerator"

    def generate(self, question: str, premises: Optional[Iterable[str]] = None) -> List[ReasoningChain]:
        raise NotImplementedError(
            "TensionLM generation is intentionally not bundled in v0. "
            "Use DeterministicHeuristicGenerator for this release."
        )
