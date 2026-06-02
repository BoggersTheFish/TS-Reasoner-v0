from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ts_metacompute.scheduler import MetacomputeScheduler, SchedulerTask
from ts_reasoner.cognitive_physics_engine import (
    LazyUniverseEngine,
    PhotonicStateLedger,
    RetrocausalFuzzer,
    ResonanceNode,
    SpectralCouplingTelepathy,
    TemporalTensionBridge,
    UnifiedFieldKernel,
    build_cognitive_physics_receipt,
    build_demo_graphs,
    evaluate_cognitive_physics_engine,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "artifacts" / "cognitive_physics_engine_report.json"
RECEIPT = ROOT / "artifacts" / "cognitive_physics_engine_receipt.json"


class CognitivePhysicsEngineTests(unittest.TestCase):
    def test_photonic_state_ledger_stores_frequency_slots(self) -> None:
        graph = build_demo_graphs()["late_contradiction"]
        payload = PhotonicStateLedger().encode_graph(graph)

        self.assertEqual(payload["architecture"], "Photonic_State_Ledger")
        self.assertEqual(len(payload["entries"]), len(graph.edges))
        self.assertEqual({entry["phase_degrees"] for entry in payload["entries"]}, {0.0, 180.0})
        self.assertTrue(all(entry["frequency_thz"] > 430.0 for entry in payload["entries"]))
        self.assertEqual(payload["accepted_without_verifier_support_count"], 0)
        self.assertFalse(payload["accepted_truth"])

    def test_interference_gate_cancels_contradictory_wave_without_accepting_truth(self) -> None:
        graph = build_demo_graphs()["late_contradiction"]
        ledger = PhotonicStateLedger()
        ledger.encode_graph(graph)
        gate = ledger.interference_gate(graph)

        self.assertTrue(gate["contradiction_detected"])
        self.assertGreater(gate["cancelled_amplitude"], 0.0)
        self.assertGreater(gate["residual_tension"], 0.0)
        self.assertFalse(gate["energy_estimate"]["physical_zero_compute_claimed"])
        self.assertEqual(gate["accepted_without_verifier_support_count"], 0)

    def test_temporal_bridge_reduces_early_assumption_probability(self) -> None:
        graph = build_demo_graphs()["late_contradiction"]
        payload = TemporalTensionBridge().propagate(
            graph,
            assumption_priors={"support_ab": 0.9, "support_bc": 0.8},
            contradiction_step=5,
        )

        self.assertEqual(payload["architecture"], "Temporal_Tension_Bridge")
        self.assertGreater(payload["propagated_tension"], 0.0)
        self.assertTrue(payload["tamper_evident_runtime_ledger"])
        for update in payload["assumption_updates"]:
            self.assertLess(update["posterior_probability"], update["prior_probability"])
        self.assertEqual(payload["accepted_without_verifier_support_count"], 0)

    def test_retrocausal_fuzzer_records_simulated_future_memory_boundary(self) -> None:
        graph = build_demo_graphs()["late_contradiction"]
        payload = RetrocausalFuzzer().fuzz(graph)

        self.assertEqual(payload["architecture"], "Retrocausal_Fuzzer")
        self.assertTrue(payload["future_memory_is_simulated"])
        self.assertGreater(payload["probability_updates_decreased_count"], 0)
        self.assertEqual(payload["accepted_without_verifier_support_count"], 0)

    def test_resonance_network_transmits_shape_not_answer(self) -> None:
        graph = build_demo_graphs()["coherent_zero_tension"]
        tokyo = ResonanceNode("node_tokyo", "Tokyo", {"logic": {"logic": 0.3}}, harmonic_frequency=1.0)
        payload = SpectralCouplingTelepathy().align(
            [
                ResonanceNode("node_london", "London", {"logic": {"logic": 1.0}}, harmonic_frequency=1.0),
                tokyo,
            ],
            "node_london",
            graph,
        )

        self.assertEqual(payload["architecture"], "Spectral_Coupling_Telepathy")
        self.assertFalse(payload["answer_transmitted"])
        self.assertEqual(payload["transmissions"][1]["answer_packet_bytes"], 0)
        self.assertIn("shape_alignment", tokyo.coupling_matrix["resonance"])
        self.assertEqual(payload["accepted_without_verifier_support_count"], 0)

    def test_unified_field_kernel_emits_only_zero_tension_verifier_supported_state(self) -> None:
        graphs = build_demo_graphs()
        kernel = UnifiedFieldKernel()
        coherent = kernel.resolve("Does A resolve to C?", graphs["coherent_zero_tension"])
        contradiction = kernel.resolve("Does A resolve to C?", graphs["late_contradiction"])
        unsupported = kernel.resolve("Does A resolve to C?", graphs["unsupported_candidate"])

        self.assertTrue(coherent["emitted"])
        self.assertTrue(coherent["accepted_truth"])
        self.assertTrue(contradiction["blocked_before_emission"])
        self.assertTrue(unsupported["blocked_before_emission"])
        self.assertEqual(coherent["accepted_without_verifier_support_count"], 0)
        self.assertEqual(contradiction["accepted_without_verifier_support_count"], 0)
        self.assertEqual(unsupported["accepted_without_verifier_support_count"], 0)

    def test_lazy_universe_engine_composes_full_stack(self) -> None:
        graph = build_demo_graphs()["coherent_zero_tension"]
        payload = LazyUniverseEngine().run("Does A resolve to C?", graph)

        self.assertEqual(payload["engine"], "The_Lazy_Universe_Engine")
        self.assertTrue(payload["all_gates_passed"], payload["gates"])
        self.assertEqual(payload["operating_power_target_watts"], 20)
        self.assertFalse(payload["literal_physics_solves_question_claimed"])
        self.assertEqual(payload["accepted_without_verifier_support_count"], 0)

    def test_scheduler_routes_new_substrates(self) -> None:
        graph = build_demo_graphs()["coherent_zero_tension"]
        scheduler = MetacomputeScheduler()

        photonic = scheduler.run(SchedulerTask("photonic_interference", graph))
        temporal = scheduler.run(SchedulerTask("temporal_tension_bridge", graph))
        resonance = scheduler.run(SchedulerTask("resonance_telemetry", graph))
        unified = scheduler.run(SchedulerTask("unified_field_resolution", graph, metadata={"question": "Does A resolve to C?"}))
        lazy = scheduler.run(SchedulerTask("lazy_universe_resolution", graph, metadata={"question": "Does A resolve to C?"}))

        self.assertEqual(photonic["selected_substrate"], "photonic_sim")
        self.assertEqual(temporal["selected_substrate"], "temporal_bridge")
        self.assertEqual(resonance["selected_substrate"], "resonance_network")
        self.assertEqual(unified["selected_substrate"], "unified_field")
        self.assertEqual(lazy["selected_substrate"], "unified_field")

    def test_report_receipt_and_cli_script(self) -> None:
        report = evaluate_cognitive_physics_engine()
        receipt = build_cognitive_physics_receipt(report)

        self.assertTrue(report["all_gates_passed"], report["gates"])
        self.assertTrue(receipt["all_gates_passed"])
        self.assertIn("The_Lazy_Universe_Engine", receipt["implemented_architectures"])
        self.assertEqual(receipt["accepted_without_verifier_support_count"], 0)

        result = subprocess.run(
            [sys.executable, "scripts/evaluate_cognitive_physics_engine.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertTrue(REPORT.exists())
        self.assertTrue(RECEIPT.exists())
        self.assertTrue(json.loads(RECEIPT.read_text(encoding="utf-8"))["all_gates_passed"])

    def test_cli_surface(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ts_reasoner.cli",
                "cognitive-physics",
                "--question",
                "Does A resolve to C?",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["all_gates_passed"], payload["gates"])


if __name__ == "__main__":
    unittest.main()

