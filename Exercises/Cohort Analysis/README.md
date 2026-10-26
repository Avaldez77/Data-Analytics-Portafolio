# Customer cohort retention

This runnable example assigns each customer to their first-purchase month,
then reports monthly active customers, cohort retention, and revenue using
fictional transactions.

From the repository root:

```bash
python "Exercises/Cohort Analysis/cohort_analysis.py" "Exercises/Cohort Analysis/examples/transactions_synthetic.csv" --output outputs/cohort_retention.csv
```

The cohort index is one-based: a customer's first observed purchase month is
index 1 and has 100% retention. A month with no purchase activity is not
materialized as an active-customer row. This is transaction activity retention,
not proof of subscription status or causal behavior.

## Extend the exercise

Add a 90-day retention definition and compare it with calendar-month retention.
Document how incomplete recent cohorts are treated and add boundary-date tests.
