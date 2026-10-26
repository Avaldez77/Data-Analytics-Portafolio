# Buyer cutoff classification

This offline example joins synthetic operational orders to a buyer reference,
validates identifiers and cutoff times, reassigns automated orders to the
reference owner, and labels each order `On time` or `Late`.

The cutoff is inclusive: an order created at the configured `HH:MM` is on
time. Input schemas and fictional sample rows are in `examples/`. No database
connection or company data is used.

Run from the repository root:

```bash
python Cutoff/Cutoff.py Cutoff/examples/operations_synthetic.csv Cutoff/examples/buyers_synthetic.csv --output outputs/cutoff.csv
```

Duplicate identifiers, invalid timestamps, unmatched buyers, and malformed
cutoff values fail explicitly.
