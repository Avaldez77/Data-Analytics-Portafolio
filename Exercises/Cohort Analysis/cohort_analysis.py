from __future__ import annotations

import argparse
import math
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"transaction_id", "customer_id", "order_date", "revenue"}


def build_cohort_report(transactions: pd.DataFrame) -> pd.DataFrame:
    missing = sorted(REQUIRED_COLUMNS - set(transactions.columns))
    if missing:
        raise ValueError(f"Input is missing required columns: {', '.join(missing)}")

    data = transactions.copy()
    for column in ("transaction_id", "customer_id"):
        data[column] = data[column].astype("string").str.strip()
        if data[column].isna().any() or data[column].eq("").any():
            raise ValueError(f"{column} cannot be blank")
    if data["transaction_id"].duplicated().any():
        raise ValueError("transaction_id values must be unique")

    data["order_date"] = pd.to_datetime(data["order_date"], errors="coerce")
    if data["order_date"].isna().any():
        raise ValueError("order_date contains invalid or missing dates")
    data["revenue"] = pd.to_numeric(data["revenue"], errors="coerce")
    if data["revenue"].isna().any() or not data["revenue"].map(math.isfinite).all():
        raise ValueError("revenue must contain valid numeric values")
    if data["revenue"].lt(0).any():
        raise ValueError("revenue cannot be negative")

    purchase_month = data["order_date"].dt.to_period("M")
    data["activity_month"] = purchase_month
    data["cohort_month"] = data.assign(purchase_month=purchase_month).groupby(
        "customer_id"
    )["purchase_month"].transform("min")
    data["cohort_index"] = (
        (data["activity_month"].dt.year - data["cohort_month"].dt.year) * 12
        + data["activity_month"].dt.month
        - data["cohort_month"].dt.month
        + 1
    )

    cohort_sizes = data.groupby("cohort_month")["customer_id"].nunique().rename("cohort_size")
    activity = (
        data.groupby(["cohort_month", "cohort_index"], as_index=False)
        .agg(active_customers=("customer_id", "nunique"), revenue=("revenue", "sum"))
        .join(cohort_sizes, on="cohort_month")
    )
    activity["retention_rate"] = activity["active_customers"] / activity["cohort_size"]
    activity["cohort_month"] = activity["cohort_month"].astype(str)
    return activity[
        [
            "cohort_month",
            "cohort_index",
            "cohort_size",
            "active_customers",
            "retention_rate",
            "revenue",
        ]
    ].sort_values(["cohort_month", "cohort_index"]).reset_index(drop=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a monthly customer cohort report.")
    parser.add_argument("input", type=Path, help="Transactions CSV")
    parser.add_argument("--output", type=Path, required=True, help="Cohort report CSV")
    args = parser.parse_args(argv)

    report = build_cohort_report(pd.read_csv(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(args.output, index=False)
    print(f"Wrote {len(report)} cohort-period rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
