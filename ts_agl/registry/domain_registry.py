from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import json


class DomainRegistry:
    """Loads TS-AGL domain manifests.

    v0 uses JSON to avoid adding dependencies.
    """

    def __init__(self, manifest_dir: str | Path = "ts_agl/domains") -> None:
        self.manifest_dir = Path(manifest_dir)
        self.domains: Dict[str, Dict[str, Any]] = {}

    def load(self) -> "DomainRegistry":
        self.domains.clear()
        for path in sorted(self.manifest_dir.glob("*.json")):
            with path.open("r", encoding="utf-8") as f:
                manifest = json.load(f)
            domain_name = manifest["domain"]
            self.domains[domain_name] = manifest
        return self

    def list_domains(self) -> List[str]:
        return sorted(self.domains)

    def get_domain(self, domain: str) -> Dict[str, Any]:
        if domain not in self.domains:
            raise KeyError(f"Unknown TS-AGL domain: {domain}")
        return self.domains[domain]

    def operations(self, domain: Optional[str] = None) -> Iterable[Dict[str, Any]]:
        if domain:
            yield from self.get_domain(domain).get("operations", [])
            return
        for manifest in self.domains.values():
            yield from manifest.get("operations", [])

    def find_operation(self, domain: str, operation_name: str) -> Optional[Dict[str, Any]]:
        for op in self.operations(domain):
            if op.get("name") == operation_name:
                return op
        return None
