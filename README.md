# alpha-autopilot

Python reimplementation of a traditional Alpha-Beta Chinese chess engine, adapted as a lightweight heuristic core for novel-fusion-autopilot research.

## Goals

- Rebuild the core search/evaluation loop in Python
- Keep the architecture database-free
- Provide a feature-matrix style evaluation that can later be adapted to chapter-planning and scene-scoring for novel generation
- Separate board state, move generation, evaluation, and search so the system remains extensible

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
- `demo.py` - small runnable example
- `train.py` - training entry point
- `recommend.py` - recommendation entry point
- `ui/index.html` - modern quant-style dashboard mockup
- `ui/styles.css` - visual system for the dashboard
- `frontend_PRD.md` - frontend delivery requirements
- `frontend_PROJECT_STATUS.md` - frontend progress report
- `frontend_TECH_BOTTLENECKS.md` - frontend bottleneck log
- `frontend_REVIEW_GUIDE.md` - frontend review guide
- `frontend_DELIVERY_CHECKLIST.md` - frontend delivery checklist

## Notes for novel-fusion-autopilot

This repository is not intended to become a chess product. It is a research prototype for exploring whether a static feature matrix can replace a large database in a recommendation engine.

The analogy is:

- chess piece value -> narrative element importance
- board position table -> chapter/scene context suitability
- mobility/control -> cross-chapter linkage strength
- protection -> consistency / continuity preservation

If the matrix is expressive enough, it can act as a compact prior over chapter recommendation, avoiding dependence on a huge database while still remaining interpretable.

## Running the prototype

- `python train.py` to train the initial matrix and write version/log artifacts
- `python recommend.py` to print chapter recommendation rankings
- Open `ui/index.html` for the quant-style dashboard mockup

## UI direction

The dashboard follows production quant tooling patterns:

- persistent sidebar navigation
- top-level health and version summary
- KPI cards for fast scanning
- panelized workflow sections
- clear state colors and hierarchy
- append-only log and snapshot awareness
- readable recommendation explanations
