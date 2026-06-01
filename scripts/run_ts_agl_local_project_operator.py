from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_agl.arena.local_project_operator import LocalProjectOperator


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the v21 local TS-AGL project operator.")
    parser.add_argument("text", nargs="*", help="Optional project operator request.")
    parser.add_argument("--receipt", default="artifacts/ts_agl_local_project_operator_receipt.json")
    args = parser.parse_args()

    raw_text = " ".join(args.text).strip() or (
        "inspect the local project, tell me the next safe action, and stage a project note"
    )
    result = LocalProjectOperator().run(raw_text)
    payload = result.to_dict()

    path = Path(args.receipt)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
