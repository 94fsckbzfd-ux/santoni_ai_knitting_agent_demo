# Santoni Athena Demo Experience Report v0.97.0

Date: 2026-06-11

## What Changed In This Stage

- Added a Stable General Manager Demo Story Pack to the Production workflow.
- Added `/api/production/demo-story-pack` as a read-only API contract.
- Added a Production Console panel that shows three fixed demo stories instead of relying on ad hoc page navigation.
- Each story separates actual APS/ERP export evidence, clearly labeled mock supplements, data gaps, suggested owner, evidence refs, and one-click Santoni Athena drilldown.

## Stories Included

1. Real delivery-risk story: which order should the General Manager watch first?
2. Real machine/style-fit story: is any style scheduled onto a risky machine specification?
3. Hybrid service-impact story: if a machine keeps stopping, which order may be affected?

## Actual Data That Can Be Demonstrated

- `Produce_Order`, `Weaving_Part_Order`, `Planned_Task`, and `Manual_Machine_Production` can support delivery-risk and plan/progress evidence.
- `Style_Component` and `T_Machine_Info` can support machine/style specification-fit evidence.
- Yarn inventory aggregate and material priority cards can support material-risk discussion, but not full BOM-to-stock consumption proof yet.

## Mock Or Future Data Still Needed

- Live IOT alarm duration, OEE, downtime, and recovery timestamps.
- Real Service ticket creation or dispatch state.
- Quality defect reasons, replenishment closure, and downstream process records.
- Labor effective-hour history.
- Purchasing, rework, freight, and per-garment cost records.

## Internal Demo Ready

The following can be shown internally:

1. Open `/production.html`.
2. Start from the Stable Demo Story Pack panel.
3. Show Story 1 as the strongest real-data story.
4. Click Ask Athena to drill down into evidence and verification process.
5. Show Story 3 to explain exactly where mock IOT/Service evidence is being used.
6. Review local follow-up items without writing APS, ERP, IOT, Service, Hermes, or machine systems.

## What The Demo Must Not Claim

- It must not claim live APS / ERP / IOT integration.
- It must not claim real machine state or real Service dispatch.
- It must not claim final root cause when evidence is incomplete.
- It must not calculate real cost without purchasing, labor, rework, freight, and downstream quality records.

## Next Stage Recommendation

- Add a one-click demo reset and scripted internal demo route.
- Add a compact user-page entry for the same story pack if the Production Console version feels too internal.
- Prepare the next data request around live IOT alarm history, quality defect records, and downstream shipment/inspection data.
