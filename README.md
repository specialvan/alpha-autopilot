# alpha-autopilot

Research-oriented小说章节推荐与写作辅助系统。

## Governance

- `v1/v2` are the stable Baseline and should remain收口
- `v3` is the Increment layer for quality, decomposition, QC, and recommendation enhancement
- V1 phase docs are archived in `V1/`
- V2 phase docs are archived in `V2/`
- authoritative Phase-3 scope note: `PHASE3_SCOPE_ALIGNMENT_2026_04_24.md`
- phase-3 closeout report: `V3_PHASE_CLOSEOUT_2026_04_24.md`
- Experimental ideas must stay isolated from the mainline behavior
- Follow `CODEX_DEVELOPMENT_GOVERNANCE.md` and `claude_review_package/README_FOR_CODEX.md` before making changes

## Goals

- Build a database-free recommendation core for narrative planning
- Model story state, feature matrices, candidate generation, versioning, and training logs
- Expose a small API for dashboard and recommendation preview
- Keep the architecture interpretable and easy to iterate

## Contents

- `alpha_autopilot/board.py` - board representation and move model
- `alpha_autopilot/eval.py` - heuristic evaluation with piece value and position tables
- `alpha_autopilot/search.py` - Alpha-Beta search with depth adaptation
- `alpha_autopilot/engine.py` - top-level move selection API
- `alpha_autopilot/narrative.py` - story-state model for chapter recommendation
- `alpha_autopilot/feature_matrix.py` - feature-based scoring and updates
- `alpha_autopilot/planner.py` - candidate generation and ranking
- `alpha_autopilot/trainer.py` - training loop and feedback updates
- `alpha_autopilot/versioning.py` - matrix snapshot version management
- `alpha_autopilot/training_log.py` - append-only training log
- `alpha_autopilot/recommend.py` - engineered recommendation output and preview logic
- `backend_app.py` - FastAPI demo app for dashboard and preview endpoints
- `backend/app/main.py` - main FastAPI app with full API routes (history, v2 workbench, v2 preview, training, feedback)
- `demo.py` - small runnable example
- `train.py` - training entry point
- `recommend.py` - recommendation entry point
- `ui/index.html` - modern quant-style dashboard mockup
- `ui/styles.css` - visual system for the dashboard
- `ui-react/` - React version of the dashboard with API fallback and preview support

## Running the prototype

- `python train.py` to train the initial matrix and write version/log artifacts
- `python recommend.py` to print chapter recommendation rankings
- `uvicorn backend.app.main:app --reload` to start the main API
- `uvicorn backend_app:app --reload` to start the demo-only API
- Open `ui/index.html` for the static quant-style dashboard mockup
- Use `ui-react/` for the componentized React dashboard prototype

## Notes

This repository focuses on narrative recommendation research. The feature matrix, state推演, preview flow, and training loop are kept explicit so they can be reviewed, adjusted, and expanded without relying on a large database.

For development execution, treat `Dashboard` as the Baseline display layer and `V2 Workbench` as the Increment decision layer.

API contract reference:

- `docs/api/v2-workbench-real-chapter-context-contract.md`
