from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd
from scipy.stats import norm


REQUIRED_COLUMNS = {"user_id", "variant", "converted"}
VARIANTS = ("control", "treatment")


def analyze_experiment(records: pd.DataFrame) -> dict[str, Any]:
    missing = sorted(REQUIRED_COLUMNS - set(records.columns))
    if missing:
        raise ValueError(f"Input is missing required columns: {', '.join(missing)}")

    data = records.loc[:, ["user_id", "variant", "converted"]].copy()
    for column in ("user_id", "variant"):
        data[column] = data[column].astype("string").str.strip()
        if data[column].isna().any() or data[column].eq("").any():
            raise ValueError(f"{column} cannot be blank")
    if data["user_id"].duplicated().any():
        raise ValueError("user_id values must be unique")
    if set(data["variant"]) != set(VARIANTS):
        raise ValueError("variant must contain control and treatment groups")

    data["converted"] = pd.to_numeric(data["converted"], errors="coerce")
    if (
        data["converted"].isna().any()
        or not data["converted"].map(math.isfinite).all()
        or not data["converted"].isin((0, 1)).all()
    ):
        raise ValueError("converted must contain only finite binary values (0 or 1)")

    grouped = data.groupby("variant")["converted"].agg(["sum", "count"])
    control_successes = int(grouped.loc["control", "sum"])
    treatment_successes = int(grouped.loc["treatment", "sum"])
    control_count = int(grouped.loc["control", "count"])
    treatment_count = int(grouped.loc["treatment", "count"])
    control_rate = control_successes / control_count
    treatment_rate = treatment_successes / treatment_count
    absolute_lift = treatment_rate - control_rate

    pooled_rate = (control_successes + treatment_successes) / (
        control_count + treatment_count
    )
    null_standard_error = math.sqrt(
        pooled_rate * (1 - pooled_rate) * (1 / control_count + 1 / treatment_count)
    )
    z_score = absolute_lift / null_standard_error if null_standard_error else 0.0
    p_value = 2 * norm.sf(abs(z_score))

    interval_standard_error = math.sqrt(
        control_rate * (1 - control_rate) / control_count
        + treatment_rate * (1 - treatment_rate) / treatment_count
    )
    margin = norm.ppf(0.975) * interval_standard_error
    relative_lift = (
        absolute_lift / control_rate if control_rate > 0 else None
    )

    return {
        "control": {
            "conversions": control_successes,
            "users": control_count,
            "conversion_rate": control_rate,
        },
        "treatment": {
            "conversions": treatment_successes,
            "users": treatment_count,
            "conversion_rate": treatment_rate,
        },
        "absolute_lift": absolute_lift,
        "relative_lift": relative_lift,
        "confidence_interval_95": [
            absolute_lift - margin,
            absolute_lift + margin,
        ],
        "z_score": z_score,
        "p_value_two_sided": p_value,
        "significant_at_0_05": bool(p_value < 0.05),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze a two-variant conversion experiment.")
    parser.add_argument("input", type=Path, help="Experiment CSV")
    parser.add_argument("--output", type=Path, required=True, help="Result JSON")
    args = parser.parse_args(argv)

    result = analyze_experiment(pd.read_csv(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote experiment analysis to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
