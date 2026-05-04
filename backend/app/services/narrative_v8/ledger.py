from __future__ import annotations

from .schemas import (
    HookLedgerState,
    LedgerSnapshot,
    NarrativeLedgerState,
    PsychologicalLedgerState,
    RelationshipLedgerState,
    StateLedgerShift,
)


LEDGER_LOW = -3
LEDGER_HIGH = 3
HIGH_MAGNITUDE_THRESHOLD = 1
MAX_HIGH_MAGNITUDE_DELTAS = 2


def apply_state_shift(snapshot: LedgerSnapshot, shift: StateLedgerShift) -> LedgerSnapshot:
    if count_high_magnitude_deltas(shift) > MAX_HIGH_MAGNITUDE_DELTAS:
        raise ValueError("at most two high-magnitude deltas are allowed per scene")

    return LedgerSnapshot(
        relationship=_apply_relationship(snapshot, shift),
        narrative=_apply_narrative(snapshot, shift),
        psychological=_apply_psychological(snapshot, shift),
        hook=_apply_hooks(snapshot, shift),
    )


def count_high_magnitude_deltas(shift: StateLedgerShift) -> int:
    delta_values = (
        shift.relationship.trust_delta,
        shift.relationship.debt_delta,
        shift.relationship.dependency_delta,
        shift.relationship.leverage_delta,
        shift.narrative.suspicion_delta,
        shift.narrative.reputation_delta,
        shift.narrative.witness_alignment_delta,
        shift.narrative.explanation_control_delta,
        shift.psychological.shame_load_delta,
        shift.psychological.wound_activation_delta,
        shift.psychological.protector_trigger_delta,
        shift.psychological.identity_destabilization_delta,
    )
    return sum(1 for value in delta_values if abs(value) > HIGH_MAGNITUDE_THRESHOLD)


def _apply_relationship(snapshot: LedgerSnapshot, shift: StateLedgerShift) -> RelationshipLedgerState:
    return RelationshipLedgerState(
        trust=_clamp(snapshot.relationship.trust + shift.relationship.trust_delta),
        debt=_clamp(snapshot.relationship.debt + shift.relationship.debt_delta),
        dependency=_clamp(snapshot.relationship.dependency + shift.relationship.dependency_delta),
        leverage=_clamp(snapshot.relationship.leverage + shift.relationship.leverage_delta),
    )


def _apply_narrative(snapshot: LedgerSnapshot, shift: StateLedgerShift) -> NarrativeLedgerState:
    return NarrativeLedgerState(
        suspicion=_clamp(snapshot.narrative.suspicion + shift.narrative.suspicion_delta),
        reputation=_clamp(snapshot.narrative.reputation + shift.narrative.reputation_delta),
        witness_alignment=_clamp(
            snapshot.narrative.witness_alignment + shift.narrative.witness_alignment_delta
        ),
        explanation_control=_clamp(
            snapshot.narrative.explanation_control + shift.narrative.explanation_control_delta
        ),
    )


def _apply_psychological(
    snapshot: LedgerSnapshot, shift: StateLedgerShift
) -> PsychologicalLedgerState:
    return PsychologicalLedgerState(
        shame_load=_clamp(snapshot.psychological.shame_load + shift.psychological.shame_load_delta),
        wound_activation=_clamp(
            snapshot.psychological.wound_activation + shift.psychological.wound_activation_delta
        ),
        protector_trigger=_clamp(
            snapshot.psychological.protector_trigger + shift.psychological.protector_trigger_delta
        ),
        identity_destabilization=_clamp(
            snapshot.psychological.identity_destabilization
            + shift.psychological.identity_destabilization_delta
        ),
    )


def _apply_hooks(snapshot: LedgerSnapshot, shift: StateLedgerShift) -> HookLedgerState:
    recovered_ids = list(snapshot.hook.recovered_hooks)
    for hook_id in shift.hook.recovered_hooks:
        if hook_id not in recovered_ids:
            recovered_ids.append(hook_id)
    recovered_set = set(recovered_ids)

    planted_hooks = [
        hook for hook in snapshot.hook.planted_hooks if hook.id not in recovered_set
    ]
    armed_payoffs = [
        hook for hook in snapshot.hook.armed_payoffs if hook.id not in recovered_set
    ]

    planted_hooks = _merge_hook_lists(planted_hooks, shift.hook.planted_hooks, recovered_set)
    armed_payoffs = _merge_hook_lists(armed_payoffs, shift.hook.armed_payoffs, recovered_set)

    return HookLedgerState(
        planted_hooks=tuple(planted_hooks),
        armed_payoffs=tuple(armed_payoffs),
        recovered_hooks=tuple(recovered_ids),
    )


def _merge_hook_lists(existing_hooks, incoming_hooks, recovered_set: set[str]):
    merged = {hook.id: hook for hook in existing_hooks if hook.id not in recovered_set}
    for hook in incoming_hooks:
        if hook.id in recovered_set:
            continue
        merged[hook.id] = hook
    return list(merged.values())


def _clamp(value: int) -> int:
    return max(LEDGER_LOW, min(LEDGER_HIGH, int(value)))
