#!/usr/bin/env python3
"""Failing wrapper for v8.0 release authority sync."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "scripts" / "v8_0" / "audit_release_authority.py"


def main() -> int:
    result = subprocess.run([sys.executable, str(AUDIT)], cwd=ROOT)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
