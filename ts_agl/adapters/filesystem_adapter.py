from __future__ import annotations

from pathlib import Path

from ts_agl.core.types import ResultPacket, TSCall


class FilesystemAdapter:
    """Filesystem adapter for TS-AGL.

    Read operations are unrestricted inside the current repo.
    Write operations are deliberately restricted to artifacts/ so the safe-write
    arena can prove confirmation gating without destructive behavior.
    """

    def _safe_artifact_path(self, raw_path: str) -> Path:
        root = Path.cwd().resolve()
        artifacts_root = (root / "artifacts").resolve()
        target = (root / raw_path).resolve()

        if artifacts_root != target and artifacts_root not in target.parents:
            raise ValueError(f"Refusing to write outside artifacts/: {raw_path}")

        return target

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

        if call.operation == "write_text_file":
            raw_path = call.args.get("path")
            content = call.args.get("content")

            if not raw_path or content is None:
                missing = []
                if not raw_path:
                    missing.append("path")
                if content is None:
                    missing.append("content")
                return ResultPacket(
                    status="missing_slots",
                    system=call.system,
                    operation=call.operation,
                    data={"missing_slots": missing},
                    mutated_state=False,
                )

            try:
                target = self._safe_artifact_path(str(raw_path))
            except ValueError as exc:
                return ResultPacket(
                    status="failed",
                    system=call.system,
                    operation=call.operation,
                    error=str(exc),
                    mutated_state=False,
                )

            existed_before = target.exists()
            previous_content = target.read_text(encoding="utf-8") if existed_before else None
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(str(content), encoding="utf-8")

            return ResultPacket(
                status="success",
                system=call.system,
                operation=call.operation,
                data={
                    "path": str(target.relative_to(Path.cwd())),
                    "existed_before": existed_before,
                    "previous_content_sha_known": previous_content is not None,
                    "bytes_written": len(str(content).encode("utf-8")),
                    "reversible_write": True,
                },
                mutated_state=True,
            )

        return ResultPacket(
            status="failed",
            system=call.system,
            operation=call.operation,
            error=f"Unknown filesystem operation: {call.operation}",
            mutated_state=False,
        )
