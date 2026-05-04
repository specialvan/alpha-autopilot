from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from alpha_autopilot_v3.decomposition.pipeline import build_records_from_plotpilot_report  # noqa: E402
from alpha_autopilot_v3.decomposition.projection import project_record_for_matrix  # noqa: E402
from alpha_autopilot_v3.decomposition.qc import build_projection_qc_report  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-report", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--genre", type=str, required=True)
    args = parser.parse_args()

    payload = json.loads(args.input_report.read_text(encoding="utf-8-sig"))
    records = build_records_from_plotpilot_report(payload, genre=args.genre)
    projections = [project_record_for_matrix(record) for record in records if record.admission != "rejected"]

    args.output_dir.mkdir(parents=True, exist_ok=True)

    records_path = args.output_dir / "reverse_outline_records.jsonl"
    with records_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(asdict(record), ensure_ascii=False))
            handle.write("\n")

    projection_path = args.output_dir / "matrix_projection.json"
    projection_path.write_text(
        json.dumps(projections, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    qc_report = build_projection_qc_report(records, projections)
    qc_path = args.output_dir / "qc_report.json"
    qc_path.write_text(
        json.dumps(qc_report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "record_count": len(records),
                "projection_count": len(projections),
                "records_path": str(records_path),
                "projection_path": str(projection_path),
                "qc_path": str(qc_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
