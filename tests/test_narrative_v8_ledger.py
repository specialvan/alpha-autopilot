from __future__ import annotations

import pytest

from backend.app.services.narrative_v8.ledger import apply_state_shift
from backend.app.services.narrative_v8.schemas import LedgerSnapshot, StateLedgerShift


def build_hook_payload(hook_id: str) -> dict[str, str]:
    return {
        "id": hook_id,
        "source_knife_id": "self_image_feeding",
        "description": f"{hook_id} description",
        "payoff_window": "mid",
        "recovery_condition": f"{hook_id} recovery",
    }


def build_snapshot() -> LedgerSnapshot:
    return LedgerSnapshot(
        relationship={
            "trust": 2,
            "debt": 1,
            "dependency": 0,
            "leverage": 3,
        },
        narrative={
            "suspicion": 1,
            "reputation": 0,
            "witness_alignment": 1,
            "explanation_control": 0,
        },
        psychological={
            "shame_load": 1,
            "wound_activation": 2,
            "protector_trigger": 0,
            "identity_destabilization": 1,
        },
        hook={
            "planted_hooks": (build_hook_payload("hook-existing"),),
            "armed_payoffs": (),
            "recovered_hooks": (),
        },
    )


def test_ledger_applies_bounded_deltas_per_layer() -> None:
    next_snapshot = apply_state_shift(
        build_snapshot(),
        StateLedgerShift(
            relationship={
                "trust_delta": 3,
                "debt_delta": -1,
                "dependency_delta": 1,
                "leverage_delta": 0,
            },
            narrative={
                "suspicion_delta": 1,
                "reputation_delta": 1,
                "witness_alignment_delta": -1,
                "explanation_control_delta": 1,
            },
            psychological={
                "shame_load_delta": 1,
                "wound_activation_delta": 2,
                "protector_trigger_delta": 1,
                "identity_destabilization_delta": 1,
            },
            hook={},
        ),
    )

    assert next_snapshot.relationship.trust == 3
    assert next_snapshot.relationship.debt == 0
    assert next_snapshot.relationship.leverage == 3
    assert next_snapshot.psychological.wound_activation == 3


def test_ledger_relationship_shifts_do_not_mutate_psychological_fields() -> None:
    snapshot = build_snapshot()

    next_snapshot = apply_state_shift(
        snapshot,
        StateLedgerShift(
            relationship={
                "trust_delta": -1,
                "debt_delta": 1,
                "dependency_delta": 1,
                "leverage_delta": -2,
            },
            narrative={},
            psychological={},
            hook={},
        ),
    )

    assert next_snapshot.psychological == snapshot.psychological


def test_ledger_hook_recovery_does_not_overwrite_other_layers() -> None:
    snapshot = build_snapshot()

    next_snapshot = apply_state_shift(
        snapshot,
        StateLedgerShift(
            relationship={},
            narrative={},
            psychological={},
            hook={
                "planted_hooks": (build_hook_payload("hook-future"),),
                "recovered_hooks": ("hook-existing",),
            },
        ),
    )

    assert next_snapshot.relationship == snapshot.relationship
    assert next_snapshot.narrative == snapshot.narrative
    assert "hook-existing" in next_snapshot.hook.recovered_hooks
    assert {hook.id for hook in next_snapshot.hook.planted_hooks} == {"hook-future"}


def test_ledger_rejects_more_than_two_high_magnitude_deltas() -> None:
    with pytest.raises(ValueError):
        apply_state_shift(
            build_snapshot(),
            StateLedgerShift(
                relationship={
                    "trust_delta": 2,
                    "debt_delta": 2,
                    "dependency_delta": 0,
                    "leverage_delta": 0,
                },
                narrative={
                    "suspicion_delta": 2,
                    "reputation_delta": 0,
                    "witness_alignment_delta": 0,
                    "explanation_control_delta": 0,
                },
                psychological={},
                hook={},
            ),
        )


def test_ledger_helper_returns_full_next_snapshot_without_manual_recomputation() -> None:
    next_snapshot = apply_state_shift(
        build_snapshot(),
        StateLedgerShift(
            relationship={
                "trust_delta": -1,
                "debt_delta": 2,
                "dependency_delta": 1,
                "leverage_delta": 0,
            },
            narrative={
                "suspicion_delta": 1,
                "reputation_delta": 1,
                "witness_alignment_delta": 0,
                "explanation_control_delta": 2,
            },
            psychological={
                "shame_load_delta": 1,
                "wound_activation_delta": 0,
                "protector_trigger_delta": 1,
                "identity_destabilization_delta": 0,
            },
            hook={
                "planted_hooks": (build_hook_payload("hook-next"),),
            },
        ),
    )

    assert next_snapshot.relationship.trust == 1
    assert next_snapshot.relationship.debt == 3
    assert next_snapshot.narrative.explanation_control == 2
    assert next_snapshot.psychological.protector_trigger == 1
    assert {hook.id for hook in next_snapshot.hook.planted_hooks} == {
        "hook-existing",
        "hook-next",
    }
