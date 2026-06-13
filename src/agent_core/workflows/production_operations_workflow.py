"""Production Operations workflow for Athena local demo.

The first implementation is deliberately read-only and mock-backed. It models
the management workflow from order intake to garment output without writing to
APS, IOT, ERP, machine programs, or service systems.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path

from agent_core.skills import (
    production_skill_registry,
    production_skill_trace_for_priority,
    production_skills_for_theme,
)

from .tianpai_aps_erp_export_adapter import TianpaiApsErpExportAdapter


PRODUCTION_TEMPLATE_ID = "athena.production_operations.v1"
PRODUCTION_VERSION = "v0.113.3"
ADAPTER_CONTRACT_ID = "athena.production_aps_iot_read_only_contract.v1"
DATA_PATH = Path(__file__).resolve().parents[2] / "mock_data" / "production_operations.mock.json"
FOLLOW_UP_REVIEW_PATH = Path(__file__).resolve().parents[2] / "mock_data" / "production_follow_up_reviews.json"


@dataclass(frozen=True)
class ProductionStage:
    id: str
    name: str
    owner_role: str
    input_object: str
    output_object: str
    adapter_status: str
    write_permission: str
    kpi: str


@dataclass(frozen=True)
class ProductionTemplate:
    template_id: str
    version: str
    name: str
    positioning: str
    workflow: list[str]
    permissions: list[str]
    adapter_contracts: list[dict]
    adapter_field_mapping: list[dict]
    integration_notes: list[str]
    workflow_primary_key: dict
    resource_lenses: list[str]
    output_objects: list[str]
    stages: list[ProductionStage]
    kpis: list[str]


def production_operations_template() -> dict:
    template = ProductionTemplate(
        template_id=PRODUCTION_TEMPLATE_ID,
        version=PRODUCTION_VERSION,
        name="Order to garment production operations monitoring",
        positioning=(
            "Production Operations Agent is a management and production-supervisor console. "
            "It monitors order, ERP, APS, IOT, production/service-escalation, and garment-output data "
            "through read-only contracts, then turns evidence into management priorities."
        ),
        workflow=[
            "order_intake",
            "erp_input",
            "aps_scheduling",
            "iot_execution",
            "production_monitoring",
            "garment_output",
        ],
        permissions=[
            "Read mock ERP order intake data.",
            "Read mock APS schedule and work-order state.",
            "Read mock IOT machine status, program-file evidence, OEE, alarm, output, and quality state.",
            "Create local analysis objects, evidence logs, KPI logs, and service request candidates.",
            "Suggest confirmation owners and local follow-up actions while keeping final confirmation with the general manager.",
            "No schedule confirmation, no .co/.cx upload, no order release, no machine control, and no real ticket creation.",
        ],
        adapter_contracts=[
            {
                "adapter": "ERP Intake Adapter",
                "status": "mock_contract",
                "read": "orders, customer, style, quantity, due date, ERP sync state",
                "write": "none",
            },
            {
                "adapter": "APS Scheduling Adapter",
                "status": "read_only_planned",
                "read": "APS order tracking, machine scheduling, auto-scheduling candidates, machine aggregate, machine task, style, and yarn forecast fields",
                "write": "none in MVP",
            },
            {
                "adapter": "Santoni IOT Adapter",
                "status": "read_only_planned",
                "read": "IOT monitor, dashboard, data-analysis, device detail, machine resource, program evidence, output, downtime, alarm, scrap, and yield fields",
                "write": "none in MVP",
            },
            {
                "adapter": "Service Request Candidate Adapter",
                "status": "mock_contract",
                "read": "production alarms and quality holds",
                "write": "candidate only; no dispatch",
            },
            {
                "adapter": "Tianpai Material Inventory Adapter",
                "status": "mock_contract",
                "read": "yarn product master data, production-task material balance aggregate, color, batch, twist, supplier, and stock movement fields",
                "write": "none",
            },
            {
                "adapter": "Tianpai APS/ERP Export Adapter",
                "status": "read_only_external_csv",
                "read": "Produce_Order, Weaving_Part_Order, Planned_Task, Manual_Machine_Production, Style_Component, Style_Sku, and T_Machine_Info exports using 表字段 DDL field order for actual-data Q&A.",
                "write": "none",
            },
        ],
        adapter_field_mapping=[
            {
                "object": "production_order",
                "console_section": "order",
                "source_system": "APS",
                "source_pages": ["weaving_monitor", "production_order", "style_management"],
                "observed_fields": ["order_code", "delivery_date", "overdue_days", "style_count", "remaining_quantity", "customer", "required_style", "status"],
                "normalized_fields": ["order_id", "due_date", "overdue_days", "style_count", "remaining_quantity", "customer", "style_code", "production_status"],
            },
            {
                "object": "yarn_material_forecast",
                "console_section": "order",
                "source_system": "APS",
                "source_pages": ["yarn_forecast"],
                "observed_fields": ["sku", "garment_part", "machine_size", "forecast_quantity", "yarn_code", "lot", "supplier", "color", "demand_kg", "stock_kg", "in_transit_kg"],
                "normalized_fields": ["sku", "garment_part", "machine_size", "forecast_quantity", "yarn_code", "lot", "supplier", "color", "demand_kg", "stock_kg", "in_transit_kg"],
            },
            {
                "object": "aps_schedule_capacity",
                "console_section": "scheduling",
                "source_system": "APS",
                "source_pages": ["machine_scheduling", "auto_scheduling", "machine_summary", "machine_task"],
                "observed_fields": ["machine_id", "cylinder_diameter", "gauge", "order_code", "style_code", "planned_quantity", "produced_quantity", "planned_window", "running_machine_count", "machine_running_rate", "capacity_pressure_days"],
                "normalized_fields": ["machine_id", "cylinder_diameter", "gauge", "order_id", "style_code", "planned_quantity", "produced_quantity", "planned_window", "running_machine_count", "machine_running_rate", "capacity_pressure_days"],
            },
            {
                "object": "iot_machine_execution",
                "console_section": "machine",
                "source_system": "Santoni IOT",
                "source_pages": ["iot_monitor", "iot_dashboard", "machine_detail"],
                "observed_fields": ["machine_id", "current_status", "status_duration", "model", "cylinder_diameter", "gauge", "shift_actual_output", "shift_theoretical_output", "time_availability_rate", "performance_availability_rate", "current_alarm"],
                "normalized_fields": ["machine_id", "iot_status", "status_duration", "model", "cylinder_diameter", "gauge", "actual_output", "theoretical_output", "time_availability_rate", "performance_availability_rate", "alarm"],
            },
            {
                "object": "iot_program_evidence",
                "console_section": "machine",
                "source_system": "Santoni IOT",
                "source_pages": ["machine_detail", "program_interface"],
                "observed_fields": ["order_code", "style_code", ".co_file", ".cx_file", "last_actual_cycle_seconds", "theoretical_cycle_seconds", "protocol_version", "last_data_time"],
                "normalized_fields": ["order_id", "style_code", "co_file", "cx_file", "last_actual_cycle_seconds", "theoretical_cycle_seconds", "protocol_version", "last_data_time"],
            },
            {
                "object": "garment_quality_output",
                "console_section": "garment",
                "source_system": "Santoni IOT",
                "source_pages": ["data_analysis", "machine_detail"],
                "observed_fields": ["actual_output_pieces", "theoretical_output_pieces", "scrap_quantity", "yield_rate", "shift_oee", "shift_scrap_quantity", "shift_defect_quantity"],
                "normalized_fields": ["actual_output", "theoretical_output", "scrap_quantity", "yield_rate", "shift_oee", "shift_scrap_quantity", "defect_quantity"],
            },
            {
                "object": "production_task_material_balance",
                "console_section": "material",
                "source_system": "ERP / Yarn inventory export",
                "source_pages": ["Yarn_Product", "Tianpai yarn inventory export"],
                "observed_fields": ["production_task_no", "material_code", "material_name", "color", "batch_no", "twist", "supplier", "unit", "opening_qty", "in_qty", "adjustment_qty", "out_qty", "balance_qty"],
                "normalized_fields": ["produce_order_code", "yarn_code", "yarn_name", "color", "batch", "twist", "supplier_code_or_name", "unit", "opening_qty", "in_qty", "adjustment_qty", "out_qty", "balance_qty"],
            },
        ],
        integration_notes=[
            "Current MVP snapshot is loaded from local static JSON at src/mock_data/production_operations.mock.json; it is not dynamically scraped from APS or Santoni IOT web pages.",
            "The production workflow must be joined by one canonical order_id across ERP, APS, IOT, production, service candidate, and garment output records.",
            "APS is the planned source for order, style, schedule, capacity pressure, machine plan, and yarn forecast fields.",
            "Santoni IOT is the planned source for live machine status, shift output, OEE, downtime, alarm, program evidence, scrap, and yield fields.",
            "The formal IOT program-interface page should be preferred for future integration over browser scraping.",
            "Credentials are session-only for manual research and must never be stored in code, mock data, docs, logs, or exports.",
        ],
        workflow_primary_key={
            "field": "order_id",
            "label": "order_id / order number",
            "role": "unique_workflow_spine",
            "description": "order_id / order number is the only canonical key used to join order intake, ERP sync, APS scheduling, IOT execution, production/service candidates, and garment output.",
            "future_integration_rule": "When APS/IOT databases or formal APIs are connected, every normalized production object must retain the same canonical order_id for workflow traceability.",
        },
        resource_lenses=["people", "machine", "material", "method", "environment", "measurement"],
        output_objects=[
            "production_overview",
            "production_object_model",
            "skill_registry",
            "management_priority_brief",
            "evidence_review_queue",
            "first_screen_service_risk",
            "mvp_demo_story",
            "stable_demo_story_pack",
            "mvp_success_check",
            "internal_demo_readiness_mode",
            "prd_alignment_audit",
            "tianpai_aps_erp_export",
            "actual_data_snapshot",
            "permission_boundary",
            "workflow_stages",
            "resource_lens",
            "optimization_signals",
            "service_escalations",
            "garment_output",
            "material_risk",
            "data_readiness",
            "general_manager_question_bank",
            "evidence_log",
            "kpi_log",
            "chatbi_root_cause_analysis",
        ],
        stages=[
            ProductionStage("order_intake", "Order Intake", "Sales / Customer Service", "order", "erp_order_object", "mock_contract", "none", "order intake completeness"),
            ProductionStage("erp_input", "ERP Input", "Planner / ERP Owner", "erp_order_object", "erp_sync_state", "mock_contract", "none", "ERP sync health"),
            ProductionStage("aps_scheduling", "APS Scheduling", "Planner", "erp_sync_state", "aps_schedule_object", "read_only_planned", "none in MVP", "schedule reliability"),
            ProductionStage("iot_execution", "IOT Execution", "Production Supervisor", "aps_schedule_object", "iot_execution_snapshot", "read_only_planned", "none in MVP", "OEE and downtime"),
            ProductionStage("production_monitoring", "Production / Service Escalation", "Production Manager / Service Manager", "iot_execution_snapshot", "resource_lens_and_service_request_candidates", "mock_contract", "analysis only; candidate only", "waste, bottleneck, and recovery lead time"),
            ProductionStage("garment_output", "Garment Output", "Quality / Warehouse", "production_result", "garment_output", "mock_contract", "none", "yield and output readiness"),
        ],
        kpis=[
            "oee",
            "downtime_minutes",
            "order_delay_risk",
            "material_risk",
            "labor_efficiency",
            "quality_risk",
            "waste_cost_opportunity",
            "capacity_occupation",
            "scrap_rate",
            "adapter_contract_coverage",
            "management_priority_items",
            "material_inventory_join_readiness",
            "data_readiness_score",
            "question_bank_coverage",
            "mvp_demo_story_coverage",
            "mvp_success_check_coverage",
            "prd_alignment_coverage",
            "tianpai_actual_export_readiness",
            "actual_data_evidence_chain_coverage",
            "skill_registry_coverage",
            "skill_execution_trace_coverage",
            "permission_boundary_coverage",
        ],
    )
    return asdict(template)


def production_adapter_contract() -> dict:
    template = production_operations_template()
    return {
        "contract_id": ADAPTER_CONTRACT_ID,
        "version": PRODUCTION_VERSION,
        "status": "mock_contract",
        "adapter_status": "mock_contract",
        "scope": "Read-only APS/IOT field mapping for the Production Operations Console.",
        "research_date": "2026-06-05",
        "credential_policy": "No APS/IOT credentials are stored in code, .env, mock data, docs, logs, exported files, or API responses.",
        "source_systems": [
            {
                "system": "APS",
                "adapter": "APS Scheduling Adapter",
                "status": "read_only_planned",
                "source_pages": ["weaving_monitor", "machine_scheduling", "machine_summary", "auto_scheduling", "yarn_forecast", "machine_task", "production_order", "style_management", "machine_resource"],
                "primary_console_sections": ["order", "scheduling"],
            },
            {
                "system": "Santoni IOT",
                "adapter": "Santoni IOT Adapter",
                "status": "read_only_planned",
                "source_pages": ["iot_monitor", "iot_dashboard", "data_analysis", "machine_detail", "program_interface", "factory_resource"],
                "primary_console_sections": ["machine", "garment"],
            },
            {
                "system": "ERP / Yarn Inventory",
                "adapter": "Tianpai Material Inventory Adapter",
                "status": "mock_contract",
                "source_pages": ["Yarn_Product", "Tianpai yarn inventory export"],
                "primary_console_sections": ["material", "data_readiness"],
            },
        ],
        "field_mapping": template["adapter_field_mapping"],
        "blocked_actions": [
            "login_from_demo_backend",
            "confirm_schedule",
            "start_auto_scheduling",
            "upload_co_file",
            "upload_cx_file",
            "release_order_to_machine",
            "control_machine",
            "save_iot_settings",
            "create_real_service_ticket",
        ],
        "next_adapter_steps": [
            "Request formal APS/IOT read-only API documentation and tokens from platform owners.",
            "Validate normalized field names with production, APS, and IOT owners.",
            "Replace mock snapshots with read-only API responses behind the same normalized objects.",
        ],
    }


class ProductionOperationsWorkflow:
    """Read-only production operations workflow over local mock data."""

    def __init__(self, data_path: Path | None = None, follow_up_store_path: Path | None = None) -> None:
        self.data_path = data_path or DATA_PATH
        self.follow_up_store_path = follow_up_store_path or FOLLOW_UP_REVIEW_PATH

    def template(self) -> dict:
        return production_operations_template()

    def adapter_contract(self) -> dict:
        return production_adapter_contract()

    def skill_registry(self) -> dict:
        return production_skill_registry()

    def tianpai_aps_erp_export(self) -> dict:
        return self.tianpai_aps_erp_export_adapter().report()

    def tianpai_aps_erp_export_adapter(self) -> TianpaiApsErpExportAdapter:
        return TianpaiApsErpExportAdapter()

    def evidence_review_queue(self, filters: dict | None = None) -> dict:
        data = self._load_data()
        filtered = self._apply_filters(data, filters or {})
        result = self._build_result(filtered, filters or {}, scenario="evidence_review_queue")
        return {
            "workflow_template": result["workflow_template"],
            "workflow_instance": result["workflow_instance"],
            "production_object_model": result["production_object_model"],
            "evidence_review_queue": result["evidence_review_queue"],
            "management_priority_brief": result["management_priority_brief"],
            "permission_boundary": result["permission_boundary"],
            "data_source": result["data_source"],
            "workflow_primary_key": result["workflow_primary_key"],
            "blocked_actions": result["workflow_instance"]["blocked_actions"],
        }

    def priority_brief(self, filters: dict | None = None) -> dict:
        data = self._load_data()
        filtered = self._apply_filters(data, filters or {})
        result = self._build_result(filtered, filters or {}, scenario="management_priority_brief")
        return {
            "workflow_template": result["workflow_template"],
            "workflow_instance": result["workflow_instance"],
            "production_object_model": result["production_object_model"],
            "skill_registry": result["skill_registry"],
            "management_priority_brief": result["management_priority_brief"],
            "data_source": result["data_source"],
            "workflow_primary_key": result["workflow_primary_key"],
            "evidence_log": result["evidence_log"],
            "blocked_actions": result["workflow_instance"]["blocked_actions"],
        }

    def follow_up_loop(self, filters: dict | None = None) -> dict:
        data = self._load_data()
        filtered = self._apply_filters(data, filters or {})
        result = self._build_result(filtered, filters or {}, scenario="decision_loop_follow_up")
        return {
            "workflow_template": result["workflow_template"],
            "workflow_instance": result["workflow_instance"],
            "production_object_model": result["production_object_model"],
            "skill_registry": result["skill_registry"],
            "management_priority_brief": result["management_priority_brief"],
            "decision_loop": result["decision_loop"],
            "data_source": result["data_source"],
            "workflow_primary_key": result["workflow_primary_key"],
            "evidence_log": result["evidence_log"],
            "blocked_actions": result["workflow_instance"]["blocked_actions"],
        }

    def demo_story_pack(self) -> dict:
        data = self._load_data()
        result = self._build_result(data, {}, scenario="stable_demo_story_pack")
        return {
            "workflow_template": result["workflow_template"],
            "workflow_instance": result["workflow_instance"],
            "stable_demo_story_pack": result["stable_demo_story_pack"],
            "management_priority_brief": result["management_priority_brief"],
            "first_screen_service_risk": result["first_screen_service_risk"],
            "actual_data_snapshot": result["actual_data_snapshot"],
            "permission_boundary": result["permission_boundary"],
            "data_source": result["data_source"],
            "workflow_primary_key": result["workflow_primary_key"],
            "blocked_actions": result["workflow_instance"]["blocked_actions"],
        }

    def internal_demo_candidate(self) -> dict:
        data = self._load_data()
        result = self._build_result(data, {}, scenario="internal_demo_candidate")
        return {
            "workflow_template": result["workflow_template"],
            "workflow_instance": result["workflow_instance"],
            "internal_demo_candidate": result["internal_demo_candidate"],
            "guided_demo_flow": result["guided_demo_flow"],
            "presenter_mode": result["presenter_mode"],
            "evidence_boundary_layer": result["evidence_boundary_layer"],
            "gm_question_regression_set": result["gm_question_regression_set"],
            "data_request_wizard": result["data_request_wizard"],
            "service_risk_confirmation_flow": result["service_risk_confirmation_flow"],
            "visible_athena_skill_process": result["visible_athena_skill_process"],
            "hermes_training_memory_review": result["hermes_training_memory_review"],
            "stable_demo_story_pack": result["stable_demo_story_pack"],
            "permission_boundary": result["permission_boundary"],
            "data_source": result["data_source"],
            "blocked_actions": result["workflow_instance"]["blocked_actions"],
        }

    def material_risk(self, filters: dict | None = None) -> dict:
        data = self._load_data()
        filtered = self._apply_filters(data, filters or {})
        result = self._build_result(filtered, filters or {}, scenario="tianpai_material_risk")
        return {
            "workflow_template": result["workflow_template"],
            "workflow_instance": result["workflow_instance"],
            "material_risk": result["material_risk"],
            "data_readiness": result["data_readiness"],
            "workflow_primary_key": result["workflow_primary_key"],
            "data_source": result["data_source"],
            "evidence_log": [
                item for item in result["evidence_log"] if item.get("evidence_id") in result["material_risk"].get("evidence_refs", [])
            ],
            "blocked_actions": result["workflow_instance"]["blocked_actions"],
        }

    def data_readiness(self, filters: dict | None = None) -> dict:
        data = self._load_data()
        filtered = self._apply_filters(data, filters or {})
        result = self._build_result(filtered, filters or {}, scenario="tianpai_data_readiness")
        return {
            "workflow_template": result["workflow_template"],
            "workflow_instance": result["workflow_instance"],
            "data_readiness": result["data_readiness"],
            "general_manager_question_bank": result["general_manager_question_bank"],
            "material_risk": result["material_risk"],
            "data_source": result["data_source"],
            "evidence_log": result["evidence_log"],
            "blocked_actions": result["workflow_instance"]["blocked_actions"],
        }

    def question_bank(self, filters: dict | None = None) -> dict:
        data = self._load_data()
        filtered = self._apply_filters(data, filters or {})
        result = self._build_result(filtered, filters or {}, scenario="general_manager_question_bank")
        return {
            "workflow_template": result["workflow_template"],
            "workflow_instance": result["workflow_instance"],
            "general_manager_question_bank": result["general_manager_question_bank"],
            "data_readiness": result["data_readiness"],
            "data_source": result["data_source"],
            "blocked_actions": result["workflow_instance"]["blocked_actions"],
        }

    def apply_follow_up_review(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        action_id = str(payload.get("action_id") or "").strip()
        review_status = str(payload.get("review_status") or "").strip()
        allowed_statuses = {
            "pending_confirmation",
            "assigned",
            "waiting_evidence",
            "confirmed",
            "closed",
            "unable_to_process",
            "needs_more_data",
            "resolved",
            "dismissed",
        }
        if not action_id:
            raise ValueError("action_id is required")
        if review_status not in allowed_statuses:
            raise ValueError(f"review_status must be one of {sorted(allowed_statuses)}")

        note = str(payload.get("review_note") or payload.get("owner_note") or "").strip()
        evidence_note = str(payload.get("evidence_note") or "").strip()
        self._reject_sensitive_review_text("review_note", note)
        self._reject_sensitive_review_text("evidence_note", evidence_note)

        loop = self.follow_up_loop()
        action_ids = {item["action_id"] for item in loop["decision_loop"]["action_items"]}
        if action_id not in action_ids:
            raise ValueError(f"Unknown action_id: {action_id}")

        store = self._load_follow_up_store()
        review = {
            "review_id": f"FUR-{PRODUCTION_VERSION}-{len(store.get('reviews', [])) + 1:03d}",
            "action_id": action_id,
            "follow_up_id": str(payload.get("follow_up_id") or f"FU-{action_id.removeprefix('ACT-')}").strip(),
            "review_status": review_status,
            "owner_role": str(payload.get("owner_role") or "").strip(),
            "review_note": note,
            "evidence_note": evidence_note,
            "reviewed_by": str(payload.get("reviewed_by") or "production_console").strip(),
            "reviewed_at": datetime.now().isoformat(timespec="seconds"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }
        store.setdefault("reviews", []).append(review)
        store["version"] = PRODUCTION_VERSION
        store["latest_reviewed_at"] = review["reviewed_at"]
        self._save_follow_up_store(store)
        return self.follow_up_loop()

    def overview(self, filters: dict | None = None) -> dict:
        data = self._load_data()
        filtered = self._apply_filters(data, filters or {})
        return self._build_result(filtered, filters or {}, scenario=None)

    def daily_brief(self, filters: dict | None = None) -> dict:
        data = self._load_data()
        filtered = self._apply_filters(data, filters or {})
        result = self._build_result(filtered, filters or {}, scenario="daily_brief_narrative")
        return {
            "workflow_template": result["workflow_template"],
            "workflow_instance": result["workflow_instance"],
            "daily_brief_narrative": result["daily_brief_narrative"],
            "management_priority_brief": result["management_priority_brief"],
            "evidence_review_queue": result["evidence_review_queue"],
            "first_screen_service_risk": result["first_screen_service_risk"],
            "decision_loop": result["decision_loop"],
            "permission_boundary": result["permission_boundary"],
            "blocked_actions": result["workflow_instance"]["blocked_actions"],
        }

    def analyze(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        data = self._load_data()
        filtered = self._apply_filters(data, payload.get("filters", {}))
        result = self._build_result(filtered, payload.get("filters", {}), scenario=payload.get("scenario"))
        result["analysis_request"] = {
            "filters": payload.get("filters", {}),
            "scenario": payload.get("scenario") or "current_mock_snapshot",
            "write_actions_blocked": True,
        }
        return result

    def chatbi(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        question = str(payload.get("question") or payload.get("message") or "").strip()
        data = self._load_data()
        result = self._build_result(data, payload.get("filters", {}), scenario="chatbi_root_cause")
        actual_analysis = self.tianpai_aps_erp_export_adapter().answer_management_question(question)
        analysis = self._with_management_template(actual_analysis or self._chatbi_analysis(data, result, question))
        evidence_refs = {
            ref
            for cause in analysis.get("root_causes", [])
            for ref in cause.get("evidence_refs", [])
        }
        trace_source_priority = self._trace_priority_for_chatbi_metric(result["management_priority_brief"], analysis.get("metric", ""))
        skill_execution_trace = analysis.get("skill_execution_trace") or (
            trace_source_priority.get("skill_execution_trace", []) if trace_source_priority else []
        )
        verification_process = self._manager_verification_process(
            analysis,
            skill_execution_trace,
            trace_source_priority,
            result,
        )
        return {
            "agent": {
                "agent_id": "athena.production_chatbi_agent.v1",
                "version": PRODUCTION_VERSION,
                "name": "Santoni Athena",
                "positioning": "Read-only question-to-data root cause analysis for production KPIs.",
            },
            "question": question,
            "language": analysis["language"],
            "metric": analysis["metric"],
            "actual_data_mode": analysis.get("actual_data_mode", False),
            "read_only": True,
            "write_actions_blocked": True,
            "answer_summary": analysis["answer_summary"],
            "executive_answer": analysis["executive_answer"],
            "metric_snapshot": analysis["metric_snapshot"],
            "root_causes": analysis["root_causes"],
            "recommended_actions": analysis["recommended_actions"],
            "next_drilldowns": analysis["next_drilldowns"],
            "data_gaps": analysis["data_gaps"],
            "management_priority_brief": analysis.get("management_priority_brief") or result["management_priority_brief"],
            "decision_loop": analysis.get("decision_loop") or result["decision_loop"],
            "confidence": analysis["confidence"],
            "source_objects": analysis["source_objects"],
            "actual_evidence_chains": analysis.get("actual_evidence_chains", []),
            "evidence_review_queue": result.get("evidence_review_queue", {}),
            "verification_process": verification_process,
            "skill_registry": self.skill_registry(),
            "skills_used": trace_source_priority.get("skills_used", []) if trace_source_priority else [],
            "skill_execution_trace": skill_execution_trace,
            "data_source": self._data_source_metadata(),
            "blocked_actions": result["workflow_instance"]["blocked_actions"],
            "evidence_log": analysis.get("evidence_log", []) or [
                item for item in data.get("evidence_log", []) if item.get("evidence_id") in evidence_refs
            ],
        }

    def _manager_verification_process(
        self,
        analysis: dict,
        skill_execution_trace: list[dict],
        trace_source_priority: dict,
        result: dict,
    ) -> dict:
        language = analysis.get("language", "en")
        root_causes = analysis.get("root_causes", [])
        data_gaps = analysis.get("data_gaps", [])
        evidence_refs = list(dict.fromkeys(
            ref
            for cause in root_causes
            for ref in cause.get("evidence_refs", [])
            if ref
        ))
        if not evidence_refs:
            evidence_refs = list(dict.fromkeys(
                ref
                for step in skill_execution_trace
                for ref in step.get("evidence_refs", [])
                if ref
            ))
        evidence_level = (
            (skill_execution_trace[0].get("evidence_level") if skill_execution_trace else "")
            or trace_source_priority.get("evidence_level")
            or ("Level 2: external APS/ERP export evidence" if analysis.get("actual_data_mode") else "Level 1: mock / demo evidence")
        )
        checked_object_ids = []
        for step in skill_execution_trace:
            checked_object_ids.extend(step.get("data_objects_checked", [])[:4])
        checked_object_ids.extend(analysis.get("source_objects", []))
        checked_object_ids = list(dict.fromkeys([item for item in checked_object_ids if item]))[:8]

        checked_objects = [
            {
                "object": item,
                "manager_label": self._manager_object_label(item, "en"),
                "manager_label_zh": self._manager_object_label(item, "zh"),
                "why_checked": self._manager_object_reason(item, language),
            }
            for item in checked_object_ids
        ]
        findings = [
            {
                "finding": cause.get("cause", ""),
                "evidence_refs": cause.get("evidence_refs", []),
                "support_level": evidence_level,
            }
            for cause in root_causes[:3]
        ]
        suggested_owner = (
            trace_source_priority.get("owner_role")
            or trace_source_priority.get("action_candidate", {}).get("owner_role")
            or self._choose(language, "Production Manager / Maintenance Owner", "生产主管 / 机修负责人")
        )
        cannot_conclude = data_gaps[:4] or [
            self._choose(
                language,
                "Current evidence is enough for risk review, but not enough for a final root-cause conclusion.",
                "当前证据足够提示风险，但还不足以确认最终根因。",
            )
        ]
        return {
            "schema_id": "athena.manager_verification_process.v1",
            "version": PRODUCTION_VERSION,
            "summary": self._choose(
                language,
                "Athena checked the available production evidence before recommending the next confirmation owner.",
                "Athena 已先查证当前可用的生产证据，再建议下一步由谁确认。",
            ),
            "checked_objects": checked_objects,
            "findings": findings,
            "evidence_level": evidence_level,
            "evidence_level_label_zh": self._manager_evidence_level_label(evidence_level),
            "cannot_conclude": cannot_conclude,
            "data_gap": cannot_conclude[0] if cannot_conclude else "",
            "suggested_confirmation_owner": suggested_owner,
            "evidence_refs": evidence_refs[:12],
            "raw_debug_trace_hidden": True,
            "read_only": True,
            "blocked_actions": result["workflow_instance"].get("blocked_actions", []),
        }

    @staticmethod
    def _manager_object_label(item: str, language: str) -> str:
        text = str(item or "").lower()
        labels = [
            (("order", "produce_order", "delivery"), ("Order / delivery", "Order / delivery")),
            (("aps", "schedule", "planned_task"), ("APS schedule", "APS schedule")),
            (("machine", "iot", "alarm", "downtime"), ("Machine / IOT signal", "Machine / IOT signal")),
            (("material", "yarn"), ("Material / yarn", "Material / yarn")),
            (("service", "maintenance"), ("Service risk", "Service risk")),
            (("quality", "scrap", "defect", "yield"), ("Quality / scrap", "Quality / scrap")),
            (("labor", "team", "shift"), ("Labor / shift", "Labor / shift")),
            (("evidence",), ("Evidence chain", "Evidence chain")),
        ]
        for tokens, value in labels:
            if any(token in text for token in tokens):
                return value[1] if language == "zh" else value[0]
        return item

    def _manager_object_reason(self, item: str, language: str) -> str:
        label = self._manager_object_label(item, language)
        reasons_en = {
            "Order / delivery": "Check whether the risk affects delivery.",
            "APS schedule": "Check whether schedule, planned quantity, and completion support the judgment.",
            "Machine / IOT signal": "Check whether stoppage, alarm, or machine load creates a bottleneck.",
            "Material / yarn": "Check whether material may limit production progress.",
            "Service risk": "Check whether maintenance or Service owner should intervene.",
            "Quality / scrap": "Check whether quality issues affect replenishment or rework.",
            "Labor / shift": "Check whether effective hours or manual intervention affects pace.",
            "Evidence chain": "Check whether the conclusion is supported by evidence.",
        }
        reasons_zh = {
            "Order / delivery": "????????????????",
            "APS schedule": "?????????????????????",
            "Machine / IOT signal": "???????????????????",
            "Material / yarn": "?????????????",
            "Service risk": "????????? Service ??????",
            "Quality / scrap": "????????????????",
            "Labor / shift": "??????????????????",
            "Evidence chain": "????????????",
        }
        if language == "zh":
            return reasons_zh.get(label, "????????????????")
        return reasons_en.get(label, "Check whether this object supports the current risk judgment.")
    @staticmethod
    def _manager_evidence_level_label(evidence_level: str) -> str:
        text = str(evidence_level or "").lower()
        if "level 4" in text:
            return "Level 4：实时系统证据"
        if "level 3" in text:
            return "Level 3：跨系统一致证据"
        if "level 2" in text or "export" in text:
            return "Level 2：Excel / APS 导出证据"
        return "Level 1：mock / demo 证据"
    @staticmethod
    def _trace_priority_for_chatbi_metric(brief: dict, metric: str) -> dict:
        metric_theme = {
            "order_delay": "delivery",
            "machine_style_mismatch": "equipment",
            "machine_plan_load": "equipment",
            "unscheduled_weaving_part_order": "material",
            "material_risk": "material",
            "quantity_report_gap": "cost",
            "machine_bottleneck": "equipment",
            "scrap_rate": "quality",
            "oee": "equipment",
            "downtime": "equipment",
            "labor_efficiency": "labor",
            "management_priority": "",
        }.get(metric, "")
        priorities = brief.get("top_priorities", [])
        if metric_theme:
            for priority in priorities:
                if (priority.get("risk_theme") or priority.get("management_theme")) == metric_theme:
                    return priority
        return priorities[0] if priorities else {}

    def _load_data(self) -> dict:
        return json.loads(self.data_path.read_text(encoding="utf-8"))

    def _data_source_metadata(self) -> dict:
        try:
            source_path = self.data_path.relative_to(Path.cwd())
        except ValueError:
            source_path = self.data_path
        return {
            "mode": "static_mock_json",
            "source": str(source_path).replace("\\", "/"),
            "dynamic_aps_iot_scraping": False,
            "read_only_adapter_status": "planned",
            "note": "Current demo reads a local static mock snapshot. APS/IOT web pages were researched for field mapping only; live read-only adapters are not connected yet.",
        }

    def _apply_filters(self, data: dict, filters: dict) -> dict:
        if not filters:
            return data

        result = dict(data)
        order_id = filters.get("order_id")
        machine_id = filters.get("machine_id")

        if order_id:
            result["orders"] = [item for item in data.get("orders", []) if item.get("order_id") == order_id]
            result["aps_schedule"] = [item for item in data.get("aps_schedule", []) if item.get("order_id") == order_id]
            result["machines"] = [item for item in data.get("machines", []) if item.get("order_id") == order_id]
            result["materials"] = [
                item for item in data.get("materials", []) if order_id in item.get("required_orders", [])
            ]
            result["process"] = [item for item in data.get("process", []) if item.get("order_id") == order_id]
            result["measurement"] = [item for item in data.get("measurement", []) if item.get("order_id") == order_id]

        if machine_id:
            result["machines"] = [item for item in result.get("machines", []) if item.get("machine_id") == machine_id]
            linked_orders = {item.get("order_id") for item in result["machines"] if item.get("order_id")}
            if linked_orders:
                result["orders"] = [item for item in result.get("orders", []) if item.get("order_id") in linked_orders]
                result["aps_schedule"] = [
                    item for item in result.get("aps_schedule", []) if item.get("order_id") in linked_orders
                ]

        return result

    def _production_object_model(self) -> dict:
        return {
            "schema_id": "athena.production_object_model.v1",
            "version": PRODUCTION_VERSION,
            "positioning": (
                "Athena reads production through structured objects instead of free-form BI questions. "
                "Every decision must connect order, process, signal, evidence, action, and future memory."
            ),
            "canonical_workflow_key": {
                "field": "order_id",
                "site_term": "订单",
                "rule": "Use order_id as the workflow spine whenever a source system exposes it; otherwise mark the object as unjoined evidence.",
            },
            "objects": [
                {
                    "object": "order",
                    "site_term": "订单",
                    "required_fields": ["order_id", "customer", "style_code", "quantity", "remaining_quantity", "due_date", "erp_status", "aps_status"],
                    "joins": ["style", "material", "aps_schedule", "machine", "measurement", "garment_output"],
                    "evidence_policy": "Order-level claims require ERP/APS evidence or an explicit mock evidence_ref.",
                },
                {
                    "object": "style",
                    "site_term": "娆惧紡",
                    "required_fields": ["style_code", "garment", "style_count"],
                    "joins": ["order", "machine", "method", "measurement"],
                    "evidence_policy": "Style risk must be linked to an order or quality/engineering evidence.",
                },
                {
                    "object": "machine",
                    "site_term": "鏈哄彴",
                    "required_fields": ["machine_id", "model", "state", "order_id", "oee", "downtime_minutes", "alarm"],
                    "joins": ["order", "aps_schedule", "method", "service_request_candidate"],
                    "evidence_policy": "Machine bottlenecks require IOT or machine-monitor evidence.",
                },
                {
                    "object": "material_inventory",
                    "site_term": "鏂?/ 绾辩嚎搴撳瓨",
                    "required_fields": ["produce_order_code", "yarn_code", "batch", "supplier_code_or_name", "unit", "balance_qty"],
                    "joins": ["order", "style", "aps_schedule", "measurement"],
                    "evidence_policy": "Material-risk claims can use inventory aggregates now; order impact still requires ERP/APS produce_order_code confirmation and BOM demand.",
                },
                {
                    "object": "process_stage",
                    "site_term": "宸ュ簭",
                    "required_fields": ["process_id", "order_id", "route", "setup_minutes", "changeover_variance_minutes"],
                    "joins": ["order", "method", "measurement"],
                    "evidence_policy": ".co/.cx status is read-only evidence; it never triggers upload or machine control.",
                },
                {
                    "object": "production_signal",
                    "site_term": "寮傚父淇″彿",
                    "required_fields": ["signal_id", "theme", "severity", "affected_objects", "evidence_refs"],
                    "joins": ["decision", "action", "follow_up"],
                    "evidence_policy": "A signal without evidence_refs cannot become a management priority.",
                },
                {
                    "object": "evidence",
                    "site_term": "璇佹嵁",
                    "required_fields": ["evidence_id", "source", "claim", "adapter_status"],
                    "joins": ["production_signal", "decision", "memory_event"],
                    "evidence_policy": "Evidence must name its source and adapter status before Athena can cite it in a decision.",
                },
                {
                    "object": "decision",
                    "site_term": "鍒ゆ柇",
                    "required_fields": ["decision_id", "priority", "conclusion", "reason", "evidence_refs", "data_gaps"],
                    "joins": ["action", "follow_up", "memory_event"],
                    "evidence_policy": "Decision text must separate evidence-backed findings from unavailable data.",
                },
                {
                    "object": "action",
                    "site_term": "鍔ㄤ綔",
                    "required_fields": ["action_id", "owner_role", "recommended_action", "requires_human_confirmation", "status"],
                    "joins": ["decision", "follow_up"],
                    "evidence_policy": "Production MVP can propose actions only; it cannot write APS/IOT/service systems.",
                },
                {
                    "object": "follow_up",
                    "site_term": "璺熻繘",
                    "required_fields": ["follow_up_id", "owner_role", "expected_evidence", "review_time", "status"],
                    "joins": ["action", "memory_event"],
                    "evidence_policy": "Follow-up closure will require owner confirmation and result evidence in the next engine stage.",
                },
                {
                    "object": "memory_event",
                    "site_term": "缁勭粐璁板繂",
                    "required_fields": ["scope", "tenant_id", "factory_id", "source", "retention_policy", "sensitivity_level", "promotion_status"],
                    "joins": ["decision", "action", "follow_up", "playbook"],
                    "evidence_policy": "Memory starts as candidate and needs review before promotion to product/domain playbook.",
                },
            ],
            "blocked_actions": [
                "change_production_schedule",
                "upload_co_file",
                "upload_cx_file",
                "control_machine",
                "create_real_service_ticket",
                "promote_memory_without_review",
            ],
        }

    def _material_risk(self, data: dict) -> dict:
        inventory = data.get("tianpai_material_inventory", {})
        source = inventory.get("source_summary", {})
        balance = inventory.get("balance_summary", {})
        zero_rows = int(balance.get("zero_balance_rows", 0))
        negative_rows = int(balance.get("negative_balance_rows", 0))
        row_count = int(source.get("row_count", 0))
        exception_rows = zero_rows + negative_rows
        exception_ratio = self._ratio(exception_rows, row_count)
        readiness_blockers = [
            "Confirm whether 生产任务单 equals APS/ERP produce_order_code, with or without prefix normalization.",
            "Confirm why negative balance exists before treating it as shortage.",
            "Connect BOM yarn demand by style_code and yarn_code before calculating shortage quantity.",
            "Connect quality/scrap records by produce_order_code, yarn_code, batch, and date before claiming material root cause.",
        ]
        return {
            "schema_id": "athena.production_material_risk.v1",
            "version": PRODUCTION_VERSION,
            "adapter_status": "mock_contract",
            "read_only": True,
            "source_summary": source,
            "inventory_structure": {
                "row_count": row_count,
                "task_order_rows": source.get("task_order_rows", 0),
                "common_inventory_rows": source.get("common_inventory_rows", 0),
                "unique_task_order_count": source.get("unique_task_order_count", 0),
                "unique_yarn_code_count": source.get("unique_yarn_code_count", 0),
                "unique_batch_count": source.get("unique_batch_count", 0),
                "unique_supplier_count": source.get("unique_supplier_count", 0),
                "unit_distribution": source.get("unit_distribution", []),
            },
            "dimension_distribution": inventory.get("dimension_distribution", {}),
            "balance_exceptions": {
                "zero_balance_rows": zero_rows,
                "negative_balance_rows": negative_rows,
                "positive_balance_rows": balance.get("positive_balance_rows", 0),
                "exception_row_count": exception_rows,
                "exception_row_ratio": round(exception_ratio, 3),
                "total_balance_quantity": balance.get("total_balance_quantity", 0),
                "quantity_unit": balance.get("quantity_unit", "kg"),
                "interpretation_required": balance.get("interpretation_required", True),
                "interpretation_note": balance.get("interpretation_note", ""),
            },
            "field_mapping": inventory.get("field_mapping", []),
            "yarn_product_schema": inventory.get("yarn_product_schema", {}),
            "risk_rules": inventory.get("risk_rules", []),
            "risk_signals": [
                {
                    "signal_id": "MAT-SIGNAL-BALANCE-001",
                    "priority": "P1",
                    "theme": "material_balance_interpretation",
                    "conclusion": f"{exception_rows} inventory rows have zero or negative balance and need warehouse/ERP interpretation.",
                    "conclusion_zh": f"{exception_rows} 行库存结存为 0 或负数，需要仓库/ERP 负责人确认业务含义。",
                    "evidence_refs": ["EV-PROD-027"],
                    "owner_role": "Warehouse / ERP Owner",
                    "data_gap": "Negative balance cannot be treated as true shortage until sign and movement rules are confirmed.",
                },
                {
                    "signal_id": "MAT-SIGNAL-JOIN-001",
                    "priority": "P0",
                    "theme": "order_join_readiness",
                    "conclusion": "Material data has production task order fields, but ERP order and APS produce_order_code mapping still need confirmation.",
                    "conclusion_zh": "物料数据已有生产任务单字段，但还需要确认它和 ERP 订单、APS produce_order_code 的映射关系。",
                    "evidence_refs": ["EV-PROD-028"],
                    "owner_role": "ERP / APS Owner",
                    "data_gap": "Without the join rule, Athena can describe material inventory but cannot prove delivery impact by order.",
                },
            ],
            "future_join_plan": inventory.get("future_join_plan", []),
            "readiness_blockers": readiness_blockers,
            "can_answer_now": [
                "Yarn inventory structure by task order, yarn code, batch, color, twist, supplier count, and unit.",
                "Zero/negative/positive balance row counts as material-risk review signals.",
                "Which fields are ready for future ERP/APS/BOM/quality joins.",
            ],
            "cannot_answer_yet": [
                "Whether a specific customer order will be delayed by yarn shortage.",
                "Exact shortage quantity by order or style.",
                "Whether a yarn batch caused scrap or quality defects.",
                "Purchasing-cost or per-garment material-cost impact.",
            ],
            "evidence_refs": inventory.get("evidence_refs", []),
            "blocked_actions": [
                "write_inventory",
                "reserve_material",
                "change_aps_schedule",
                "claim_order_delay_without_erp_aps_join",
                "claim_material_quality_root_cause_without_quality_join",
            ],
        }

    def _general_manager_question_bank(self, data: dict) -> dict:
        questions = [
            ("GMQ-001", "P0", "delivery", "Which orders are most likely to be delayed?", ["erp_orders", "split_delivery", "aps_schedule", "production_output"], "conclusion_reason_evidence_recommendation", "hypothesis"),
            ("GMQ-002", "P0", "delivery", "How many backlog orders and remaining quantities do we have this week/month?", ["erp_orders", "shipment_records"], "summary_table_and_risk_list", "hypothesis"),
            ("GMQ-003", "P0", "management_priority", "Which three issues should the general manager review today?", ["erp_orders", "aps_schedule", "material_inventory", "quality", "iot"], "top_three_management_brief", "hypothesis"),
            ("GMQ-004", "P0", "root_cause", "Is delivery risk caused by scheduling, material, quality, or capacity?", ["erp_orders", "aps_schedule", "material_inventory", "quality", "iot"], "root_cause_split_with_data_gaps", "hypothesis"),
            ("GMQ-005", "P1", "style", "Which styles are dragging delivery?", ["erp_orders", "aps_schedule", "production_output"], "style_risk_ranking", "hypothesis"),
            ("GMQ-006", "P1", "material", "Which production task orders do not have enough yarn?", ["material_inventory", "bom_yarn_demand", "erp_aps_mapping"], "material_gap_by_task_order", "hypothesis"),
            ("GMQ-007", "P1", "material", "Which yarn batches or suppliers are highest risk?", ["material_inventory", "quality"], "batch_supplier_risk_ranking", "hypothesis"),
            ("GMQ-008", "P1", "early_warning", "Which orders are not late yet but close to the risk boundary?", ["erp_orders", "aps_schedule", "material_inventory"], "early_warning_list", "hypothesis"),
            ("GMQ-009", "P1", "cost_proxy", "Which orders may need air freight or acceleration?", ["erp_orders", "estimated_finish", "freight_rules"], "delivery_to_cost_risk", "hypothesis"),
            ("GMQ-010", "P1", "quality", "Which styles or process stages concentrate quality issues?", ["quality", "rework", "process_stage"], "quality_reason_ranking", "hypothesis"),
            ("GMQ-011", "P1", "quality_root_cause", "Is scrap caused by style, machine, material, team, or method?", ["iot_scrap", "machine", "style", "material_inventory", "shift_team"], "scrap_root_cause_split", "hypothesis"),
            ("GMQ-012", "P2", "machine", "Which machines are current bottlenecks?", ["aps_schedule", "iot_machine"], "machine_bottleneck_ranking", "hypothesis"),
            ("GMQ-013", "P2", "schedule_variance", "Which orders deviate most from plan?", ["aps_schedule", "actual_output"], "plan_vs_actual_variance", "hypothesis"),
            ("GMQ-014", "P2", "customer_style_history", "Which customers or styles often create rush orders, delays, or rework?", ["erp_history", "order_changes", "rework"], "history_risk_patterns", "hypothesis"),
            ("GMQ-015", "P2", "inventory", "Which yarn inventory is excessive or possibly idle?", ["material_inventory", "demand_history"], "slow_moving_inventory", "hypothesis"),
            ("GMQ-016", "P2", "cost", "Which orders have high cost risk?", ["purchasing_cost", "labor", "rework", "freight"], "cost_proxy_until_real_cost", "hypothesis"),
            ("GMQ-017", "P2", "data_governance", "Which data gaps prevent Athena from making a conclusion?", ["all_connected_sources"], "missing_data_owner_list", "hypothesis"),
        ]
        available_sources = self._available_data_source_ids(data)
        question_items = []
        for question_id, priority, theme, question, required_sources, template, status in questions:
            available_required = [source for source in required_sources if source in available_sources]
            missing_required = [source for source in required_sources if source not in available_sources]
            readiness = "answerable_now" if not missing_required else "partial" if available_required else "blocked"
            question_items.append(
                {
                    "question_id": question_id,
                    "priority": priority,
                    "theme": theme,
                    "question": question,
                    "required_data_sources": required_sources,
                    "available_data_sources": available_required,
                    "missing_data_sources": missing_required,
                    "answer_template": template,
                    "evidence_requirements": self._question_evidence_requirements(theme),
                    "data_gap_behavior": "State the unavailable source and avoid claiming root cause when required evidence is missing.",
                    "verification_status": status,
                    "current_readiness": readiness,
                }
            )
        return {
            "schema_id": "athena.general_manager_question_bank.v1",
            "version": PRODUCTION_VERSION,
            "persona": "tianpai_general_manager",
            "status": "hypothesis_pending_voc",
            "verification_owner": "Product Owner + Agnes + Tianpai onsite roles",
            "question_count": len(question_items),
            "questions": question_items,
            "answer_format": {
                "template": "conclusion + reason/evidence + risk + recommendation + data_gap + next_confirmation_owner",
                "required_sections": ["conclusion", "reason_evidence", "risk", "recommendation", "data_gap", "next_confirmation_owner"],
            },
            "review_plan": [
                "Product Owner reviews whether each question belongs in Athena long-term.",
                "Agnes validates whether the question reflects management concern.",
                "Planner, warehouse, production, quality, APS/IOT/ERP owners validate field meaning and actionability.",
                "Final customer management review changes verification_status from hypothesis to reviewed or approved.",
            ],
            "blocked_actions": [
                "treat_hypothesis_as_confirmed_voc",
                "train_as_approved_without_customer_review",
                "claim_answerability_when_required_sources_are_missing",
            ],
        }

    def _data_readiness(self, data: dict, material_risk: dict, question_bank: dict) -> dict:
        sources = [
            {
                "source_id": "agnes_voc",
                "name": "Agnes VOC",
                "status": "available",
                "fields": ["delivery_priority", "quality_priority", "cost_data_need", "data_limitations"],
                "supports_questions": ["GMQ-001", "GMQ-003", "GMQ-004", "GMQ-016", "GMQ-017"],
                "confidence": "medium",
                "owner_to_confirm": "Agnes / Product Owner",
            },
            {
                "source_id": "aps_schedule",
                "name": "APS Planned Task / schedule evidence",
                "status": "partial_available",
                "fields": ["produce_order_code", "machine_id", "style_code", "planned_quantity", "produced_quantity", "plan_start_time", "plan_end_time", "estimate_end_time", "delivery_time"],
                "supports_questions": ["GMQ-001", "GMQ-004", "GMQ-005", "GMQ-012", "GMQ-013"],
                "confidence": "medium",
                "owner_to_confirm": "APS Owner / Planner",
            },
            {
                "source_id": "iot",
                "name": "Tianpai IOT weekly exports",
                "status": "partial_available_unjoined",
                "fields": ["machine", "style", "shift output", "scrap", "fault"],
                "supports_questions": ["GMQ-011", "GMQ-012"],
                "confidence": "low_medium",
                "owner_to_confirm": "IOT Owner / Production Supervisor",
            },
            {
                "source_id": "material_inventory",
                "name": "Tianpai yarn inventory aggregate",
                "status": "available_aggregate",
                "fields": ["produce_order_code", "yarn_code", "yarn_name", "color", "batch", "twist", "supplier", "opening_qty", "in_qty", "adjustment_qty", "out_qty", "balance_qty"],
                "supports_questions": ["GMQ-006", "GMQ-007", "GMQ-015", "GMQ-017"],
                "confidence": "medium",
                "owner_to_confirm": "Warehouse / ERP Owner",
            },
            {
                "source_id": "erp_orders",
                "name": "ERP order and split-delivery records",
                "status": "not_available",
                "fields": ["order_id", "customer_id", "style_code", "order_qty", "created_date", "delivery_date", "split_delivery", "order_status"],
                "supports_questions": ["GMQ-001", "GMQ-002", "GMQ-003", "GMQ-004", "GMQ-008", "GMQ-014"],
                "confidence": "blocked",
                "owner_to_confirm": "Customer ERP Owner",
            },
            {
                "source_id": "bom_yarn_demand",
                "name": "Style/BOM yarn demand",
                "status": "not_available",
                "fields": ["style_code", "yarn_code", "required_qty_per_piece", "loss_rate", "required_total_qty"],
                "supports_questions": ["GMQ-006", "GMQ-015"],
                "confidence": "blocked",
                "owner_to_confirm": "ERP/BOM Owner",
            },
            {
                "source_id": "quality",
                "name": "Quality inspection, rework, replenishment records",
                "status": "not_available",
                "fields": ["order_id", "process_stage", "defect_reason", "defect_qty", "rework_qty", "replenishment_order"],
                "supports_questions": ["GMQ-007", "GMQ-010", "GMQ-011"],
                "confidence": "blocked",
                "owner_to_confirm": "Quality Owner",
            },
        ]
        source_status = {item["source_id"]: item["status"] for item in sources}
        ready_questions = [item for item in question_bank.get("questions", []) if item.get("current_readiness") == "answerable_now"]
        partial_questions = [item for item in question_bank.get("questions", []) if item.get("current_readiness") == "partial"]
        blocked_questions = [item for item in question_bank.get("questions", []) if item.get("current_readiness") == "blocked"]
        score = round(
            self._ratio(len(ready_questions) * 1.0 + len(partial_questions) * 0.45, max(1, question_bank.get("question_count", 1))),
            3,
        )
        return {
            "schema_id": "athena.tianpai_data_readiness.v1",
            "version": PRODUCTION_VERSION,
            "status": "partial_ready",
            "readiness_score": score,
            "data_sources": sources,
            "source_status": source_status,
            "question_coverage": {
                "question_count": question_bank.get("question_count", 0),
                "answerable_now": len(ready_questions),
                "partial": len(partial_questions),
                "blocked": len(blocked_questions),
                "answerable_question_ids": [item["question_id"] for item in ready_questions],
                "partial_question_ids": [item["question_id"] for item in partial_questions],
                "blocked_question_ids": [item["question_id"] for item in blocked_questions],
            },
            "can_answer_now": [
                "Material inventory structure, batch/color/twist/supplier coverage, and balance-exception review.",
                "APS schedule/task progress questions where produce_order_code is sufficient.",
                "IOT machine/scrap/fault trend questions when order-level causality is not claimed.",
                "Data-gap questions and next data request ownership.",
            ],
            "cannot_answer_yet": [
                "Full order-level delivery root cause without ERP order and split-delivery records.",
                "Material shortage impact by customer order without ERP/APS produce_order_code and BOM demand confirmation.",
                "Material-caused quality root cause without quality records joined to yarn batch and date.",
                "True per-garment cost without purchasing, labor, rework, and freight cost records.",
            ],
            "next_data_requests": [
                {
                    "request_id": "DATA-ERP-ORDER-MIN",
                    "owner_role": "Customer ERP Owner",
                    "fields": ["order_id", "style_code", "order_qty", "created_date", "delivery_date", "split_delivery", "status"],
                    "purpose": "Join ERP order commitments to APS weaving execution and delivery-risk analysis.",
                    "priority": "P0",
                    "sensitivity_level": "customer_operational",
                    "needed_for": ["GMQ-001", "GMQ-002", "GMQ-003", "GMQ-004", "GMQ-008"],
                },
                {
                    "request_id": "DATA-BOM-YARN-MIN",
                    "owner_role": "ERP/BOM Owner",
                    "fields": ["style_code", "yarn_code", "required_qty_per_piece", "loss_rate"],
                    "purpose": "Connect yarn material availability to order and style delivery risk.",
                    "priority": "P1",
                    "sensitivity_level": "customer_operational",
                    "needed_for": ["GMQ-006", "GMQ-015"],
                },
                {
                    "request_id": "DATA-QUALITY-MIN",
                    "owner_role": "Quality Owner",
                    "fields": ["produce_order_code", "style_code", "process_stage", "defect_reason", "defect_qty", "rework_qty"],
                    "purpose": "Connect defect and rework evidence to quality risk and replenishment decisions.",
                    "priority": "P1",
                    "sensitivity_level": "customer_operational",
                    "needed_for": ["GMQ-007", "GMQ-010", "GMQ-011"],
                },
            ],
            "material_readiness_link": {
                "material_schema_id": material_risk.get("schema_id"),
                "material_exception_row_ratio": material_risk.get("balance_exceptions", {}).get("exception_row_ratio"),
                "material_join_blockers": material_risk.get("readiness_blockers", []),
            },
            "blocked_actions": [
                "claim_full_tianpai_root_cause",
                "claim_customer_cost_savings",
                "write_to_erp_aps_iot",
                "store_raw_customer_files",
            ],
        }

    def _available_data_source_ids(self, data: dict) -> set[str]:
        available = set()
        if data.get("orders"):
            available.add("mock_orders")
        if data.get("aps_schedule"):
            available.add("aps_schedule")
        if data.get("machines"):
            available.add("iot_machine")
        if data.get("measurement"):
            available.add("iot_scrap")
        if data.get("tianpai_material_inventory"):
            available.add("material_inventory")
        if data.get("materials"):
            available.add("aps_yarn_forecast")
        available.add("agnes_voc")
        available.add("all_connected_sources")
        return available

    def _question_evidence_requirements(self, theme: str) -> list[str]:
        base = ["evidence_refs", "data_source_status", "owner_confirmation_before_action"]
        by_theme = {
            "delivery": ["ERP order due date", "remaining quantity", "APS schedule or explicit data gap"],
            "management_priority": ["ranked KPI impact", "affected objects", "recommended owner"],
            "root_cause": ["cause category evidence", "missing-source statement when evidence is incomplete"],
            "material": ["produce_order_code", "yarn_code", "batch", "balance_qty", "BOM demand if shortage quantity is claimed"],
            "quality": ["inspection row", "defect reason", "process stage", "rework or replenishment impact"],
            "quality_root_cause": ["style", "machine", "material batch", "team/method evidence", "causal confidence"],
            "machine": ["machine_id", "OEE/downtime", "alarm/fault evidence", "program evidence if setup is mentioned"],
            "data_governance": ["missing field", "affected question", "data owner", "next request"],
        }
        return [*base, *by_theme.get(theme, ["structured source object"])]

    def _management_priority_brief(
        self,
        data: dict,
        overview: dict,
        resource_lens: dict,
        optimization_signals: list[dict],
        service_escalations: list[dict],
        garment_output: dict,
        actual_priority_analyses: list[dict] | None = None,
    ) -> dict:
        orders = data.get("orders", [])
        machines = data.get("machines", [])
        materials = data.get("materials", [])
        measurements = data.get("measurement", [])
        labor = data.get("labor", [])
        inventory = data.get("tianpai_material_inventory", {})
        inventory_source = inventory.get("source_summary", {})
        inventory_balance = inventory.get("balance_summary", {})
        process = data.get("process", [])
        evidence_by_id = {item.get("evidence_id"): item for item in data.get("evidence_log", [])}
        orders_by_id = {item.get("order_id"): item for item in orders}
        machines_by_order = self._group_by(machines, "order_id")
        process_by_order = self._group_by(process, "order_id")

        priorities: list[dict] = []
        actual_priorities = self._actual_management_priorities(actual_priority_analyses or [])
        priorities.extend(actual_priorities)

        quality_items = sorted(
            [item for item in measurements if item.get("status") != "ok" or item.get("defect_rate", 0) >= 0.03],
            key=lambda item: (item.get("defect_rate", 0), item.get("scrap_quantity", 0)),
            reverse=True,
        )
        if quality_items:
            quality = quality_items[0]
            order = orders_by_id.get(quality.get("order_id"), {})
            linked_machines = machines_by_order.get(quality.get("order_id"), [])
            linked_process = process_by_order.get(quality.get("order_id"), [])
            evidence_refs = self._unique_refs(
                [
                    order.get("evidence_ref"),
                    quality.get("evidence_ref"),
                    *[item.get("evidence_ref") for item in linked_machines],
                    *[item.get("evidence_ref") for item in linked_process],
                ]
            )
            priorities.append(
                {
                    "priority_id": "MGMT-PRIO-QUALITY-001",
                    "rank": 0,
                    "priority": "P0" if order.get("production_status") == "quality_hold" else "P1",
                    "score": 96 if order.get("production_status") == "quality_hold" else 88,
                    "management_theme": "quality",
                    "theme_label": "璐ㄩ噺浼樺厛",
                    "title": f"Stabilize {order.get('style_code', quality.get('order_id'))} quality before expanding production",
                    "title_zh": f"先稳定 {order.get('style_code', quality.get('order_id'))} 质量，再扩大生产",
                    "management_question": "Will this quality issue damage customer trust or trigger replenishment cost?",
                    "conclusion": (
                        f"{order.get('order_id', quality.get('order_id'))} has quality warning, "
                        f"defect rate {quality.get('defect_rate', 0):.1%}, yield {quality.get('yield_rate', 0):.1%}."
                    ),
                    "conclusion_zh": (
                        f"{order.get('order_id', quality.get('order_id'))} 触发质量预警，"
                        f"缺陷率 {quality.get('defect_rate', 0):.1%}，良品率 {quality.get('yield_rate', 0):.1%}。"
                    ),
                    "reason": "Quality is ranked first because poor quality can lose repeat orders and create hidden cost beyond visible scrap.",
                    "reason_zh": "质量排第一，因为质量问题不只产生可见废品，还可能损害客户复购并形成隐性成本。",
                    "risk_if_ignored": "More rework, replenishment orders, delayed downstream sewing/packing, and customer confidence loss.",
                    "risk_if_ignored_zh": "如果不处理，可能带来返工、补单、后道缝制/包装延误和客户信任损失。",
                    "recommended_action": "Hold expansion on the affected style, review SM8-03 setup/program evidence, and confirm defect reasons before the next shift.",
                    "recommended_action_zh": "先暂停扩大该款生产，在下一个班次前复核 SM8-03 的 setup/程序证据，并确认不良原因。",
                    "owner_role": "Production Manager / Quality Owner",
                    "confirmation_needed_by": "next_shift_start",
                    "decision_gate": "quality_owner_confirms_root_cause_or_releases_hold",
                    "affected_objects": {
                        "orders": [quality.get("order_id")],
                        "styles": [order.get("style_code", "")],
                        "machines": [item.get("machine_id") for item in linked_machines],
                        "process_stages": [item.get("process_id") for item in linked_process],
                    },
                    "kpi_links": ["quality_risk", "scrap_rate", "average_yield_rate", "oee"],
                    "evidence_refs": evidence_refs,
                    "evidence_claims": self._evidence_claims(evidence_by_id, evidence_refs),
                    "data_gaps": [
                        "Need real defect inspection rows and downstream rework/replenishment records to prove full cost impact.",
                    ],
                    "action_candidate": self._priority_action_candidate(
                        "ACT-QUALITY-001",
                        "Production Manager / Quality Owner",
                        "Confirm whether fabric tension, logo elasticity, setup variance, or machine condition is the first cause.",
                        ["defect inspection row", "machine alarm history", ".co/.cx read-only evidence", "owner confirmation"],
                    ),
                }
            )

        risky_orders = [
            item for item in orders if item.get("aps_status") != "scheduled" or item.get("erp_status") == "exception"
        ]
        if risky_orders:
            material_refs = {
                material_ref
                for order in risky_orders
                for material_ref in order.get("yarn_material_refs", [])
            }
            linked_materials = [item for item in materials if item.get("material_id") in material_refs]
            evidence_refs = self._unique_refs(
                [
                    *[item.get("evidence_ref") for item in risky_orders],
                    *[item.get("evidence_ref") for item in linked_materials],
                ]
            )
            priorities.append(
                {
                    "priority_id": "MGMT-PRIO-DELIVERY-001",
                    "rank": 0,
                    "priority": "P1",
                    "score": 86,
                    "management_theme": "delivery",
                    "theme_label": "浜ゆ湡椋庨櫓",
                    "title": "Resolve unscheduled and material-held orders before they force air freight",
                    "title_zh": "先处理未排单和缺料订单，避免后续被迫空运。",
                    "management_question": "Which backlog items can still be protected before delivery risk becomes cost?",
                    "conclusion": (
                        f"{len(risky_orders)} orders need scheduling or ERP/material review; "
                        f"remaining quantity {sum(int(item.get('remaining_quantity', 0)) for item in risky_orders)}."
                    ),
                    "conclusion_zh": (
                        f"{len(risky_orders)} 个订单需要排单或 ERP/物料复核，"
                        f"剩余数量 {sum(int(item.get('remaining_quantity', 0)) for item in risky_orders)}。"
                    ),
                    "reason": "Delivery risk converts into cost when buffer is consumed and the only recovery option becomes overtime or air freight.",
                    "reason_zh": "交期风险会在缓冲被消耗后转化为成本，常见补救方式是加班或空运。",
                    "risk_if_ignored": "Planner firefighting, production resequencing, overtime, or air freight escalation.",
                    "risk_if_ignored_zh": "如果不处理，可能出现计划员救火、生产重排、加班或空运成本上升。",
                    "recommended_action": "Confirm ERP exception on ORD-20260605-004 and elastane lot E-224 availability before changing APS sequence.",
                    "recommended_action_zh": "在调整 APS 顺序前，先确认 ORD-20260605-004 的 ERP 异常和 E-224 氨纶批次到料情况。",
                    "owner_role": "Planner / ERP Owner",
                    "confirmation_needed_by": "same_day_planning_meeting",
                    "decision_gate": "erp_exception_closed_and_material_eta_confirmed",
                    "affected_objects": {
                        "orders": [item.get("order_id") for item in risky_orders],
                        "styles": [item.get("style_code") for item in risky_orders],
                        "materials": [item.get("material_id") for item in linked_materials],
                    },
                    "kpi_links": ["order_delay_risk", "material_risk", "capacity_occupation"],
                    "evidence_refs": evidence_refs,
                    "evidence_claims": self._evidence_claims(evidence_by_id, evidence_refs),
                    "data_gaps": [
                        "Need real order-created, promised delivery, shipment, and freight-mode records for production-grade delay cost.",
                    ],
                    "action_candidate": self._priority_action_candidate(
                        "ACT-DELIVERY-001",
                        "Planner / ERP Owner",
                        "Close ERP exception and confirm material ETA before APS resequencing.",
                        ["ERP exception reason", "material ETA", "planner confirmation"],
                    ),
                }
            )

        labor_candidates = sorted(
            [item for item in labor if item.get("risk") != "low" or item.get("efficiency", 1) < 0.85],
            key=lambda item: (float(item.get("efficiency", 1)), -int(item.get("manual_interventions", 0))),
        )
        if labor_candidates:
            labor_item = labor_candidates[0]
            service_refs = [item.get("evidence_ref") for item in service_escalations]
            evidence_refs = self._unique_refs([labor_item.get("evidence_ref"), *service_refs[:2]])
            priorities.append(
                {
                    "priority_id": "MGMT-PRIO-LABOR-001",
                    "rank": 0,
                    "priority": "P1" if float(labor_item.get("efficiency", 1)) < 0.8 else "P2",
                    "score": 84 if float(labor_item.get("efficiency", 1)) < 0.8 else 74,
                    "management_theme": "labor",
                    "theme_label": "浜哄伐鏈夋晥宸ユ椂",
                    "title": f"Confirm {labor_item.get('team_id')} effective-hour loss before it hides delivery risk",
                    "title_zh": f"纭 {labor_item.get('team_id')} 鐨勬湁鏁堝伐鏃舵崯澶憋紝閬垮厤浜や粯椋庨櫓琚帺鐩?",
                    "management_question": "Is low effective labor time caused by repeated machine intervention, waiting, rework, or unclear ownership?",
                    "conclusion": (
                        f"{labor_item.get('team_id')} efficiency is {labor_item.get('efficiency', 0):.0%} with "
                        f"{labor_item.get('manual_interventions', 0)} manual interventions."
                    ),
                    "conclusion_zh": (
                        f"{labor_item.get('team_id')} 有效工时效率为 {labor_item.get('efficiency', 0):.0%}，"
                        f"人工干预 {labor_item.get('manual_interventions', 0)} 次。"
                    ),
                    "reason": "Low effective hours can hide waiting, repeated mechanic intervention, rework, or unclear handoff before they become visible delivery misses.",
                    "reason_zh": "有效工时偏低会把等待、反复机修干预、返工或交接不清隐藏起来，直到它们变成交付问题。",
                    "risk_if_ignored": "The same people may stay busy while useful output stays low, creating missed delivery recovery windows and hidden labor cost.",
                    "risk_if_ignored_zh": "如果不处理，现场可能看起来很忙但有效产出偏低，错过交付恢复窗口并形成隐性人工成本。",
                    "recommended_action": "Ask the team leader and maintenance owner to confirm whether interventions are service, setup, waiting, or rework before the next shift review.",
                    "recommended_action_zh": "下次班次复盘前，请班组长和设备负责人确认人工干预来自服务、调机、等待还是返工。",
                    "owner_role": "Team Leader / Maintenance Owner",
                    "confirmation_needed_by": "next_shift_review",
                    "decision_gate": "team_leader_confirms_effective_hour_cause",
                    "affected_objects": {
                        "teams": [labor_item.get("team_id")],
                        "roles": [labor_item.get("role")],
                        "machines": [item.get("machine_id") for item in service_escalations if item.get("machine_id")],
                        "orders": [item.get("order_id") for item in service_escalations if item.get("order_id")],
                    },
                    "kpi_links": ["labor_efficiency", "downtime_minutes", "service_escalation_count"],
                    "evidence_refs": evidence_refs,
                    "evidence_claims": self._evidence_claims(evidence_by_id, evidence_refs),
                    "data_gaps": [
                        "Need historical effective-hour baseline, team assignment history, and confirmed intervention reasons to separate normal support from waste.",
                    ],
                    "action_candidate": self._priority_action_candidate(
                        "ACT-LABOR-001",
                        "Team Leader / Maintenance Owner",
                        "Confirm whether repeated manual interventions are service, setup, waiting, or rework.",
                        ["shift labor record", "manual intervention reason", "team leader confirmation"],
                    ),
                }
            )

        machine_candidates = sorted(
            [item for item in machines if item.get("state") in {"stopped", "idle"} or item.get("downtime_minutes", 0) >= 60],
            key=lambda item: (int(item.get("downtime_minutes", 0)), 1 if item.get("state") == "stopped" else 0),
            reverse=True,
        )
        if len(priorities) < 3 and machine_candidates:
            machine = machine_candidates[0]
            evidence_refs = self._unique_refs([machine.get("evidence_ref"), *[item.get("evidence_ref") for item in service_escalations if item.get("machine_id") == machine.get("machine_id")]])
            priorities.append(
                {
                    "priority_id": "MGMT-PRIO-CAPACITY-001",
                    "rank": 0,
                    "priority": "P1" if machine.get("state") == "stopped" else "P2",
                    "score": 82 if machine.get("state") == "stopped" else 72,
                    "management_theme": "cost",
                    "theme_label": "鎴愭湰/浜ц兘",
                    "title": f"Recover {machine.get('machine_id')} capacity leakage",
                    "title_zh": f"鎭㈠ {machine.get('machine_id')} 鐨勪骇鑳芥崯澶?",
                    "management_question": "Which machine capacity loss is turning into avoidable labor or waiting cost?",
                    "conclusion": (
                        f"{machine.get('machine_id')} is {machine.get('state')} with "
                        f"{machine.get('downtime_minutes', 0)} downtime minutes and OEE {machine.get('oee', 0):.0%}."
                    ),
                    "conclusion_zh": (
                        f"{machine.get('machine_id')} 当前状态为 {machine.get('state')}，"
                        f"停机 {machine.get('downtime_minutes', 0)} 分钟，OEE {machine.get('oee', 0):.0%}。"
                    ),
                    "reason": "Idle or stopped machine time creates hidden cost even before it shows up as a delivery miss.",
                    "reason_zh": "机台空闲或停机在形成交期问题之前，就已经产生隐性成本。",
                    "risk_if_ignored": "Lost machine hours, repeated mechanic intervention, lower labor efficiency, and delayed recovery.",
                    "risk_if_ignored_zh": "如果不处理，可能损失机台工时、增加维修反复干预、降低人工效率并延长恢复时间。",
                    "recommended_action": "Confirm whether the machine is waiting for work order, material, setup, or service review; do not auto-dispatch.",
                    "recommended_action_zh": "确认机台是在等工单、等物料、等调机还是需要服务复核；不要自动派工。",
                    "owner_role": "Production Supervisor / Service Manager",
                    "confirmation_needed_by": "current_shift_review",
                    "decision_gate": "machine_recovery_owner_assigned",
                    "affected_objects": {
                        "orders": [machine.get("order_id")] if machine.get("order_id") else [],
                        "machines": [machine.get("machine_id")],
                        "service_candidates": [item.get("candidate_id") for item in service_escalations if item.get("machine_id") == machine.get("machine_id")],
                    },
                    "kpi_links": ["oee", "downtime_minutes", "labor_efficiency", "waste_cost_opportunity"],
                    "evidence_refs": evidence_refs,
                    "evidence_claims": self._evidence_claims(evidence_by_id, evidence_refs),
                    "data_gaps": [
                        "Need longer IOT history, planned downtime, and maintenance closure records to separate planned idle from avoidable loss.",
                    ],
                    "action_candidate": self._priority_action_candidate(
                        "ACT-CAPACITY-001",
                        "Production Supervisor / Service Manager",
                        "Assign a recovery owner and confirm whether the issue is planning, material, setup, or service.",
                        ["IOT alarm duration", "service candidate review", "shift owner confirmation"],
                    ),
                }
            )

        if len(priorities) < 3 and optimization_signals:
            for index, signal in enumerate(optimization_signals[: 3 - len(priorities)]):
                priorities.append(
                    {
                        "priority_id": f"MGMT-PRIO-SIGNAL-{index + 1:03d}",
                        "rank": 0,
                        "priority": "P2",
                        "score": 60 - index,
                        "management_theme": signal.get("type", "operations"),
                        "theme_label": "杩愯惀淇″彿",
                        "title": signal.get("title", ""),
                        "title_zh": signal.get("title", ""),
                        "management_question": "Does this evidence signal need an owner before the next shift?",
                        "conclusion": signal.get("title", ""),
                        "reason": signal.get("waste_or_cost_point", ""),
                        "risk_if_ignored": "The same waste signal may recur without owner confirmation.",
                        "recommended_action": signal.get("suggested_action", ""),
                        "owner_role": "Production Owner",
                        "confirmation_needed_by": "next_shift_review",
                        "decision_gate": "owner_confirms_or_closes_signal",
                        "affected_objects": {},
                        "kpi_links": ["waste_cost_opportunity"],
                        "evidence_refs": self._unique_refs([signal.get("evidence_ref")]),
                        "evidence_claims": self._evidence_claims(evidence_by_id, self._unique_refs([signal.get("evidence_ref")])),
                        "data_gaps": ["Need owner confirmation to turn this signal into a closed-loop action."],
                        "action_candidate": self._priority_action_candidate(
                            f"ACT-SIGNAL-{index + 1:03d}",
                            "Production Owner",
                            signal.get("suggested_action", ""),
                            ["owner confirmation"],
                        ),
                    }
                )

        theme_order = {"delivery": 0, "equipment": 1, "material": 2, "cost": 3, "quality": 4, "labor": 5}
        sorted_priorities = sorted(
            priorities,
            key=lambda item: (theme_order.get(item.get("management_theme", ""), 9), -int(item.get("score", 0)), item["priority_id"]),
        )
        priorities = []
        seen_themes = set()
        for item in sorted_priorities:
            theme = item.get("risk_theme") or item.get("management_theme") or item.get("priority_id")
            if theme in seen_themes:
                continue
            priorities.append(item)
            seen_themes.add(theme)
            if len(priorities) == 3:
                break
        if len(priorities) < 3:
            for item in sorted_priorities:
                if item in priorities:
                    continue
                priorities.append(item)
                if len(priorities) == 3:
                    break
        for index, item in enumerate(priorities, start=1):
            item["rank"] = index
            item["risk_level"] = self._priority_risk_level(item)
            item["risk_level_label"] = self._priority_risk_level_label(item["risk_level"])
            self._ensure_priority_card_contract(item)

        data_gaps = [
            {
                "gap_id": "MGMT-GAP-ORDER-HISTORY",
                "needed_for": ["delivery", "cost"],
                "gap": "Missing order-created dates, actual delivery dates, shipment mode, and downstream stage timestamps.",
                "current_workaround": "Use due_date, APS status, material risk, and mock remaining quantity as directional evidence.",
            },
            {
                "gap_id": "MGMT-GAP-IOT-JOIN",
                "needed_for": ["machine", "quality", "cost"],
                "gap": "Real Tianpai IOT exports currently lack reliable order_id, and not all machines are connected.",
                "current_workaround": "Keep IOT-like mock machine evidence separate unless order_id is present.",
            },
            {
                "gap_id": "MGMT-GAP-COST",
                "needed_for": ["cost"],
                "gap": "Customer purchasing, labor, rework, and freight cost tables are unavailable.",
                "current_workaround": "Use quality, downtime, material, and delivery-risk proxies instead of claiming exact cost.",
            },
            {
                "gap_id": "MGMT-GAP-LABOR-BASELINE",
                "needed_for": ["labor", "cost", "delivery"],
                "gap": "Historical effective-hour baseline, team assignment history, and confirmed intervention reasons are unavailable.",
                "current_workaround": "Use current shift efficiency and manual intervention count as directional evidence only.",
            },
        ]

        return {
            "brief_id": f"MGMT-BRIEF-{PRODUCTION_VERSION}-CURRENT",
            "version": PRODUCTION_VERSION,
            "persona": "tianpai_general_manager",
            "audience": "General Manager / Production leadership",
            "snapshot_time": data.get("factory", {}).get("snapshot_time", ""),
            "automation_status": "actual_export_first_priority_engine" if actual_priorities else "deterministic_mock_priority_engine",
            "data_source_policy": {
                "priority_order": ["Tianpai APS/ERP export", "mock production snapshot"],
                "actual_export_priority_count": len([item for item in priorities if item.get("data_source_mode") == "actual_aps_erp_export_first"]),
                "mock_fallback_priority_count": len([item for item in priorities if item.get("data_source_mode") != "actual_aps_erp_export_first"]),
                "read_only": True,
            },
            "priority_policy": {
                "kpi_priority": ["delivery", "quality", "cost"],
                "card_themes": ["delivery_risk_order", "equipment_or_spec_risk", "material_or_quantity_control_risk"],
                "principle": "Delivery risk is reviewed first, quality risk second, and cost is treated as the consequence of delivery and quality failures.",
                "read_only": True,
                "human_confirmation_required_before_action": True,
            },
            "daily_brief": {
                "headline": self._management_headline(priorities),
                "top_three": [item["title"] for item in priorities],
                "summary": [
                    f"Actual APS/ERP export: {len([item for item in priorities if item.get('data_source_mode') == 'actual_aps_erp_export_first'])} of today's top-three cards are backed by external export evidence chains.",
                    f"Delivery: review the top order-risk card first, then confirm whether unscheduled quantities or low plan completion need owner action today.",
                    f"Equipment/material/cost: review spec mismatch, unscheduled part orders, or plan/report gaps before changing schedules or machine assignments.",
                    "Data boundary: Athena remains read-only; final action still requires owner confirmation and downstream ERP/APS/IOT evidence.",
                ],
                "summary_zh": [
                    f"真实 APS/ERP 导出：今天前三张风险卡中有 {len([item for item in priorities if item.get('data_source_mode') == 'actual_aps_erp_export_first'])} 张带外部导出证据链。",
                    "交付：先看最高订单风险，再确认未排数量或计划完成率是否需要今天处理。",
                    "设备/物料/成本：改排程或调机前，先复核规格不匹配、未排满部件单、计划/报工差异。",
                    "数据边界：Athena 保持只读；最终行动仍需要负责人确认和后续 ERP/APS/IOT 证据。",
                ],
            },
            "shift_brief": {
                "review_cadence": "daily_and_shift_review",
                "next_review": "current_shift_review",
                "owner_confirmation_required": True,
                "recommended_sequence": [item["action_candidate"]["action_id"] for item in priorities],
            },
            "top_priorities": priorities,
            "data_gaps": data_gaps,
            "future_handoff_contract": {
                "next_engine": "decision_loop_follow_up_engine",
                "handoff_objects": ["decision", "action", "follow_up", "memory_event"],
                "status": "contract_ready_not_yet_closed_loop",
            },
            "kpi_snapshot": {
                "order_count": overview.get("order_count", 0),
                "scrap_rate": overview.get("scrap_rate", 0),
                "average_oee": overview.get("average_oee", 0),
                "downtime_minutes": overview.get("downtime_minutes", 0),
                "material_risk_count": overview.get("material_risk_count", 0),
                "service_escalation_count": overview.get("service_escalation_count", 0),
                "estimated_good_quantity": garment_output.get("estimated_good_quantity", 0),
                "resource_status": {key: value.get("status") for key, value in resource_lens.items()},
            },
        }

    def _decision_loop_follow_up(self, management_priority_brief: dict) -> dict:
        store = self._load_follow_up_store()
        latest_by_action = self._latest_follow_up_reviews_by_action(store)
        decisions = []
        actions = []
        follow_ups = []
        memory_events = []

        for priority in management_priority_brief.get("top_priorities", []):
            action = priority.get("action_candidate", {})
            action_id = action.get("action_id") or f"ACT-{priority.get('priority_id', 'UNKNOWN')}"
            follow_up_id = f"FU-{action_id.removeprefix('ACT-')}"
            decision_id = f"DEC-{priority.get('priority_id', 'UNKNOWN').removeprefix('MGMT-PRIO-')}"
            review = latest_by_action.get(action_id, {})
            status = review.get("review_status") or "pending_confirmation"
            evidence_status = self._follow_up_evidence_status(status, review)
            owner_role = review.get("owner_role") or action.get("owner_role") or priority.get("owner_role", "")
            expected_evidence = action.get("expected_evidence", [])

            decisions.append(
                {
                    "decision_id": decision_id,
                    "priority_id": priority.get("priority_id"),
                    "rank": priority.get("rank"),
                    "priority": priority.get("priority"),
                    "risk_level": priority.get("risk_level"),
                    "management_theme": priority.get("management_theme"),
                    "conclusion": priority.get("conclusion"),
                    "conclusion_zh": priority.get("conclusion_zh"),
                    "reason": priority.get("reason"),
                    "risk_if_ignored": priority.get("risk_if_ignored"),
                    "evidence_refs": priority.get("evidence_refs", []),
                    "actual_evidence_chains": priority.get("actual_evidence_chains", []),
                    "field_sources": priority.get("field_sources", []),
                    "skills_used": priority.get("skills_used", []),
                    "skill_execution_trace": priority.get("skill_execution_trace", []),
                    "data_source_mode": priority.get("data_source_mode", ""),
                    "data_gaps": priority.get("data_gaps", []),
                    "drilldown_question": priority.get("drilldown_question", ""),
                    "decision_gate": priority.get("decision_gate"),
                    "status": self._decision_status_from_follow_up(status),
                }
            )
            actions.append(
                {
                    "action_id": action_id,
                    "decision_id": decision_id,
                    "priority_id": priority.get("priority_id"),
                    "source_card_type": "hard_risk",
                    "related_object": self._related_object_from_priority(priority),
                    "owner_role": owner_role,
                    "recommended_action": action.get("recommended_action") or priority.get("recommended_action"),
                    "recommended_action_zh": priority.get("recommended_action_zh"),
                    "confirmation_need": priority.get("decision_gate") or action.get("recommended_action") or priority.get("recommended_action"),
                    "athena_recommendation_reason": priority.get("reason") or priority.get("conclusion"),
                    "requires_human_confirmation": True,
                    "status": status,
                    "review_status": review.get("review_status", "not_reviewed"),
                    "review_note": review.get("review_note", ""),
                    "evidence_note": review.get("evidence_note", ""),
                    "reviewed_at": review.get("reviewed_at", ""),
                    "expected_evidence": expected_evidence,
                    "blocked_automation": action.get("blocked_automation", []),
                    "write_scope": action.get("write_scope", "local_metadata_only"),
                    "drilldown_question": action.get("drilldown_question", priority.get("drilldown_question", "")),
                    "field_sources": action.get("field_sources", priority.get("field_sources", [])),
                    "skills_used": priority.get("skills_used", []),
                    "skill_execution_trace": priority.get("skill_execution_trace", []),
                    "linked_evidence_chain": action.get("linked_evidence_chain", (priority.get("actual_evidence_chains") or [{}])[0]),
                    "follow_up_contract": action.get("follow_up_contract", {}),
                    "read_only_boundary": {
                        "read_only": True,
                        "write_scope": "local_metadata_only",
                        "blocked_actions": ["write_aps", "write_erp", "write_iot", "create_real_service_ticket", "control_machine"],
                    },
                }
            )
            follow_ups.append(
                {
                    "follow_up_id": follow_up_id,
                    "action_id": action_id,
                    "decision_id": decision_id,
                    "source_card_type": "hard_risk",
                    "related_object": self._related_object_from_priority(priority),
                    "owner_role": owner_role,
                    "confirmation_need": priority.get("decision_gate") or action.get("recommended_action") or priority.get("recommended_action"),
                    "athena_recommendation_reason": priority.get("reason") or priority.get("conclusion"),
                    "status": status,
                    "review_time": priority.get("confirmation_needed_by", "next_shift_review"),
                    "expected_evidence": expected_evidence,
                    "evidence_status": evidence_status,
                    "closure_gate": priority.get("decision_gate"),
                    "recurrence_watch": {
                        "enabled": True,
                        "watch_kpis": priority.get("kpi_links", []),
                        "reopen_condition": "same priority theme returns as P0/P1 in the next review cycle after closure",
                    },
                    "source_priority_id": priority.get("priority_id"),
                    "linked_risk_card_id": priority.get("priority_id"),
                    "linked_risk_level": priority.get("risk_level"),
                    "linked_risk_theme": priority.get("risk_theme"),
                    "evidence_refs": priority.get("evidence_refs", []),
                    "actual_evidence_chains": priority.get("actual_evidence_chains", []),
                    "field_sources": priority.get("field_sources", []),
                    "skills_used": priority.get("skills_used", []),
                    "skill_execution_trace": priority.get("skill_execution_trace", []),
                    "drilldown_question": priority.get("drilldown_question", ""),
                    "data_source_mode": priority.get("data_source_mode", ""),
                    "internal_demo_ready": priority.get("internal_demo_ready", False),
                    "write_scope": "local_metadata_only",
                    "writes_real_system": False,
                    "human_owner_required": True,
                    "read_only_boundary": {
                        "read_only": True,
                        "write_scope": "local_metadata_only",
                        "blocked_actions": ["write_aps", "write_erp", "write_iot", "create_real_service_ticket", "control_machine"],
                    },
                }
            )
            memory_events.append(
                {
                    "memory_event_id": f"MEM-{follow_up_id}",
                    "event_type": "production_follow_up_candidate",
                    "scope": "tenant",
                    "tenant_id": "tianpai",
                    "factory_id": None,
                    "source": "demo",
                    "retention_policy": "review_before_promotion",
                    "sensitivity_level": "internal",
                    "promotion_status": "reviewed" if status == "closed" else "candidate",
                    "linked_decision_id": decision_id,
                    "linked_action_id": action_id,
                    "linked_follow_up_id": follow_up_id,
                    "summary": priority.get("title"),
                    "evidence_refs": priority.get("evidence_refs", []),
                    "blocked_until": "human_review_and_result_evidence",
                }
            )

        status_counts = self._count_by([item["status"] for item in follow_ups])
        loop_status = "ready_for_review"
        if status_counts.get("closed") == len(follow_ups) and follow_ups:
            loop_status = "closed_ready_for_memory_review"
        elif status_counts.get("unable_to_process"):
            loop_status = "unable_to_process_review"
        elif status_counts.get("waiting_evidence"):
            loop_status = "waiting_evidence"
        elif status_counts.get("assigned") or status_counts.get("confirmed"):
            loop_status = "in_progress"

        return {
            "schema_id": "athena.production_decision_loop.v1",
            "version": PRODUCTION_VERSION,
            "loop_id": f"PROD-DECISION-LOOP-{PRODUCTION_VERSION}-CURRENT",
            "source_brief_id": management_priority_brief.get("brief_id", ""),
            "status": loop_status,
            "read_only": True,
            "write_actions_blocked": True,
            "lifecycle": [
                "pending_confirmation",
                "confirmed",
                "needs_more_data",
                "resolved",
                "dismissed",
                "assigned",
                "waiting_evidence",
                "closed",
                "unable_to_process",
            ],
            "closed_loop_contract": [
                "management_priority",
                "decision",
                "action",
                "follow_up",
                "owner_confirmation",
                "evidence_check",
                "memory_event_candidate",
            ],
            "decision_items": decisions,
            "action_items": actions,
            "follow_up_items": follow_ups,
            "memory_event_candidates": memory_events,
            "review_state": {
                "version": store.get("version", PRODUCTION_VERSION),
                "review_count": len(store.get("reviews", [])),
                "latest_reviewed_at": store.get("latest_reviewed_at", ""),
                "metadata_only": True,
                "raw_files_stored": False,
                "credentials_stored": False,
            },
            "loop_kpis": {
                "decision_count": len(decisions),
                "action_count": len(actions),
                "follow_up_count": len(follow_ups),
                "open_follow_up_count": len([item for item in follow_ups if item["status"] not in {"closed", "unable_to_process"}]),
                "closed_follow_up_count": status_counts.get("closed", 0),
                "assigned_count": status_counts.get("assigned", 0),
                "waiting_evidence_count": status_counts.get("waiting_evidence", 0),
                "pending_confirmation_count": status_counts.get("pending_confirmation", 0),
                "confirmed_count": status_counts.get("confirmed", 0),
                "unable_to_process_count": status_counts.get("unable_to_process", 0),
                "memory_candidate_count": len(memory_events),
                "reviewed_memory_candidate_count": len([item for item in memory_events if item["promotion_status"] == "reviewed"]),
            },
            "blocked_actions": [
                "auto_assign_owner_without_confirmation",
                "auto_close_follow_up_without_evidence",
                "write_to_aps_or_iot",
                "create_real_service_ticket",
                "promote_memory_without_review",
            ],
            "next_actions": self._decision_loop_next_actions(status_counts, follow_ups),
        }

    def _first_screen_service_risk(
        self,
        service_escalations: list[dict],
        decision_loop: dict,
        evidence_log: list[dict],
    ) -> dict:
        action_items = decision_loop.get("action_items", [])
        evidence_by_ref = {
            item.get("evidence_ref"): item
            for item in evidence_log
            if item.get("evidence_ref")
        }
        fallback_action = next(
            (
                item
                for item in action_items
                if item.get("priority_id", "").lower().find("equipment") >= 0
                or item.get("priority_id", "").lower().find("delivery") >= 0
            ),
            action_items[0] if action_items else {},
        )
        cards = []

        for index, candidate in enumerate(service_escalations, start=1):
            evidence_ref = candidate.get("evidence_ref", "")
            evidence = evidence_by_ref.get(evidence_ref, {})
            order_id = candidate.get("order_id", "")
            machine_id = candidate.get("machine_id", "")
            priority = candidate.get("priority", "P1")
            linked_action = {"action_id": f"ACT-SVC-RISK-{index:03d}"}
            risk_level = "red" if priority in {"P0", "P1"} else "yellow"
            cards.append(
                {
                    "card_id": f"SVC-RISK-{index:03d}",
                    "candidate_id": candidate.get("candidate_id", ""),
                    "risk_theme": "service",
                    "risk_theme_label": "Service / 设备",
                    "title": f"Confirm whether {machine_id} is blocking production",
                    "title_zh": f"确认 {machine_id} 是否正在影响订单交付",
                    "risk_level": risk_level,
                    "risk_level_label": "High risk" if risk_level == "red" else "Attention",
                    "priority": priority,
                    "machine_id": machine_id,
                    "order_id": order_id,
                    "issue": candidate.get("issue", ""),
                    "service_request_candidate": candidate.get("service_request_candidate", True),
                    "auto_dispatch": False,
                    "read_only": True,
                    "why_it_matters": (
                        "A service candidate can turn a production delay into a repeated bottleneck if no owner "
                        "confirms machine status, alarm history, and recovery plan."
                    ),
                    "why_it_matters_zh": (
                        "如果没有负责人确认机台状态、报警历史和恢复计划，Service 候选问题可能把单次生产延误变成反复瓶颈。"
                    ),
                    "suggested_owner": "Service Manager / Maintenance Owner",
                    "recommended_action": (
                        "Ask maintenance to confirm whether the machine alarm is still active, whether the order is affected, "
                        "and whether a real service ticket is required."
                    ),
                    "recommended_action_zh": (
                        "请机修或 Service 负责人确认报警是否仍在、是否影响该订单，以及是否需要创建真实 Service 工单。"
                    ),
                    "evidence_refs": [ref for ref in [evidence_ref] if ref],
                    "evidence_claims": [
                        {
                            "evidence_ref": evidence_ref,
                            "claim": candidate.get("reason", "Service candidate generated from production signal."),
                            "source": evidence.get("source", "production_service_escalation_candidate"),
                        }
                    ],
                    "field_sources": [
                        "machines.machine_id",
                        "machines.state",
                        "machines.alarm",
                        "machines.order_id",
                        "service_escalations.candidate_id",
                    ],
                    "affected_objects": {
                        "orders": [order_id] if order_id else [],
                        "machines": [machine_id] if machine_id else [],
                        "service_candidates": [candidate.get("candidate_id", "")] if candidate.get("candidate_id") else [],
                    },
                    "data_gaps": [
                        "Need real IOT alarm duration and recovery timestamp before confirming service root cause.",
                        "Need maintenance owner confirmation before creating a real service ticket.",
                        "Need ERP/APS order impact confirmation before changing production priority.",
                    ],
                    "drilldown_question": (
                        f"为什么 {machine_id} 的 Service 风险可能影响订单 {order_id}？请按机台状态、报警、订单影响和证据链下钻。"
                    ),
                    "linked_action_id": linked_action.get("action_id", ""),
                    "local_follow_up_supported": bool(linked_action.get("action_id")),
                    "blocked_actions": [
                        "dispatch_service_automatically",
                        "create_real_service_ticket",
                        "control_machine",
                        "modify_schedule_automatically",
                    ],
                    "internal_demo_ready": True,
                    "demo_note": "Can be shown as a service-risk candidate and local follow-up example; not a real dispatch.",
                }
            )

        return {
            "schema_id": "athena.production_first_screen_service_risk.v1",
            "version": PRODUCTION_VERSION,
            "title": "First-screen Service risk",
            "title_zh": "总经理首屏 Service 风险",
            "summary": "Service risks are shown as confirmation candidates beside the top-three production priorities.",
            "summary_zh": "Service 风险作为待确认候选项，与总经理前三件事放在同一条生产决策链路里。",
            "adapter_status": "mock_contract",
            "read_only": True,
            "write_scope": "local_metadata_only",
            "service_risk_cards": cards,
            "service_candidate_count": len(cards),
            "blocked_actions": [
                "dispatch_service_automatically",
                "create_real_service_ticket",
                "control_machine",
                "modify_schedule_automatically",
            ],
        }

    def _extend_decision_loop_with_review_and_service(
        self,
        decision_loop: dict,
        evidence_review_queue: dict,
        first_screen_service_risk: dict,
    ) -> dict:
        store = self._load_follow_up_store()
        latest_by_action = self._latest_follow_up_reviews_by_action(store)
        loop = {
            **decision_loop,
            "decision_items": list(decision_loop.get("decision_items", [])),
            "action_items": list(decision_loop.get("action_items", [])),
            "follow_up_items": list(decision_loop.get("follow_up_items", [])),
            "memory_event_candidates": list(decision_loop.get("memory_event_candidates", [])),
        }

        for index, card in enumerate((evidence_review_queue.get("review_queue") or [])[:4], start=1):
            object_id = str(card.get("object_id") or card.get("produce_order_code") or f"{index:03d}")
            suffix = self._safe_id(object_id)
            action_id = f"ACT-EVID-REVIEW-{suffix}"
            decision_id = f"DEC-EVID-REVIEW-{suffix}"
            follow_up_id = f"FU-EVID-REVIEW-{suffix}"
            review = latest_by_action.get(action_id, {})
            status = review.get("review_status") or "pending_confirmation"
            owner = review.get("owner_role") or card.get("suggested_confirmation_owner") or "Planning Manager / APS Owner"
            confirmation_need = card.get("suggested_confirmation_action") or card.get("cannot_conclude_reason") or "Confirm planning and quantity evidence before Athena treats this as delivery risk."
            reason = card.get("why_not_delivery_risk") or "Evidence is inconsistent and needs reconciliation."
            self._append_decision_loop_item(
                loop,
                source_card_type="evidence_review",
                action_id=action_id,
                decision_id=decision_id,
                follow_up_id=follow_up_id,
                related_object=object_id,
                owner_role=owner,
                status=status,
                title=f"Evidence review for order {object_id}",
                title_zh=f"订单 {object_id} 数据复核",
                confirmation_need=confirmation_need,
                recommendation=card.get("suggested_confirmation_action") or confirmation_need,
                recommendation_zh=card.get("suggested_confirmation_action") or confirmation_need,
                reason=reason,
                evidence_refs=card.get("evidence_refs", []),
                field_sources=card.get("field_sources", []),
                expected_evidence=[
                    "Order close/cancel/current status confirmation",
                    "APS unscheduled quantity explanation",
                    "Manual report quantity scope confirmation",
                ],
                drilldown_question=card.get("drilldown_question", ""),
                review=review,
            )

        for index, card in enumerate(first_screen_service_risk.get("service_risk_cards") or [], start=1):
            object_id = card.get("machine_id") or card.get("candidate_id") or f"{index:03d}"
            suffix = self._safe_id(str(card.get("card_id") or object_id))
            action_id = card.get("linked_action_id") or f"ACT-SVC-RISK-{suffix}"
            decision_id = f"DEC-SVC-RISK-{suffix}"
            follow_up_id = f"FU-SVC-RISK-{suffix}"
            review = latest_by_action.get(action_id, {})
            status = review.get("review_status") or "pending_confirmation"
            owner = review.get("owner_role") or card.get("suggested_owner") or "Service Manager / Maintenance Owner"
            confirmation_need = card.get("recommended_action") or "Confirm machine alarm status, order impact, and whether a real service ticket is required."
            reason = card.get("why_it_matters") or "Service risk may affect production if no owner confirms machine recovery."
            self._append_decision_loop_item(
                loop,
                source_card_type="service_risk",
                action_id=action_id,
                decision_id=decision_id,
                follow_up_id=follow_up_id,
                related_object=str(object_id),
                owner_role=owner,
                status=status,
                title=card.get("title") or f"Service risk for {object_id}",
                title_zh=card.get("title_zh") or f"{object_id} Service 椋庨櫓纭",
                confirmation_need=confirmation_need,
                recommendation=card.get("recommended_action") or confirmation_need,
                recommendation_zh=card.get("recommended_action_zh") or confirmation_need,
                reason=reason,
                evidence_refs=card.get("evidence_refs", []),
                field_sources=card.get("field_sources", []),
                expected_evidence=[
                    "Machine alarm active/cleared status",
                    "Recovery timestamp or maintenance owner note",
                    "Order impact confirmation",
                ],
                drilldown_question=card.get("drilldown_question", ""),
                review=review,
            )

        status_counts = self._count_by([item["status"] for item in loop["follow_up_items"]])
        loop["loop_kpis"].update(
            {
                "decision_count": len(loop["decision_items"]),
                "action_count": len(loop["action_items"]),
                "follow_up_count": len(loop["follow_up_items"]),
                "open_follow_up_count": len([item for item in loop["follow_up_items"] if item["status"] not in {"closed", "unable_to_process", "resolved", "dismissed"}]),
                "closed_follow_up_count": status_counts.get("closed", 0) + status_counts.get("resolved", 0),
                "pending_confirmation_count": status_counts.get("pending_confirmation", 0),
                "confirmed_count": status_counts.get("confirmed", 0),
                "needs_more_data_count": status_counts.get("needs_more_data", 0),
                "dismissed_count": status_counts.get("dismissed", 0),
            }
        )
        loop["next_actions"] = self._decision_loop_next_actions(status_counts, loop["follow_up_items"])
        return loop

    def _append_decision_loop_item(
        self,
        loop: dict,
        source_card_type: str,
        action_id: str,
        decision_id: str,
        follow_up_id: str,
        related_object: str,
        owner_role: str,
        status: str,
        title: str,
        title_zh: str,
        confirmation_need: str,
        recommendation: str,
        recommendation_zh: str,
        reason: str,
        evidence_refs: list[str],
        field_sources: list[str],
        expected_evidence: list[str],
        drilldown_question: str,
        review: dict,
    ) -> None:
        read_only_boundary = {
            "read_only": True,
            "write_scope": "local_metadata_only",
            "blocked_actions": ["write_aps", "write_erp", "write_iot", "create_real_service_ticket", "control_machine"],
        }
        evidence_status = self._follow_up_evidence_status(status, review)
        loop["decision_items"].append(
            {
                "decision_id": decision_id,
                "priority_id": decision_id,
                "source_card_type": source_card_type,
                "related_object": related_object,
                "priority": "P1" if source_card_type == "service_risk" else "P2",
                "risk_level": "yellow",
                "management_theme": source_card_type,
                "conclusion": title,
                "conclusion_zh": title_zh,
                "reason": reason,
                "evidence_refs": evidence_refs,
                "field_sources": field_sources,
                "data_source_mode": "actual_aps_erp_export_first" if source_card_type == "evidence_review" else "mock_contract",
                "drilldown_question": drilldown_question,
                "decision_gate": confirmation_need,
                "status": self._decision_status_from_follow_up(status),
            }
        )
        loop["action_items"].append(
            {
                "action_id": action_id,
                "decision_id": decision_id,
                "priority_id": decision_id,
                "source_card_type": source_card_type,
                "related_object": related_object,
                "owner_role": owner_role,
                "recommended_action": recommendation,
                "recommended_action_zh": recommendation_zh,
                "confirmation_need": confirmation_need,
                "athena_recommendation_reason": reason,
                "requires_human_confirmation": True,
                "status": status,
                "review_status": review.get("review_status", "not_reviewed"),
                "review_note": review.get("review_note", ""),
                "evidence_note": review.get("evidence_note", ""),
                "reviewed_at": review.get("reviewed_at", ""),
                "expected_evidence": expected_evidence,
                "blocked_automation": read_only_boundary["blocked_actions"],
                "write_scope": "local_metadata_only",
                "drilldown_question": drilldown_question,
                "field_sources": field_sources,
                "linked_evidence_chain": {},
                "follow_up_contract": {
                    "mode": "local_metadata_only",
                    "writes_real_system": False,
                    "blocked_systems": ["APS", "ERP", "IOT", "service_ticket", "machine_control"],
                },
                "read_only_boundary": read_only_boundary,
            }
        )
        loop["follow_up_items"].append(
            {
                "follow_up_id": follow_up_id,
                "action_id": action_id,
                "decision_id": decision_id,
                "source_card_type": source_card_type,
                "related_object": related_object,
                "owner_role": owner_role,
                "confirmation_need": confirmation_need,
                "athena_recommendation_reason": reason,
                "status": status,
                "review_time": "current_shift_review",
                "expected_evidence": expected_evidence,
                "evidence_status": evidence_status,
                "closure_gate": confirmation_need,
                "source_priority_id": decision_id,
                "linked_risk_card_id": decision_id,
                "linked_risk_level": "yellow",
                "linked_risk_theme": source_card_type,
                "evidence_refs": evidence_refs,
                "field_sources": field_sources,
                "drilldown_question": drilldown_question,
                "data_source_mode": "actual_aps_erp_export_first" if source_card_type == "evidence_review" else "mock_contract",
                "internal_demo_ready": True,
                "write_scope": "local_metadata_only",
                "writes_real_system": False,
                "human_owner_required": True,
                "read_only_boundary": read_only_boundary,
            }
        )
        loop["memory_event_candidates"].append(
            {
                "memory_event_id": f"MEM-{follow_up_id}",
                "event_type": f"production_{source_card_type}_follow_up_candidate",
                "scope": "tenant",
                "tenant_id": "tianpai",
                "factory_id": None,
                "source": "demo",
                "retention_policy": "review_before_promotion",
                "sensitivity_level": "internal",
                "promotion_status": "reviewed" if status in {"closed", "resolved"} else "candidate",
                "linked_decision_id": decision_id,
                "linked_action_id": action_id,
                "linked_follow_up_id": follow_up_id,
                "summary": title,
                "evidence_refs": evidence_refs,
                "blocked_until": "human_review_and_result_evidence",
            }
        )

    def _daily_brief_narrative(
        self,
        management_priority_brief: dict,
        evidence_review_queue: dict,
        first_screen_service_risk: dict,
        decision_loop: dict,
        permission_boundary: dict,
    ) -> dict:
        priorities = management_priority_brief.get("top_priorities", [])[:3]
        review_cards = (evidence_review_queue.get("review_queue") or [])[:4]
        service_cards = (first_screen_service_risk.get("service_risk_cards") or [])[:2]
        top_three = [
            {
                "rank": item.get("rank", index),
                "title": item.get("title_zh") or item.get("title") or item.get("priority_id"),
                "theme": item.get("management_theme", ""),
                "owner": item.get("owner_role", ""),
                "action": item.get("recommended_action_zh") or item.get("recommended_action") or "",
                "evidence_refs": item.get("evidence_refs", [])[:4],
            }
            for index, item in enumerate(priorities, start=1)
        ]
        do_not_conclude = [
            {
                "object": card.get("object_id") or card.get("produce_order_code"),
                "reason": card.get("cannot_conclude_reason") or card.get("why_not_delivery_risk"),
                "owner": card.get("suggested_confirmation_owner"),
                "action": card.get("suggested_confirmation_action"),
                "evidence_refs": card.get("evidence_refs", [])[:4],
            }
            for card in review_cards
        ]
        owners = []
        for item in top_three:
            if item["owner"]:
                owners.append({"owner": item["owner"], "confirm": item["action"], "source": "hard_risk"})
        for item in do_not_conclude[:3]:
            owners.append({"owner": item.get("owner", ""), "confirm": item.get("action", ""), "source": "evidence_review"})
        for card in service_cards:
            owners.append(
                {
                    "owner": card.get("suggested_owner", ""),
                    "confirm": card.get("recommended_action_zh") or card.get("recommended_action", ""),
                    "source": "service_risk",
                }
            )
        impact_lines = [
            "Delivery: handle hard-risk orders and scheduling gaps first.",
            "Quality / equipment: treat Service and machine anomalies as confirmation candidates until owner review.",
            "Cost: data conflicts, repeated downtime, replenishment, and air-freight risk may amplify cost, but real cost tables are not connected yet.",
        ]
        evidence_boundary = [
            "Athena currently uses local APS/ERP export evidence, mock IOT/Service evidence, and local follow-up metadata.",
            "Evidence review candidates are not confirmed risks until planning, APS owner, or reporting owner confirms them.",
            "Athena does not write APS/ERP/IOT, does not change scheduling, does not dispatch, and does not control machines.",
        ]
        text_lines = [
            "Daily brief: review the top three priorities first, then handle evidence review and Service confirmation.",
            *[f"{item['rank']}. {item['title']}; owner: {item['owner'] or 'pending owner'}." for item in top_three],
            f"Do not conclude yet: {len(review_cards)} evidence review candidates need order status, unscheduled quantity, and reporting-scope confirmation.",
            f"Service/equipment: {len(service_cards)} candidates need maintenance or Service owner confirmation before claiming delivery impact.",
            "Evidence boundary: Athena only performs read-only verification and recommendation; final action still requires owner confirmation.",
        ]
        return {
            "schema_id": "athena.production_daily_brief_narrative.v1",
            "version": PRODUCTION_VERSION,
            "title": "Daily Brief Narrative",
            "title_zh": "今日总经理早会摘要",
            "read_time": "3_minutes",
            "read_only": True,
            "raw_json_visible_to_user": False,
            "internal_schema_visible_to_user": False,
            "copy_supported": True,
            "summary_zh": "\n".join(text_lines),
            "top_three_priorities": top_three,
            "do_not_conclude_yet": do_not_conclude,
            "confirmation_owners": owners[:8],
            "impact_focus": impact_lines,
            "evidence_boundary": evidence_boundary,
            "follow_up_summary": {
                "source_card_types": sorted({item.get("source_card_type", "") for item in decision_loop.get("follow_up_items", []) if item.get("source_card_type")}),
                "follow_up_count": len(decision_loop.get("follow_up_items", [])),
                "metadata_only": True,
            },
            "permission_boundary": {
                "read_only": True,
                "blocked_actions": permission_boundary.get("blocked_actions", []),
            },
        }

    def _internal_demo_readiness_mode(
        self,
        management_priority_brief: dict,
        first_screen_service_risk: dict,
        mvp_success_check: dict,
        permission_boundary: dict,
        data_readiness: dict,
    ) -> dict:
        priority_count = len(management_priority_brief.get("top_priorities", []))
        service_count = first_screen_service_risk.get("service_candidate_count", 0)
        success_ready = bool(mvp_success_check.get("within_three_minutes_ready"))
        can_demo = priority_count == 3 and success_ready
        return {
            "schema_id": "athena.internal_demo_readiness_mode.v1",
            "version": PRODUCTION_VERSION,
            "mode_id": f"INTERNAL-DEMO-{PRODUCTION_VERSION}",
            "status": "ready_for_internal_demo" if can_demo else "needs_work_before_internal_demo",
            "audience": "Santoni internal team and selected customer preview",
            "audience_zh": "Santoni 内部团队和客户预览",
            "demo_positioning": "General Manager 3-minute production decision workflow",
            "demo_positioning_zh": "总经理三分钟生产决策工作流",
            "can_demo": [
                "Select General Manager on the user page and see today's top three production priorities.",
                "Click a risk card to ask Athena for evidence-based root-cause drilldown.",
                "Generate local follow-up candidates without writing APS, ERP, IOT, or Service systems.",
                "Show Service risk as a confirmation candidate, not an automatic dispatch.",
                "Explain data gaps and evidence level before claiming conclusions.",
            ],
            "cannot_demo_yet": [
                "Live ERP/APS/IOT database integration.",
                "Automatic schedule change, machine control, .co/.cx upload, or service dispatch.",
                "Customer-verified general-manager VOC coverage.",
                "Full downstream garment quality and warehouse flow based on real records.",
            ],
            "demo_script": [
                {
                    "step": 1,
                    "title": "Choose General Manager",
                    "expected_visible_result": "Athena shows the top-three priorities and read-only boundary.",
                },
                {
                    "step": 2,
                    "title": "Open evidence detail",
                    "expected_visible_result": "Each card explains evidence refs, field sources, and data gaps.",
                },
                {
                    "step": 3,
                    "title": "Drill down with Santoni Athena",
                    "expected_visible_result": "The original chat keeps the conversation and returns root-cause analysis.",
                },
                {
                    "step": 4,
                    "title": "Create local follow-up",
                    "expected_visible_result": "A local metadata-only follow-up appears and can be reviewed.",
                },
            ],
            "demo_kpis": {
                "top_priority_count": priority_count,
                "service_risk_candidate_count": service_count,
                "success_readiness_score": mvp_success_check.get("readiness_score", 0),
                "data_readiness_status": data_readiness.get("status", "unknown"),
            },
            "visible_pages": ["/", "/production.html", "/developer.html", "/docs.html", "/changelog.html"],
            "evidence_level": mvp_success_check.get("current_evidence_level", "Level 1: mock / demo evidence"),
            "blocked_actions": permission_boundary.get("blocked_actions", []),
            "read_only": True,
        }

    def _permission_boundary(self) -> dict:
        return {
            "schema_id": "athena.production_permission_boundary.v1",
            "version": PRODUCTION_VERSION,
            "final_confirmation_owner": "General Manager",
            "final_confirmation_owner_zh": "总经理",
            "decision_authority": (
                "Athena supports fact collection, risk explanation, owner suggestion, "
                "local follow-up reminders, and evidence review. It does not replace "
                "the general manager's final decision authority."
            ),
            "decision_authority_zh": (
                "Athena 负责收集事实、解释风险、建议负责人、生成本地跟进和复核证据，"
                "但不替代总经理的最终确认权。"
            ),
            "allowed_actions": [
                "show_risks",
                "explain_reasons_and_evidence",
                "suggest_confirmation_owner",
                "suggest_confirmation_action",
                "generate_local_follow_up_items",
                "record_metadata_only_review_state",
            ],
            "allowed_actions_zh": [
                "灞曠ず椋庨櫓",
                "瑙ｉ噴鍘熷洜鍜岃瘉鎹?",
                "寤鸿纭璐熻矗浜?",
                "寤鸿纭鍔ㄤ綔",
                "鐢熸垚鏈湴寰呭姙",
                "璁板綍浠呭厓鏁版嵁鐨勫鏍哥姸鎬?",
            ],
            "blocked_actions": [
                "replace_erp_aps_iot",
                "modify_schedule_automatically",
                "dispatch_service_automatically",
                "upload_co_file",
                "upload_cx_file",
                "control_machine",
                "evaluate_employee_performance_directly",
                "claim_certain_conclusion_when_evidence_is_insufficient",
                "replace_general_manager_decision",
            ],
            "blocked_actions_zh": [
                "鏇夸唬 ERP / APS / IOT 绯荤粺",
                "鑷姩淇敼鎺掔▼",
                "鑷姩娲惧彂 Service 宸ュ崟",
                "涓婁紶 .co 鏂囦欢",
                "涓婁紶 .cx 鏂囦欢",
                "鎺у埗鏈哄彴",
                "鐩存帴璇勪环鍛樺伐缁╂晥",
                "璇佹嵁涓嶈冻鏃剁粰鍑虹‘瀹氱粨璁?",
                "替代总经理决策",
            ],
            "evidence_policy": {
                "insufficient_evidence_behavior": "state_missing_data_and_next_needed_evidence",
                "confidence_policy": "do_not_force_root_cause_when_data_is_missing",
                "employee_policy": (
                    "Review labor effective hours as process evidence, not as individual employee performance scoring."
                ),
            },
            "evidence_policy_zh": {
                "insufficient_evidence_behavior": "璇存槑缂哄け鏁版嵁鍜屼笅涓€姝ラ渶瑕佽ˉ鍏呯殑璇佹嵁",
                "confidence_policy": "鏁版嵁缂哄け鏃朵笉寮鸿缁欏嚭鏍瑰洜缁撹",
                "employee_policy": "鏈夋晥宸ユ椂鍙綔涓烘祦绋嬭瘉鎹紝涓嶇洿鎺ヤ綔涓轰釜浜虹哗鏁堣瘎鍒?",
            },
            "ui_note": {
                "en": "Athena can recommend what to check and who should confirm it; the general manager remains the final decision owner.",
                "zh": "Athena 可以建议查什么、由谁确认；最终决策仍由总经理确认。",
            },
        }

    def _mvp_demo_story(
        self,
        management_priority_brief: dict,
        decision_loop: dict,
        service_escalations: list[dict],
        permission_boundary: dict,
    ) -> dict:
        priorities = management_priority_brief.get("top_priorities", [])
        priority_by_theme = {item.get("management_theme"): item for item in priorities}
        delivery = priority_by_theme.get("delivery") or (priorities[0] if priorities else {})
        quality = priority_by_theme.get("quality") or {}
        labor = priority_by_theme.get("labor") or {}
        service = service_escalations[0] if service_escalations else {}
        follow_ups = decision_loop.get("follow_up_items", [])
        delivery_objects = delivery.get("affected_objects", {})
        service_order = service.get("order_id") or (delivery_objects.get("orders") or [""])[0]

        story_steps = [
            {
                "step_id": "story_step_1_open",
                "title": "Open Athena and read the management summary",
                "title_zh": "打开 Athena，先看管理摘要",
                "object_refs": [management_priority_brief.get("brief_id", "")],
                "proof": "daily_brief.summary",
                "proof_zh": "daily_brief.summary_zh",
                "expected_manager_understanding": "Know today's delivery, quality, labor, and data-boundary situation before drilling down.",
                "expected_manager_understanding_zh": "先知道今天交付、质量、人工和数据边界的大致情况，再进入下钻。",
            },
            {
                "step_id": "story_step_2_delivery",
                "title": "Start from the delivery-risk order",
                "title_zh": "从交付风险订单开始",
                "object_refs": [delivery.get("priority_id", ""), service_order],
                "proof": delivery.get("evidence_refs", []),
                "proof_zh": delivery.get("evidence_refs", []),
                "expected_manager_understanding": delivery.get("conclusion", ""),
                "expected_manager_understanding_zh": delivery.get("conclusion_zh", ""),
            },
            {
                "step_id": "story_step_3_root_cause",
                "title": "Connect delivery risk to quality, labor, and service signals",
                "title_zh": "把交付风险连接到质量、人工和服务信号",
                "object_refs": [
                    quality.get("priority_id", ""),
                    labor.get("priority_id", ""),
                    service.get("machine_id", ""),
                ],
                "proof": list(dict.fromkeys(
                    quality.get("evidence_refs", [])
                    + labor.get("evidence_refs", [])
                    + ([service.get("evidence_ref")] if service.get("evidence_ref") else [])
                )),
                "proof_zh": list(dict.fromkeys(
                    quality.get("evidence_refs", [])
                    + labor.get("evidence_refs", [])
                    + ([service.get("evidence_ref")] if service.get("evidence_ref") else [])
                )),
                "expected_manager_understanding": (
                    "The order risk is not a single KPI issue; it may be connected to replenishment quality, "
                    "low effective labor hours, and a machine/service review candidate."
                ),
                "expected_manager_understanding_zh": (
                    "这个订单风险不是单个 KPI 问题，而是可能同时关联补单质量、人工有效工时偏低，以及机台/服务复核候选。"
                ),
            },
            {
                "step_id": "story_step_4_follow_up",
                "title": "Turn the story into local follow-up items",
                "title_zh": "把故事线转成本地跟进事项",
                "object_refs": [item.get("follow_up_id", "") for item in follow_ups],
                "proof": [item.get("linked_risk_card_id", "") for item in follow_ups],
                "proof_zh": [item.get("linked_risk_card_id", "") for item in follow_ups],
                "expected_manager_understanding": "Every suggested action has an owner, evidence request, closure gate, and linked risk card.",
                "expected_manager_understanding_zh": "每条建议动作都有负责人、证据要求、关闭门槛，并关联回风险卡。",
            },
            {
                "step_id": "story_step_5_confirm",
                "title": "Keep final confirmation with the general manager",
                "title_zh": "最终确认仍由总经理完成",
                "object_refs": [permission_boundary.get("schema_id", "")],
                "proof": permission_boundary.get("blocked_actions", []),
                "proof_zh": permission_boundary.get("blocked_actions_zh", []),
                "expected_manager_understanding": permission_boundary.get("ui_note", {}).get("en", ""),
                "expected_manager_understanding_zh": permission_boundary.get("ui_note", {}).get("zh", ""),
            },
        ]

        return {
            "schema_id": "athena.production_mvp_demo_story.v1",
            "version": PRODUCTION_VERSION,
            "story_id": f"MVP-DEMO-STORY-{PRODUCTION_VERSION}-ORDER-RISK",
            "title": "Order delivery risk connected to quality, labor, and service signals",
            "title_zh": "订单交付风险连接质量、人工和服务信号",
            "audience": "General Manager / customer management demo",
            "audience_zh": "总经理 / 客户管理层演示",
            "positioning": "A three-minute story path for explaining Athena as a digital general manager, not as a chatbot.",
            "positioning_zh": "用于三分钟说明 Athena 是数字总经理，而不是聊天机器人。",
            "source_prd_section": "16. MVP Demo Story",
            "initial_story": (
                "An order's delivery risk increases. Athena detects that the risk may be connected to quality "
                "replenishment, low labor effective hours, and service-related machine stoppage risk."
            ),
            "initial_story_zh": (
                "某个订单的交付风险升高。Athena 发现这个风险可能与质量补单、人工有效工时偏低，"
                "以及 Service 相关的机台停机风险有关。"
            ),
            "story_steps": story_steps,
            "success_criteria": [
                "top_three_priorities_visible",
                "why_they_matter_visible",
                "evidence_refs_visible",
                "next_owner_confirmation_visible",
                "data_gaps_visible",
                "final_confirmation_boundary_visible",
            ],
            "success_criteria_zh": [
                "能看到今天前三件事",
                "能看到为什么重要",
                "能看到证据引用",
                "能看到下一步由谁确认",
                "能看到数据缺口",
                "能看到最终确认边界",
            ],
            "read_only": True,
            "data_boundary": "Local mock story assembled from management_priority_brief, decision_loop, service_escalations, and permission_boundary.",
            "data_boundary_zh": "本地 mock 故事线，由 management_priority_brief、decision_loop、service_escalations 和 permission_boundary 组装。",
        }

    def _stable_demo_story_pack(
        self,
        management_priority_brief: dict,
        first_screen_service_risk: dict,
        actual_data_snapshot: dict,
        material_risk: dict,
        data_readiness: dict,
        decision_loop: dict,
    ) -> dict:
        priorities = management_priority_brief.get("top_priorities", [])
        priority_by_theme = {item.get("management_theme"): item for item in priorities}
        delivery = priority_by_theme.get("delivery") or (priorities[0] if priorities else {})
        equipment = priority_by_theme.get("equipment") or (priorities[1] if len(priorities) > 1 else {})
        service_cards = first_screen_service_risk.get("service_risk_cards", [])
        service = service_cards[0] if service_cards else {}
        actual_sources = actual_data_snapshot.get("tables", [])
        actual_source_names = [
            item.get("table_name") or item.get("object_name") or item.get("name")
            for item in actual_sources
            if item.get("table_name") or item.get("object_name") or item.get("name")
        ]

        def story_from_priority(
            story_id: str,
            title: str,
            title_zh: str,
            story_type: str,
            priority: dict,
            manager_question: str,
            demo_badge: str,
            demo_badge_zh: str,
        ) -> dict:
            evidence_mode = "actual_export" if priority.get("actual_evidence_chains") else "mock_or_partial"
            return {
                "story_id": story_id,
                "story_type": story_type,
                "title": title,
                "title_zh": title_zh,
                "demo_badge": demo_badge,
                "demo_badge_zh": demo_badge_zh,
                "manager_question": manager_question,
                "chatbi_question": priority.get("drilldown_question") or manager_question,
                "primary_objects": priority.get("affected_objects", {}),
                "what_athena_shows": [
                    priority.get("title_zh") or priority.get("title") or title,
                    priority.get("conclusion_zh") or priority.get("conclusion") or "",
                    priority.get("recommended_action_zh") or priority.get("recommended_action") or "",
                ],
                "evidence_mode": evidence_mode,
                "real_data_sources": priority.get("source_objects", []) or actual_source_names,
                "field_sources": priority.get("field_sources", []),
                "evidence_refs": priority.get("evidence_refs", []),
                "actual_evidence_chains": priority.get("actual_evidence_chains", []),
                "mock_supplements": [],
                "data_gaps": priority.get("data_gaps", []),
                "suggested_owner": priority.get("owner_role", ""),
                "internal_demo_ready": bool(priority.get("internal_demo_ready")),
                "read_only": True,
                "blocked_actions": [
                    "no_aps_writeback",
                    "no_erp_writeback",
                    "no_iot_writeback",
                    "no_machine_control",
                    "no_auto_dispatch",
                ],
            }

        stories = [
            story_from_priority(
                "STABLE-DEMO-001-REAL-DELIVERY",
                "Which order should the General Manager watch first?",
                "总经理今天先盯哪个订单？",
                "real_data_main_line",
                delivery,
                "今天先盯哪个订单？为什么？",
                "Actual APS/ERP export",
                "真实 APS/ERP 导出",
            ),
            story_from_priority(
                "STABLE-DEMO-002-REAL-MACHINE-FIT",
                "Is any style scheduled onto a risky machine specification?",
                "是否有款式被排到存在规格风险的机台？",
                "real_data_main_line",
                equipment,
                "这批订单是否有机台/款式规格不匹配风险？",
                "Actual APS/ERP export",
                "真实 APS/ERP 导出",
            ),
        ]

        stories.append(
            {
                "story_id": "STABLE-DEMO-003-HYBRID-SERVICE-IMPACT",
                "story_type": "hybrid_real_order_mock_iot_service",
                "title": "If a machine keeps stopping, which order may be affected?",
                "title_zh": "这台机如果继续停机，会影响哪个订单？",
                "demo_badge": "Real schedule context + mock IOT/Service signal",
                "demo_badge_zh": "真实排产上下文 + mock IOT/Service 信号",
                "manager_question": "这台机如果继续停机会影响哪个订单？",
                "chatbi_question": service.get("drilldown_question") or "这台机如果继续停机会影响哪个订单？",
                "primary_objects": service.get("affected_objects", {}),
                "what_athena_shows": [
                    service.get("title_zh") or service.get("title") or "",
                    service.get("why_it_matters_zh") or service.get("why_it_matters") or "",
                    service.get("recommended_action_zh") or service.get("recommended_action") or "",
                ],
                "evidence_mode": "hybrid",
                "real_data_sources": [
                    "management_priority_brief.actual APS/ERP order context",
                    "Planned_Task / Produce_Order evidence when the affected order is present in export",
                ],
                "field_sources": service.get("field_sources", []),
                "evidence_refs": service.get("evidence_refs", []),
                "actual_evidence_chains": delivery.get("actual_evidence_chains", [])[:1],
                "mock_supplements": [
                    "IOT machine state / alarm signal is currently mock_contract",
                    "Service request candidate is local metadata only",
                ],
                "data_gaps": service.get("data_gaps", []),
                "suggested_owner": service.get("suggested_owner", "Service Manager / Maintenance Owner"),
                "internal_demo_ready": bool(service.get("internal_demo_ready")),
                "read_only": True,
                "blocked_actions": service.get("blocked_actions", []) or [
                    "dispatch_service_automatically",
                    "create_real_service_ticket",
                    "control_machine",
                ],
            }
        )

        return {
            "schema_id": "athena.production_stable_demo_story_pack.v1",
            "version": PRODUCTION_VERSION,
            "pack_id": f"STABLE-DEMO-PACK-{PRODUCTION_VERSION}",
            "title": "General Manager three-minute production decision demo",
            "title_zh": "总经理三分钟生产决策演示包",
            "positioning": "A repeatable demo pack that separates real evidence, mock supplements, and missing data before Athena gives recommendations.",
            "positioning_zh": "一套可重复演示的故事包：先区分真实证据、mock 补充和缺失数据，再让 Athena 给出建议。",
            "demo_policy": {
                "real_data_main_line": "Use Tianpai APS/ERP export evidence for delivery and machine/style-fit stories.",
                "mock_supplement_rule": "Use mock IOT/Service only to show future workflow behavior, and label it clearly.",
                "claim_boundary": "Do not claim live root cause, live IOT status, real dispatch, cost result, or downstream quality proof.",
            },
            "demo_policy_zh": {
                "real_data_main_line": "交付风险和机台/款式规格风险优先使用天派 APS/ERP 导出证据。",
                "mock_supplement_rule": "IOT/Service mock 只用于展示未来工作流行为，必须明确标注。",
                "claim_boundary": "不声称实时根因、实时 IOT 状态、真实派工、真实成本或下游质量证明。",
            },
            "actual_data_available": {
                "usable_for_demo": [
                    "delivery risk from Produce_Order / Weaving_Part_Order / Planned_Task / Manual_Machine_Production",
                    "machine/style fit from Style_Component and T_Machine_Info",
                    "material signal from yarn inventory aggregate and material priority card",
                ],
                "usable_for_demo_zh": [
                    "基于 Produce_Order / Weaving_Part_Order / Planned_Task / Manual_Machine_Production 的交付风险",
                    "基于 Style_Component 和 T_Machine_Info 的机台/款式规格匹配",
                    "基于纱线库存汇总和物料风险卡的物料信号",
                ],
                "source_tables": actual_source_names,
                "evidence_level": "Level 2: external APS/ERP export evidence",
            },
            "mock_needed_for_demo": [
                "live IOT alarm duration and OEE",
                "real service ticket dispatch status",
                "quality defect reason and replenishment closure",
                "labor effective-hour history",
                "purchase, rework, freight, and per-garment cost",
            ],
            "stories": stories,
            "recommended_demo_sequence": [
                "Open /production.html and start with the stable demo story pack.",
                "Open Story 1 and send its question to Santoni Athena.",
                "Show the verification process and evidence chain.",
                "Open Story 3 to show which parts are mock supplements.",
                "Create or review a local follow-up item without writing real systems.",
            ],
            "recommended_demo_sequence_zh": [
                "打开 /production.html，先看稳定演示故事包。",
                "打开故事 1，把问题发送给 Santoni Athena。",
                "展示查证过程和证据链。",
                "打开故事 3，说明哪些是 mock 补充。",
                "创建或查看本地 follow-up，不写真实系统。",
            ],
            "decision_loop_refs": [item.get("follow_up_id") for item in decision_loop.get("follow_up_items", [])],
            "material_context": {
                "material_priority_id": material_risk.get("priority_id") or material_risk.get("material_risk_id") or "",
                "readiness_status": data_readiness.get("overall_status", ""),
            },
            "read_only": True,
        }

    def _mvp_success_check(
        self,
        management_priority_brief: dict,
        decision_loop: dict,
        mvp_demo_story: dict,
        permission_boundary: dict,
    ) -> dict:
        priorities = management_priority_brief.get("top_priorities", [])
        follow_ups = decision_loop.get("follow_up_items", [])
        story_steps = mvp_demo_story.get("story_steps", [])
        all_priorities_have_reasons = all(
            item.get("reason") and item.get("risk_if_ignored") for item in priorities
        )
        all_priorities_have_evidence = all(
            item.get("evidence_refs") and item.get("evidence_claims") for item in priorities
        )
        all_followups_have_owner = bool(follow_ups) and all(
            item.get("owner_role") and item.get("linked_risk_card_id") for item in follow_ups
        )
        priority_data_gaps = [
            gap
            for item in priorities
            for gap in item.get("data_gaps", [])
            if gap
        ]
        brief_data_gaps = management_priority_brief.get("data_gaps", [])
        summary_lines = management_priority_brief.get("daily_brief", {}).get("summary", [])

        checks = [
            {
                "criterion_id": "success_top_three_things",
                "prd_requirement": "The top three things to handle today",
                "prd_requirement_zh": "今天最应该处理的前三件事",
                "status": "pass" if len(priorities) == 3 and 3 <= len(summary_lines) <= 5 else "needs_work",
                "evidence_refs": [item.get("priority_id", "") for item in priorities],
                "object_refs": [management_priority_brief.get("brief_id", "")],
                "manager_visible_surface": "General Manager 3-Minute Brief",
                "manager_visible_surface_zh": "总经理三分钟简报",
            },
            {
                "criterion_id": "success_why_they_matter",
                "prd_requirement": "Why they matter",
                "prd_requirement_zh": "为什么重要",
                "status": "pass" if all_priorities_have_reasons else "needs_work",
                "evidence_refs": [item.get("priority_id", "") for item in priorities if item.get("risk_if_ignored")],
                "object_refs": [item.get("priority_id", "") for item in priorities],
                "manager_visible_surface": "Risk cards and expanded details",
                "manager_visible_surface_zh": "风险卡与展开详情",
            },
            {
                "criterion_id": "success_evidence_support",
                "prd_requirement": "Which evidence supports them",
                "prd_requirement_zh": "哪些证据支持这些判断",
                "status": "pass" if all_priorities_have_evidence else "needs_work",
                "evidence_refs": list(dict.fromkeys(
                    ref
                    for item in priorities
                    for ref in item.get("evidence_refs", [])
                    if ref
                )),
                "object_refs": [item.get("priority_id", "") for item in priorities],
                "manager_visible_surface": "Evidence chips and evidence detail lists",
                "manager_visible_surface_zh": "证据标签与证据详情列表",
            },
            {
                "criterion_id": "success_next_owner_confirmation",
                "prd_requirement": "Who should confirm next",
                "prd_requirement_zh": "下一步应该由谁确认",
                "status": "pass" if all_followups_have_owner else "needs_work",
                "evidence_refs": [item.get("linked_risk_card_id", "") for item in follow_ups],
                "object_refs": [item.get("follow_up_id", "") for item in follow_ups],
                "manager_visible_surface": "Decision Loop / local follow-up items",
                "manager_visible_surface_zh": "决策闭环 / 本地跟进事项",
            },
            {
                "criterion_id": "success_missing_data_visible",
                "prd_requirement": "Which data is still missing",
                "prd_requirement_zh": "仍然缺少哪些数据",
                "status": "pass" if brief_data_gaps and priority_data_gaps else "needs_work",
                "evidence_refs": [item.get("gap_id", "") for item in brief_data_gaps],
                "object_refs": [item.get("priority_id", "") for item in priorities if item.get("data_gaps")],
                "manager_visible_surface": "Data gaps in risk-card details and data-readiness section",
                "manager_visible_surface_zh": "风险卡详情与数据准备度里的数据缺口",
            },
        ]
        pass_count = len([item for item in checks if item["status"] == "pass"])
        check_count = len(checks)
        readiness_score = pass_count / check_count if check_count else 0
        all_core_pass = pass_count == check_count

        return {
            "schema_id": "athena.production_mvp_success_check.v1",
            "version": PRODUCTION_VERSION,
            "check_id": f"MVP-SUCCESS-CHECK-{PRODUCTION_VERSION}-CURRENT",
            "source_prd_section": "17. Success Criteria",
            "within_three_minutes_ready": all_core_pass,
            "readiness_status": "demo_ready_with_mock_evidence" if all_core_pass else "needs_more_evidence",
            "readiness_score": round(readiness_score, 2),
            "current_evidence_level": "Level 1: mock / demo evidence",
            "criteria_checks": checks,
            "criteria_summary": {
                "pass_count": pass_count,
                "check_count": check_count,
                "needs_work_count": check_count - pass_count,
                "story_step_count": len(story_steps),
                "follow_up_count": len(follow_ups),
            },
            "manager_readout": (
                "A general manager can review the top three priorities, reasons, evidence, next confirmation owners, "
                "and data gaps in one Production Console flow. Current proof is still Level 1 mock evidence."
            ),
            "manager_readout_zh": (
                "总经理可以在一个 Production Console 流程中看到前三件事、原因、证据、下一步确认负责人和数据缺口。"
                "当前证明仍属于 Level 1 mock 证据。"
            ),
            "remaining_data_boundary": [
                "Real ERP/APS/IOT joins are not connected.",
                "Historical labor baseline is not connected.",
                "Quality and downstream process records are still mock or planned.",
                "General manager VOC verification is still pending.",
            ],
            "remaining_data_boundary_zh": [
                "真实 ERP/APS/IOT 关联尚未接入。",
                "历史人工有效工时基线尚未接入。",
                "质量和后道工序记录仍是 mock 或计划中。",
                "总经理 VOC 验证仍待完成。",
            ],
            "blocked_actions": permission_boundary.get("blocked_actions", []),
            "read_only": True,
        }

    def _demo_evolution_pack(
        self,
        management_priority_brief: dict,
        stable_demo_story_pack: dict,
        first_screen_service_risk: dict,
        decision_loop: dict,
        actual_data_snapshot: dict,
        material_risk: dict,
        data_readiness: dict,
        permission_boundary: dict,
    ) -> dict:
        priorities = management_priority_brief.get("top_priorities", [])
        stories = stable_demo_story_pack.get("stories", [])
        service_cards = first_screen_service_risk.get("service_risk_cards", [])
        follow_ups = decision_loop.get("follow_up_items", [])
        question_set = [
            {
                "question_id": "GM-REG-001",
                "question_zh": "今天先看哪三件事？",
                "question": "What are today's top three production priorities?",
                "coverage": "today_top_three",
                "expected_contract": ["conclusion", "evidence", "recommendation", "data_gap", "read_only_boundary"],
            },
            {
                "question_id": "GM-REG-002",
                "question_zh": "哪个订单最可能影响交付？证据是什么？",
                "question": "Which order has the strongest delivery risk and what evidence supports it?",
                "coverage": "delivery_risk",
                "expected_contract": ["affected_order", "actual_export_evidence", "suggested_confirmation_owner"],
            },
            {
                "question_id": "GM-REG-003",
                "question_zh": "有没有机台和款式规格不匹配的风险？",
                "question": "Is any style scheduled on a machine with specification-fit risk?",
                "coverage": "machine_style_fit",
                "expected_contract": ["machine", "style_or_part", "field_sources", "cannot_confirm_root_cause"],
            },
            {
                "question_id": "GM-REG-004",
                "question_zh": "这台机如果继续停机会影响哪个订单？",
                "question": "If this machine keeps stopping, which order may be affected?",
                "coverage": "service_risk",
                "expected_contract": ["service_candidate", "mock_iot_boundary", "no_auto_dispatch"],
            },
            {
                "question_id": "GM-REG-005",
                "question_zh": "鐗╂枡鏁版嵁鐜板湪鑳芥敮鎸佷粈涔堝垽鏂紵杩樼己浠€涔堬紵",
                "question": "What can material data support today and what is still missing?",
                "coverage": "material_risk",
                "expected_contract": ["material_signal", "inventory_boundary", "data_request"],
            },
            {
                "question_id": "GM-REG-006",
                "question_zh": "目前哪些结论不能说死？",
                "question": "Which conclusions cannot be claimed as final today?",
                "coverage": "data_gap",
                "expected_contract": ["cannot_claim", "missing_data", "human_confirmation"],
            },
        ]
        evidence_modes = {
            "actual_export": {
                "manager_label": "Actual APS/ERP export evidence",
                "description": "Read-only Tianpai APS/ERP export evidence used for delivery, scheduling, and machine/style checks.",
                "allowed_claims": ["risk signal", "evidence chain", "suggested confirmation owner"],
                "cannot_claim": ["live shop-floor status", "final root cause", "automatic rescheduling"],
            },
            "mock_contract": {
                "manager_label": "Local mock contract",
                "description": "Used to demonstrate future IOT, Service, quality, and labor workflow behavior.",
                "allowed_claims": ["capability boundary", "candidate workflow"],
                "cannot_claim": ["real IOT alarm", "real Service ticket", "real quality conclusion"],
            },
            "hybrid": {
                "manager_label": "Actual export plus mock supplement",
                "description": "Orders and schedules use export evidence; live equipment, Service, quality, or labor details may remain mock candidates.",
                "allowed_claims": ["demo workflow", "explicit evidence boundary"],
                "cannot_claim": ["fully live integration", "confirmed production action"],
            },
            "data_gap": {
                "manager_label": "Data gap",
                "description": "Required fields or joins are missing, so Athena can only ask for confirmation or more data.",
                "allowed_claims": ["what is missing", "who should confirm"],
                "cannot_claim": ["risk certainty", "cost certainty", "owner fault"],
            },
        }
        data_requests = data_readiness.get("next_data_requests", [])
        demo_ready_actual = [story for story in stories if story.get("evidence_mode") == "actual_export"]
        demo_ready_hybrid = [story for story in stories if story.get("evidence_mode") == "hybrid"]
        service_flow = [
            {
                "candidate_id": card.get("card_id") or card.get("candidate_id", ""),
                "title": card.get("title", ""),
                "suggested_owner": card.get("suggested_owner", "Maintenance / Service owner"),
                "evidence_refs": card.get("evidence_refs", []),
                "auto_dispatch": False,
                "write_scope": "local_metadata_only",
            }
            for card in service_cards
        ]
        skill_process = [
            {
                "step": "collect_evidence",
                "manager_label": "Athena checks order, schedule, machine, material, Service, and evidence-chain objects.",
                "raw_debug_visible": False,
            },
            {
                "step": "rank_priority",
                "manager_label": "Athena ranks top priorities by delivery, quality, then cost impact.",
                "raw_debug_visible": False,
            },
            {
                "step": "create_follow_up_candidate",
                "manager_label": "Athena can create local metadata-only follow-up candidates after manager review.",
                "raw_debug_visible": False,
            },
        ]
        memory_candidates = decision_loop.get("memory_event_candidates", [])
        guided_steps = [
            {
                "step": 1,
                "title": "Open General Manager mode",
                "expected_manager_understanding": "Athena starts from the daily top-three priorities.",
            },
            {
                "step": 2,
                "title": "Review hard risks",
                "expected_manager_understanding": "Hard-risk cards are action candidates with evidence and owners.",
            },
            {
                "step": 3,
                "title": "Review evidence candidates",
                "expected_manager_understanding": "Evidence-review cards are data confirmation tasks, not confirmed risks.",
            },
            {
                "step": 4,
                "title": "Drill down with Athena",
                "expected_manager_understanding": "Athena explains what it checked, what it found, and what remains uncertain.",
            },
            {
                "step": 5,
                "title": "Create local follow-up",
                "expected_manager_understanding": "Follow-up stays local metadata only and does not write APS, ERP, IOT, or Service systems.",
            },
            {
                "step": 6,
                "title": "Use Daily Brief",
                "expected_manager_understanding": "Daily Brief summarizes priorities, data gaps, owners, and the read-only boundary.",
            },
        ]
        return {
            "schema_id": "athena.production_internal_demo_candidate.v1",
            "version": PRODUCTION_VERSION,
            "candidate_id": f"INTERNAL-DEMO-CANDIDATE-{PRODUCTION_VERSION}",
            "guided_demo_flow": {
                "schema_id": "athena.production_guided_demo_flow.v1",
                "version": PRODUCTION_VERSION,
                "status": "ready_for_internal_demo",
                "steps": guided_steps,
                "demo_reset_policy": {
                    "scope": "local_demo_state_only",
                    "does_not_delete_actual_export": True,
                    "does_not_write_external_systems": True,
                },
                "read_only": True,
            },
            "user_page_gm_demo_entry": {
                "schema_id": "athena.user_page_gm_demo_entry.v1",
                "version": PRODUCTION_VERSION,
                "entry_label": "总经理",
                "visible_sections": ["today_top_three", "stable_story_shortcuts", "service_risk", "local_follow_up", "original_chat_drilldown"],
                "hidden_from_user_page": ["Internal Demo Mode", "raw payload", "debug trace", "development plan"],
                "read_only": True,
            },
            "presenter_mode": {
                "schema_id": "athena.production_presenter_mode.v1",
                "version": PRODUCTION_VERSION,
                "recommended_sequence": stable_demo_story_pack.get("recommended_demo_sequence", []),
                "recommended_questions": question_set,
                "expected_outputs": [
                    "today_top_three_risk_cards",
                    "evidence_boundary_readout",
                    "manager_language_verification_process",
                    "local_follow_up_candidate",
                ],
                "customer_page_debug_visible": False,
            },
            "evidence_boundary_layer": {
                "schema_id": "athena.production_evidence_boundary_layer.v1",
                "version": PRODUCTION_VERSION,
                "modes": evidence_modes,
                "story_mode_summary": [
                    {
                        "story_id": story.get("story_id"),
                        "evidence_mode": story.get("evidence_mode"),
                        "field_sources": story.get("field_sources", []),
                        "cannot_claim": evidence_modes.get(story.get("evidence_mode"), evidence_modes["data_gap"])["cannot_claim"],
                    }
                    for story in stories
                ],
                "read_only": True,
            },
            "gm_question_regression_set": {
                "schema_id": "athena.gm_question_regression_set.v1",
                "version": PRODUCTION_VERSION,
                "questions": question_set,
                "minimum_answer_contract": ["conclusion", "evidence", "recommendation", "data_gap", "read_only_boundary"],
                "run_mode": "local_test_harness",
            },
            "data_request_wizard": {
                "schema_id": "athena.data_request_wizard.v1",
                "version": PRODUCTION_VERSION,
                "requests": data_requests,
                "does_not_store_raw_sensitive_data": True,
            },
            "service_risk_confirmation_flow": {
                "schema_id": "athena.service_risk_confirmation_flow.v1",
                "version": PRODUCTION_VERSION,
                "confirmation_cards": service_flow,
                "auto_dispatch": False,
                "create_real_ticket": False,
                "control_machine": False,
            },
            "visible_athena_skill_process": {
                "schema_id": "athena.visible_skill_process.v1",
                "version": PRODUCTION_VERSION,
                "manager_language_steps": skill_process,
                "raw_debug_visible": False,
                "raw_payload_visible": False,
                "internal_schema_visible": False,
            },
            "hermes_training_memory_review": {
                "schema_id": "athena.hermes_training_memory_review.v1",
                "version": PRODUCTION_VERSION,
                "candidate_count": len(memory_candidates),
                "review_statuses": ["candidate", "reviewed", "approved"],
                "memory_event_fields": [
                    "scope",
                    "tenant_id",
                    "factory_id",
                    "source",
                    "retention_policy",
                    "sensitivity_level",
                    "promotion_status",
                ],
                "candidates": memory_candidates,
                "live_hermes_write": False,
            },
            "internal_demo_candidate_report": {
                "path": "docs/product/athena_daily_brief_narrative_v0.113.0.md",
                "linked_from_docs": True,
                "actual_export_story_count": len(demo_ready_actual),
                "hybrid_story_count": len(demo_ready_hybrid),
                "should_enter_v1": False,
                "reason_not_v1": "Internal demo candidate is stronger, but live ERP/IOT/quality/labor/cost integration and customer validation are still missing.",
            },
            "actual_data_basis": {
                "actual_export_status": actual_data_snapshot.get("actual_export_status", ""),
                "source_tables": stable_demo_story_pack.get("actual_data_available", {}).get("source_tables", []),
                "priority_count": management_priority_brief.get("data_source_policy", {}).get("actual_export_priority_count", 0),
            },
            "mock_or_hybrid_basis": {
                "mock_needed_for_demo": stable_demo_story_pack.get("mock_needed_for_demo", []),
                "service_candidate_count": len(service_cards),
                "material_status": material_risk.get("risk_level") or material_risk.get("status", ""),
                "data_readiness_status": data_readiness.get("overall_status", ""),
            },
            "read_only_boundary": {
                "read_only": True,
                "blocked_actions": permission_boundary.get("blocked_actions", []),
            },
        }

    def _actual_data_snapshot(self, export_report: dict) -> dict:
        standard_objects = export_report.get("standard_objects", {})
        metrics = standard_objects.get("actual_snapshot_metrics", {})
        mismatch = standard_objects.get("machine_style_spec_mismatch_candidates", {})
        quality = export_report.get("data_quality_report", {})
        return {
            "schema_id": "athena.production_actual_data_snapshot.v1",
            "version": PRODUCTION_VERSION,
            "source_modes": ["mock_snapshot", "tianpai_aps_export"],
            "current_data_source_label": "Mock / Tianpai APS Export",
            "actual_export_status": export_report.get("adapter_status", "missing_external_csv"),
            "read_only": True,
            "raw_file_stored_in_repo": export_report.get("raw_file_stored_in_repo", False),
            "kpis": {
                "total_order_count": metrics.get("total_order_count", 0),
                "near_due_order_count": metrics.get("near_due_order_count", 0),
                "scheduled_weaving_part_order_count": metrics.get("scheduled_weaving_part_order_count", 0),
                "unscheduled_weaving_part_order_count": metrics.get("unscheduled_weaving_part_order_count", 0),
                "plan_completion_rate": metrics.get("plan_completion_rate", 0),
                "manual_report_completion_rate": metrics.get("manual_report_completion_rate", 0),
                "machine_plan_load_candidate_count": metrics.get("machine_plan_load_candidate_count", 0),
                "machine_style_spec_mismatch_candidate_count": metrics.get("machine_style_spec_mismatch_candidate_count", 0),
            },
            "machine_plan_load_top": standard_objects.get("machine_plan_load", [])[:10],
            "machine_style_spec_mismatch_candidates": {
                "candidate_count_total": mismatch.get("candidate_count_total", 0),
                "sample_limit": mismatch.get("sample_limit", 0),
                "candidates": mismatch.get("candidates", [])[:20],
            },
            "join_quality": quality.get("join_quality", []),
            "capability_boundary": export_report.get("capability_boundary", {}),
            "blocked_actions": export_report.get("blocked_actions", []),
        }

    def _actual_management_priority_analyses(self, adapter: TianpaiApsErpExportAdapter) -> list[dict]:
        questions = [
            {
                "question": "哪些订单有交付风险？",
                "priority_id": "MGMT-PRIO-ACTUAL-DELIVERY-001",
                "risk_theme": "delivery",
                "theme_label": "交付",
                "priority": "P0",
                "score": 100,
                "owner_role": "Planning Manager / Production Manager",
                "decision_gate": "planning_owner_confirms_actual_delivery_risk",
                "confirmation_needed_by": "today",
                "action_id": "ACT-ACTUAL-DELIVERY-001",
            },
            {
                "question": "哪些款式可能因为机台规格不匹配导致风险？",
                "priority_id": "MGMT-PRIO-ACTUAL-EQUIPMENT-001",
                "risk_theme": "equipment",
                "theme_label": "设备",
                "priority": "P1",
                "score": 94,
                "owner_role": "APS Engineer / Production Engineering",
                "decision_gate": "engineering_confirms_machine_style_match",
                "confirmation_needed_by": "current_shift_review",
                "action_id": "ACT-ACTUAL-EQUIPMENT-001",
            },
            {
                "question": "哪些部件单还没有排满？",
                "priority_id": "MGMT-PRIO-ACTUAL-MATERIAL-001",
                "risk_theme": "material",
                "theme_label": "物料/部件",
                "priority": "P1",
                "score": 90,
                "owner_role": "Planning Manager",
                "decision_gate": "planner_confirms_unscheduled_part_order",
                "confirmation_needed_by": "current_shift_review",
                "action_id": "ACT-ACTUAL-MATERIAL-001",
            },
            {
                "question": "哪些订单计划量和报工量差异最大？",
                "priority_id": "MGMT-PRIO-ACTUAL-COST-001",
                "risk_theme": "cost",
                "theme_label": "成本/报工",
                "priority": "P2",
                "score": 84,
                "owner_role": "Production Supervisor / Reporting Owner",
                "decision_gate": "production_owner_confirms_quantity_report_gap",
                "confirmation_needed_by": "next_shift_review",
                "action_id": "ACT-ACTUAL-COST-001",
            },
            {
                "question": "哪些机台负载最高？",
                "priority_id": "MGMT-PRIO-ACTUAL-EQUIPMENT-LOAD-001",
                "risk_theme": "equipment",
                "theme_label": "设备",
                "priority": "P2",
                "score": 80,
                "owner_role": "Planning Manager / Production Supervisor",
                "decision_gate": "planner_confirms_machine_load_balance",
                "confirmation_needed_by": "next_shift_review",
                "action_id": "ACT-ACTUAL-EQUIPMENT-LOAD-001",
            },
        ]
        analyses: list[dict] = []
        for config in questions:
            analysis = adapter.answer_management_question(config["question"])
            if not analysis or not analysis.get("actual_data_mode") or not analysis.get("actual_evidence_chains"):
                continue
            enriched = dict(analysis)
            enriched["priority_config"] = config
            analyses.append(enriched)
        return analyses

    def _actual_management_priorities(self, analyses: list[dict]) -> list[dict]:
        priorities: list[dict] = []
        for analysis in analyses:
            config = analysis.get("priority_config", {})
            chains = analysis.get("actual_evidence_chains", [])
            if not chains:
                continue
            chain = chains[0]
            evidence_refs = self._unique_refs(chain.get("evidence_refs", []))
            field_source = chain.get("field_source") or "Tianpai APS Export"
            produce_order = chain.get("produce_order_code")
            machine_code = chain.get("machine_code")
            part_id = chain.get("weaving_part_order_id") or ", ".join(chain.get("weaving_part_order_ids", [])[:3])
            title_subject = produce_order or machine_code or part_id or analysis.get("metric", "actual data")
            risk_theme = config.get("risk_theme", "delivery")
            action_id = config.get("action_id", f"ACT-{analysis.get('metric', 'ACTUAL').upper()}")
            recommended_action = self._actual_priority_recommended_action(analysis.get("metric", ""), title_subject)
            recommended_action_zh = self._actual_priority_recommended_action_zh(analysis.get("metric", ""), title_subject)
            drilldown_question = self._actual_priority_drilldown_question(analysis.get("metric", ""), title_subject)
            action_candidate = self._priority_action_candidate(
                action_id,
                config.get("owner_role", "Production Owner"),
                recommended_action,
                ["actual APS/ERP export row", "field source review", "owner confirmation"],
            )
            action_candidate.update(
                {
                    "write_scope": "local_metadata_only",
                    "linked_evidence_chain": chain,
                    "field_sources": [field_source],
                    "drilldown_question": drilldown_question,
                    "follow_up_contract": {
                        "mode": "local_metadata_only",
                        "writes_real_system": False,
                        "blocked_systems": ["APS", "ERP", "IOT", "service_ticket", "machine_control"],
                    },
                }
            )
            priorities.append(
                {
                    "priority_id": config.get("priority_id", f"MGMT-PRIO-ACTUAL-{analysis.get('metric', 'UNKNOWN').upper()}"),
                    "rank": 0,
                    "priority": config.get("priority", "P1"),
                    "score": config.get("score", 80),
                    "management_theme": risk_theme,
                    "risk_theme": risk_theme,
                    "risk_theme_label": config.get("theme_label", risk_theme),
                    "theme_label": config.get("theme_label", risk_theme),
                    "title": self._actual_priority_title(analysis.get("metric", ""), title_subject),
                    "title_zh": self._actual_priority_title_zh(analysis.get("metric", ""), title_subject),
                    "management_question": config.get("question", ""),
                    "conclusion": analysis.get("answer_summary", ""),
                    "conclusion_zh": analysis.get("answer_summary", ""),
                    "reason": self._actual_priority_reason(analysis, chain),
                    "reason_zh": self._actual_priority_reason_zh(analysis, chain),
                    "risk_if_ignored": self._actual_priority_risk_if_ignored(analysis.get("metric", "")),
                    "risk_if_ignored_zh": self._actual_priority_risk_if_ignored_zh(analysis.get("metric", "")),
                    "recommended_action": recommended_action,
                    "recommended_action_zh": recommended_action_zh,
                    "owner_role": config.get("owner_role", "Production Owner"),
                    "confirmation_needed_by": config.get("confirmation_needed_by", "current_shift_review"),
                    "decision_gate": config.get("decision_gate", "owner_confirms_actual_evidence"),
                    "affected_objects": self._affected_objects_from_actual_chain(chain),
                    "kpi_links": self._actual_priority_kpi_links(analysis.get("metric", "")),
                    "evidence_refs": evidence_refs,
                    "evidence_claims": self._actual_evidence_claims(evidence_refs, analysis, chain),
                    "actual_evidence_chains": [chain],
                    "field_sources": [field_source],
                    "source_objects": analysis.get("source_objects", []),
                    "data_source_mode": "actual_aps_erp_export_first",
                    "evidence_level": "Level 2: external APS/ERP export evidence",
                    "internal_demo_ready": True,
                    "drilldown_question": drilldown_question,
                    "data_gaps": analysis.get("data_gaps", []),
                    "action_candidate": action_candidate,
                }
            )
        return priorities

    @staticmethod
    def _actual_priority_title(metric: str, subject: str) -> str:
        titles = {
            "order_delay": f"Confirm delivery risk for order {subject}",
            "machine_style_mismatch": f"Confirm machine/style match for {subject}",
            "unscheduled_weaving_part_order": f"Confirm unscheduled weaving part order {subject}",
            "quantity_report_gap": f"Confirm plan/report quantity gap for {subject}",
            "machine_plan_load": f"Review high machine plan load on {subject}",
        }
        return titles.get(metric, f"Review actual-data risk for {subject}")

    @staticmethod
    def _actual_priority_title_zh(metric: str, subject: str) -> str:
        titles = {
            "order_delay": f"确认订单 {subject} 的交付风险",
            "machine_style_mismatch": f"确认 {subject} 的机台/款式匹配风险",
            "unscheduled_weaving_part_order": f"确认织造部件单 {subject} 的未排满风险",
            "quantity_report_gap": f"确认 {subject} 的计划/报工数量差异",
            "machine_plan_load": f"复核 {subject} 的机台计划负载",
        }
        return titles.get(metric, f"复核 {subject} 的真实数据风险")

    @staticmethod
    def _actual_priority_recommended_action(metric: str, subject: str) -> str:
        actions = {
            "order_delay": f"Ask planning to confirm order {subject}, its unscheduled quantity, and whether recovery action is needed today.",
            "machine_style_mismatch": f"Ask APS or engineering to confirm whether {subject} is a real machine/style mismatch or an allowed substitution.",
            "unscheduled_weaving_part_order": f"Ask planning to confirm whether part order {subject} needs rescheduling or is intentionally left open.",
            "quantity_report_gap": f"Ask the reporting owner to confirm whether {subject} is caused by split tasks, rework, or reporting timing.",
            "machine_plan_load": f"Ask planning to confirm whether {subject} is intentional capacity concentration or a scheduling risk.",
        }
        return actions.get(metric, f"Ask the responsible owner to confirm the actual-data evidence for {subject}.")

    @staticmethod
    def _actual_priority_recommended_action_zh(metric: str, subject: str) -> str:
        actions = {
            "order_delay": f"请计划负责人确认订单 {subject} 的未排数量，以及今天是否需要恢复动作。",
            "machine_style_mismatch": f"请 APS 或生产工程确认 {subject} 是否真实存在机台/款式不匹配，还是允许的替代机台。",
            "unscheduled_weaving_part_order": f"请计划负责人确认部件单 {subject} 是否需要重排，还是故意保留未排。",
            "quantity_report_gap": f"请报工负责人确认 {subject} 是否由拆分任务、返工或报工时间差造成。",
            "machine_plan_load": f"请计划负责人确认 {subject} 是有意集中产能，还是排程风险。",
        }
        return actions.get(metric, f"请责任人确认 {subject} 的真实数据证据。")

    @staticmethod
    def _actual_priority_drilldown_question(metric: str, subject: str) -> str:
        questions = {
            "order_delay": f"为什么订单 {subject} 有交付风险？请按订单、部件单、计划任务、机台和字段来源下钻。",
            "machine_style_mismatch": f"为什么 {subject} 有机台/款式规格不匹配风险？请按筒径、针距、任务和字段来源下钻。",
            "unscheduled_weaving_part_order": f"为什么织造部件单 {subject} 还没排满？请按订单、部件单、计划量和字段来源下钻。",
            "quantity_report_gap": f"为什么 {subject} 的计划量和报工量差异大？请按订单、任务、报工和字段来源下钻。",
            "machine_plan_load": f"为什么机台 {subject} 计划负载最高？请按任务、订单、计划量和字段来源下钻。",
        }
        return questions.get(metric, f"为什么 {subject} 是当前真实数据风险？请按证据链和字段来源下钻。")

    @staticmethod
    def _actual_priority_reason(analysis: dict, chain: dict) -> str:
        refs = ", ".join(chain.get("evidence_refs", [])[:3])
        return f"{analysis.get('answer_summary', '')} Field source: {chain.get('field_source', 'Tianpai APS Export')}. Evidence: {refs or 'actual export row'}."

    @staticmethod
    def _actual_priority_reason_zh(analysis: dict, chain: dict) -> str:
        refs = "；".join(chain.get("evidence_refs", [])[:3])
        source = chain.get("field_source", "天派 APS/ERP 导出")
        return f"{analysis.get('answer_summary', '')} 字段来源：{source}。证据：{refs or '真实导出行'}。"

    @staticmethod
    def _actual_priority_risk_if_ignored(metric: str) -> str:
        risks = {
            "order_delay": "If ignored, the order can become a same-day delivery recovery problem instead of a planned confirmation task.",
            "machine_style_mismatch": "If ignored, the factory may lose time on setup, rework, or machine reassignment before the issue is noticed.",
            "unscheduled_weaving_part_order": "If ignored, unplanned part-order gaps can silently consume buffer and push delivery recovery downstream.",
            "quantity_report_gap": "If ignored, plan/report quantity gaps can hide rework, split-task reporting, or inaccurate progress visibility.",
            "machine_plan_load": "If ignored, concentrated load can create bottlenecks even when total capacity looks sufficient.",
        }
        return risks.get(metric, "If ignored, the risk can recur without owner confirmation.")

    @staticmethod
    def _actual_priority_risk_if_ignored_zh(metric: str) -> str:
        risks = {
            "order_delay": "如果不处理，订单可能从计划确认事项变成当天交付恢复问题。",
            "machine_style_mismatch": "如果不处理，现场可能在调机、返工或换机台上损失时间，直到问题被动暴露。",
            "unscheduled_weaving_part_order": "如果不处理，未排满部件单会悄悄消耗交付 buffer，并把恢复压力推到后段。",
            "quantity_report_gap": "如果不处理，计划/报工差异可能掩盖返工、拆分任务或进度可视化不准。",
            "machine_plan_load": "如果不处理，即使总产能看似足够，负载集中也可能形成瓶颈。",
        }
        return risks.get(metric, "如果不处理，该风险可能在没有负责人确认的情况下反复出现。")

    @staticmethod
    def _actual_priority_kpi_links(metric: str) -> list[str]:
        links = {
            "order_delay": ["order_delay_risk", "plan_completion_rate", "unscheduled_weaving_part_order_count"],
            "machine_style_mismatch": ["machine_style_spec_mismatch_candidate_count", "setup_risk", "downtime_minutes"],
            "unscheduled_weaving_part_order": ["unscheduled_weaving_part_order_count", "capacity_occupation", "order_delay_risk"],
            "quantity_report_gap": ["manual_report_completion_rate", "planned_quantity", "reported_quantity"],
            "machine_plan_load": ["machine_plan_load_candidate_count", "capacity_occupation", "machine_load"],
        }
        return links.get(metric, ["actual_data_evidence_chain_coverage"])

    @staticmethod
    def _affected_objects_from_actual_chain(chain: dict) -> dict:
        return {
            "orders": [chain.get("produce_order_code")] if chain.get("produce_order_code") else [],
            "machines": [item for item in [chain.get("machine_code"), chain.get("machine_id"), *(chain.get("machine_ids") or [])] if item],
            "weaving_part_order_ids": [item for item in [chain.get("weaving_part_order_id"), *(chain.get("weaving_part_order_ids") or [])] if item],
            "planned_task_ids": [item for item in [chain.get("planned_task_id"), *(chain.get("planned_task_ids") or [])] if item],
            "styles": [chain.get("sku_code")] if chain.get("sku_code") else [],
            "process_stages": [chain.get("part")] if chain.get("part") else [],
        }

    @staticmethod
    def _actual_evidence_claims(evidence_refs: list[str], analysis: dict, chain: dict) -> list[dict]:
        return [
            {
                "evidence_ref": ref,
                "claim": analysis.get("answer_summary", ""),
                "source": chain.get("field_source", "Tianpai APS Export"),
                "adapter_status": "read_only_external_csv",
            }
            for ref in evidence_refs
        ]

    def _prd_alignment_audit(
        self,
        management_priority_brief: dict,
        decision_loop: dict,
        mvp_demo_story: dict,
        mvp_success_check: dict,
        permission_boundary: dict,
        service_escalations: list[dict],
        data_readiness: dict,
        material_risk: dict,
        general_manager_question_bank: dict,
    ) -> dict:
        section_checks = [
            {
                "section": "1. Product Definition",
                "status": "covered",
                "implemented_by": ["workflow_template.positioning", "management_priority_brief", "production.html"],
                "evidence_refs": [management_priority_brief.get("brief_id", "")],
                "remaining_gap": "Real customer deployment value still needs Tianpai general-manager review.",
            },
            {
                "section": "2. Core User",
                "status": "covered_with_gaps",
                "implemented_by": ["management_priority_brief.audience", "general_manager_question_bank"],
                "evidence_refs": [general_manager_question_bank.get("schema_id", "")],
                "remaining_gap": "Question bank is still a hypothesis until verified by customer management.",
            },
            {
                "section": "3. Core Problem",
                "status": "covered",
                "implemented_by": ["data_readiness", "evidence_log", "production_object_model"],
                "evidence_refs": [data_readiness.get("schema_id", "")],
                "remaining_gap": "Local mock data proves the structure, not the customer's full data reality.",
            },
            {
                "section": "4. Value Proposition",
                "status": "covered",
                "implemented_by": ["management_priority_brief", "decision_loop", "permission_boundary"],
                "evidence_refs": [
                    management_priority_brief.get("brief_id", ""),
                    decision_loop.get("schema_id", ""),
                ],
                "remaining_gap": "Business value should be measured after real order, service, and quality data are connected.",
            },
            {
                "section": "5. Product Scope",
                "status": "covered",
                "implemented_by": ["workflow_template.workflow", "service_escalations", "chatbi_root_cause_analysis"],
                "evidence_refs": [item.get("candidate_id", "") for item in service_escalations[:3]],
                "remaining_gap": "MVP is limited to Production and Service; finance, CRM, and customer customization remain out of scope.",
            },
            {
                "section": "6. Hero Question",
                "status": "covered",
                "implemented_by": ["management_priority_brief.top_priorities", "gmThreeMinuteBrief panel"],
                "evidence_refs": [item.get("priority_id", "") for item in management_priority_brief.get("top_priorities", [])],
                "remaining_gap": "Priority quality depends on real order, quality, labor, and service data quality.",
            },
            {
                "section": "7. Decision Boundary",
                "status": "covered",
                "implemented_by": ["permission_boundary", "decision_loop.follow_up_items"],
                "evidence_refs": [permission_boundary.get("schema_id", "")],
                "remaining_gap": "Athena suggests confirmation owners; it does not replace the general manager.",
            },
            {
                "section": "8. Explicit Non-Goals",
                "status": "covered",
                "implemented_by": ["workflow_instance.blocked_actions", "permission_boundary.blocked_actions"],
                "evidence_refs": permission_boundary.get("blocked_actions", [])[:6],
                "remaining_gap": "Future integrations must preserve these blocked actions unless the PRD is updated.",
            },
            {
                "section": "9. User Experience Principle",
                "status": "covered",
                "implemented_by": ["gmThreeMinuteBrief", "productionSummary", "mvp_success_check"],
                "evidence_refs": [mvp_success_check.get("check_id", "")],
                "remaining_gap": "Usability still needs customer observation with a real manager.",
            },
            {
                "section": "10. Customer Segment",
                "status": "covered_with_gaps",
                "implemented_by": ["data_readiness.source_status", "adapter_contract"],
                "evidence_refs": [item.get("request_id", "") for item in data_readiness.get("next_data_requests", [])[:2]],
                "remaining_gap": "Demo is generalized from Tianpai-like workflow, but customer-specific field mapping is pending.",
            },
            {
                "section": "11. Risk Priority Policy",
                "status": "covered",
                "implemented_by": ["management_priority_brief.priority_policy"],
                "evidence_refs": [management_priority_brief.get("brief_id", "")],
                "remaining_gap": "Weights may need customer tuning after real operation review.",
            },
            {
                "section": "12. Core Data Objects",
                "status": "covered_with_gaps",
                "implemented_by": ["production_object_model", "material_risk", "data_readiness"],
                "evidence_refs": [material_risk.get("schema_id", ""), data_readiness.get("schema_id", "")],
                "remaining_gap": "ERP order data and historical labor baselines are not available yet.",
            },
            {
                "section": "13. Core Questions",
                "status": "covered_with_gaps",
                "implemented_by": ["general_manager_question_bank", "Santoni Athena panel"],
                "evidence_refs": [general_manager_question_bank.get("schema_id", "")],
                "remaining_gap": "Question set is not yet verified by the general manager.",
            },
            {
                "section": "14. Service Extension",
                "status": "covered_with_gaps",
                "implemented_by": ["service_escalations", "first_screen_service_risk", "serviceRiskBrief"],
                "evidence_refs": [item.get("evidence_ref", "") for item in service_escalations[:3]],
                "remaining_gap": "Service suggestions are candidates only; no real dispatch or service system integration.",
            },
            {
                "section": "15. Follow-up / Action Loop",
                "status": "covered",
                "implemented_by": ["decision_loop", "production_follow_up_reviews.json"],
                "evidence_refs": [item.get("follow_up_id", "") for item in decision_loop.get("follow_up_items", [])],
                "remaining_gap": "Follow-up state is local metadata, not a customer workflow system.",
            },
            {
                "section": "16. MVP Demo Story",
                "status": "covered",
                "implemented_by": ["mvp_demo_story", "mvpDemoStory panel"],
                "evidence_refs": [mvp_demo_story.get("story_id", "")],
                "remaining_gap": "Story should be refined after the manager-demo script is tested.",
            },
            {
                "section": "17. Success Criteria",
                "status": "covered",
                "implemented_by": ["mvp_success_check", "mvpSuccessCheck panel"],
                "evidence_refs": [mvp_success_check.get("check_id", "")],
                "remaining_gap": "Current pass is for Level 1 local mock evidence only.",
            },
            {
                "section": "18. Open Questions For Later PRD Versions",
                "status": "open_by_design",
                "implemented_by": ["data_readiness.next_data_requests", "prd_alignment_audit.remaining_open_questions"],
                "evidence_refs": [item.get("request_id", "") for item in data_readiness.get("next_data_requests", [])],
                "remaining_gap": "These questions intentionally remain for later PRD versions and customer-data negotiation.",
            },
        ]
        covered_count = len([item for item in section_checks if item["status"] in {"covered", "covered_with_gaps"}])
        total_count = len(section_checks)

        return {
            "schema_id": "athena.production_prd_alignment_audit.v1",
            "version": PRODUCTION_VERSION,
            "audit_id": f"PRD-ALIGNMENT-{PRODUCTION_VERSION}-CURRENT",
            "source_prd": "docs/product/athena_prd_v0.1.md",
            "coverage_status": "local_mvp_prd_covered_with_mock_and_open_data_boundaries",
            "coverage_score": round(covered_count / total_count, 2) if total_count else 0,
            "section_checks": section_checks,
            "core_loop_coverage": [
                "general_manager_question_to_priority_brief",
                "priority_brief_to_evidence",
                "evidence_to_recommended_owner_confirmation",
                "recommended_action_to_local_follow_up",
                "follow_up_to_memory_event_candidate",
                "service_risk_to_service_request_candidate",
            ],
            "remaining_open_questions": [
                "ERP order fields and Tianpai order flow still need customer confirmation.",
                "Historical labor effective-hour baseline is not connected.",
                "Quality and downstream garment process records are still mock or planned.",
                "General manager question bank still needs VOC verification.",
                "Live APS/IOT/database adapters are not connected.",
            ],
            "blocked_completion_claim": (
                "This audit proves local mock PRD coverage for the demo; it does not prove live customer "
                "deployment readiness."
            ),
            "read_only": True,
        }

    def _build_result(self, data: dict, filters: dict, scenario: str | None) -> dict:
        overview = self._production_overview(data)
        stages = self._workflow_stages(data)
        resource_lens = self._resource_lens(data)
        service_escalations = self._service_escalations(data)
        optimization_signals = self._optimization_signals(data, resource_lens, service_escalations)
        garment_output = self._garment_output(data)
        production_object_model = self._production_object_model()
        material_risk = self._material_risk(data)
        general_manager_question_bank = self._general_manager_question_bank(data)
        data_readiness = self._data_readiness(data, material_risk, general_manager_question_bank)
        tianpai_adapter = self.tianpai_aps_erp_export_adapter()
        tianpai_aps_erp_export = tianpai_adapter.report()
        evidence_review_queue = tianpai_adapter.delivery_evidence_review_queue(language="zh", limit=10)
        actual_priority_analyses = self._actual_management_priority_analyses(tianpai_adapter)
        management_priority_brief = self._management_priority_brief(
            data,
            overview,
            resource_lens,
            optimization_signals,
            service_escalations,
            garment_output,
            actual_priority_analyses,
        )
        if not evidence_review_queue.get("review_queue"):
            first_priority = (management_priority_brief.get("top_priorities") or [{}])[0]
            affected_objects = first_priority.get("affected_objects") or ["production_snapshot"]
            if isinstance(affected_objects, dict):
                affected_object = next(iter(affected_objects.values()), "production_snapshot")
            else:
                affected_object = affected_objects[0] if affected_objects else "production_snapshot"
            evidence_review_queue["review_queue"] = [
                {
                    "card_id": "EVIDENCE-REVIEW-FALLBACK-001",
                    "object_id": affected_object,
                    "review_type": "data_gap_confirmation",
                    "title": "Confirm data scope before final conclusion",
                    "why_not_delivery_risk": "No export-level reconciliation candidate is available in the current snapshot; Athena can only ask for data-scope confirmation.",
                    "evidence_credibility": "needs_reconciliation",
                    "suggested_confirmation_owner": "Planning / APS Owner",
                    "suggested_confirmation_action": "Confirm whether the current export includes closed orders, split tasks, and reporting-scope differences.",
                    "field_sources": first_priority.get("field_sources", []),
                    "evidence_refs": first_priority.get("evidence_refs", []),
                    "data_gaps": first_priority.get("data_gaps", []),
                    "read_only": True,
                    "local_follow_up_supported": True,
                    "mock_contract_fallback": True,
                }
            ]
            evidence_review_queue["review_count"] = 1
        decision_loop = self._decision_loop_follow_up(management_priority_brief)
        permission_boundary = self._permission_boundary()
        first_screen_service_risk = self._first_screen_service_risk(
            service_escalations,
            decision_loop,
            data.get("evidence_log", []),
        )
        decision_loop = self._extend_decision_loop_with_review_and_service(
            decision_loop,
            evidence_review_queue,
            first_screen_service_risk,
        )
        daily_brief_narrative = self._daily_brief_narrative(
            management_priority_brief,
            evidence_review_queue,
            first_screen_service_risk,
            decision_loop,
            permission_boundary,
        )
        mvp_demo_story = self._mvp_demo_story(
            management_priority_brief,
            decision_loop,
            service_escalations,
            permission_boundary,
        )
        mvp_success_check = self._mvp_success_check(
            management_priority_brief,
            decision_loop,
            mvp_demo_story,
            permission_boundary,
        )
        internal_demo_readiness_mode = self._internal_demo_readiness_mode(
            management_priority_brief,
            first_screen_service_risk,
            mvp_success_check,
            permission_boundary,
            data_readiness,
        )
        prd_alignment_audit = self._prd_alignment_audit(
            management_priority_brief,
            decision_loop,
            mvp_demo_story,
            mvp_success_check,
            permission_boundary,
            service_escalations,
            data_readiness,
            material_risk,
            general_manager_question_bank,
        )
        actual_data_snapshot = self._actual_data_snapshot(tianpai_aps_erp_export)
        stable_demo_story_pack = self._stable_demo_story_pack(
            management_priority_brief,
            first_screen_service_risk,
            actual_data_snapshot,
            material_risk,
            data_readiness,
            decision_loop,
        )
        internal_demo_candidate = self._demo_evolution_pack(
            management_priority_brief,
            stable_demo_story_pack,
            first_screen_service_risk,
            decision_loop,
            actual_data_snapshot,
            material_risk,
            data_readiness,
            permission_boundary,
        )
        kpi_log = self._kpi_log(overview, resource_lens, optimization_signals, tianpai_aps_erp_export)

        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": PRODUCTION_TEMPLATE_ID,
                "version": PRODUCTION_VERSION,
                "status": self._overall_status(overview, optimization_signals),
                "filters": filters,
                "scenario": scenario or "current_mock_snapshot",
                "read_only": True,
                "blocked_actions": [
                    "confirm_schedule",
                    "upload_co_file",
                    "upload_cx_file",
                    "release_order_to_machine",
                    "control_machine",
                    "create_real_service_ticket",
                    "modify_schedule_automatically",
                    "dispatch_service_automatically",
                    "replace_general_manager_decision",
                ],
            },
            "production_overview": overview,
            "production_object_model": production_object_model,
            "skill_registry": self.skill_registry(),
            "material_risk": material_risk,
            "data_readiness": data_readiness,
            "general_manager_question_bank": general_manager_question_bank,
            "management_priority_brief": management_priority_brief,
            "evidence_review_queue": evidence_review_queue,
            "decision_loop": decision_loop,
            "permission_boundary": permission_boundary,
            "first_screen_service_risk": first_screen_service_risk,
            "daily_brief_narrative": daily_brief_narrative,
            "mvp_demo_story": mvp_demo_story,
            "stable_demo_story_pack": stable_demo_story_pack,
            "guided_demo_flow": internal_demo_candidate["guided_demo_flow"],
            "user_page_gm_demo_entry": internal_demo_candidate["user_page_gm_demo_entry"],
            "presenter_mode": internal_demo_candidate["presenter_mode"],
            "evidence_boundary_layer": internal_demo_candidate["evidence_boundary_layer"],
            "gm_question_regression_set": internal_demo_candidate["gm_question_regression_set"],
            "data_request_wizard": internal_demo_candidate["data_request_wizard"],
            "service_risk_confirmation_flow": internal_demo_candidate["service_risk_confirmation_flow"],
            "visible_athena_skill_process": internal_demo_candidate["visible_athena_skill_process"],
            "hermes_training_memory_review": internal_demo_candidate["hermes_training_memory_review"],
            "internal_demo_candidate": internal_demo_candidate,
            "mvp_success_check": mvp_success_check,
            "internal_demo_readiness_mode": internal_demo_readiness_mode,
            "prd_alignment_audit": prd_alignment_audit,
            "tianpai_aps_erp_export": tianpai_aps_erp_export,
            "actual_data_snapshot": actual_data_snapshot,
            "workflow_stages": stages,
            "resource_lens": resource_lens,
            "optimization_signals": optimization_signals,
            "service_escalations": service_escalations,
            "garment_output": garment_output,
            "tool_interfaces": self.template()["adapter_contracts"],
            "adapter_contract": self.adapter_contract(),
            "data_source": self._data_source_metadata(),
            "workflow_primary_key": self.template()["workflow_primary_key"],
            "evidence_log": data.get("evidence_log", []),
            "kpi_log": kpi_log,
        }

    def _production_overview(self, data: dict) -> dict:
        orders = data.get("orders", [])
        machines = data.get("machines", [])
        materials = data.get("materials", [])
        labor = data.get("labor", [])
        measurements = data.get("measurement", [])
        inventory = data.get("tianpai_material_inventory", {})
        inventory_source = inventory.get("source_summary", {})
        inventory_balance = inventory.get("balance_summary", {})

        running_machines = [item for item in machines if item.get("state") == "running"]
        scheduled_orders = [item for item in orders if item.get("aps_status") == "scheduled"]
        pending_orders = [item for item in orders if item.get("aps_status") not in {"scheduled"}]
        exception_orders = [
            item for item in orders if item.get("erp_status") == "exception" or item.get("production_status") in {"blocked", "quality_hold"}
        ]
        average_oee = self._average([item.get("oee", 0) for item in machines if item.get("oee", 0) > 0])
        labor_efficiency = self._average([item.get("efficiency", 0) for item in labor])
        material_risks = [item for item in materials if item.get("risk") in {"medium", "high"}]
        quality_risks = [item for item in measurements if item.get("status") != "ok"]
        style_count = sum(int(item.get("style_count", 1)) for item in orders)
        remaining_quantity = sum(int(item.get("remaining_quantity", item.get("quantity", 0))) for item in orders)
        scheduled_quantity = sum(int(item.get("scheduled_quantity", 0)) for item in data.get("aps_schedule", []))
        capacity_occupation = self._average(
            [item.get("capacity_occupation_rate", 0) for item in data.get("aps_schedule", []) if item.get("capacity_occupation_rate") is not None]
        ) or self._ratio(len(running_machines), len(machines))
        fault_machines = [
            item for item in machines if item.get("state") == "stopped" or item.get("alarm") not in {"", None, "none"}
        ]
        offline_machines = [item for item in machines if item.get("iot_status") == "offline"]
        scrap_quantity = sum(int(item.get("scrap_quantity", 0)) for item in measurements)
        actual_output = sum(int(item.get("actual_output", 0)) for item in measurements)
        average_yield = self._average([item.get("yield_rate", 0) for item in measurements if item.get("yield_rate")])

        return {
            "order_count": len(orders),
            "backlog_order_count": len(orders),
            "total_style_count": style_count,
            "total_remaining_quantity": remaining_quantity,
            "scheduled_order_count": len(scheduled_orders),
            "scheduled_quantity": scheduled_quantity,
            "pending_or_exception_order_count": len(pending_orders),
            "exception_order_count": len(exception_orders),
            "machine_count": len(machines),
            "running_machine_count": len(running_machines),
            "machine_running_rate": self._ratio(len(running_machines), len(machines)),
            "capacity_occupation_rate": round(capacity_occupation, 3),
            "fault_machine_count": len(fault_machines),
            "offline_machine_count": len(offline_machines),
            "average_oee": round(average_oee, 3),
            "downtime_minutes": sum(int(item.get("downtime_minutes", 0)) for item in machines),
            "material_risk_count": len(material_risks),
            "material_inventory_row_count": inventory_source.get("row_count", 0),
            "material_inventory_task_order_count": inventory_source.get("unique_task_order_count", 0),
            "material_inventory_exception_rows": int(inventory_balance.get("zero_balance_rows", 0)) + int(inventory_balance.get("negative_balance_rows", 0)),
            "labor_efficiency": round(labor_efficiency, 3),
            "quality_risk_count": len(quality_risks),
            "average_yield_rate": round(average_yield, 3),
            "scrap_quantity": scrap_quantity,
            "scrap_rate": round(self._ratio(scrap_quantity, actual_output + scrap_quantity), 3),
            "service_escalation_count": len(self._service_escalations(data)),
        }

    def _workflow_stages(self, data: dict) -> list[dict]:
        orders = data.get("orders", [])
        schedules = data.get("aps_schedule", [])
        machines = data.get("machines", [])
        measurements = data.get("measurement", [])
        stage_status = {
            "order_intake": "attention" if any(order.get("erp_status") == "exception" for order in orders) else "ok",
            "erp_input": "attention" if any(order.get("erp_status") == "exception" for order in orders) else "ok",
            "aps_scheduling": "attention" if any(item.get("schedule_status") != "released" for item in schedules) else "ok",
            "iot_execution": "attention" if any(item.get("state") in {"stopped", "material_hold"} for item in machines) else "ok",
            "production_monitoring": "attention" if self._service_escalations(data) else "ok",
            "garment_output": "attention" if any(item.get("status") != "ok" for item in measurements) else "ok",
        }
        evidence = {
            "order_intake": "EV-PROD-001",
            "erp_input": "EV-PROD-004",
            "aps_scheduling": "EV-PROD-006",
            "iot_execution": "EV-PROD-010",
            "production_monitoring": "EV-PROD-018",
            "garment_output": "EV-PROD-024",
        }

        return [
            {
                **asdict(stage),
                "status": stage_status[stage.id],
                "evidence_ref": evidence[stage.id],
            }
            for stage in production_operations_template()["stages"]
            for stage in [ProductionStage(**stage)]
        ]

    def _resource_lens(self, data: dict) -> dict:
        labor = data.get("labor", [])
        machines = data.get("machines", [])
        materials = data.get("materials", [])
        process = data.get("process", [])
        environment = data.get("environment", [])
        measurement = data.get("measurement", [])

        return {
            "people": {
                "label": "People",
                "status": self._lens_status([item.get("risk") for item in labor]),
                "score": round(self._average([item.get("efficiency", 0) for item in labor]) * 100),
                "signals": [
                    {
                        "title": f"{item['team_id']} {item['role']}",
                        "detail": f"efficiency {item['efficiency']:.0%}, manual interventions {item['manual_interventions']}",
                        "risk": item["risk"],
                        "evidence_ref": item["evidence_ref"],
                    }
                    for item in labor
                ],
            },
            "machine": {
                "label": "Machine",
                "status": "attention" if any(item.get("state") in {"stopped", "material_hold"} for item in machines) else "ok",
                "score": round(self._average([item.get("oee", 0) for item in machines if item.get("oee", 0) > 0]) * 100),
                "signals": [
                    {
                        "title": f"{item['machine_id']} {item['state']}",
                        "detail": (
                            f"IOT {item.get('iot_status', item['state'])}, OEE {item['oee']:.0%}, "
                            f"time availability {item.get('time_availability_rate', 0):.0%}, "
                            f"performance {item.get('performance_availability_rate', 0):.0%}, "
                            f"scrap {item.get('scrap_quantity', 0)}, alarm {item['alarm'] or 'none'}"
                        ),
                        "risk": "high" if item.get("state") == "stopped" else "medium" if item.get("alarm") else "low",
                        "evidence_ref": item["evidence_ref"],
                    }
                    for item in machines
                ],
            },
            "material": {
                "label": "Material",
                "status": self._lens_status([item.get("risk") for item in materials]),
                "score": max(0, 100 - 30 * len([item for item in materials if item.get("risk") == "high"]) - 15 * len([item for item in materials if item.get("risk") == "medium"])),
                "signals": [
                    {
                        "title": f"{item['name']} lot {item['lot']}",
                        "detail": (
                            f"{item['status']}, demand {item.get('demand_kg', 0)} kg, "
                            f"stock {item['stock_kg']} kg, in transit {item.get('in_transit_kg', 0)} kg"
                        ),
                        "risk": item["risk"],
                        "evidence_ref": item["evidence_ref"],
                    }
                    for item in materials
                ],
            },
            "method": {
                "label": "Method",
                "status": self._lens_status([item.get("risk") for item in process]),
                "score": max(0, 100 - sum(int(item.get("changeover_variance_minutes", 0)) for item in process)),
                "signals": [
                    {
                        "title": item["process_id"],
                        "detail": (
                            f"{item['co_cx_policy']}, .co {item.get('co_file', 'reserved')}, "
                            f".cx {item.get('cx_file', 'reserved')}, setup {item['setup_minutes']} min, "
                            f"variance {item['changeover_variance_minutes']} min"
                        ),
                        "risk": item["risk"],
                        "evidence_ref": item["evidence_ref"],
                    }
                    for item in process
                ],
            },
            "environment": {
                "label": "Environment",
                "status": self._lens_status([item.get("risk") for item in environment]),
                "score": max(0, 100 - 15 * len([item for item in environment if item.get("risk") == "medium"])),
                "signals": [
                    {
                        "title": item["zone"],
                        "detail": f"{item['temperature_c']} C, {item['humidity_percent']}% RH, network {item['network_status']}",
                        "risk": item["risk"],
                        "evidence_ref": item["evidence_ref"],
                    }
                    for item in environment
                ],
            },
            "measurement": {
                "label": "Measurement",
                "status": "attention" if any(item.get("status") != "ok" for item in measurement) else "ok",
                "score": round(self._average([item.get("yield_rate", 0) for item in measurement]) * 100),
                "signals": [
                    {
                        "title": item["quality_id"],
                        "detail": (
                            f"yield {item['yield_rate']:.1%}, defect {item['defect_rate']:.1%}, "
                            f"actual output {item.get('actual_output', 0)}, scrap {item.get('scrap_quantity', 0)}, "
                            f"source {item['inspection_source']}"
                        ),
                        "risk": "medium" if item.get("status") != "ok" else "low",
                        "evidence_ref": item["evidence_ref"],
                    }
                    for item in measurement
                ],
            },
        }

    def _optimization_signals(self, data: dict, resource_lens: dict, service_escalations: list[dict]) -> list[dict]:
        signals = []
        for material in data.get("materials", []):
            if material.get("risk") in {"medium", "high"}:
                signals.append(
                    {
                        "type": "material_flow",
                        "title": f"Material risk for {material['name']}",
                        "severity": material["risk"],
                        "waste_or_cost_point": "machine waiting and planner rework",
                        "suggested_action": "Confirm APS yarn forecast demand, substitute lot, or resequence schedule before machine idle time expands.",
                        "evidence_ref": material["evidence_ref"],
                    }
                )
        for machine in data.get("machines", []):
            if machine.get("downtime_minutes", 0) >= 60:
                signals.append(
                    {
                        "type": "machine_downtime",
                        "title": f"{machine['machine_id']} downtime above threshold",
                        "severity": "high" if machine.get("state") == "stopped" else "medium",
                        "waste_or_cost_point": "lost machine hours",
                        "suggested_action": "Review IOT alarm, setup status, program evidence, and service request candidate before next shift.",
                        "evidence_ref": machine["evidence_ref"],
                    }
                )
        for lens_key, lens in resource_lens.items():
            if lens["status"] == "attention" and lens_key in {"people", "method", "measurement"}:
                signals.append(
                    {
                        "type": f"{lens_key}_optimization",
                        "title": f"{lens['label']} needs management attention",
                        "severity": "medium",
                        "waste_or_cost_point": "repeat manual work or quality rework",
                        "suggested_action": f"Use {lens['label']} evidence to identify the next improvement owner.",
                        "evidence_ref": lens["signals"][0]["evidence_ref"] if lens["signals"] else "EV-PROD-001",
                    }
                )
        for escalation in service_escalations:
            signals.append(
                {
                    "type": "service_recovery",
                    "title": escalation["issue"],
                    "severity": escalation["priority"],
                    "waste_or_cost_point": "production recovery lead time",
                    "suggested_action": "Prepare service case context, but do not auto-dispatch in Production MVP.",
                    "evidence_ref": escalation["evidence_ref"],
                }
            )
        return signals

    def _service_escalations(self, data: dict) -> list[dict]:
        escalations = []
        for machine in data.get("machines", []):
            if machine.get("state") == "stopped" or "tension" in machine.get("alarm", "").lower():
                escalations.append(
                    {
                        "candidate_id": f"SVC-CAND-{machine['machine_id']}",
                        "machine_id": machine["machine_id"],
                        "order_id": machine.get("order_id", ""),
                        "issue": machine.get("alarm") or "machine stopped",
                        "priority": "P1" if machine.get("state") == "stopped" else "P2",
                        "service_request_candidate": True,
                        "auto_dispatch": False,
                        "reason": "Production console can prepare context, but Service Manager or Service Agent must confirm dispatch.",
                        "evidence_ref": machine["evidence_ref"],
                    }
                )
        return escalations

    def _garment_output(self, data: dict) -> dict:
        orders = data.get("orders", [])
        measurements = {item["order_id"]: item for item in data.get("measurement", [])}
        output = []
        for order in orders:
            measurement = measurements.get(order["order_id"], {})
            produced = int(order["quantity"] * measurement.get("yield_rate", 0)) if measurement else 0
            output.append(
                {
                    "order_id": order["order_id"],
                    "style_code": order["style_code"],
                    "garment": order["garment"],
                    "planned_quantity": order["quantity"],
                    "remaining_quantity": order.get("remaining_quantity", order["quantity"]),
                    "estimated_good_quantity": produced,
                    "scrap_quantity": measurement.get("scrap_quantity", 0),
                    "defect_reasons": measurement.get("defect_reasons", []),
                    "status": "quality_hold" if measurement.get("status") == "warning" else order["production_status"],
                    "evidence_ref": measurement.get("evidence_ref", order["evidence_ref"]),
                }
            )
        return {
            "orders": output,
            "total_planned_quantity": sum(item["quantity"] for item in orders),
            "estimated_good_quantity": sum(item["estimated_good_quantity"] for item in output),
            "quality_hold_count": len([item for item in output if item["status"] == "quality_hold"]),
        }

    def _kpi_log(
        self,
        overview: dict,
        resource_lens: dict,
        optimization_signals: list[dict],
        tianpai_aps_erp_export: dict | None = None,
    ) -> list[dict]:
        actual_export_loaded = (tianpai_aps_erp_export or {}).get("adapter_status") == "read_only_external_csv"
        return [
            {
                "kpi": "oee",
                "value": overview["average_oee"],
                "target": 0.82,
                "status": "attention" if overview["average_oee"] < 0.82 else "ok",
                "evidence_ref": "EV-PROD-008",
            },
            {
                "kpi": "downtime_minutes",
                "value": overview["downtime_minutes"],
                "target": "< 120 per shift",
                "status": "attention" if overview["downtime_minutes"] >= 120 else "ok",
                "evidence_ref": "EV-PROD-010",
            },
            {
                "kpi": "order_delay_risk",
                "value": overview["pending_or_exception_order_count"],
                "target": 0,
                "status": "attention" if overview["pending_or_exception_order_count"] else "ok",
                "evidence_ref": "EV-PROD-004",
            },
            {
                "kpi": "material_risk",
                "value": overview["material_risk_count"],
                "target": 0,
                "status": "attention" if overview["material_risk_count"] else "ok",
                "evidence_ref": "EV-PROD-015",
            },
            {
                "kpi": "labor_efficiency",
                "value": overview["labor_efficiency"],
                "target": 0.85,
                "status": "attention" if overview["labor_efficiency"] < 0.85 else "ok",
                "evidence_ref": "EV-PROD-018",
            },
            {
                "kpi": "quality_risk",
                "value": overview["quality_risk_count"],
                "target": 0,
                "status": "attention" if overview["quality_risk_count"] else "ok",
                "evidence_ref": "EV-PROD-024",
            },
            {
                "kpi": "waste_cost_opportunity",
                "value": len(optimization_signals),
                "target": "review top 3 per shift",
                "status": "attention" if optimization_signals else "ok",
                "evidence_ref": optimization_signals[0]["evidence_ref"] if optimization_signals else "EV-PROD-001",
            },
            {
                "kpi": "capacity_occupation",
                "value": overview["capacity_occupation_rate"],
                "target": "review under 70% or over 95%",
                "status": "attention" if overview["capacity_occupation_rate"] < 0.7 or overview["capacity_occupation_rate"] > 0.95 else "ok",
                "evidence_ref": "EV-PROD-006",
            },
            {
                "kpi": "scrap_rate",
                "value": overview["scrap_rate"],
                "target": "< 3%",
                "status": "attention" if overview["scrap_rate"] >= 0.03 else "ok",
                "evidence_ref": "EV-PROD-024",
            },
            {
                "kpi": "adapter_contract_coverage",
                "value": 1.0,
                "target": "APS and IOT read-only source pages mapped",
                "status": "ok",
                "evidence_ref": "EV-PROD-025",
            },
            {
                "kpi": "management_priority_items",
                "value": 3 if optimization_signals else 0,
                "target": "top 3 evidence-backed priorities per review",
                "status": "attention" if optimization_signals else "ok",
                "evidence_ref": optimization_signals[0]["evidence_ref"] if optimization_signals else "EV-PROD-025",
            },
            {
                "kpi": "material_inventory_join_readiness",
                "value": 0.45,
                "target": "confirm produce_order_code, ERP order join, and BOM demand before shortage claims",
                "status": "attention",
                "evidence_ref": "EV-PROD-028",
            },
            {
                "kpi": "data_readiness_score",
                "value": 0.35,
                "target": "raise above 0.70 before claiming Tianpai end-to-end root cause",
                "status": "attention",
                "evidence_ref": "EV-PROD-027",
            },
            {
                "kpi": "question_bank_coverage",
                "value": "hypothesis_only",
                "target": "reviewed or approved by Product Owner, Agnes, and Tianpai roles",
                "status": "attention",
                "evidence_ref": "EV-PROD-027",
            },
            {
                "kpi": "mvp_demo_story_coverage",
                "value": 1.0,
                "target": "PRD section 16 story path visible in Production Console",
                "status": "ok",
                "evidence_ref": "MVP-DEMO-STORY",
            },
            {
                "kpi": "mvp_success_check_coverage",
                "value": 1.0,
                "target": "PRD section 17 success criteria visible in Production Console",
                "status": "ok",
                "evidence_ref": "MVP-SUCCESS-CHECK",
            },
            {
                "kpi": "prd_alignment_coverage",
                "value": 1.0,
                "target": "PRD sections 1-18 mapped to implementation, evidence, and remaining gaps",
                "status": "ok",
                "evidence_ref": "PRD-ALIGNMENT",
            },
            {
                "kpi": "tianpai_actual_export_readiness",
                "value": "loaded" if actual_export_loaded else "missing",
                "target": "read-only APS/ERP external CSV loaded with DDL field order",
                "status": "ok" if actual_export_loaded else "attention",
                "evidence_ref": "TIANPAI-APS-ERP-EXPORT",
            },
            {
                "kpi": "actual_data_evidence_chain_coverage",
                "value": "available" if actual_export_loaded else "blocked",
                "target": "supported management Q&A returns order, WPO, task, machine, evidence refs, and field source",
                "status": "ok" if actual_export_loaded else "attention",
                "evidence_ref": "TIANPAI-APS-ERP-EXPORT",
            },
            {
                "kpi": "skill_registry_coverage",
                "value": len(self.skill_registry().get("skills", [])),
                "target": "8 production skills registered for GM demo workflow",
                "status": "ok",
                "evidence_ref": "ATHENA-SKILL-REGISTRY",
            },
            {
                "kpi": "skill_execution_trace_coverage",
                "value": "available",
                "target": "risk cards and drilldown responses expose readable skill execution traces",
                "status": "ok",
                "evidence_ref": "ATHENA-SKILL-TRACE",
            },
            {
                "kpi": "permission_boundary_coverage",
                "value": 1.0,
                "target": "GM final-confirmation boundary visible in Production Console",
                "status": "ok",
                "evidence_ref": "PERMISSION-BOUNDARY",
            },
        ]

    def _chatbi_analysis(self, data: dict, result: dict, question: str) -> dict:
        language = "zh" if any("\u4e00" <= char <= "\u9fff" for char in question) else "en"
        metric = self._detect_chatbi_metric(question)
        if metric == "management_priority":
            return self._chatbi_management_priority(data, result, language)
        if metric == "data_gap":
            return self._chatbi_data_gap(data, result, language)
        if metric == "machine_bottleneck":
            return self._chatbi_machine_bottleneck(data, result, language)
        if metric == "scrap_rate":
            return self._chatbi_scrap_rate(data, result, language)
        if metric == "oee":
            return self._chatbi_oee(data, result, language)
        if metric == "downtime":
            return self._chatbi_downtime(data, result, language)
        if metric == "labor_efficiency":
            return self._chatbi_labor_efficiency(data, result, language)
        if metric == "material_risk":
            return self._chatbi_material_risk(data, result, language)
        if metric == "order_delay":
            return self._chatbi_order_delay(data, result, language)
        return self._chatbi_overall(data, result, language)

    def _detect_chatbi_metric(self, question: str) -> str:
        lowered = question.lower()
        priority_terms = ["top three", "three things", "priority", "daily brief", "general manager brief", "三件事", "先看", "优先", "总经理"]
        if any(token in lowered for token in priority_terms):
            return "management_priority"
        if any(token in lowered for token in ["data gap", "missing data", "what can't", "cannot answer", "不能回答", "数据缺口", "缺什么数据"]):
            return "data_gap"
        if (
            any(token in lowered for token in ["machine bottleneck", "machines are current bottlenecks", "worst machine", "machine ranking", "机台瓶颈", "机器瓶颈", "拖后腿"])
            or (any(token in lowered for token in ["machine", "machines", "机台", "机器"]) and any(token in lowered for token in ["bottleneck", "bottlenecks", "load", "负载", "瓶颈"]))
        ):
            return "machine_bottleneck"
        if any(token in lowered for token in ["scrap", "waste", "defect", "yield", "废弃", "废品", "不良", "良率", "质量"]):
            return "scrap_rate"
        if "oee" in lowered or "稼动率" in lowered or "开机率" in lowered:
            return "oee"
        if any(token in lowered for token in ["downtime", "停机", "故障", "报警"]):
            return "downtime"
        if any(token in lowered for token in ["labor", "effective hour", "effective-hour", "manual intervention", "team leader", "人工", "有效工时", "班组", "人工干预", "组长"]):
            return "labor_efficiency"
        if any(token in lowered for token in ["material", "yarn", "纱线", "物料", "库存", "缺料"]):
            return "material_risk"
        if any(token in lowered for token in ["delivery", "lead time", "order", "due", "shipment", "交付", "交期", "货期", "订单", "延期"]):
            return "order_delay"
        return "overview"
    def _chatbi_management_priority(self, data: dict, result: dict, language: str) -> dict:
        brief = result["management_priority_brief"]
        priorities = brief.get("top_priorities", [])
        root_causes = [
            {
                "rank": item["rank"],
                "category": "management_priority",
                "category_label": self._choose(language, "Management priority", "绠＄悊浼樺厛"),
                "cause": self._choose(language, item["title"], item.get("title_zh", item["title"])),
                "impact": {
                    "priority_id": item["priority_id"],
                    "priority": item["priority"],
                    "theme": item["management_theme"],
                    "affected_objects": item.get("affected_objects", {}),
                    "kpi_links": item.get("kpi_links", []),
                },
                "data_points": [
                    self._choose(language, item["reason"], item.get("reason_zh", item["reason"])),
                    self._choose(language, item["risk_if_ignored"], item.get("risk_if_ignored_zh", item["risk_if_ignored"])),
                    self._choose(language, item["recommended_action"], item.get("recommended_action_zh", item["recommended_action"])),
                ],
                "evidence_refs": item.get("evidence_refs", []),
            }
            for item in priorities
        ]
        headline = brief.get("daily_brief", {}).get("headline", "")
        return {
            "language": language,
            "metric": "management_priority",
            "answer_summary": self._choose(
                language,
                headline or "Athena ranks today's management attention from evidence-backed production risks.",
                "Athena 已根据当前证据生成今天总经理最应该先看的管理优先级。",
            ),
            "metric_snapshot": {
                "priority_count": len(priorities),
                "top_priority": priorities[0]["priority_id"] if priorities else "",
                "priority_policy": "delivery > quality > cost",
                "status": "attention" if priorities else "ok",
            },
            "root_causes": root_causes,
            "recommended_actions": [
                self._choose(language, item["recommended_action"], item.get("recommended_action_zh", item["recommended_action"]))
                for item in priorities
            ],
            "next_drilldowns": [
                self._choose(language, "Open the priority item by order_id, machine_id, evidence_refs, and owner role.", "Open the priority item by order_id, machine_id, evidence_refs, and owner role."),
                self._choose(language, "Convert the top priority into a follow-up item only after owner confirmation.", "Convert the top priority into a follow-up item only after owner confirmation."),
            ],
            "data_gaps": [item["gap"] for item in brief.get("data_gaps", [])],
            "management_priority_brief": brief,
            "decision_loop": result["decision_loop"],
            "confidence": "medium_high",
            "source_objects": ["management_priority_brief", "production_object_model", "evidence_log", "kpi_log"],
        }

    def _chatbi_data_gap(self, data: dict, result: dict, language: str) -> dict:
        gaps = [
            self._default_data_gaps(metric, language)[0]
            for metric in ["order_delay", "scrap_rate", "oee", "material_risk", "data_gap"]
        ]
        root_causes = [
            {
                "rank": index + 1,
                "category": "data_gap",
                "category_label": self._choose(language, "Data gap", "鏁版嵁缂哄彛"),
                "cause": gap,
                "impact": {
                    "decision_impact": self._choose(
                        language,
                        "Athena must avoid claiming this conclusion as proven until the missing data is connected.",
                        "在缺失数据接入前，Athena 不能把这个结论说成已证明事实。",
                    )
                },
                "data_points": [
                    self._choose(language, "Current demo remains read-only and mock-backed.", "当前 demo 仍是只读 mock 数据。")
                ],
                "evidence_refs": ["EV-PROD-025"],
            }
            for index, gap in enumerate(gaps)
        ]
        return {
            "language": language,
            "metric": "data_gap",
            "answer_summary": self._choose(
                language,
                "Athena can explain current mock order, machine, material, and quality signals, but cannot prove historical lead time, true per-garment cost, or full process bottlenecks yet.",
                "Athena 现在可以解释当前 mock 的订单、机台、物料和质量信号，但还不能证明历史货期、真实单件成本或全流程瓶颈。",
            ),
            "metric_snapshot": {
                "known_scope": self._choose(language, "mock orders, APS schedule, IOT-like machine snapshot, material and quality evidence", "mock 订单、APS 排单、类 IOT 机台快照、物料和质量证据"),
                "missing_scope_count": len(gaps),
                "status": "needs_real_data",
            },
            "root_causes": root_causes,
            "recommended_actions": [
                self._choose(language, "Prioritize APS-to-IOT order join and real delivery records before training delivery root cause.", "Prioritize APS-to-IOT order join and real delivery records before training delivery root cause."),
                self._choose(language, "Keep cost conclusions as unavailable until purchasing, labor, and per-order cost tables are connected.", "Keep cost conclusions as unavailable until purchasing, labor, and per-order cost tables are connected."),
            ],
            "next_drilldowns": [
                self._choose(language, "List required fields by KPI: delivery, quality, cost, machine efficiency, and process WIP.", "List required fields by KPI: delivery, quality, cost, machine efficiency, and process WIP.")
            ],
            "data_gaps": gaps,
            "confidence": "high",
            "source_objects": ["data_source", "adapter_contract", "training_pack", "evidence_log"],
        }

    def _chatbi_machine_bottleneck(self, data: dict, result: dict, language: str) -> dict:
        machines = sorted(
            data.get("machines", []),
            key=lambda item: (item.get("oee", 0), -int(item.get("downtime_minutes", 0)), -int(item.get("scrap_quantity", 0))),
        )
        top_machines = machines[:4]
        root_causes = [
            {
                "rank": index + 1,
                "category": "machine_bottleneck",
                "category_label": self._choose(language, "Machine bottleneck", "鏈哄彴鐡堕"),
                "cause": self._choose(
                    language,
                    f"{machine['machine_id']} is the strongest drag: OEE {machine.get('oee', 0):.0%}, downtime {machine.get('downtime_minutes', 0)} min, state {machine.get('state')}.",
                    f"{machine['machine_id']} 是当前最明显拖累项：OEE {machine.get('oee', 0):.0%}，停机 {machine.get('downtime_minutes', 0)} 分钟，状态 {machine.get('state')}。",
                ),
                "impact": {
                    "machine_id": machine["machine_id"],
                    "order_id": machine.get("order_id", ""),
                    "current_style_code": machine.get("current_style_code", ""),
                    "oee": machine.get("oee", 0),
                    "downtime_minutes": machine.get("downtime_minutes", 0),
                    "scrap_quantity": machine.get("scrap_quantity", 0),
                },
                "data_points": [
                    self._choose(language, f"Alarm {machine.get('alarm') or 'none'}", f"Alarm {machine.get('alarm') or 'none'}"),
                    self._choose(language, f".co/.cx {machine.get('co_file', '')} / {machine.get('cx_file', '')}", f".co/.cx {machine.get('co_file', '')} / {machine.get('cx_file', '')}"),
                ],
                "evidence_refs": [machine["evidence_ref"]],
            }
            for index, machine in enumerate(top_machines)
        ]
        worst = top_machines[0] if top_machines else {}
        return self._generic_chatbi_response(
            language,
            "machine_bottleneck",
            self._choose(
                language,
                f"{worst.get('machine_id', 'No machine')} is the current top machine bottleneck based on OEE, downtime, and scrap evidence.",
                f"{worst.get('machine_id', '暂无机台')} 是当前最需要关注的机台瓶颈，依据是 OEE、停机和废弃证据。",
            ),
            {
                "top_bottleneck_machine": worst.get("machine_id", ""),
                "oee": worst.get("oee", 0),
                "downtime_minutes": worst.get("downtime_minutes", 0),
                "scrap_quantity": worst.get("scrap_quantity", 0),
                "status": "attention",
            },
            root_causes,
            ["machines", "process", "measurement", "evidence_log"],
        )

    def _chatbi_scrap_rate(self, data: dict, result: dict, language: str) -> dict:
        overview = result["production_overview"]
        measurements = sorted(data.get("measurement", []), key=lambda item: item.get("scrap_quantity", 0), reverse=True)
        orders_by_id = {item["order_id"]: item for item in data.get("orders", [])}
        machines_by_order = self._group_by(data.get("machines", []), "order_id")
        process_by_order = self._group_by(data.get("process", []), "order_id")
        material_by_id = {item["material_id"]: item for item in data.get("materials", [])}
        total_scrap = sum(int(item.get("scrap_quantity", 0)) for item in measurements)
        total_actual = sum(int(item.get("actual_output", 0)) for item in measurements)
        root_causes = []

        for measurement in measurements:
            if not measurement.get("scrap_quantity"):
                continue
            order = orders_by_id.get(measurement["order_id"], {})
            machines = machines_by_order.get(measurement["order_id"], [])
            machine_ids = [item["machine_id"] for item in machines]
            share = self._ratio(int(measurement["scrap_quantity"]), total_scrap)
            root_causes.append(
                {
                    "rank": len(root_causes) + 1,
                    "category": "style_quality",
                    "category_label": self._choose(language, "Style / quality", "娆惧紡 / 璐ㄩ噺"),
                    "cause": self._choose(
                        language,
                        f"{order.get('style_code', measurement['order_id'])} contributes {share:.0%} of current scrap.",
                        f"{order.get('style_code', measurement['order_id'])} 贡献了当前废弃数量的 {share:.0%}。",
                    ),
                    "impact": {
                        "order_id": measurement["order_id"],
                        "style_code": order.get("style_code", ""),
                        "scrap_quantity": measurement.get("scrap_quantity", 0),
                        "scrap_share": share,
                        "defect_rate": measurement.get("defect_rate", 0),
                        "yield_rate": measurement.get("yield_rate", 0),
                    },
                    "data_points": [
                        self._choose(language, f"Defect rate {measurement.get('defect_rate', 0):.1%}", f"Defect rate {measurement.get('defect_rate', 0):.1%}"),
                        self._choose(language, f"Yield {measurement.get('yield_rate', 0):.1%}", f"Yield {measurement.get('yield_rate', 0):.1%}"),
                        self._choose(language, f"Machines {', '.join(machine_ids) or 'none'}", f"Machines {', '.join(machine_ids) or 'none'}"),
                        self._choose(language, f"Reasons: {', '.join(measurement.get('defect_reasons', []))}", f"Reasons: {', '.join(measurement.get('defect_reasons', []))}"),
                    ],
                    "evidence_refs": [measurement["evidence_ref"], *[item["evidence_ref"] for item in machines]],
                }
            )

        stopped_machines = [item for item in data.get("machines", []) if item.get("state") == "stopped" and item.get("scrap_quantity", 0)]
        for machine in stopped_machines:
            root_causes.append(
                {
                    "rank": len(root_causes) + 1,
                    "category": "machine",
                    "category_label": self._choose(language, "Machine", "鏈哄櫒"),
                    "cause": self._choose(
                        language,
                        f"{machine['machine_id']} is stopped with {machine.get('alarm')}; this is a direct machine-side scrap driver.",
                        f"{machine['machine_id']} 因 {machine.get('alarm')} 停机，是直接的机器侧废弃驱动因素。",
                    ),
                    "impact": {
                        "machine_id": machine["machine_id"],
                        "scrap_quantity": machine.get("scrap_quantity", 0),
                        "oee": machine.get("oee", 0),
                        "downtime_minutes": machine.get("downtime_minutes", 0),
                    },
                    "data_points": [
                        self._choose(language, f"OEE {machine.get('oee', 0):.0%}", f"OEE {machine.get('oee', 0):.0%}"),
                        self._choose(language, f"Downtime {machine.get('downtime_minutes', 0)} min", f"鍋滄満 {machine.get('downtime_minutes', 0)} 鍒嗛挓"),
                        self._choose(language, f".co {machine.get('co_file', '')}, .cx {machine.get('cx_file', '')}", f".co {machine.get('co_file', '')}，.cx {machine.get('cx_file', '')}"),
                    ],
                    "evidence_refs": [machine["evidence_ref"]],
                }
            )

        for order_id, process_items in process_by_order.items():
            for process in process_items:
                if process.get("risk") == "medium" or int(process.get("changeover_variance_minutes", 0)) >= 15:
                    root_causes.append(
                        {
                            "rank": len(root_causes) + 1,
                            "category": "method",
                            "category_label": self._choose(language, "Method / setup", "宸ヨ壓 / 璋冩満"),
                            "cause": self._choose(
                                language,
                                f"{process['process_id']} has setup variance {process.get('changeover_variance_minutes', 0)} min.",
                                f"{process['process_id']} 的调机偏差达到 {process.get('changeover_variance_minutes', 0)} 分钟。",
                            ),
                            "impact": {
                                "order_id": order_id,
                                "setup_minutes": process.get("setup_minutes", 0),
                                "changeover_variance_minutes": process.get("changeover_variance_minutes", 0),
                            },
                            "data_points": [
                                self._choose(language, f"Read-only .co/.cx evidence: {process.get('co_file', '')} / {process.get('cx_file', '')}", f"Read-only .co/.cx evidence: {process.get('co_file', '')} / {process.get('cx_file', '')}"),
                            ],
                            "evidence_refs": [process["evidence_ref"]],
                        }
                    )

        material_notes = []
        for order in orders_by_id.values():
            if order.get("production_status") not in {"running", "quality_hold"}:
                continue
            for material_ref in order.get("yarn_material_refs", []):
                material = material_by_id.get(material_ref)
                if material:
                    material_notes.append(f"{material['name']}:{material['risk']}")
        root_causes.append(
            {
                "rank": len(root_causes) + 1,
                "category": "material",
                "category_label": self._choose(language, "Material", "鐗╂枡"),
                "cause": self._choose(
                    language,
                    "Material is not the primary current scrap driver in this snapshot.",
                    "从当前快照看，物料不是本次废弃率升高的首要原因。",
                ),
                "impact": {
                    "causal_status": "not_primary_current_scrap_driver",
                    "running_order_material_risks": material_notes,
                },
                "data_points": [
                    self._choose(
                        language,
                        "High-risk elastane is linked to an order that has not started, while current scrap comes from running/quality-hold orders.",
                        "高风险纱线关联的是未开始订单；当前废弃主要来自运行中/质量暂停订单。",
                    )
                ],
                "evidence_refs": ["EV-PROD-015", "EV-PROD-024"],
            }
        )

        return {
            "language": language,
            "metric": "scrap_rate",
            "answer_summary": self._choose(
                language,
                f"Current scrap rate is about {overview['scrap_rate']:.0%}. The strongest evidence points to style/quality and machine/setup issues, not material as the primary current driver.",
                f"当前废弃率约 {overview['scrap_rate']:.0%}。最强证据指向款式质量与机器调机问题，物料不是当前废弃率的首要驱动因素。",
            ),
            "metric_snapshot": {
                "scrap_rate": overview["scrap_rate"],
                "scrap_quantity": overview["scrap_quantity"],
                "actual_output": total_actual,
                "target": "< 3%",
                "status": "attention" if overview["scrap_rate"] >= 0.03 else "ok",
            },
            "root_causes": root_causes,
            "recommended_actions": [
                self._choose(language, "Prioritize YOGA-BRA-240 / SM8-03 review before treating this as a general material issue.", "Prioritize YOGA-BRA-240 / SM8-03 review before treating this as a general material issue."),
                self._choose(language, "Check fabric tension variation, logo elasticity, setup variance, and .co/.cx evidence together.", "Check fabric tension variation, logo elasticity, setup variance, and .co/.cx evidence together."),
                self._choose(language, "Use the result as a service request candidate only after the production/service owner confirms.", "Use the result as a service request candidate only after the production/service owner confirms."),
            ],
            "next_drilldowns": [
                self._choose(language, "Break scrap by style and machine.", "Break scrap by style and machine."),
                self._choose(language, "Compare setup variance with defect reasons.", "Compare setup variance with defect reasons."),
                self._choose(language, "Check whether the same .co/.cx files behave differently across machines.", "Check whether the same .co/.cx files behave differently across machines."),
            ],
            "confidence": "medium_high",
            "source_objects": ["measurement", "machines", "process", "materials", "orders", "evidence_log"],
        }

    def _chatbi_oee(self, data: dict, result: dict, language: str) -> dict:
        overview = result["production_overview"]
        machines = sorted(data.get("machines", []), key=lambda item: item.get("oee", 0))
        low_machines = [item for item in machines if item.get("oee", 0) < 0.82]
        root_causes = [
            {
                "rank": index + 1,
                "category": "machine",
                "category_label": self._choose(language, "Machine", "鏈哄櫒"),
                "cause": self._choose(language, f"{machine['machine_id']} pulls OEE down.", f"{machine['machine_id']} pulls OEE down."),
                "impact": {
                    "machine_id": machine["machine_id"],
                    "oee": machine.get("oee", 0),
                    "state": machine.get("state", ""),
                    "downtime_minutes": machine.get("downtime_minutes", 0),
                },
                "data_points": [
                    self._choose(language, f"State {machine.get('state')}", f"State {machine.get('state')}"),
                    self._choose(language, f"Alarm {machine.get('alarm') or 'none'}", f"Alarm {machine.get('alarm') or 'none'}"),
                ],
                "evidence_refs": [machine["evidence_ref"]],
            }
            for index, machine in enumerate(low_machines[:4])
        ]
        return self._generic_chatbi_response(
            language,
            "oee",
            self._choose(language, f"Average OEE is {overview['average_oee']:.0%}, below the 82% target.", f"Average OEE is {overview['average_oee']:.0%}, below the 82% target."),
            {"average_oee": overview["average_oee"], "target": 0.82, "status": "attention"},
            root_causes,
            ["machines", "kpi_log", "evidence_log"],
        )

    def _chatbi_downtime(self, data: dict, result: dict, language: str) -> dict:
        overview = result["production_overview"]
        machines = sorted(data.get("machines", []), key=lambda item: item.get("downtime_minutes", 0), reverse=True)
        root_causes = [
            {
                "rank": index + 1,
                "category": "machine",
                "category_label": self._choose(language, "Machine downtime", "鏈哄櫒鍋滄満"),
                "cause": self._choose(language, f"{machine['machine_id']} contributes {machine.get('downtime_minutes', 0)} downtime minutes.", f"{machine['machine_id']} contributes {machine.get('downtime_minutes', 0)} downtime minutes."),
                "impact": {
                    "machine_id": machine["machine_id"],
                    "downtime_minutes": machine.get("downtime_minutes", 0),
                    "state": machine.get("state", ""),
                },
                "data_points": [self._choose(language, f"Alarm {machine.get('alarm') or 'none'}", f"Alarm {machine.get('alarm') or 'none'}")],
                "evidence_refs": [machine["evidence_ref"]],
            }
            for index, machine in enumerate(machines[:4])
            if machine.get("downtime_minutes", 0)
        ]
        return self._generic_chatbi_response(
            language,
            "downtime",
            self._choose(language, f"Total downtime is {overview['downtime_minutes']} minutes; the top machines explain most of it.", f"Total downtime is {overview['downtime_minutes']} minutes; the top machines explain most of it."),
            {"downtime_minutes": overview["downtime_minutes"], "target": "< 120 per shift", "status": "attention"},
            root_causes,
            ["machines", "evidence_log"],
        )

    def _chatbi_labor_efficiency(self, data: dict, result: dict, language: str) -> dict:
        overview = result["production_overview"]
        labor = sorted(
            data.get("labor", []),
            key=lambda item: (float(item.get("efficiency", 1)), -int(item.get("manual_interventions", 0))),
        )
        service_escalations = result.get("service_escalations", [])
        root_causes = [
            {
                "rank": index + 1,
                "category": "labor",
                "category_label": self._choose(language, "Labor effective hours", "浜哄伐鏈夋晥宸ユ椂"),
                "cause": self._choose(
                    language,
                    f"{item['team_id']} efficiency is {item.get('efficiency', 0):.0%} with {item.get('manual_interventions', 0)} manual interventions.",
                    f"{item['team_id']} efficiency is {item.get('efficiency', 0):.0%} with {item.get('manual_interventions', 0)} manual interventions.",
                ),
                "impact": {
                    "team_id": item["team_id"],
                    "role": item.get("role", ""),
                    "planned_hours": item.get("planned_hours", 0),
                    "actual_hours": item.get("actual_hours", 0),
                    "efficiency": item.get("efficiency", 0),
                    "manual_interventions": item.get("manual_interventions", 0),
                    "linked_service_candidates": [case.get("candidate_id") for case in service_escalations],
                },
                "data_points": [
                    self._choose(language, f"Risk {item.get('risk', '')}", f"椋庨櫓 {item.get('risk', '')}"),
                    self._choose(language, "Current MVP uses current-shift mock evidence, not a historical baseline.", "Current MVP uses current-shift mock evidence, not a historical baseline."),
                ],
                "evidence_refs": [item["evidence_ref"]],
            }
            for index, item in enumerate(labor[:4])
            if item.get("risk") != "low" or item.get("efficiency", 1) < 0.9
        ]
        return self._generic_chatbi_response(
            language,
            "labor_efficiency",
            self._choose(
                language,
                f"Average labor efficiency is {overview['labor_efficiency']:.0%}; the first review should confirm whether low effective hours come from service, setup, waiting, or rework.",
                f"Average labor efficiency is {overview['labor_efficiency']:.0%}; the first review should confirm whether low effective hours come from service, setup, waiting, or rework.",
            ),
            {
                "labor_efficiency": overview["labor_efficiency"],
                "target": ">= 85%",
                "status": "attention" if overview["labor_efficiency"] < 0.85 else "monitor",
            },
            root_causes,
            ["labor", "service_escalations", "machines", "evidence_log"],
        )

    def _chatbi_material_risk(self, data: dict, result: dict, language: str) -> dict:
        overview = result["production_overview"]
        materials = sorted(data.get("materials", []), key=lambda item: {"high": 0, "medium": 1, "low": 2}.get(item.get("risk"), 3))
        root_causes = [
            {
                "rank": index + 1,
                "category": "material",
                "category_label": self._choose(language, "Material", "鐗╂枡"),
                "cause": self._choose(language, f"{material['name']} lot {material['lot']} is {material['risk']} risk.", f"{material['name']} lot {material['lot']} is {material['risk']} risk."),
                "impact": {
                    "material_id": material["material_id"],
                    "risk": material["risk"],
                    "demand_kg": material.get("demand_kg", 0),
                    "stock_kg": material.get("stock_kg", 0),
                    "in_transit_kg": material.get("in_transit_kg", 0),
                    "required_orders": material.get("required_orders", []),
                },
                "data_points": [
                    self._choose(language, f"Demand {material.get('demand_kg', 0)} kg, stock {material.get('stock_kg', 0)} kg", f"Demand {material.get('demand_kg', 0)} kg, stock {material.get('stock_kg', 0)} kg"),
                ],
                "evidence_refs": [material["evidence_ref"]],
            }
            for index, material in enumerate(materials[:4])
            if material.get("risk") in {"medium", "high"}
        ]
        return self._generic_chatbi_response(
            language,
            "material_risk",
            self._choose(language, f"There are {overview['material_risk_count']} material risk items; elastane is the highest risk.", f"There are {overview['material_risk_count']} material risk items; elastane is the highest risk."),
            {"material_risk_count": overview["material_risk_count"], "target": 0, "status": "attention"},
            root_causes,
            ["materials", "orders", "aps_schedule", "evidence_log"],
        )

    def _chatbi_order_delay(self, data: dict, result: dict, language: str) -> dict:
        overview = result["production_overview"]
        all_orders = data.get("orders", [])
        snapshot_day = self._safe_date(data.get("factory", {}).get("snapshot_time", "")[:10])
        due_offsets = []
        for order in all_orders:
            due_day = self._safe_date(order.get("due_date", ""))
            if not snapshot_day or not due_day:
                continue
            due_offsets.append(
                {
                    "order_id": order["order_id"],
                    "due_date": order.get("due_date", ""),
                    "days_to_due": (due_day - snapshot_day).days,
                    "aps_status": order.get("aps_status", ""),
                    "erp_status": order.get("erp_status", ""),
                    "remaining_quantity": order.get("remaining_quantity", 0),
                    "evidence_ref": order.get("evidence_ref", ""),
                }
            )
        average_days_to_due = round(sum(item["days_to_due"] for item in due_offsets) / len(due_offsets), 1) if due_offsets else None
        earliest_due_date = min((item["due_date"] for item in due_offsets), default="")
        latest_due_date = max((item["due_date"] for item in due_offsets), default="")
        risky_orders = [
            item for item in data.get("orders", [])
            if item.get("aps_status") != "scheduled" or item.get("erp_status") == "exception"
        ]
        due_by_order = {item["order_id"]: item for item in due_offsets}
        root_causes = [
            {
                "rank": index + 1,
                "category": "order_schedule",
                "category_label": self._choose(language, "Order / schedule", "订单 / 排单"),
                "cause": self._choose(language, f"{order['order_id']} is {order.get('aps_status')}.", f"{order['order_id']} 褰撳墠鐘舵€佷负 {order.get('aps_status')}"),
                "impact": {
                    "order_id": order["order_id"],
                    "style_code": order.get("style_code", ""),
                    "remaining_quantity": order.get("remaining_quantity", 0),
                    "erp_status": order.get("erp_status", ""),
                    "aps_status": order.get("aps_status", ""),
                    "due_date": order.get("due_date", ""),
                    "days_to_due": due_by_order.get(order["order_id"], {}).get("days_to_due"),
                },
                "data_points": [
                    self._choose(language, f"Remaining quantity {order.get('remaining_quantity', 0)}", f"鍓╀綑鏁伴噺 {order.get('remaining_quantity', 0)}"),
                    self._choose(language, f"Due date {order.get('due_date', 'unknown')}", f"浜ゆ湡 {order.get('due_date', '鏈煡')}"),
                ],
                "evidence_refs": [order["evidence_ref"]],
            }
            for index, order in enumerate(risky_orders)
        ]
        return self._generic_chatbi_response(
            language,
            "order_delay",
            self._choose(
                language,
                f"Current backlog has an average {average_days_to_due} days until due date; {overview['pending_or_exception_order_count']} orders still need scheduling or exception review.",
                f"当前订单 backlog 距离交期平均还有 {average_days_to_due} 天；{overview['pending_or_exception_order_count']} 个订单仍需要排单或异常复核。",
            ),
            {
                "average_days_to_due": average_days_to_due,
                "earliest_due_date": earliest_due_date,
                "latest_due_date": latest_due_date,
                "pending_or_exception_order_count": overview["pending_or_exception_order_count"],
                "target": 0,
                "status": "attention",
                "data_boundary": self._choose(
                    language,
                    "This is not a real one-week historical average lead time because mock data has due_date but no order-created date or actual delivery records.",
                    "这不是真实近一周历史平均货期；当前 mock 只有 due_date，没有接单日期和实际交货记录。",
                ),
            },
            root_causes,
            ["orders", "aps_schedule", "materials", "evidence_log"],
        )

    @staticmethod
    def _safe_date(value: str) -> date | None:
        try:
            return date.fromisoformat(value)
        except (TypeError, ValueError):
            return None

    def _chatbi_overall(self, data: dict, result: dict, language: str) -> dict:
        root_causes = [
            {
                "rank": index + 1,
                "category": signal["type"],
                "category_label": self._choose(language, "Optimization signal", "浼樺寲淇″彿"),
                "cause": signal["title"],
                "impact": {
                    "severity": signal["severity"],
                    "waste_or_cost_point": signal["waste_or_cost_point"],
                },
                "data_points": [signal["suggested_action"]],
                "evidence_refs": [signal["evidence_ref"]],
            }
            for index, signal in enumerate(result.get("optimization_signals", [])[:5])
        ]
        return self._generic_chatbi_response(
            language,
            "overall",
            self._choose(language, "The current snapshot needs attention across machine downtime, material flow, and quality measurement.", "The current snapshot needs attention across machine downtime, material flow, and quality measurement."),
            result["production_overview"],
            root_causes,
            ["production_overview", "optimization_signals", "evidence_log"],
        )

    def _generic_chatbi_response(
        self,
        language: str,
        metric: str,
        answer_summary: str,
        metric_snapshot: dict,
        root_causes: list[dict],
        source_objects: list[str],
    ) -> dict:
        return {
            "language": language,
            "metric": metric,
            "answer_summary": answer_summary,
            "metric_snapshot": metric_snapshot,
            "root_causes": root_causes,
            "recommended_actions": [
                self._choose(language, "Review the top evidence-linked cause before changing schedules or machine settings.", "Review the top evidence-linked cause before changing schedules or machine settings."),
                self._choose(language, "Keep this analysis read-only and ask the production owner to confirm before action.", "Keep this analysis read-only and ask the production owner to confirm before action."),
            ],
            "next_drilldowns": [
                self._choose(language, "Drill down by order, style, machine, material lot, and shift.", "Drill down by order, style, machine, material lot, and shift."),
            ],
            "confidence": "medium",
            "source_objects": source_objects,
        }

    def _with_management_template(self, analysis: dict) -> dict:
        language = analysis.get("language", "en")
        metric = analysis.get("metric", "overall")
        root_causes = analysis.get("root_causes", [])
        recommended_actions = analysis.get("recommended_actions", [])
        data_gaps = analysis.get("data_gaps") or self._default_data_gaps(metric, language)
        top_cause = root_causes[0] if root_causes else {}
        evidence_refs = top_cause.get("evidence_refs", [])
        reason_evidence = self._choose(
            language,
            f"{top_cause.get('cause', 'No evidence-backed root cause yet.')} Evidence: {', '.join(evidence_refs) or 'none'}",
            f"{top_cause.get('cause', 'No evidence-backed root cause yet.')} Evidence: {', '.join(evidence_refs) or 'none'}",
        )
        analysis["data_gaps"] = data_gaps
        analysis["executive_answer"] = {
            "template": self._choose(
                language,
                "Conclusion + reason/evidence + risk + recommendation + data gap",
                "缁撹 + 鍘熷洜/璇佹嵁 + 椋庨櫓 + 寤鸿 + 鏁版嵁缂哄彛",
            ),
            "conclusion": analysis.get("answer_summary", ""),
            "reason_evidence": reason_evidence,
            "risk": self._management_risk_sentence(analysis, language),
            "recommendation": recommended_actions[0] if recommended_actions else self._choose(
                language,
                "Ask the production owner to confirm the evidence before action.",
                "行动前请生产负责人先确认证据。",
            ),
            "data_gap": data_gaps[0] if data_gaps else self._choose(language, "No major data gap for this mock answer.", "No major data gap for this mock answer."),
        }
        return analysis

    def _management_risk_sentence(self, analysis: dict, language: str) -> str:
        snapshot = analysis.get("metric_snapshot", {})
        status = snapshot.get("status", "")
        metric = analysis.get("metric", "")
        if status in {"attention", "needs_real_data"}:
            return self._choose(
                language,
                f"Risk is attention-level for {metric}; review before schedule, service, or cost decisions.",
                f"{metric} 当前是需要关注级别；排单、服务或成本决策前要先复核。",
            )
        return self._choose(
            language,
            f"Risk is monitor-level for {metric}; keep tracking evidence before operational changes.",
            f"{metric} 当前是持续观察级别；操作调整前继续跟踪证据。",
        )

    def _default_data_gaps(self, metric: str, language: str) -> list[str]:
        gaps = {
            "order_delay": (
                "True recent-week average lead time still needs order-created dates, shipment dates, and actual delivery records.",
                "真实近一周平均货期仍需要接单日期、出货日期和实际交货记录。",
            ),
            "scrap_rate": (
                "Scrap root cause will be stronger after real defect inspection rows, yarn lot traceability, and operator/shift history are connected.",
                "接入真实检验明细、纱线批次追溯和班组/班次记录后，废弃率根因会更可靠。",
            ),
            "oee": (
                "OEE explanation still needs real shift history, planned downtime, and machine maintenance records.",
                "OEE 解释仍需要真实班次历史、计划停机和机台保养记录。",
            ),
            "downtime": (
                "Downtime explanation still needs alarm duration history, maintenance response time, and service closure records.",
                "停机解释仍需要报警持续时间、维修响应时间和服务关闭记录。",
            ),
            "material_risk": (
                "Material risk explanation still needs purchasing ETA, warehouse movement, and supplier confirmation records.",
                "物料风险解释仍需要采购 ETA、仓库流转和供应商确认记录。",
            ),
            "machine_bottleneck": (
                "Machine bottleneck ranking still needs longer IOT history and comparable style/machine workload normalization.",
                "机台瓶颈排名仍需要更长 IOT 历史，以及款式/机台负载的可比归一化。",
            ),
            "data_gap": (
                "Full production root cause still needs APS-to-IOT order join, real delivery records, cost tables, and downstream process WIP/quality records.",
                "完整生产根因仍需要 APS 到 IOT 的订单关联、真实交付记录、成本表和后道工序在制/质量记录。",
            ),
            "overall": (
                "Overall management view still needs real APS/IOT/ERP joins before it can rank waste and cost with production-grade confidence.",
                "管理总览仍需要真实 APS/IOT/ERP 关联后，才能用生产级置信度排序浪费和成本。",
            ),
        }
        english, chinese = gaps.get(metric, gaps["overall"])
        return [self._choose(language, english, chinese)]

    def _group_by(self, items: list[dict], key: str) -> dict:
        grouped: dict[str, list[dict]] = {}
        for item in items:
            grouped.setdefault(item.get(key, ""), []).append(item)
        return grouped

    def _choose(self, language: str, english: str, chinese: str) -> str:
        return chinese if language == "zh" else english

    def _unique_refs(self, refs: list[str | None]) -> list[str]:
        seen = set()
        clean = []
        for ref in refs:
            if not ref or ref in seen:
                continue
            seen.add(ref)
            clean.append(ref)
        return clean

    def _evidence_claims(self, evidence_by_id: dict, refs: list[str]) -> list[dict]:
        return [
            {
                "evidence_ref": ref,
                "claim": evidence_by_id.get(ref, {}).get("claim", ""),
                "source": evidence_by_id.get(ref, {}).get("source", ""),
                "adapter_status": evidence_by_id.get(ref, {}).get("adapter_status", ""),
            }
            for ref in refs
        ]

    def _ensure_priority_card_contract(self, priority: dict) -> None:
        theme = priority.get("risk_theme") or priority.get("management_theme") or "cost"
        label_map = {
            "delivery": "浜や粯",
            "quality": "璐ㄩ噺",
            "cost": "鎴愭湰",
            "equipment": "璁惧",
            "labor": "浜哄伐",
            "material": "鐗╂枡",
        }
        priority.setdefault("risk_theme", theme)
        priority.setdefault("risk_theme_label", label_map.get(theme, theme))
        priority.setdefault("actual_evidence_chains", [])
        priority.setdefault("field_sources", self._field_sources_from_evidence_claims(priority.get("evidence_claims", [])))
        priority.setdefault("source_objects", ["mock_production_snapshot"])
        priority.setdefault("data_source_mode", "mock_snapshot_fallback")
        priority.setdefault("evidence_level", "Level 1: mock / demo evidence")
        priority.setdefault("internal_demo_ready", bool(priority.get("evidence_refs")))
        priority.setdefault("drilldown_question", "")
        priority.setdefault("demo_readiness_note", "Ready for internal demo if the owner treats the card as read-only evidence and confirms before action.")
        skills = production_skills_for_theme(theme)
        priority.setdefault(
            "skills_used",
            [
                {
                    "skill_id": skill["skill_id"],
                    "name_zh": skill["name_zh"],
                    "name_en": skill["name_en"],
                    "demo_status": skill["demo_status"],
                }
                for skill in skills
            ],
        )
        priority.setdefault("athena_checked", [skill["name_en"] for skill in skills])
        priority.setdefault("athena_checked_zh", [skill["name_zh"] for skill in skills])
        priority.setdefault("skill_execution_trace", production_skill_trace_for_priority(priority))
        action = priority.setdefault("action_candidate", {})
        action.setdefault("write_scope", "local_metadata_only")
        action.setdefault("linked_evidence_chain", (priority.get("actual_evidence_chains") or [{}])[0])
        action.setdefault("field_sources", priority.get("field_sources", []))
        action.setdefault("drilldown_question", priority.get("drilldown_question", ""))
        action.setdefault(
            "follow_up_contract",
            {
                "mode": "local_metadata_only",
                "writes_real_system": False,
                "blocked_systems": ["APS", "ERP", "IOT", "service_ticket", "machine_control"],
            },
        )

    @staticmethod
    def _field_sources_from_evidence_claims(claims: list[dict]) -> list[str]:
        sources = []
        for claim in claims:
            source = claim.get("source")
            if source and source not in sources:
                sources.append(source)
        return sources or ["mock production evidence"]

    @staticmethod
    def _safe_id(value: str) -> str:
        cleaned = "".join(char if char.isalnum() else "-" for char in str(value or "UNKNOWN")).strip("-")
        return cleaned.upper() or "UNKNOWN"

    @staticmethod
    def _related_object_from_priority(priority: dict) -> str:
        affected = priority.get("affected_objects", {}) or {}
        for key in ("orders", "machines", "materials", "styles", "weaving_part_order_ids", "planned_task_ids"):
            values = affected.get(key)
            if isinstance(values, list) and values:
                return str(values[0])
        chains = priority.get("actual_evidence_chains", []) or []
        if chains:
            chain = chains[0]
            return str(
                chain.get("produce_order_code")
                or chain.get("machine_id")
                or chain.get("weaving_part_order_id")
                or priority.get("priority_id")
            )
        return str(priority.get("priority_id", "unknown"))

    def _load_follow_up_store(self) -> dict:
        if not self.follow_up_store_path.exists():
            return {
                "schema": "athena.production_follow_up_reviews.v1",
                "version": PRODUCTION_VERSION,
                "reviews": [],
                "metadata_only": True,
            }
        loaded = json.loads(self.follow_up_store_path.read_text(encoding="utf-8"))
        loaded.setdefault("schema", "athena.production_follow_up_reviews.v1")
        loaded.setdefault("version", PRODUCTION_VERSION)
        loaded.setdefault("reviews", [])
        loaded.setdefault("metadata_only", True)
        return loaded

    def _save_follow_up_store(self, store: dict) -> None:
        self.follow_up_store_path.parent.mkdir(parents=True, exist_ok=True)
        self.follow_up_store_path.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _latest_follow_up_reviews_by_action(store: dict) -> dict:
        latest = {}
        for review in store.get("reviews", []):
            action_id = review.get("action_id")
            if action_id:
                latest[action_id] = review
        return latest

    @staticmethod
    def _reject_sensitive_review_text(field: str, value: str) -> None:
        lowered = value.lower()
        sensitive_markers = ["password", "api key", "apikey", "token", "secret", "1qaz"]
        if any(marker in lowered for marker in sensitive_markers):
            raise ValueError(f"{field} must not contain credentials, tokens, or passwords")

    @staticmethod
    def _follow_up_evidence_status(status: str, review: dict) -> str:
        if status == "resolved":
            return "resolved_with_local_metadata"
        if status == "dismissed":
            return "dismissed_by_general_manager"
        if status == "needs_more_data":
            return "waiting_additional_data"
        if status == "closed":
            return "accepted" if review.get("evidence_note") else "closed_without_full_evidence_note"
        if status == "confirmed":
            return "owner_confirmed_waiting_closure"
        if status == "waiting_evidence":
            return "waiting_evidence"
        if status == "assigned":
            return "owner_assigned"
        if status == "unable_to_process":
            return "blocked_by_owner"
        if status == "pending_confirmation":
            return "pending_general_manager_confirmation"
        return "needed"

    @staticmethod
    def _decision_status_from_follow_up(status: str) -> str:
        if status in {"closed", "unable_to_process", "resolved", "dismissed"}:
            return "reviewed"
        if status in {"assigned", "waiting_evidence", "confirmed", "needs_more_data"}:
            return "in_review"
        return "pending_confirmation"

    @staticmethod
    def _count_by(values: list[str]) -> dict:
        counts = {}
        for value in values:
            counts[value] = counts.get(value, 0) + 1
        return counts

    def _decision_loop_next_actions(self, status_counts: dict, follow_ups: list[dict]) -> list[str]:
        if not follow_ups:
            return ["No follow-up item is available until Athena produces management priorities."]
        if status_counts.get("dismissed"):
            return ["Review dismissed items and decide whether they should be archived or reopened with new evidence."]
        if status_counts.get("unable_to_process"):
            return ["Ask the general manager to decide whether unable_to_process items should be reassigned, escalated, or archived."]
        if status_counts.get("needs_more_data") or status_counts.get("waiting_evidence"):
            return ["Collect the expected evidence for waiting_evidence items before closing the loop."]
        if status_counts.get("closed", 0) + status_counts.get("resolved", 0) == len(follow_ups):
            return ["Review closed follow-ups and decide which memory-event candidates can be promoted to Hermes playbook review."]
        if status_counts.get("assigned") or status_counts.get("confirmed"):
            return ["Review assigned follow-ups at the next shift meeting and update evidence status."]
        return ["Ask the general manager to confirm or assign the top pending_confirmation item before the next shift review."]

    @staticmethod
    def _priority_action_candidate(action_id: str, owner_role: str, recommended_action: str, expected_evidence: list[str]) -> dict:
        return {
            "action_id": action_id,
            "owner_role": owner_role,
            "recommended_action": recommended_action,
            "requires_human_confirmation": True,
            "status": "pending_confirmation",
            "expected_evidence": expected_evidence,
            "blocked_automation": [
                "no_schedule_writeback",
                "no_machine_control",
                "no_auto_service_dispatch",
            ],
        }

    @staticmethod
    def _priority_risk_level(priority: dict) -> str:
        if not priority.get("evidence_refs"):
            return "gray"
        if priority.get("priority") in {"P0", "P1"}:
            return "red"
        return "yellow"

    @staticmethod
    def _priority_risk_level_label(risk_level: str) -> str:
        labels = {
            "red": "Red: must be confirmed today",
            "yellow": "Yellow: confirm within 24-48 hours",
            "gray": "Gray: insufficient data; visibility only",
        }
        return labels.get(risk_level, labels["gray"])

    @staticmethod
    def _management_headline(priorities: list[dict]) -> str:
        if not priorities:
            return "No evidence-backed management priority is available in the current snapshot."
        titles = [item.get("title", "") for item in priorities[:3]]
        return "Today's GM focus: " + " | ".join(title for title in titles if title)

    def _overall_status(self, overview: dict, signals: list[dict]) -> str:
        if overview["service_escalation_count"] or any(item.get("severity") in {"high", "P1"} for item in signals):
            return "attention_required"
        if signals:
            return "monitor"
        return "on_track"

    def _lens_status(self, risks: list[str]) -> str:
        if "high" in risks:
            return "attention"
        if "medium" in risks:
            return "attention"
        return "ok"

    def _average(self, values: list[float]) -> float:
        clean = [float(item) for item in values if item is not None]
        return sum(clean) / len(clean) if clean else 0.0

    def _ratio(self, numerator: int, denominator: int) -> float:
        return round(numerator / denominator, 3) if denominator else 0.0





