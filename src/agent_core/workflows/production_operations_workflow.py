"""Production Operations workflow for Athena local demo.

The first implementation is deliberately read-only and mock-backed. It models
the management workflow from order intake to garment output without writing to
APS, IOT, ERP, machine programs, or service systems.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


PRODUCTION_TEMPLATE_ID = "athena.production_operations.v1"
PRODUCTION_VERSION = "v0.25.3"
ADAPTER_CONTRACT_ID = "athena.production_aps_iot_read_only_contract.v1"
DATA_PATH = Path(__file__).resolve().parents[2] / "mock_data" / "production_operations.mock.json"


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
            "through read-only contracts."
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
        ],
        adapter_field_mapping=[
            {
                "object": "production_order",
                "console_section": "order",
                "source_system": "APS",
                "source_pages": ["织造监控", "生产单", "款式管理"],
                "observed_fields": ["订单号", "交期", "逾期天数", "款式数", "剩余数量", "客户", "需求款式", "状态"],
                "normalized_fields": ["order_id", "due_date", "overdue_days", "style_count", "remaining_quantity", "customer", "style_code", "production_status"],
            },
            {
                "object": "yarn_material_forecast",
                "console_section": "order",
                "source_system": "APS",
                "source_pages": ["纱线预估"],
                "observed_fields": ["SKU", "部位", "机器尺寸", "预测产量", "纱线代码", "批次", "供应商", "颜色", "需求量(KG)", "库存量(KG)", "在途量(KG)"],
                "normalized_fields": ["sku", "garment_part", "machine_size", "forecast_quantity", "yarn_code", "lot", "supplier", "color", "demand_kg", "stock_kg", "in_transit_kg"],
            },
            {
                "object": "aps_schedule_capacity",
                "console_section": "scheduling",
                "source_system": "APS",
                "source_pages": ["机器排产", "自动排产", "机台汇总", "机台计划单"],
                "observed_fields": ["机台号", "筒径", "针距", "订单号", "款式号", "计划生产件数", "已生产件数", "计划时间", "开机数", "开机率", "单机生产天数"],
                "normalized_fields": ["machine_id", "cylinder_diameter", "gauge", "order_id", "style_code", "planned_quantity", "produced_quantity", "planned_window", "running_machine_count", "machine_running_rate", "capacity_pressure_days"],
            },
            {
                "object": "iot_machine_execution",
                "console_section": "machine",
                "source_system": "Santoni IOT",
                "source_pages": ["实时监控", "仪表盘", "单机详情"],
                "observed_fields": ["机台号", "当前状态", "持续时长", "机型", "筒径", "针距", "班次实际产量", "班次理论产量", "时间开动率", "性能开动率", "当前告警"],
                "normalized_fields": ["machine_id", "iot_status", "status_duration", "model", "cylinder_diameter", "gauge", "actual_output", "theoretical_output", "time_availability_rate", "performance_availability_rate", "alarm"],
            },
            {
                "object": "iot_program_evidence",
                "console_section": "machine",
                "source_system": "Santoni IOT",
                "source_pages": ["单机详情", "程序接口"],
                "observed_fields": ["订单号", "款式号", ".co文件", ".cx文件", "最近实际周期", "理论生产周期", "协议版本", "最后一条数据更新时间"],
                "normalized_fields": ["order_id", "style_code", "co_file", "cx_file", "last_actual_cycle_seconds", "theoretical_cycle_seconds", "protocol_version", "last_data_time"],
            },
            {
                "object": "garment_quality_output",
                "console_section": "garment",
                "source_system": "Santoni IOT",
                "source_pages": ["数据分析", "单机详情"],
                "observed_fields": ["实际产量(件)", "理论产量(件)", "废弃数量", "成品率", "班次OEE", "班次废弃件数", "班次不良品件数"],
                "normalized_fields": ["actual_output", "theoretical_output", "scrap_quantity", "yield_rate", "shift_oee", "shift_scrap_quantity", "defect_quantity"],
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
            "label": "订单号",
            "role": "unique_workflow_spine",
            "description": "订单号 is the only canonical key used to join order intake, ERP sync, APS scheduling, IOT execution, production/service candidates, and garment output.",
            "future_integration_rule": "When APS/IOT databases or formal APIs are connected, every normalized production object must retain the same canonical order_id for workflow traceability.",
        },
        resource_lenses=["people", "machine", "material", "method", "environment", "measurement"],
        output_objects=[
            "production_overview",
            "workflow_stages",
            "resource_lens",
            "optimization_signals",
            "service_escalations",
            "garment_output",
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
                "source_pages": ["织造监控", "机器排产", "机台汇总", "自动排产", "纱线预估", "机台计划单", "生产单", "款式管理", "机器资料"],
                "primary_console_sections": ["order", "scheduling"],
            },
            {
                "system": "Santoni IOT",
                "adapter": "Santoni IOT Adapter",
                "status": "read_only_planned",
                "source_pages": ["实时监控", "仪表盘", "数据分析", "单机详情", "程序接口", "工厂资源"],
                "primary_console_sections": ["machine", "garment"],
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

    def __init__(self, data_path: Path | None = None) -> None:
        self.data_path = data_path or DATA_PATH

    def template(self) -> dict:
        return production_operations_template()

    def adapter_contract(self) -> dict:
        return production_adapter_contract()

    def overview(self, filters: dict | None = None) -> dict:
        data = self._load_data()
        filtered = self._apply_filters(data, filters or {})
        return self._build_result(filtered, filters or {}, scenario=None)

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
        analysis = self._chatbi_analysis(data, result, question)
        evidence_refs = {
            ref
            for cause in analysis.get("root_causes", [])
            for ref in cause.get("evidence_refs", [])
        }
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
            "read_only": True,
            "write_actions_blocked": True,
            "answer_summary": analysis["answer_summary"],
            "metric_snapshot": analysis["metric_snapshot"],
            "root_causes": analysis["root_causes"],
            "recommended_actions": analysis["recommended_actions"],
            "next_drilldowns": analysis["next_drilldowns"],
            "confidence": analysis["confidence"],
            "source_objects": analysis["source_objects"],
            "data_source": self._data_source_metadata(),
            "blocked_actions": result["workflow_instance"]["blocked_actions"],
            "evidence_log": [
                item for item in data.get("evidence_log", []) if item.get("evidence_id") in evidence_refs
            ],
        }

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

    def _build_result(self, data: dict, filters: dict, scenario: str | None) -> dict:
        overview = self._production_overview(data)
        stages = self._workflow_stages(data)
        resource_lens = self._resource_lens(data)
        service_escalations = self._service_escalations(data)
        optimization_signals = self._optimization_signals(data, resource_lens, service_escalations)
        garment_output = self._garment_output(data)
        kpi_log = self._kpi_log(overview, resource_lens, optimization_signals)

        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": PRODUCTION_TEMPLATE_ID,
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
                ],
            },
            "production_overview": overview,
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

    def _kpi_log(self, overview: dict, resource_lens: dict, optimization_signals: list[dict]) -> list[dict]:
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
        ]

    def _chatbi_analysis(self, data: dict, result: dict, question: str) -> dict:
        language = "zh" if any("\u4e00" <= char <= "\u9fff" for char in question) else "en"
        metric = self._detect_chatbi_metric(question)
        if metric == "scrap_rate":
            return self._chatbi_scrap_rate(data, result, language)
        if metric == "oee":
            return self._chatbi_oee(data, result, language)
        if metric == "downtime":
            return self._chatbi_downtime(data, result, language)
        if metric == "material_risk":
            return self._chatbi_material_risk(data, result, language)
        if metric == "order_delay":
            return self._chatbi_order_delay(data, result, language)
        return self._chatbi_overall(data, result, language)

    def _detect_chatbi_metric(self, question: str) -> str:
        lowered = question.lower()
        if any(token in lowered for token in ["scrap", "waste", "defect", "yield", "废弃", "废料", "不良", "良品"]):
            return "scrap_rate"
        if "oee" in lowered or "开动率" in lowered or "稼动率" in lowered:
            return "oee"
        if any(token in lowered for token in ["downtime", "停机", "报警", "故障"]):
            return "downtime"
        if any(token in lowered for token in ["material", "yarn", "纱", "物料", "到料", "库存"]):
            return "material_risk"
        if any(token in lowered for token in ["delay", "overdue", "交期", "延期", "逾期", "未排"]):
            return "order_delay"
        return "overall"

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
                    "category_label": self._choose(language, "Style / quality", "款式 / 质量"),
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
                        self._choose(language, f"Defect rate {measurement.get('defect_rate', 0):.1%}", f"缺陷率 {measurement.get('defect_rate', 0):.1%}"),
                        self._choose(language, f"Yield {measurement.get('yield_rate', 0):.1%}", f"良品率 {measurement.get('yield_rate', 0):.1%}"),
                        self._choose(language, f"Machines {', '.join(machine_ids) or 'none'}", f"关联机台 {', '.join(machine_ids) or '无'}"),
                        self._choose(language, f"Reasons: {', '.join(measurement.get('defect_reasons', []))}", f"原因：{', '.join(measurement.get('defect_reasons', []))}"),
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
                    "category_label": self._choose(language, "Machine", "机器"),
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
                        self._choose(language, f"Downtime {machine.get('downtime_minutes', 0)} min", f"停机 {machine.get('downtime_minutes', 0)} 分钟"),
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
                            "category_label": self._choose(language, "Method / setup", "工艺 / 调机"),
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
                                self._choose(language, f"Read-only .co/.cx evidence: {process.get('co_file', '')} / {process.get('cx_file', '')}", f"只读 .co/.cx 证据：{process.get('co_file', '')} / {process.get('cx_file', '')}"),
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
                "category_label": self._choose(language, "Material", "物料"),
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
                        "高风险氨纶关联的是未开始订单；当前废弃主要来自运行中/质量暂停订单。",
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
                f"当前废弃率约 {overview['scrap_rate']:.0%}。最强证据指向款式/质量与机器/调机问题，物料不是当前废弃率的首要驱动因素。",
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
                self._choose(language, "Prioritize YOGA-BRA-240 / SM8-03 review before treating this as a general material issue.", "优先复核 YOGA-BRA-240 / SM8-03，不要先把问题归因为通用物料问题。"),
                self._choose(language, "Check fabric tension variation, logo elasticity, setup variance, and .co/.cx evidence together.", "把布面张力波动、logo 弹性、调机偏差和 .co/.cx 程序证据一起检查。"),
                self._choose(language, "Use the result as a service request candidate only after the production/service owner confirms.", "只有生产/服务负责人确认后，才把结果转成服务请求候选。"),
            ],
            "next_drilldowns": [
                self._choose(language, "Break scrap by style and machine.", "按款式和机台拆分废弃数量。"),
                self._choose(language, "Compare setup variance with defect reasons.", "对比调机偏差和不良原因。"),
                self._choose(language, "Check whether the same .co/.cx files behave differently across machines.", "检查同一组 .co/.cx 文件在不同机台上的表现差异。"),
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
                "category_label": self._choose(language, "Machine", "机器"),
                "cause": self._choose(language, f"{machine['machine_id']} pulls OEE down.", f"{machine['machine_id']} 拉低了整体 OEE。"),
                "impact": {
                    "machine_id": machine["machine_id"],
                    "oee": machine.get("oee", 0),
                    "state": machine.get("state", ""),
                    "downtime_minutes": machine.get("downtime_minutes", 0),
                },
                "data_points": [
                    self._choose(language, f"State {machine.get('state')}", f"状态 {machine.get('state')}"),
                    self._choose(language, f"Alarm {machine.get('alarm') or 'none'}", f"报警 {machine.get('alarm') or '无'}"),
                ],
                "evidence_refs": [machine["evidence_ref"]],
            }
            for index, machine in enumerate(low_machines[:4])
        ]
        return self._generic_chatbi_response(
            language,
            "oee",
            self._choose(language, f"Average OEE is {overview['average_oee']:.0%}, below the 82% target.", f"平均 OEE 为 {overview['average_oee']:.0%}，低于 82% 目标。"),
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
                "category_label": self._choose(language, "Machine downtime", "机器停机"),
                "cause": self._choose(language, f"{machine['machine_id']} contributes {machine.get('downtime_minutes', 0)} downtime minutes.", f"{machine['machine_id']} 贡献了 {machine.get('downtime_minutes', 0)} 分钟停机。"),
                "impact": {
                    "machine_id": machine["machine_id"],
                    "downtime_minutes": machine.get("downtime_minutes", 0),
                    "state": machine.get("state", ""),
                },
                "data_points": [self._choose(language, f"Alarm {machine.get('alarm') or 'none'}", f"报警 {machine.get('alarm') or '无'}")],
                "evidence_refs": [machine["evidence_ref"]],
            }
            for index, machine in enumerate(machines[:4])
            if machine.get("downtime_minutes", 0)
        ]
        return self._generic_chatbi_response(
            language,
            "downtime",
            self._choose(language, f"Total downtime is {overview['downtime_minutes']} minutes; the top machines explain most of it.", f"总停机时间为 {overview['downtime_minutes']} 分钟，头部机台解释了主要停机来源。"),
            {"downtime_minutes": overview["downtime_minutes"], "target": "< 120 per shift", "status": "attention"},
            root_causes,
            ["machines", "evidence_log"],
        )

    def _chatbi_material_risk(self, data: dict, result: dict, language: str) -> dict:
        overview = result["production_overview"]
        materials = sorted(data.get("materials", []), key=lambda item: {"high": 0, "medium": 1, "low": 2}.get(item.get("risk"), 3))
        root_causes = [
            {
                "rank": index + 1,
                "category": "material",
                "category_label": self._choose(language, "Material", "物料"),
                "cause": self._choose(language, f"{material['name']} lot {material['lot']} is {material['risk']} risk.", f"{material['name']} 批次 {material['lot']} 是 {material['risk']} 风险。"),
                "impact": {
                    "material_id": material["material_id"],
                    "risk": material["risk"],
                    "demand_kg": material.get("demand_kg", 0),
                    "stock_kg": material.get("stock_kg", 0),
                    "in_transit_kg": material.get("in_transit_kg", 0),
                    "required_orders": material.get("required_orders", []),
                },
                "data_points": [
                    self._choose(language, f"Demand {material.get('demand_kg', 0)} kg, stock {material.get('stock_kg', 0)} kg", f"需求 {material.get('demand_kg', 0)} kg，库存 {material.get('stock_kg', 0)} kg"),
                ],
                "evidence_refs": [material["evidence_ref"]],
            }
            for index, material in enumerate(materials[:4])
            if material.get("risk") in {"medium", "high"}
        ]
        return self._generic_chatbi_response(
            language,
            "material_risk",
            self._choose(language, f"There are {overview['material_risk_count']} material risk items; elastane is the highest risk.", f"当前有 {overview['material_risk_count']} 个物料风险项，其中氨纶风险最高。"),
            {"material_risk_count": overview["material_risk_count"], "target": 0, "status": "attention"},
            root_causes,
            ["materials", "orders", "aps_schedule", "evidence_log"],
        )

    def _chatbi_order_delay(self, data: dict, result: dict, language: str) -> dict:
        overview = result["production_overview"]
        orders = [
            item for item in data.get("orders", [])
            if item.get("aps_status") != "scheduled" or item.get("erp_status") == "exception"
        ]
        root_causes = [
            {
                "rank": index + 1,
                "category": "order_schedule",
                "category_label": self._choose(language, "Order / schedule", "订单 / 排单"),
                "cause": self._choose(language, f"{order['order_id']} is {order.get('aps_status')}.", f"{order['order_id']} 当前状态为 {order.get('aps_status')}。"),
                "impact": {
                    "order_id": order["order_id"],
                    "style_code": order.get("style_code", ""),
                    "remaining_quantity": order.get("remaining_quantity", 0),
                    "erp_status": order.get("erp_status", ""),
                    "aps_status": order.get("aps_status", ""),
                },
                "data_points": [self._choose(language, f"Remaining quantity {order.get('remaining_quantity', 0)}", f"剩余数量 {order.get('remaining_quantity', 0)}")],
                "evidence_refs": [order["evidence_ref"]],
            }
            for index, order in enumerate(orders)
        ]
        return self._generic_chatbi_response(
            language,
            "order_delay",
            self._choose(language, f"{overview['pending_or_exception_order_count']} orders need scheduling or exception review.", f"{overview['pending_or_exception_order_count']} 个订单需要排单或异常复核。"),
            {"pending_or_exception_order_count": overview["pending_or_exception_order_count"], "target": 0, "status": "attention"},
            root_causes,
            ["orders", "aps_schedule", "materials", "evidence_log"],
        )

    def _chatbi_overall(self, data: dict, result: dict, language: str) -> dict:
        root_causes = [
            {
                "rank": index + 1,
                "category": signal["type"],
                "category_label": self._choose(language, "Optimization signal", "优化信号"),
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
            self._choose(language, "The current snapshot needs attention across machine downtime, material flow, and quality measurement.", "当前快照需要关注机器停机、物料流转和质量检测。"),
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
                self._choose(language, "Review the top evidence-linked cause before changing schedules or machine settings.", "先复核排名最高且有证据链接的原因，再考虑调整排单或机台设置。"),
                self._choose(language, "Keep this analysis read-only and ask the production owner to confirm before action.", "该分析保持只读，行动前需要生产负责人确认。"),
            ],
            "next_drilldowns": [
                self._choose(language, "Drill down by order, style, machine, material lot, and shift.", "继续按订单、款式、机台、物料批次和班次下钻。"),
            ],
            "confidence": "medium",
            "source_objects": source_objects,
        }

    def _group_by(self, items: list[dict], key: str) -> dict:
        grouped: dict[str, list[dict]] = {}
        for item in items:
            grouped.setdefault(item.get(key, ""), []).append(item)
        return grouped

    def _choose(self, language: str, english: str, chinese: str) -> str:
        return chinese if language == "zh" else english

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
