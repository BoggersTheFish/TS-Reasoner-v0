from __future__ import annotations

from pathlib import Path

from ts_agl.core.types import ResultPacket, TSCall


class FilesystemAdapter:
    """Read-only filesystem adapter for TS-AGL v0."""

    def execute(self, call: TSCall) -> ResultPacket:
        if call.operation == "pwd":
            return ResultPacket(
                status="success",
                system=call.system,
                operation=call.operation,
                data={"cwd": str(Path.cwd())},
                mutated_state=False,
            )

        if call.operation == "list_files":
            path = Path(call.args.get("path", "."))
            if not path.exists():
                return ResultPacket(
                    status="failed",
                    system=call.system,
                    operation=call.operation,
                    error=f"Path does not exist: {path}",
                    mutated_state=False,
                )
            entries = sorted(p.name for p in path.iterdir())
            return ResultPacket(
                status="success",
                system=call.system,
                operation=call.operation,
                data={"path": str(path), "entries": entries},
                mutated_state=False,
            )

        return ResultPacket(
            status="failed",
            system=call.system,
            operation=call.operation,
            error=f"Unknown filesystem operation: {call.operation}",
            mutated_state=False,
        )
