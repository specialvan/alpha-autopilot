from __future__ import annotations

from dataclasses import dataclass

from .common import clamp
from .schemas import BenchmarkParameterSet, NQMVector, ThresholdBand


@dataclass(frozen=True)
class ThresholdBandEngine:
    default_high: float = 0.78
    default_low: float = 0.52
    default_opening_t8: float = 0.60

    def build_band(self, metric_id: str, benchmark: BenchmarkParameterSet) -> ThresholdBand:
        mean = benchmark.nqm_mean
        sigma = max(0.01, benchmark.nqm_std)
        support = clamp(mean - 0.8 * sigma)
        resistance = clamp(mean + 0.8 * sigma)
        stop_loss = clamp(support - 0.07)
        breakout_confirm = clamp(resistance + 0.05)

        if metric_id == "T8":
            support = clamp(benchmark.opening_gate_t8)
            stop_loss = clamp(support - 0.08)
            resistance = max(resistance, support)

        return ThresholdBand(
            support=support,
            resistance=resistance,
            stop_loss=stop_loss,
            breakout_confirm=breakout_confirm,
        )

    def classify_zone(self, composite: float, benchmark: BenchmarkParameterSet) -> str:
        high = benchmark.high_threshold or self.default_high
        low = benchmark.low_threshold or self.default_low
        score = clamp(composite)
        if score < low:
            return "hard_intervention"
        if score <= high:
            return "elastic_injection"
        return "free_generation"

    def detect_pattern(self, ohlcv_open: float, ohlcv_close: float, ohlcv_volume: float, band: ThresholdBand) -> str:
        close_value = clamp(ohlcv_close)
        open_value = clamp(ohlcv_open)
        if close_value < band.stop_loss:
            return "volume_breakdown" if ohlcv_volume >= 700 else "support_breakdown"
        if close_value > band.breakout_confirm:
            return "confirmed_breakout" if ohlcv_volume >= 700 else "thin_breakout"
        if close_value >= band.resistance and close_value >= open_value:
            return "resistance_test"
        if close_value <= band.support and close_value <= open_value:
            return "support_retest"
        return "range_trading"

    def build_metric_bands(self, vector: NQMVector, benchmark: BenchmarkParameterSet) -> dict[str, ThresholdBand]:
        output: dict[str, ThresholdBand] = {}
        for metric_id in vector.metrics:
            output[metric_id] = self.build_band(metric_id, benchmark)
        return output
