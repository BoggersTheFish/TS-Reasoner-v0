#!/usr/bin/env python3
"""Run the grant-facing learned-candidate demo."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.learned_model.dataset import candidate, label_case, load_cases, write_split_files
from ts_reasoner.learned_model.infer import verify_scored_case
from ts_reasoner.learned_model.model import TinyCandidateModel
from ts_reasoner.learned_model.train import train_model


def ensure_model(model_path: Path) -> TinyCandidateModel:
    if not model_path.exists():
        write_split_files(ROOT)
        train_model(load_cases(ROOT / "data/learned_candidate_model_train.jsonl")).save(model_path)
    return TinyCandidateModel.load(model_path)


def demo_case() -> dict:
    return label_case(
        {
            "split": "demo",
            "case_id": "demo_grant_deeper_chain",
            "input_text": "All A are B. All B are C. All C are D. Are all A D?",
            "candidates": [
                candidate("demo_accept_all_a_d", "All A are D", 0.55),
                candidate("demo_reject_reverse_d_a", "All D are A", 0.96),
                candidate("demo_reject_identity_a_d", "A equals D", 0.88),
            ],
            "tags": ["deeper_chain", "grant_demo", "high_confidence_wrong"],
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="artifacts/learned_candidate_model.json")
    parser.add_argument("--out", default="artifacts/learned_candidate_model_demo.json")
    args = parser.parse_args()

    model = ensure_model(ROOT / args.model)
    payload = verify_scored_case(model, demo_case())
    result = {
        "title": "TS-Reasoner v2.0.0: Learned Candidate Model Demo",
        "premises": ["All A are B", "All B are C", "All C are D"],
        "question": "Are all A D?",
        "model_proposes": [
            {
                "candidate_id": item["candidate_id"],
                "claim": item["claim"],
                "input_candidate_confidence": item["confidence"],
                "learned_ranking_score": item["prediction"]["ranking_score"],
                "learned_model_confidence": item["prediction"]["model_confidence"],
                "predicted_status": item["prediction"]["status"],
                "predicted_channels": item["prediction"]["channels"],
            }
            for item in payload["scored_candidates"]
        ],
        "verifier_returns": {
            "accepted": payload["verification"]["accepted"],
            "rejected": [
                {
                    "claim": item["claim"],
                    "reason": item["reason"],
                    "channels": item["channels"],
                }
                for item in payload["verification"]["candidate_results"]
                if item["status"] == "rejected"
            ],
            "abstained": payload["verification"]["abstained"],
        },
        "trace": {
            "transitivity_activated": any(
                "logic_transitivity" in item["channels"]
                for item in payload["verification"]["candidate_results"]
            ),
            "directionality_activated": any(
                "directionality" in item["channels"]
                for item in payload["verification"]["candidate_results"]
            ),
            "identity_preservation_activated": any(
                "identity_preservation" in item["channels"]
                for item in payload["verification"]["candidate_results"]
            ),
            "surface_structure_tagged_inference": any(
                "inferred"
                in result.get("typed_runtime", {}).get("context", {}).get("surface_tags", {}).values()
                for result in payload["verification"]["candidate_results"]
            ),
            "candidate_graph_contamination_count": sum(
                1
                for item in payload["verification"]["candidate_results"]
                for status in item.get("typed_runtime", {}).get("context", {}).get("surface_tags", {}).values()
                if status == "candidate"
            ),
        },
        "boundary": "The learned model proposes/ranks candidates. TS-Reasoner typed channels verify. Confidence is metadata, not proof.",
        "raw_payload": payload,
    }
    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
