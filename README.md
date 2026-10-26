# Data Analytics Portfolio

Three small, runnable examples of operational analytics work: consolidating monthly files, applying cutoff rules, and producing outbound volume summaries. The original projects were built around private operational systems. This public version keeps the transformation logic while replacing private paths, credentials, names, and source data.

The CSV files under each `examples/` folder are synthetic. They exist only to make the code easy to review and run; they are not client records and the output should not be interpreted as a business result.

## Projects

| Project | What it demonstrates | Demo output |
| --- | --- | --- |
| [Performance](Performance/) | Monthly-file discovery, schema checks, date validation, ISO calendar fields, and consolidation | A clean CSV plus a JSON quality summary |
| [Cutoff](Cutoff/) | Reference-data joins, configurable cutoff rules, bot-owner reassignment, and on-time/late classification | A row-level CSV ready for BI |
| [Outbound](Outbound/) | Data cleaning, transport-mode normalization, KPI aggregation, and multi-sheet Excel reporting | An Excel workbook with order, KPI, and quality sheets |
| [Practical exercises](Exercises/README.md) | Data reconciliation, effective-dated rules, and quality-gated reporting | Three extension challenges |

## Run the examples

The repository targets Python 3.10 or newer.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt

python Performance/performance.py Performance/examples --output outputs/performance.csv --summary outputs/performance_summary.json
python Cutoff/Cutoff.py Cutoff/examples/operations_synthetic.csv Cutoff/examples/buyers_synthetic.csv --output outputs/cutoff.csv
python Outbound/Outbound.py Outbound/examples/orders_synthetic.csv --output outputs/outbound.xlsx
```

Run the lightweight test suite with:

```bash
python -m unittest discover -s tests -v
```

## Design notes

- File locations are command-line arguments; there are no workstation-specific or network-share paths.
- Transformations are exposed as functions so they can be tested without touching a database.
- Every pipeline validates its required schema before doing work and creates parent output folders when needed.
- The public examples are offline demos. They do not connect to SQL Server or
  any other enterprise system.
- SQL Server publishing is deliberately outside this public sample. In a production deployment I would keep credentials in environment or secret storage and load through a staging table with an explicit merge strategy.
- The repository does not claim time savings, accuracy improvements, or production scale because those measurements are not included in the public evidence.

The `.docx` files are retained as the earlier project notes. The READMEs and Python modules are the maintained, runnable versions.
