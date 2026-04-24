from __future__ import annotations

from alpha_autopilot_v2.domain import NarrativeAction, RuleCheck, SearchResult
from alpha_autopilot_v2.validation.models import ValidationRecord

from backend.app.services.narrative_v2.decision_contract import build_preview_decision


def test_build_preview_decision_returns_standardized_decision_object() -> None:
    rule_checks = [
        RuleCheck(action="push_conflict", status="legal"),
        RuleCheck(action="reveal_clue", status="legal"),
        RuleCheck(action="deliver_payoff", status="blocked", blockers=["stage_not_ready"]),
    ]
    recommendations = [
        SearchResult(
            action=NarrativeAction(
                action="push_conflict",
                delta={"conflict_intensity": 0.16},
                explanation="Raise direct confrontation.",
            ),
            rule_check=rule_checks[0],
            score=0.8123,
            details={"structure_value": 0.9, "feasibility": 1.0},
        )
    ]
    validation = ValidationRecord(
        case_id="case-42",
        accepted_actions=["push_conflict", "reveal_clue"],
        blocked_actions=["deliver_payoff"],
        top_action="push_conflict",
        notes="preview",
    )

    decision = build_preview_decision(
        rule_checks=rule_checks,
        recommendations=recommendations,
        validation=validation,
    )

    assert decision["selected_action"] == "push_conflict"
    assert decision["selected_score"] == 0.8123
    assert decision["accepted_actions"] == ["push_conflict", "reveal_clue"]
    assert decision["blocked_actions"] == ["deliver_payoff"]
    assert decision["prerequisite_missing_actions"] == []
    assert decision["rule_status_summary"] == {
        "legal_count": 2,
        "blocked_count": 1,
        "prerequisite_missing_count": 0,
    }
    assert decision["constraint_hint"] == "hard_blocked"
    assert decision["validation_case_id"] == "case-42"
    assert decision["quality_hint"] == "review"


def test_build_preview_decision_marks_blocked_when_no_ranked_recommendation() -> None:
    rule_checks = [
        RuleCheck(action="deliver_payoff", status="blocked", blockers=["stage_not_ready"]),
        RuleCheck(action="open_new_thread", status="prerequisite_missing", blockers=["late_stage_locked"]),
    ]
    validation = ValidationRecord(
        case_id="case-77",
        accepted_actions=[],
        blocked_actions=["deliver_payoff", "open_new_thread"],
        top_action="",
        notes="preview",
    )

    decision = build_preview_decision(
        rule_checks=rule_checks,
        recommendations=[],
        validation=validation,
    )

    assert decision["selected_action"] == ""
    assert decision["selected_score"] == 0.0
    assert decision["accepted_actions"] == []
    assert decision["blocked_actions"] == ["deliver_payoff"]
    assert decision["prerequisite_missing_actions"] == ["open_new_thread"]
    assert decision["rule_status_summary"] == {
        "legal_count": 0,
        "blocked_count": 1,
        "prerequisite_missing_count": 1,
    }
    assert decision["constraint_hint"] == "mixed_constraints"
    assert decision["validation_case_id"] == "case-77"
    assert decision["quality_hint"] == "blocked"


def test_build_preview_decision_marks_ready_when_top_score_is_high_and_no_blocked_rules() -> None:
    rule_checks = [
        RuleCheck(action="push_conflict", status="legal"),
        RuleCheck(action="reveal_clue", status="legal"),
    ]
    recommendations = [
        SearchResult(
            action=NarrativeAction(
                action="push_conflict",
                delta={"conflict_intensity": 0.16},
                explanation="Raise direct confrontation.",
            ),
            rule_check=rule_checks[0],
            score=0.8123,
            details={"structure_value": 0.9, "feasibility": 1.0},
        )
    ]
    validation = ValidationRecord(
        case_id="case-88",
        accepted_actions=["push_conflict", "reveal_clue"],
        blocked_actions=[],
        top_action="push_conflict",
        notes="preview",
    )

    decision = build_preview_decision(
        rule_checks=rule_checks,
        recommendations=recommendations,
        validation=validation,
    )

    assert decision["quality_hint"] == "ready"
    assert decision["constraint_hint"] == "clear"


def test_build_preview_decision_marks_prerequisite_missing_when_no_legal_action_and_no_hard_block() -> None:
    rule_checks = [
        RuleCheck(action="reveal_clue", status="prerequisite_missing", blockers=["foreshadowing_load_low"]),
        RuleCheck(action="close_sideplot", status="prerequisite_missing", blockers=["sideplot_progress_low"]),
    ]
    validation = ValidationRecord(
        case_id="case-91",
        accepted_actions=[],
        blocked_actions=[],
        top_action="",
        notes="preview",
    )

    decision = build_preview_decision(
        rule_checks=rule_checks,
        recommendations=[],
        validation=validation,
    )

    assert decision["quality_hint"] == "prerequisite_missing"
    assert decision["constraint_hint"] == "prerequisite_missing"
    assert decision["rule_status_summary"] == {
        "legal_count": 0,
        "blocked_count": 0,
        "prerequisite_missing_count": 2,
    }
