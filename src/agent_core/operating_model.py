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
            "description": "Monitor people, machine, material, method, environment, and measurement signals, and prepare service request candidates when production recovery needs support.",
        },
        {
            "stage": "Garment Output",
            "status": "implemented_mock",
            "certainty": "confirmed_by_production_mvp_plan",
            "description": "Summarize planned quantity, estimated good garments, quality holds, and output-readiness evidence.",
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
            progress=58,
            purpose="Ensure Athena capabilities land as structured templates with inputs, outputs, owners, tools, evidence, gates, and KPIs.",
            current_scope="Design Intake Structuring and Production Operations consoles implement deterministic local workflow templates with evidence and KPI logs.",
            next_step="Validate the template fields with SWS/Arachne, APS, IOT, sampling, and production stakeholders.",
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
            status="placeholder",
            progress=5,
            purpose="Self-check whether the response answers the user and whether more information is needed.",
            current_scope="No formal evaluation loop yet.",
            next_step="Create checks for premature generation, missing information, and unsafe service advice.",
        ),
    ]

    return {
        "version": "v0.25.3",
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
        },
    }


def project_documentation() -> dict:
    model = operating_model_progress()
    return {
        "version": "v0.25.3",
        "title": "AI Knitting Agent Product / Development Notes",
        "implemented_features": [
            {
                "name": "Natural-language identity routing",
                "status": "done",
                "description": "Main Agent can infer Designer or Service intent from conversation instead of relying on the left role selector.",
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
                "description": "Management-facing console and API monitor order intake, ERP, APS, IOT, production, service escalation candidates, garment output, 人机料法环测 resource lenses, optimization signals, evidence logs, and KPI logs using local mock data.",
            },
            {
                "name": "Santoni Athena production insight",
                "status": "done",
                "description": "Production console includes Santoni Athena as a read-only question-to-data agent that explains KPI changes such as scrap rate, OEE, downtime, material risk, and order delay through structured root causes, recommended actions, drilldowns, and evidence references.",
            },
            {
                "name": "Production order-id workflow spine",
                "status": "done",
                "description": "Production Operations template and page explicitly state that order_id / 订单号 is the unique key joining order intake, ERP, APS, IOT, production/service candidates, and garment output.",
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
                "name": "Real service ticket and handoff integration",
                "status": "planned",
                "description": "Send approved handoff payloads into the real ticket, service leader, or field engineer process.",
            },
        ],
        "confirmed": [
            "Main Agent should infer identity and intent from natural language rather than relying on manual role selection.",
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
            "Production management lens is 人机料法环测: people, machine, material, method, environment, and measurement.",
            "Every current web page should expose a Chinese / English language switch, and the choice should persist across navigation in the browser.",
            "Production Operations Console should display customer-facing Chinese labels by default while keeping English available through the language switch.",
            "Production Operations Console should show production data from order to scheduling to machine execution to garment output, instead of exposing only abstract 人机料法环测 panels.",
            "Production managers and customers should be able to ask why a KPI changed and receive structured root-cause analysis from production data objects instead of generic chatbot text.",
            "Santoni Athena production insight must remain read-only and evidence-based; it must not change APS schedules, write IOT data, upload .co/.cx files, control machines, or auto-dispatch service tickets.",
            "Production workflow traceability depends on one canonical order_id / 订单号 across ERP, APS, IOT, production, service candidate, and garment output records.",
            "APS page research maps order tracking, production orders, styles, machine scheduling, auto-scheduling, machine aggregate, machine task, machine master, and yarn forecast fields into Production adapter objects.",
            "Santoni IOT page research maps monitor, dashboard, data-analysis, device detail, factory resource, and program-interface fields into Production adapter objects.",
            "Production landing should prefer direct APS/IOT database access or formal APIs over web-page scraping; current APS/IOT test pages only informed field mapping.",
            "Seamless machine sample/production program files should be referred to as .co and .cx files.",
            "Future real IOT integration should prefer the formal program-interface/API documentation route instead of browser scraping.",
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
            "Santoni Athena production root-cause analysis is deterministic over the current local mock snapshot; real BI semantic models, time-series drilldowns, and live APS/IOT data are not connected yet.",
            "Formal APS/IOT API documentation, token scope, rate limits, and deployment access model are not confirmed yet.",
            "Future APS/IOT database schema, order_id join rules, access control, and refresh cadence are not confirmed yet.",
            "Real handoff payloads for SWS, suppliers, service leaders, and ticket systems are not yet defined.",
            "Real tools and data integrations are not connected yet.",
        ],
        "designer_state_flow": model["state_flows"]["designer"],
        "service_state_flow": model["state_flows"]["service"],
        "athena_mvp_state_flow": model["state_flows"]["athena_mvp"],
        "production_operations_state_flow": model["state_flows"]["production_operations"],
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
