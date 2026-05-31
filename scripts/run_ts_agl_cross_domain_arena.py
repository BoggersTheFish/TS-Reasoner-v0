from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_agl.arena.cross_domain_arena import (
    DEFAULT_CROSS_DOMAIN_REQUEST,
    run_cross_domain_arena,
    summarize_cross_domain_trace,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the v13.0 cross-domain TS-AGL arena.")
    parser.add_argument("text", nargs="*", help="Optional cross-domain request text.")
    parser.add_argument("--receipt", default="artifacts/ts_agl_cross_domain_arena_receipt.json")
    args = parser.parse_args()

    text = " ".join(args.text).strip() or DEFAULT_CROSS_DOMAIN_REQUEST
    trace = run_cross_domain_arena(text)
    summary = summarize_cross_domain_trace(trace)

    path = Path(args.receipt)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(trace.rendered_reply)
    print()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
