# Santoni Athena Development Progress Report v0.90.2

Date: 2026-06-11

## Stage Summary: Unified General Manager Conversation Flow

Athena v0.90.2 removes the extra General Manager follow-up input from the embedded Production workspace. After the `总经理` identity is selected and the three priority risk cards are shown, all follow-up questions now use the original bottom conversation box and remain in the same chat history.

Clicking `让 Athena 下钻` on a risk card now writes the drilldown question into the main conversation stream and returns the Santoni Athena Production root-cause analysis in the same stream. This makes the user-page demo feel like one agent session instead of a dashboard plus a separate mini form.

## What Athena Can Do Now

- Show the General Manager top-three Production risk cards on the user page.
- Use the original bottom conversation box for all General Manager follow-up questions.
- Preserve conversation history for typed follow-ups and risk-card drilldowns.
- Route General Manager messages directly to the Production evidence/root-cause engine instead of the older generic `/api/chat` rendering path.
- Display executive answer, reason/evidence, suggested action, data gaps, and Skill Execution Trace in the main conversation stream.
- Preserve the read-only Production boundary: no APS write-back, no ERP write-back, no IOT write-back, no automatic scheduling change, no automatic dispatch, and no `.co` / `.cx` upload.

## What Athena Cannot Do Yet

- Athena is still not connected to live APS, ERP, IOT, CRM, ticket, or Hermes production endpoints.
- This patch does not add new live data sources or new Production reasoning skills.
- Hermes remains a governed memory/training architecture rather than a live runtime integration in the demo.

## Internal Demo Ready

- `/` customer-facing `总经理` workflow with one unified conversation box.
- Risk-card `让 Athena 下钻` actions that append to the main chat history.
- Bottom-input General Manager questions that return Production root-cause output, not the older first-version generic response.
- `/production.html` remains available for deeper internal console review.

## Future Development Plan

1. Improve the visual polish of the main General Manager chat cards.
2. Add guided executive follow-up chips below each returned answer.
3. Validate whether the one-box interaction feels natural enough for internal Santoni demo.

## Demo Boundary

This version is an interaction-flow patch. It does not change live integration, data availability, or operational write permissions.
