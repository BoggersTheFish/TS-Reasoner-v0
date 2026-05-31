from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set
import json


ALLOWED_RISKS = {
    "read_only",
    "reversible_write",
    "destructive_write",
    "external_side_effect",
}


@dataclass(frozen=True)
class ManifestValidationIssue:
    severity: str
    domain: str
    message: str
    path: str = ""

    def to_dict(self) -> Dict[str, str]:
        return {
            "severity": self.severity,
            "domain": self.domain,
            "message": self.message,
            "path": self.path,
        }


@dataclass
class ManifestValidationReport:
    manifest_count: int = 0
    operation_count: int = 0
    language_example_count: int = 0
    issues: List[ManifestValidationIssue] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "warning")

    @property
    def valid(self) -> bool:
        return self.error_count == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "manifest_count": self.manifest_count,
            "operation_count": self.operation_count,
            "language_example_count": self.language_example_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "valid": self.valid,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(_is_nonempty_string(item) for item in value)


def _add_issue(
    report: ManifestValidationReport,
    severity: str,
    domain: str,
    message: str,
    path: str = "",
) -> None:
    report.issues.append(
        ManifestValidationIssue(
            severity=severity,
            domain=domain or "<unknown>",
            message=message,
            path=path,
        )
    )


def validate_manifest(manifest: Dict[str, Any]) -> ManifestValidationReport:
    report = ManifestValidationReport(manifest_count=1)
    domain = manifest.get("domain", "")

    if not _is_nonempty_string(domain):
        _add_issue(report, "error", domain, "Manifest requires non-empty string field `domain`.", "domain")

    if not _is_nonempty_string(manifest.get("description")):
        _add_issue(report, "error", domain, "Manifest requires non-empty string field `description`.", "description")

    for list_field in ("node_types", "edge_types", "failure_modes"):
        value = manifest.get(list_field)
        if not _is_string_list(value):
            _add_issue(report, "error", domain, f"`{list_field}` must be a list of non-empty strings.", list_field)
        elif len(set(value)) != len(value):
            _add_issue(report, "error", domain, f"`{list_field}` contains duplicate entries.", list_field)

    operations = manifest.get("operations")
    if not isinstance(operations, list) or not operations:
        _add_issue(report, "error", domain, "`operations` must be a non-empty list.", "operations")
        return report

    report.operation_count += len(operations)
    seen_ops: Set[str] = set()

    for index, operation in enumerate(operations):
        op_path = f"operations[{index}]"
        if not isinstance(operation, dict):
            _add_issue(report, "error", domain, "Operation must be an object.", op_path)
            continue

        name = operation.get("name")
        if not _is_nonempty_string(name):
            _add_issue(report, "error", domain, "Operation requires non-empty string field `name`.", f"{op_path}.name")
        elif name in seen_ops:
            _add_issue(report, "error", domain, f"Duplicate operation name `{name}`.", f"{op_path}.name")
        else:
            seen_ops.add(name)

        if not _is_nonempty_string(operation.get("description")):
            _add_issue(report, "error", domain, f"Operation `{name}` requires a description.", f"{op_path}.description")

        required_inputs = operation.get("required_inputs")
        if not _is_string_list(required_inputs):
            _add_issue(report, "error", domain, f"Operation `{name}` requires `required_inputs` as a string list.", f"{op_path}.required_inputs")

        risk = operation.get("risk")
        if risk not in ALLOWED_RISKS:
            _add_issue(
                report,
                "error",
                domain,
                f"Operation `{name}` has invalid risk `{risk}`.",
                f"{op_path}.risk",
            )

        requires_confirmation = operation.get("requires_confirmation")
        if not isinstance(requires_confirmation, bool):
            _add_issue(report, "error", domain, f"Operation `{name}` requires boolean `requires_confirmation`.", f"{op_path}.requires_confirmation")

        if risk != "read_only" and requires_confirmation is False:
            _add_issue(
                report,
                "error",
                domain,
                f"Operation `{name}` is risky but does not require confirmation.",
                f"{op_path}.requires_confirmation",
            )

        examples = operation.get("examples")
        if not _is_string_list(examples) or not examples:
            _add_issue(report, "error", domain, f"Operation `{name}` requires at least one language example.", f"{op_path}.examples")
        else:
            report.language_example_count += len(examples)

    return report


def validate_manifests(manifests: Iterable[Dict[str, Any]]) -> ManifestValidationReport:
    merged = ManifestValidationReport()
    seen_domains: Set[str] = set()

    for manifest in manifests:
        report = validate_manifest(manifest)
        domain = manifest.get("domain", "")

        merged.manifest_count += report.manifest_count
        merged.operation_count += report.operation_count
        merged.language_example_count += report.language_example_count
        merged.issues.extend(report.issues)

        if domain in seen_domains:
            _add_issue(merged, "error", domain, f"Duplicate manifest domain `{domain}`.", "domain")
        elif domain:
            seen_domains.add(domain)

    return merged


def load_manifest_file(path: str | Path) -> Dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def load_manifest_dir(path: str | Path = "ts_agl/domains") -> List[Dict[str, Any]]:
    base = Path(path)
    return [load_manifest_file(p) for p in sorted(base.glob("*.json"))]


def validate_manifest_dir(path: str | Path = "ts_agl/domains") -> ManifestValidationReport:
    return validate_manifests(load_manifest_dir(path))
