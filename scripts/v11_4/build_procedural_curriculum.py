from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.gpt2_boundary.procedural_curriculum import CurriculumConfig, generate_curriculum

CONFIG = ROOT / "data" / "v11_4" / "procedural_curriculum_config.json"
OUT = ROOT / "artifacts" / "v11_4" / "procedural_curriculum.jsonl"


def main() -> None:
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    config = CurriculumConfig(**payload)
    tasks = generate_curriculum(config)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "\n".join(json.dumps(task, sort_keys=True) for task in tasks) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"wrote": str(OUT), "task_count": len(tasks)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
