"""Agent Operating Model placeholders.

These interfaces reserve the product architecture for the five capabilities
that turn the demo from a chatbot into a business agent.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class OperatingModelCapability:
    key: str
    name: str
    status: str
    progress: int
    purpose: str
    current_scope: str
    next_step: str


@dataclass
class GoalInterface:
    """Defines agent objectives and success criteria."""

    primary_goal: str = ""
    success_criteria: list[str] = field(default_factory=list)
    failure_modes: list[str] = field(default_factory=list)


@dataclass
class StateInterface:
    """Tracks where the user is in the workflow."""

    workflow: str = "unknown"
    stage: str = "intake"
    known_info: dict = field(default_factory=dict)
    missing_info: list[str] = field(default_factory=list)


@dataclass
class GuardrailsInterface:
    """Defines boundaries and escalation rules."""

    rules: list[str] = field(default_factory=list)
    requires_human_confirmation: list[str] = field(default_factory=list)
    blocked_actions: list[str] = field(default_factory=list)


@dataclass
class HandoffInterface:
    """Defines when and how the agent hands work to humans or systems."""

    target_role: str = ""
    handoff_payload: dict = field(default_factory=dict)
    handoff_reason: str = ""


@dataclass
class EvaluationInterface:
    """Defines self-checks before the agent responds or acts."""

    checks: list[str] = field(default_factory=list)
    score: float | None = None
    revision_needed: bool = False


def designer_state_flow() -> list[dict]:
    return [
        {
            "stage": "Identity / Intent Detection",
            "status": "implemented",
            "certainty": "confirmed",
            "description": "Main Agent infers whether the user is a designer or service user from natural language and session context.",
        },
        {
            "stage": "Design Discovery",
            "status": "in_progress",
            "certainty": "assumption_until_designer_voc",
            "description": "Collect product type, target user, use case, function, cost, style, and constraints.",
        },
        {
            "stage": "Concept Clarification",
            "status": "planned",
            "certainty": "assumption_until_designer_voc",
            "description": "Clarify concept direction, reference image interpretation, brand line, and success criteria.",
        },
        {
            "stage": "Feasibility Check",
            "status": "planned",
            "certainty": "high_confidence",
            "description": "Evaluate feasibility under Santoni machine/SWS assumptions and identify risks or alternatives.",
        },
        {
            "stage": "Product Development Brief",
            "status": "planned",
            "certainty": "high_confidence",
            "description": "Generate a first-version product development brief for internal review and supplier communication.",
        },
        {
            "stage": "Knitting / SWS Proposal",
            "status": "planned",
            "certainty": "high_confidence",
            "description": "Translate the approved brief into knitting structure, yarn, machine, and SWS-oriented direction.",
        },
        {
            "stage": "Sampling Plan",
            "status": "planned",
            "certainty": "medium_confidence",
            "description": "Estimate sample path, timing, risks, and information required for sampling.",
        },
        {
            "stage": "Handoff",
            "status": "placeholder",
            "certainty": "needs_process_definition",
            "description": "Package context for designers, SWS engineers, suppliers, or future system integrations.",
        },
    ]


def service_state_flow() -> list[dict]:
    return [
        {
            "stage": "Identity / Intent Detection",
            "status": "implemented",
            "certainty": "confirmed",
            "description": "Main Agent infers whether the user is reporting a customer-side equipment/service issue from natural language and session context.",
        },
        {
            "stage": "Service Intake",
            "status": "in_progress",
            "certainty": "confirmed",
            "description": "Collect machine model, serial number, symptom, alarm evidence, and basic production impact.",
        },
        {
            "stage": "Impact & Urgency Check",
            "status": "in_progress",
            "certainty": "confirmed",
            "description": "Classify stopped production, reduced speed, running risk, installation support, and urgency level.",
        },
        {
            "stage": "Online Assist",
            "status": "in_progress",
            "certainty": "high_confidence",
            "description": "Offer safe first checks and match future service cases before deciding whether onsite support is required.",
        },
        {
            "stage": "Escalation Decision",
            "status": "planned",
            "certainty": "needs_service_case_list",
            "description": "Decide whether the issue is online-solvable, needs remote expert help, or requires onsite dispatch.",
        },
        {
            "stage": "Ticket Creation",
            "status": "in_progress",
            "certainty": "confirmed",
            "description": "Create a service ticket only after minimum information and dispatch confirmation are present.",
        },
        {
            "stage": "Dispatch Tracking",
            "status": "placeholder",
            "certainty": "needs_ticket_system_integration",
            "description": "Track assigned engineer, ETA, spare parts, onsite status, and customer updates.",
        },
        {
            "stage": "Close / Feedback",
            "status": "placeholder",
            "certainty": "needs_process_definition",
            "description": "Capture resolution, parts used, downtime, customer feedback, and future case-learning data.",
        },
    ]


def athena_mvp_state_flow() -> list[dict]:
    return [
        {
            "stage": "Design Request / Style3D-CLO-AI-Image-TP Intake",
            "status": "implemented_mock",
            "certainty": "confirmed_by_athena_v1_architecture",
            "description": "Normalize design-request, Style3D, CLO, AI image, reference image, or technical-package inputs into a design_request object.",
        },
        {
            "stage": "SWS/Arachne Engineering Brief",
            "status": "implemented_mock",
            "certainty": "confirmed_by_athena_v1_architecture",
            "description": "Convert the design_request object into machine, yarn, zone-structure, and parameter assumptions for SWS/Arachne review.",
        },
        {
            "stage": "Manufacturability Check",
            "status": "implemented_mock",
            "certainty": "confirmed_by_athena_v1_architecture",
            "description": "Score explicit knitting risks before sampling and keep blocked actions separate from recommendations.",
        },
        {
            "stage": "Sampling Feedback",
            "status": "implemented_mock",
            "certainty": "confirmed_by_athena_v1_architecture",
            "description": "Capture sample-round notes, defect signals, and missing physical evidence as workflow objects.",
        },
        {
            "stage": "Revision Suggestion",
            "status": "implemented_mock",
            "certainty": "confirmed_by_athena_v1_architecture",
            "description": "Generate parameter-level revision suggestions with reason, tradeoff, and next owner.",
        },
        {
            "stage": "Production Readiness",
            "status": "implemented_mock",
            "certainty": "confirmed_by_athena_v1_architecture",
            "description": "Calculate a readiness gate and checklist while preserving human engineer approval.",
        },
    ]


def production_operations_state_flow() -> list[dict]:
    return [
        {
            "stage": "Order Intake",
            "status": "implemented_mock",
            "certainty": "confirmed_by_production_mvp_plan",
            "description": "Normalize order demand, customer, style, quantity, due date, and priority into a production order object.",
        },
        {
            "stage": "ERP Input",
            "status": "implemented_mock",
            "certainty": "confirmed_by_production_mvp_plan",
            "description": "Track ERP sync state, exceptions, and order completeness without writing back to ERP.",
        },
        {
            "stage": "APS Scheduling",
            "status": "implemented_mock",
            "certainty": "confirmed_by_production_mvp_plan",
            "description": "Expose APS schedule, work-order release, machine assignment, changeover, and planner notes through a read-only contract.",
        },
        {
            "stage": "IOT Execution",
            "status": "implemented_mock",
            "certainty": "confirmed_by_production_mvp_plan",
            "description": "Expose machine state, OEE, downtime, alarms, setup status, and .co/.cx file evidence without upload or control actions.",
        },
        {
            "stage": "Production Monitoring / Service Escalation",
            "status": "implemented_mock",
            "certainty": "confirmed_by_production_mvp_plan",
            "description": "Monitor people, machine, material, method, environment, and measurement signals, rank evidence-backed management priorities, and prepare service request candidates when production recovery needs support.",
        },
        {
            "stage": "Garment Output",
            "status": "implemented_mock",
            "certainty": "confirmed_by_production_mvp_plan",
            "description": "Summarize planned quantity, estimated good garments, quality holds, and output-readiness evidence.",
        },
    ]


def hermes_integration_state_flow() -> list[dict]:
    return [
        {
            "stage": "Hermes Boundary",
            "status": "implemented_mock",
            "certainty": "confirmed_by_athena_architecture",
            "description": "Position Hermes as Athena runtime, memory, tool orchestration, and self-evolution layer while keeping Santoni Agent Core as the domain workflow system of record.",
        },
        {
            "stage": "Adapter Contract",
            "status": "implemented_mock",
            "certainty": "confirmed_by_current_demo_scope",
            "description": "Expose local Hermes template, overview, and suggestion APIs without connecting to a live Hermes endpoint or storing credentials.",
        },
        {
            "stage": "Memory Event Candidates",
            "status": "implemented_mock",
            "certainty": "confirmed_by_pmo_data",
            "description": "Normalize architecture decisions, PMO data, production boundaries, and next development direction into Athena memory-event candidates.",
        },
        {
            "stage": "Development Suggestion Loop",
            "status": "implemented_mock",
            "certainty": "confirmed_by_hermes_mvp_plan",
            "description": "Generate evidence-based development suggestions for Hermes, Production, and evaluation work without automatic code changes.",
        },
        {
            "stage": "Human Review Gate",
            "status": "implemented_mock",
            "certainty": "high_confidence",
            "description": "Require human review before any Hermes memory write, production adapter change, service handoff, or code change becomes implemented.",
        },
        {
            "stage": "Live Hermes Connector",
            "status": "planned",
            "certainty": "needs_hermes_endpoint_schema_auth",
            "description": "Replace the local mock contract with a real HTTP or MCP Hermes connector after endpoint, schema, auth, and retention rules are confirmed.",
        },
    ]


def training_automation_state_flow() -> list[dict]:
    return [
        {
            "stage": "Training Pack Intake",
            "status": "implemented_mock",
            "certainty": "confirmed_by_tianpai_training_pack",
            "description": "Load the structured Tianpai training pack, including VOC, IOT exports, workflow notes, data-quality findings, candidate tasks, and training governance.",
        },
        {
            "stage": "Task Queue Generation",
            "status": "implemented_mock",
            "certainty": "confirmed_by_current_training_scope",
            "description": "Convert candidate Tianpai tasks into an automatic evaluation queue for management priority, data boundaries, downtime, scrap, fault, cost, workflow, and process-stage capabilities.",
        },
        {
            "stage": "Automatic Evaluation Run",
            "status": "implemented_mock",
            "certainty": "confirmed_by_current_training_scope",
            "description": "Run deterministic local evaluation checks for evidence resolution, governance alignment, known data gaps, scoring, and task status without manual task-by-task review.",
        },
        {
            "stage": "Hermes Result JSON",
            "status": "mock_contract",
            "certainty": "needs_live_hermes_runner",
            "description": "Emit Hermes-style training result JSON with scope, tenant, retention, sensitivity, promotion status, task scores, evidence references, and next actions.",
        },
        {
            "stage": "Codex Work Packet Queue",
            "status": "mock_contract",
            "certainty": "confirmed_by_current_training_scope",
            "description": "Prepare read-only Codex work packet drafts from approved training iteration proposals, including validation requirements and blocked actions before any future worktree or runner execution.",
        },
        {
            "stage": "Codex Patch / Data Queue",
            "status": "mock_contract",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Prepare read-only Codex patch candidates from ready work packets and keep training signal queues visible, while blocking branch creation, commits, PRs, live Hermes writes, and real data integration.",
        },
        {
            "stage": "Codex Execution Gate",
            "status": "mock_contract",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Convert ready patch candidates into pending human-reviewed execution candidates and block all patch execution until explicit confirmation is defined.",
        },
        {
            "stage": "Codex Execution Gate Review",
            "status": "implemented_mock",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Record metadata-only execution review decisions such as approved-for-worktree, needs-changes, deferred, rejected, or note-only without executing code.",
        },
        {
            "stage": "Codex Worktree Preparation Queue",
            "status": "mock_contract",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Convert approved execution reviews into read-only worktree preparation task drafts without creating branches, applying patches, committing, pushing, or opening PRs.",
        },
        {
            "stage": "Codex Worktree Launch Gate",
            "status": "mock_contract",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Convert ready worktree preparation tasks into read-only launch request drafts with preflight checks and suggested user instructions, while blocking all git and patch actions until an explicit user command.",
        },
        {
            "stage": "Codex Worktree Result Intake",
            "status": "implemented_mock",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Record metadata-only result summaries, changed-file paths, validation statuses, and blocked actions after an explicitly user-launched Codex worktree task.",
        },
        {
            "stage": "Codex Worktree Result Review Gate",
            "status": "implemented_mock",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Review validated worktree results into regression or Hermes memory candidates without automatic promotion, merge, commit, push, PR, or live Hermes write.",
        },
        {
            "stage": "Codex Promotion Candidate Queue",
            "status": "mock_contract",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Prepare read-only regression baseline and Hermes memory promotion candidates from approved result reviews without promoting baselines or writing live memory.",
        },
        {
            "stage": "Codex Promotion Approval Gate",
            "status": "implemented_mock",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Record product-owner decisions on promotion candidates and prepare future action plans without executing baseline promotion, live Hermes writes, git actions, or real data integration.",
        },
        {
            "stage": "Codex Promotion Handoff Queue",
            "status": "mock_contract",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Convert approved-but-not-executed future promotion actions into manual handoff contracts with owners, preflight checks, suggested user confirmation, and execution evidence requirements.",
        },
        {
            "stage": "Codex Promotion Execution Readiness Gate",
            "status": "mock_contract",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Evaluate promotion handoff items for missing execution prerequisites before any real baseline promotion or live Hermes memory write can be considered.",
        },
        {
            "stage": "Codex Promotion Execution Readiness Review",
            "status": "implemented_mock",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Record metadata-only product-owner readiness decisions so execution prerequisites can be confirmed, deferred, rejected, or sent back for more inputs without executing promotion.",
        },
        {
            "stage": "Codex Promotion Execution Result Intake",
            "status": "implemented_mock",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Record metadata-only summaries after explicitly manual promotion execution outside the demo, without performing baseline promotion, live Hermes writes, or git actions.",
        },
        {
            "stage": "Codex Promotion Closure / Hermes Sync Audit",
            "status": "implemented_mock",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Audit whether metadata-only promotion execution results are complete enough for future regression baseline or Hermes synchronization review, without performing any live sync or baseline update.",
        },
        {
            "stage": "Codex Promotion Sync Review Gate",
            "status": "implemented_mock",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Record metadata-only product-owner review decisions for future regression baseline or Hermes sync candidates while blocking all baseline updates, live Hermes writes, and git actions.",
        },
        {
            "stage": "Codex Promotion Sync Handoff Queue",
            "status": "mock_contract",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Convert approved future sync actions into manual handoff contracts with target system, owner role, preflight checks, suggested instruction, and required execution evidence.",
        },
        {
            "stage": "Codex Promotion Sync Execution Readiness Gate",
            "status": "mock_contract",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Evaluate manual sync handoff items for missing execution prerequisites before any regression baseline update or live Hermes memory write is considered.",
        },
        {
            "stage": "Codex Promotion Sync Execution Readiness Review",
            "status": "implemented_mock",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Record metadata-only prerequisite review decisions for sync execution readiness items without performing any regression baseline update or live Hermes memory write.",
        },
        {
            "stage": "Codex Promotion Sync Execution Result Intake",
            "status": "implemented_mock",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Record metadata-only summaries after explicitly manual sync execution outside the demo, without updating regression baselines, writing live Hermes memory, storing raw files, or running git actions.",
        },
        {
            "stage": "Codex Promotion Sync Closure Audit",
            "status": "implemented_mock",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Audit whether metadata-only manual sync execution results are complete enough for final review, while still blocking real regression baseline updates, live Hermes memory writes, raw-file storage, credentials, and git actions.",
        },
        {
            "stage": "Codex Promotion Sync Closure Review Gate",
            "status": "implemented_mock",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Record metadata-only final sync closure review decisions and prepare approved-but-not-executed future real sync action plans while still blocking baseline updates, live Hermes writes, raw-file storage, credentials, and git actions.",
        },
        {
            "stage": "Codex Promotion Final Sync Handoff Queue",
            "status": "mock_contract",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Convert approved final sync closure review actions into manual final sync handoff contracts with owner roles, required real-sync inputs, suggested instructions, and execution evidence requirements while still blocking baseline updates, live Hermes writes, raw-file storage, credentials, and git actions.",
        },
        {
            "stage": "Codex Promotion Final Sync Execution Readiness Gate",
            "status": "mock_contract",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Evaluate final sync handoff contracts for missing real-system prerequisites such as endpoint/store contracts, auth, schema, tenant/factory scope, retention, rollback planning, current validation output, execution evidence plan, and product-owner confirmation before any real baseline update or live Hermes write is considered.",
        },
        {
            "stage": "Codex Promotion Final Sync Execution Result Intake",
            "status": "implemented_mock",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Record metadata-only result summaries after explicit manual final sync execution outside the demo, including changed records, validation summaries, rollback summaries, and validation command summaries while blocking baseline updates, live Hermes writes, raw-file storage, credentials, git actions, and real data integration.",
        },
        {
            "stage": "Codex Promotion Final Sync Closure Audit",
            "status": "implemented_mock",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Audit whether metadata-only final sync execution results are complete enough for final completion review while still blocking baseline updates, live Hermes writes, project-memory publication, raw-file storage, credentials, and git actions.",
        },
        {
            "stage": "Codex Promotion Final Completion Review Gate",
            "status": "implemented_mock",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Record metadata-only final completion review decisions and prepare approved-but-not-published future publication plans while still blocking project-memory publication, baseline updates, live Hermes writes, raw-file storage, credentials, and git actions.",
        },
        {
            "stage": "Codex Promotion Final Publication Handoff Queue",
            "status": "mock_contract",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Convert approved final completion publication plans into manual final publication handoff contracts with target systems, owner roles, required publication inputs, publication evidence, and suggested instructions while still blocking project-memory publication, baseline updates, live Hermes writes, raw-file storage, credentials, and git actions.",
        },
        {
            "stage": "Codex Promotion Final Publication Readiness Gate",
            "status": "mock_contract",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Evaluate final publication handoff contracts for missing endpoint, auth, schema, baseline store, version label, tenant/factory scope, retention, rollback, validation, evidence-capture, and product-owner confirmation prerequisites while still blocking project-memory publication, baseline updates, live Hermes writes, raw-file storage, credentials, and git actions.",
        },
        {
            "stage": "Codex Promotion Final Publication Result Intake",
            "status": "implemented_mock",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Record metadata-only result summaries after explicit manual final publication outside the demo, including publication references, published record identifiers, validation summaries, rollback summaries, and validation command evidence while blocking project-memory publication, baseline updates, live Hermes writes, raw-file storage, credentials, and git actions.",
        },
        {
            "stage": "Codex Promotion Final Publication Closure Audit",
            "status": "implemented_mock",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Audit whether metadata-only final publication results are complete enough for final release/archive review while still blocking project-memory publication, baseline updates, live Hermes writes, raw-file storage, credentials, git actions, and real data integration.",
        },
        {
            "stage": "Codex Promotion Final Release / Archive Review Gate",
            "status": "implemented_mock",
            "certainty": "confirmed_by_automation_boundary",
            "description": "Prepare product-owner final release and archive review candidates from complete final publication closure metadata while still blocking archive creation, project-memory publication, baseline updates, live Hermes writes, raw artifact storage, credentials, git actions, and real data integration.",
        },
        {
            "stage": "Live Hermes Runner",
            "status": "planned",
            "certainty": "needs_hermes_endpoint_schema_auth",
            "description": "Replace the local deterministic evaluator with a real Hermes training runner after endpoint, auth, schema, retention, and tool-call permissions are confirmed.",
        },
    ]


def operating_model_progress() -> dict:
    designer_goal = GoalInterface(
        primary_goal=(
            "Starting from a design reference image or natural-language idea, help brand designers form a first-version "
            "product development proposal that can support internal review, sampling communication, and later Santoni/SWS conversion."
        ),
        success_criteria=[
            "The agent understands design intent before generating a technical proposal.",
            "The output can support internal design review and supplier/sampling communication.",
            "The agent identifies feasibility, risks, missing information, and next decisions.",
            "When information is sufficient, the agent can translate the brief into a knitting/SWS-oriented technical direction.",
        ],
        failure_modes=[
            "Generating a knitting/SWS proposal before design intent is clear.",
            "Treating a reference image as enough context without asking about user, market, function, and constraints.",
            "Ignoring cost, lead time, brand line, and supplier communication concerns.",
        ],
    )
    service_goal = GoalInterface(
        primary_goal=(
            "Act as the customer-side Santoni service assistant: understand the customer's equipment problem, "
            "help restore production as quickly as possible, solve online whenever safe and feasible, and create/dispatch "
            "a service ticket only when online resolution is insufficient or onsite support is required."
        ),
        success_criteria=[
            "The agent first understands the machine, symptom, production impact, and available evidence.",
            "The agent attempts safe online assistance before dispatch when the issue is suitable for remote handling.",
            "The agent avoids unsafe machine-control instructions and escalates high-risk or production-stopping issues.",
            "When dispatch is needed, the ticket contains enough context for Santoni service leader and onsite engineer.",
            "Future service-case lists can define which issues are online-solvable.",
        ],
        failure_modes=[
            "Dispatching a ticket before collecting the minimum service information.",
            "Giving unsafe or overconfident repair instructions to customer engineers.",
            "Failing to escalate production-stopping, safety-related, or repeated failures.",
            "Ignoring online-solvable issues and sending engineers unnecessarily.",
        ],
    )

    capabilities = [
        OperatingModelCapability(
            key="goal",
            name="Goal / Success Criteria",
            status="in_progress",
            progress=70,
            purpose="Define what each agent is trying to achieve and what good output means.",
            current_scope="Designer and Service Agent goals are defined. Online-solvable service case list is pending.",
            next_step="Define workflow states for Designer and Service Agents.",
        ),
        OperatingModelCapability(
            key="state",
            name="State",
            status="in_progress",
            progress=72,
            purpose="Track workflow stage, known information, and missing information.",
            current_scope="Designer and Service state flows are captured. Service Manager Console now exposes review state, editable case state, and handoff payload previews.",
            next_step="Connect customer conversations to explicit service stage labels and stage transitions.",
        ),
        OperatingModelCapability(
            key="guardrails",
            name="Guardrails",
            status="planned",
            progress=10,
            purpose="Prevent unsafe actions, premature dispatch, or overconfident recommendations.",
            current_scope="Some behavior is implicit in routing, but no formal guardrail engine exists yet.",
            next_step="Define non-negotiable rules for service, design, and customer-facing output.",
        ),
        OperatingModelCapability(
            key="workflow_template_governance",
            name="Workflow Template Governance",
            status="in_progress",
            progress=62,
            purpose="Ensure Athena capabilities land as structured templates with inputs, outputs, owners, tools, evidence, gates, and KPIs.",
            current_scope="Design Intake Structuring, Production Operations, and Hermes Integration consoles implement deterministic local workflow templates with evidence and KPI logs.",
            next_step="Validate the template fields with SWS/Arachne, APS, IOT, Hermes, sampling, and production stakeholders.",
        ),
        OperatingModelCapability(
            key="runtime_memory_orchestration",
            name="Runtime / Memory / Tool Orchestration",
            status="in_progress",
            progress=43,
            purpose="Connect Athena to Hermes as a controlled runtime, project memory, tool orchestration, and development suggestion layer.",
            current_scope="Hermes local adapter contract, memory-event candidates, chat runtime-event envelopes, tool registry candidates, development suggestion loop, and automatic training result contract are available as mock-backed APIs.",
            next_step="Confirm real Hermes endpoint, auth, memory schema, retention policy, HTTP-vs-MCP integration route, runtime-event ingestion, and training-runner JSON schema.",
        ),
        OperatingModelCapability(
            key="handoff",
            name="Handoff",
            status="placeholder",
            progress=25,
            purpose="Package context for designers, technicians, service leaders, SWS, or ticket systems.",
            current_scope="Mock ticket payloads and Service Manager Console handoff payload previews exist. Real CRM/ticket write-back is not connected.",
            next_step="Confirm the CRM/ticket payload schema with service managers before integration.",
        ),
        OperatingModelCapability(
            key="evaluation",
            name="Evaluation",
            status="in_progress",
            progress=28,
            purpose="Self-check whether the response answers the user and whether more information is needed.",
            current_scope="Training Automation Console now runs deterministic local evaluation over Tianpai training tasks, evidence references, governance rules, known data gaps, Hermes-style result JSON, approved baseline regression promotion, playbook regression queue, local automatic regression runs, regression gate decisions, next-loop handoff queues, metadata-only handoff review decisions, next-loop closure-gate readiness, read-only training iteration proposals, metadata-only proposal review decisions, read-only Codex work packet queues, read-only Codex patch queue contracts, read-only Codex execution gates, metadata-only Codex execution gate reviews, read-only Codex worktree preparation queues, read-only Codex worktree launch gates, metadata-only Codex worktree result intake, metadata-only Codex worktree result review gates, read-only Codex promotion candidate queues, metadata-only Codex promotion approval gates, read-only Codex promotion handoff queues, read-only Codex promotion execution readiness gates, metadata-only Codex promotion execution readiness reviews, metadata-only Codex promotion execution result intake, read-only Codex promotion closure / Hermes sync audit, metadata-only Codex promotion sync review gate, read-only Codex promotion sync handoff queue, read-only Codex promotion sync execution readiness gate, metadata-only Codex promotion sync execution readiness review, metadata-only Codex promotion sync execution result intake, read-only Codex promotion sync closure audit, metadata-only Codex promotion sync closure review gate, read-only Codex promotion final sync handoff queue, read-only Codex promotion final sync execution readiness gate, metadata-only Codex promotion final sync execution result intake, read-only Codex promotion final sync closure audit, metadata-only Codex promotion final completion review gate, read-only Codex promotion final publication handoff queue, read-only Codex promotion final publication readiness gate, and metadata-only Codex promotion final publication result intake.",
            next_step="Connect a real Hermes training runner and expand baseline regression beyond Tianpai production training into service, design, and guardrail sets.",
        ),
    ]

    return {
        "version": "v0.113.1",
        "capabilities": [asdict(item) for item in capabilities],
        "interfaces": {
            "goal": GoalInterface.__name__,
            "state": StateInterface.__name__,
            "guardrails": GuardrailsInterface.__name__,
            "handoff": HandoffInterface.__name__,
            "evaluation": EvaluationInterface.__name__,
        },
        "agent_goals": {
            "designer": asdict(designer_goal),
            "service": asdict(service_goal),
        },
        "state_flows": {
            "designer": designer_state_flow(),
            "service": service_state_flow(),
            "athena_mvp": athena_mvp_state_flow(),
            "production_operations": production_operations_state_flow(),
            "hermes_integration": hermes_integration_state_flow(),
            "training_automation": training_automation_state_flow(),
        },
    }


def project_documentation() -> dict:
    model = operating_model_progress()
    return {
        "version": "v0.113.1",
        "title": "AI Knitting Agent Product / Development Notes",
        "implemented_features": [
            {
                "name": "Natural-language identity routing",
                "status": "done",
                "description": "Main Agent can infer Designer, Service, or Production intent as a backend fallback, while the customer-facing page now prefers explicit identity selection for reliable routing.",
            },
            {
                "name": "Designer discovery workflow",
                "status": "in_progress",
                "description": "Designer Agent asks about product intent before producing a brief or SWS-oriented proposal.",
            },
            {
                "name": "Mock image input contract",
                "status": "done",
                "description": "Web demo accepts image attachments and routes metadata through a mock Image Understanding Agent.",
            },
            {
                "name": "Active LLM runtime status",
                "status": "done",
                "description": "Local demo startup now treats the current project .env as the active provider/model configuration and /api/status reports the normalized active LLM provider, model, and enabled state.",
            },
            {
                "name": "Chinese routing dictionary cleanup",
                "status": "done",
                "description": "MainAgent Chinese route terms now cover design, service, and Tianpai production-management vocabulary with regression coverage against mojibake reintroduction.",
            },
            {
                "name": "Athena structure PNG",
                "status": "done",
                "description": "The current Athena demo architecture is rendered as docs/athena_structure_v0.113.0.png with a reusable local rendering script.",
            },
            {
                "name": "Guided Demo Flow",
                "status": "done",
                "description": "Production Console now exposes a guided internal demo flow covering today's top three priorities, actual APS/ERP delivery risk, Athena verification drilldown, machine/style risk, hybrid Service risk, and local follow-up without writing external systems.",
            },
            {
                "name": "User Page GM Demo Entry",
                "status": "done",
                "description": "The customer-facing General Manager workspace now includes compact stable story shortcuts that send questions into the original chat stream and keep raw payloads, debug traces, and development notes out of the user page.",
            },
            {
                "name": "Presenter Mode",
                "status": "done",
                "description": "Athena now exposes presenter-safe narration sequence, recommended questions, and expected outputs for repeatable internal demos.",
            },
            {
                "name": "Evidence Boundary Layer",
                "status": "done",
                "description": "Production stories and risk contracts distinguish actual_export, mock_contract, hybrid, and data_gap evidence modes with manager-language allowed and blocked claims.",
            },
            {
                "name": "GM Question Regression Set",
                "status": "done",
                "description": "The general-manager regression set now covers today鈥檚 three priorities, delivery risk, machine/style fit, Service risk, material risk, and data-gap questions with required answer contracts.",
            },
            {
                "name": "Data Request Wizard",
                "status": "done",
                "description": "Athena generates next-round data requests for ERP, IOT, quality, labor, cost, and shipping, including fields, purpose, answerable questions, priority, sensitivity, and suggested owner.",
            },
            {
                "name": "Service Risk Confirmation Flow",
                "status": "done",
                "description": "Service risk candidates now expand into a confirmation flow with machine, order impact, evidence, maintenance questions, and no-auto-dispatch boundaries.",
            },
            {
                "name": "Visible Athena Skill Process",
                "status": "done",
                "description": "Athena can show which management-facing abilities were used, such as checking orders, schedules, machine specs, materials, Service candidates, and data gaps without exposing raw debug traces.",
            },
            {
                "name": "Hermes Training / Memory Review",
                "status": "done",
                "description": "Demo questions, follow-ups, data gaps, and feedback can be converted into local Hermes memory/training candidates with scope, tenant/factory, source, retention, sensitivity, and promotion fields.",
            },
            {
                "name": "Internal Demo Candidate Report",
                "status": "done",
                "description": "The internal demo candidate report documents demoable capabilities, actual APS/ERP evidence, mock/hybrid boundaries, test questions, data gaps, and readiness recommendations for controlled internal presentation.",
            },
            {
                "name": "General Manager Dashboard Hierarchy",
                "status": "done",
                "description": "The customer-facing General Manager page opens with daily KPI monitoring, keeps the top-three priorities as the decision focus, and compresses Athena drilldown into one management-facing answer with expandable evidence and data-boundary details.",
            },
            {
                "name": "Actual Export Evidence Sanity Guard",
                "status": "done",
                "description": "The Tianpai APS/ERP export adapter reads no-header CSV by the 琛ㄥ瓧娈?DDL order, filters deleted rows, and marks stale delivery dates or extreme planned-vs-reported quantity gaps as evidence-reconciliation candidates before Athena can present them as management conclusions.",
            },
            {
                "name": "Machine Style Root Cause Evidence",
                "status": "done",
                "description": "The v0.108.2 machine/style mismatch analysis includes required Style_Component cylinder/needle values, actual T_Machine_Info machine cylinder/needle values, and structured mismatch details so Athena can explain the root cause instead of only naming the mismatched field.",
            },
            {
                "name": "Delivery Risk Driver Guard",
                "status": "done",
                "description": "The v0.108.3 delivery-risk analysis records explicit risk drivers and downgrades essentially completed but inconsistent orders into delivery status or quantity reconciliation candidates before Athena can claim a hard delivery risk.",
            },
            {
                "name": "Evidence Review Queue",
                "status": "done",
                "description": "The v0.109.0 Production workflow exposes evidence_review_queue and /api/production/evidence-review so planning/status or quantity reconciliation candidates stay separate from hard General Manager risks.",
            },
            {
                "name": "GM First Screen Hierarchy Polish",
                "status": "done",
                "description": "The v0.113.0 customer-facing General Manager page is organized as KPI dashboard, top-three hard risks, evidence review candidates, Service/equipment risk candidates, and the original chat stream for all drilldowns.",
            },
            {
                "name": "General Manager Decision UI Compression",
                "status": "done",
                "description": "The v0.111.0 user page compresses Production drilldown answers into conclusion, evidence support, suggested confirmation owner, and next action, while detailed evidence remains expandable.",
            },
            {
                "name": "Local Decision Follow-up Board",
                "status": "done",
                "description": "The v0.112.0 decision loop lets hard risk, evidence review, and Service risk cards generate metadata-only follow-ups with source card type, related object, confirmation need, Athena reason, evidence refs, and read-only boundary.",
            },
            {
                "name": "Daily Brief Narrative",
                "status": "done",
                "description": "The v0.113.0 General Manager page generates a three-minute daily brief from top-three priorities, evidence review candidates, Service risks, confirmation owners, impact focus, and evidence boundary.",
            },
            {
                "name": "Athena PRD v0.1",
                "status": "done",
                "description": "Customer-facing PRD draft defines Athena as a digital general manager focused on Production and Service risks, three-priority first screen, evidence-backed drill-down, local follow-up items, and explicit permission boundaries.",
            },
            {
                "name": "Athena PRD visible entry",
                "status": "done",
                "description": "Athena.html now shows a PRD v0.1 entry section at the top of the page and links to the full in-page detail section and Markdown PRD file.",
            },
            {
                "name": "Athena PRD web route",
                "status": "done",
                "description": "The local demo server can now serve docs/Athena.html at /Athena.html and linked project docs from the read-only docs route.",
            },
            {
                "name": "Developer page API interaction fix",
                "status": "done",
                "description": "Developer.html now exposes direct API status/model/docs links and the developer app script has clean UTF-8 strings so identity selection and chat testing bind correctly.",
            },
            {
                "name": "User-page General Manager agent workspace",
                "status": "done",
                "description": "The customer-facing home page now exposes a 鎬荤粡鐞?identity button that opens the Production priority brief, risk cards, and Santoni Athena root-cause drilldown in the same user flow.",
            },
            {
                "name": "Unified General Manager conversation flow",
                "status": "done",
                "description": "General Manager follow-up questions and risk-card drilldowns on the customer-facing home page now use the original bottom chat box and append to the same conversation history.",
            },
            {
                "name": "General Manager follow-up loop demo",
                "status": "done",
                "description": "Customer-facing General Manager risk cards can now generate local follow-up todos, show owner/evidence/status context, update metadata-only status, and continue Athena drilldown from the same todo without writing APS, ERP, IOT, Hermes memory, ticket systems, or machine controls.",
            },
            {
                "name": "Developer General Manager flow parity",
                "status": "done",
                "description": "Developer/debug page General Manager selection now triggers the same Production three-priority brief and routes follow-up test input through the same read-only Santoni Athena production evidence API used by the customer-facing page.",
            },
            {
                "name": "General Manager 3-minute production brief",
                "status": "done",
                "description": "Production Console now opens with a three-priority general-manager brief driven by evidence-backed management priorities, owner confirmation gates, affected objects, and recommended actions.",
            },
            {
                "name": "First-screen Service Risk brief",
                "status": "done",
                "description": "Production Console now shows an independent first-screen Service Risk section for stopped machines, alarm signals, affected orders, evidence references, and candidate-only service context.",
            },
            {
                "name": "Internal Demo Readiness Mode",
                "status": "done",
                "description": "Production workflow now exposes internal_demo_readiness_mode for Codex completion reports and internal documentation; the customer-facing General Manager page does not show this internal guidance.",
            },
            {
                "name": "General Manager Demo UX Polish",
                "status": "done",
                "description": "The customer-facing General Manager page now keeps first-screen content focused on today's priorities, Service/equipment risk, evidence details, and local follow-up instead of showing internal demo readiness, development progress, version-style summaries, or raw payload content.",
            },
            {
                "name": "Athena verification process visualization",
                "status": "done",
                "description": "Production drilldown answers now expose a manager-facing verification_process with checked objects, findings, evidence level, cannot-conclude/data-gap statements, suggested confirmation owner, and read-only blocked actions while hiding raw debug trace from the user page.",
            },
            {
                "name": "Stable General Manager Demo Story Pack",
                "status": "done",
                "description": "Production Console now exposes a repeatable three-story internal demo pack that separates actual APS/ERP export evidence, clearly labeled mock IOT/Service supplements, data gaps, suggested owners, evidence refs, and one-click Santoni Athena drilldown questions.",
            },
            {
                "name": "Risk card drill-down actions",
                "status": "done",
                "description": "Production Console risk cards can now launch structured Santoni Athena drill-down questions into the read-only root-cause panel, linking general-manager priorities and service candidates back to affected orders, machines, evidence, and permission boundaries.",
            },
            {
                "name": "PRD first-screen risk-card alignment",
                "status": "done",
                "description": "Production Management Priority Engine now follows the Athena PRD first-screen structure: delivery-risk order, quality/replenishment risk, and labor effective-hour risk, with delivery > quality > cost as the priority policy and cost treated as a consequence metric.",
            },
            {
                "name": "PRD risk-card evidence detail layer",
                "status": "done",
                "description": "Production first-screen risk cards now expose PRD-required risk level, key evidence preview, full evidence details with evidence level, data gaps, and linked follow-up risk-card IDs while remaining read-only.",
            },
            {
                "name": "PRD follow-up status lifecycle",
                "status": "done",
                "description": "Production local follow-up items now use the PRD status lifecycle: pending_confirmation, assigned, waiting_evidence, confirmed, closed, and unable_to_process, with matching console controls and metadata-only review updates.",
            },
            {
                "name": "PRD first-screen management summary",
                "status": "done",
                "description": "Production Management Priority Engine now produces a 3-5 line bilingual first-screen management summary covering delivery, quality/replenishment, labor effective hours, and data boundary, and the console renders it above the risk cards.",
            },
            {
                "name": "Lock-machine activation-password service tool",
                "status": "done",
                "description": "Service Agent can run the controlled lock-machine activation-password flow in mock or experimental real-platform mode.",
            },
            {
                "name": "Service Case Online Assist Mock",
                "status": "done",
                "description": "Service Agent matches structured service cases and returns online troubleshooting guidance before dispatch.",
            },
            {
                "name": "Recent service case distilled library",
                "status": "done",
                "description": "Recent service report data from 2026-04-18 to 2026-05-18 is distilled into eight mock service skills.",
            },
            {
                "name": "Service follow-up context guard",
                "status": "done",
                "description": "Split-input customer conversations preserve the current issue and avoid accidental tool misrouting.",
            },
            {
                "name": "Guided service troubleshooting follow-up",
                "status": "done",
                "description": "Service Agent can answer follow-up diagnostic questions and record observations during online assistance.",
            },
            {
                "name": "Service Case Library review page",
                "status": "done",
                "description": "Readonly web page shows available mock cases, review status, customer visibility, steps, risks, and dispatch triggers.",
            },
            {
                "name": "Operation guide page",
                "status": "done",
                "description": "Business testers can open a guide page to understand demo scope, usage method, functions, limitations, and testing suggestions.",
            },
            {
                "name": "Excel auto importer",
                "status": "done",
                "description": "CLI importer reads monthly service Excel files and generates draft service-case JSON for human review.",
            },
            {
                "name": "Case approval workflow",
                "status": "done",
                "description": "Service reviewers can approve, request changes, or mark cases internal-only from the Service Case Library.",
            },
            {
                "name": "Service Manager Console",
                "status": "done",
                "description": "Service managers can review case readiness, edit case knowledge, inspect diffs, and preview future CRM/ticket handoff payloads.",
            },
            {
                "name": "Developer changelog preview",
                "status": "done",
                "description": "Developer page now shows the latest changelog entries directly in the sidebar while retaining the full changelog link.",
            },
            {
                "name": "Design Intake Structuring Console",
                "status": "done",
                "description": "Structured testbench and API normalize design/Style3D/CLO/AI-image/TP inputs into design_request, source_asset, engineering-brief candidate, manufacturability-check, sampling-feedback, revision-suggestion, evidence-log, and KPI objects for schema review.",
            },
            {
                "name": "Production Operations Console",
                "status": "done",
                "description": "Management-facing console and API monitor order intake, ERP, APS, IOT, production, service escalation candidates, garment output, 娴滅儤婧€閺傛瑦纭堕悳顖涚ゴ resource lenses, optimization signals, evidence logs, and KPI logs using local mock data.",
            },
            {
                "name": "Santoni Athena production insight",
                "status": "done",
                "description": "Production console includes Santoni Athena as a read-only question-to-data agent that explains KPI changes such as scrap rate, OEE, downtime, material risk, and order delay through structured root causes, recommended actions, drilldowns, and evidence references.",
            },
            {
                "name": "Main chat production-manager routing",
                "status": "done",
                "description": "The customer-facing /api/chat entry now detects production-manager, order, delivery, scheduling, KPI, and root-cause questions and routes them to production_athena instead of the old Designer/Service clarification path.",
            },
            {
                "name": "Athena runtime event envelope",
                "status": "done",
                "description": "Every Main Agent chat response now includes an athena_runtime_event object for Hermes-ready workflow, persona, intent, evidence, data-boundary, memory-event candidate, and blocked-action metadata without storing raw user text or credentials.",
            },
            {
                "name": "Production order-id workflow spine",
                "status": "done",
                "description": "Production Operations template and page explicitly state that order_id / 鐠併垹宕熼崣?is the unique key joining order intake, ERP, APS, IOT, production/service candidates, and garment output.",
            },
            {
                "name": "Tianpai Material Risk v1",
                "status": "done",
                "description": "Production Operations now consumes aggregate Tianpai yarn inventory evidence as a read-only material-risk object with yarn code, batch, color, twist, supplier, task-order balance, zero/negative balance review, field mapping, and future ERP/APS/BOM/quality join blockers without storing raw inventory rows.",
            },
            {
                "name": "Tianpai Data Readiness v1",
                "status": "done",
                "description": "Production Operations now evaluates current APS, IOT, yarn inventory, VOC, ERP, BOM, and quality data-source readiness so Athena can say which general-manager questions are answerable, partial, or blocked and who should provide the next data source.",
            },
            {
                "name": "General Manager Question Bank v1",
                "status": "done",
                "description": "Production Operations now exposes a hypothesis-status question bank with question_id, priority, required sources, answer template, evidence requirements, data-gap behavior, and verification status for future Agnes/customer review and regression training.",
            },
            {
                "name": "Hermes Adapter Contract",
                "status": "done",
                "description": "Hermes Integration Console and API define Athena runtime, memory, tool orchestration, development suggestion, evidence, KPI, and blocked-action objects without live Hermes credentials or writeback.",
            },
            {
                "name": "Hermes memory event governance",
                "status": "done",
                "description": "Hermes memory events now carry scope, tenant_id, factory_id, source, retention_policy, sensitivity_level, and promotion_status so product, domain, tenant, and session memory can be governed separately.",
            },
            {
                "name": "Organization Memory / Playbook Engine v1",
                "status": "done",
                "description": "Hermes Integration now converts Production decision-loop follow-ups into organization_memory_playbook candidates with promotion gates, memory-event candidates, regression-case candidates, local metadata-only review state, and live-memory writeback blocked.",
            },
            {
                "name": "Playbook Regression Queue v1",
                "status": "done",
                "description": "Training Automation now consumes Hermes organization-memory playbook candidates and exposes approved, evidence-backed candidates as local playbook_regression_queue regression-case candidates while keeping unapproved candidates blocked.",
            },
            {
                "name": "Automatic Regression Runner v1",
                "status": "done",
                "description": "Training Automation now runs deterministic local automatic_regression_run checks over approved Tianpai baseline tasks and approved playbook regression candidates, reporting executable, passed, failed, blocked, pass-rate, evidence, and KPI objects without live Hermes execution.",
            },
            {
                "name": "Regression Gate v1",
                "status": "done",
                "description": "Training Automation now converts automatic_regression_run results into regression_gate decisions with pass-rate threshold, next-loop permission, human-review queue, Codex next-action queue, Hermes feedback payload, and blocked actions.",
            },
            {
                "name": "Next Loop Handoff v1",
                "status": "done",
                "description": "Training Automation now converts Regression Gate output into athena.next_loop_handoff.v1 with automatic work, human-review, and data-request queues plus a Hermes handoff payload while blocking automatic code writes, live Hermes memory writes, and real data integration.",
            },
            {
                "name": "Next Loop Handoff Review v1",
                "status": "done",
                "description": "Training Automation now records metadata-only review decisions for next-loop handoff items, including approve-for-next-loop, resolved, deferred, needs-data, rejected, and note-only states without executing blocked work.",
            },
            {
                "name": "Next Loop Closure Gate v1",
                "status": "done",
                "description": "Training Automation now evaluates handoff review decisions into athena.next_loop_closure_gate.v1 with local iteration permission, closure completeness, open/rejected handoff items, and a read-only local iteration plan.",
            },
            {
                "name": "Training Iteration Proposal v1",
                "status": "done",
                "description": "Training Automation now converts closure-gate output into athena.training_iteration_proposal.v1 with task seeds, open-item watchlist, confirmation boundary, Hermes proposal payload, KPI log, and evidence log without executing the iteration.",
            },
            {
                "name": "Training Iteration Proposal Review v1",
                "status": "done",
                "description": "Training Automation now records metadata-only proposal review decisions, including approved-for-queue, needs-changes, deferred, rejected, and note-only states, while keeping execution and code writes blocked.",
            },
            {
                "name": "Codex Work Packet Queue v1",
                "status": "done",
                "description": "Training Automation now converts approved training iteration proposals into read-only Codex work packet drafts with validation requirements, queue status, Hermes payload, KPI log, and evidence log while blocking automatic execution.",
            },
            {
                "name": "Codex Patch Queue Contract v1",
                "status": "done",
                "description": "Training Automation now converts ready Codex work packets into read-only patch candidates with validation requirements, training-signal context, Hermes payload, KPI log, and evidence log while blocking automatic patch application.",
            },
            {
                "name": "Codex Execution Gate v1",
                "status": "done",
                "description": "Training Automation now converts ready patch candidates into pending human-reviewed execution candidates and records the execution boundary while blocking automatic patch execution.",
            },
            {
                "name": "Codex Execution Gate Review v1",
                "status": "done",
                "description": "Training Automation now records metadata-only review decisions for Codex execution candidates, including approve-for-worktree, needs-changes, deferred, rejected, and note-only states without executing code.",
            },
            {
                "name": "Codex Worktree Preparation Queue v1",
                "status": "done",
                "description": "Training Automation now converts approved execution review records into read-only worktree preparation task drafts with expected result contracts and validation requirements while blocking actual branch creation and patch execution.",
            },
            {
                "name": "Codex Worktree Launch Gate v1",
                "status": "done",
                "description": "Training Automation now converts ready worktree preparation tasks into read-only launch request drafts with preflight checks and suggested user instructions while blocking git worktree creation, branch switching, patch application, commits, pushes, and PRs.",
            },
            {
                "name": "Codex Worktree Result Intake v1",
                "status": "done",
                "description": "Training Automation now records metadata-only worktree result summaries with changed-file paths and validation statuses while blocking raw patch storage, automatic merge, commits, pushes, PRs, live Hermes writes, and real data integration.",
            },
            {
                "name": "Codex Worktree Result Review Gate v1",
                "status": "done",
                "description": "Training Automation now records metadata-only worktree result review decisions and prepares regression/Hermes memory candidates while blocking automatic promotion, merge, commits, pushes, PRs, raw patch storage, and live Hermes writes.",
            },
            {
                "name": "Codex Promotion Candidate Queue v1",
                "status": "done",
                "description": "Training Automation now prepares read-only regression baseline and Hermes memory promotion candidates from approved result reviews while blocking actual baseline promotion, live Hermes writes, merges, commits, pushes, PRs, and raw patch storage.",
            },
            {
                "name": "Codex Promotion Approval Gate v1",
                "status": "done",
                "description": "Training Automation now records metadata-only product-owner decisions on promotion candidates and prepares approved-but-not-executed future action plans while blocking actual baseline promotion, live Hermes writes, merges, commits, pushes, PRs, and raw patch storage.",
            },
            {
                "name": "Codex Promotion Handoff Queue v1",
                "status": "done",
                "description": "Training Automation now converts approved-but-not-executed future promotion actions into manual handoff contracts with owner roles, preflight checks, suggested confirmation wording, and execution evidence requirements while blocking automatic baseline promotion, live Hermes writes, merges, commits, pushes, PRs, and raw patch storage.",
            },
            {
                "name": "Codex Promotion Execution Readiness Gate v1",
                "status": "done",
                "description": "Training Automation now evaluates manual promotion handoff items for missing execution prerequisites such as product-owner confirmation, fresh validation output, rollback planning, baseline target contract, and live Hermes endpoint/schema/auth scope before any real execution can be considered.",
            },
            {
                "name": "Codex Promotion Execution Readiness Review v1",
                "status": "done",
                "description": "Training Automation now records metadata-only product-owner review decisions for promotion execution readiness items and can mark prerequisites confirmed for final manual execution confirmation while still blocking automatic baseline promotion, live Hermes writes, commits, pushes, PRs, raw patch storage, and credentials.",
            },
            {
                "name": "Codex Promotion Execution Result Intake v1",
                "status": "done",
                "description": "Training Automation now records metadata-only result summaries after explicitly manual promotion execution outside the demo, including changed record identifiers and validation summaries while still blocking automatic baseline promotion, live Hermes writes, commits, pushes, PRs, raw patch storage, and credentials.",
            },
            {
                "name": "Codex Promotion Closure / Hermes Sync Audit v1",
                "status": "done",
                "description": "Training Automation now audits metadata-only promotion execution results for closure readiness and prepares future regression baseline or Hermes synchronization audit candidates while still blocking baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, and credentials.",
            },
            {
                "name": "Codex Promotion Sync Review Gate v1",
                "status": "done",
                "description": "Training Automation now records metadata-only product-owner review decisions for promotion sync audit candidates and creates approved-but-not-executed future sync action plans while still blocking baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, and credentials.",
            },
            {
                "name": "Codex Promotion Sync Handoff Queue v1",
                "status": "done",
                "description": "Training Automation now converts approved-but-not-executed future sync actions into manual handoff contracts with target systems, owner roles, preflight checks, suggested instructions, and execution evidence requirements while still blocking baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, and credentials.",
            },
            {
                "name": "Codex Promotion Sync Execution Readiness Gate v1",
                "status": "done",
                "description": "Training Automation now evaluates manual sync handoff items for missing baseline-update or live-Hermes prerequisites before any real sync execution can be considered, while still blocking baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, and credentials.",
            },
            {
                "name": "Codex Promotion Sync Execution Readiness Review v1",
                "status": "done",
                "description": "Training Automation now records metadata-only review decisions for sync execution readiness items, including confirmed-ready, needs-inputs, deferred, rejected, and note-only states while still blocking baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, and credentials.",
            },
            {
                "name": "Codex Promotion Sync Execution Result Intake v1",
                "status": "done",
                "description": "Training Automation now records metadata-only result summaries after explicitly manual sync execution outside the demo, including changed record identifiers and validation summaries while still blocking baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, and credentials.",
            },
            {
                "name": "Codex Promotion Sync Closure Audit v1",
                "status": "done",
                "description": "Training Automation now audits whether metadata-only manual sync execution results are complete enough for final review candidates while still blocking baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, and credentials.",
            },
            {
                "name": "Codex Promotion Sync Closure Review Gate v1",
                "status": "done",
                "description": "Training Automation now records metadata-only final sync closure review decisions and turns approved candidates into approved-but-not-executed future real sync action plans while still blocking baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and real data integration.",
            },
            {
                "name": "Codex Promotion Final Sync Handoff Queue v1",
                "status": "done",
                "description": "Training Automation now prepares manual final sync handoff contracts from approved closure-review future actions, including owner roles, required real-sync inputs, suggested instructions, and execution evidence requirements while still blocking baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and real data integration.",
            },
            {
                "name": "Codex Promotion Final Sync Execution Readiness Gate v1",
                "status": "done",
                "description": "Training Automation now evaluates final sync handoff contracts for missing baseline/Hermes execution prerequisites such as endpoint or store contracts, auth, schema, tenant/factory scope, retention, rollback planning, current validation output, execution evidence plan, and product-owner confirmation while still blocking any real baseline update or live Hermes write.",
            },
            {
                "name": "Codex Promotion Final Sync Execution Result Intake v1",
                "status": "done",
                "description": "Training Automation now records metadata-only result summaries after explicit manual final sync execution outside the demo, including changed records and validation evidence while still blocking baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and real data integration.",
            },
            {
                "name": "Codex Promotion Final Sync Closure Audit v1",
                "status": "done",
                "description": "Training Automation now audits whether final sync result records are complete enough for final completion review while still blocking baseline updates, live Hermes writes, project-memory publication, commits, pushes, PRs, raw file storage, credentials, and real data integration.",
            },
            {
                "name": "Codex Promotion Final Completion Review Gate v1",
                "status": "done",
                "description": "Training Automation now records metadata-only final completion review decisions, including approved, needs-inputs, deferred, rejected, and note-only states, then prepares approved-but-not-published future publication plans while still blocking project-memory publication, baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and real data integration.",
            },
            {
                "name": "Codex Promotion Final Publication Handoff Queue v1",
                "status": "done",
                "description": "Training Automation now converts approved final completion publication plans into metadata-only manual publication handoff contracts with target systems, owner roles, required publication inputs, publication evidence, and suggested user instructions while still blocking project-memory publication, baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and real data integration.",
            },
            {
                "name": "Codex Promotion Final Publication Readiness Gate v1",
                "status": "done",
                "description": "Training Automation now evaluates final publication handoff contracts for missing publication prerequisites before any project-memory publication, regression baseline update, or live Hermes write can be considered while still blocking real writes, commits, pushes, PRs, raw file storage, credentials, and real data integration.",
            },
            {
                "name": "Codex Promotion Final Publication Result Intake v1",
                "status": "done",
                "description": "Training Automation now records metadata-only result summaries after explicit manual final publication outside the demo, including publication references, published record identifiers, validation summaries, rollback summaries, and validation command evidence while still blocking project-memory publication, baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and real data integration.",
            },
            {
                "name": "Codex Promotion Final Publication Closure Audit v1",
                "status": "done",
                "description": "Training Automation now audits whether final publication result metadata is complete enough for final release/archive review, including expected, recorded, complete, missing, and failed result counts while still blocking project-memory publication, baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and real data integration.",
            },
            {
                "name": "Codex Promotion Final Release / Archive Review Gate v1",
                "status": "done",
                "description": "Training Automation now prepares product-owner final release and archive review candidates from complete final publication closure metadata while still blocking archive creation, project-memory publication, baseline updates, live Hermes writes, commits, pushes, PRs, raw artifact storage, credentials, and real data integration.",
            },
            {
                "name": "Tianpai training data pack",
                "status": "done",
                "description": "Agnes VOC screenshots and Melos-provided Tianpai IOT output, scrap, and fault exports are structured into a local training pack with normalized field maps, data-quality findings, aggregate KPI seeds, candidate training tasks, and Hermes tenant memory-event candidates.",
            },
            {
                "name": "Tianpai APS workflow fragment",
                "status": "done",
                "description": "The Tianpai training pack records the APS-side onsite workflow fragment and now registers the APS Planned Task delivery-time attachment as metadata-only schedule evidence, while keeping APS-to-IOT join-rule confirmation as the remaining blocker for full order-level root cause.",
            },
            {
                "name": "Tianpai actual onsite workflow",
                "status": "done",
                "description": "The Tianpai training pack now records the confirmed onsite workflow: ERP enters orders, total quantity, split deliveries, and work split; APS only schedules the weaving portion; IOT currently does not participate in Tianpai's production flow; physical stages run from yarn picking through weaving, pre-treatment, dyeing, inspection, cutting, sewing, packing, detection, storage, and container loading.",
            },
            {
                "name": "Tianpai training governance",
                "status": "done",
                "description": "The Tianpai training pack now records first-persona priority, answer format, KPI priority, weaving-only recommendation scope, data-insufficiency behavior, standard-field/site-term terminology, automation boundaries, and iterative acceptance-standard policy.",
            },
            {
                "name": "Athena Automatic Training Console",
                "status": "done",
                "description": "Training Console and API automatically evaluate Tianpai training tasks, score evidence and governance alignment, emit Hermes-style JSON, track capability progress, flag data gaps, and prepare Codex/Hermes next-iteration queues.",
            },
            {
                "name": "Training review and data intake",
                "status": "done",
                "description": "Training Console now lets reviewers approve, request changes, reject, or annotate a task, and register, skip, or mark unavailable a needed data source without uploading raw files or storing credentials.",
            },
            {
                "name": "Training round summary and baseline promotion",
                "status": "done",
                "description": "Training Console and API now summarize approved training rounds, split promoted tasks into capability regression and data-gap regression, record data decisions, and promote the approved Tianpai task set into an automatic regression baseline.",
            },
            {
                "name": "Bilingual page language switch",
                "status": "done",
                "description": "All current web pages include a shared Chinese / English toggle that preserves the selected language in browser local storage and translates page chrome without changing business data or exported logs.",
            },
            {
                "name": "Production Console Chinese display",
                "status": "done",
                "description": "Production Operations Console defaults to Chinese for customer review and localizes dynamic status, workflow, resource lenses, optimization signals, service candidates, KPI logs, and evidence logs while retaining English toggle support.",
            },
            {
                "name": "Production site flow layout",
                "status": "done",
                "description": "Production Operations Console now presents the former resource-lens area as a top-down order, scheduling, machine, and garment flow with backlog, style count, material linkage, capacity occupation, machine status, running rate, defect proxy, yield, and defect-reason summaries.",
            },
            {
                "name": "APS/IOT adapter field mapping",
                "status": "done",
                "description": "Production Operations now includes a read-only adapter contract and field map for APS order, schedule, capacity, yarn forecast, and IOT machine, program evidence, output, scrap, and yield fields.",
            },
            {
                "name": ".co/.cx program-file terminology",
                "status": "done",
                "description": "Production Operations now names seamless machine sample/production program files by the correct .co and .cx extensions.",
            },
            {
                "name": "Customer-facing interaction page",
                "status": "done",
                "description": "The root web page now provides a clean customer interaction entry with Santoni branding, quick prompts, image upload, and simplified response cards.",
            },
            {
                "name": "Customer identity selection gate",
                "status": "done",
                "description": "The customer-facing home page now requires users to choose 鎬荤粡鐞? Service Engineer, or Design Development before effective chat, using the selected identity as the explicit routing role and future permission-management seed.",
            },
            {
                "name": "Developer identity selection gate",
                "status": "done",
                "description": "The developer/debug page now uses explicit 鎬荤粡鐞? Service Engineer, and Design Development identity buttons and blocks test chat until an identity is selected.",
            },
            {
                "name": "User page script scope guard",
                "status": "done",
                "description": "The customer-facing user script now runs inside its own scope and avoids shared language-switch globals so the identity buttons and status updates initialize reliably.",
            },
            {
                "name": "Production delivery-time wording route",
                "status": "done",
                "description": "Production Athena now treats Chinese 鐠愌勬埂 / 楠炲啿娼庣拹褎婀?questions as order-delay analysis and explains the current mock-data boundary around due dates versus true historical lead time.",
            },
            {
                "name": "Production management answer template",
                "status": "done",
                "description": "Production Athena now returns a fixed management answer object with conclusion, reason/evidence, risk, recommendation, and data-gap fields for general-manager style review.",
            },
            {
                "name": "Production high-frequency management questions",
                "status": "done",
                "description": "Production Athena now has explicit branches for delivery risk, low yield/scrap, machine bottleneck, and current data-gap questions using structured evidence instead of generic chat.",
            },
            {
                "name": "Production object model and Management Priority Engine v1",
                "status": "done",
                "description": "Production Operations now exposes production_object_model and management_priority_brief objects so Athena can rank the general manager's top evidence-backed priorities across order, style, machine, process, signal, evidence, decision, action, follow-up, and memory-event contracts.",
            },
            {
                "name": "Decision Loop / Follow-up Engine v1",
                "status": "done",
                "description": "Production Operations now converts management priorities into decision_loop objects with decision, action, follow_up, owner, evidence status, closure gate, recurrence watch, metadata-only review state, and Hermes memory-event candidates.",
            },
            {
                "name": "Production permission boundary and GM final confirmation",
                "status": "done",
                "description": "Production Operations now exposes a permission_boundary object and console panel that separate allowed Athena support actions from blocked APS/IOT, service-dispatch, machine-control, employee-scoring, and final-decision actions.",
            },
            {
                "name": "Production MVP demo story",
                "status": "done",
                "description": "Production Operations now exposes an mvp_demo_story object and console panel that turn the PRD demo story into a three-minute management path across delivery risk, quality/replenishment, labor effective hours, service risk, follow-up items, and GM confirmation boundary.",
            },
            {
                "name": "Production MVP success check",
                "status": "done",
                "description": "Production Operations now exposes an mvp_success_check object and console panel that evaluate PRD success criteria for the general manager's three-minute review: top priorities, why they matter, evidence, next confirmation owner, missing data, and remaining mock-data boundary.",
            },
            {
                "name": "Production PRD alignment audit",
                "status": "done",
                "description": "Production Operations now exposes a prd_alignment_audit object and console panel that map Athena PRD v0.1 sections 1-18 to implemented objects, evidence refs, remaining gaps, and the local-mock versus live-deployment boundary.",
            },
            {
                "name": "Tianpai APS/ERP export adapter",
                "status": "done",
                "description": "Production Operations now exposes a read-only Tianpai APS/ERP CSV export adapter that parses no-header external CSV files by 琛ㄥ瓧娈?DDL field order, builds standard object counts, join quality, missing-field checks, unmatched-record counts, capability boundaries, and blocked write actions without copying raw customer data into the repo.",
            },
            {
                "name": "Production mock plus actual snapshot console",
                "status": "done",
                "description": "Production Console now shows the current data source as Mock / Tianpai APS Export and renders actual-data KPIs for orders, near-due orders, scheduled and unscheduled weaving part orders, plan completion, report completion, machine plan load, and machine/style cylinder-gauge mismatch candidates.",
            },
            {
                "name": "Tianpai actual-data management Q&A",
                "status": "done",
                "description": "Santoni Athena production Q&A now answers supported management questions from the Tianpai APS/ERP export before falling back to mock analysis, returning evidence chains across order, weaving part order, planned task, machine, evidence refs, and field source.",
            },
            {
                "name": "Production GM first-screen actual priority workflow",
                "status": "done",
                "description": "Production Console now generates the general manager's top-three first-screen risk cards from Tianpai APS/ERP export evidence first, then falls back to mock production evidence when actual evidence is unavailable.",
            },
            {
                "name": "Risk card drilldown and local follow-up contract",
                "status": "done",
                "description": "Production risk cards now carry drilldown questions, field sources, actual evidence chains, internal-demo readiness, and local metadata-only follow-up contracts linked to the original risk card.",
            },
            {
                "name": "GM Demo Mode UI",
                "status": "done",
                "description": "Production Console now opens as a general-manager demo surface centered on the question '浠婂ぉ鎴戝簲璇ュ厛鐩摢涓変欢浜嬶紵' while moving development-heavy evidence and PRD audit details below the primary risk-card experience.",
            },
            {
                "name": "Athena Skill Registry",
                "status": "done",
                "description": "Production workflow now exposes a read-only skill registry for GM daily brief, delivery risk, machine fit, material constraint, bottleneck detection, quality/scrap, service escalation, and local follow-up action skills.",
            },
            {
                "name": "Skill Execution Trace",
                "status": "done",
                "description": "Risk-card details and Santoni Athena drilldown responses now show which skill was used, what Athena checked, which objects/evidence were inspected, evidence level, result summary, and data gaps.",
            },
            {
                "name": "Athena v0.90 development progress report",
                "status": "done",
                "description": "A staged progress report now documents the user-page general-manager agent workflow, current Athena capabilities, current limits, internal demo scope, future development plan, and the read-only demo boundary.",
            },
            {
                "name": "Activation credential prompt",
                "status": "done",
                "description": "The customer page prompts for one-time platform credentials when a lock-machine activation-password task is detected.",
            },
            {
                "name": "Unlock intent credential trigger",
                "status": "done",
                "description": "The customer page now treats natural unlock-machine wording as an activation-password task and keeps that credential context for follow-up details.",
            },
            {
                "name": "Natural lock activation routing",
                "status": "done",
                "description": "Backend routing now treats natural machine-lock phrases such as 'my machine is locked' as a service activation-password intake instead of asking a generic design/service clarification.",
            },
            {
                "name": "Lock-machine activation wording",
                "status": "done",
                "description": "Customer-facing wording now names the flow as lock-machine activation while retaining TOP2 model matching where technically required.",
            },
            {
                "name": "Full Santoni logo asset",
                "status": "done",
                "description": "The customer-facing home page now uses the provided full Santoni horizontal logo image instead of the previous simplified SVG asset.",
            },
        ],
        "planned_features": [
            {
                "name": "Formal Guardrails engine",
                "status": "planned",
                "description": "Centralize unsafe-action rules, dispatch gates, and confidence checks for customer-facing responses.",
            },
            {
                "name": "Real SWS/Arachne adapter",
                "status": "planned",
                "description": "Replace the Design Intake mock engineering-brief candidate with controlled adapters for real design files, SWS/Arachne file reading, parameter mapping, diffing, and engineer review.",
            },
            {
                "name": "Real APS/IOT production adapters",
                "status": "planned",
                "description": "Replace the Production Operations normalized mock snapshot with controlled read-only API adapters for APS schedule/material data and Santoni IOT machine execution/output data.",
            },
            {
                "name": "Real ERP order and material adapter",
                "status": "planned",
                "description": "Connect read-only ERP order, split-delivery, production-task, BOM yarn demand, and yarn inventory balance data after customer approval, anonymization rules, and canonical produce_order_code/order_id mapping are confirmed.",
            },
            {
                "name": "Real Hermes runtime connector",
                "status": "planned",
                "description": "Connect Athena to a real Hermes endpoint or MCP server after schema, auth, memory retention, and tool-call permissions are confirmed.",
            },
            {
                "name": "Production follow-up real workflow integration",
                "status": "planned",
                "description": "Connect follow-up owners, review reminders, evidence collection, closure, and recurrence checks to real production-management workflows after Tianpai process owners confirm the handoff rules.",
            },
            {
                "name": "Customer-validated GM demo storyline",
                "status": "planned",
                "description": "Review the v0.113.0 General Manager dashboard hierarchy and internal demo storylines with Tianpai or internal stakeholders and decide which parts are safe for customer-facing presentation.",
            },
            {
                "name": "Live demo reset policy",
                "status": "planned",
                "description": "Define a future reset workflow for live deployments after storage boundaries, user permissions, and audit requirements are confirmed.",
            },
            {
                "name": "Real Hermes organization-memory connector",
                "status": "planned",
                "description": "Connect approved playbook candidates to real Hermes memory only after live schema, retention, anonymization, tenant-scope policy, and approval workflow are confirmed.",
            },
            {
                "name": "Live Hermes automatic training runner",
                "status": "planned",
                "description": "Replace the current local deterministic evaluator with a live Hermes runner that can execute training tasks, return JSON results, and drive repeated Codex/Hermes improvement loops under the approved automation boundary.",
            },
            {
                "name": "Live Hermes playbook regression runner",
                "status": "planned",
                "description": "After real Hermes schema, review workflow, and regression execution policy are confirmed, convert approved playbook regression candidates into live repeated tests instead of local mock-contract queue items.",
            },
            {
                "name": "Real service ticket and handoff integration",
                "status": "planned",
                "description": "Send approved handoff payloads into the real ticket, service leader, or field engineer process.",
            },
        ],
        "confirmed": [
            "Main Agent should keep natural-language identity and intent inference as a backend fallback, while the customer-facing page uses explicit identity selection as the primary routing path.",
            "Customer-facing chat should use explicit identity buttons as the primary workflow-routing path; natural-language identity detection should remain a backend fallback rather than the main customer entry method.",
            "Developer/debug chat should also require explicit identity selection before effective test messages, so the demo UI matches future role-based permission management.",
            "Page-specific scripts should not reuse shared global identifiers from the language switch; user-facing pages need a readiness signal or regression check when identity controls are script-driven.",
            "Chinese 鐠愌勬埂 questions are in Production Athena scope, but true recent-week average lead time requires order-created dates and actual delivery records; current mock data can only summarize due-date distance for the backlog.",
            "Production Athena answers for management users should follow a fixed conclusion, reason/evidence, risk, recommendation, and data-gap structure before any deeper drilldown.",
            "High-frequency general-manager questions should be routed to explicit structured branches: delivery risk, quality/scrap, machine bottleneck, and data gaps.",
            "Athena's production value proposition is not generic ChatBI; it should rank what management should look at first, explain evidence and risk, and prepare action candidates for follow-up.",
            "Production GM first-screen priorities should prefer Tianpai APS/ERP actual export evidence when available, while keeping mock production evidence as a clearly labeled fallback.",
            "General Manager hard risks and evidence/data reconciliation candidates should be displayed as separate lanes so Athena does not confuse real risk with weak or inconsistent evidence.",
            "Every internal-demo production risk card should expose evidence chain, field source, suggested owner, suggested action, data gaps, and a local metadata-only follow-up contract.",
            "Production risk cards should expose which Athena skills were used and show a readable Skill Execution Trace so the demo communicates process, not only structured ChatBI output.",
            "GM Demo Mode should keep the first screen focused on the three priorities and move developer-heavy adapter details, raw evidence, and PRD audit information into details or developer-facing sections.",
            "The customer-facing General Manager page should not show Internal Demo Mode, demo readiness, development progress, version notes, raw JSON, payloads, or full technical field lists outside evidence details.",
            "General Manager drilldown answers should translate Athena's verification work into management language: checked objects, findings, evidence level, cannot-conclude/data-gap statements, and suggested confirmation owner.",
            "Stable internal demos should use actual APS/ERP export evidence as the main line and clearly label any mock IOT/Service supplements instead of blending them into one undifferentiated story.",
            "Athena's product-level value proposition is workflow-native onsite workforce, management decision-loop agent, and Hermes-governed self-evolution.",
            "Production Management Priority Engine should use delivery > quality > cost as the PRD priority policy while treating cost as a consequence of delivery and quality failures until real cost tables are available.",
            "Production priority decisions must be linked to production_object_model fields and evidence_refs before they can become follow-up or Hermes memory candidates.",
            "Decision Loop / Follow-up Engine v1 should keep follow-up review state as metadata-only local records, require human owner confirmation, and block APS/IOT writes, service-ticket creation, and Hermes memory promotion.",
            "The first follow-up lifecycle is proposed, assigned, waiting_evidence, confirmed, closed, and reopened; closed items may only become reviewed memory-event candidates after human review and result evidence.",
            "Organization Memory / Playbook Engine v1 should treat Production follow-up outputs as playbook candidates only; it must block live Hermes memory writes, raw customer data storage, credential storage, and tenant-memory promotion without human review.",
            "A playbook candidate can only be approved after follow-up closure, accepted evidence, human playbook review, sensitivity check, and regression-case preparation.",
            "Approved Hermes playbook candidates may enter the local Training playbook_regression_queue as regression-case candidates, but unapproved or evidence-incomplete candidates must remain blocked.",
            "Automatic Regression Runner v1 may execute approved Tianpai baseline tasks and approved playbook regression candidates locally; blocked playbook candidates must remain visible but non-executable.",
            "Regression Gate v1 should block the next local Codex/Hermes loop when executable regression cases fail, while keeping blocked playbook candidates visible for human review rather than executing them.",
            "Next Loop Handoff v1 should split the post-gate loop into automatic local-training items, human-review items, and data-request items so the automatic loop can continue without hiding blocked evidence work.",
            "Next Loop Handoff Review v1 should record user decisions on handoff items as metadata only and must not execute blocked playbooks, write live Hermes memory, or change code automatically.",
            "Next Loop Closure Gate v1 should keep open or rejected handoff items visible while allowing only read-only local iteration planning when the regression gate allows it.",
            "Training Iteration Proposal v1 should prepare only read-only local training task seeds and must not execute tasks, change code, write live Hermes memory, or start real data integration.",
            "Training Iteration Proposal Review v1 should mark a proposal as approved for future queue preparation only, not execute tasks or change code automatically.",
            "Codex Work Packet Queue v1 should prepare read-only work packet drafts from approved proposals only; it must not execute packets, create branches, change code, write live Hermes memory, or start real data integration automatically.",
            "Codex Patch Queue Contract v1 should prepare patch candidates from ready work packets only; it must not apply code, create branches, commit, push, open PRs, write live Hermes memory, or start real data integration automatically.",
            "Codex Execution Gate v1 should convert ready patch candidates into pending human-reviewed execution candidates only; it must not execute patches, create branches, commit, push, open PRs, write live Hermes memory, or start real data integration automatically.",
            "Codex Execution Gate Review v1 should approve worktree preparation only as metadata; it must not execute patches, create branches, commit, push, open PRs, write live Hermes memory, or start real data integration automatically.",
            "Codex Worktree Preparation Queue v1 should prepare task drafts from approved execution reviews only; it must not create worktrees, switch branches, apply patches, commit, push, open PRs, write live Hermes memory, or start real data integration automatically.",
            "Codex Worktree Launch Gate v1 should prepare launch request drafts from ready worktree preparation tasks only; it must not run git, create worktrees, switch branches, apply patches, commit, push, open PRs, write live Hermes memory, or start real data integration automatically.",
            "Codex Worktree Result Intake v1 should store only metadata summaries, changed-file paths, validation statuses, and blocked actions; it must not store raw diffs, raw logs, raw files, credentials, commits, pushes, PRs, live Hermes writes, or real data integration actions.",
            "Codex Worktree Result Review Gate v1 should prepare regression and Hermes memory candidates only after metadata review; it must not promote baselines, write live Hermes memory, merge, commit, push, open PRs, store raw patches, or start real data integration automatically.",
            "Codex Promotion Candidate Queue v1 should collect approved result-review candidates into read-only regression and Hermes queues; it must not promote baselines, write live Hermes memory, merge, commit, push, open PRs, store raw patches, or start real data integration automatically.",
            "Codex Promotion Approval Gate v1 should record product-owner decisions on promotion candidates and create approved-but-not-executed future action plans only; it must not execute baseline promotion, write live Hermes memory, merge, commit, push, open PRs, store raw patches, or start real data integration automatically.",
            "Codex Promotion Handoff Queue v1 should convert approved-but-not-executed future promotion actions into manual handoff contracts only; it must not execute baseline promotion, write live Hermes memory, merge, commit, push, open PRs, store raw patches, or start real data integration automatically.",
            "Codex Promotion Execution Readiness Gate v1 should identify missing execution prerequisites before any real baseline promotion or live Hermes memory write; it must not execute baseline promotion, write live Hermes memory, merge, commit, push, open PRs, store raw patches, or start real data integration automatically.",
            "Codex Promotion Execution Readiness Review v1 should store prerequisite-confirmation metadata only and can unlock final manual execution confirmation, not automatic baseline promotion, live Hermes memory writes, commits, pushes, PRs, raw patch storage, or real data integration.",
            "Codex Promotion Execution Result Intake v1 should store manual execution result metadata only and must not claim real promotion success without changed record identifiers plus compileall and harness validation summaries.",
            "Codex Promotion Closure / Hermes Sync Audit v1 should audit whether all confirmed promotion readiness items have complete manual execution result records, then prepare future sync-audit candidates without updating baselines, writing live Hermes memory, committing, pushing, opening PRs, storing raw files, or starting real data integration.",
            "Codex Promotion Sync Review Gate v1 should approve future sync action plans only as metadata; it must not update baselines, write live Hermes memory, commit, push, open PRs, store raw files, store credentials, or start real data integration.",
            "Codex Promotion Sync Handoff Queue v1 should prepare manual execution handoff contracts only; it must not update baselines, write live Hermes memory, commit, push, open PRs, store raw files, store credentials, or start real data integration.",
            "Codex Promotion Sync Execution Readiness Gate v1 should identify missing sync execution prerequisites only; it must not update baselines, write live Hermes memory, commit, push, open PRs, store raw files, store credentials, or start real data integration.",
            "Codex Promotion Sync Execution Readiness Review v1 should store prerequisite-confirmation metadata only and can unlock final manual sync execution confirmation, not automatic baseline updates, live Hermes memory writes, commits, pushes, PRs, raw file storage, or real data integration.",
            "Codex Promotion Sync Execution Result Intake v1 should store manual sync result metadata only and must not claim real baseline or Hermes sync success without changed record identifiers plus compileall and harness validation summaries.",
            "Codex Promotion Sync Closure Audit v1 should treat closure-ready as final manual review readiness only, not as permission to update regression baselines, write live Hermes memory, commit, push, open PRs, store raw files, or start real data integration.",
            "Codex Promotion Sync Closure Review Gate v1 should record final closure approval only as metadata and produce approved-but-not-executed future real sync action plans; it must not update regression baselines, write live Hermes memory, commit, push, open PRs, store raw files, store credentials, or start real data integration.",
            "Codex Promotion Final Sync Handoff Queue v1 should prepare manual final sync handoff contracts only; it must not update regression baselines, write live Hermes memory, commit, push, open PRs, store raw files, store credentials, or start real data integration.",
            "Codex Promotion Final Sync Execution Readiness Gate v1 should evaluate missing real-system prerequisites only; it must not update regression baselines, write live Hermes memory, commit, push, open PRs, store raw files, store credentials, or start real data integration.",
            "Codex Promotion Final Sync Execution Result Intake v1 should store manual final sync result metadata only and must not claim real baseline or Hermes sync success without changed record identifiers plus compileall and harness validation summaries.",
            "Codex Promotion Final Sync Closure Audit v1 should treat closure-ready as final completion review readiness only, not as permission to update regression baselines, write live Hermes memory, publish project memory, commit, push, open PRs, store raw files, or start real data integration.",
            "Codex Promotion Final Completion Review Gate v1 should record product-owner final completion decisions only as metadata and produce approved-but-not-published future publication plans; it must not publish project memory, update regression baselines, write live Hermes memory, commit, push, open PRs, store raw files, store credentials, or start real data integration.",
            "Codex Promotion Final Publication Handoff Queue v1 should prepare manual final publication handoff contracts only; it must not publish project memory, update regression baselines, write live Hermes memory, commit, push, open PRs, store raw files, store credentials, or start real data integration.",
            "Codex Promotion Final Publication Readiness Gate v1 should evaluate publication prerequisites only; it must not publish project memory, update regression baselines, write live Hermes memory, commit, push, open PRs, store raw files, store credentials, or start real data integration.",
            "Codex Promotion Final Publication Result Intake v1 should store manual final publication result metadata only and must not claim real publication success without publication references, published record identifiers, post-publication validation summaries, and compileall/harness validation summaries.",
            "Codex Promotion Final Publication Closure Audit v1 should treat closure-ready as final release/archive review readiness only, not as permission to publish project memory, update regression baselines, write live Hermes memory, commit, push, open PRs, store raw files, or start real data integration.",
            "Codex Promotion Final Release / Archive Review Gate v1 should treat release-ready as product-owner archive/release review readiness only, not as permission to create archive artifacts, publish project memory, update regression baselines, write live Hermes memory, commit, push, open PRs, store raw files, or start real data integration.",
            "Designer Agent is a product development copilot, not a direct SWS generator.",
            "Designer Agent should understand design intent before generating a technical proposal.",
            "Service Agent is customer-facing and should prioritize fast production recovery.",
            "Service Agent should attempt safe online assistance before dispatching service tickets.",
            "Service dispatch requires machine model, serial number, symptom/alarm, production status, photo/video evidence, factory location, contact, and online steps attempted.",
            "TOP2MP lease-password lock is the first tool-automation Service case; it should generate a password only through a controlled future tool, not by exposing platform credentials.",
            "The current lease-password generator is a local mock tool using mock records only.",
            "The web demo has an experimental real-platform connection mode; credentials are request-only and excluded from exported test logs.",
            "Real-platform mode can submit the login form and safely summarize post-login fields/links for mapping.",
            "Each browser refresh starts a new web session, and the demo has a Clear Memory button for repeatable tests.",
            "Service Agent state flow follows intake, urgency check, online assist, escalation, ticketing, tracking, and closure.",
            "Service Case Online Assist Mock loads structured service cases and matches customer issues to online troubleshooting guidance.",
            "Recent service cases from 2026-04-18 to 2026-05-18 are distilled into eight mock online-assist case skills.",
            "The Service Case Library review page exposes each mock case for business review before future customer-facing approval.",
            "The web demo includes an operation guide for business testers.",
            "Excel service reports can be imported into draft service-case JSON through scripts/import_service_cases.py.",
            "Service case review status can be saved from the web page; approved Excel drafts can enter customer-facing matching.",
            "Service managers can edit case keywords, online steps, safety warnings, dispatch triggers, and handoff payload previews before approving customer-visible knowledge.",
            "Developer page should show recent changelog entries in-page so testers can confirm the current iteration without leaving the debug workflow.",
            "The Design Intake Structuring Console is a Design Agent data-structuring middleware testbench, not the full Athena MVP.",
            "Its current purpose is to test whether design requests, Style3D/CLO notes, AI/reference-image notes, or technical package summaries can be normalized into auditable data objects.",
            "It is not intended to be a manual design-exhaustion tool; future constraint discovery and training should come from automated design, sampling, engineering, and production data.",
            "Athena capabilities should land as workflow templates, data objects, tool interfaces, evidence logs, and KPIs rather than as generic chatbot behavior.",
            "Production Operations Console should monitor order intake, ERP, APS, IOT, production, service escalation candidates, and garment output for management and production supervisors.",
            "Production Operations MVP uses local mock data and read-only adapter contracts only; it must not upload .co/.cx files, confirm schedules, release orders, control machines, or create real service tickets.",
            "Production management lens is 娴滅儤婧€閺傛瑦纭堕悳顖涚ゴ: people, machine, material, method, environment, and measurement.",
            "Every current web page should expose a Chinese / English language switch, and the choice should persist across navigation in the browser.",
            "Production Operations Console should display customer-facing Chinese labels by default while keeping English available through the language switch.",
            "Production Operations Console should show production data from order to scheduling to machine execution to garment output, instead of exposing only abstract 娴滅儤婧€閺傛瑦纭堕悳顖涚ゴ panels.",
            "Production managers and customers should be able to ask why a KPI changed and receive structured root-cause analysis from production data objects instead of generic chatbot text.",
            "Santoni Athena production insight must remain read-only and evidence-based; it must not change APS schedules, write IOT data, upload .co/.cx files, control machines, or auto-dispatch service tickets.",
            "Production workflow traceability depends on one canonical order_id / 鐠併垹宕熼崣?across ERP, APS, IOT, production, service candidate, and garment output records.",
            "APS page research maps order tracking, production orders, styles, machine scheduling, auto-scheduling, machine aggregate, machine task, machine master, and yarn forecast fields into Production adapter objects.",
            "Santoni IOT page research maps monitor, dashboard, data-analysis, device detail, factory resource, and program-interface fields into Production adapter objects.",
            "Production landing should prefer direct APS/IOT database access or formal APIs over web-page scraping; current APS/IOT test pages only informed field mapping.",
            "Seamless machine sample/production program files should be referred to as .co and .cx files.",
            "Future real IOT integration should prefer the formal program-interface/API documentation route instead of browser scraping.",
            "Hermes should first connect as Athena's runtime, project memory, tool orchestration, and development-suggestion layer, not as a replacement for Santoni Agent Core.",
            "Hermes development suggestions must be evidence-based and human-reviewed before changing workflows, code, production adapters, or service handoffs.",
            "Hermes memory events must distinguish product, domain, tenant, and session scope, and tenant memory must not become global domain knowledge without reviewed or approved promotion.",
            "Hermes did not override the old Main Agent route; the customer-facing chat needed an explicit production-manager bridge from /api/chat into the Production Operations workflow.",
            "Every /api/chat response should expose a Hermes-ready athena_runtime_event envelope with workflow, persona, intent, evidence_refs, data_boundary, memory_event_candidate, and blocked_actions while excluding raw user text, generated sensitive values, credentials, and live memory writes.",
            "Tianpai VOC from Agnes identifies delivery date as the general manager's P0 concern, quality as secondary, and real-time cost as useful only when purchasing and labor data are available.",
            "Tianpai yarn inventory is now available to Athena as aggregate material evidence with 8146 rows, 128 yarn codes, 392 batches, 67 suppliers, task-order fields, and balance fields; raw inventory rows are not stored in the repo.",
            "Tianpai material-risk analysis must treat zero and negative balance rows as review signals until warehouse/ERP owners confirm movement and sign rules.",
            "The General Manager Question Bank is a hypothesis set until Product Owner, Agnes, Tianpai onsite roles, and customer management verify or approve each question.",
            "Current Tianpai IOT exports support machine/style/shift monitoring, converted-scrap ranking, downtime review, and fault-code ranking, but not full order-level delivery root cause.",
            "The current Tianpai actual workflow confirms that ERP handles order entry, total quantity, split deliveries, and work split; APS only handles weaving scheduling; IOT currently does not participate in Tianpai's production workflow.",
            "Tianpai physical production stages are yarn picking, weaving greige, pre-treatment, storage, dyeing scheduling/dyeing, inspection with replenishment order if failed, cutting, sewing, packing, needle/metal detection, packing, finished-goods storage, and container loading.",
            "Tianpai training should target the general manager first and answer with management summary, reason/evidence, and recommended action.",
            "Tianpai training KPI priority is delivery > quality > cost; cost remains a consequence metric until purchasing, labor, rework, and freight records are available.",
            "Athena may propose weaving-process recommendations for Tianpai now; recommendations outside weaving should be framed as data needs or items requiring confirmation until real ERP expansion is approved.",
            "Athena should explicitly say when Tianpai data is insufficient and name the missing data rather than forcing a root-cause conclusion.",
            "Tianpai terminology should use standard_field_name (site_term), preserving site terms such as 閹炬垹娅ч崸?/ 闊晝娅ч崸? 閹烘帞鍑? 妤楊厽鐓? 妤犲矂鎷? and 闁叉垵鐫樺Λ鈧ù?",
            "Training Athena manually is not useful for the product goal; the Training Console should run automatic evaluation tasks and expose progress, Hermes-style JSON results, data gaps, and next actions.",
            "The current automatic training loop is a local evaluator over structured training packs, not model-weight fine-tuning and not a live Hermes runner.",
            "Training review/data intake should store metadata, review notes, and source references only; raw Excel files, credentials, tokens, and API keys must not be stored in repo files.",
            "Approved Tianpai training tasks should be kept in the automatic regression baseline and rerun after Athena production, Hermes, adapter-contract, training-pack, wording, or small-code changes.",
            "The APS Planned Task delivery-time CSV attachment contains 127 rows with produce_order_code, machine_id, style_code, planned/produced quantity, plan/actual/estimate timing, status, and delivery_time fields; it can serve as APS schedule and delivery-time metadata for training, but raw CSV content should not be stored in the repo.",
            "True customer purchasing/labor cost data and stage-level downstream process records are not available now; Athena must state those limitations instead of calculating customer cost or full downstream bottlenecks from mock data.",
            "The root web page is customer-facing, while /developer.html keeps the previous development and debugging interface.",
            "Customer-facing lock-machine activation tasks can collect platform credentials only when needed and keep them in browser memory for the session.",
            "Customer-facing wording should say lock-machine activation; TOP2 remains a technical machine-family matcher in code and mock data.",
            "The customer-facing home page should use the full approved Santoni logo asset.",
            "Natural machine-lock wording should enter the Service activation-password intake, ask for confirmed model, serial number, and lock-screen machine code, and never invent those tool inputs.",
            "All current SWS, APS, ticket, service case, and image recognition data are mocked.",
            "DeepSeek and OpenAI provider switching is supported through local environment configuration.",
        ],
        "uncertain": [
            "Designer VOC is not complete, so the 8-stage Designer process is an assumption.",
            "Exact designer decision criteria for cost, lead time, hand feel, visual direction, and brand line need VOC input.",
            "Service online-solvable issue list is pending from Joey / Santoni service knowledge.",
            "Imported Excel-derived cases require service review before they should be treated as approved customer-visible knowledge.",
            "Web-based case editing and diff view are implemented for Service Manager Console, but formal audit permissions are not implemented yet.",
            "The Design Intake Structuring Console uses deterministic mock rules; real Style3D/CLO/design-file/SWS/Arachne adapters are not connected yet.",
            "Production Operations Console uses deterministic mock data with APS/IOT-like normalized fields; real APS and IOT API adapters are not connected yet.",
            "Production first-screen priorities can use Tianpai APS/ERP export files, but this is still file-export evidence rather than a live read-only database/API adapter.",
            "Tianpai APS/ERP no-header CSV files are interpreted by the 琛ㄥ瓧娈?DDL field order; if the DDL order changes or a CSV export layout changes, Athena must revalidate the mapping before using the evidence.",
            "Extreme planned-vs-reported quantity gaps and stale delivery dates are now evidence-reconciliation candidates, not confirmed production root causes.",
            "Orders with essentially complete planned-task progress must not be shown as hard delivery-risk candidates unless a separate non-completion delivery driver is available.",
            "The Evidence Review Queue improves trust but still needs APS/planning owner validation before its thresholds and owner roles are treated as customer-standard workflow.",
            "Machine/style mismatch evidence is only a root-cause candidate when both required style parameter and actual machine parameter are available and comparable; allowed substitutions still require APS or engineering confirmation.",
            "Actual-data priority cards currently cover APS/ERP order, WPO, task, machine, and reporting evidence; downstream quality, labor, shipment, cost, and live IOT joins remain incomplete.",
            "The Production Skill Registry is currently a local contract linked to deterministic workflow logic; it is not yet a dynamic tool runtime or live Hermes skill executor.",
            "Skill Execution Trace shows the current deterministic analysis path and evidence checks, but it does not yet prove causal root cause beyond the available export/mock evidence.",
            "The v0.113.0 verification process is a management-facing explanation of available evidence checks, not a live autonomous investigation or causal proof engine.",
            "The v0.113.0 General Manager dashboard hierarchy is ready for internal UI review, but the service-impact story still uses mock IOT/Service evidence and must be presented as a hybrid scenario.",
            "The v0.113.0 Daily Brief Narrative is structured and evidence-bound, but its wording still needs validation with a real general manager or internal presenter before customer demo use.",
            "The v0.112.0 local follow-up board is metadata-only and does not yet persist tenant/user-specific ownership beyond the local review store.",
            "Santoni Athena production root-cause analysis is deterministic over the current local mock snapshot; real BI semantic models, time-series drilldowns, and live APS/IOT data are not connected yet.",
            "Formal APS/IOT API documentation, token scope, rate limits, and deployment access model are not confirmed yet.",
            "Future APS/IOT database schema, order_id join rules, access control, and refresh cadence are not confirmed yet.",
            "Real Hermes endpoint, authentication mode, memory schema, retention policy, and HTTP-vs-MCP integration route are not confirmed yet.",
            "Athena runtime events are local session-scope candidates only; live Hermes ingestion, deduplication, retention enforcement, and promotion workflow are not connected yet.",
            "Tianpai IOT production output currently has 100% missing order_id in the provided export; the APS attachment gives a produce_order_code candidate, but the APS-to-IOT join rule is still not confirmed.",
            "Tianpai ERP order and split-delivery data are not available yet and require customer communication before Athena can prove full order-level delivery root cause.",
            "Tianpai General Manager questions have not been directly validated through customer VOC yet; current questions remain a structured hypothesis list for review.",
            "Tianpai yarn inventory has material-balance evidence, but BOM yarn demand, supplier-code mapping, and quality-to-yarn-batch joins are not confirmed yet.",
            "Tianpai machine coverage is partial because not all onsite machines are connected to IOT yet.",
            "The Tianpai APS fragment is not yet a detailed scheduling export, and APS only covers weaving, so it cannot support full-factory schedule adherence, downstream bottleneck, or order-level root-cause calculation by itself.",
            "Tianpai training acceptance standards are not fixed yet and should be discovered through repeated tasks, evaluation JSON, and review.",
            "The current Training Console can auto-evaluate local Tianpai tasks, but real Hermes training execution, result ingestion from Hermes, and automatic code-change orchestration are not connected yet.",
            "Training data-source registration does not parse or ingest Excel content yet; it only records which source should be reviewed or requested next.",
            "Tianpai material, labor-cost, stage-level quality-inspection, and garment-output tables are not available yet, so per-garment cost and downstream quality root-cause training remain blocked.",
            "Real handoff payloads for SWS, suppliers, service leaders, and ticket systems are not yet defined.",
            "Real tools and data integrations are not connected yet.",
        ],
        "designer_state_flow": model["state_flows"]["designer"],
        "service_state_flow": model["state_flows"]["service"],
        "athena_mvp_state_flow": model["state_flows"]["athena_mvp"],
        "production_operations_state_flow": model["state_flows"]["production_operations"],
        "hermes_integration_state_flow": model["state_flows"]["hermes_integration"],
        "training_automation_state_flow": model["state_flows"]["training_automation"],
        "service_case_mock_structure": [
            "case_id and title",
            "machine_models and issue_category",
            "symptom_keywords and alarm_codes",
            "production_impact and severity",
            "online_solvable and online_resolution_steps",
            "safety_warnings",
            "required_customer_info and required_evidence",
            "probable_causes and recommended_parts",
            "dispatch_triggers",
            "automation_candidate, automation_tool, tool_inputs_required, tool_success_output, and data_sources",
            "manual_escalation_triggers for tool-based service cases",
            "handoff_payload, estimated_resolution_time, confidence_notes, and related_cases",
        ],
        "next_decisions": [
            "Confirm the Product Development Brief mandatory fields.",
            "Validate Design Intake object schemas, required fields, evidence format, and future file-import adapter assumptions with design, SWS/Arachne, sampling, and application engineering stakeholders.",
            "Validate Production Operations resource lenses, KPIs, and APS/IOT read-only adapter fields with production, APS, and IOT owners.",
            "Validate Santoni Athena production root-cause categories, thresholds, evidence format, and management-language output with production owners.",
            "Validate Production Management Priority Engine scoring, top-three ordering, owner roles, evidence requirements, and handoff gates with Tianpai management and onsite implementation colleagues.",
            "Validate whether the v0.113.0 delivery-risk driver guard matches APS owner expectations for completed orders, stale delivery dates, status fields, unscheduled quantities, and planned-vs-reported quantity reconciliation.",
            "Validate whether the v0.109.0 Evidence Review Queue should be reviewed daily by planning, APS owner, production supervisor, or a combined production-control role.",
            "Validate whether the v0.113.0 General Manager first-screen hierarchy is clear enough for internal demo without showing development-progress language.",
            "Validate whether v0.108.2 machine/style mismatch root-cause evidence matches APS and engineering expectations for cylinder diameter, needle spacing, unit convention, and allowed machine substitutions.",
            "Validate whether the customer-facing 鎬荤粡鐞?identity workflow on / feels more like an agent session than a linked dashboard page.",
            "Validate whether the v0.113.0 customer-facing local follow-up loop feels like a General Manager decision workflow rather than a dashboard control.",
            "Validate whether the developer/debug General Manager flow now matches the customer-facing three-priority Athena flow closely enough for repeatable testing.",
            "Validate whether GM Demo Mode is simple enough for a three-minute internal demo and whether the Skill Execution Trace feels like Athena's process rather than debugging noise.",
            "Validate whether the v0.113.0 user-page verification process makes Athena feel like a production decision agent rather than a structured ChatBI panel.",
            "Validate whether the v0.111.0 compressed drilldown format gives enough evidence without distracting the general manager.",
            "Validate whether the v0.112.0 follow-up source-card types and statuses match how a general manager would assign confirmation work.",
            "Validate whether the v0.113.0 Daily Brief Narrative can be used directly in a morning production meeting.",
            "Review the v0.113.0 Delivery Risk Driver Guard report with APS and planning owners before treating delivery-risk cards as customer-facing root-cause evidence.",
            "Confirm whether the compact user-page story entry should stay customer-facing or remain internal-demo-only after tomorrow's UI review.",
            "Confirm which Production skills should become real tool executors first after quality, labor, and live APS/IOT data are available.",
            "Confirm which actual APS/ERP priority cards should be promoted into the standard internal-demo story and which should stay as technical evidence examples.",
            "Validate the first Decision Loop / Follow-up Engine lifecycle, owner roles, evidence requirements, closure gates, and recurrence-watch rules with Tianpai production owners.",
            "Define which priority outcomes should become Hermes playbook candidates and which should remain tenant/session memory only.",
            "Confirm Hermes playbook reviewer roles, approval status meanings, tenant anonymization rules, and the handoff from approved playbook candidate to real Hermes memory.",
            "Confirm which approved playbook regression candidates should become live Hermes regression runs, and which should stay as local Training Console regression cases.",
            "Confirm the acceptance threshold for automatic_regression_run pass-rate before allowing Hermes/Codex loop proposals to trigger code changes.",
            "Confirm how Next Loop Handoff records should be persisted or handed to a future live Hermes runner once real Hermes execution is connected.",
            "Confirm which handoff review statuses should unlock future live Hermes runner actions after tenant-specific governance is implemented.",
            "Confirm whether closure_complete must be true before any future live Hermes runner can execute a next-loop plan, or whether local small-fix iteration can proceed with tracked open items.",
            "Confirm which Training Iteration Proposal fields should become the contract for future Codex worktree tasks or live Hermes runner tasks.",
            "Confirm how approved Codex Work Packet Queue items should map to future Codex worktree branches, code patches, or live Hermes runner jobs.",
            "Confirm which Codex Patch Queue Contract statuses should unlock future automatic small-fix execution versus human-reviewed branch preparation.",
            "Confirm which Codex Execution Gate candidates can become actual Codex worktree tasks and what user confirmation wording should be required before execution.",
            "Confirm how approved Codex Execution Gate Review records should map to future Codex worktree task creation and what validation evidence should be required before returning results.",
            "Confirm the exact user command wording and safety gate needed before Codex may create an actual worktree from a Worktree Preparation Queue task.",
            "Confirm whether Worktree Launch Gate requests should become explicit user-facing buttons, command templates, or remain JSON-only contracts before any actual Codex worktree creation.",
            "Confirm how Codex Worktree Result Intake records should move into product-owner review, regression baselines, or Hermes memory candidates after validation passes.",
            "Confirm which Codex Worktree Result Review decisions should unlock future automatic baseline promotion or live Hermes memory writes after governance is implemented.",
            "Confirm which Codex Promotion Candidate Queue items should become real regression baseline promotions or live Hermes memory writes after product-owner approval and governance checks.",
            "Confirm which approved Codex Promotion Approval Gate future actions should become real baseline promotion or live Hermes memory writes after endpoint, schema, retention, and governance checks are implemented.",
            "Confirm whether Codex Promotion Handoff Queue items should become explicit user-facing execution buttons, command templates, or remain JSON-only contracts before any real baseline promotion or live Hermes memory write.",
            "Confirm which Codex Promotion Execution Readiness Gate prerequisites are mandatory for local baseline promotion versus live Hermes memory write, and how execution evidence should be captured after manual approval.",
            "Confirm which Codex Promotion Execution Readiness Review statuses should unlock future manual execution result intake and what evidence summary fields are mandatory before that step.",
            "Confirm whether approved Codex Promotion Final Completion Review Gate publication plans should become explicit project-memory publication requests, real regression-baseline update requests, live Hermes write requests, or remain JSON-only evidence before any real completion claim.",
            "Confirm Hermes endpoint, authentication mode, memory-event schema, retention policy, and HTTP-vs-MCP integration route.",
            "Confirm which Athena events Hermes may persist as project memory and which require human review first.",
            "Validate Hermes retention_policy, sensitivity_level, and promotion_status values with future deployment and customer-account requirements.",
            "Review the Tianpai training pack with Agnes and Melos, then decide which memory events can move from candidate to reviewed.",
            "Review the APS Planned Task delivery-time CSV field mapping, confirm whether produce_order_code is the canonical order/work-order key, and define the APS-to-IOT join rule before parsing it into structured training objects.",
            "Start the Tianpai general-manager training loop with evaluation JSON for workflow boundaries, data-insufficiency behavior, KPI priority, and weaving-scope recommendations.",
            "Review the Training Console automatic run results, then decide which needs-data tasks should become the next APS/IOT/ERP export requests.",
            "Decide which registered training data sources should be parsed into structured local training objects after sensitivity and field review.",
            "Confirm the live Hermes training-runner schema before enabling real Hermes task execution or automatic code-change orchestration.",
            "Confirm the canonical production order_id mapping when connecting directly to APS/IOT databases or formal APIs.",
            "Confirm whether production integration should read APS/IOT database views directly, use formal read-only APIs, or combine both.",
            "Request formal APS/IOT read-only API documentation and confirm whether the current field mapping matches platform API objects.",
            "Define Guardrails for Designer and Service.",
            "Define which Service issues can be solved online and which must dispatch.",
            "Confirm Service ticket/handoff fields for Santoni service leader and onsite engineer.",
            "Review the Excel draft cases and decide which can become approved customer-visible service knowledge.",
            "Confirm the Service Manager Console payload fields for future CRM/ticket integration.",
        ],
    }





