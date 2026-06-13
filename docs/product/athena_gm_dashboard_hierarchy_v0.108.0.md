# Santoni Athena GM Dashboard Hierarchy v0.108.0

Date: 2026-06-12

## Summary

Athena v0.108.0 improves the General Manager user experience without changing the read-only production boundary. The user page now treats the dashboard as the daily operating surface and Athena drilldown as the explanation layer.

This aligns with the PRD first-screen requirement: a single management page with daily KPI overview, management summary, top-three risk cards, Service risk, local follow-up, and data boundary.

## What Changed

- Added a General Manager daily KPI dashboard on the user page.
- Kept "today's top three priorities" below the dashboard as the decision focus.
- Reduced drilldown output from many separate modules into one compact Athena answer.
- Moved full evidence, data gaps, read-only boundary, and process details into an expandable section.
- Preserved original chat flow: risk-card and story drilldowns still appear in the same conversation history.

## Dashboard KPIs

The user-page dashboard now shows:

- Delivery risk.
- Scheduling status.
- Plan completion.
- Equipment risk.
- Service confirmation candidates.
- Data confidence.

These are management-facing indicators, not automatic action triggers.

## Drilldown Display Policy

Default view shows only:

- Conclusion.
- What Athena checked.
- What Athena found.
- Evidence support.
- Suggested confirmation owner.

Expanded detail shows:

- Evidence level.
- Full checked objects.
- Key evidence.
- What cannot be concluded.
- Read-only boundary.

## Still Read-Only

Athena still does not write APS, ERP, IOT, or Hermes. It does not change schedules, upload `.co` / `.cx`, control machines, dispatch Service, or create real tickets.

## Why This Matters

This version makes Athena feel less like a long analysis report and more like a daily General Manager cockpit with an intelligent assistant behind it. The dashboard supports quick monitoring; Athena explains root cause only when the manager asks.

## Next UX Question

The next validation question is whether the dashboard indicators are the right daily operating KPIs for a factory General Manager, or whether the first row should be simplified further for customer demos.
