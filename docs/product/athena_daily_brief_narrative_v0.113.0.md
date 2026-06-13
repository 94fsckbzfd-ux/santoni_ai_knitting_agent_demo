# Santoni Athena Daily Brief Narrative v0.113.0

Athena v0.113.0 adds a General Manager daily brief narrative for the three-minute production decision workflow.

## Implemented
- The General Manager page generates a daily brief after loading the dashboard.
- The brief summarizes today's top-three hard risks, data that should not be concluded yet, confirmation owners, impact focus, and evidence boundary.
- The user page includes a "Generate Daily Brief" action and copy support.
- The brief is built from structured risk cards, Evidence Review Queue, Service risk cards, and the local decision loop.

## Boundary
- The brief does not expose raw JSON or internal schema.
- It does not invent final root-cause conclusions when evidence is incomplete.
- Athena remains read-only: no APS/ERP/IOT writes, no schedule changes, no dispatch, and no machine control.

