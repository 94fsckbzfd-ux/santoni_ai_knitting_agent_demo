# AI Knitting Agent Demo

Santoni AI Knitting Agent MVP demo.

This project is designed around one shared Agent Core with two product entries:

- Web demo: lightweight, no long-term memory, suitable for free trials and sales demos.
- Feishu agent: workflow-integrated assistant with identity, memory, task tracking, and dispatch notifications.

## MVP Scope

The current demo includes four local review surfaces:

1. Design Intake Structuring Console
   - Structured Design Request / Style3D-CLO-AI-image-TP intake
   - Mock engineering brief candidate for SWS/Arachne review
   - Manufacturability check with explicit risks and blocked actions
   - Sampling feedback capture, revision suggestion, and readiness-style gate for schema review
   - Evidence log, tool-interface contract, and KPI log for business review
   - This is a Design Agent data-structuring testbench, not the full Athena MVP and not a manual design-exhaustion tool

2. Production Operations Console
   - Mock order intake, ERP sync, APS scheduling, IOT execution, service escalation candidate, and garment output monitoring
   - Top-down production site flow for orders, scheduling, machines, and garment output, backed by 人机料法环测 evidence
   - APS/IOT page-research field mapping and read-only adapter contract for future production data integration
   - Management-facing KPI log for OEE, downtime, order delay risk, material risk, labor efficiency, quality risk, and waste/cost opportunity
   - Read-only adapter contracts only; no APS/IOT login, no .co/.cx upload, no schedule confirmation, no machine control, and no real service ticket creation

3. Designer workflow
   - Natural language design brief
   - Translation Agent converts desire into structured knitting requirements
   - Digital Twin Agent simulates SWS 3D output, process package, cost, time, yield, and machine recommendation
   - Optional reference image upload is routed through a mock Image Understanding Agent

4. Customer equipment engineer workflow
   - Natural language installation or maintenance request
   - Service Dispatch Agent collects missing information
   - Agent attempts safe online assistance first, then creates and dispatches a service ticket after confirmation when onsite support is needed
   - Output includes priority, assigned Santoni service engineer, spare parts, ETA, and dispatch rationale
   - Optional alarm, component, or defect image upload is routed through a mock Image Understanding Agent

All business data is mocked in phase 1. The system should remain ready to replace mock data with real SWS APIs, APS data, DPP data, device data, and service ticket APIs later.

## Project Layout

```text
AI_Knitting_Agent_Demo/
  docs/                  Product and architecture notes
  src/
    agent_core/          Main Agent, sub-agents, workflows, shared models
    mock_data/           Mock customers, machines, engineers, parts, rules
    web_app/             Web chat entry
    feishu_app/          Feishu bot entry
  scripts/               Local utility scripts
  tests/                 Unit and workflow tests
```

## Development Principle

Main Agent is the orchestrator. It identifies role, intent, workflow state, and routes tasks to sub-agents. Sub-agents perform domain-specific work and return structured results.

## Versioning

Current version: `v0.25.3`

Version rule: `vMajor.Feature.Patch`

- Patch updates change the third number.
- New features change the second number.
- Major iterations change the first number.

The customer-facing Web demo is available at `/`. The developer/debugging page is available at `/developer.html`.

All current web pages include a Chinese / English language switch. The selected language is stored in browser local storage and follows the user across the demo pages.

The Design Intake Structuring Console is available at `/athena-mvp.html`. It is deliberately kept as a data-structuring testbench rather than a chatbot, a full Athena MVP, or a manual design-exhaustion tool. The local API exposes `/api/athena-mvp/template` and `/api/athena-mvp/run`.

The Production Operations Console is available at `/production.html`. It is a management dashboard for order intake -> ERP input -> APS scheduling -> IOT execution -> production/service escalation -> garment output. It defaults to Chinese customer-facing labels and now presents the site flow as order, scheduling, machine, and garment sections while keeping English available through the language switch. The console also includes Santoni Athena as a read-only production insight agent for KPI root-cause questions such as scrap rate, OEE, downtime, material risk, and order delay. The current production snapshot is static local mock data from `src/mock_data/production_operations.mock.json`, not dynamic APS/IOT web scraping. Future live integration should use direct APS/IOT database views and/or formal read-only APIs, not browser scraping. The workflow spine is the unique `order_id` / 订单号, which joins order intake, ERP, APS, IOT, production/service candidates, and garment output. The local API exposes `/api/production/template`, `/api/production/overview`, `/api/production/analyze`, `/api/production/adapter-contract`, and `/api/production/chatbi`.

For lock-machine activation-password tasks on the customer page, the UI prompts for platform username and password only when the activation task is detected. Credentials are sent only with that request and are kept in browser memory for the current session.

## Agent Operating Model

The architecture now reserves interfaces for five production-agent capabilities:

- Goal / Success Criteria
- State
- Guardrails
- Handoff
- Evaluation

The web demo shows their current status in `Agent Model Progress`, powered by `/api/operating-model`.

## Project Docs

The developer page links to `/docs.html`, which shows:

- Implemented and planned feature status
- Confirmed project decisions
- Uncertain or pending assumptions
- Designer state flow
- Service state flow
- Next product decisions

The developer page also shows a compact Latest Changelog preview sourced from `/changelog.html`, so testers can verify the current iteration without leaving the debug workflow.

The demo links to `/athena-mvp.html`, which shows the Design Agent input-structuring loop: design/Style3D/CLO/AI-image/TP input -> normalized design_request and source_asset objects -> engineering brief candidate -> manufacturability check -> sampling feedback -> revision suggestion -> evidence and KPI logs. Real Style3D/CLO/SWS/Arachne adapters are not connected yet.

The demo links to `/production.html`, which shows the Production Operations loop with mock APS/IOT data, APS/IOT field mapping, order/scheduling/machine/garment site-flow sections, Santoni Athena root-cause analysis, optimization signals, service request candidates, evidence logs, and KPI logs.

The APS/IOT production adapter mapping note is stored at `docs/aps_iot_production_adapter_mapping.md`. It documents observed APS/IOT source pages and normalized read-only objects without storing credentials.

The demo also links to `/service-cases.html`, a Service Manager Console. It shows service case readiness, Excel draft cases, review status, customer visibility, online troubleshooting steps, safety warnings, dispatch triggers, editable case knowledge, diff view, and future CRM/ticket handoff payload previews.

The demo links to `/guide.html`, which explains the Agent scope, usage method, current features, limitations, and test suggestions for business users.

## Excel Service Case Import

Use the importer to convert a monthly service Excel file into draft cases for human review:

```powershell
python scripts/import_service_cases.py .codex_tmp/service_cases_20260418_20260518.xlsx
```

The default output is:

```text
src/mock_data/service_cases.draft_import.json
```

Draft cases are shown in the Service Case Library as `draft_needs_review`. They are not used by the Service Agent for customer-facing answers until a reviewer marks them `approved`.

## Service Case Approval

Use `/service-cases.html` to review and edit cases. Service managers can update keywords, online troubleshooting steps, safety warnings, recommended parts, dispatch triggers, review notes, and customer visibility. The console keeps imported/mock source data separate from reviewer edits so the diff remains visible.

Use the console to mark cases as:

- `approved`: visible to customer-facing Service Agent matching when the case is online-solvable.
- `needs_changes`: kept for review but blocked from customer-facing matching.
- `internal_only`: kept for internal reference and blocked from customer-facing matching.
- `draft_needs_review`: default Excel draft state.

Review decisions are saved to:

```text
src/mock_data/service_case_reviews.json
```

## Export Test Logs

Use `Export Test Log` in the Web demo to download the current test session as JSON.

The export includes:

- App version
- Runtime status
- Selected role
- User messages
- Attachment metadata
- Raw Agent responses

Image file contents are not exported; only image metadata is included.

## Bilingual Behavior

The MVP supports Chinese and English demo interactions.

- Chinese input returns Chinese summaries, follow-up questions, and mock business results.
- English input returns English summaries, follow-up questions, and mock business results.
- Role routing has priority over keyword routing, so service issues like "yarn tension alarm" remain in the service workflow when the user role is Equipment Engineer.

## GPT Text Understanding

The demo can use GPT for structured text understanding through the OpenAI Responses API, or DeepSeek through its OpenAI-compatible Chat Completions API.

Set environment variables before running:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
$env:OPENAI_MODEL="gpt-4o-mini"
python scripts/run_web_demo.py
```

Or create a local `.env` file in the project root:

```text
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

For DeepSeek, use:

```text
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_deepseek_key_here
DEEPSEEK_MODEL=deepseek-chat
```

Then run:

```powershell
python scripts/run_web_demo.py
```

`.env` is ignored by git and should stay local.

If the browser keeps hitting an old backend, stop stale demo processes first:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/stop_web_demo.ps1
python scripts/run_web_demo.py
```

If the selected provider key is not set, the demo automatically uses a local rule-based fallback parser. This keeps the demo usable for offline review, but results will be less intelligent than LLM-backed parsing.

The GPT layer extracts:

- `DesignBrief` for Designer workflow
- `ServiceIssue` for Equipment Engineer workflow

Both are displayed in the Web UI as `Text Understanding` / `文本理解`.

The downstream sub-agents also use GPT when available:

- Translation Agent generates the knitting recommendation
- Digital Twin Agent generates the simulated SWS and sampling plan
- Service Dispatch Agent generates the ticket and dispatch plan

Check these fields in the UI:

- `parser_status`: whether the text understanding used GPT or fallback
- `reasoning_status`: whether the recommendation/dispatch generation used an LLM or fallback

## Image Input

The Web demo supports optional image upload.

Phase 1 does not perform real image recognition. Uploaded images are passed as attachments to the Agent Core, then handled by a mock Image Understanding Agent. This reserves the contract for future GPT Vision integration.

## Run The Web Demo

```powershell
python scripts/run_web_demo.py
```

Then open:

```text
http://127.0.0.1:8765
```

To run on another port:

```powershell
python scripts/run_web_demo.py 8766
```
