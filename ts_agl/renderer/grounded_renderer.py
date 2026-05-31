from __future__ import annotations

from typing import Iterable, List

from ts_agl.core.types import ResultPacket


def _render_git_status(result: ResultPacket) -> str:
    data = result.data
    clean = data.get("clean")
    branch = data.get("branch") or "unknown branch"
    upstream = data.get("upstream") or "no upstream detected"
    dirty_lines = data.get("status_short", [])

    if clean:
        return f"Repo is clean. Current branch: {branch}. Upstream: {upstream}."
    return f"Repo is not clean. Current branch: {branch}. Dirty entries: {len(dirty_lines)}."


def _render_current_tag(result: ResultPacket) -> str:
    data = result.data
    tags_at_head = data.get("tags_at_head", [])
    latest = data.get("latest_reachable_tag")
    if tags_at_head:
        return f"HEAD is tagged: {', '.join(tags_at_head)}. Latest reachable tag: {latest or 'unknown'}."
    return f"HEAD is not currently tagged. Latest reachable tag: {latest or 'none found'}."


def _render_next_action(result: ResultPacket) -> str:
    return str(result.data.get("next_safe_action", "No next action returned."))


def render_results(results: Iterable[ResultPacket]) -> str:
    chunks: List[str] = []

    for result in results:
        if result.status == "missing_slots":
            missing = result.data.get("missing_slots", [])
            chunks.append(f"I need more information before calling `{result.operation}`. Missing: {', '.join(missing)}.")
            continue

        if result.status == "needs_confirmation":
            chunks.append(f"`{result.operation}` is not read-only. I staged it but did not execute it.")
            continue

        if result.status == "failed":
            chunks.append(f"`{result.operation}` failed: {result.error}")
            continue

        if result.system == "git_repo" and result.operation == "git_status":
            chunks.append(_render_git_status(result))
        elif result.system == "git_repo" and result.operation == "current_tag":
            chunks.append(_render_current_tag(result))
        elif result.system == "git_repo" and result.operation == "next_safe_release_action":
            chunks.append(_render_next_action(result))
        elif result.system == "ts_reasoner" and result.operation == "summarize_session":
            chunks.append(str(result.data.get("summary")))
        elif result.system == "ts_reasoner" and result.operation == "check_support":
            if result.status == "abstained":
                chunks.append(str(result.data.get("reason")))
            else:
                chunks.append(f"Support check result: {result.data}")
        elif result.system == "ts_reasoner" and result.operation == "explain_rejection":
            chunks.append(str(result.data.get("explanation")))
        elif result.system == "ts_reasoner" and result.operation == "correct_candidate":
            chunks.append("Correction recorded as candidate language state. Accepted graph state was not changed.")
        else:
            chunks.append(f"`{result.operation}` returned `{result.status}` with data: {result.data}")

    if not chunks:
        return "No TS-AGL results to render."

    return " ".join(chunks)
