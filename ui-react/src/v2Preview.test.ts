import { describe, expect, it } from 'vitest';
import { DEFAULT_V2_PREVIEW_STATE, buildNarrativeV2PreviewRequest } from './v2Preview';

describe('buildNarrativeV2PreviewRequest', () => {
  it('serializes six-step plot unit scaffold into preview payload', () => {
    const payload = buildNarrativeV2PreviewRequest(DEFAULT_V2_PREVIEW_STATE, {
      plotUnitScaffold: {
        encounter_event: 'The hero receives a public accusation.',
        desire_goal: 'Clear her name before the council.',
        obstacle: 'The rival controls key witness testimony.',
        solution_method: 'Expose the forged evidence chain.',
        action_climax: {
          node: 'The witness flips and names the mastermind.',
          turn_type: 'goal_inversion',
        },
        resolution: 'The council suspends judgment and opens a hidden investigation.',
      },
    });

    expect(payload.plot_unit_scaffold).toEqual({
      encounter_event: 'The hero receives a public accusation.',
      desire_goal: 'Clear her name before the council.',
      obstacle: 'The rival controls key witness testimony.',
      solution_method: 'Expose the forged evidence chain.',
      action_climax: {
        node: 'The witness flips and names the mastermind.',
        turn_type: 'goal_inversion',
      },
      resolution: 'The council suspends judgment and opens a hidden investigation.',
    });
  });
});
