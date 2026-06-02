from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ts_reasoner.research_os import (
    AutomatedResearchForge,
    ConfirmedPatchExecutionEngine,
    EcosystemBrain,
    OntologyCompiler,
    SelfHostingResearchOS,
    SelfRepairingReasoningKernel,
    TSAGLPlanCompiler,
    VerifierGatedMemoryLedger,
    VerifierModelCoEvolution,
    write_v32_v40_receipts,
)


ROOT = Path(__file__).resolve().parents[1]


class ResearchOSV40Tests(unittest.TestCase):
    def test_v32_ontology_compiler_emits_typed_scientific_domain(self) -> None:
        compiler = OntologyCompiler()
        ontology = compiler.compile("Here is a domain: scientific experiment reports.")
        manifest = compiler.emit_manifest(ontology)
        arena = compiler.regression_arena(ontology)

        self.assertIn("Hypothesis", ontology.objects)
        self.assertIn("Falsification Test", ontology.objects)
        self.assertEqual(manifest["domain"], "scientific_experiment_reports")
        self.assertIn("evaluate_claim_support", [op["name"] for op in ontology.operations])
        self.assertTrue(arena["all_gates_passed"], arena)
        self.assertEqual(arena["candidate_graph_contamination_count"], 0)

    def test_v33_memory_quarantines_unsafe_self_learning_claim(self) -> None:
        ledger = VerifierGatedMemoryLedger()
        good = ledger.add_candidate("model confidence is not proof", provenance=["test"])
        ledger.promote(good.item_id, receipt="artifacts/test_receipt.json", confirmed=True)
        bad = ledger.add_candidate("TS-Reasoner is self-learning AGI.", provenance=["test"])
        ledger.promote(bad.item_id, receipt="artifacts/test_receipt.json", confirmed=True)

        self.assertEqual(ledger.items[good.item_id].state, "active")
        self.assertEqual(ledger.items[bad.item_id].state, "quarantined")
        self.assertIn("generated text is not proof", ledger.forbidden_claims())
        self.assertEqual(ledger.to_dict()["candidate_graph_contamination_count"], 0)

    def test_v34_plan_compiler_requires_confirmation_for_patch_steps(self) -> None:
        plan = TSAGLPlanCompiler().compile(
            "Check if this release is safe, fix stale docs if needed, and prepare a release summary."
        )
        operations = [step.operation for step in plan.steps]

        self.assertIn("inspect_repo_state", operations)
        self.assertIn("stage_doc_patch", operations)
        self.assertIn("emit_release_candidate_receipt", operations)
        self.assertTrue(plan.required_confirmations)
        self.assertIn("destructive_write", plan.blocked_side_effects)

    def test_v35_to_v39_surfaces_preserve_boundaries(self) -> None:
        research = AutomatedResearchForge().forge(
            "Investigate whether provenance weighted contradiction repair beats naive repair."
        )
        repair = SelfRepairingReasoningKernel().audit(ROOT)
        patch = ConfirmedPatchExecutionEngine().stage_doc_patch(
            "README.md",
            "# staged candidate\n",
            "Stage candidate patch.",
        )
        unconfirmed = ConfirmedPatchExecutionEngine().apply(patch, confirmed=False)
        ecosystem = EcosystemBrain().audit()
        model = VerifierModelCoEvolution().evaluate()

        self.assertIn("receipt", research["artifacts"])
        self.assertTrue(repair["confirmation_required"])
        self.assertEqual(unconfirmed["status"], "needs_confirmation")
        self.assertFalse(unconfirmed["mutated_state"])
        self.assertTrue(ecosystem["dry_run_only"])
        self.assertFalse(model["model_is_proof_authority"])
        self.assertEqual(model["metrics"]["accepted_without_typed_support"], 0)
        self.assertEqual(model["metrics"]["candidate_graph_contamination_count"], 0)

    def test_v37_confirmed_patch_apply_mutates_only_after_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("old\n", encoding="utf-8")
            engine = ConfirmedPatchExecutionEngine(root)
            patch = engine.stage_doc_patch("README.md", "new\n", "Update README in temp root.")

            blocked = engine.apply(patch, confirmed=False)
            self.assertEqual(blocked["status"], "needs_confirmation")
            self.assertEqual((root / "README.md").read_text(encoding="utf-8"), "old\n")

            applied = engine.apply(patch, confirmed=True)
            self.assertEqual(applied["status"], "success")
            self.assertTrue(applied["mutated_state"])
            self.assertEqual((root / "README.md").read_text(encoding="utf-8"), "new\n")
            self.assertIn("previous_sha256", applied["rollback"]["README.md"])

    def test_v40_research_os_composes_full_stack(self) -> None:
        receipt = SelfHostingResearchOS().run(
            "prepare the next safe TS-Reasoner release candidate",
            ROOT,
        )

        self.assertEqual(receipt["release"], "v40.0.0")
        self.assertTrue(receipt["all_gates_passed"], receipt["gates"])
        self.assertTrue(receipt["confirmation_required"])
        self.assertTrue(receipt["patch_staged"])
        self.assertIn("Not AGI.", receipt["non_claims"])
        self.assertFalse(receipt["external_llm_used"])
        self.assertEqual(receipt["network_call_performed_count"], 0)
        self.assertEqual(receipt["external_side_effect_performed_count"], 0)
        self.assertEqual(receipt["candidate_graph_contamination_count"], 0)

    def test_receipt_writer_can_emit_all_v32_v40_receipts_to_temp_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            summary = write_v32_v40_receipts(tmp, repo=ROOT)
            self.assertTrue(summary["all_gates_passed"], summary)
            self.assertEqual(summary["receipt_count"], 9)
            for path in summary["receipts"].values():
                self.assertTrue(Path(path).exists(), path)

    def test_cli_and_compiler_surfaces(self) -> None:
        plan = subprocess.run(
            [
                sys.executable,
                "-m",
                "ts_agl.compiler",
                "audit this repo for release readiness and prepare the next safe action",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(plan.stdout)
        self.assertIn("inspect_repo_state", [step["operation"] for step in payload["steps"]])

        research_os = subprocess.run(
            [
                sys.executable,
                "-m",
                "ts_reasoner.cli",
                "research-os",
                "--mission",
                "prepare the next safe TS-Reasoner release candidate",
                "--repo",
                str(ROOT),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        receipt = json.loads(research_os.stdout)
        self.assertTrue(receipt["all_gates_passed"], receipt["gates"])

    def test_pyproject_packages_ts_agl(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('"ts_agl*"', pyproject)
        self.assertIn('version = "40.0.0"', pyproject)


if __name__ == "__main__":
    unittest.main()
