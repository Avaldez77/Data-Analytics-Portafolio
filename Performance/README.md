# Monthly performance consolidation

This offline example consolidates monthly CSV or Excel exports that include a
`Document Date` column. It validates dates, adds ISO year/week fields, records
the source filename, and writes a consolidated CSV and JSON summary.

The included data is synthetic. This public example does not connect to SQL
Server, shared folders, or any company system, and it does not claim measured
business impact.

Run from the repository root:

```bash
python Performance/performance.py Performance/examples --output outputs/performance.csv --summary outputs/performance_summary.json
```

Invalid or missing dates and missing required columns are reported as errors
instead of being silently accepted.
