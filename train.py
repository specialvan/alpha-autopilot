from __future__ import annotations

import json
from pathlib import Path

from alpha_autopilot import StoryState, Trainer, TrainingSample
from alpha_autopilot.training_log import TrainingLogger
from alpha_autopilot.versioning import VersionManager


ROOT = Path(__file__).resolve().parent
SAMPLES_PATH = ROOT / "samples.json"


def load_samples() -> list[TrainingSample]:
    raw = json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))
    samples: list[TrainingSample] = []
    for item in raw:
        state = StoryState(
            chapter_index=item["chapter_index"],
            stage=item["stage"],
            mainline_progress=item["mainline_progress"],
            sideplot_progress=item["sideplot_progress"],
            conflict_intensity=item["conflict_intensity"],
            emotional_temperature=item["emotional_temperature"],
            pacing_speed=item["pacing_speed"],
            foreshadowing_load=item["foreshadowing_load"],
            payoff_pressure=item["payoff_pressure"],
            tags=item.get("tags", []),
        )
        samples.append(
            TrainingSample(
                state=state,
                target_action=item["target_action"],
                target_score=item["target_score"],
                feedback=item["feedback"],
            )
        )
    return samples


def main() -> None:
    trainer = Trainer()
    logger = TrainingLogger(ROOT)
    versioner = VersionManager(ROOT)
    samples = load_samples()
    matrix = trainer.fit(samples)
    snapshot = versioner.create_version(matrix.weights, matrix.bias, len(samples), notes="initial narrative training")

    for entry in trainer.history:
        logger.record(
            stage="fit",
            action=entry["action"],
            predicted=entry["predicted"],
            target=entry["target"],
            feedback=entry.get("feedback", 0.0),
            notes=snapshot.version,
        )

    print("trained_weights=")
    for key, value in sorted(matrix.weights.items()):
        print(f"  {key}: {value:.4f}")
    print(f"bias={matrix.bias:.4f}")
    print(f"history_len={len(trainer.history)}")
    print(f"summary={trainer.summary()}")
    print(f"version={snapshot.version}")


if __name__ == "__main__":
    main()
