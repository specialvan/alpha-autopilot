from __future__ import annotations

from copy import deepcopy
from time import perf_counter
from typing import Any, Callable

from pydantic import BaseModel, Field


class CharacterValidationIssue(BaseModel):
    field_path: str
    description: str
    suggested_value: Any = None


class CharacterValidationIssueList(BaseModel):
    issues: list[CharacterValidationIssue] = Field(default_factory=list)


IssueInspector = Callable[[list[dict[str, object]]], CharacterValidationIssueList]
TargetedFixer = Callable[
    [list[dict[str, object]], CharacterValidationIssueList],
    list[dict[str, object]],
]


def run_character_validation_loop(
    characters: object,
    *,
    enabled: bool,
    inspector: IssueInspector | None = None,
    fixer: TargetedFixer | None = None,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    started_at = perf_counter()
    inspector_mode = "external_judge" if inspector is not None else "heuristic"
    fixer_mode_default = "external_fixer" if fixer is not None else "deterministic_patch"
    llm_mode = "external" if (inspector is not None or fixer is not None) else "simulated"
    if not enabled:
        return _normalized_characters(characters), {
            "enabled": False,
            "skipped": True,
            "reason": "disabled",
            "issue_list": CharacterValidationIssueList().model_dump(mode="json"),
            "llm_calls": {"generate": 0, "self_inspect": 0, "targeted_fix": 0},
            "elapsed_ms": 0.0,
            "inspector_mode": inspector_mode,
            "fixer_mode": "skipped",
            "llm_mode": llm_mode,
        }

    # Step 1: Generate
    generated = _normalized_characters(characters)
    llm_calls = {"generate": 1, "self_inspect": 1, "targeted_fix": 0}

    # Step 2: Self-Inspect
    inspect_step = inspector or _self_inspect
    issue_list = inspect_step(generated)

    # Step 3: Targeted-Fix
    if issue_list.issues:
        fix_step = fixer or _apply_targeted_fixes
        fixed = fix_step(generated, issue_list)
        llm_calls["targeted_fix"] = 1
        fixer_mode = fixer_mode_default
    else:
        fixed = generated
        fixer_mode = "skipped"

    elapsed_ms = max(0.0, round((perf_counter() - started_at) * 1000.0, 4))
    return fixed, {
        "enabled": True,
        "skipped": False,
        "issue_list": issue_list.model_dump(mode="json"),
        "issue_count": len(issue_list.issues),
        "llm_calls": llm_calls,
        "elapsed_ms": elapsed_ms,
        "inspector_mode": inspector_mode,
        "fixer_mode": fixer_mode,
        "llm_mode": llm_mode,
    }


def _normalized_characters(characters: object) -> list[dict[str, object]]:
    if not isinstance(characters, list):
        return []
    return [deepcopy(item) for item in characters if isinstance(item, dict)]


def _self_inspect(characters: list[dict[str, object]]) -> CharacterValidationIssueList:
    issues: list[CharacterValidationIssue] = []
    for index, character in enumerate(characters):
        function_type = str(character.get("function_type", "")).strip().lower()
        if function_type == "disguise":
            if not str(character.get("surface_relation", "")).strip():
                issues.append(
                    CharacterValidationIssue(
                        field_path=f"{index}.surface_relation",
                        description="Disguise role requires a surface_relation.",
                        suggested_value="unknown",
                    )
                )
            if not str(character.get("actual_relation", "")).strip():
                issues.append(
                    CharacterValidationIssue(
                        field_path=f"{index}.actual_relation",
                        description="Disguise role requires an actual_relation.",
                        suggested_value="unknown",
                    )
                )

        emotion_slider_map = character.get("emotion_slider_map")
        if isinstance(emotion_slider_map, dict):
            baseline = emotion_slider_map.get("baseline")
            if isinstance(baseline, dict):
                stress = _safe_float(baseline.get("stress_baseline"), default=0.0)
                calmness = _safe_float(character.get("calmness"), default=0.5)
                if stress > 5 and calmness > 0.8:
                    issues.append(
                        CharacterValidationIssue(
                            field_path=f"{index}.calmness",
                            description="High stress character should not keep extreme calmness.",
                            suggested_value=0.65,
                        )
                    )
    return CharacterValidationIssueList(issues=issues)


def _apply_targeted_fixes(
    characters: list[dict[str, object]],
    issue_list: CharacterValidationIssueList,
) -> list[dict[str, object]]:
    fixed = deepcopy(characters)
    for issue in issue_list.issues:
        if issue.suggested_value is None:
            continue
        _set_path(fixed, issue.field_path, issue.suggested_value)
    return fixed


def _set_path(characters: list[dict[str, object]], field_path: str, value: Any) -> None:
    segments = field_path.split(".")
    if not segments:
        return
    try:
        character_index = int(segments[0])
    except Exception:
        return
    if character_index < 0 or character_index >= len(characters):
        return
    target: Any = characters[character_index]
    for segment in segments[1:-1]:
        if not isinstance(target, dict):
            return
        if segment not in target or not isinstance(target[segment], dict):
            target[segment] = {}
        target = target[segment]
    last = segments[-1]
    if isinstance(target, dict):
        target[last] = value


def _safe_float(value: object, *, default: float) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except Exception:
        return default
