#!/usr/bin/env python3
"""Run the optional TS-Reasoner + TensionLM proposal bridge."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ts_reasoner.tensionlm_bridge import (  # noqa: E402
    PublicTensionLMProposer,
    StaticCompletionProposer,
    run_tensionlm_bridge,
)
from ts_reasoner.trace import write_json  # noqa: E402


DEFAULT_QUESTION = "If all mammals are animals and all whales are mammals, are all whales animals?"
DEFAULT_PREMISES = ["All mammals are animals.", "All whales are mammals."]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Let TensionLM propose and TS-Reasoner verify candidate chains.")
    parser.add_argument("--question", default=DEFAULT_QUESTION)
    parser.add_argument("--premise", action="append", dest="premises", default=None)
    parser.add_argument("--tensionlm-path", default="../TensionLM")
    parser.add_argument("--repo-id", default="BoggersTheFish/TensionLM-Curriculum-13M")
    parser.add_argument("--proposal-count", type=int, default=2)
    parser.add_argument("--max-new", type=int, default=32)
    parser.add_argument("--temperature", type=float, default=0.85)
    parser.add_argument("--top-p", type=float, default=0.92)
    parser.add_argument("--rep-penalty", type=float, default=1.25)
    parser.add_argument("--cache-dir", default=None)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Use deterministic local completions instead of loading a public TensionLM checkpoint.",
    )
    parser.add_argument("--out", default="artifacts/tensionlm_bridge_smoke.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    premises = args.premises if args.premises is not None else DEFAULT_PREMISES
    if args.offline:
        proposer = StaticCompletionProposer(
            [
                "Therefore all whales are animals.",
                "waves of certainty with no relation syntax",
            ],
            source="OfflineBridgeSmoke",
        )
    else:
        proposer = PublicTensionLMProposer(
            tensionlm_path=args.tensionlm_path,
            repo_id=args.repo_id,
            cache_dir=args.cache_dir,
            device=args.device,
            max_new=args.max_new,
            temperature=args.temperature,
            top_p=args.top_p,
            rep_penalty=args.rep_penalty,
        )
    output = run_tensionlm_bridge(
        question=args.question,
        premises=premises,
        proposer=proposer,
        proposal_count=args.proposal_count,
    )
    path = write_json(output, ROOT / args.out)
    summary = {
        "final_answer": output.final_answer,
        "selected_chain": output.selected_chain.chain_id,
        "global_tension": output.tension_score.global_tension,
        "trace": str(path.relative_to(ROOT)),
        "neural_generation": output.trace["neural_generation"],
        "limitation": "TensionLM is only a raw proposal source; TS-Reasoner is the verifier.",
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
