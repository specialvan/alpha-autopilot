from __future__ import annotations

from .constraints import (
    build_candidate_knife_ids,
    evaluate_compatibility_conflict,
    evaluate_knife_rejection,
)
from .knife_library import build_compatibility_graph, build_default_knife_library, get_knife_by_id
from .schemas import (
    DecisionLayer,
    KnifeCompatibilityEdge,
    KnifePrimitive,
    NarrativeV8BaseModel,
    RejectedKnifeReason,
    SceneContext,
    SelectedKnifeSignal,
    TargetProfile,
    VillainProfile,
)


PUBLIC_PRESSURE_KNIVES = {"self_image_feeding", "courteous_humiliation", "high_ground_pity"}
PRIVATE_PRESSURE_KNIVES = {"fake_vulnerability", "gentle_absorption", "relationship_withdrawal"}
RESOURCE_PRESSURE_KNIVES = {"baited_concession", "delayed_asking"}
MEMORY_PRESSURE_KNIVES = {"old_wound_trigger", "memory_reframing"}
PRIMARY_SELECTION_THRESHOLD = 0.55
SECONDARY_SELECTION_THRESHOLD = 0.68


class KnifeSelectionResult(NarrativeV8BaseModel):
    decision: DecisionLayer
    scored_candidates: tuple[SelectedKnifeSignal, ...] = ()


def select_knives(
    villain: VillainProfile,
    target: TargetProfile,
    scene: SceneContext,
    *,
    library: tuple[KnifePrimitive, ...] | None = None,
    compatibility_graph: tuple[KnifeCompatibilityEdge, ...] | None = None,
) -> KnifeSelectionResult:
    resolved_library = library or build_default_knife_library()
    resolved_graph = compatibility_graph or build_compatibility_graph()
    rejections: list[RejectedKnifeReason] = []
    scored_candidates: list[SelectedKnifeSignal] = []

    for knife_id in build_candidate_knife_ids(villain):
        knife = get_knife_by_id(knife_id, library=resolved_library)
        rejection = evaluate_knife_rejection(
            knife,
            villain=villain,
            target=target,
            scene=scene,
        )
        if rejection is not None:
            rejections.append(rejection)
            continue

        scored_candidates.append(_score_candidate(knife, villain=villain, target=target, scene=scene))

    scored_candidates.sort(key=lambda item: item.fit_score, reverse=True)

    viable_candidates = [
        candidate for candidate in scored_candidates if candidate.fit_score >= PRIMARY_SELECTION_THRESHOLD
    ]
    if not viable_candidates:
        return KnifeSelectionResult(
            decision=_build_fallback_decision(
                scene=scene,
                rejected_knives=tuple(
                    rejections
                    + _low_fit_rejections(
                        scored_candidates,
                        detail="survived hard filters but did not meet the fit threshold",
                    )
                ),
                fallback_reason="no knife survived hard filters with a usable fit score",
            ),
            scored_candidates=tuple(scored_candidates),
        )

    primary_signal = viable_candidates[0]
    primary_knife = get_knife_by_id(primary_signal.knife_id, library=resolved_library)
    selected_signals: list[SelectedKnifeSignal] = [primary_signal]

    for candidate_signal in viable_candidates[1:]:
        if candidate_signal.fit_score < SECONDARY_SELECTION_THRESHOLD:
            rejections.append(
                RejectedKnifeReason(
                    knife_id=candidate_signal.knife_id,
                    category="low_fit_score",
                    detail="candidate ranked below the secondary selection threshold",
                )
            )
            continue

        candidate_knife = get_knife_by_id(candidate_signal.knife_id, library=resolved_library)
        compatibility_issue = evaluate_compatibility_conflict(
            primary=primary_knife,
            candidate=candidate_knife,
            compatibility_graph=resolved_graph,
        )
        if compatibility_issue is not None:
            rejections.append(compatibility_issue)
            continue

        selected_signals.append(candidate_signal)
        break

    selected_ids = {signal.knife_id for signal in selected_signals}
    for candidate_signal in scored_candidates:
        if candidate_signal.knife_id in selected_ids:
            continue
        if candidate_signal.fit_score < PRIMARY_SELECTION_THRESHOLD:
            rejections.append(
                RejectedKnifeReason(
                    knife_id=candidate_signal.knife_id,
                    category="low_fit_score",
                    detail="candidate ranked below the primary selection threshold",
                )
            )
            continue
        if candidate_signal.fit_score < SECONDARY_SELECTION_THRESHOLD:
            rejections.append(
                RejectedKnifeReason(
                    knife_id=candidate_signal.knife_id,
                    category="low_fit_score",
                    detail="candidate stayed in the scored pool but was too weak for selection",
                )
            )

    secondary_signal = selected_signals[1] if len(selected_signals) > 1 else None
    decision = DecisionLayer(
        selection_mode="scored_fit",
        primary_knife_id=primary_signal.knife_id,
        secondary_knife_id=secondary_signal.knife_id if secondary_signal else None,
        selected_signals=tuple(selected_signals),
        rejected_knives=tuple(rejections),
    )
    return KnifeSelectionResult(decision=decision, scored_candidates=tuple(scored_candidates))


def _score_candidate(
    knife: KnifePrimitive,
    *,
    villain: VillainProfile,
    target: TargetProfile,
    scene: SceneContext,
) -> SelectedKnifeSignal:
    score = 0.2
    reasons: list[str] = []

    if knife.id in villain.preferred_knives:
        score += 0.3
        reasons.append("preferred_palette")
        if villain.preferred_knives and knife.id == villain.preferred_knives[0]:
            score += 0.05
            reasons.append("lead_preference")
    elif knife.id in villain.secondary_knives:
        score += 0.16
        reasons.append("secondary_palette")

    if scene.arena in knife.best_arenas:
        score += 0.12
        reasons.append(f"arena_fit:{scene.arena}")

    if knife.id in PUBLIC_PRESSURE_KNIVES and scene.stake == "reputation":
        score += 0.1
        reasons.append("reputation_pressure")
    if knife.id in PRIVATE_PRESSURE_KNIVES and scene.stake == "bond":
        score += 0.1
        reasons.append("bond_pressure")
    if knife.id in RESOURCE_PRESSURE_KNIVES and scene.stake == "resource":
        score += 0.1
        reasons.append("resource_pressure")

    if knife.id in PUBLIC_PRESSURE_KNIVES and target.witness_sensitivity == "high":
        score += 0.1
        reasons.append("witness_sensitive_target")
    if knife.id in {"self_image_feeding", "memory_reframing"} and target.identity_anchor.strip():
        score += 0.08
        reasons.append("identity_anchor_exposed")
    if knife.id == "fake_vulnerability" and "protector_complex" in target.weak_points:
        score += 0.12
        reasons.append("protector_complex_target")
    if knife.id in {"delayed_asking", "baited_concession"} and "debt_sensitive" in target.weak_points:
        score += 0.1
        reasons.append("debt_sensitive_target")
    if knife.id in MEMORY_PRESSURE_KNIVES and "old_wound" in target.weak_points:
        score += 0.1
        reasons.append("old_wound_target")

    control_preference = villain.flavor_profile.control_preference
    if control_preference == "public_rewrite" and knife.id in PUBLIC_PRESSURE_KNIVES:
        score += 0.14
        reasons.append("public_rewrite_fit")
    if control_preference == "private_invasion" and knife.id in PRIVATE_PRESSURE_KNIVES:
        score += 0.14
        reasons.append("private_invasion_fit")
    if control_preference == "resource_cut" and knife.id in RESOURCE_PRESSURE_KNIVES:
        score += 0.14
        reasons.append("resource_cut_fit")
    if control_preference == "emotional_absorption" and knife.id in {"gentle_absorption", "fake_vulnerability"}:
        score += 0.14
        reasons.append("emotional_absorption_fit")

    if villain.witness_need == "high" and knife.id in PUBLIC_PRESSURE_KNIVES:
        score += 0.08
        reasons.append("high_witness_need")
    if villain.witness_need == "low" and knife.id in PUBLIC_PRESSURE_KNIVES:
        score -= 0.04
        reasons.append("low_witness_need_drag")

    if villain.psychology_literacy == "systematic" and knife.id in {
        "self_image_feeding",
        "memory_reframing",
        "baited_concession",
    }:
        score += 0.06
        reasons.append("systematic_modeling")
    if villain.psychology_literacy in {"instinctive", "experiential"} and knife.id in {
        "fake_vulnerability",
        "gentle_absorption",
        "relationship_withdrawal",
    }:
        score += 0.06
        reasons.append("embodied_reading")

    observer_bonus = _observer_support_bonus(knife=knife, scene=scene)
    if observer_bonus > 0.0:
        score += observer_bonus
        reasons.append("observer_topology_support")

    final_score = max(0.0, min(0.99, round(score / 1.45, 4)))
    return SelectedKnifeSignal(
        knife_id=knife.id,
        fit_score=final_score,
        reasons=tuple(reasons or ["baseline_fit"]),
    )


def _observer_support_bonus(*, knife: KnifePrimitive, scene: SceneContext) -> float:
    if not knife.constraints.observer_requirements:
        return 0.0
    weighted_support = sum(
        observer.importance + max(observer.visibility_impact, 0)
        for observer in scene.observers
        if observer.alignment != "target"
    )
    return min(0.14, weighted_support / 50.0)


def _build_fallback_decision(
    *,
    scene: SceneContext,
    rejected_knives: tuple[RejectedKnifeReason, ...],
    fallback_reason: str,
) -> DecisionLayer:
    fallback_action = "reduce_exposure" if scene.visibility == "public" else "gather_information"
    return DecisionLayer(
        selection_mode="fallback",
        fallback_action=fallback_action,
        fallback_reason=fallback_reason,
        selected_signals=(),
        rejected_knives=rejected_knives,
    )


def _low_fit_rejections(
    scored_candidates: list[SelectedKnifeSignal], *, detail: str
) -> list[RejectedKnifeReason]:
    return [
        RejectedKnifeReason(
            knife_id=candidate.knife_id,
            category="low_fit_score",
            detail=detail,
        )
        for candidate in scored_candidates
    ]
