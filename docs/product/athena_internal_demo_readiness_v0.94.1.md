# Santoni Athena Internal Demo Readiness Report v0.94.1

Date: 2026-06-11

## Patch Note

v0.94.1 removes the Internal Demo Mode panel from the customer-facing user page. Internal demo guidance is still preserved as a Codex-facing delivery artifact and documentation report, not as content shown to the General Manager user. The internal story remains a General Manager 3-minute production decision workflow.

## What Athena Can Do Now

- Show a General Manager first screen around "what should I watch first today?"
- Rank production risks with delivery first, then equipment/material risks from the available APS/ERP export evidence.
- Show evidence references, field sources, affected objects, suggested owner, suggested action, and data gaps on each risk card.
- Explain Service risk as a confirmation candidate when machine or production signals may require maintenance review.
- Let the user ask Santoni Athena for root-cause drilldown from the same conversation thread.
- Generate and track local follow-up items as metadata-only review records.

## What Athena Cannot Do Yet

- It cannot connect to live ERP, APS, IOT, Service, or warehouse databases.
- It cannot automatically modify schedules, control machines, upload `.co` / `.cx` files, or dispatch Service work orders.
- It cannot prove Tianpai General Manager VOC coverage without customer verification.
- It cannot replace the General Manager's final decision authority.

## Internal Demo Ready

The following story can be demonstrated internally:

1. Open `/` and select General Manager.
2. Athena automatically shows today's top-three production priorities.
3. Open evidence details to show evidence refs, field sources, and data gaps.
4. Use "让 Athena 下钻" to ask for root-cause analysis in the original chat.
5. Show the Service risk section as a candidate requiring human confirmation.
6. Generate a local follow-up item and update its review status.
7. Explain that all actions are local metadata only and no APS/ERP/IOT write-back occurs.

## Evidence Boundary

- APS/ERP export evidence is preferred where available.
- Local mock data fills gaps for Service, quality, labor, and downstream production flow.
- Missing data is shown explicitly instead of being hidden behind a confident answer.
- Service risk is a candidate, not a dispatch.
- There is no APS write-back, no ERP write-back, no IOT write-back, and no automatic service dispatch.

## Future Development Plan

- Connect more real production tables when customer data is available.
- Strengthen the General Manager question bank with verified VOC.
- Add historical comparison for effective labor hours, machine downtime, quality events, and delivery risk.
- Build a stronger Service risk board for maintenance users after the General Manager flow is stable.
- Convert repeated follow-up patterns into Hermes-reviewed memory candidates.

## Demo Pages

- User page: `/`
- Production Console: `/production.html`
- Developer page: `/developer.html`
- Docs: `/docs.html`
- Changelog: `/changelog.html`

## Supporting APIs

- `/api/production/overview`
- `/api/production/chatbi`
- `/api/production/follow-up`
- `/api/production/follow-up/review`
- `/api/production/skills`
