# Santoni Athena GM First Screen Hierarchy v0.110.0

## Purpose

Athena v0.110.0 improves the customer-facing General Manager page so the first screen reads as a management decision workspace instead of a development dashboard.

## User-Page Hierarchy

The General Manager mode now follows this hierarchy:

1. Daily KPI dashboard
2. Today's top three hard risks
3. Evidence Review Queue
4. Service / equipment risk candidates
5. Original chat stream for all drilldowns and follow-up questions

## Interaction Rule

Risk-card and evidence-review drilldowns stay in the original chat stream. Athena answers with a compact management summary first:

- conclusion
- what evidence supports it
- who should confirm
- next action

Detailed evidence, field sources, sanity flags, and read-only boundaries stay in expandable detail areas.

## User-Page Exclusions

The customer-facing page should not show Internal Demo Mode, development progress, raw payloads, raw JSON, version development notes, or long technical field lists.

Those remain appropriate for `/developer.html`, `/production.html`, docs, and Codex completion reports.
