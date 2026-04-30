from __future__ import annotations

from .schemas import BenchmarkParameterSet


def refit_thresholds(benchmark: BenchmarkParameterSet) -> BenchmarkParameterSet:
    mean = benchmark.nqm_mean
    std = max(0.01, benchmark.nqm_std)
    return benchmark.model_copy(
        update={
            "high_threshold": min(1.0, mean + 0.16),
            "low_threshold": max(0.0, mean - 0.10),
            "opening_gate_t8": max(0.4, min(0.8, benchmark.opening_gate_t8)),
            "nqm_std": std,
        }
    )
