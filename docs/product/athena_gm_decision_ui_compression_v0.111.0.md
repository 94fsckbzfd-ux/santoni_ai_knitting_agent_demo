# Santoni Athena GM Decision UI Compression v0.111.0

Athena v0.111.0 compresses the customer-facing General Manager experience into a decision-first surface.

## Implemented
- Drilldown answers default to four manager-facing fields: conclusion, evidence support, suggested confirmation owner, and next action.
- Full evidence, checked objects, field sources, sanity flags, and data gaps stay inside expandable details.
- Hard-risk cards, evidence-review cards, and Service-risk cards use different management meanings.
- Evidence Review Queue cards are presented as confirmation tasks instead of confirmed risk conclusions.

## Boundary
- No raw JSON or payload is shown on the customer home page.
- Developer and Production Console pages may still show fuller internal evidence.

