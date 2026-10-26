# Practical exercises

Use only the fictional CSV files in this repository. Each exercise is designed
to be completed without access to a company system or customer data.

## 0. Customer cohort retention

Run the implemented [Cohort Analysis](./Cohort%20Analysis/README.md) example
to calculate monthly active-customer counts, retention rates, and revenue by
first-purchase month. Then extend it to test a rolling 90-day retention window.

**Acceptance criteria:** each customer is assigned to exactly one cohort,
month zero has 100% retention, and missing or duplicate transaction IDs fail
before metrics are produced.

## 1. Performance pipeline: reconcile a late-arriving file

Add a third monthly CSV with one valid record and one malformed date. Confirm
that the pipeline reports the source file and row for invalid dates, then repair
the record and verify the consolidated row count and ISO week.

**Acceptance criteria:** input files are discovered deterministically; invalid
dates fail with a useful message; the JSON summary matches the resulting data.

## 2. Cutoff rules: make ownership effective-dated

Extend the buyer reference with `effective_from` and `effective_to` fields.
Resolve each order to exactly one active buyer record before applying the cutoff.
Add tests for a boundary date, an overlapping interval, and no matching interval.

**Acceptance criteria:** ambiguous or missing buyer references fail explicitly;
the existing on-time rule remains inclusive at the cutoff minute.

## 3. Outbound reporting: add a quality gate

Add a configurable maximum-volume rule and produce a separate exception sheet
for orders that exceed it. Do not silently drop records with unsupported
countries or invalid numeric values.

**Acceptance criteria:** the workbook contains reproducible KPI and exception
sheets, and tests cover both a passing and a failing quality rule.

Run the current examples and test suite from this repository root:

```bash
python Performance/performance.py Performance/examples --output outputs/performance.csv --summary outputs/performance_summary.json
python Cutoff/Cutoff.py Cutoff/examples/operations_synthetic.csv Cutoff/examples/buyers_synthetic.csv --output outputs/cutoff.csv
python Outbound/Outbound.py Outbound/examples/orders_synthetic.csv --output outputs/outbound.xlsx
python Exercises/Cohort\ Analysis/cohort_analysis.py Exercises/Cohort\ Analysis/examples/transactions_synthetic.csv --output outputs/cohort_retention.csv
python -m unittest discover -s tests -v
```
