# V2 Workbench Design

**Date**: 2026-04-22

## 1. Goal

Promote the current `v2` preview surface from an embedded debug panel into a dedicated `V2 Workbench` route that supports chapter-mapped context, decision comparison, session run history, and exportable validation snapshots.

The workbench should preserve the current strengths of `v2`:

- transparent `rule -> search -> evaluation -> validation` visibility
- fast iteration on a single chapter decision
- stable validation artifacts

It should also adopt the product interaction strengths observed in `PlotPilot`:

- task-first workspace structure
- explicit context selection
- continuous operator flow
- visible status and traceability

## 2. Non-Goals

This design does **not** attempt to rebuild the full PlotPilot platform.

Out of scope for this phase:

- multi-book home/dashboard replacement
- full chapter authoring editor
- autopilot daemon control surface
- cast graph / location graph / worldbuilding suites
- replacing the existing `v1` dashboard

This phase focuses only on a high-capability `v2` decision cockpit.

## 3. Product Positioning

`V2 Workbench` is a **single-chapter decision cockpit**.

It answers:

1. What is the best narrative action for the current chapter context?
2. Why is that action recommended now?
3. Which actions are blocked, and why?
4. How does this run differ from the previous run?
5. What validation artifact should be retained from this run?

This differs from the current embedded `V2PreviewLab`, which is an inspection panel inside the existing dashboard.

## 4. UX Direction

The workbench becomes a standalone route and uses a three-column workspace layout:

- **Left: Context Rail**
  Holds source selection, chapter selection, base state summary, and manual overrides.
- **Center: Decision Surface**
  Holds the top recommendation, candidate ranking, score breakdown, and narrative explanation.
- **Right: Validation Rail**
  Holds rule legality, blocker aggregation, validation record, run history, and export actions.

The reading order is:

1. What chapter/context am I looking at?
2. What does the system recommend?
3. Why does it recommend that?
4. What is blocked?
5. What changed versus the previous run?
6. What trace should I retain?

## 5. Advanced Capabilities Included in Phase 1

This design explicitly includes the advanced capabilities requested by the user.

### 5.1 Chapter-Mapped Context

The workbench supports three context sources:

- `demo`
- `mapped_chapter`
- `manual_override`

`mapped_chapter` is the primary workflow path.

The system should derive a `NarrativeV2StoryState` from chapter metadata or chapter-level context and let the operator refine it through overrides.

### 5.2 Compare Last Run

Each run can be compared against:

- the immediately previous run
- a selected historical run from the session history

The comparison must show at least:

- top action change
- top score delta
- rule status deltas
- blocker deltas

### 5.3 Session Run History

The workbench keeps an in-memory session history of recent runs.

Each entry contains:

- timestamp
- source
- chapter identifier or case id
- top action
- top score
- full preview payload snapshot

History is session-scoped for this phase.

### 5.4 State Diff View

The UI must distinguish:

- chapter-mapped base state
- operator overrides
- final submitted state

The operator can see which fields were changed and by how much.

### 5.5 Snapshot Export

The operator can export a structured JSON snapshot containing:

- context source metadata
- mapped chapter metadata when present
- base state
- override set
- submitted state
- full `v2` preview response
- comparison metadata
- export timestamp

## 6. Route and Navigation Model

Add a dedicated route for the workbench.

Recommended route:

- `/v2/workbench`

Optional query parameters:

- `source=demo|mapped_chapter|manual_override`
- `chapter=<id>`
- `case=<id>`

The existing dashboard remains intact. The new workbench is a parallel surface, not a replacement.

## 7. Information Architecture

### 7.1 Top Bar

The top bar replaces marketing-style hero content with operational context.

It shows:

- breadcrumb or label: `Book / Chapter / Stage`
- fixed product label: `V2 Workbench`
- source badge
- last run timestamp
- actions:
  - `Run Preview`
  - `Compare Last Run`
  - `Export Snapshot`

### 7.2 Context Rail

The left rail contains:

- source switcher
- chapter picker
- chapter summary card
- state summary card
- override editor
- state diff summary

Default behavior:

- users see chapter-mapped context first
- override controls are secondary, not dominant

### 7.3 Decision Surface

The center surface contains:

- `RecommendationHeroCard`
- compare strip
- ranked candidate list
- score breakdown
- narrative explanation / expected effect

The center surface is the visual focal point of the page.

### 7.4 Validation Rail

The right rail contains:

- rule summary by legality state
- blocked reason aggregation
- validation record
- recent run history
- export tools

## 8. Component Model

### 8.1 Route-Level Container

#### `V2WorkbenchPage`

Responsibilities:

- route entry
- initial context load
- chapter mapping orchestration
- current vs comparison preview state
- session run history
- export orchestration

### 8.2 Structural Components

#### `WorkbenchTopBar`

Responsibilities:

- route-level title and breadcrumb
- source / chapter badges
- run / compare / export actions

#### `ContextRail`

Responsibilities:

- source switching
- chapter selection
- chapter context summary
- base state summary
- manual override controls
- state diff summary

#### `DecisionSurface`

Responsibilities:

- own the main recommendation reading flow
- hold hero card, candidates, breakdown, and explanation sections

#### `ValidationRail`

Responsibilities:

- own legality, blocker, trace, and history sections

### 8.3 Decision Components

#### `RecommendationHeroCard`

Displays:

- top action
- top score
- short “why now”
- expected state delta
- change vs comparison run

#### `CandidateList`

Displays ranked candidates with:

- action name
- score
- rule status
- one-line explanation
- top dimensions

#### `ScoreBreakdownPanel`

Displays the detailed score dimensions for the selected or top candidate.

#### `NarrativeExplanationPanel`

Displays:

- why this action fits the current context
- what it is expected to change next

### 8.4 Validation Components

#### `RuleSummaryPanel`

Groups rule checks into:

- `legal`
- `blocked`
- `prerequisite_missing`

#### `BlockedReasonPanel`

Aggregates blocker reasons into a compact human-readable summary.

#### `ValidationRecordPanel`

Displays:

- case id
- accepted actions
- blocked actions
- top action
- notes

#### `RunHistoryPanel`

Displays recent run entries and supports picking one as comparison baseline.

## 9. State Model

### 9.1 Primary State

- `contextSource`
- `selectedChapter`
- `baseState`
- `workingState`
- `overrides`
- `currentPreview`
- `comparisonPreview`
- `runHistory`
- `uiStatus`

### 9.2 State Definitions

#### `contextSource`

One of:

- `demo`
- `mapped_chapter`
- `manual_override`

#### `selectedChapter`

The active chapter context when chapter mapping is used.

#### `baseState`

The system-derived `NarrativeV2StoryState` from the current source.

#### `overrides`

Only the operator-modified fields.

#### `workingState`

The state submitted to `/api/v2/recommendation/preview`.

Computed as:

- `workingState = baseState + overrides`

#### `currentPreview`

The latest successful `v2` preview response.

#### `comparisonPreview`

The currently selected baseline preview for diff presentation.

#### `runHistory`

Session-scoped list of prior successful runs.

#### `uiStatus`

One of:

- `loading_context`
- `ready`
- `dirty`
- `running`
- `error`

## 10. Interaction Model

### 10.1 Initial Load

1. Route opens
2. Workbench loads source context
3. System resolves `baseState`
4. System runs an initial preview
5. Workbench enters `ready`

### 10.2 Chapter-Mapped Flow

1. Operator selects a chapter
2. Workbench maps chapter data into `baseState`
3. `workingState` resets to `baseState`
4. Workbench marks current result stale or auto-runs depending on chosen UX policy
5. Operator optionally edits overrides
6. Operator runs preview

### 10.3 Dirty State

After any override change:

- `uiStatus = dirty`
- existing preview remains visible
- top bar shows an `Inputs Changed` indicator

The page must not auto-submit on every input change in this phase.

### 10.4 Run Preview

On run:

1. copy `currentPreview` to comparison candidate if needed
2. submit `case_id + workingState`
3. on success:
   - update `currentPreview`
   - append history entry
   - clear dirty state
4. on failure:
   - preserve previous successful preview
   - show error state

### 10.5 Compare Last Run

If a previous successful run exists:

- comparison strip becomes active
- hero card shows top action delta
- rule summary shows state changes
- blocked reason panel shows added/removed blockers

### 10.6 Export Snapshot

Export includes:

- source
- selected chapter metadata
- base state
- overrides
- working state
- current preview
- comparison preview id or timestamp when present
- export timestamp

## 11. Data Contracts

### 11.1 Existing Contract Reused

The workbench continues to use:

- `POST /api/v2/recommendation/preview`

with:

- `case_id`
- `state`

### 11.2 Frontend-Only Session Models

Add frontend session types for:

- `WorkbenchRunEntry`
- `WorkbenchComparisonDelta`
- `ChapterMappedContext`

### 11.3 Phase-1 Mapping Adapter

Because the backend does not yet provide a dedicated chapter-mapping API, phase 1 may use a frontend adapter layer that maps chapter or chapter-like context into `NarrativeV2StoryState`.

That adapter must remain isolated and replaceable once a backend `v2` chapter context API exists.

## 12. Error and Empty-State Policy

### 12.1 Error Policy

Errors must not wipe the current successful result.

On preview error:

- preserve current displayed result
- show error banner in top bar or workbench body
- keep workbench interactive for retry

### 12.2 Empty States

Provide explicit empty states for:

- no chapter selected
- no mapped context available
- no previous run to compare
- no history entries yet
- no blocked actions

## 13. Visual Design Rules

### 13.1 Visual Tone

Use a dark decision-cockpit aesthetic rather than a marketing dashboard.

Principles:

- center column is visually dominant
- left and right rails are quieter
- typography emphasizes recommendation first, explanation second, trace third
- status colors remain explicit and functional

### 13.2 Layout Behavior

- desktop: three-column layout
- tablet: stacked rails around central decision area
- mobile: top bar, then decision surface, then context, then validation

### 13.3 Design Language

Retain:

- glass / panel visual continuity
- status pills
- dense analytical cards

Improve:

- stronger workbench framing
- less hero marketing copy
- more route-level task clarity

## 14. Testing and Acceptance Criteria

### 14.1 Frontend Acceptance

The workbench is acceptable when:

- it exists on a dedicated route
- a user can choose a context source
- a user can select or map a chapter context
- a user can edit overrides
- a user can run preview and see all three surfaces update
- a user can compare the current run with the previous run
- a user can inspect blocked reasons and validation record
- a user can export the current snapshot

### 14.2 Engineering Acceptance

The implementation is acceptable when:

- frontend tests cover the dedicated route and core interactions
- the build passes
- existing `v2` backend tests still pass
- the workbench components are split by responsibility

### 14.3 Product Acceptance

The page should feel like a decision cockpit, not a debug card embedded in a dashboard.

## 15. Recommended Implementation Order

1. Add dedicated `V2 Workbench` route and page shell
2. Move current `v2` preview logic behind the new route container
3. Build `ContextRail` and chapter/context source abstraction
4. Build center decision components
5. Build validation rail
6. Add comparison and session run history
7. Add snapshot export
8. Polish responsive layout and visual hierarchy

## 16. Final Recommendation

Proceed with a dedicated `V2 Workbench` route that applies advanced capability support from the first implementation phase.

This is the narrowest way to achieve a product-grade `v2` interaction model while preserving the transparency and calibration value of the current `v2` system.
