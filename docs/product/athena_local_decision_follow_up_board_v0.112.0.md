# Santoni Athena Local Decision Follow-up Board v0.112.0

Athena v0.112.0 extends the local decision loop so all General Manager card types can become metadata-only follow-up items.

## Implemented
- Hard risks, evidence-review candidates, and Service-risk candidates share one local follow-up contract.
- Each follow-up records source card type, related object, confirmation owner, confirmation need, Athena recommendation reason, evidence refs, and read-only boundary.
- Supported manager-facing statuses include pending confirmation, confirmed, needs more data, resolved, and dismissed.
- Follow-up questions continue in the original user chat stream.

## Boundary
- Follow-ups do not write APS, ERP, IOT, ticket systems, Hermes memory, or machine controls.
- Follow-ups are local metadata only and require human confirmation.

