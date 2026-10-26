from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

import pandas as pd


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "Exercises"
    / "Cohort Analysis"
    / "cohort_analysis.py"
)
SPEC = importlib.util.spec_from_file_location("cohort_analysis", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load cohort analysis module from {MODULE_PATH}")
COHORT_ANALYSIS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COHORT_ANALYSIS)


class CohortAnalysisTests(unittest.TestCase):
    def test_reports_monthly_retention_and_revenue(self) -> None:
        transactions = pd.DataFrame(
            [
                ["T1", "A", "2026-01-01", 10],
                ["T2", "B", "2026-01-15", 20],
                ["T3", "A", "2026-02-01", 5],
            ],
            columns=["transaction_id", "customer_id", "order_date", "revenue"],
        )

        report = COHORT_ANALYSIS.build_cohort_report(transactions)
        january = report[report["cohort_month"] == "2026-01"].reset_index(drop=True)

        self.assertEqual(january["cohort_size"].tolist(), [2, 2])
        self.assertEqual(january["active_customers"].tolist(), [2, 1])
        self.assertEqual(january["retention_rate"].tolist(), [1.0, 0.5])
        self.assertEqual(january["revenue"].tolist(), [30, 5])

    def test_rejects_duplicate_transaction_ids(self) -> None:
        transactions = pd.DataFrame(
            [
                ["T1", "A", "2026-01-01", 10],
                ["T1", "A", "2026-02-01", 5],
            ],
            columns=["transaction_id", "customer_id", "order_date", "revenue"],
        )

        with self.assertRaisesRegex(ValueError, "transaction_id values must be unique"):
            COHORT_ANALYSIS.build_cohort_report(transactions)

    def test_rejects_negative_revenue(self) -> None:
        transactions = pd.DataFrame(
            [["T1", "A", "2026-01-01", -1]],
            columns=["transaction_id", "customer_id", "order_date", "revenue"],
        )

        with self.assertRaisesRegex(ValueError, "revenue cannot be negative"):
            COHORT_ANALYSIS.build_cohort_report(transactions)


if __name__ == "__main__":
    unittest.main()
