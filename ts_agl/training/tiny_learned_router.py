from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple
import json
import math
import re

from ts_agl.core.types import LanguageMove, TSCall
from ts_agl.router.operation_router import OperationRouter
from ts_agl.registry import DomainRegistry


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9_]+", text.lower())


@dataclass(frozen=True)
class TinyRouterPrediction:
    domain: str
    operation: str
    score: float
    abstained: bool
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "operation": self.operation,
            "score": self.score,
            "abstained": self.abstained,
            "reason": self.reason,
        }


class TinyLearnedAGLRouter:
    """Dependency-free learned-ish router from TS-AGL routing rows.

    It is a tiny multinomial Naive Bayes classifier over token counts.

    Boundary:
    - proposer only
    - confidence is not proof
    - low-confidence predictions abstain to route_unknown
    - TSCall still goes through the normal operation router/risk gates
    """

    def __init__(
        self,
        class_token_counts: Dict[str, Dict[str, int]],
        class_counts: Dict[str, int],
        vocabulary: List[str],
        threshold: float = 0.55,
    ) -> None:
        self.class_token_counts = class_token_counts
        self.class_counts = class_counts
        self.vocabulary = sorted(vocabulary)
        self.threshold = threshold

    @staticmethod
    def class_name(domain: str, operation: str) -> str:
        return f"{domain}.{operation}"

    @staticmethod
    def split_class_name(name: str) -> Tuple[str, str]:
        if "." not in name:
            return "ts_reasoner", "route_unknown"
        domain, operation = name.split(".", 1)
        return domain, operation

    @classmethod
    def train(cls, rows: Iterable[Dict[str, Any]], threshold: float = 0.55) -> "TinyLearnedAGLRouter":
        class_counts: Dict[str, int] = {}
        token_counts: Dict[str, Dict[str, int]] = {}
        vocabulary = set()

        for row in rows:
            label = row.get("label")
            if label == "abstain":
                class_name = "ts_reasoner.route_unknown"
            else:
                class_name = cls.class_name(row["expected_domain"], row["expected_operation"])

            class_counts[class_name] = class_counts.get(class_name, 0) + 1
            token_counts.setdefault(class_name, {})

            for token in tokenize(row["text"]):
                vocabulary.add(token)
                token_counts[class_name][token] = token_counts[class_name].get(token, 0) + 1

        if not class_counts:
            raise ValueError("Cannot train TinyLearnedAGLRouter on empty rows.")

        return cls(
            class_token_counts=token_counts,
            class_counts=class_counts,
            vocabulary=sorted(vocabulary),
            threshold=threshold,
        )

    def predict(self, text: str) -> TinyRouterPrediction:
        tokens = tokenize(text)
        if not tokens:
            return TinyRouterPrediction(
                domain="ts_reasoner",
                operation="route_unknown",
                score=0.0,
                abstained=True,
                reason="empty_input",
            )

        total_docs = sum(self.class_counts.values())
        vocab_size = max(1, len(self.vocabulary))

        log_scores: Dict[str, float] = {}
        for class_name, class_count in self.class_counts.items():
            prior = math.log(class_count / total_docs)
            token_count_map = self.class_token_counts.get(class_name, {})
            total_tokens = sum(token_count_map.values())

            log_score = prior
            for token in tokens:
                count = token_count_map.get(token, 0)
                log_score += math.log((count + 1) / (total_tokens + vocab_size))
            log_scores[class_name] = log_score

        max_log = max(log_scores.values())
        exp_scores = {
            class_name: math.exp(value - max_log)
            for class_name, value in log_scores.items()
        }
        denom = sum(exp_scores.values())
        probs = {
            class_name: value / denom
            for class_name, value in exp_scores.items()
        }

        best_class = max(probs, key=probs.get)
        score = probs[best_class]

        if score < self.threshold:
            return TinyRouterPrediction(
                domain="ts_reasoner",
                operation="route_unknown",
                score=score,
                abstained=True,
                reason="below_threshold",
            )

        domain, operation = self.split_class_name(best_class)
        abstained = best_class == "ts_reasoner.route_unknown"
        return TinyRouterPrediction(
            domain=domain,
            operation=operation,
            score=score,
            abstained=abstained,
            reason="route_unknown_class" if abstained else "predicted",
        )

    def route_to_call(self, text: str, registry: DomainRegistry | None = None) -> TSCall:
        registry = registry or DomainRegistry().load()
        router = OperationRouter(registry)
        prediction = self.predict(text)

        move = LanguageMove(
            move_type="ASK" if prediction.abstained else "EXECUTE",
            raw_text=text,
            target=prediction.domain,
            content=text,
            slots={"utterance": text} if prediction.abstained else {},
            operation_hint=prediction.operation,
            domain_hint=prediction.domain,
            confidence=prediction.score,
        )
        return router.route(move)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_type": "tiny_multinomial_naive_bayes_router",
            "threshold": self.threshold,
            "class_counts": self.class_counts,
            "class_token_counts": self.class_token_counts,
            "vocabulary": self.vocabulary,
            "boundary": {
                "proposer_only": True,
                "confidence_is_not_proof": True,
                "language_layer_is_not_proof_authority": True,
            },
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "TinyLearnedAGLRouter":
        return cls(
            class_token_counts={
                key: {token: int(count) for token, count in value.items()}
                for key, value in payload["class_token_counts"].items()
            },
            class_counts={key: int(value) for key, value in payload["class_counts"].items()},
            vocabulary=list(payload["vocabulary"]),
            threshold=float(payload.get("threshold", 0.55)),
        )


def load_router_dataset(path: str | Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def save_tiny_router(model: TinyLearnedAGLRouter, path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(model.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_tiny_router(path: str | Path) -> TinyLearnedAGLRouter:
    return TinyLearnedAGLRouter.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
