# Santoni Athena Evidence Review Queue v0.109.0

## Purpose

Athena v0.109.0 adds an Evidence Review Queue for General Manager production decisions.

The queue separates confirmed hard risks from records where APS/ERP export evidence is internally inconsistent. This prevents Athena from presenting completed or nearly completed orders as delivery risks when the stronger conclusion is that planning status or quantity scope needs review.

## Review Candidate Rules

An order can enter the review queue when:

- planned-task completion is greater than or equal to 98% but part-order quantity still appears unscheduled
- planned-task completion is greater than or equal to 98% but planned/report quantity evidence has sanity flags
- delivery date is stale enough that order status must be confirmed before the row is treated as current risk
- evidence credibility is `needs_reconciliation`

## Card Contract

Each card includes:

- order or object id
- why Athena does not treat it as hard delivery risk
- reconciliation drivers
- plan completion rate
- days to due
- unscheduled quantity
- report-plan quantity gap
- sanity flags
- field sources
- suggested confirmation owner
- suggested confirmation action
- cannot-conclude reason
- read-only boundary

## Read-Only Boundary

The queue does not write APS, ERP, IOT, service systems, schedules, machine controls, or Hermes memory.

The correct next action is owner confirmation, not automatic production action.
