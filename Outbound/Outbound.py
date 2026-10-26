from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "Ship-To Country",
    "Ship Type",
    "DG Y/N",
    "DO",
    "Delivery Qty",
    "Gross Weight",
    "Vol.",
}
COUNTRY_TO_SUBSIDIARY = {
    "AR": "SEDA",
    "MX": "SEM",
    "CO": "SAMCOL",
    "CL": "SECH",
    "BR": "SEASA",
    "PR": "SEPR",
}
NUMERIC_COLUMNS = ("Delivery Qty", "Gross Weight", "Vol.")


def build_reports(source: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    missing = sorted(REQUIRED_COLUMNS - set(source.columns))
    if missing:
        raise ValueError(f"Input is missing required columns: {', '.join(missing)}")

    orders = source.copy()
    orders["Ship-To Country"] = orders["Ship-To Country"].astype("string").str.strip().str.upper()
    orders["Ship Type"] = orders["Ship Type"].astype("string").str.strip().str.title()
    orders["DG Y/N"] = orders["DG Y/N"].astype("string").str.strip().str.upper()
    orders["DO"] = orders["DO"].astype("string").str.strip()

    for column in NUMERIC_COLUMNS:
        values = pd.to_numeric(orders[column], errors="coerce")
        if values.isna().any():
            raise ValueError(f"{column} must contain valid numeric values")
        if values.lt(0).any():
            raise ValueError(f"{column} cannot contain negative values")
        orders[column] = values

    if not orders["Ship Type"].isin({"Air", "Ocean"}).all():
        raise ValueError("Ship Type must be Air or Ocean")
    if not orders["DG Y/N"].isin({"YES", "NO"}).all():
        raise ValueError("DG Y/N must be Yes or No")

    orders["Subsidiary"] = orders["Ship-To Country"].map(COUNTRY_TO_SUBSIDIARY)
    unmapped = orders["Subsidiary"].isna()
    quality = pd.DataFrame(
        [
            {"check": "input_rows", "value": len(orders)},
            {"check": "unmapped_country_rows", "value": int(unmapped.sum())},
            {"check": "duplicate_delivery_orders", "value": int(orders["DO"].duplicated().sum())},
        ]
    )
    if unmapped.any():
        countries = ", ".join(sorted(orders.loc[unmapped, "Ship-To Country"].astype(str).unique()))
        raise ValueError(f"Unsupported Ship-To Country values: {countries}")

    summary = (
        orders.groupby(["Subsidiary", "Ship Type", "DG Y/N"], as_index=False)
        .agg(
            Lines=("DO", "count"),
            Quantity=("Delivery Qty", "sum"),
            Weight_Kg=("Gross Weight", "sum"),
            Volume_M3=("Vol.", "sum"),
        )
        .sort_values(["Subsidiary", "Ship Type", "DG Y/N"])
        .reset_index(drop=True)
    )
    return orders, summary, quality


def export_workbook(
    orders: pd.DataFrame, summary: pd.DataFrame, quality: pd.DataFrame, output: Path
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output, engine="openpyxl") as workbook:
        orders.to_excel(workbook, sheet_name="Orders", index=False)
        summary.to_excel(workbook, sheet_name="Shipment KPIs", index=False)
        quality.to_excel(workbook, sheet_name="Data Quality", index=False)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build an outbound logistics KPI workbook.")
    parser.add_argument("input", type=Path, help="Synthetic or authorized orders CSV")
    parser.add_argument("--output", type=Path, required=True, help="Destination XLSX workbook")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    reports = build_reports(pd.read_csv(args.input))
    export_workbook(*reports, args.output)
    print(f"Workbook written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
