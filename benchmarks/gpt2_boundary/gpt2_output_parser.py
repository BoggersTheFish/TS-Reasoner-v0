from __future__ import annotations

from ts_reasoner.runtime_kernel import normalize_claim


LABELS = ("ANSWER", "CLAIM", "SUPPORT", "STATUS")


def parse_gpt2_output(text: str) -> dict[str, str | bool]:
    parsed = {label.lower(): "" for label in LABELS}
    current: str | None = None
    for raw_line in str(text).splitlines():
        line = raw_line.strip()
        upper = line.upper()
        matched = False
        for label in LABELS:
            prefix = f"{label}:"
            if upper.startswith(prefix):
                current = label.lower()
                parsed[current] = line[len(prefix):].strip()
                matched = True
                break
        if matched:
            continue
        if current and line:
            parsed[current] = f"{parsed[current]} {line}".strip()

    answer = str(parsed["answer"]).lower().strip().strip(".")
    if answer not in {"yes", "no", "unknown"}:
        if answer.startswith("yes"):
            answer = "yes"
        elif answer.startswith("no"):
            answer = "no"
        elif "unknown" in answer or "not enough" in answer or "cannot" in answer:
            answer = "unknown"

    return {
        "answer": answer,
        "claim": normalize_claim(str(parsed["claim"])),
        "support": str(parsed["support"]).strip(),
        "status": str(parsed["status"]).lower().strip(),
        "format_parse_ok": all(bool(str(parsed[label.lower()]).strip()) for label in LABELS),
    }
