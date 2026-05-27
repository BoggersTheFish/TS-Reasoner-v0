#!/usr/bin/env python3
"""Build the controlled learned-candidate dataset."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ts_reasoner.learned_model.dataset import write_split_files


def main() -> None:
    write_split_files(ROOT)


if __name__ == "__main__":
    main()
