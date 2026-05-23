"""TS-Reasoner-v0: toy constraint-graph reasoning telemetry."""

from .pipeline import TSReasoner, run_reasoner
from .operation_router import OperationRouter
from .tension_agents import TensionCoordinator
from .coupling_learner import train_residual_coupling_matrix
from .benchmark import BenchmarkRunner, BenchmarkTask, load_benchmark
from .tensionproof_smoke import evaluate_tensionproof_smoke
from .types import ReasonerOutput, TensionAgentSignal

__all__ = [
    "BenchmarkRunner",
    "BenchmarkTask",
    "OperationRouter",
    "ReasonerOutput",
    "TSReasoner",
    "TensionAgentSignal",
    "TensionCoordinator",
    "evaluate_tensionproof_smoke",
    "load_benchmark",
    "run_reasoner",
    "train_residual_coupling_matrix",
]
