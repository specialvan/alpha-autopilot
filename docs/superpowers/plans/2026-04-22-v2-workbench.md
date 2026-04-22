# V2 Workbench Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a dedicated `V2 Workbench` route that turns the current embedded `v2` preview panel into a chapter-oriented decision cockpit with comparison, run history, and snapshot export.

**Architecture:** The implementation keeps the existing dashboard alive on `/` and adds a dedicated `/v2/workbench` route using `react-router-dom`. The new route is driven by a focused controller hook plus small workbench-specific components, while chapter-mapped contexts, run history, comparison deltas, and export payloads live in isolated frontend-only helper modules that can later be swapped for backend APIs.

**Tech Stack:** React 19, TypeScript, Vite, Vitest, Testing Library, `react-router-dom`

---

## File Map

- Modify: `D:\workspace\alpha-autopilot\ui-react\package.json`
  Add `react-router-dom` and keep test/build scripts intact.
- Modify: `D:\workspace\alpha-autopilot\ui-react\src\main.tsx`
  Mount the app through the router shell.
- Create: `D:\workspace\alpha-autopilot\ui-react\src\router\AppRouter.tsx`
  Define `/` and `/v2/workbench` routes and export testable route components.
- Create: `D:\workspace\alpha-autopilot\ui-react\src\router\AppRouter.test.tsx`
  Route smoke tests for dashboard and workbench pages.
- Create: `D:\workspace\alpha-autopilot\ui-react\src\pages\V2WorkbenchPage.tsx`
  Dedicated route container for the workbench.
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\types.ts`
  Route-local types for mapped contexts, run history, diffs, and export payloads.
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\chapterContexts.ts`
  Seeded chapter-mapped contexts for phase 1.
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\contextMapping.ts`
  Base-state resolution and state diff helpers.
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\session.ts`
  Run entry, comparison delta, and snapshot export helpers.
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\contextMapping.test.ts`
  Pure tests for chapter mapping and diff helpers.
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\session.test.ts`
  Pure tests for run history and export helpers.
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\useV2WorkbenchController.ts`
  Page-level state orchestration.
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\components\WorkbenchTopBar.tsx`
  Top bar with run/compare/export actions.
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\components\ContextRail.tsx`
  Source selection, chapter picker, context summary, and overrides.
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\components\DecisionSurface.tsx`
  Hero card, candidate ranking, and score breakdown.
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\components\ValidationRail.tsx`
  Rule summary, blocker aggregation, validation record, and run history.
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\components\RunHistoryPanel.tsx`
  Selectable session run history list.
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\workbench.css`
  Route-specific layout and cockpit styling.
- Create: `D:\workspace\alpha-autopilot\ui-react\src\pages\V2WorkbenchPage.test.tsx`
  Interaction tests for the workbench page.
- Modify: `D:\workspace\alpha-autopilot\ui-react\src\App.tsx`
  Keep the dashboard on `/`, remove the embedded `V2PreviewLab`, and expose a launch path to the workbench.
- Modify: `D:\workspace\alpha-autopilot\ui-react\src\components\Hero.tsx`
  Replace dead CTA buttons with workbench entry actions.
- Modify: `D:\workspace\alpha-autopilot\ui-react\src\components\Sidebar.tsx`
  Add a stable workbench navigation link.
- Modify: `D:\workspace\alpha-autopilot\ui-react\src\styles.css`
  Add link/button styling that works for route navigation and dashboard cleanup.
- Delete: `D:\workspace\alpha-autopilot\ui-react\src\App.v2-preview.test.tsx`
  Replace the embedded-preview test with route-level and page-level workbench coverage.

### Task 1: Add the Dedicated Route Shell

**Files:**
- Modify: `D:\workspace\alpha-autopilot\ui-react\package.json`
- Modify: `D:\workspace\alpha-autopilot\ui-react\src\main.tsx`
- Create: `D:\workspace\alpha-autopilot\ui-react\src\router\AppRouter.tsx`
- Create: `D:\workspace\alpha-autopilot\ui-react\src\router\AppRouter.test.tsx`
- Create: `D:\workspace\alpha-autopilot\ui-react\src\pages\V2WorkbenchPage.tsx`
- Test: `D:\workspace\alpha-autopilot\ui-react\src\router\AppRouter.test.tsx`

- [ ] **Step 1: Add the router dependency**

Run:

```bash
npm install react-router-dom
```

Expected:

```text
Install completes without errors and `react-router-dom` is added to `package.json`.
```

- [ ] **Step 2: Write the failing route smoke test**

```tsx
// D:/workspace/alpha-autopilot/ui-react/src/router/AppRouter.test.tsx
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { AppRoutes } from './AppRouter';

describe('AppRoutes', () => {
  it('renders the dashboard on the root route', async () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <AppRoutes />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /量化推荐工作台/i })).toBeInTheDocument();
  });

  it('renders the dedicated workbench route', async () => {
    render(
      <MemoryRouter initialEntries={['/v2/workbench']}>
        <AppRoutes />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: 'V2 Workbench' })).toBeInTheDocument();
  });
});
```

- [ ] **Step 3: Run the test to verify it fails**

Run:

```bash
npm test -- src/router/AppRouter.test.tsx
```

Expected:

```text
FAIL src/router/AppRouter.test.tsx
Cannot find module './AppRouter'
```

- [ ] **Step 4: Write the minimal route shell**

```tsx
// D:/workspace/alpha-autopilot/ui-react/src/router/AppRouter.tsx
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { App as DashboardPage } from '../App';
import { V2WorkbenchPage } from '../pages/V2WorkbenchPage';

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/v2/workbench" element={<V2WorkbenchPage />} />
    </Routes>
  );
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}

// D:/workspace/alpha-autopilot/ui-react/src/pages/V2WorkbenchPage.tsx
export function V2WorkbenchPage() {
  return (
    <main className="main">
      <section className="panel glass" id="v2-workbench-route">
        <p className="label">Decision Cockpit</p>
        <h1>V2 Workbench</h1>
        <p className="muted">Route shell for the dedicated v2 workspace.</p>
      </section>
    </main>
  );
}

// D:/workspace/alpha-autopilot/ui-react/src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { AppRouter } from './router/AppRouter';
import './styles.css';

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <AppRouter />
  </React.StrictMode>,
);
```

- [ ] **Step 5: Run the route test to verify it passes**

Run:

```bash
npm test -- src/router/AppRouter.test.tsx
```

Expected:

```text
Test Files  1 passed
Tests       2 passed
```

- [ ] **Step 6: Commit**

```bash
git add D:/workspace/alpha-autopilot/ui-react/package.json D:/workspace/alpha-autopilot/ui-react/package-lock.json D:/workspace/alpha-autopilot/ui-react/src/main.tsx D:/workspace/alpha-autopilot/ui-react/src/router/AppRouter.tsx D:/workspace/alpha-autopilot/ui-react/src/router/AppRouter.test.tsx D:/workspace/alpha-autopilot/ui-react/src/pages/V2WorkbenchPage.tsx
git commit -m "feat: add v2 workbench route shell"
```

### Task 2: Add Context Mapping and Session Models

**Files:**
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\types.ts`
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\chapterContexts.ts`
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\contextMapping.ts`
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\session.ts`
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\contextMapping.test.ts`
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\session.test.ts`
- Test: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\contextMapping.test.ts`
- Test: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\session.test.ts`

- [ ] **Step 1: Write failing pure tests for mapping, diffs, history, and export**

```ts
// D:/workspace/alpha-autopilot/ui-react/src/features/v2Workbench/contextMapping.test.ts
import { describe, expect, it } from 'vitest';
import { listChapterMappedContexts, resolveBaseState, computeStateDiff } from './contextMapping';

describe('contextMapping', () => {
  it('resolves a mapped chapter into a story state', () => {
    const chapter = listChapterMappedContexts()[0];
    const state = resolveBaseState('mapped_chapter', chapter.id);

    expect(state.chapter_index).toBe(chapter.chapterNumber);
    expect(state.stage).toBe(chapter.stage);
  });

  it('returns only changed fields in the state diff', () => {
    const chapter = listChapterMappedContexts()[0];
    const working = { ...chapter.state, payoff_pressure: 0.48 };

    expect(computeStateDiff(chapter.state, working)).toEqual([
      { field: 'payoff_pressure', previous: 0.32, current: 0.48 },
    ]);
  });
});

// D:/workspace/alpha-autopilot/ui-react/src/features/v2Workbench/session.test.ts
import { describe, expect, it } from 'vitest';
import { appendRunEntry, buildComparisonDelta, buildSnapshotPayload } from './session';

describe('session helpers', () => {
  it('appends a run entry and computes deltas', () => {
    const previous = appendRunEntry([], {
      source: 'demo',
      label: 'demo-middle',
      submittedState: { chapter_index: 8, stage: 'middle', mainline_progress: 0.45, sideplot_progress: 0.22, conflict_intensity: 0.64, emotional_temperature: 0.58, pacing_speed: 0.5, foreshadowing_load: 0.38, payoff_pressure: 0.32, characters: {}, tags: ['power'] },
      preview: { case_id: 'demo-middle', state: { chapter_index: 8, stage: 'middle', mainline_progress: 0.45, sideplot_progress: 0.22, conflict_intensity: 0.64, emotional_temperature: 0.58, pacing_speed: 0.5, foreshadowing_load: 0.38, payoff_pressure: 0.32, characters: {}, tags: ['power'] }, rule_checks: [], recommendations: [], evaluation_summary: { count: 1, top_action: 'push_conflict', top_score: 0.81 }, validation: { case_id: 'demo-middle', accepted_actions: ['push_conflict'], blocked_actions: ['deliver_payoff'], top_action: 'push_conflict', notes: 'demo' } },
    })[0];

    const current = appendRunEntry([previous], {
      source: 'demo',
      label: 'demo-middle',
      submittedState: previous.submittedState,
      preview: { ...previous.preview, evaluation_summary: { count: 1, top_action: 'reveal_clue', top_score: 0.77 }, validation: { ...previous.preview.validation, top_action: 'reveal_clue', blocked_actions: [] } },
    })[1];

    expect(buildComparisonDelta(previous.preview, current.preview).topActionChanged).toBe(true);
    expect(buildSnapshotPayload({ source: 'demo', selectedChapter: null, baseState: previous.submittedState, overrides: {}, workingState: current.submittedState, currentPreview: current.preview, comparisonPreview: previous.preview }).currentPreview.validation.top_action).toBe('reveal_clue');
  });
});
```

- [ ] **Step 2: Run the pure tests to verify they fail**

Run:

```bash
npm test -- src/features/v2Workbench/contextMapping.test.ts src/features/v2Workbench/session.test.ts
```

Expected:

```text
FAIL src/features/v2Workbench/contextMapping.test.ts
Cannot find module './contextMapping'
FAIL src/features/v2Workbench/session.test.ts
Cannot find module './session'
```

- [ ] **Step 3: Write the minimal mapping and session modules**

```ts
// D:/workspace/alpha-autopilot/ui-react/src/features/v2Workbench/types.ts
import type { NarrativeV2PreviewResponse, NarrativeV2StoryState } from '../../api';

export type V2ContextSource = 'demo' | 'mapped_chapter' | 'manual_override';

export type ChapterMappedContext = {
  id: string;
  chapterNumber: number;
  title: string;
  stage: NarrativeV2StoryState['stage'];
  summary: string;
  state: NarrativeV2StoryState;
};

export type StateDiffEntry = {
  field: keyof NarrativeV2StoryState;
  previous: number | string;
  current: number | string;
};

export type WorkbenchRunEntry = {
  id: string;
  timestamp: string;
  source: V2ContextSource;
  label: string;
  submittedState: NarrativeV2StoryState;
  preview: NarrativeV2PreviewResponse;
};

// D:/workspace/alpha-autopilot/ui-react/src/features/v2Workbench/chapterContexts.ts
import type { ChapterMappedContext } from './types';

export const CHAPTER_MAPPED_CONTEXTS: ChapterMappedContext[] = [
  {
    id: 'chapter-08',
    chapterNumber: 8,
    title: 'Pressure Rises in the Midpoint',
    stage: 'middle',
    summary: 'Mainline pressure climbs while payoff remains immature.',
    state: { chapter_index: 8, stage: 'middle', mainline_progress: 0.45, sideplot_progress: 0.22, conflict_intensity: 0.64, emotional_temperature: 0.58, pacing_speed: 0.5, foreshadowing_load: 0.38, payoff_pressure: 0.32, characters: {}, tags: ['power'] },
  },
  {
    id: 'chapter-19',
    chapterNumber: 19,
    title: 'Foreshadow Threads Start Converging',
    stage: 'mid_late',
    summary: 'Setups are mature enough for stronger clue and payoff decisions.',
    state: { chapter_index: 19, stage: 'mid_late', mainline_progress: 0.7, sideplot_progress: 0.43, conflict_intensity: 0.69, emotional_temperature: 0.61, pacing_speed: 0.53, foreshadowing_load: 0.56, payoff_pressure: 0.62, characters: {}, tags: ['payoff'] },
  },
];

// D:/workspace/alpha-autopilot/ui-react/src/features/v2Workbench/contextMapping.ts
import type { NarrativeV2StoryState } from '../../api';
import { DEFAULT_V2_PREVIEW_STATE } from '../../v2Preview';
import { CHAPTER_MAPPED_CONTEXTS } from './chapterContexts';
import type { StateDiffEntry, V2ContextSource } from './types';

export function listChapterMappedContexts() {
  return CHAPTER_MAPPED_CONTEXTS;
}

export function resolveBaseState(source: V2ContextSource, chapterId?: string): NarrativeV2StoryState {
  if (source === 'mapped_chapter') {
    const context = CHAPTER_MAPPED_CONTEXTS.find((item) => item.id === chapterId) ?? CHAPTER_MAPPED_CONTEXTS[0];
    return context.state;
  }
  return DEFAULT_V2_PREVIEW_STATE;
}

export function computeStateDiff(baseState: NarrativeV2StoryState, workingState: NarrativeV2StoryState): StateDiffEntry[] {
  return (Object.keys(baseState) as Array<keyof NarrativeV2StoryState>)
    .filter((field) => ['characters', 'tags'].indexOf(String(field)) === -1)
    .filter((field) => baseState[field] !== workingState[field])
    .map((field) => ({
      field,
      previous: baseState[field] as number | string,
      current: workingState[field] as number | string,
    }));
}

// D:/workspace/alpha-autopilot/ui-react/src/features/v2Workbench/session.ts
import type { NarrativeV2PreviewResponse, NarrativeV2StoryState } from '../../api';
import type { V2ContextSource, WorkbenchRunEntry } from './types';

export function appendRunEntry(
  history: WorkbenchRunEntry[],
  input: { source: V2ContextSource; label: string; submittedState: NarrativeV2StoryState; preview: NarrativeV2PreviewResponse },
) {
  return history.concat({
    id: `${Date.now()}-${history.length + 1}`,
    timestamp: new Date().toISOString(),
    source: input.source,
    label: input.label,
    submittedState: input.submittedState,
    preview: input.preview,
  });
}

export function buildComparisonDelta(previous: NarrativeV2PreviewResponse, current: NarrativeV2PreviewResponse) {
  const previousBlockers = new Set(previous.validation.blocked_actions);
  const currentBlockers = new Set(current.validation.blocked_actions);
  return {
    topActionChanged: previous.evaluation_summary.top_action !== current.evaluation_summary.top_action,
    previousTopAction: previous.evaluation_summary.top_action,
    currentTopAction: current.evaluation_summary.top_action,
    topScoreDelta: Number((current.evaluation_summary.top_score - previous.evaluation_summary.top_score).toFixed(4)),
    addedBlockers: [...currentBlockers].filter((item) => !previousBlockers.has(item)),
    removedBlockers: [...previousBlockers].filter((item) => !currentBlockers.has(item)),
  };
}

export function buildSnapshotPayload(input: {
  source: V2ContextSource;
  selectedChapter: string | null;
  baseState: NarrativeV2StoryState;
  overrides: Partial<NarrativeV2StoryState>;
  workingState: NarrativeV2StoryState;
  currentPreview: NarrativeV2PreviewResponse;
  comparisonPreview: NarrativeV2PreviewResponse | null;
}) {
  return {
    exportedAt: new Date().toISOString(),
    source: input.source,
    selectedChapter: input.selectedChapter,
    baseState: input.baseState,
    overrides: input.overrides,
    workingState: input.workingState,
    currentPreview: input.currentPreview,
    comparisonPreview: input.comparisonPreview,
  };
}
```

- [ ] **Step 4: Run the pure tests to verify they pass**

Run:

```bash
npm test -- src/features/v2Workbench/contextMapping.test.ts src/features/v2Workbench/session.test.ts
```

Expected:

```text
Test Files  2 passed
Tests       3 passed
```

- [ ] **Step 5: Commit**

```bash
git add D:/workspace/alpha-autopilot/ui-react/src/features/v2Workbench/types.ts D:/workspace/alpha-autopilot/ui-react/src/features/v2Workbench/chapterContexts.ts D:/workspace/alpha-autopilot/ui-react/src/features/v2Workbench/contextMapping.ts D:/workspace/alpha-autopilot/ui-react/src/features/v2Workbench/session.ts D:/workspace/alpha-autopilot/ui-react/src/features/v2Workbench/contextMapping.test.ts D:/workspace/alpha-autopilot/ui-react/src/features/v2Workbench/session.test.ts
git commit -m "feat: add v2 workbench state and mapping models"
```

### Task 3: Build the Workbench Cockpit

**Files:**
- Modify: `D:\workspace\alpha-autopilot\ui-react\src\pages\V2WorkbenchPage.tsx`
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\useV2WorkbenchController.ts`
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\components\WorkbenchTopBar.tsx`
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\components\ContextRail.tsx`
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\components\DecisionSurface.tsx`
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\components\ValidationRail.tsx`
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\components\RunHistoryPanel.tsx`
- Create: `D:\workspace\alpha-autopilot\ui-react\src\features\v2Workbench\workbench.css`
- Create: `D:\workspace\alpha-autopilot\ui-react\src\pages\V2WorkbenchPage.test.tsx`
- Test: `D:\workspace\alpha-autopilot\ui-react\src\pages\V2WorkbenchPage.test.tsx`

- [ ] **Step 1: Write the failing page interaction test**

```tsx
// D:/workspace/alpha-autopilot/ui-react/src/pages/V2WorkbenchPage.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { V2WorkbenchPage } from './V2WorkbenchPage';

const fetchRecommendationPreviewV2 = vi.fn();

vi.mock('../api', async () => {
  const actual = await vi.importActual<typeof import('../api')>('../api');
  return { ...actual, fetchRecommendationPreviewV2 };
});

describe('V2WorkbenchPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    fetchRecommendationPreviewV2.mockResolvedValue({
      case_id: 'chapter-08',
      state: { chapter_index: 8, stage: 'middle', mainline_progress: 0.45, sideplot_progress: 0.22, conflict_intensity: 0.64, emotional_temperature: 0.58, pacing_speed: 0.5, foreshadowing_load: 0.38, payoff_pressure: 0.32, characters: {}, tags: ['power'] },
      rule_checks: [{ action: 'push_conflict', status: 'legal', prerequisites: ['mainline_progress>=0.20'], blockers: [], risk_flags: [] }],
      recommendations: [{ action: { action: 'push_conflict', delta: { conflict_intensity: 0.16 }, explanation: 'Raise direct confrontation.' }, rule_check: { action: 'push_conflict', status: 'legal', prerequisites: ['mainline_progress>=0.20'], blockers: [], risk_flags: [] }, score: 0.8123, details: { structure_value: 0.82, continuity_safety: 0.71, emotional_payoff: 0.67, foreshadow_balance: 0.62, stage_fit: 1, feasibility: 1 } }],
      evaluation_summary: { count: 1, top_action: 'push_conflict', top_score: 0.8123 },
      validation: { case_id: 'chapter-08', accepted_actions: ['push_conflict'], blocked_actions: ['deliver_payoff'], top_action: 'push_conflict', notes: 'mapped chapter run' },
    });
  });

  it('renders the workbench rails and runs preview against chapter context', async () => {
    const user = userEvent.setup();
    render(<V2WorkbenchPage />);

    expect(await screen.findByRole('heading', { name: 'V2 Workbench' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Decision Surface' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Validation Rail' })).toBeInTheDocument();

    await user.selectOptions(screen.getByLabelText('Chapter Context'), 'chapter-19');
    await user.click(screen.getByRole('button', { name: 'Run Preview' }));

    await waitFor(() =>
      expect(fetchRecommendationPreviewV2).toHaveBeenLastCalledWith(
        expect.objectContaining({ case_id: 'demo-v2-mid_late-19' }),
      ),
    );
  });
});
```

- [ ] **Step 2: Run the page test to verify it fails**

Run:

```bash
npm test -- src/pages/V2WorkbenchPage.test.tsx
```

Expected:

```text
FAIL src/pages/V2WorkbenchPage.test.tsx
Unable to find role "heading" with name "Decision Surface"
```

- [ ] **Step 3: Implement the controller and workbench components**

```tsx
// D:/workspace/alpha-autopilot/ui-react/src/features/v2Workbench/useV2WorkbenchController.ts
import { useEffect, useMemo, useState } from 'react';
import { fetchRecommendationPreviewV2, type NarrativeV2PreviewResponse, type NarrativeV2StoryState } from '../../api';
import { buildNarrativeV2PreviewRequest, clampNarrativeV2Value } from '../../v2Preview';
import { listChapterMappedContexts, resolveBaseState, computeStateDiff } from './contextMapping';
import { appendRunEntry, buildComparisonDelta, buildSnapshotPayload } from './session';
import type { V2ContextSource, WorkbenchRunEntry } from './types';

export function useV2WorkbenchController() {
  const contexts = listChapterMappedContexts();
  const [contextSource, setContextSource] = useState<V2ContextSource>('mapped_chapter');
  const [selectedChapter, setSelectedChapter] = useState<string>(contexts[0].id);
  const [overrides, setOverrides] = useState<Partial<NarrativeV2StoryState>>({});
  const [currentPreview, setCurrentPreview] = useState<NarrativeV2PreviewResponse | null>(null);
  const [comparisonPreview, setComparisonPreview] = useState<NarrativeV2PreviewResponse | null>(null);
  const [runHistory, setRunHistory] = useState<WorkbenchRunEntry[]>([]);
  const [uiStatus, setUiStatus] = useState<'loading_context' | 'ready' | 'dirty' | 'running' | 'error'>('loading_context');
  const [error, setError] = useState<string | null>(null);

  const baseState = useMemo(() => resolveBaseState(contextSource, selectedChapter), [contextSource, selectedChapter]);
  const workingState = useMemo(() => ({ ...baseState, ...overrides }), [baseState, overrides]);
  const stateDiff = useMemo(() => computeStateDiff(baseState, workingState), [baseState, workingState]);
  const comparisonDelta = useMemo(() => (currentPreview && comparisonPreview ? buildComparisonDelta(comparisonPreview, currentPreview) : null), [comparisonPreview, currentPreview]);

  const runPreview = async () => {
    setUiStatus('running');
    try {
      const preview = await fetchRecommendationPreviewV2(buildNarrativeV2PreviewRequest(workingState));
      setComparisonPreview(currentPreview);
      setCurrentPreview(preview);
      setRunHistory((history) => appendRunEntry(history, { source: contextSource, label: selectedChapter, submittedState: workingState, preview }));
      setError(null);
      setUiStatus('ready');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'v2 preview failed');
      setUiStatus('error');
    }
  };

  useEffect(() => {
    void runPreview();
  }, [contextSource, selectedChapter]);

  return {
    contexts,
    contextSource,
    selectedChapter,
    baseState,
    workingState,
    stateDiff,
    currentPreview,
    comparisonPreview,
    comparisonDelta,
    runHistory,
    uiStatus,
    error,
    setContextSource,
    setSelectedChapter,
    setNumericOverride: (field: keyof NarrativeV2StoryState, value: number) => {
      setOverrides((current) => ({ ...current, [field]: clampNarrativeV2Value(value) }));
      setUiStatus('dirty');
    },
    runPreview,
    selectComparisonRun: (id: string) => {
      const selected = runHistory.find((entry) => entry.id === id);
      setComparisonPreview(selected?.preview ?? null);
    },
    exportSnapshot: () => (currentPreview ? buildSnapshotPayload({ source: contextSource, selectedChapter, baseState, overrides, workingState, currentPreview, comparisonPreview }) : null),
  };
}

// D:/workspace/alpha-autopilot/ui-react/src/pages/V2WorkbenchPage.tsx
import '../features/v2Workbench/workbench.css';
import { ContextRail } from '../features/v2Workbench/components/ContextRail';
import { DecisionSurface } from '../features/v2Workbench/components/DecisionSurface';
import { ValidationRail } from '../features/v2Workbench/components/ValidationRail';
import { WorkbenchTopBar } from '../features/v2Workbench/components/WorkbenchTopBar';
import { useV2WorkbenchController } from '../features/v2Workbench/useV2WorkbenchController';

export function V2WorkbenchPage() {
  const controller = useV2WorkbenchController();

  return (
    <main className="v2-workbench-shell">
      <WorkbenchTopBar controller={controller} />
      <section className="v2-workbench-grid">
        <ContextRail controller={controller} />
        <DecisionSurface controller={controller} />
        <ValidationRail controller={controller} />
      </section>
    </main>
  );
}
```

- [ ] **Step 4: Run the page test to verify it passes**

Run:

```bash
npm test -- src/pages/V2WorkbenchPage.test.tsx
```

Expected:

```text
Test Files  1 passed
Tests       1 passed
```

- [ ] **Step 5: Commit**

```bash
git add D:/workspace/alpha-autopilot/ui-react/src/pages/V2WorkbenchPage.tsx D:/workspace/alpha-autopilot/ui-react/src/pages/V2WorkbenchPage.test.tsx D:/workspace/alpha-autopilot/ui-react/src/features/v2Workbench/useV2WorkbenchController.ts D:/workspace/alpha-autopilot/ui-react/src/features/v2Workbench/components/WorkbenchTopBar.tsx D:/workspace/alpha-autopilot/ui-react/src/features/v2Workbench/components/ContextRail.tsx D:/workspace/alpha-autopilot/ui-react/src/features/v2Workbench/components/DecisionSurface.tsx D:/workspace/alpha-autopilot/ui-react/src/features/v2Workbench/components/ValidationRail.tsx D:/workspace/alpha-autopilot/ui-react/src/features/v2Workbench/components/RunHistoryPanel.tsx D:/workspace/alpha-autopilot/ui-react/src/features/v2Workbench/workbench.css
git commit -m "feat: build v2 workbench cockpit"
```

### Task 4: Remove the Embedded Lab and Finalize the Product Flow

**Files:**
- Modify: `D:\workspace\alpha-autopilot\ui-react\src\App.tsx`
- Modify: `D:\workspace\alpha-autopilot\ui-react\src\components\Hero.tsx`
- Modify: `D:\workspace\alpha-autopilot\ui-react\src\components\Sidebar.tsx`
- Modify: `D:\workspace\alpha-autopilot\ui-react\src\styles.css`
- Modify: `D:\workspace\alpha-autopilot\ui-react\src\router\AppRouter.test.tsx`
- Delete: `D:\workspace\alpha-autopilot\ui-react\src\App.v2-preview.test.tsx`
- Test: `D:\workspace\alpha-autopilot\ui-react\src\router\AppRouter.test.tsx`
- Test: `D:\workspace\alpha-autopilot\ui-react\src\pages\V2WorkbenchPage.test.tsx`

- [ ] **Step 1: Extend the route smoke test with dashboard cleanup expectations**

```tsx
// D:/workspace/alpha-autopilot/ui-react/src/router/AppRouter.test.tsx
it('links the dashboard to the dedicated workbench and no longer renders the embedded lab', async () => {
  render(
    <MemoryRouter initialEntries={['/']}>
      <AppRoutes />
    </MemoryRouter>,
  );

  expect(await screen.findByRole('link', { name: 'Open V2 Workbench' })).toHaveAttribute('href', '/v2/workbench');
  expect(screen.queryByRole('heading', { name: 'V2 Preview Lab' })).not.toBeInTheDocument();
});
```

- [ ] **Step 2: Run the route test to verify it fails**

Run:

```bash
npm test -- src/router/AppRouter.test.tsx
```

Expected:

```text
FAIL src/router/AppRouter.test.tsx
Unable to find role "link" with name "Open V2 Workbench"
```

- [ ] **Step 3: Remove the embedded lab and expose the dedicated entry**

```tsx
// D:/workspace/alpha-autopilot/ui-react/src/components/Hero.tsx
import { Link } from 'react-router-dom';

export function Hero() {
  return (
    <header className="hero glass" id="overview">
      <div>
        <p className="eyebrow">Decision cockpit for narrative action calibration</p>
        <h2>面向小说章节规划的量化推荐工作台</h2>
        <p className="lede">Keep the v1 dashboard for overview and launch the dedicated v2 cockpit for transparent chapter-level decisions.</p>
      </div>
      <div className="hero-actions">
        <Link className="primary hero-link" to="/v2/workbench">Open V2 Workbench</Link>
        <button className="secondary" type="button">导入拆解样本</button>
      </div>
    </header>
  );
}

// D:/workspace/alpha-autopilot/ui-react/src/components/Sidebar.tsx
import { Link } from 'react-router-dom';
// Keep the existing brand header and overview cards unchanged.
        <a href="#recommendations" className="nav-item">推荐结果</a>
        <Link to="/v2/workbench" className="nav-item">V2 Workbench</Link>
        <a href="#feedback" className="nav-item">反馈闭环</a>
        <a href="#logs" className="nav-item">训练日志</a>

// D:/workspace/alpha-autopilot/ui-react/src/App.tsx
// Remove:
// - V2PreviewLab import
// - v2PreviewState/currentPreview/comparison state
// - fetchRecommendationPreviewV2 bootstrapping effect
// - the `<V2PreviewLab />` element block
```

- [ ] **Step 4: Run the final verification set**

Run:

```bash
npm test
npm run build
pytest tests -q -k "v2"
```

Expected:

```text
Vitest exits 0 with all tests passing.
Vite build exits 0 and prints the generated `dist/` asset summary.
Pytest reports `12 passed`.
```

- [ ] **Step 5: Commit**

```bash
git add D:/workspace/alpha-autopilot/ui-react/src/App.tsx D:/workspace/alpha-autopilot/ui-react/src/components/Hero.tsx D:/workspace/alpha-autopilot/ui-react/src/components/Sidebar.tsx D:/workspace/alpha-autopilot/ui-react/src/styles.css D:/workspace/alpha-autopilot/ui-react/src/router/AppRouter.test.tsx D:/workspace/alpha-autopilot/ui-react/src/pages/V2WorkbenchPage.test.tsx
git rm D:/workspace/alpha-autopilot/ui-react/src/App.v2-preview.test.tsx
git commit -m "feat: promote v2 workbench over embedded preview lab"
```

## Self-Review

- Spec coverage:
  - dedicated route: Task 1
  - chapter-mapped context: Task 2 + Task 3
  - comparison and run history: Task 2 + Task 3
  - export snapshot: Task 2 + Task 3
  - dashboard cleanup: Task 4
- Placeholder scan:
  - No `TBD`, `TODO`, or “similar to previous task” markers remain.
- Type consistency:
  - `V2ContextSource`, `ChapterMappedContext`, `WorkbenchRunEntry`, and `NarrativeV2StoryState` are introduced before they are consumed by the controller and page.
