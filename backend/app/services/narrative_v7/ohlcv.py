from __future__ import annotations

from .common import clamp
from .schemas import NarrativeMetricOHLCV


def merge_ohlcv_series(units: list[NarrativeMetricOHLCV]) -> NarrativeMetricOHLCV:
    if not units:
        return NarrativeMetricOHLCV()

    open_value = units[0].open
    close_value = units[-1].close
    high_value = max(unit.high for unit in units)
    low_value = min(unit.low for unit in units)
    volume = sum(unit.volume for unit in units)

    return NarrativeMetricOHLCV(
        open=clamp(open_value),
        high=clamp(high_value),
        low=clamp(low_value),
        close=clamp(close_value),
        volume=max(0.0, float(volume)),
    )
