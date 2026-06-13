# AI Knitting Agent Demo

Santoni AI Knitting Agent MVP demo.

This project is designed around one shared Agent Core with two product entries:

- Web demo: lightweight, no long-term memory, suitable for free trials and sales demos.
- Feishu agent: workflow-integrated assistant with identity, memory, task tracking, and dispatch notifications.

## MVP Scope

The current demo includes six local review surfaces:

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

3. Hermes Integration Console
   - Local adapter contract for Athena runtime, project memory, tool orchestration, and self-evolution planning
   - Mock memory events, evolution candidates, development suggestions, tool registry candidates, evidence logs, and KPI logs
   - Proposal-only development loop with human review gates
   - No live Hermes endpoint connection yet, no credentials stored, no production writeback, and no automatic code modification

4. Athena Automatic Training Console
   - Automatic local evaluation loop for Tianpai general-manager training tasks
   - Reads the structured Tianpai training pack, runs evidence/governance/data-gap checks, and emits Hermes-style JSON results
   - Shows task status, capability progress, Codex patch/data queue, next training tasks, evidence logs, and KPI logs
   - Not model-weight fine tuning and not a live Hermes runner yet; real Hermes execution and major automatic code changes remain behind confirmation

5. Designer workflow
   - Natural language design brief
   - Translation Agent converts desire into structured knitting requirements
   - Digital Twin Agent simulates SWS 3D output, process package, cost, time, yield, and machine recommendation
   - Optional reference image upload is routed through a mock Image Understanding Agent

6. Customer equipment engineer workflow
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

Current version: `v0.113.3`

Version rule: `vMajor.Feature.Patch`

- Patch updates change the third number.
- New features change the second number.
- Major iterations change the first number.

The customer-facing Web demo is available at `/`. The developer/debugging page is available at `/developer.html`.

The customer-facing home page and developer/debug page require users to select an identity before effective chat. Current identity buttons are 总经理, Service Engineer, and Design Development. The selected identity is sent as the request role for workflow routing and future permission management; natural-language identity detection remains only a fallback inside the backend.

The current Athena structure map is rendered at `docs/athena_structure_v0.113.0.png`. Re-run `python scripts/render_athena_structure_png.py` after architecture changes to refresh the PNG.

Daily development smoke check: run `python scripts/smoke_check.py` after routine edits. It performs compileall, scans the customer-facing Production surface plus General Manager priority / stable-demo-story API text for mojibake / malformed HTML, and runs the high-signal smoke tests. Keep the full harness for release validation and GitHub backup.

Athena PRD v0.1 is available at `docs/product/athena_prd_v0.1.md` and mirrored as a customer-facing section inside `docs/Athena.html`.

The customer-facing page script is scoped separately from the shared language switch so identity buttons and status updates do not fail because of shared browser globals.

All current web pages include a Chinese / English language switch. The selected language is stored in browser local storage and follows the user across the demo pages.

The Design Intake Structuring Console is available at `/athena-mvp.html`. It is deliberately kept as a data-structuring testbench rather than a chatbot, a full Athena MVP, or a manual design-exhaustion tool. The local API exposes `/api/athena-mvp/template` and `/api/athena-mvp/run`.

Athena's core value proposition is now recorded in `docs/Athena.html`: workflow-native onsite workforce, management decision-loop agent, and Hermes-governed self-evolution. These three capabilities are the product guardrail for future work: Athena should join customer workflow objects, turn management questions into evidence-backed follow-up loops, and learn only through reviewed memory events, playbooks, and regression cases.

The customer-facing home page `/` is now the primary general-manager demo path. Selecting the `总经理` identity opens an embedded Santoni Athena Production workspace with KPI dashboard, today's top-three hard-risk cards, Evidence Review Queue, Service/equipment risk candidates, and same-page root-cause drilldown in the original chat stream. `/production.html` remains the richer internal Production Console for reviewing the full management dashboard, data-source snapshots, follow-up contracts, skill registry, and PRD/audit panels. Production analysis still follows the order-intake -> ERP input -> APS scheduling -> IOT execution -> production/service escalation -> garment-output workflow. The first-screen General Manager, Evidence Review, and Service Risk cards include drill-down actions that send structured evidence-scoped questions into Santoni Athena. The customer-facing home page also routes production-manager questions about orders, delivery, scheduling, scrap, downtime, OEE, materials, and root cause into the same `production_athena` analysis instead of the older Designer/Service clarification path. The current production snapshot is static local mock data from `src/mock_data/production_operations.mock.json`, not dynamic APS/IOT web scraping. Future live integration should use direct APS/IOT database views and/or formal read-only APIs, not browser scraping. The workflow spine is the unique `order_id` / 订单号, which joins order intake, ERP, APS, IOT, production/service candidates, and garment output. The local API exposes `/api/production/template`, `/api/production/overview`, `/api/production/skills`, `/api/production/priority-brief`, `/api/production/evidence-review`, `/api/production/follow-up`, `/api/production/follow-up/review`, `/api/production/analyze`, `/api/production/adapter-contract`, and `/api/production/chatbi`.

Tianpai Material Risk / Data Readiness v1 is now available inside the Production workflow. Athena consumes the provided yarn inventory export as aggregate material evidence only: raw inventory rows are not copied into the repo. The material object records yarn inventory structure, batch / supplier / color / twist distribution, zero and negative balance review signals, Yarn_Product field mapping, and future join blockers for ERP, APS, BOM demand, and quality records. The local API exposes `/api/production/material-risk`, `/api/production/data-readiness`, and `/api/production/question-bank`. The General Manager Question Bank is still a hypothesis set until Product Owner, Agnes, Tianpai onsite roles, and customer management verify it. Tianpai ERP order and split-delivery data are not available yet, so Athena can prepare material and data-readiness evidence but must not claim full order-level delivery root cause.

Chinese 璐ф湡 / 骞冲潎璐ф湡 questions now route to the Production Athena order-delay analysis. With current mock data Athena can summarize backlog days-to-due, but a real recent-week average lead time still needs order-created dates and actual delivery records.

Production Athena management answers use a fixed structure: conclusion, reason/evidence, risk, recommendation, and data gap. The first high-frequency branches cover delivery risk, low yield/scrap, machine bottleneck, material risk, and current data limitations.

Production Object Model and Management Priority Engine v1 are now available in the Production workflow. Athena exposes `production_object_model` for order, style, machine, process_stage, production_signal, evidence, decision, action, follow_up, and memory_event contracts. It also exposes `management_priority_brief`, which ranks the general manager's first-screen hard risks with delivery risk first, and `evidence_review_queue`, which separates data/status reconciliation candidates from confirmed risks. In v0.110.0 delivery-risk evidence records explicit risk drivers and the user page presents evidence-review candidates below hard risks. Cost remains a consequence metric until purchasing, labor, rework, and freight records are connected.

Production first-screen management summary now follows the PRD 3-5 line requirement. The `management_priority_brief.daily_brief` object includes bilingual summary lines for actual APS/ERP evidence coverage, delivery, equipment/material/cost confirmation, and data boundary, and `/production.html` renders them above the three risk cards.

Production first-screen risk cards now follow the PRD detail contract: each card shows risk level, affected objects, why it matters, key evidence, suggested owner, suggested confirmation action, and an expandable detail area for full evidence, evidence level, and data gaps. Local follow-up items also show the linked risk-card ID so the decision loop stays traceable.

Production local follow-up items now follow the PRD status lifecycle: pending confirmation, assigned, waiting for evidence, confirmed, closed, and unable to process. These controls write only local metadata review records and remain blocked from APS, IOT, ticket systems, machine control, and Hermes memory promotion.

Decision Loop / Follow-up Engine v1 is now available in the Production workflow. Athena converts priority action candidates into `decision_loop` objects with decision, action, follow_up, owner, review time, expected evidence, evidence status, closure gate, recurrence watch, and Hermes memory-event candidates. Production Console can simulate pending-confirmation / assigned / waiting-evidence / confirmed / closed / unable-to-process status updates through metadata-only local review records in `src/mock_data/production_follow_up_reviews.json`; it does not write APS, IOT, real service tickets, or Hermes memory.

Production permission boundary v1 is now available in the Production workflow. Athena exposes a `permission_boundary` object and `/production.html` panel that make the GM final-confirmation rule explicit: Athena can show risks, explain reasons and evidence, suggest owners/actions, and create local follow-up items, but it cannot replace ERP/APS/IOT, modify schedules, dispatch service automatically, upload `.co/.cx` files, control machines, score individual employees, force conclusions when evidence is insufficient, or replace the general manager's decision.

Production MVP Demo Story v1 is now available in the Production workflow. Athena exposes an `mvp_demo_story` object and `/production.html` panel that turns PRD section 16 into a three-minute customer-management story: an order delivery risk is connected to quality/replenishment, labor effective-hour, and service/machine-stoppage signals, then converted into evidence-backed owner-confirmation actions, local follow-up items, and the GM final-confirmation boundary.

Production MVP Success Check v1 is now available in the Production workflow. Athena exposes an `mvp_success_check` object and `/production.html` panel that evaluates PRD section 17 against the current snapshot: top three priorities, why they matter, supporting evidence, next confirmation owner, missing data visibility, and the remaining Level 1 mock-evidence boundary.

Production PRD Alignment Audit v1 is now available in the Production workflow. Athena exposes a `prd_alignment_audit` object and `/production.html` panel that map PRD sections 1-18 to implemented objects, evidence refs, remaining gaps, and the boundary between local mock MVP coverage and live customer deployment readiness.

Tianpai APS/ERP Export Adapter v1 is available as the actual-data foundation introduced in v0.81.0 and consumed by the v0.82.0 console snapshot. Athena reads external no-header CSV exports through `TianpaiApsErpExportAdapter`, uses the `表字段` DDL field order for Produce_Order, Weaving_Part_Order, Planned_Task, Manual_Machine_Production, Style_Component, Style_Sku, and T_Machine_Info, and exposes `/api/production/tianpai-aps-export` with standard object counts, join quality, missing fields, unmatched records, capability boundaries, and blocked write actions. Raw customer CSV files remain outside the repo.

Production Mock + Actual Snapshot v1 is now available in the Production Console. Athena exposes an `actual_data_snapshot` object and `/production.html` panel showing the current data source as Mock / Tianpai APS Export, with actual-data KPIs for total orders, near-due orders, scheduled and unscheduled weaving part orders, plan completion, report completion, machine plan load, and machine/style cylinder-gauge mismatch candidates.

Production Actual-Data Management Q&A v1 is now available in Santoni Athena on `/production.html`. For supported management questions, Athena uses the Tianpai APS/ERP export before falling back to mock analysis and returns evidence chains with order, weaving part order, planned task, machine, evidence refs, and field source. The first actual-data branches cover delivery risk, unscheduled weaving part orders, machine plan load, machine/style spec mismatch, and planned-vs-reported quantity gaps.

Production GM First-Screen Priority Workflow v1 is now available. The `/production.html` general-manager brief now prefers Tianpai APS/ERP export evidence when generating today's top three risk cards, then falls back to the mock production snapshot only when actual evidence is unavailable. Each card records risk theme, risk level, affected objects, actual evidence chain, field source, suggested owner, suggested action, data gaps, and internal-demo readiness.

Risk Card Drilldown + Follow-up Action Contract v1 is now available. Each Production risk card carries a drilldown question into Santoni Athena root-cause analysis and produces a local metadata-only follow-up candidate linked to the original risk card, evidence refs, field source, and evidence chain. These follow-ups do not write APS, ERP, IOT, service tickets, or machine controls.

User-page General Manager Agent Workspace v1 is now available. The `/` page exposes a `总经理` identity button that opens the Production priority brief and Santoni Athena drilldown panel in the same customer-facing flow, while `/production.html` keeps data-source snapshots, PRD audits, and raw adapter details for internal review.

Unified General Manager Conversation Flow v1 is now available. After the `/` page shows the top-three Production risk cards, all General Manager follow-up questions use the original bottom chat box. Risk-card `让 Athena 下钻` actions also append the question and answer to the same chat history, so the demo behaves as one Athena conversation rather than a dashboard with a separate follow-up form.

General Manager Follow-up Loop Demo v1 is now available on `/`. Each top-three Production risk card can generate a local follow-up todo with owner role, linked risk card, evidence refs, expected evidence, review time, and status. The General Manager can update the todo status and continue asking Athena from that todo, while the review update remains local metadata only and never writes APS, ERP, IOT, ticket systems, Hermes memory, or machine controls.

Developer General Manager Flow Parity v1 is now available. On `/developer.html`, selecting `总经理` automatically loads the same three-priority Production brief, and the original developer test input routes General Manager follow-up questions through `/api/production/chatbi` instead of the older generic `/api/chat` path. This keeps the customer page and developer/debug page aligned while still exposing raw payloads and export logs for testing.

GM Demo Mode UI v1 remains available. `/production.html` opens with the general manager's three-minute question and keeps data-source snapshots, PRD audits, and raw adapter details below the primary demo experience.

Athena Skill Registry v1 is now available. Production risk cards are linked to explicit skills: `gm_daily_brief_skill`, `delivery_risk_skill`, `machine_fit_skill`, `material_constraint_skill`, `bottleneck_detection_skill`, `quality_or_scrap_skill`, `service_escalation_skill`, and `follow_up_action_skill`. The registry is visible through `/api/production/skills` and remains read-only.

Skill Execution Trace v1 is now available. Risk-card details and Santoni Athena drilldown responses show which skill was used, what Athena checked, which objects and evidence refs were inspected, the evidence level, result summary, and data gaps. This trace is designed for internal demonstration rather than raw debugging.

Athena GM Decision UI Compression v0.111.0, Local Decision Follow-up Board v0.112.0, and Daily Brief Narrative v0.113.0 are available at `docs/product/athena_gm_decision_ui_compression_v0.111.0.md`, `docs/product/athena_local_decision_follow_up_board_v0.112.0.md`, and `docs/product/athena_daily_brief_narrative_v0.113.0.md`. They document how Athena compresses General Manager drilldowns, turns hard risk / evidence review / Service risk cards into local metadata-only follow-ups, and generates a three-minute daily brief without exposing raw JSON or writing external systems.

GM First Screen Hierarchy Polish v0.113.0 keeps the customer-facing General Manager page focused on the KPI dashboard, today's three priorities, Service risk candidates, evidence review, local follow-up items, and same-page Santoni Athena drilldown while removing raw payload-style output from the user experience.

GM Dashboard Hotfix v0.113.1 restores the customer-facing General Manager dashboard load path, adds the missing user-page percent formatter, improves the dashboard error message, and cleans the first-screen Daily Brief / risk-card Chinese wording used in the Production view.

Daily Smoke Check v0.113.2 adds `scripts/smoke_check.py` so normal edits can catch compile errors, critical-page mojibake, malformed Production HTML, and high-risk Production regression failures without running the full harness every time.

Stable Demo Story Pack Encoding Guard v0.113.3 fixes Chinese mojibake in the Production Console stable demo story pack and extends `scripts/smoke_check.py` to scan that API object so customer-visible story-pack text is covered by the fast daily check.

Production Console now includes a Stable General Manager Demo Story Pack. The pack provides three repeatable internal-demo stories: a real APS/ERP delivery-risk story, a real APS/ERP machine/style-fit story, and a hybrid service-impact story that combines real scheduling context with clearly labeled mock IOT/Service evidence. Each story includes suggested questions, evidence refs, field sources, mock supplements, data gaps, suggested owner, and one-click Santoni Athena drilldown.

The Hermes Integration Console is available at `/hermes.html`. It is the first local contract for connecting Athena to Hermes as runtime, project memory, tool orchestration, development-suggestion, and organization-memory playbook layer. It is not connected to a live Hermes endpoint yet. The local API exposes `/api/hermes/template`, `/api/hermes/overview`, `/api/hermes/playbook`, `/api/hermes/suggest`, and `/api/hermes/playbook/review`.

Hermes memory events are governed with `scope`, `tenant_id`, `factory_id`, `source`, `retention_policy`, `sensitivity_level`, and `promotion_status`. Current demo memory uses product/domain scope with null tenant and factory IDs; future customer accounts should use tenant/session scope and must not promote tenant memory into global Santoni domain memory without review.

Organization Memory / Playbook Engine v1 is now available inside the Hermes workflow. It converts Production `decision_loop` follow-ups into `organization_memory_playbook` candidates with promotion gates, memory-event candidates, regression-case candidates, and metadata-only local review records in `src/mock_data/hermes_playbook_reviews.json`. Approval is blocked until follow-up closure and accepted evidence are available; no live Hermes memory, raw customer files, credentials, APS/IOT data, or code changes are written.

Playbook Regression Queue v1 is now available through the Training workflow. Approved Hermes playbook candidates are exposed as local `playbook_regression_queue` regression-case candidates and can flow into the next Training/Codex queue after review. Unapproved, evidence-incomplete, or unclosed playbook candidates stay blocked. The local API exposes `/api/training/playbook-regression`; it does not write live Hermes memory, change code automatically, or touch APS/IOT systems.

Automatic Regression Runner v1 is now available through the Training workflow. It runs deterministic local checks over approved Tianpai baseline tasks and approved playbook regression candidates, returning `automatic_regression_run` with executable, passed, failed, blocked, and pass-rate metrics. The local API exposes `/api/training/regression-run`; it is not live Hermes execution, not model-weight fine tuning, and not automatic code modification.

Regression Gate v1 is now available through the Training workflow. It converts local regression results into a `regression_gate` decision with pass-rate threshold, automatic-loop permission, human-review requirements, blocked actions, Codex next-action queue, and Hermes feedback payload. The local API exposes `/api/training/regression-gate`; failed executable cases block the next loop, while blocked playbook candidates remain visible but non-executable.

Next Loop Handoff v1 is now available through the Training workflow. It converts Regression Gate output into `athena.next_loop_handoff.v1`, splitting the next loop into automatic local-training items, human-review items, and data-request items with a Hermes handoff payload. The local API exposes `/api/training/next-loop`; it does not automatically patch code, write live Hermes memory, parse raw files, or start APS/IOT integration.

Next Loop Handoff Review v1 is now available through the Training workflow. It records metadata-only decisions for handoff items, including approve-for-next-loop, resolved, deferred, needs-data, rejected, and note-only states. The local API exposes `/api/training/handoff-review` and `/api/training/handoff-reviews`; review decisions do not execute blocked work, write live Hermes memory, store raw files, or change code automatically.

Next Loop Closure Gate v1 is now available through the Training workflow. It evaluates handoff review decisions into `athena.next_loop_closure_gate.v1`, reporting whether local training iteration may proceed, whether handoff closure is complete, and which open or rejected items must stay visible. The local API exposes `/api/training/next-loop-closure`; it does not execute the plan, write code, write live Hermes memory, store raw files, or start APS/IOT integration.

Training Iteration Proposal v1 is now available through the Training workflow. It converts closure-gate output into `athena.training_iteration_proposal.v1`, with task seeds, open-item watchlist, confirmation boundary, Hermes proposal payload, KPI log, and evidence log. The local API exposes `/api/training/iteration-proposal`; it is a read-only proposal and does not execute tasks, write code, write live Hermes memory, store raw files, or start APS/IOT integration.

Training Iteration Proposal Review v1 is now available through the Training workflow. It records metadata-only approval, needs-changes, deferred, rejected, and note-only decisions for the training iteration proposal. The local API exposes `/api/training/iteration-proposal-review` and `/api/training/iteration-proposal-reviews`; approval only marks the proposal as ready for future queue preparation and does not execute tasks, write code, write live Hermes memory, store raw files, or start APS/IOT integration.

Codex Work Packet Queue v1 is now available through the Training workflow. It converts approved Training Iteration Proposals into read-only `athena.codex_work_packet_queue.v1` work packet drafts for future Codex worktree preparation. The local API exposes `/api/training/codex-work-packets`; packets do not execute automatically, create branches, change code, write live Hermes memory, store raw files, store credentials, or start APS/IOT integration.

Codex Patch Queue Contract v1 is now available through the Training workflow. It converts ready Codex work packets into read-only `athena.codex_patch_queue_contract.v1` patch candidates with validation requirements and training-signal context. The local API exposes `/api/training/codex-patch-queue`; candidates do not apply code, create branches, commit, push, open PRs, write live Hermes memory, store raw files, store credentials, or start APS/IOT integration.

Codex Execution Gate v1 is now available through the Training workflow. It converts ready patch candidates into pending human-reviewed execution candidates and records the execution boundary before any future small-fix worktree action. The local API exposes `/api/training/codex-execution-gate`; the gate does not execute patches, create branches, commit, push, open PRs, write live Hermes memory, store raw files, store credentials, or start APS/IOT integration.

Codex Execution Gate Review v1 is now available through the Training workflow. It records metadata-only review decisions for execution candidates, including approved-for-worktree, needs-changes, deferred, rejected, and note-only states. The local API exposes `/api/training/codex-execution-review` and `/api/training/codex-execution-reviews`; approval only marks future worktree preparation as allowed and does not execute code, create branches, commit, push, open PRs, write live Hermes memory, store raw files, store credentials, or start APS/IOT integration.

Codex Worktree Preparation Queue v1 is now available through the Training workflow. It converts approved execution review records into read-only worktree preparation task drafts with expected result contracts and validation requirements. The local API exposes `/api/training/codex-worktree-prep`; these tasks do not create worktrees, switch branches, apply patches, commit, push, open PRs, write live Hermes memory, store raw files, store credentials, or start APS/IOT integration.

Codex Worktree Launch Gate v1 is now available through the Training workflow. It converts ready worktree preparation tasks into read-only launch request drafts with explicit preflight checks and suggested user instructions. The local API exposes `/api/training/codex-worktree-launch`; launch requests do not run git, create worktrees, switch branches, apply patches, commit, push, open PRs, write live Hermes memory, store raw files, store credentials, or start APS/IOT integration.

Codex Worktree Result Intake v1 is now available through the Training workflow. It records metadata-only result summaries after explicitly user-launched Codex worktree tasks, including changed-file paths, validation statuses, and blocked actions. The local API exposes `/api/training/codex-worktree-results` and `/api/training/codex-worktree-result`; result intake does not store raw diffs, raw logs, raw files, credentials, commit, push, open PRs, write live Hermes memory, or start APS/IOT integration.

Codex Worktree Result Review Gate v1 is now available through the Training workflow. It converts validation-complete worktree result records into product-owner review candidates and can mark metadata-only regression baseline candidates or Hermes memory candidates. The local API exposes `/api/training/codex-worktree-result-review-gate`, `/api/training/codex-worktree-result-reviews`, and `/api/training/codex-worktree-result-review`; review approval does not promote a baseline, write live Hermes memory, merge, commit, push, open PRs, store raw patches, or start APS/IOT integration.

Codex Promotion Candidate Queue v1 is now available through the Training workflow. It collects approved result-review records into read-only regression baseline and Hermes memory promotion candidates. The local API exposes `/api/training/codex-promotion-candidates`; candidate queue generation does not promote a baseline, write live Hermes memory, merge, commit, push, open PRs, store raw patches, or start APS/IOT integration.

Codex Promotion Approval Gate v1 is now available through the Training workflow. It records metadata-only product-owner decisions on promotion candidates and prepares approved-but-not-executed future action plans for regression baseline promotion or Hermes memory writes. The local API exposes `/api/training/codex-promotion-approval-gate`, `/api/training/codex-promotion-approvals`, and `/api/training/codex-promotion-approval`; approval does not execute baseline promotion, write live Hermes memory, merge, commit, push, open PRs, store raw patches, store credentials, or start APS/IOT integration.

Codex Promotion Handoff Queue v1 is now available through the Training workflow. It converts approved-but-not-executed future promotion actions into manual handoff contracts with target system, owner role, required preflight checks, suggested user confirmation wording, and execution evidence requirements. The local API exposes `/api/training/codex-promotion-handoff`; handoff generation does not execute baseline promotion, write live Hermes memory, merge, commit, push, open PRs, store raw patches, store credentials, or start APS/IOT integration.

Codex Promotion Execution Readiness Gate v1 is now available through the Training workflow. It evaluates manual promotion handoff items for missing execution prerequisites before any real baseline promotion or live Hermes memory write can be considered. The local API exposes `/api/training/codex-promotion-execution-readiness`; readiness evaluation does not execute baseline promotion, write live Hermes memory, merge, commit, push, open PRs, store raw patches, store credentials, or start APS/IOT integration.

Codex Promotion Execution Readiness Review v1 is now available through the Training workflow. It records product-owner metadata decisions for readiness items, including confirmed-ready, needs-inputs, deferred, rejected, and note-only states. Confirmed readiness can clear the missing-prerequisite list and move the gate to final manual execution confirmation, but it still does not execute baseline promotion, write live Hermes memory, merge, commit, push, open PRs, store raw patches, store credentials, or start APS/IOT integration. The local API exposes `/api/training/codex-promotion-readiness-reviews` and `/api/training/codex-promotion-readiness-review`.

Codex Promotion Execution Result Intake v1 is now available through the Training workflow. It records metadata-only result summaries after explicitly manual promotion execution outside the demo, including changed record identifiers and validation summaries. The local API exposes `/api/training/codex-promotion-execution-results` and `/api/training/codex-promotion-execution-result`; result intake does not execute baseline promotion, write live Hermes memory, merge, commit, push, open PRs, store raw patches, store credentials, or start APS/IOT integration.

Codex Promotion Closure / Hermes Sync Audit v1 is now available through the Training workflow. It audits whether metadata-only promotion execution result records are complete enough to close the promotion loop and prepare future regression-baseline or Hermes synchronization audit candidates. The local API exposes `/api/training/codex-promotion-closure-audit`; closure audit does not update baselines, write live Hermes memory, merge, commit, push, open PRs, store raw files, store credentials, or start APS/IOT integration.

Codex Promotion Sync Review Gate v1 is now available through the Training workflow. It records metadata-only product-owner review decisions for closure-audit sync candidates and prepares approved-but-not-executed future sync action plans. The local API exposes `/api/training/codex-promotion-sync-review-gate`, `/api/training/codex-promotion-sync-reviews`, and `/api/training/codex-promotion-sync-review`; sync review does not update baselines, write live Hermes memory, merge, commit, push, open PRs, store raw files, store credentials, or start APS/IOT integration.

Codex Promotion Sync Handoff Queue v1 is now available through the Training workflow. It converts approved-but-not-executed future sync action plans into read-only manual execution handoff contracts with target system, owner role, preflight checks, suggested instruction text, and required execution evidence. The local API exposes `/api/training/codex-promotion-sync-handoff`; handoff preparation does not update baselines, write live Hermes memory, merge, commit, push, open PRs, store raw files, store credentials, or start APS/IOT integration.

Codex Promotion Sync Execution Readiness Gate v1 is now available through the Training workflow. It evaluates manual sync handoff items for missing prerequisite inputs before any regression baseline update or live Hermes memory write can be considered. The local API exposes `/api/training/codex-promotion-sync-readiness`; readiness evaluation does not update baselines, write live Hermes memory, merge, commit, push, open PRs, store raw files, store credentials, or start APS/IOT integration.

Codex Promotion Sync Execution Readiness Review v1 is now available through the Training workflow. It records metadata-only product-owner review decisions for sync execution readiness items, including confirmed-ready, needs-inputs, deferred, rejected, and note-only states. The local API exposes `/api/training/codex-promotion-sync-readiness-reviews` and `/api/training/codex-promotion-sync-readiness-review`; review decisions do not update baselines, write live Hermes memory, merge, commit, push, open PRs, store raw files, store credentials, or start APS/IOT integration.

Codex Promotion Sync Execution Result Intake v1 is now available through the Training workflow. It records metadata-only result summaries after explicitly manual sync execution outside the demo, including changed record identifiers and validation summaries. The local API exposes `/api/training/codex-promotion-sync-execution-results` and `/api/training/codex-promotion-sync-execution-result`; result intake does not update baselines, write live Hermes memory, merge, commit, push, open PRs, store raw files, store credentials, or start APS/IOT integration.

Codex Promotion Sync Closure Audit v1 is now available through the Training workflow. It audits whether metadata-only manual sync execution result records are complete enough for final review candidates. The local API exposes `/api/training/codex-promotion-sync-closure-audit`; closure audit does not update baselines, write live Hermes memory, merge, commit, push, open PRs, store raw files, store credentials, or start APS/IOT integration.

Codex Promotion Sync Closure Review Gate v1 is now available through the Training workflow. It records product-owner final sync closure decisions as metadata only and turns approved candidates into approved-but-not-executed future real sync action plans. The local API exposes `/api/training/codex-promotion-sync-closure-review-gate`, `/api/training/codex-promotion-sync-closure-reviews`, and `/api/training/codex-promotion-sync-closure-review`; the gate does not update baselines, write live Hermes memory, merge, commit, push, open PRs, store raw files, store credentials, or start APS/IOT integration.

Codex Promotion Final Sync Handoff Queue v1 is now available through the Training workflow. It prepares manual final sync handoff contracts from approved closure-review future actions, including target system, owner role, required real-sync inputs, suggested instruction text, and execution evidence requirements. The local API exposes `/api/training/codex-promotion-final-sync-handoff`; handoff preparation does not update baselines, write live Hermes memory, merge, commit, push, open PRs, store raw files, store credentials, or start APS/IOT integration.

Codex Promotion Final Sync Execution Readiness Gate v1 is now available through the Training workflow. It evaluates final sync handoff contracts for missing real-system prerequisites before any baseline update or live Hermes write can be considered, including endpoint or baseline store contracts, auth, schema, tenant/factory scope, retention, rollback planning, current validation output, execution evidence plan, and product-owner execution confirmation. The local API exposes `/api/training/codex-promotion-final-sync-readiness`; readiness evaluation does not update baselines, write live Hermes memory, merge, commit, push, open PRs, store raw files, store credentials, or start APS/IOT integration.

Codex Promotion Final Sync Execution Result Intake v1 is now available through the Training workflow. It records metadata-only result summaries after explicit manual final sync execution outside the demo, including changed record identifiers, validation summaries, rollback summaries, and validation command summaries. The local API exposes `/api/training/codex-promotion-final-sync-execution-results` and `/api/training/codex-promotion-final-sync-execution-result`; result intake does not update baselines, write live Hermes memory, merge, commit, push, open PRs, store raw files, store credentials, or start APS/IOT integration.

Codex Promotion Final Sync Closure Audit v1 is now available through the Training workflow. It audits whether final sync result records are complete enough for final completion review, including expected result count, recorded result count, complete result count, missing result count, failed result count, and completion-review candidates. The local API exposes `/api/training/codex-promotion-final-sync-closure-audit`; closure audit does not update baselines, write live Hermes memory, publish project memory, merge, commit, push, open PRs, store raw files, store credentials, or start APS/IOT integration.

Codex Promotion Final Completion Review Gate v1 is now available through the Training workflow. It records metadata-only product-owner final completion decisions for completion-review candidates, including approved, needs-inputs, deferred, rejected, and note-only states, then prepares approved-but-not-published future publication plans. The local API exposes `/api/training/codex-promotion-final-completion-review-gate`, `/api/training/codex-promotion-final-completion-reviews`, and `/api/training/codex-promotion-final-completion-review`; final completion review does not publish project memory, update baselines, write live Hermes memory, merge, commit, push, open PRs, store raw files, store credentials, or start APS/IOT integration.

Codex Promotion Final Publication Handoff Queue v1 is now available through the Training workflow. It converts approved final completion publication plans into metadata-only manual handoff contracts with target system, owner role, required publication inputs, publication evidence, and suggested user instruction. The local API exposes `/api/training/codex-promotion-final-publication-handoff`; handoff preparation does not publish project memory, update regression baselines, write live Hermes memory, merge, commit, push, open PRs, store raw files, store credentials, or start APS/IOT integration.

Codex Promotion Final Publication Readiness Gate v1 is now available through the Training workflow. It evaluates final publication handoff contracts for missing publication prerequisites before any project-memory publication, regression baseline update, or live Hermes write can be considered, including target system contract, endpoint/auth or baseline store, schema or version label, tenant/factory scope, retention, rollback, current validation output, publication evidence plan, and product-owner publication confirmation. The local API exposes `/api/training/codex-promotion-final-publication-readiness`; readiness evaluation does not publish project memory, update regression baselines, write live Hermes memory, merge, commit, push, open PRs, store raw files, store credentials, or start APS/IOT integration.

Codex Promotion Final Publication Result Intake v1 is now available through the Training workflow. It records metadata-only result summaries after explicitly manual final publication outside the demo, including publication reference, published record identifiers, validation summary, rollback summary, and validation command summaries. The local API exposes `/api/training/codex-promotion-final-publication-results` and `/api/training/codex-promotion-final-publication-result`; result intake does not publish project memory, update regression baselines, write live Hermes memory, merge, commit, push, open PRs, store raw files, store credentials, or start APS/IOT integration.

Codex Promotion Final Publication Closure Audit v1 is now available through the Training workflow. It audits whether final publication result records are complete enough for final release/archive review, including expected result count, recorded result count, complete result count, missing result count, failed result count, and final release-review candidates. The local API exposes `/api/training/codex-promotion-final-publication-closure-audit`; closure audit does not publish project memory, update regression baselines, write live Hermes memory, merge, commit, push, open PRs, store raw files, store credentials, or start APS/IOT integration.

Codex Promotion Final Release / Archive Review Gate v1 is now available through the Training workflow. It prepares product-owner final release and archive review candidates from complete final publication closure metadata, including publication references, published record identifiers, validation summaries, compileall summaries, harness summaries, rollback ownership, and post-release monitoring ownership. The local API exposes `/api/training/codex-promotion-final-release-review-gate`; release review preparation does not create archive artifacts, publish project memory, update regression baselines, write live Hermes memory, merge, commit, push, open PRs, store raw artifacts, store credentials, or start APS/IOT integration.

Every `/api/chat` response now carries an `athena_runtime_event` envelope for future Hermes ingestion. It records workflow, persona, intent, data sufficiency, data boundary, evidence references, blocked actions, and a memory-event candidate, while intentionally excluding raw user text, generated sensitive values, credentials, and live Hermes writeback.

The Athena Automatic Training Console is available at `/training.html`. It is the first automatic training progress surface for Athena and Tianpai: it loads `docs/training/tianpai_training_pack_v0_1.json`, automatically evaluates candidate tasks, scores evidence and governance alignment, flags known data gaps, emits Hermes-style JSON, prepares Codex/Hermes next-iteration queues, summarizes the current training round, promotes approved tasks into a regression baseline, displays approved-playbook regression readiness, runs local automatic regression checks, evaluates the regression gate, prepares the next-loop handoff, records handoff review decisions, evaluates closure readiness, prepares a read-only training iteration proposal, records proposal review decisions, prepares approved read-only Codex work packets, converts ready work packets into read-only Codex patch candidates, gates execution candidates behind human confirmation, records metadata-only execution gate reviews, prepares approved worktree task drafts, evaluates a read-only worktree launch gate, records metadata-only worktree results, records metadata-only worktree result review decisions, prepares read-only promotion candidates, records metadata-only promotion approval decisions, prepares read-only manual promotion handoff contracts, evaluates promotion execution readiness prerequisites, records metadata-only promotion execution readiness review decisions, records metadata-only promotion execution result summaries, audits promotion closure / Hermes sync readiness, records metadata-only promotion sync review decisions, prepares read-only promotion sync handoff contracts, evaluates sync execution readiness prerequisites, records metadata-only sync readiness review decisions, records metadata-only sync execution result summaries, audits sync closure readiness, records metadata-only sync closure review decisions for future real sync action planning, prepares final sync handoff contracts, evaluates final sync execution readiness, records metadata-only final sync execution result summaries, audits final sync closure readiness, records metadata-only final completion review decisions, prepares manual final publication handoff contracts, evaluates final publication readiness, records metadata-only final publication result summaries, and audits final publication closure readiness before any real publication claim. This is not manual training, not model-weight fine tuning, and not a live Hermes runner yet. The local API exposes `/api/training/template`, `/api/training/overview`, `/api/training/run`, `/api/training/round-summary`, `/api/training/promote-baseline`, `/api/training/playbook-regression`, `/api/training/regression-run`, `/api/training/regression-gate`, `/api/training/next-loop`, `/api/training/handoff-review`, `/api/training/handoff-reviews`, `/api/training/next-loop-closure`, `/api/training/iteration-proposal`, `/api/training/iteration-proposal-review`, `/api/training/iteration-proposal-reviews`, `/api/training/codex-work-packets`, `/api/training/codex-patch-queue`, `/api/training/codex-execution-gate`, `/api/training/codex-execution-review`, `/api/training/codex-execution-reviews`, `/api/training/codex-worktree-prep`, `/api/training/codex-worktree-launch`, `/api/training/codex-worktree-results`, `/api/training/codex-worktree-result`, `/api/training/codex-worktree-result-review-gate`, `/api/training/codex-worktree-result-reviews`, `/api/training/codex-worktree-result-review`, `/api/training/codex-promotion-candidates`, `/api/training/codex-promotion-approval-gate`, `/api/training/codex-promotion-approvals`, `/api/training/codex-promotion-approval`, `/api/training/codex-promotion-handoff`, `/api/training/codex-promotion-execution-readiness`, `/api/training/codex-promotion-readiness-reviews`, `/api/training/codex-promotion-readiness-review`, `/api/training/codex-promotion-execution-results`, `/api/training/codex-promotion-execution-result`, `/api/training/codex-promotion-closure-audit`, `/api/training/codex-promotion-sync-review-gate`, `/api/training/codex-promotion-sync-reviews`, `/api/training/codex-promotion-sync-review`, `/api/training/codex-promotion-sync-handoff`, `/api/training/codex-promotion-sync-readiness`, `/api/training/codex-promotion-sync-readiness-reviews`, `/api/training/codex-promotion-sync-readiness-review`, `/api/training/codex-promotion-sync-execution-results`, `/api/training/codex-promotion-sync-execution-result`, `/api/training/codex-promotion-sync-closure-audit`, `/api/training/codex-promotion-sync-closure-review-gate`, `/api/training/codex-promotion-sync-closure-reviews`, `/api/training/codex-promotion-sync-closure-review`, `/api/training/codex-promotion-final-sync-handoff`, `/api/training/codex-promotion-final-sync-readiness`, `/api/training/codex-promotion-final-sync-execution-results`, `/api/training/codex-promotion-final-sync-execution-result`, `/api/training/codex-promotion-final-sync-closure-audit`, `/api/training/codex-promotion-final-completion-review-gate`, `/api/training/codex-promotion-final-completion-reviews`, `/api/training/codex-promotion-final-completion-review`, `/api/training/codex-promotion-final-publication-handoff`, `/api/training/codex-promotion-final-publication-readiness`, `/api/training/codex-promotion-final-publication-results`, `/api/training/codex-promotion-final-publication-result`, and `/api/training/codex-promotion-final-publication-closure-audit`.

Training review and data intake are also available on `/training.html`. Users can approve, request changes, reject, or annotate a training task, and can register, skip, or mark unavailable a needed data source. The review API stores only review metadata and source references in `src/mock_data/training_task_reviews.json`; it does not upload, copy, parse, or store raw Excel files or credentials. The local API exposes `/api/training/reviews`, `/api/training/review`, and `/api/training/data-source`.

The first Tianpai training baseline is stored in `docs/training/tianpai_training_pack_v0_1.json`, with a human-readable summary in `docs/training/tianpai_training_summary_v0_1.md`. It structures Agnes VOC screenshots, Melos-provided Tianpai IOT output/scrap/fault exports, the APS-side workflow fragment, the confirmed Tianpai onsite workflow, and the current Tianpai training-governance rules into data-quality findings, normalized field maps, KPI seeds, candidate training tasks, and Hermes tenant memory-event candidates. The current approved regression set is recorded in `src/mock_data/training_task_reviews.json` as metadata-only baseline promotion state. The APS Planned Task delivery-time CSV attachment can cover APS schedule and delivery-time fields through `produce_order_code`, machine, style, quantity, plan/actual/estimate timing, status, and `delivery_time`; it is not copied into the repo. Full order-flow training still needs the APS-to-IOT join rule and real downstream/material/quality records.

Tianpai training governance currently targets the general manager first. Athena should answer with management summary + reason/evidence + recommended action, prioritize KPIs as delivery > quality > cost, keep first-screen risk cards evidence-backed and actual-export-first when available, propose recommendations only inside the weaving-process scope for now, explicitly state missing data when evidence is insufficient, and use terminology in `standard_field_name (site_term)` format. Small fixes may proceed automatically in the Codex/Hermes loop; large feature changes, new pages, real data integration, feature-version changes, and major-version changes require user confirmation.

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
- Hermes integration state flow
- Next product decisions

The developer page also shows a compact Latest Changelog preview sourced from `/changelog.html`, so testers can verify the current iteration without leaving the debug workflow.

The demo links to `/athena-mvp.html`, which shows the Design Agent input-structuring loop: design/Style3D/CLO/AI-image/TP input -> normalized design_request and source_asset objects -> engineering brief candidate -> manufacturability check -> sampling feedback -> revision suggestion -> evidence and KPI logs. Real Style3D/CLO/SWS/Arachne adapters are not connected yet.

The demo links to `/production.html`, which shows the Production Operations loop with mock APS/IOT data, APS/IOT field mapping, order/scheduling/machine/garment site-flow sections, Santoni Athena root-cause analysis, optimization signals, service request candidates, evidence logs, and KPI logs.

The demo links to `/hermes.html`, which shows the Hermes adapter contract, Athena memory-event candidates, memory governance fields, self-evolution loop, development suggestions, tool registry candidates, blocked actions, evidence logs, and KPI logs.

The demo links to `/training.html`, which shows Athena's automatic Tianpai training loop, task status, task review actions, data-source registration, capability progress, Hermes-style JSON result, Codex patch/data queue, next training tasks, evidence logs, and KPI logs.

The Tianpai training pack under `docs/training/` is the local handoff package for future Athena/Hermes training tasks. It includes the current data boundary explicitly: Tianpai IOT records in the provided export have no usable `order_id`, not all machines are connected, IOT currently does not participate in Tianpai's actual production workflow, APS only schedules the weaving portion, APS Planned Task delivery-time rows are available as metadata-only schedule evidence, the APS-to-IOT join rule is still unconfirmed, the first training acceptance standard is intentionally iterative, and material/labor/stage-level quality-output tables are still needed before Athena can explain full order-level root cause and customer cost.

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




