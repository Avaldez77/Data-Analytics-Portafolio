from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


OPERATION_COLUMNS = {"order_id", "buyer_code", "created_at", "created_by"}
BUYER_COLUMNS = {"buyer_code", "country", "group", "cutoff_time", "owner"}


def classify_orders(operations: pd.DataFrame, buyers: pd.DataFrame) -> pd.DataFrame:
    missing_operations = sorted(OPERATION_COLUMNS - set(operations.columns))
    missing_buyers = sorted(BUYER_COLUMNS - set(buyers.columns))
    if missing_operations:
        raise ValueError(f"Operations data is missing columns: {', '.join(missing_operations)}")
    if missing_buyers:
        raise ValueError(f"Buyer data is missing columns: {', '.join(missing_buyers)}")

    operations = operations.copy()
    buyers = buyers.copy()
    for frame, key, label in (
        (operations, "order_id", "order_id"),
        (operations, "buyer_code", "buyer_code"),
        (buyers, "buyer_code", "buyer_code"),
    ):
        frame[key] = frame[key].astype("string").str.strip()
        if frame[key].isna().any() or frame[key].eq("").any():
            raise ValueError(f"{label} cannot be blank")
    if operations["order_id"].duplicated().any():
        raise ValueError("order_id values must be unique")
    if buyers["buyer_code"].duplicated().any():
        raise ValueError("buyer_code values must be unique")

    operations["created_at"] = pd.to_datetime(operations["created_at"], errors="coerce")
    if operations["created_at"].isna().any():
        raise ValueError("created_at contains invalid or missing timestamps")
    if buyers["cutoff_time"].isna().any() or not buyers["cutoff_time"].astype(str).str.fullmatch(
        r"(?:[01]\d|2[0-3]):[0-5]\d"
    ).all():
        raise ValueError("cutoff_time must use 24-hour HH:MM format")

    result = operations.merge(
        buyers,
        on="buyer_code",
        how="left",
        validate="many_to_one",
        indicator=True,
    )
    unmatched = result["_merge"] != "both"
    if unmatched.any():
        codes = ", ".join(sorted(result.loc[unmatched, "buyer_code"].astype(str).unique()))
        raise ValueError(f"No buyer reference found for buyer_code values: {codes}")
    result = result.drop(columns="_merge")

    cutoff_minutes = (
        result["cutoff_time"].str.slice(0, 2).astype(int) * 60
        + result["cutoff_time"].str.slice(3, 5).astype(int)
    )
    created_minutes = result["created_at"].dt.hour * 60 + result["created_at"].dt.minute
    is_automated = result["created_by"].astype("string").str.contains(
        r"BOT|CRT", case=False, na=False
    )
    result["assigned_to"] = result["created_by"].where(~is_automated, result["owner"])
    result["status"] = (created_minutes <= cutoff_minutes).map(
        {True: "On time", False: "Late"}
    )
    return result.sort_values(["created_at", "order_id"]).reset_index(drop=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Classify orders against buyer cutoff rules.")
    parser.add_argument("operations", type=Path, help="Operations CSV")
    parser.add_argument("buyers", type=Path, help="Buyer reference CSV")
    parser.add_argument("--output", type=Path, required=True, help="Output CSV")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = classify_orders(pd.read_csv(args.operations), pd.read_csv(args.buyers))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"Classified {len(result)} orders")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
