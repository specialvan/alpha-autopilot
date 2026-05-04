from __future__ import annotations

from .schemas import (
    KnifeCompatibilityEdge,
    KnifePrimitive,
    RejectedKnifeReason,
    SceneContext,
    TargetProfile,
    VillainProfile,
)


def build_candidate_knife_ids(villain: VillainProfile) -> tuple[str, ...]:
    ordered_ids: list[str] = []
    for knife_id in (*villain.preferred_knives, *villain.secondary_knives, *villain.forbidden_moves):
        if knife_id not in ordered_ids:
            ordered_ids.append(knife_id)
    return tuple(ordered_ids)


def evaluate_knife_rejection(
    knife: KnifePrimitive,
    *,
    villain: VillainProfile,
    target: TargetProfile,
    scene: SceneContext,
) -> RejectedKnifeReason | None:
    if knife.id in villain.forbidden_moves:
        return RejectedKnifeReason(
            knife_id=knife.id,
            category="forbidden_move",
            detail=f"{knife.id} is explicitly forbidden by the villain profile",
        )

    for token in knife.constraints.scene_restrictions:
        if not _scene_restriction_satisfied(token, scene=scene):
            return RejectedKnifeReason(
                knife_id=knife.id,
                category="scene_restriction",
                detail=f"scene restriction failed: {token}",
            )

    for token in knife.constraints.target_restrictions:
        if not _target_restriction_satisfied(token, target=target):
            return RejectedKnifeReason(
                knife_id=knife.id,
                category="target_restriction",
                detail=f"target restriction failed: {token}",
            )

    for token in knife.constraints.observer_requirements:
        if not _observer_requirement_satisfied(token, scene=scene):
            return RejectedKnifeReason(
                knife_id=knife.id,
                category="observer_requirement_missing",
                detail=f"observer requirement missing: {token}",
            )

    for token in knife.constraints.anti_conditions:
        if _condition_triggered(token, villain=villain, target=target, scene=scene):
            return RejectedKnifeReason(
                knife_id=knife.id,
                category="anti_condition",
                detail=f"anti-condition triggered: {token}",
            )

    for token in knife.constraints.backfire_conditions:
        if _condition_triggered(token, villain=villain, target=target, scene=scene):
            return RejectedKnifeReason(
                knife_id=knife.id,
                category="backfire_condition",
                detail=f"backfire condition triggered: {token}",
            )

    for token in knife.constraints.ineffective_conditions:
        if _condition_triggered(token, villain=villain, target=target, scene=scene):
            return RejectedKnifeReason(
                knife_id=knife.id,
                category="ineffective_condition",
                detail=f"ineffective condition triggered: {token}",
            )

    for token in knife.constraints.flavor_conflicts:
        if _flavor_conflict_triggered(token, villain=villain):
            return RejectedKnifeReason(
                knife_id=knife.id,
                category="flavor_conflict",
                detail=f"flavor conflict triggered: {token}",
            )

    return None


def evaluate_compatibility_conflict(
    *,
    primary: KnifePrimitive,
    candidate: KnifePrimitive,
    compatibility_graph: tuple[KnifeCompatibilityEdge, ...],
) -> RejectedKnifeReason | None:
    pair = frozenset((primary.id, candidate.id))
    for edge in compatibility_graph:
        if frozenset((edge.left, edge.right)) != pair:
            continue
        if edge.relation == "incompatible":
            return RejectedKnifeReason(
                knife_id=candidate.id,
                category="compatibility_conflict",
                detail=edge.reason,
            )
        return None

    if candidate.id in primary.incompatible_with or primary.id in candidate.incompatible_with:
        return RejectedKnifeReason(
            knife_id=candidate.id,
            category="compatibility_conflict",
            detail=f"{candidate.id} is incompatible with primary knife {primary.id}",
        )

    return None


def _scene_restriction_satisfied(token: str, *, scene: SceneContext) -> bool:
    key, _, value = token.partition(":")
    if key == "visibility":
        return scene.visibility == value
    if key == "stake":
        return scene.stake == value
    if key == "arena":
        return scene.arena == value
    return True


def _target_restriction_satisfied(token: str, *, target: TargetProfile) -> bool:
    key, _, value = token.partition(":")
    if key == "identity_anchor" and value == "required":
        return bool(target.identity_anchor.strip())
    if key == "weak_point":
        return value in target.weak_points
    if key == "core_need":
        return target.core_need == value
    if key == "witness_sensitivity":
        return target.witness_sensitivity == value
    if key == "social_priority":
        return value in target.social_priorities
    return True


def _observer_requirement_satisfied(token: str, *, scene: SceneContext) -> bool:
    key, _, value = token.partition(":")
    if key != "observer_role":
        return True
    return any(observer.role == value for observer in scene.observers)


def _condition_triggered(
    token: str,
    *,
    villain: VillainProfile,
    target: TargetProfile,
    scene: SceneContext,
) -> bool:
    key, _, value = token.partition(":")
    if key == "witness_sensitivity":
        return target.witness_sensitivity == value
    if key == "defense_style":
        return target.defense_style == value
    if key == "resistance_style":
        return target.resistance_style == value
    if key == "time_pressure":
        return scene.time_pressure == value
    if key == "stake":
        return scene.stake == value
    if key == "time_horizon":
        return villain.time_horizon == value
    if key == "visibility":
        return scene.visibility == value
    if key == "observer_alignment":
        return any(observer.alignment == value for observer in scene.observers)
    if key == "observer_role":
        return any(observer.role == value for observer in scene.observers)
    if key == "core_need":
        return target.core_need == value
    if key == "weak_point":
        return value in target.weak_points
    if key == "identity_anchor":
        normalized = target.identity_anchor.strip().lower()
        if value == "diffuse":
            return normalized in {"diffuse", "unclear", "模糊"}
        return normalized == value
    if key == "power_edge" and value == "target_over_villain":
        return any(
            (
                edge.source == target.id
                and edge.target == villain.id
                and edge.asymmetry > 0
            )
            or (
                edge.source == villain.id
                and edge.target == target.id
                and edge.asymmetry < 0
            )
            for edge in scene.power_topology
        )
    if key == "wound_activation" and value == "already_saturated":
        return scene.existing_state.psychological.wound_activation >= 2
    return False


def _flavor_conflict_triggered(token: str, *, villain: VillainProfile) -> bool:
    key, _, value = token.partition(":")
    if key == "control_preference":
        return villain.flavor_profile.control_preference == value
    if key == "cruelty_visibility":
        return villain.flavor_profile.cruelty_visibility == value
    if key == "witness_dependence":
        return villain.flavor_profile.witness_dependence == value
    return False
