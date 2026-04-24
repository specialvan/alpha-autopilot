from __future__ import annotations

from alpha_autopilot_v2.domain import RuleCheck, SearchResult
from alpha_autopilot_v2.validation.models import ValidationRecord

from .schemas import (
    NarrativeV2DecisionCandidatePayload,
    NarrativeV2DecisionPayload,
    NarrativeV2RetentionDriverPayload,
    RuleStatusSummaryPayload,
)


def build_preview_decision(
    rule_checks: list[RuleCheck],
    recommendations: list[SearchResult],
    validation: ValidationRecord,
    retention_driver: dict[str, object] | None = None,
) -> dict[str, object]:
    legal_count = sum(1 for check in rule_checks if check.status == "legal")
    blocked_count = sum(1 for check in rule_checks if check.status == "blocked")
    prerequisite_missing_count = sum(
        1 for check in rule_checks if check.status == "prerequisite_missing"
    )
    blocked_actions = [check.action for check in rule_checks if check.status == "blocked"]
    prerequisite_missing_actions = [
        check.action for check in rule_checks if check.status == "prerequisite_missing"
    ]
    selected_action = validation.top_action or _top_action(recommendations)
    selected_recommendation = _selected_recommendation(selected_action, recommendations)
    selected_score = selected_recommendation.score if selected_recommendation is not None else 0.0
    selected_explanation = _decision_explanation(
        selected_recommendation,
        retention_driver,
    )
    selected_details = (
        _numeric_details(selected_recommendation.details)
        if selected_recommendation is not None
        else {}
    )

    decision = NarrativeV2DecisionPayload(
        selected_action=selected_action,
        selected_score=round(selected_score, 4),
        accepted_actions=list(validation.accepted_actions),
        blocked_actions=blocked_actions,
        prerequisite_missing_actions=prerequisite_missing_actions,
        rule_status_summary=RuleStatusSummaryPayload(
            legal_count=legal_count,
            blocked_count=blocked_count,
            prerequisite_missing_count=prerequisite_missing_count,
        ),
        constraint_hint=_constraint_hint(
            blocked_count=blocked_count,
            prerequisite_missing_count=prerequisite_missing_count,
        ),
        validation_case_id=validation.case_id,
        quality_hint=_quality_hint(
            selected_action=selected_action,
            selected_score=selected_score,
            legal_count=legal_count,
            blocked_count=blocked_count,
            prerequisite_missing_count=prerequisite_missing_count,
        ),
        explanation=selected_explanation,
        details=selected_details,
        candidates=[
            NarrativeV2DecisionCandidatePayload(
                action=item.action.action,
                score=round(item.score, 4),
                explanation=item.action.explanation,
                details=_numeric_details(item.details),
            )
            for item in recommendations[:3]
        ],
        retention_driver=_retention_driver_payload(retention_driver),
    )
    return decision.model_dump(exclude_none=True)


def _top_action(recommendations: list[SearchResult]) -> str:
    if not recommendations:
        return ""
    return recommendations[0].action.action


def _selected_recommendation(
    selected_action: str,
    recommendations: list[SearchResult],
) -> SearchResult | None:
    if not recommendations:
        return None
    for recommendation in recommendations:
        if recommendation.action.action == selected_action:
            return recommendation
    return None


def _numeric_details(details: dict[str, float]) -> dict[str, float]:
    normalized: dict[str, float] = {}
    for key, value in details.items():
        if isinstance(value, (int, float)):
            normalized[key] = round(float(value), 4)
    return normalized


def _constraint_hint(
    blocked_count: int,
    prerequisite_missing_count: int,
) -> str:
    if blocked_count > 0 and prerequisite_missing_count > 0:
        return "mixed_constraints"
    if blocked_count > 0:
        return "hard_blocked"
    if prerequisite_missing_count > 0:
        return "prerequisite_missing"
    return "clear"


def _quality_hint(
    selected_action: str,
    selected_score: float,
    legal_count: int,
    blocked_count: int,
    prerequisite_missing_count: int,
) -> str:
    if legal_count == 0:
        if blocked_count > 0:
            return "blocked"
        if prerequisite_missing_count > 0:
            return "prerequisite_missing"
        return "blocked"
    if not selected_action:
        return "review"
    if selected_score >= 0.75 and blocked_count == 0 and prerequisite_missing_count == 0:
        return "ready"
    return "review"


def _retention_driver_payload(
    retention_driver: dict[str, object] | None,
) -> NarrativeV2RetentionDriverPayload | None:
    if not isinstance(retention_driver, dict):
        return None
    try:
        return NarrativeV2RetentionDriverPayload.model_validate(retention_driver)
    except Exception:
        return None


def _decision_explanation(
    recommendation: SearchResult | None,
    retention_driver: dict[str, object] | None,
) -> str:
    base = recommendation.action.explanation if recommendation is not None else ""
    if not isinstance(retention_driver, dict):
        return base

    retention_score = retention_driver.get("selected_retention_score")
    penalty = retention_driver.get("selected_guardrail_penalty")
    mode = retention_driver.get("control_mode")
    if isinstance(retention_score, (int, float)) and isinstance(penalty, (int, float)):
        mode_text = f", mode={mode}" if isinstance(mode, str) and mode.strip() else ""
        suffix = (
            f" Retention driver: score={float(retention_score):.4f}, "
            f"penalty={float(penalty):.4f}{mode_text}."
        )
        return f"{base}{suffix}".strip()
    return base
