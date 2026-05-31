from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ts_agl.teaching import DomainTeachingSpec, OperationTeachingSpec, write_generated_domain_pack


def build_demo_spec() -> DomainTeachingSpec:
    return DomainTeachingSpec(
        domain="research_notes",
        description="Generated teaching pack for bounded research note workflows.",
        node_types=["note", "topic", "summary", "draft", "publication_target"],
        edge_types=["summarizes", "references", "drafts", "publishes_to"],
        failure_modes=[
            "missing_note",
            "missing_topic",
            "unsafe_publish_without_confirmation",
            "ambiguous_note_reference",
        ],
        operations=[
            OperationTeachingSpec(
                name="summarize_note",
                description="Summarize a bounded research note.",
                required_inputs=["note_id"],
                risk="read_only",
                examples=[
                    "summarize this research note",
                    "what does this note say",
                    "give me the note summary",
                ],
            ),
            OperationTeachingSpec(
                name="draft_note",
                description="Draft a bounded research note artifact.",
                required_inputs=["topic"],
                risk="reversible_write",
                examples=[
                    "draft a research note",
                    "create a note draft",
                    "write a bounded note about this topic",
                ],
            ),
            OperationTeachingSpec(
                name="publish_note_dry_run",
                description="Stage a dry-run publication action for a note.",
                required_inputs=["note_id", "target"],
                risk="external_side_effect",
                examples=[
                    "stage a note publication",
                    "publish this note in dry run",
                    "prepare to send this note externally",
                ],
            ),
        ],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the v17 TS-AGL demo domain pack.")
    parser.add_argument(
        "--output",
        default="artifacts/generated_domain_packs/research_notes.json",
        help="Where to write the generated domain pack.",
    )
    args = parser.parse_args()

    manifest = write_generated_domain_pack(build_demo_spec(), args.output)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
