from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


DATE_COLUMN = "Document Date"


def process_files(input_dir: Path) -> tuple[pd.DataFrame, dict[str, object]]:
    files = sorted(
        (*input_dir.glob("*.csv"), *input_dir.glob("*.xlsx"))
    )
    if not files:
        raise ValueError(f"No CSV or Excel files found in {input_dir}")

    frames: list[pd.DataFrame] = []
    for path in files:
        frame = (
            pd.read_excel(path, engine="openpyxl")
            if path.suffix.lower() == ".xlsx"
            else pd.read_csv(path)
        )
        if frame.empty:
            raise ValueError(f"{path.name} contains no data rows")
        if DATE_COLUMN not in frame.columns:
            raise ValueError(f"{path.name} is missing required column '{DATE_COLUMN}'")

        dates = pd.to_datetime(frame[DATE_COLUMN], errors="coerce")
        invalid_rows = (dates.isna()).to_numpy().nonzero()[0] + 2
        if len(invalid_rows):
            rows = ", ".join(map(str, invalid_rows[:10]))
            raise ValueError(f"{path.name} has invalid dates on CSV/Excel rows: {rows}")

        frame = frame.copy()
        frame[DATE_COLUMN] = dates
        iso_dates = dates.dt.isocalendar()
        frame["ISO Year"] = iso_dates.year.astype(int)
        frame["ISO Week"] = iso_dates.week.astype(int)
        frame["Source File"] = path.name
        frames.append(frame)

    result = pd.concat(frames, ignore_index=True, sort=False)
    summary: dict[str, object] = {
        "files_processed": len(files),
        "rows_processed": len(result),
        "first_document_date": result[DATE_COLUMN].min().date().isoformat(),
        "last_document_date": result[DATE_COLUMN].max().date().isoformat(),
    }
    return result, summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Consolidate monthly performance exports.")
    parser.add_argument("input_dir", type=Path, help="Directory containing CSV/XLSX exports")
    parser.add_argument("--output", type=Path, required=True, help="Path to the consolidated CSV")
    parser.add_argument("--summary", type=Path, required=True, help="Path to the JSON quality summary")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result, summary = process_files(args.input_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Processed {summary['rows_processed']} rows from {summary['files_processed']} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
