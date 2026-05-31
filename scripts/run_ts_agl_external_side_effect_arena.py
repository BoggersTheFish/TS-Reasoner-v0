from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_agl.arena.external_side_effect_arena import run_external_side_effect_arena


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the v16.0 TS-AGL external side-effect staging arena.")
    parser.add_argument("--receipt", default="artifacts/ts_agl_external_side_effect_staging_receipt.json")
    args = parser.parse_args()

    result = run_external_side_effect_arena()
    payload = result.to_dict()

    path = Path(args.receipt)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
