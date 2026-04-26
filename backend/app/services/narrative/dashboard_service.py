from __future__ import annotations

from alpha_autopilot import FeatureMatrix, recommend_chapter

from ..narrative_v4.alert_channel import route_v4_observability_alerts
from ..narrative_v4.observability import build_v4_observability_snapshot
from .schemas import DashboardResponse
from .state_builder import base_state


def build_dashboard() -> DashboardResponse:
    state = base_state()
    recommendations = recommend_chapter(state, FeatureMatrix())
    v4_observability = build_v4_observability_snapshot()
    v4_observability["alertRouting"] = route_v4_observability_alerts(v4_observability)
    return DashboardResponse(
        overview={
            "matrixVersion": "v003",
            "healthValue": 82,
            "sampleCount": 19,
            "versionCount": 3,
            "hitRate": "76%",
            "riskScore": 34,
        },
        narrativeSignals=[
            {"label": "Mainline Progress", "value": 61},
            {"label": "Conflict Intensity", "value": 64},
            {"label": "Foreshadow Load", "value": 36},
            {"label": "Payoff Pressure", "value": 31},
        ],
        matrixWeights=[
            {"label": "Conflict Momentum", "value": "1.32"},
            {"label": "Emotion Payoff", "value": "1.18"},
            {"label": "Hook Strength", "value": "1.09"},
            {"label": "Continuity Safety", "value": "1.24"},
            {"label": "Character Focus", "value": "0.96"},
            {"label": "Foreshadow Value", "value": "1.12"},
            {"label": "Pacing Fit", "value": "1.04"},
        ],
        chapterSummary={
            "title": "Chapter Strategy Snapshot",
            "hook": "Open with high-pressure information to lock reader attention quickly.",
            "conflict": "Prioritize mainline conflict and preserve a recoverable contradiction point.",
            "turn": "Inject a mid-section reveal or light reversal to avoid pacing flatness.",
            "payoff": "Close with a concrete stage payoff and a clear next-chapter hook.",
        },
        tuningWeights=[
            {
                "label": "Payoff Burst",
                "value": 0.78,
                "direction": "up",
                "description": "Increase release intensity after suppression and reversal.",
            },
            {
                "label": "Pacing Speed",
                "value": 0.62,
                "direction": "up",
                "description": "Accelerate chapter progression and reduce drag.",
            },
            {
                "label": "Action Density",
                "value": 0.55,
                "direction": "up",
                "description": "Increase action scenes and collision cadence.",
            },
            {
                "label": "Emotion Dwell",
                "value": 0.47,
                "direction": "down",
                "description": "Trim overlong emotional pauses that reduce momentum.",
            },
            {
                "label": "Setup Weight",
                "value": 0.58,
                "direction": "down",
                "description": "Reduce excessive setup and surface core conflict sooner.",
            },
        ],
        recommendations=recommendations,
        feedbackNotes=[
            "Early chapter samples most strongly corrected conflict momentum weights.",
            "Mid-stage samples improved linkage between foreshadow and pacing.",
            "Late-stage samples strengthened payoff pressure to emotion payoff coupling.",
        ],
        logs=[
            {
                "time": "2026-04-21 10:41",
                "text": "v001 matrix initialized and trained on 10 samples.",
            },
            {
                "time": "2026-04-21 11:08",
                "text": "Added middle-stage samples and adjusted foreshadow/pacing weights.",
            },
            {
                "time": "2026-04-21 11:32",
                "text": "Added late-stage samples and strengthened payoff/emotion feedback loop.",
            },
        ],
        v4Observability=v4_observability,
    )
