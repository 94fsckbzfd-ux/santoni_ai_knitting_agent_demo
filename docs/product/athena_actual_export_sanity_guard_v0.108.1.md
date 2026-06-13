# Santoni Athena Actual Export Evidence Sanity Guard v0.108.1

Date: 2026-06-12

## Summary

Athena v0.108.1 improves how Tianpai APS/ERP export evidence is treated before it appears in the General Manager workflow. The CSV exports still have no headers, so Athena reads them by the `表字段` DDL field order (`biao-ziduan`, table-field definition). This version adds guardrails so unusual values are not presented as certain production conclusions.

## What Changed

- Filters deleted rows before building order, schedule, reporting, machine, and evidence-chain objects.
- Keeps raw row count and active row count visible in the adapter report.
- Excludes delivery dates more than 30 days overdue from current delivery-risk ranking until order status is confirmed.
- Marks extreme manual-report versus plan gaps as `needs_reconciliation`.
- Adds data-gap notes explaining that task_id, barcode, reporting date, split-task policy, and unit scope must be reconciled before claiming production loss.

## Why It Was Needed

Two examples exposed the risk:

- Order `1260123` showed `days_to_due = -74` and `plan_completion_rate = 0.0`. The source delivery date exists, but the order is too stale for a current-risk card without status review.
- Order `1260341` showed a planned-vs-reported gap of `168145`. The arithmetic comes from export aggregates, but the value is large enough that Athena should treat it as a reporting reconciliation candidate.

## Current Behavior

Athena can still use these records as evidence, but it changes the claim:

- From: "this is definitely a production abnormality."
- To: "this is a data/evidence reconciliation candidate that the planning or reporting owner should confirm."

## Still Read-Only

Athena does not write APS, ERP, IOT, or Hermes. It also does not write ticket systems or machine controls. It does not change schedules, upload `.co` / `.cx`, dispatch Service, or correct customer data.

## Next Validation

Ask APS and Tianpai process owners to confirm:

- The status meaning for `Produce_Order.status`, `Weaving_Part_Order.status`, and `Planned_Task.status`.
- Whether `Manual_Machine_Production.operator_quantity` can be summed directly by `produce_order_code`.
- Whether part-order `quantity`, `planned_quantity`, and reporting quantity share the same unit and scope.
