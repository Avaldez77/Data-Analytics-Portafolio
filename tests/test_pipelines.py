from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from Cutoff.Cutoff import classify_orders
from Outbound.Outbound import build_reports, export_workbook
from Performance.performance import process_files


class PerformanceTests(unittest.TestCase):
    def test_combines_files_and_adds_iso_calendar_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pd.DataFrame({"Document Date": ["2026-01-05"], "Order ID": ["A"]}).to_csv(
                root / "jan.csv", index=False
            )
            pd.DataFrame({"Document Date": ["2026-01-08"], "Order ID": ["B"]}).to_csv(
                root / "feb.csv", index=False
            )

            result, summary = process_files(root)

        self.assertEqual(len(result), 2)
        self.assertEqual(result["ISO Week"].tolist(), [2, 2])
        self.assertEqual(summary["files_processed"], 2)

    def test_rejects_invalid_dates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pd.DataFrame({"Document Date": ["not-a-date"]}).to_csv(root / "bad.csv", index=False)

            with self.assertRaisesRegex(ValueError, "invalid dates"):
                process_files(root)

    def test_rejects_empty_exports(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pd.DataFrame(columns=["Document Date"]).to_csv(root / "empty.csv", index=False)

            with self.assertRaisesRegex(ValueError, "no data rows"):
                process_files(root)


class CutoffTests(unittest.TestCase):
    def test_applies_cutoff_and_reassigns_automated_orders(self) -> None:
        operations = pd.DataFrame(
            [
                ["A", "B1", "2026-01-05 11:00", "BOT-01"],
                ["B", "B1", "2026-01-05 11:01", "person@example.test"],
            ],
            columns=["order_id", "buyer_code", "created_at", "created_by"],
        )
        buyers = pd.DataFrame(
            [["B1", "AR", "Prime Auto", "11:00", "owner@example.test"]],
            columns=["buyer_code", "country", "group", "cutoff_time", "owner"],
        )

        result = classify_orders(operations, buyers)

        self.assertEqual(result["status"].tolist(), ["On time", "Late"])
        self.assertEqual(result.loc[0, "assigned_to"], "owner@example.test")

    def test_rejects_missing_buyer_reference(self) -> None:
        operations = pd.DataFrame(
            [["A", "missing", "2026-01-05 10:00", "analyst"]],
            columns=["order_id", "buyer_code", "created_at", "created_by"],
        )
        buyers = pd.DataFrame(
            columns=["buyer_code", "country", "group", "cutoff_time", "owner"]
        )

        with self.assertRaisesRegex(ValueError, "No buyer reference"):
            classify_orders(operations, buyers)


class OutboundTests(unittest.TestCase):
    def test_aggregates_shipment_kpis_and_exports_workbook(self) -> None:
        source = pd.DataFrame(
            [
                ["AR", "air", "no", "DO-1", "12", "48.5", "0.42"],
                ["AR", "AIR", "yes", "DO-2", "4", "16", "0.18"],
            ],
            columns=[
                "Ship-To Country",
                "Ship Type",
                "DG Y/N",
                "DO",
                "Delivery Qty",
                "Gross Weight",
                "Vol.",
            ],
        )

        orders, summary, quality = build_reports(source)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.xlsx"
            export_workbook(orders, summary, quality, output)
            with pd.ExcelFile(output) as workbook:
                sheet_names = set(workbook.sheet_names)

        self.assertEqual(sheet_names, {"Orders", "Shipment KPIs", "Data Quality"})
        self.assertEqual(summary["Lines"].sum(), 2)
        self.assertEqual(quality.loc[0, "value"], 2)

    def test_rejects_unsupported_country(self) -> None:
        source = pd.DataFrame(
            [["ZZ", "Air", "No", "DO-1", 1, 1, 1]],
            columns=[
                "Ship-To Country",
                "Ship Type",
                "DG Y/N",
                "DO",
                "Delivery Qty",
                "Gross Weight",
                "Vol.",
            ],
        )

        with self.assertRaisesRegex(ValueError, "Unsupported Ship-To Country"):
            build_reports(source)


if __name__ == "__main__":
    unittest.main()
