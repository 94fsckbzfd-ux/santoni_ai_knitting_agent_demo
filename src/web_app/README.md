# Web App

Web entries for the MVP.

Phase 1 goal: provide a low-friction demo for General Manager, Designer, and Customer Equipment Engineer workflows, a Design Intake Structuring Console for design-input object review, a Production Operations Console for mock order-to-garment monitoring, a Hermes Integration Console for Athena runtime/memory/tool-orchestration contract review, and an Athena Automatic Training Console for Tianpai training progress.

All HTML entries load the shared `i18n.js` language switch for Chinese / English page chrome.

General Manager Demo UX Polish v1 keeps the user page focused on management decisions: today's top-three priorities, Service/equipment risk, evidence details, local follow-up, and the original chat stream. It does not show Internal Demo Mode, demo readiness, development progress, version notes, raw JSON, payloads, or full technical field lists outside evidence details.

Athena Verification Process Visualization v1 adds a management-facing verification section to Production drilldown answers. The user sees what Athena checked, what it found, the evidence level, what it still cannot conclude, the data gap, and who should confirm next; raw debug trace and internal schema details remain hidden from the user page.

Stable General Manager Demo Story Pack v1 is available in Production Console. It gives internal presenters three repeatable stories with actual APS/ERP export evidence, clearly labeled mock IOT/Service supplements, data gaps, suggested owners, and one-click Santoni Athena drilldown questions.

Delivery Risk Driver Guard v0.108.3 separates hard delivery-risk orders from delivery status or quantity reconciliation candidates. Athena now records explicit delivery risk drivers and avoids presenting essentially completed but inconsistent orders as current delivery-risk conclusions.

Evidence Review Queue v0.109.0 adds a customer-visible but management-level review lane for APS/ERP records that need planning or quantity reconciliation before Athena can call them hard risks.

GM First Screen Hierarchy Polish v0.110.0 organizes the user page into KPI dashboard, top-three hard risks, evidence review candidates, Service/equipment risk candidates, and the original chat stream. It keeps raw JSON, payloads, and development progress out of the customer-facing page.

General Manager Decision UI Compression v0.111.0 compresses Production drilldown answers into conclusion, evidence support, suggested confirmation owner, and next action by default. Full evidence, field sources, sanity flags, and checked objects remain available only in expandable details.

Local Decision Follow-up Board v0.112.0 lets hard risk, evidence review, and Service risk cards create local metadata-only follow-ups with source card type, related object, confirmation need, Athena recommendation reason, evidence refs, and read-only boundary.

Daily Brief Narrative v0.113.0 generates a three-minute General Manager morning-brief summary from the structured dashboard, top-three risks, Evidence Review Queue, Service risk cards, and local follow-up state. The brief can be copied from the user page and does not expose raw JSON or internal schema.

GM First Screen Hierarchy Polish v0.113.0 keeps the customer-facing General Manager page focused on the KPI dashboard, today's three priorities, Service risk candidates, evidence review, local follow-up items, and same-page Santoni Athena drilldown while avoiding raw payload-style output.

GM Dashboard Hotfix v0.113.1 restores the user-page General Manager dashboard load path, adds the missing local percent formatter, keeps real render errors visible in the page, and cleans first-screen Chinese copy for the Daily Brief and actual-data risk cards.

Daily Smoke Check v0.113.2 adds `scripts/smoke_check.py` for compileall, critical Production page mojibake scanning, General Manager priority API text scanning, and high-signal smoke tests during routine development.

Stable Demo Story Pack Encoding Guard v0.113.3 fixes Stable Demo Story Pack Chinese text and extends the smoke check to scan that Production API object before it reaches `/production.html`.

Machine/style evidence still uses `Style_Component` and `T_Machine_Info` as the required-vs-actual parameter sources for cylinder diameter and needle spacing checks.

Production Operations Console defaults to Chinese for customer review and localizes API-driven status, KPI, evidence, APS/IOT field mapping, and production site-flow content.

The customer-facing home page is now the primary General Manager demo entry. Selecting the `总经理` identity opens an embedded Production workspace with top-three risk cards, evidence refs, suggested owners/actions, and a same-page Santoni Athena root-cause drilldown panel.

The customer-facing home page also routes production-manager/order/delivery/KPI/root-cause questions from the original bottom chat box into Santoni Athena production analysis and renders management-summary, reason/evidence, recommended-action, data-boundary, and Skill Execution Trace cards in the same chat history. Risk-card `让 Athena 下钻` actions append to that same conversation stream.

General Manager Follow-up Loop Demo v1 is now available on the customer-facing home page. Each top-three Production risk card can generate a local follow-up todo, show owner/evidence/status context, update metadata-only status, and continue asking Athena from the same todo without writing APS, ERP, IOT, Hermes memory, ticket systems, or machine controls.

General Manager Internal Demo guidance is now kept out of the customer-facing home page. The embedded workspace shows Service risk candidates and expandable evidence details/data gaps, while internal demo readiness guidance stays in the Codex completion conversation and the linked report.

Developer General Manager Flow Parity v1 is now available. The developer/debug page mirrors the same General Manager interaction path: selecting `总经理` automatically requests the top-three Production priority brief, and the original developer test input routes Production follow-ups through `/api/production/chatbi`.

The customer-facing home page and developer/debug page require identity selection before effective chat. General Manager, Service Engineer, and Design Development buttons set the request role explicitly, while natural-language identity detection remains a backend fallback.

The customer-facing page script runs in its own scope and exposes a readiness marker so shared language-switch globals cannot silently break identity controls.

Production Athena treats Chinese 货期 / 平均货期 wording as order-delay analysis. Current mock output uses due-date distance for backlog review and does not claim to calculate real recent-week historical lead time.

Production Athena management answers use a fixed conclusion, reason/evidence, risk, recommendation, and data-gap structure. The first high-frequency management branches cover delivery risk, low yield/scrap, machine bottleneck, material risk, and current data limitations.

Production Console now shows Management Priority Engine v1: Athena ranks the general manager's top evidence-backed priorities, affected objects, owner roles, decision gates, data gaps, and action candidates before any future follow-up or Hermes playbook promotion.

Production Console now shows Decision Loop / Follow-up Engine v1: Athena turns priority actions into local follow-up items with owner, evidence status, closure gate, recurrence watch, and metadata-only review buttons. These controls do not write APS, IOT, ticket systems, or Hermes memory.

The customer-facing home page now keeps production follow-up turns in the `production_manager` role after a `production_athena` response. `/api/chat` responses include an `athena_runtime_event` envelope for future Hermes ingestion without persisting raw user text or credentials.

Hermes Integration Console is mock-contract only. It defines Athena memory events, organization-memory playbook candidates, development suggestions, tool registry candidates, evidence logs, KPI logs, and blocked actions without connecting to a live Hermes endpoint or storing credentials.

Hermes Console now shows Organization Memory / Playbook Engine v1. It turns Production decision-loop follow-ups into playbook candidates with promotion gates, memory-event candidates, regression-case candidates, and metadata-only review buttons; approval stays blocked until follow-up closure and accepted evidence are available.

Athena Automatic Training Console runs local automatic evaluation over structured Tianpai training tasks, emits Hermes-style JSON, and shows task progress, capability progress, data gaps, patch/data queues, evidence logs, KPI logs, training round summary, baseline promotion state, playbook regression queue, automatic regression run results, regression gate decisions, next-loop handoff queues, metadata-only handoff review decisions, next-loop closure-gate results, read-only training iteration proposals, and metadata-only proposal review decisions. It is not model-weight fine tuning and is not connected to a live Hermes runner yet.

Training review and data intake controls let reviewers approve, request changes, reject, or annotate a task, and register, skip, or mark unavailable a needed data source. The console records metadata only and does not upload or store raw Excel files or credentials.

Training baseline controls promote approved tasks into the automatic regression set and record APS attachment coverage plus unavailable cost/stage-record decisions as metadata only.

Training Console now also shows Playbook Regression Queue v1. Approved Hermes playbook candidates can become local regression-case candidates for the next automatic loop, while unapproved or evidence-incomplete candidates stay blocked and read-only.

Training Console now shows Automatic Regression Run v1. The Run Regression button executes deterministic local checks over approved Tianpai baseline tasks and approved playbook regression candidates; blocked playbook candidates are visible but not executed.

Training Console now shows Regression Gate v1. The gate converts regression results into local Codex/Hermes next-loop permission, human-review queues, blocked actions, and Hermes feedback payload without live memory writeback or automatic code modification.

Training Console now shows Next Loop Handoff v1. The handoff converts gate output into automatic local-training items, human-review items, and data-request items, while keeping code writes, live Hermes memory writes, raw-file storage, and real data integration blocked.

Training Console now shows Next Loop Handoff Review v1. Handoff item buttons record approve, resolve, defer, needs-data, and note-only decisions in the local training review store without executing blocked work or writing live Hermes memory.

Training Console now shows Next Loop Closure Gate v1. The gate evaluates handoff review decisions into local iteration permission, closure completeness, open/rejected item lists, and a read-only local iteration plan.

Training Console now shows Training Iteration Proposal v1. The proposal converts closure-gate output into local task seeds, open-item watchlist, confirmation boundary, Hermes proposal payload, and blocked actions without executing the iteration.

Training Console now shows Training Iteration Proposal Review v1. Proposal review controls record approval, needs-changes, deferred, rejected, or note-only decisions while keeping task execution, code writes, live Hermes memory, and real data integration blocked.

Training Console now shows Codex Work Packet Queue v1. Approved Training Iteration Proposals can become read-only Codex work packet drafts for future worktree preparation, while unreviewed, rejected, deferred, or needs-changes proposals stay blocked. Work packets do not execute automatically, create branches, change code, write live Hermes memory, store raw files, store credentials, or start APS/IOT integration.

Training Console now shows Codex Patch Queue Contract v1. Ready Codex work packets can become read-only patch candidates with validation requirements and training-signal context, while blocked work packets keep the patch queue blocked. Patch candidates do not apply code, create branches, commit, push, open PRs, write live Hermes memory, store raw files, store credentials, or start APS/IOT integration.

Training Console now shows Codex Execution Gate v1. Ready patch candidates can become pending human-reviewed execution candidates, but automatic execution remains blocked. The gate does not execute patches, create branches, commit, push, open PRs, write live Hermes memory, store raw files, store credentials, or start APS/IOT integration.

Training Console now shows Codex Execution Gate Review v1. Execution candidate buttons record approve-for-worktree, needs-changes, defer, reject, or note-only decisions in the local training review store without executing patches, creating branches, committing, pushing, opening PRs, writing live Hermes memory, storing raw files, storing credentials, or starting APS/IOT integration.

Training Console now shows Codex Worktree Preparation Queue v1. Approved execution reviews can become read-only worktree preparation task drafts with expected result contracts and validation requirements, while actual worktree creation, branch switching, patch application, commits, pushes, PRs, live Hermes writes, raw-file storage, credentials, and APS/IOT integration remain blocked.

Training Console now shows Codex Worktree Launch Gate v1. Ready preparation tasks can become read-only launch request drafts with preflight checks and suggested user instructions, while git worktree creation, branch switching, patch application, commits, pushes, PRs, live Hermes writes, raw-file storage, credentials, and APS/IOT integration remain blocked.

Training Console now shows Codex Worktree Result Intake v1. Future user-launched worktree tasks can return metadata-only result summaries, changed-file paths, validation statuses, and blocked actions, while raw diffs, raw logs, raw files, credentials, automatic merges, commits, pushes, PRs, live Hermes writes, and APS/IOT integration remain blocked.

Training Console now shows Codex Worktree Result Review Gate v1. Validation-complete worktree results can become product-owner review candidates and metadata-only regression or Hermes memory candidates, while automatic baseline promotion, live Hermes writes, merges, commits, pushes, PRs, raw patch storage, credentials, and APS/IOT integration remain blocked.

Training Console now shows Codex Promotion Candidate Queue v1. Approved result-review records can become read-only regression baseline and Hermes memory promotion candidates, while actual baseline promotion, live Hermes writes, merges, commits, pushes, PRs, raw patch storage, credentials, and APS/IOT integration remain blocked.

Training Console now also shows Codex Promotion Approval Gate v1. Product-owner decisions on promotion candidates are stored as metadata-only approval records and converted into approved-but-not-executed future action plans; actual baseline promotion, live Hermes writes, merges, commits, pushes, PRs, raw patch storage, credentials, and APS/IOT integration remain blocked.

Training Console now shows Codex Promotion Handoff Queue v1. Approved-but-not-executed future actions become read-only manual handoff contracts with owner roles, preflight checks, suggested confirmation wording, and execution evidence requirements; actual baseline promotion, live Hermes writes, merges, commits, pushes, PRs, raw patch storage, credentials, and APS/IOT integration remain blocked.

Training Console now shows Codex Promotion Execution Readiness Gate v1. Manual promotion handoff items are checked for missing execution prerequisites before any real baseline promotion or live Hermes memory write is considered; execution still requires explicit product-owner confirmation, fresh validation evidence, rollback planning, and live-system contract details.

Training Console now shows Codex Promotion Execution Readiness Review v1. Review buttons record metadata-only confirmed-ready, needs-inputs, deferred, rejected, and note-only decisions for readiness items; confirmed prerequisites can move the gate to final manual execution confirmation but cannot execute baseline promotion, live Hermes writes, commits, pushes, PRs, raw patch storage, credentials, or APS/IOT integration.

Training Console now shows Codex Promotion Execution Result Intake v1. Metadata-only result records can be entered after explicit manual promotion execution outside the demo; records include changed record identifiers and validation summaries while actual baseline promotion, live Hermes writes, commits, pushes, PRs, raw patch storage, credentials, and APS/IOT integration remain blocked.

Training Console now shows Codex Promotion Closure / Hermes Sync Audit v1. The panel checks whether recorded promotion execution results are complete enough for future regression-baseline or Hermes synchronization review, while actual baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and APS/IOT integration remain blocked.

Training Console now shows Codex Promotion Sync Review Gate v1. Product-owner sync-review decisions are stored as metadata only and converted into approved-but-not-executed future sync plans; actual baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and APS/IOT integration remain blocked.

Training Console now shows Codex Promotion Sync Handoff Queue v1. Approved future sync actions become read-only manual execution handoff contracts with target systems, owner roles, preflight checks, suggested instructions, and execution evidence requirements while baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and APS/IOT integration remain blocked.

Training Console now shows Codex Promotion Sync Execution Readiness Gate v1. Manual sync handoff items are checked for missing execution prerequisites before any regression baseline update or live Hermes memory write is considered; baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and APS/IOT integration remain blocked.

Training Console now shows Codex Promotion Sync Execution Readiness Review v1. Sync readiness item buttons record confirmed-ready, needs-inputs, deferred, rejected, or note-only decisions in the local training review store without updating baselines, writing live Hermes memory, committing, pushing, opening PRs, storing raw files, storing credentials, or starting APS/IOT integration.

Training Console now shows Codex Promotion Sync Execution Result Intake v1. Metadata-only result records can be entered after explicit manual sync execution outside the demo; records include changed record identifiers and validation summaries while baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and APS/IOT integration remain blocked.

Training Console now shows Codex Promotion Sync Closure Audit v1. The panel audits whether metadata-only manual sync result records are complete enough for final review candidates, while real baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and APS/IOT integration remain blocked.

Training Console now shows Codex Promotion Sync Closure Review Gate v1. Final sync closure review buttons store metadata-only product-owner decisions and convert approved candidates into approved-but-not-executed future real sync action plans; baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and APS/IOT integration remain blocked.

Training Console now shows Codex Promotion Final Sync Handoff Queue v1. Approved closure-review future actions become read-only manual final sync handoff contracts with target systems, owner roles, required real-sync inputs, suggested instructions, and execution evidence requirements; baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and APS/IOT integration remain blocked.

Training Console now shows Codex Promotion Final Sync Execution Readiness Gate v1. Final sync handoff contracts are checked for missing real-system prerequisites such as endpoint or baseline store contracts, auth, schema, tenant/factory scope, retention, rollback planning, current validation output, execution evidence plan, and product-owner confirmation before any baseline update or live Hermes write can be considered; real writes, git actions, raw-file storage, credentials, and APS/IOT integration remain blocked.

Training Console now shows Codex Promotion Final Sync Execution Result Intake v1. Final sync result buttons record metadata-only summaries after explicit manual final sync execution outside the demo, including changed records, validation summaries, rollback summaries, and validation command evidence; baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and APS/IOT integration remain blocked.

Training Console now shows Codex Promotion Final Sync Closure Audit v1. Final sync closure audit cards summarize expected, recorded, complete, missing, failed, and completion-review candidate counts from final sync result metadata; baseline updates, live Hermes writes, project-memory publication, commits, pushes, PRs, raw file storage, credentials, and APS/IOT integration remain blocked.

Training Console now shows Codex Promotion Final Completion Review Gate v1. Product-owner buttons record metadata-only final completion decisions for approved, needs-inputs, deferred, rejected, and note-only states, then prepare approved-but-not-published future publication plans; project-memory publication, baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and APS/IOT integration remain blocked.

Training Console now shows Codex Promotion Final Publication Handoff Queue v1. Approved final completion publication plans become metadata-only manual publication handoff contracts with target systems, owner roles, required publication inputs, publication evidence, and suggested user instructions; project-memory publication, baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and APS/IOT integration remain blocked.

Training Console now shows Codex Promotion Final Publication Readiness Gate v1. Final publication handoff contracts are checked for missing publication prerequisites such as endpoint/auth or baseline store, schema or version label, tenant/factory scope, retention, rollback planning, current validation output, publication evidence plan, and product-owner confirmation before any project-memory publication, baseline update, or live Hermes write can be considered; real writes, git actions, raw-file storage, credentials, and APS/IOT integration remain blocked.

Training Console now shows Codex Promotion Final Publication Result Intake v1. Result buttons record metadata-only summaries after explicit manual final publication outside the demo, including publication reference, published record identifiers, validation summary, rollback summary, and validation command evidence; project-memory publication, baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and APS/IOT integration remain blocked.


