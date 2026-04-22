import '../features/v2Workbench/workbench.css';
import { ContextRail } from '../features/v2Workbench/components/ContextRail';
import { DecisionSurface } from '../features/v2Workbench/components/DecisionSurface';
import { ValidationRail } from '../features/v2Workbench/components/ValidationRail';
import { WorkbenchTopBar } from '../features/v2Workbench/components/WorkbenchTopBar';
import { useV2WorkbenchController } from '../features/v2Workbench/useV2WorkbenchController';

export function V2WorkbenchPage() {
  const controller = useV2WorkbenchController();

  return (
    <main className="v2-workbench-shell" id="v2-workbench-route">
      <WorkbenchTopBar controller={controller} />
      <section className="v2-workbench-grid">
        <ContextRail controller={controller} />
        <DecisionSurface controller={controller} />
        <ValidationRail controller={controller} />
      </section>
    </main>
  );
}
