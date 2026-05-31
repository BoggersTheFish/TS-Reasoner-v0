from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List
import json
import re

from ts_agl.registry.manifest_validator import ALLOWED_RISKS, validate_manifest


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9_]+", "_", value.strip().lower())
    slug = re.sub(r"_+", "_", slug).strip("_")
    if not slug:
        raise ValueError("Cannot build slug from empty value.")
    return slug


@dataclass(frozen=True)
class OperationTeachingSpec:
    """Structured teaching input for one domain operation.

    This is teaching material, not proof authority.
    """

    name: str
    description: str
    required_inputs: List[str]
    risk: str
    examples: List[str]
    requires_confirmation: bool | None = None

    def to_manifest_operation(self) -> Dict[str, Any]:
        name = _slug(self.name)
        risk = self.risk

        if risk not in ALLOWED_RISKS:
            raise ValueError(f"Invalid risk level for {name}: {risk}")

        requires_confirmation = (
            risk != "read_only"
            if self.requires_confirmation is None
            else self.requires_confirmation
        )

        return {
            "name": name,
            "description": self.description.strip(),
            "required_inputs": [_slug(item) for item in self.required_inputs],
            "risk": risk,
            "requires_confirmation": bool(requires_confirmation),
            "examples": [example.strip() for example in self.examples if example.strip()],
        }


@dataclass(frozen=True)
class DomainTeachingSpec:
    """Structured teaching input for a TS-AGL domain pack."""

    domain: str
    description: str
    node_types: List[str]
    edge_types: List[str]
    failure_modes: List[str]
    operations: List[OperationTeachingSpec] = field(default_factory=list)

    def to_manifest(self) -> Dict[str, Any]:
        return {
            "domain": _slug(self.domain),
            "description": self.description.strip(),
            "node_types": [_slug(item) for item in self.node_types],
            "edge_types": [_slug(item) for item in self.edge_types],
            "failure_modes": [_slug(item) for item in self.failure_modes],
            "operations": [
                operation.to_manifest_operation()
                for operation in self.operations
            ],
        }


def generate_domain_pack(spec: DomainTeachingSpec) -> Dict[str, Any]:
    """Generate and validate a TS-AGL domain pack from structured teaching input."""

    manifest = spec.to_manifest()
    report = validate_manifest(manifest)
    if not report.valid:
        raise ValueError(f"Generated manifest failed validation: {report.to_dict()}")
    return manifest


def write_generated_domain_pack(spec: DomainTeachingSpec, path: str | Path) -> Dict[str, Any]:
    manifest = generate_domain_pack(spec)
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest
