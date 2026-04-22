# V3 Reverse Decomposition Quality Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first executable slice of the V3 reverse-decomposition quality layer so chapter text can be turned into taxonomy-stable, QC-gated, machine-consumable decomposition records.

**Architecture:** This implementation adds a new `alpha_autopilot_v3` package instead of expanding `v2`, keeping the quality layer isolated from the calibration baseline. The first slice covers taxonomy definitions, decomposition/QC schemas, a heuristic decomposition pipeline, admission grading, PlotPilot report import, and a local script that emits normalized records and training-oriented projections.

**Tech Stack:** Python 3.10+, stdlib, pytest

---

## File Map

- Create: `D:\workspace\alpha-autopilot\alpha_autopilot_v3\__init__.py`
- Create: `D:\workspace\alpha-autopilot\alpha_autopilot_v3\decomposition\__init__.py`
- Create: `D:\workspace\alpha-autopilot\alpha_autopilot_v3\decomposition\taxonomy.py`
- Create: `D:\workspace\alpha-autopilot\alpha_autopilot_v3\decomposition\models.py`
- Create: `D:\workspace\alpha-autopilot\alpha_autopilot_v3\decomposition\pipeline.py`
- Create: `D:\workspace\alpha-autopilot\alpha_autopilot_v3\decomposition\projection.py`
- Create: `D:\workspace\alpha-autopilot\scripts\build_v3_reverse_decomposition_records.py`
- Create: `D:\workspace\alpha-autopilot\tests\test_alpha_autopilot_v3_taxonomy_and_models.py`
- Create: `D:\workspace\alpha-autopilot\tests\test_alpha_autopilot_v3_pipeline.py`
- Create: `D:\workspace\alpha-autopilot\tests\test_alpha_autopilot_v3_plotpilot_import.py`
- Create: `D:\workspace\alpha-autopilot\tests\test_alpha_autopilot_v3_build_script.py`

### Task 1: Add Frozen Taxonomy and Record Schemas

**Files:**
- Create: `D:\workspace\alpha-autopilot\alpha_autopilot_v3\__init__.py`
- Create: `D:\workspace\alpha-autopilot\alpha_autopilot_v3\decomposition\__init__.py`
- Create: `D:\workspace\alpha-autopilot\alpha_autopilot_v3\decomposition\taxonomy.py`
- Create: `D:\workspace\alpha-autopilot\alpha_autopilot_v3\decomposition\models.py`
- Test: `D:\workspace\alpha-autopilot\tests\test_alpha_autopilot_v3_taxonomy_and_models.py`

- [ ] **Step 1: Write the failing taxonomy/schema test**

```python
from alpha_autopilot_v3.decomposition.models import (
    ChapterDecompositionRecord,
    CheckpointResult,
    EvidenceSpan,
)
from alpha_autopilot_v3.decomposition.taxonomy import (
    CHAPTER_FUNCTIONS,
    CHECKPOINTS,
    STYLE_DNA_AXES,
)


def test_v3_taxonomy_and_models_expose_frozen_decomposition_contract() -> None:
    assert "conflict-escalation" in CHAPTER_FUNCTIONS
    assert "chapter-function-fit" in CHECKPOINTS
    assert "pace" in STYLE_DNA_AXES

    record = ChapterDecompositionRecord(
        chapter_number=8,
        title="Pressure Rises in the Midpoint",
        scope="single",
        genre="xuanhuan",
        stage="middle",
        stage_inferred=False,
        primary_function="conflict-escalation",
        secondary_functions=["foreshadow-plant"],
        structure={
            "goal": "Drive the protagonist into open conflict.",
            "opening_hook": "The creditor arrives before dawn.",
            "escalations": ["debt threat", "public humiliation"],
            "reversal_or_reveal": "The creditor serves another faction.",
            "payoff": "The protagonist refuses to kneel.",
            "ending_hook": "A stronger enemy notices the scene.",
        },
        style_dna={
            "pace": "brisk",
            "dialogue_reliance": "medium",
            "emotional_directness": "explicit",
        },
        evidence_spans=[
            EvidenceSpan(
                label="opening_hook",
                text="The creditor arrived before dawn.",
                paragraph_index=0,
                confidence="direct",
            )
        ],
        checkpoints=[
            CheckpointResult(
                name="chapter-function-fit",
                status="pass",
                evidence="The chapter cleanly escalates the debt conflict.",
                implication="Safe for approved pool.",
            )
        ],
        admission="approved",
        workbench_context={
            "recommended_stage": "middle",
            "narrative_signals": {"conflict_intensity": 0.76, "payoff_pressure": 0.31},
            "notes": "Conflict spike without payoff release.",
        },
    )

    assert record.primary_function == "conflict-escalation"
    assert record.checkpoints[0].status == "pass"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_alpha_autopilot_v3_taxonomy_and_models.py -q`
Expected: `ModuleNotFoundError: No module named 'alpha_autopilot_v3'`

- [ ] **Step 3: Write the minimal taxonomy and dataclasses**

```python
CHAPTER_FUNCTIONS = (
    "hook-opening",
    "conflict-escalation",
    "information-reveal",
    "payoff-delivery",
    "transition-breathing",
    "pre-climax-loading",
    "climax-execution",
    "closing-consolidation",
)
STYLE_DNA_AXES = (
    "pace",
    "exposition_density",
    "dialogue_reliance",
    "emotional_directness",
    "sensory_density",
    "conflict_sharpness",
    "hook_aggression",
    "payoff_explicitness",
)
CHECKPOINTS = (
    "continuity-stability",
    "conflict-progression",
    "emotional-reward",
    "foreshadow-payoff-balance",
    "chapter-function-fit",
    "read-through-drive",
)
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_alpha_autopilot_v3_taxonomy_and_models.py -q`
Expected: `1 passed`

### Task 2: Add Heuristic Decomposition, Checkpoints, and Admission Grading

**Files:**
- Modify: `D:\workspace\alpha-autopilot\alpha_autopilot_v3\decomposition\models.py`
- Create: `D:\workspace\alpha-autopilot\alpha_autopilot_v3\decomposition\pipeline.py`
- Test: `D:\workspace\alpha-autopilot\tests\test_alpha_autopilot_v3_pipeline.py`

- [ ] **Step 1: Write the failing pipeline test**

```python
from alpha_autopilot_v3.decomposition.pipeline import decompose_chapter_text


def test_v3_pipeline_emits_evidence_style_qc_and_admission() -> None:
    chapter = (
        "债主在天亮前堵门。\\n\\n"
        "他先把欠条摔在桌上，又叫人砸碎门框。\\n\\n"
        "主角没有退，反而当众掀桌。\\n\\n"
        "巷口最后出现了一名更强的敌人。"
    )

    result = decompose_chapter_text(
        chapter_number=8,
        title="Pressure Rises in the Midpoint",
        text=chapter,
        genre="xuanhuan",
        stage="middle",
    )

    assert result.primary_function == "conflict-escalation"
    assert result.evidence_spans
    assert result.workbench_context["narrative_signals"]["conflict_intensity"] > 0.6
    assert result.admission in {"approved", "provisional", "rejected"}
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_alpha_autopilot_v3_pipeline.py -q`
Expected: `Cannot find module 'alpha_autopilot_v3.decomposition.pipeline'`

- [ ] **Step 3: Implement the minimal heuristic pipeline**

```python
def decompose_chapter_text(...):
    # split paragraphs
    # infer primary function with simple conflict / reveal / payoff heuristics
    # create evidence span list from decisive paragraphs
    # emit bounded style DNA
    # evaluate checkpoint results
    # assign admission:
    #   approved when no fail checkpoints
    #   provisional when any mixed but no fail
    #   rejected when any fail
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_alpha_autopilot_v3_pipeline.py -q`
Expected: `1 passed`

### Task 3: Import PlotPilot Report Data into V3 Records

**Files:**
- Modify: `D:\workspace\alpha-autopilot\alpha_autopilot_v3\decomposition\pipeline.py`
- Create: `D:\workspace\alpha-autopilot\alpha_autopilot_v3\decomposition\projection.py`
- Test: `D:\workspace\alpha-autopilot\tests\test_alpha_autopilot_v3_plotpilot_import.py`

- [ ] **Step 1: Write the failing PlotPilot import test**

```python
from alpha_autopilot_v3.decomposition.pipeline import build_records_from_plotpilot_report


def test_v3_plotpilot_import_turns_report_into_decomposition_records() -> None:
    payload = {
        "model": "gpt-5.4",
        "results": [
            {
                "chapter": 1,
                "title": "black_jade_awakens",
                "success": True,
                "chars": 3354,
                "preview": "A young cultivator escapes into a sword valley.",
            }
        ],
    }

    records = build_records_from_plotpilot_report(payload, genre="xuanhuan")

    assert len(records) == 1
    assert records[0].title == "black jade awakens"
    assert records[0].workbench_context["recommended_stage"] == "opening"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_alpha_autopilot_v3_plotpilot_import.py -q`
Expected: missing function failure

- [ ] **Step 3: Implement PlotPilot report conversion and projection**

```python
def build_records_from_plotpilot_report(payload, genre):
    # map each successful result to decompose_chapter_text(...)
    # use preview as source text seed
    # title = slug with spaces

def project_record_for_matrix(record):
    return {
        "primary_function": record.primary_function,
        "style_dna": record.style_dna,
        "admission": record.admission,
        "recommended_stage": record.workbench_context["recommended_stage"],
    }
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_alpha_autopilot_v3_plotpilot_import.py -q`
Expected: `1 passed`

### Task 4: Add a Local Build Script for Approved V3 Records

**Files:**
- Create: `D:\workspace\alpha-autopilot\scripts\build_v3_reverse_decomposition_records.py`
- Test: `D:\workspace\alpha-autopilot\tests\test_alpha_autopilot_v3_build_script.py`

- [ ] **Step 1: Write the failing script test**

```python
import json
import subprocess
import sys
from pathlib import Path


def test_v3_build_script_emits_records_and_matrix_projection(tmp_path: Path) -> None:
    source = tmp_path / "report.json"
    source.write_text(
        json.dumps(
            {
                "model": "gpt-5.4",
                "results": [
                    {
                        "chapter": 1,
                        "title": "black_jade_awakens",
                        "success": True,
                        "chars": 3354,
                        "preview": "A young cultivator escapes into a sword valley.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    target = tmp_path / "out"
    cmd = [
        sys.executable,
        "scripts/build_v3_reverse_decomposition_records.py",
        "--input-report",
        str(source),
        "--output-dir",
        str(target),
        "--genre",
        "xuanhuan",
    ]
    result = subprocess.run(cmd, cwd=Path(__file__).resolve().parents[1], check=False)

    assert result.returncode == 0
    assert (target / "reverse_outline_records.jsonl").exists()
    assert (target / "matrix_projection.json").exists()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_alpha_autopilot_v3_build_script.py -q`
Expected: script file not found

- [ ] **Step 3: Implement the script**

```python
# read PlotPilot report JSON
# call build_records_from_plotpilot_report(...)
# write reverse_outline_records.jsonl
# write matrix_projection.json from approved + provisional records
# print summary JSON
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest tests/test_alpha_autopilot_v3_build_script.py -q`
Expected: `1 passed`

### Task 5: Run Verification

**Files:**
- Test: `D:\workspace\alpha-autopilot\tests\test_alpha_autopilot_v3_taxonomy_and_models.py`
- Test: `D:\workspace\alpha-autopilot\tests\test_alpha_autopilot_v3_pipeline.py`
- Test: `D:\workspace\alpha-autopilot\tests\test_alpha_autopilot_v3_plotpilot_import.py`
- Test: `D:\workspace\alpha-autopilot\tests\test_alpha_autopilot_v3_build_script.py`

- [ ] **Step 1: Run targeted V3 tests**

Run:

```bash
pytest tests/test_alpha_autopilot_v3_taxonomy_and_models.py tests/test_alpha_autopilot_v3_pipeline.py tests/test_alpha_autopilot_v3_plotpilot_import.py tests/test_alpha_autopilot_v3_build_script.py -q
```

Expected:

```text
4 passed
```

- [ ] **Step 2: Run the broader V2/V3 regression slice**

Run:

```bash
pytest tests -q -k "v2 or v3"
```

Expected:

```text
all targeted v2/v3 tests pass
```

## Self-Review

- Spec coverage:
  - taxonomy and schema: Task 1
  - evidence-anchored decomposition: Task 2
  - PlotPilot import: Task 3
  - training-oriented projection: Task 3 and Task 4
  - local executable dataset builder: Task 4
- Placeholder scan:
  - No placeholder markers remain.
- Type consistency:
  - `ChapterDecompositionRecord` remains the central artifact passed from pipeline to projection and script output.
