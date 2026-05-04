from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_v3_build_script_emits_records_and_matrix_projection(tmp_path: Path) -> None:
    source = tmp_path / "report.json"
    source.write_text(
        json.dumps(
            {
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
        ),
        encoding="utf-8",
    )

    target = tmp_path / "out"
    cmd = [
        sys.executable,
        "scripts/build_v3_reverse_decomposition_records.py",
        "--input-report",
        str(source),
        "--output-dir",
        str(target),
        "--genre",
        "xuanhuan",
    ]
    result = subprocess.run(
        cmd,
        cwd=Path(__file__).resolve().parents[1],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    assert result.returncode == 0, result.stderr
    assert (target / "reverse_outline_records.jsonl").exists()
    assert (target / "matrix_projection.json").exists()
    assert (target / "qc_report.json").exists()

    stdout = json.loads(result.stdout)
    assert stdout["qc_path"] == str(target / "qc_report.json")

    qc = json.loads((target / "qc_report.json").read_text(encoding="utf-8"))
    assert qc["record_count"] == 1
    assert qc["projection_count"] == 1
    assert qc["schema_version"] == "1.0"
    assert "admission_distribution" in qc
    assert "checkpoint_status_distribution" in qc
    assert "generated_at" in qc


def test_v3_build_script_accepts_utf8_bom_report(tmp_path: Path) -> None:
    source = tmp_path / "report.json"
    source.write_text(
        json.dumps(
            {
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
        ),
        encoding="utf-8-sig",
    )

    target = tmp_path / "out"
    cmd = [
        sys.executable,
        "scripts/build_v3_reverse_decomposition_records.py",
        "--input-report",
        str(source),
        "--output-dir",
        str(target),
        "--genre",
        "xuanhuan",
    ]
    result = subprocess.run(
        cmd,
        cwd=Path(__file__).resolve().parents[1],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    assert result.returncode == 0, result.stderr
    assert (target / "qc_report.json").exists()
