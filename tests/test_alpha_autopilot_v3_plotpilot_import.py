from __future__ import annotations

from alpha_autopilot_v3.decomposition.pipeline import build_records_from_plotpilot_report
from alpha_autopilot_v3.decomposition.projection import project_record_for_matrix


def test_v3_plotpilot_import_turns_report_into_decomposition_records() -> None:
    payload = {
        "model": "gpt-5.4",
        "results": [
            {
                "chapter": 1,
                "title": "black_jade_awakens",
                "success": True,
                "chars": 3354,
                "preview": "A young cultivator escapes into a sword valley.",
            }
        ],
    }

    records = build_records_from_plotpilot_report(payload, genre="xuanhuan")

    assert len(records) == 1
    assert records[0].title == "black jade awakens"
    assert records[0].workbench_context["recommended_stage"] == "opening"

    projection = project_record_for_matrix(records[0])
    assert projection["genre"] == "xuanhuan"
    assert projection["recommended_stage"] == "opening"
