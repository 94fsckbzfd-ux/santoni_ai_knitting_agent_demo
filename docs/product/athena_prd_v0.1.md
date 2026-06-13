# Santoni Athena PRD v0.1

Version: v0.82.0  
Date: 2026-06-10  
Audience: Santoni customers, pilot factory management, Santoni product / implementation teams  
Status: Draft for MVP alignment

## 1. Product Definition

Santoni Athena is a digital general manager for knitting factories.

Athena is not a generic chatbot and not a simple ChatBI tool. It organizes production and service workflow, evidence, exceptions, risks, recommended confirmation actions, and local memory around the order number.

The first MVP should help a factory general manager answer one question within three minutes:

**What are the three things I should handle first today?**

## 2. Primary User

The first primary user is the factory general manager.

The first customer scenario is modeled from a Tianpai-like seamless knitting factory, but the product should be presented as a reusable Santoni customer solution. The demo should not over-emphasize a specific customer name.

## 3. Core Pain Point

Factory-site information is scattered across people, ERP, APS, IOT, quality, materials, labor, and service channels.

Management often relies on manual reporting, which makes it difficult to quickly identify:

- Which orders are at risk.
- Which quality issues may trigger rework or replenishment orders.
- Whether labor effective hours are performing normally.
- Which equipment or service issues may affect delivery.
- Which conclusions are evidence-backed and which still need data.

## 4. MVP Scope

The MVP focuses only on:

- Production
- Service risks that may affect production

The following capabilities are background or future scope for this PRD:

- Design Agent
- Style3D / CLO / AI image input
- SWS / Arachne engineering brief
- Sampling workflow beyond production-readiness context

## 5. Core MVP Loop

The MVP loop is:

1. General manager opens Athena.
2. Athena shows a management summary.
3. Athena shows three dynamic risk cards around delivery, quality/replenishment, and labor effective hours.
4. The general manager clicks "continue asking" on a risk card.
5. Athena explains root cause, evidence, affected objects, suggested owner, and data gaps.
6. Athena creates local follow-up items.
7. Final confirmation remains with the general manager.

## 6. Priority Policy

The first-screen priority is:

1. Delivery risk
2. Quality risk
3. Cost risk

Cost is usually the consequence of delivery and quality problems. For example, late delivery may trigger air freight, and quality issues may cause rework, replenishment orders, customer claims, or lost future orders.

## 7. First-Screen Experience

The first screen should be a single management page if UI complexity allows.

It should include:

- A 3-5 line management summary.
- Three dynamic risk cards.
- A Service risk section below the main risk cards.
- A local follow-up / todo section.
- A data boundary note.

The three main risk-card themes are fixed, but titles should be dynamically generated from the data:

- Delivery risk order
- Quality exception / replenishment risk
- Labor effective-hour risk

## 8. Risk Card Required Fields

Each main risk card must contain:

- Risk title
- Affected object, such as order number, quality issue, team, or process stage
- Why it matters
- Reason and evidence
- Suggested owner
- Suggested confirmation action
- Data gaps

Evidence should show 2-3 key evidence items by default. Full evidence should be available in expanded details.

## 9. Root Cause Drill-Down

Each risk card should expose a "continue asking" action. The preferred UI is a right-side analysis panel. If space is limited, the card may expand inline.

The first MVP must support these question types:

- Why is this order at risk?
- Is the issue related to machine, material, labor, process, or another factor?
- Where do the main quality problems come from?
- Which orders will be affected?
- Who should confirm next?
- What data is still missing?

The conversation entry is allowed, but it should be positioned as a context and drill-down tool, not as a generic chatbot.

## 10. Service Risk Section

Service should have an independent section because equipment problems can directly affect production delivery.

The first Service risk section should show:

- Equipment failures affecting delivery
- Repeated alarm machines
- Stopped machines

In future versions, when Athena is used by a customer's Service department, this section can also give machine-maintenance suggestions to mechanics or equipment owners.

## 11. Local Follow-Up Items

Athena should generate local follow-up items in the MVP.

The first statuses are:

- Pending confirmation
- Assigned
- Waiting for evidence
- Confirmed
- Closed
- Unable to process

Each follow-up item must be linked to a risk card.

Allowed owner roles:

- Production supervisor
- Quality supervisor
- Material supervisor
- Maintenance / equipment owner
- Team leader
- General manager confirmation

All final confirmation remains with the general manager.

## 12. Risk Levels

The MVP should use three risk levels:

- Red: must be confirmed today
- Yellow: confirm within 24-48 hours
- Gray: insufficient data; visibility only

Risk levels should help management prioritize attention. They must not imply automatic action.

## 13. Evidence Levels

Evidence level should be visible in details, not on the first card surface unless needed.

Evidence levels:

- Level 1: mock / demo evidence
- Level 2: Excel imported evidence
- Level 3: read-only database evidence
- Level 4: reviewed human confirmation

The current MVP uses Level 1 evidence as the main path.

## 14. Data Strategy

The first MVP uses mock data as the primary path.

Future paths:

- Excel import simulation
- Read-only ERP / APS / IOT database integration
- Reviewed human confirmation
- Hermes memory and playbook promotion

When real data is missing, Athena should not hide the issue and should not force a confident guess. It should show:

- What cannot be determined
- Which data is missing
- What Athena could answer after the data is available

## 15. Permission Boundary

Athena can:

- Show risks
- Explain reasons and evidence
- Suggest who should confirm
- Suggest confirmation actions
- Generate local follow-up items

Athena must not:

- Replace ERP / APS / IOT
- Automatically modify scheduling
- Automatically dispatch service work
- Directly evaluate employee performance
- Give a certain conclusion when evidence is insufficient

Athena does not replace the general manager's decision authority. It replaces a large amount of manual information collection, follow-up questioning, cross-checking, and reminder work so the general manager can see facts, risks, and responsibility points faster.

## 16. MVP Demo Story

Initial demo story:

An order's delivery risk increases. Athena detects that the risk may be connected to quality replenishment, low labor effective hours, and Service-related machine stoppage risk. Athena then shows today's three priorities, evidence, suggested owner confirmation actions, and local follow-up items.

More demo stories can be added after the product implementation becomes stable.

## 17. Success Criteria

The MVP is successful if a general manager can understand within three minutes:

- The top three things to handle today
- Why they matter
- Which evidence supports them
- Who should confirm next
- Which data is still missing

## 18. Open Questions For Later PRD Versions

- Which real ERP order fields can be provided?
- How much historical labor effective-hour data can be used as baseline?
- Which quality records can be joined to order number and process stage?
- Which Service events can be joined to delivery-impact risk?
- What is the customer-approved definition of effective hours?
- How should Hermes promotion work for customer-specific memory?
