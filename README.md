# alpha-autopilot

Python narrative recommendation prototype with a companion React dashboard.

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
- `demo.py` - small runnable example
- `train.py` - training entry point
- `recommend.py` - recommendation entry point
- `ui/index.html` - modern quant-style dashboard mockup
- `ui/styles.css` - visual system for the dashboard
- `ui-react/` - React version of the dashboard with API fallback and preview support

## Running the prototype

- `python train.py` to train the initial matrix and write version/log artifacts
- `python recommend.py` to print chapter recommendation rankings
- `uvicorn backend_app:app --reload` to start the demo API
- Open `ui/index.html` for the static quant-style dashboard mockup
- Use `ui-react/` for the componentized React dashboard prototype

## Notes

This repository focuses on narrative recommendation research. The feature matrix, state推演, preview flow, and training loop are kept explicit so they can be reviewed, adjusted, and expanded without relying on a large database.
