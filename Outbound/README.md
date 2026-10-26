# Outbound shipment reporting

This offline example validates a synthetic orders CSV, normalizes shipment
mode and dangerous-goods labels, maps supported country codes to subsidiaries,
and generates a workbook with order-level data, shipment KPIs, and data-quality
counts.

The country mapping and sample records are fictional demonstration inputs.
Unsupported countries and invalid or negative measures are rejected rather
than silently excluded.

Run from the repository root:

```bash
python Outbound/Outbound.py Outbound/examples/orders_synthetic.csv --output outputs/outbound.xlsx
```

The example does not claim production scale or measured business results.
