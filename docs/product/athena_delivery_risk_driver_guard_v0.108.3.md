# Santoni Athena Delivery Risk Driver Guard v0.108.3

## Purpose

Athena v0.108.3 fixes a delivery-risk classification issue found during actual APS/ERP export testing.

In v0.108.2, an order could enter the delivery-risk list only because its delivery date was close or its part-order quantity still showed an unscheduled gap. This created confusing evidence such as an order with 99.5% to 100% planned-task completion still being described as a current delivery risk.

## Rule Change

Athena now separates two concepts:

- **Delivery risk**: evidence shows the order is due soon or recently overdue, and planned-task completion is not close to complete.
- **Delivery reconciliation candidate**: evidence is internally inconsistent, stale, or status-dependent, so a planning owner must confirm the order state before Athena can claim a delivery risk.

## Driver Contract

Each delivery evidence chain can include `delivery_risk_drivers`.

Driver fields:

- `driver`
- `classification`: `delivery_risk` or `data_reconciliation`
- `field_source`
- `value`
- `threshold`
- `explanation_en`
- `explanation_zh`

## Current Actual-Export Example

Orders `7260149`, `7260147`, and `7260148` had planned-task completion at roughly 99.5% to 100%, while their export evidence also showed reconciliation flags or stale delivery-date status. Athena now classifies these as delivery status or quantity reconciliation candidates instead of hard delivery-risk candidates.

## Read-Only Boundary

Athena still does not:

- write APS
- write ERP
- write IOT
- change schedules
- dispatch work orders
- claim a root cause without evidence

The correct next action is to ask the planning owner to confirm order status, split-task policy, and quantity reporting scope before using these rows as customer-facing delivery-risk evidence.
