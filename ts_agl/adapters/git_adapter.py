from __future__ import annotations

from pathlib import Path
from subprocess import CompletedProcess, run
from typing import Dict, List

from ts_agl.core.types import ResultPacket, TSCall


class GitAdapter:
    """Read-only local git adapter for TS-AGL v0."""

    def _git(self, args: List[str]) -> CompletedProcess[str]:
        return run(["git", *args], text=True, capture_output=True, check=False)

    def _status_data(self) -> Dict[str, object]:
        short = self._git(["status", "--short"])
        branch = self._git(["branch", "--show-current"])
        upstream = self._git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
        clean = short.returncode == 0 and short.stdout.strip() == ""

        return {
            "cwd": str(Path.cwd()),
            "branch": branch.stdout.strip() if branch.returncode == 0 else None,
            "upstream": upstream.stdout.strip() if upstream.returncode == 0 else None,
            "clean": clean,
            "status_short": short.stdout.strip().splitlines() if short.stdout.strip() else [],
            "git_status_returncode": short.returncode,
            "git_status_stderr": short.stderr.strip(),
        }

    def execute(self, call: TSCall) -> ResultPacket:
        if call.operation == "git_status":
            return ResultPacket(
                status="success",
                system=call.system,
                operation=call.operation,
                data=self._status_data(),
                mutated_state=False,
            )

        if call.operation == "current_tag":
            points = self._git(["tag", "--points-at", "HEAD"])
            latest = self._git(["describe", "--tags", "--abbrev=0"])
            return ResultPacket(
                status="success" if points.returncode == 0 else "failed",
                system=call.system,
                operation=call.operation,
                data={
                    "tags_at_head": points.stdout.strip().splitlines() if points.stdout.strip() else [],
                    "latest_reachable_tag": latest.stdout.strip() if latest.returncode == 0 else None,
                    "points_at_head_stderr": points.stderr.strip(),
                    "latest_tag_stderr": latest.stderr.strip(),
                },
                error=None if points.returncode == 0 else points.stderr.strip(),
                mutated_state=False,
            )

        if call.operation == "next_safe_release_action":
            status = self._status_data()
            points = self._git(["tag", "--points-at", "HEAD"])
            tags_at_head = points.stdout.strip().splitlines() if points.stdout.strip() else []

            if not status["clean"]:
                action = "Do not release yet. Review or restore the dirty worktree first."
            elif tags_at_head:
                action = f"HEAD is already tagged ({', '.join(tags_at_head)}). Start a new experiment branch for the next feature."
            else:
                action = "Worktree is clean but HEAD is not tagged. Run tests, then decide whether this commit should be tagged or branched."

            return ResultPacket(
                status="success",
                system=call.system,
                operation=call.operation,
                data={
                    "status": status,
                    "tags_at_head": tags_at_head,
                    "next_safe_action": action,
                },
                mutated_state=False,
            )

        return ResultPacket(
            status="failed",
            system=call.system,
            operation=call.operation,
            error=f"Unknown git operation: {call.operation}",
            mutated_state=False,
        )
