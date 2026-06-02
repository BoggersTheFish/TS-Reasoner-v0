from __future__ import annotations

from pathlib import Path
from subprocess import run
from typing import Any, Dict, List
import re

from ts_agl.core.types import ResultPacket, TSCall


V31_RELEASE = "v31.0.0"
V31_TITLE = "TS Project Curriculum Pack v1"
V31_REPORT = Path("artifacts/ts_project_curriculum_report.json")
V31_RECEIPT = Path("artifacts/ts_project_curriculum_receipt.json")


def _read(path: str) -> str:
    target = Path(path)
    if not target.exists():
        return ""
    return target.read_text(encoding="utf-8")


def _grep(pattern: str, paths: List[str]) -> List[Dict[str, Any]]:
    regex = re.compile(pattern, flags=re.IGNORECASE)
    hits: List[Dict[str, Any]] = []
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if regex.search(line):
                hits.append({"path": raw_path, "line": line_number, "text": line.strip()})
    return hits


def _git_status() -> Dict[str, Any]:
    short = run(["git", "status", "--short"], text=True, capture_output=True, check=False)
    branch = run(["git", "branch", "--show-current"], text=True, capture_output=True, check=False)
    return {
        "branch": branch.stdout.strip() if branch.returncode == 0 else None,
        "clean": short.returncode == 0 and short.stdout.strip() == "",
        "status_short": short.stdout.strip().splitlines() if short.stdout.strip() else [],
    }


class TSProjectAdapter:
    """Bounded TS project curriculum adapter.

    The adapter teaches project-local operations without granting language,
    examples, or repeated experience durable proof authority.
    """

    def _release_surface(self) -> Dict[str, Any]:
        readme = _read("README.md")
        release_notes = _read("RELEASE_NOTES.md")
        release_ladder = _read("docs/RELEASE_LADDER.md")
        pyproject = _read("pyproject.toml")
        return {
            "pyproject_mentions_v31_or_later": V31_RELEASE.strip("v") in pyproject or "40.0.0" in pyproject,
            "v31_documented": (V31_RELEASE in readme or V31_RELEASE in release_ladder)
            and (V31_TITLE in readme or V31_TITLE in release_ladder),
            "release_notes_entry": f"## {V31_RELEASE}: {V31_TITLE}" in release_notes,
            "core_v12_boundary_visible": ("v12.0.0" in readme or "v12.0.0" in release_ladder)
            and ("Verifier-Gated Proposer Stack" in readme or "Verifier-Gated Proposer Stack" in release_ladder),
        }

    def _boundary_payload(self) -> Dict[str, Any]:
        return {
            "built": [
                "verifier boundary",
                "typed proof support",
                "candidate/proposer separation",
                "router/action surface",
                "local OS loop",
                "risk gates",
                "confirmation gates",
                "receipts",
                "domain teaching contract",
                "TS Project Domain Pack v1",
            ],
            "not_fully_built": [
                "open-ended memory growth",
                "autonomous concept formation",
                "self-training over arbitrary new domains",
                "long-term weighted knowledge evolution",
                "safe promotion from repeated experience into durable belief",
            ],
            "ready_to_teach": True,
            "ready_for_free_self_learning": False,
            "safe_learning_mode": "bounded_curriculum_learning",
            "language_layer_is_proof_authority": False,
            "router_confidence_is_proof": False,
            "typed_verifier_support_remains_proof_boundary": True,
        }

    def execute(self, call: TSCall) -> ResultPacket:
        if call.operation == "inspect_project_state":
            surface = self._release_surface()
            return ResultPacket(
                status="success",
                system=call.system,
                operation=call.operation,
                data={
                    "release": V31_RELEASE,
                    "title": V31_TITLE,
                    "git": _git_status(),
                    "release_surface": surface,
                    "all_release_surfaces_current": all(surface.values()),
                    "external_llm_used": False,
                },
                mutated_state=False,
            )

        if call.operation == "explain_release_state":
            return ResultPacket(
                status="success",
                system=call.system,
                operation=call.operation,
                data={
                    "release": V31_RELEASE,
                    "title": V31_TITLE,
                    "claim": (
                        "v31 teaches TS-Reasoner its own project domain as bounded curriculum: "
                        "repo, release, artifact, receipt, claim, proof boundary, unsafe overclaim, "
                        "next safe action, stale public surface, and missing receipt."
                    ),
                    "core_substrate": "v12.0.0 - Verifier-Gated Proposer Stack",
                    "flagship_surface": "v30.0.0 - Verifier-First Local Agent OS",
                    "open_ended_self_learning": False,
                },
                mutated_state=False,
            )

        if call.operation == "find_missing_receipts":
            raw_expected = call.args.get("expected_receipts")
            expected = (
                [Path(item) for item in raw_expected]
                if isinstance(raw_expected, list) and raw_expected
                else [V31_REPORT, V31_RECEIPT]
            )
            missing = [str(path) for path in expected if not path.exists()]
            return ResultPacket(
                status="success",
                system=call.system,
                operation=call.operation,
                data={
                    "expected_receipts": [str(path) for path in expected],
                    "missing_receipts": missing,
                    "missing_receipt_count": len(missing),
                    "has_required_v31_receipts": len(missing) == 0,
                },
                mutated_state=False,
            )

        if call.operation == "detect_stale_public_surface":
            stale_hits = _grep(
                r"Current release:\s*\*\*v30\.0\.0|release-v30\.0\.0|version = \"30\.0\.0\"|## v31\.0\.0: Verifier-First Local Agent OS",
                ["README.md", "RELEASE_NOTES.md", "pyproject.toml", "docs/RELEASE_LADDER.md"],
            )
            release_surface = self._release_surface()
            return ResultPacket(
                status="success",
                system=call.system,
                operation=call.operation,
                data={
                    "stale_public_surface_hits": stale_hits,
                    "stale_public_surface_count": len(stale_hits),
                    "release_surface": release_surface,
                    "public_surface_current": len(stale_hits) == 0 and all(release_surface.values()),
                },
                mutated_state=False,
            )

        if call.operation == "reject_unsafe_overclaim":
            claim = call.args.get("claim") or call.source_move.get("raw_text") or ""
            unsafe_terms = [
                "freely self-learning",
                "autonomously learn anything",
                "open-ended autonomous learner",
                "free self-learning",
                "learn this forever",
            ]
            unsafe = any(term in claim.lower() for term in unsafe_terms)
            return ResultPacket(
                status="rejected" if unsafe else "abstained",
                system=call.system,
                operation=call.operation,
                data={
                    "claim": claim,
                    "unsafe_overclaim_detected": unsafe,
                    "decision": "rejected" if unsafe else "abstained",
                    "reason": (
                        "TS-Reasoner is ready for bounded curriculum learning, "
                        "not free self-learning or autonomous durable belief promotion."
                    ),
                    "language_layer_is_proof_authority": False,
                },
                mutated_state=False,
            )

        if call.operation == "inspect_proof_boundary":
            return ResultPacket(
                status="success",
                system=call.system,
                operation=call.operation,
                data=self._boundary_payload(),
                mutated_state=False,
            )

        if call.operation == "suggest_next_safe_release_action":
            status = _git_status()
            surface = self._release_surface()
            if not status["clean"]:
                action = "Finish or review the v31 working tree, run focused tests, restore generated receipt noise, then open a PR."
            elif not all(surface.values()):
                action = "Update v31 public release surfaces before tagging or merging."
            else:
                action = "Run full verification, open the v31 PR, and do not tag until merged to a clean main."
            return ResultPacket(
                status="success",
                system=call.system,
                operation=call.operation,
                data={
                    "next_safe_action": action,
                    "git": status,
                    "release_surface": surface,
                    "risk": "read_only",
                },
                mutated_state=False,
            )

        if call.operation == "summarize_curriculum_boundary":
            payload = self._boundary_payload()
            payload["summary"] = (
                "Yes, TS-Reasoner is ready to be taught through bounded domain packs. "
                "No, it is not ready for free self-learning. Durable promotion remains gated."
            )
            return ResultPacket(
                status="success",
                system=call.system,
                operation=call.operation,
                data=payload,
                mutated_state=False,
            )

        if call.operation == "promote_lesson_candidate":
            return ResultPacket(
                status="success",
                system=call.system,
                operation=call.operation,
                data={
                    "lesson_id": call.args.get("lesson_id"),
                    "evidence_path": call.args.get("evidence_path"),
                    "promotion_recorded": True,
                    "durable_belief_authorized_by_language": False,
                    "requires_confirmation": True,
                },
                mutated_state=True,
            )

        return ResultPacket(
            status="failed",
            system=call.system,
            operation=call.operation,
            error=f"Unknown TS project operation: {call.operation}",
            mutated_state=False,
        )
