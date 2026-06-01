#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.proof_object_examples import write_proof_object_examples


def main() -> int:
    payload = write_proof_object_examples(ROOT / "artifacts" / "proof_object_examples.json")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
