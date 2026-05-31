from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_agl.core.types import AGLTrace
from ts_agl.parser import parse_language_moves
from ts_agl.registry import DomainRegistry
from ts_agl.router import Dispatcher, OperationRouter
from ts_agl.renderer import render_results


DEFAULT_TEXT = "Check where we are in the repo and tell me the next safe release action."


def run_demo(text: str, receipt_path: str | None = "artifacts/ts_agl_demo_receipt.json") -> AGLTrace:
    registry = DomainRegistry().load()
    router = OperationRouter(registry)
    dispatcher = Dispatcher()

    moves = parse_language_moves(text)
    calls = router.route_many(moves)
    results = [dispatcher.dispatch(call) for call in calls]
    reply = render_results(results)

    trace = AGLTrace(
        raw_text=text,
        moves=moves,
        calls=calls,
        results=results,
        rendered_reply=reply,
        wrong_state_mutation_count=sum(1 for r in results if r.mutated_state),
        candidate_graph_contamination_count=0,
        external_llm_used=False,
    )

    if receipt_path:
        path = Path(receipt_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(trace.to_json() + "\n", encoding="utf-8")

    print(reply)
    print()
    print("Receipt:")
    print(json.dumps(trace.to_dict(), indent=2, sort_keys=True))

    return trace


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a TS-AGL language-to-operation demo.")
    parser.add_argument("text", nargs="*", help="Natural language request to route through TS-AGL.")
    parser.add_argument("--receipt", default="artifacts/ts_agl_demo_receipt.json")
    args = parser.parse_args()

    text = " ".join(args.text).strip() or DEFAULT_TEXT
    run_demo(text, receipt_path=args.receipt)


if __name__ == "__main__":
    main()
