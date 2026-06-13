# Santoni Athena Demo Experience Report v0.96.0

Date: 2026-06-11

## What Changed In This Stage

- Polished the customer-facing General Manager workspace so the first screen focuses on management decisions, not project status.
- Removed version-style summary content from the user page and replaced it with management-facing indicators.
- Added a `verification_process` contract to Santoni Athena production drilldown responses.
- Updated user-page drilldown answers to show what Athena checked, what it found, evidence level, what it still cannot conclude, and who should confirm next.
- Kept Internal Demo Mode and development-progress content out of the user page.

## What Athena Can Do Now

- Show the General Manager today's top three production priorities.
- Show Service / equipment risk as a confirmation candidate when it may affect delivery.
- Let the General Manager drill down from a risk card into the original chat flow.
- Explain the verification process in management language instead of raw debug trace.
- Generate and update local follow-up items without writing APS, ERP, IOT, Service, or machine systems.

## What Athena Cannot Do Yet

- It cannot connect to live ERP, APS, IOT, Service, or warehouse databases.
- It cannot automatically change schedules, dispatch service, control machines, or upload `.co` / `.cx` files.
- It cannot make final root-cause claims when evidence is incomplete.
- It cannot replace the General Manager's final confirmation.

## Internal Demo Ready

The following can be shown internally:

1. Select General Manager on `/`.
2. Review today's top three priorities.
3. Review Service risk candidates.
4. Open evidence details.
5. Ask Athena to drill down in the original chat.
6. Show Athena's verification process.
7. Generate a local follow-up item and update its status.

## What The User Page Should Not Show

- Internal Demo Mode
- Development progress or release planning
- Raw JSON or payload
- Internal schema names
- Full technical field lists outside evidence detail
- Claims that are not supported by available evidence

## Next Stage Recommendation

- Build a stable internal demo scenario pack for repeatable presentation.
- Add a one-click demo reset so the General Manager story can be replayed.
- Improve the Service risk story after real maintenance and IOT records are available.
- Prepare real-data import contracts for the next customer data round.

