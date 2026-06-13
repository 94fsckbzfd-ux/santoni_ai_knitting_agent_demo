# Santoni Athena Development Progress Report v0.91.0

Date: 2026-06-11

## Stage Summary: General Manager Follow-up Loop Demo

Athena v0.91.0 moves the customer-facing General Manager workflow from "show today's three priorities" toward "track today's three priorities." The `/` user page now lets the General Manager generate local follow-up items from the three Production risk cards, review their owner/evidence/status, update status, and continue asking Athena about the same item.

This keeps the demo workflow-native: risk card -> local follow-up -> owner confirmation -> evidence check -> continued root-cause question. All follow-up changes remain metadata-only local records and do not write APS, ERP, IOT, ticket systems, Hermes memory, or machine controls.

## What Athena Can Do Now

- Show the General Manager top-three Production risk cards on the user page.
- Generate a local follow-up item from each risk card.
- Display local follow-up status, owner role, linked risk card, evidence refs, expected evidence, and review timing.
- Update follow-up status through the existing metadata-only `/api/production/follow-up/review` contract.
- Continue asking Athena from a follow-up item through `/api/production/chatbi` while preserving the Production evidence workflow.
- Keep Skill Execution Trace available in follow-up drilldowns so internal reviewers can see which Athena skill checked the evidence.
- Preserve the read-only Production boundary: no APS write-back, no ERP write-back, no IOT write-back, no automatic scheduling change, no automatic dispatch, and no `.co` / `.cx` upload.

## What Athena Cannot Do Yet

- Follow-up items are still local demo metadata, not real APS/ERP/IOT workflow tasks.
- Athena cannot notify real owners, assign work in a customer system, or close an issue with real evidence automatically.
- Hermes remains a governed memory/training architecture rather than a live runtime integration in the demo.

## Internal Demo Ready

- `/` customer-facing `总经理` workflow with top-three priorities and local follow-up loop.
- Risk-card `生成跟进项` actions that create visible local todos.
- Follow-up status controls for assigned, waiting evidence, confirmed, and closed.
- Follow-up `继续追问` actions that ask Santoni Athena to drill down with the same evidence chain.

## Future Development Plan

1. Add a more guided executive story around one complete follow-up from risk detection to evidence closure.
2. Decide whether follow-up status should be persisted per session, per tenant, or per customer workspace after real Hermes is connected.
3. Validate with internal users whether the local follow-up loop feels like a General Manager workflow rather than a dashboard control.

## Demo Boundary

This version is a local follow-up loop demo. It does not create real work orders, dispatch service, update schedules, publish Hermes memory, or store raw customer data.
