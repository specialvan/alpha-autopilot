from alpha_autopilot.feature_matrix import FeatureMatrix
from alpha_autopilot.narrative import StoryState
from alpha_autopilot.trainer import TrainingExample, Trainer


def build_samples() -> list[TrainingExample]:
    opening = StoryState(chapter_index=1, stage="opening", conflict_intensity=0.35, emotional_temperature=0.40, pacing_speed=0.70)
    midgame = StoryState(chapter_index=18, stage="midgame", conflict_intensity=0.65, emotional_temperature=0.55, pacing_speed=0.50)
    peak = StoryState(chapter_index=42, stage="climax", conflict_intensity=0.85, emotional_temperature=0.82, pacing_speed=0.62)
    return [
        TrainingExample(state=opening, target_action="plant_foreshadow", quality=0.74),
        TrainingExample(state=midgame, target_action="push_conflict", quality=0.83),
        TrainingExample(state=peak, target_action="deliver_payoff", quality=0.91),
    ]


def main() -> None:
    matrix = FeatureMatrix()
    trainer = Trainer(matrix)
    report = trainer.train(build_samples(), epochs=12, lr=0.06)
    state = StoryState(chapter_index=12, stage="midgame", conflict_intensity=0.68, emotional_temperature=0.52, pacing_speed=0.48, payoff_pressure=0.35)
    recommendations = trainer.planner.recommend(state)
    print("training_report", report)
    print("top_recommendations")
    for item in recommendations[:3]:
        print(item.candidate.action, round(item.score, 4), item.candidate.explanation)


if __name__ == "__main__":
    main()
