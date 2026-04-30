from __future__ import annotations

from .schemas import (
    AntiPatternAlert,
    AntiPatternCheckRequest,
    AntiPatternCheckResponse,
    AntiPatternSeverity,
)


class AntiPatternRegistry:
    def evaluate(self, payload: AntiPatternCheckRequest) -> AntiPatternCheckResponse:
        metrics = payload.vector.metrics
        streak = payload.continuous_trigger_count
        severity = self._severity_by_streak(streak)

        alerts: list[AntiPatternAlert] = []

        def add(pattern: str, reason: str) -> None:
            alerts.append(AntiPatternAlert(pattern=pattern, severity=severity, reason=reason))

        if metrics.get("P7", 1.0) < 0.45 or payload.hint_flags.get("pov_pollution", False):
            add("POV_POLLUTION", "POV consistency dropped below baseline")
        if metrics.get("P6", 1.0) < 0.50 or payload.hint_flags.get("dialogue_awkward", False):
            add("DIALOGUE_AWKWARD", "Dialogue identity coefficient too low")
        if metrics.get("W1", 1.0) < 0.45 or payload.hint_flags.get("logic_break", False):
            add("LOGIC_BREAK", "World rule consistency dropped")
        if metrics.get("P3", 1.0) < 0.35 or payload.hint_flags.get("puppet_mc", False):
            add("PUPPET_PROTAGONIST", "Goal alignment ratio indicates passive protagonist")
        if metrics.get("T9", 1.0) < 0.50 or payload.hint_flags.get("villain_nerf", False):
            add("VILLAIN_NERF", "Antagonist pressure index indicates downgraded antagonist")
        if metrics.get("T2", 1.0) < 0.35 or payload.hint_flags.get("pacing_drag", False):
            add("PACING_DRAG", "Tension gradient is too weak")
        if metrics.get("A6", 1.0) < 0.45 or payload.hint_flags.get("self_indulgence", False):
            add("SELF_INDULGENCE_TOPIC", "IP flavor corridor delta indicates audience mismatch")

        critical = any(alert.severity == AntiPatternSeverity.CRITICAL for alert in alerts)
        return AntiPatternCheckResponse(alerts=alerts, critical=critical)

    def _severity_by_streak(self, streak: int) -> AntiPatternSeverity:
        if streak >= 3:
            return AntiPatternSeverity.CRITICAL
        if streak == 2:
            return AntiPatternSeverity.ERROR
        return AntiPatternSeverity.WARNING
