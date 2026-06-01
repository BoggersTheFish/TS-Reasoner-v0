#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_agl.os.first_contact_demo import write_first_contact_demo


def main() -> int:
    payload = write_first_contact_demo(
        ROOT / "artifacts" / "first_contact_demo_report.json",
        ROOT / "artifacts" / "first_contact_demo_receipt.json",
    )
    checks = payload["checks"]
    print("TS-Reasoner first-contact demo passed." if payload["all_gates_passed"] else "TS-Reasoner first-contact demo failed.")
    print()
    print(f"Safe route: {'PASS' if checks['safe_route'] else 'FAIL'}")
    print(f"Unsafe abstention: {'PASS' if checks['unsafe_abstention'] else 'FAIL'}")
    print(f"External side effect blocked: {'PASS' if checks['external_side_effect_blocked'] else 'FAIL'}")
    print(f"Typed proof boundary: {'PASS' if checks['typed_proof_boundary'] else 'FAIL'}")
    print(f"Receipt written: {'PASS' if checks['receipt_written'] else 'FAIL'}")
    return 0 if payload["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
