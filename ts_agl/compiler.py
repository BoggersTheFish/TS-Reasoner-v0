"""TS-AGL natural-language to typed-plan compiler CLI."""

from __future__ import annotations

import argparse
import json

from ts_reasoner.research_os import TSAGLPlanCompiler


def compile_intent(intent: str) -> dict[str, object]:
    return TSAGLPlanCompiler().compile(intent).to_dict()


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile natural language into a typed TS-AGL operation plan.")
    parser.add_argument("intent", help="Natural-language operation intent.")
    args = parser.parse_args()
    print(json.dumps(compile_intent(args.intent), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
