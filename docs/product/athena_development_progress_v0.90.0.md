# Santoni Athena Development Progress Report v0.90.0

Date: 2026-06-11

## Stage Summary

Athena has moved from a production-console page demo into a user-page general-manager agent workflow. The customer-facing `/` page now has an explicit `总经理` identity button. After this role is selected, Athena opens an embedded Production workspace with today's three priority risk cards and same-page root-cause drilldown interaction.

This version keeps `/production.html` as the richer internal Production Console, but the primary demo path is now: choose `总经理` on `/`, review the top-three production priorities, then ask Santoni Athena to investigate the root cause without leaving the user page.

## What Athena Can Do Now

- Open a general-manager Production workspace directly from the customer-facing home page.
- Load the same evidence-backed management priority brief used by the Production Console.
- Present three structured risk cards with risk theme, level, affected objects, suggested owner, suggested action, skill usage, and evidence refs.
- Let the user click a risk card and send its drilldown question into Santoni Athena root-cause analysis.
- Let the user type follow-up production questions in the same workspace.
- Show Athena's process through root-cause outputs and `Skill Execution Trace` instead of only returning a static KPI answer.
- Keep the Production Console, Production Skill Registry, and GM Demo Mode available for deeper internal review.
- Preserve the read-only boundary: no APS write-back, no ERP write-back, no IOT write-back, no automatic scheduling change, no automatic dispatch, and no `.co` / `.cx` upload.

## What Athena Cannot Do Yet

- Athena is not connected to live APS, ERP, IOT, CRM, ticket, or Hermes production endpoints.
- The user-page workspace still consumes the current local Production API snapshot; it does not stream live factory data.
- Athena cannot prove full order-to-garment root cause without downstream production-stage, quality-inspection, labor, material-demand, shipment, and cost tables.
- Athena cannot replace the general manager's decision or the production owner's confirmation.
- Athena cannot modify schedules, release orders, control machines, or create real service tickets.
- Hermes is still shown as governance and memory architecture; this version does not demonstrate live Hermes execution.

## Internal Demo Ready

- `/` customer-facing General Manager identity workflow.
- Embedded top-three risk cards for "今天我应该先盯哪三件事？".
- Same-page Santoni Athena drilldown for risk-card questions and free-form production follow-up.
- `/production.html` GM Demo Mode first screen for the more complete internal dashboard.
- `/api/production/skills` Production Skill Registry for explaining Athena's skill layer.
- `Skill Execution Trace` as the internal proof that Athena is using structured skills and evidence, not just ChatBI-style metric lookup.

## Future Development Plan

1. Validate whether the `/` General Manager workspace feels demo-ready for Santoni internal stakeholders.
2. Improve the user-page visual storytelling so the first screen feels like an agent session rather than a web dashboard.
3. Add a small set of guided executive questions with evidence-backed expected behavior.
4. Add real quality inspection and replenishment-order data so quality/scrap analysis can move beyond current contract coverage.
5. Add labor effective-hour baseline and team assignment history for stronger labor-efficiency reasoning.
6. Define direct read-only database/API adapters for APS and IOT instead of browser scraping.
7. Connect closed follow-up outcomes into Hermes memory events only after human review and evidence acceptance.

## Demo Boundary

This version is suitable for internal Santoni demonstration of the Athena interaction model: a general manager chooses an identity, sees the production priorities, and asks Athena to investigate root cause from structured evidence. It is not yet suitable as a live customer production-control system because all external integration remains read-only or file-export based, and all operational actions require human confirmation outside Athena.
