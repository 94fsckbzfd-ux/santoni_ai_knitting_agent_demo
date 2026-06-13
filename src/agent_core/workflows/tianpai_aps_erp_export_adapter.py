"""Read-only Tianpai APS/ERP CSV export adapter.

The adapter reads customer-provided CSV exports from an external folder. It
does not copy raw files into the repository and only returns aggregate object
counts, join quality, capability boundaries, and small non-sensitive examples.
"""

from __future__ import annotations

import csv
import os
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


FIELD_SCHEMA_FILE_NAME = "表字段"


def _default_export_dir() -> Path:
    docs_root = Path(__file__).resolve().parents[4]
    return docs_root / "Product" / "AI Knitting Agent" / "Athena Training" / "aps-data" / "aps-data"


DEFAULT_EXPORT_DIR = _default_export_dir()
TABLE_FILE_NAMES = {
    "Produce_Order": "Produce_Order.csv",
    "Weaving_Part_Order": "Weaving_Part_Order.csv",
    "Style_Sku": "Style_Sku.csv",
    "Style_Component": "Style_Component.csv",
    "Planned_Task": "Planned_Task.csv",
    "Manual_Machine_Production": "Manual_Machine_Production.csv",
    "T_Machine_Info": "T_Machine_Info.csv",
}

ADAPTER_VERSION = "v0.113.3"
CURRENT_DELIVERY_OVERDUE_REVIEW_DAYS = -30
CURRENT_DELIVERY_LOOKAHEAD_DAYS = 45
COMPLETED_PLAN_RATE_THRESHOLD = 0.98
EXTREME_QUANTITY_GAP_ABSOLUTE = 10000
EXTREME_QUANTITY_GAP_RATIO = 0.3

_REPORT_CACHE: dict[tuple[str, tuple[tuple[str, float | None], ...]], dict] = {}
_TABLE_LOAD_CACHE: dict[tuple[str, tuple[tuple[str, float | None], ...]], dict[str, "TableLoad"]] = {}

FALLBACK_FIELD_ORDER = {
    "Manual_Machine_Production": [
        "id",
        "institute_id",
        "factory_id",
        "task_id",
        "produce_order_code",
        "sku_code",
        "part",
        "device_id",
        "date",
        "operator_quantity",
        "operator_defects",
        "operator_discards",
        "inspector_quantity",
        "inspector_defects",
        "bar_code",
        "create_time",
        "modified_time",
        "deleted_at",
    ],
    "Planned_Task": [
        "id",
        "task_code",
        "institute_id",
        "factory_id",
        "task_source",
        "produce_order_code",
        "weaving_part_order_id",
        "machine_id",
        "style_code",
        "symbol_id",
        "symbol",
        "sku_code",
        "size_id",
        "size",
        "part_id",
        "part",
        "color_id",
        "color",
        "produced_quantity",
        "planned_quantity",
        "plan_start_time",
        "plan_end_time",
        "actual_start_time",
        "actual_end_time",
        "estimate_end_time",
        "status",
        "flag",
        "outer_id",
        "report_bar_code",
        "create_time",
        "modified_time",
        "creator_id",
        "operator_id",
        "deleted_at",
    ],
    "Produce_Order": [
        "id",
        "outer_order_id",
        "org_id",
        "org_name",
        "manufacture_batch",
        "code",
        "institute_id",
        "customer_code",
        "customer_name",
        "delivery_time",
        "manufacture_date",
        "status",
        "create_time",
        "modified_time",
        "creator_id",
        "operator_id",
        "deleted_at",
    ],
    "Style_Component": [
        "id",
        "institute_id",
        "produce_order_id",
        "produce_order_code",
        "sku_code",
        "part_id",
        "part",
        "color_id",
        "color",
        "type",
        "program_file",
        "program_file_url",
        "number",
        "ratio",
        "cylinder_diameter",
        "needle_spacing",
        "description",
        "expected_produce_time",
        "expected_weight",
        "standard_number",
        "machine_requirement",
        "finish_width",
        "finish_length",
        "waste_rate",
        "dye",
        "default_efficiency",
        "actual_efficiency",
        "yarn_usage",
        "create_time",
        "modified_time",
        "deleted_at",
    ],
    "Style_Sku": [
        "id",
        "institute_id",
        "produce_order_id",
        "produce_order_code",
        "style_code",
        "code",
        "size_id",
        "size",
        "expected_produce_time",
        "create_time",
        "modified_time",
        "deleted_at",
    ],
    "Weaving_Part_Order": [
        "id",
        "institute_id",
        "factory_id",
        "weaving_order_id",
        "produce_order_id",
        "produce_order_code",
        "style_component_id",
        "style_code",
        "symbol_id",
        "symbol",
        "sku_code",
        "size_id",
        "size",
        "part_id",
        "part",
        "color_id",
        "color",
        "program",
        "task_detail_id",
        "prod_schedule_detail_id",
        "figure",
        "unit",
        "comment",
        "quantity",
        "produced_quantity",
        "planned_quantity",
        "finish_time",
        "status",
        "create_time",
        "modified_time",
        "deleted_at",
    ],
    "T_Machine_Info": [
        "f_machine_id",
        "f_outer_id",
        "f_machine_code",
        "f_machine_number",
        "f_machine_type",
        "f_area",
        "f_cylinder_diameter",
        "f_needle_spacing",
        "f_during_running",
        "f_deleted",
        "f_create_time",
        "f_update_time",
        "f_needle_quantity",
        "f_ktf",
        "f_lgl_large",
        "f_lgl_small",
        "f_elan",
        "f_rolling",
        "f_backward",
    ],
}


@dataclass(frozen=True)
class TableLoad:
    name: str
    file_name: str
    fields: list[str]
    rows: list[dict[str, str]]
    exists: bool
    error: str | None = None


class TianpaiApsErpExportAdapter:
    """Load and summarize the Tianpai APS/ERP export folder."""

    adapter_id = "athena.tianpai_aps_erp_export_adapter.v1"

    def __init__(self, export_dir: str | Path | None = None) -> None:
        configured = export_dir or os.environ.get("TIANPAI_APS_EXPORT_DIR")
        self.export_dir = Path(configured) if configured else DEFAULT_EXPORT_DIR

    def report(self) -> dict:
        signature = self._cache_signature()
        if signature in _REPORT_CACHE:
            return _REPORT_CACHE[signature]
        loads = self._load_tables()
        raw_tables = {name: load.rows for name, load in loads.items()}
        tables = {name: self._active_rows(name, rows) for name, rows in raw_tables.items()}
        unavailable = [name for name, load in loads.items() if not load.exists or load.error]
        if unavailable:
            report = self._missing_report(loads, unavailable)
            _REPORT_CACHE[signature] = report
            return report

        normalized = self._normalized_objects(tables)
        quality = self._data_quality(tables)
        capability = self._capability_boundary(tables, quality)

        report = {
            "adapter_id": self.adapter_id,
            "version": ADAPTER_VERSION,
            "source": "Tianpai APS/ERP CSV export",
            "adapter_status": "read_only_external_csv",
            "read_only": True,
            "raw_file_stored_in_repo": False,
            "export_dir": str(self.export_dir),
            "table_field_source": "field schema DDL order",
            "schema_source_file": FIELD_SCHEMA_FILE_NAME,
            "tables": {
                name: {
                    "file_name": load.file_name,
                    "row_count": len(tables.get(name, load.rows)),
                    "raw_row_count": len(load.rows),
                    "excluded_deleted_row_count": max(len(load.rows) - len(tables.get(name, load.rows)), 0),
                    "field_count": len(load.fields),
                    "fields": load.fields,
                    "exists": load.exists,
                    "error": load.error,
                }
                for name, load in loads.items()
            },
            "standard_objects": normalized,
            "data_quality_report": quality,
            "capability_boundary": capability,
            "blocked_actions": [
                "copy_raw_customer_csv_into_repo",
                "write_back_to_erp_or_aps",
                "confirm_schedule",
                "release_order_to_machine",
                "modify_customer_data",
                "claim_quality_root_cause_from_zero_defect_export",
            ],
        }
        _REPORT_CACHE[signature] = report
        return report

    def answer_management_question(self, question: str) -> dict | None:
        question_type = self._detect_actual_question_type(question)
        if not question_type:
            return None
        language = "zh" if any("\u4e00" <= char <= "\u9fff" for char in question) else "en"
        loads = self._load_tables()
        raw_tables = {name: load.rows for name, load in loads.items()}
        tables = {name: self._active_rows(name, rows) for name, rows in raw_tables.items()}
        unavailable = [name for name, load in loads.items() if not load.exists or load.error]
        if unavailable:
            return self._actual_data_unavailable_answer(question_type, language, unavailable)
        if question_type == "delivery_reconciliation":
            return self._answer_delivery_reconciliation(tables, language, question)
        if question_type == "delivery_risk":
            return self._answer_delivery_risk(tables, language)
        if question_type == "unscheduled_parts":
            return self._answer_unscheduled_parts(tables, language)
        if question_type == "machine_load":
            return self._answer_machine_load(tables, language)
        if question_type == "machine_style_mismatch":
            return self._answer_machine_style_mismatch(tables, language)
        if question_type == "quantity_report_gap":
            return self._answer_quantity_report_gap(tables, language)
        return None

    def _detect_actual_question_type(self, question: str) -> str | None:
        lowered = question.lower()
        if any(token in lowered for token in ["reconciliation", "not delivery risk", "evidence review", "data review", "复核", "不是交付风险", "数据口径"]):
            return "delivery_reconciliation"
        if any(token in lowered for token in ["quantity gap", "report gap", "planned vs reported", "manual report", "计划量", "报工量", "差异"]):
            return "quantity_report_gap"
        if any(token in lowered for token in ["cylinder", "gauge", "machine spec", "style spec", "machine style", "机台规格", "不匹配", "筒径", "针距"]):
            return "machine_style_mismatch"
        if any(token in lowered for token in ["load highest", "machine load", "highest load", "capacity load", "负载最高", "机台负载", "机器负载"]):
            return "machine_load"
        if any(
            token in lowered
            for token in [
                "delivery risk",
                "at risk orders",
                "due risk",
                "order delay",
                "交付风险",
                "交期风险",
                "货期风险",
                "延期风险",
                "影响交付",
                "交付",
                "交期",
                "货期",
            ]
        ):
            return "delivery_risk"
        if any(token in lowered for token in ["unscheduled", "not fully scheduled", "part order", "没有排满", "未排", "部件单"]):
            return "unscheduled_parts"
        return None
    def delivery_evidence_review_queue(self, language: str = "zh", limit: int = 10) -> dict:
        loads = self._load_tables()
        raw_tables = {name: load.rows for name, load in loads.items()}
        tables = {name: self._active_rows(name, rows) for name, rows in raw_tables.items()}
        unavailable = [name for name, load in loads.items() if not load.exists or load.error]
        if unavailable:
            return {
                "schema_id": "athena.production_evidence_review_queue.v1",
                "version": ADAPTER_VERSION,
                "language": language,
                "adapter_status": "missing_external_csv",
                "read_only": True,
                "source": "Tianpai APS Export",
                "review_queue": [],
                "candidate_count": 0,
                "data_gaps": unavailable,
                "blocked_actions": ["write_aps", "write_erp", "write_iot", "change_schedule", "dispatch_service"],
            }
        orders = self._order_aggregates(tables)
        candidates = [order for order in orders if self._has_delivery_reconciliation_driver(order)]
        cards = [self._delivery_reconciliation_card(order, language) for order in candidates]
        cards = sorted(
            cards,
            key=lambda item: (
                0 if item.get("plan_completion_rate", 0) >= COMPLETED_PLAN_RATE_THRESHOLD else 1,
                item.get("days_to_due") if item.get("days_to_due") is not None else 9999,
                -abs(item.get("quantity_report_gap", 0) or 0),
                -int(item.get("unscheduled_quantity", 0) or 0),
                item.get("object_id", ""),
            ),
        )
        return {
            "schema_id": "athena.production_evidence_review_queue.v1",
            "version": ADAPTER_VERSION,
            "language": language,
            "adapter_status": "read_only_external_csv",
            "read_only": True,
            "source": "Tianpai APS Export",
            "review_queue": cards[:limit],
            "candidate_count": len(cards),
            "summary": self._choose(
                language,
                f"{len(cards)} delivery evidence records need planning or quantity reconciliation before Athena can treat them as hard delivery risks.",
                f"{len(cards)} 条交付证据需要先做计划状态或数量口径复核，Athena 不能直接把它们当作硬性交付风险。",
            ),
            "blocked_actions": ["write_aps", "write_erp", "write_iot", "change_schedule", "dispatch_service"],
        }

    def _actual_data_unavailable_answer(self, metric: str, language: str, unavailable: list[str]) -> dict:
        summary = self._choose(
            language,
            "The Tianpai APS Export is not fully available, so Athena cannot answer this actual-data question yet.",
            "天派 APS Export 尚未完整可用，因此 Athena 暂时不能回答这个真实数据问题。",
        )
        return {
            "language": language,
            "metric": metric,
            "actual_data_mode": True,
            "answer_summary": summary,
            "metric_snapshot": {"status": "missing_external_csv", "unavailable_tables": unavailable},
            "root_causes": [],
            "recommended_actions": [
                self._choose(language, "Confirm the external export folder and required CSV files.", "确认外部导出目录和所需 CSV 文件是否齐全。")
            ],
            "next_drilldowns": [],
            "data_gaps": unavailable,
            "confidence": "low",
            "source_objects": ["Tianpai APS Export"],
            "actual_evidence_chains": [],
            "evidence_log": [],
        }

    def _answer_delivery_risk(self, tables: dict[str, list[dict[str, str]]], language: str) -> dict:
        orders = self._order_aggregates(tables)
        risk_orders = [order for order in orders if self._is_current_delivery_risk_candidate(order)]
        reconciliation_orders = [order for order in orders if self._has_delivery_reconciliation_driver(order)]
        risk_orders = sorted(
            risk_orders,
            key=lambda item: (
                item["days_to_due"] if item["days_to_due"] is not None else 9999,
                -item["unscheduled_quantity"],
                item["plan_completion_rate"],
            ),
        )[:5]
        evidence = [self._order_evidence_chain(item) for item in risk_orders]
        root_causes = [
            self._root_cause_from_chain(
                index,
                "delivery_risk",
                self._choose(language, "Delivery risk", "交付风险"),
                self._delivery_risk_cause(chain, language),
                chain,
            )
            for index, chain in enumerate(evidence, start=1)
        ]
        return self._actual_answer(
            language=language,
            metric="order_delay",
            summary=self._choose(
                language,
                f"{len(risk_orders)} orders are current delivery-risk candidates in the Tianpai APS Export.",
                f"天派 APS Export 中当前有 {len(risk_orders)} 个订单进入交付风险候选。",
            ),
            snapshot={
                "risk_order_count": len(risk_orders),
                "delivery_reconciliation_candidate_count": len(reconciliation_orders),
                "total_order_count": len(tables["Produce_Order"]),
                "source": "Tianpai APS Export",
            },
            root_causes=root_causes,
            evidence=evidence,
            actions=[
                self._choose(language, "Ask planning to confirm the top risk orders and missing scheduled quantities.", "请计划负责人确认最高风险订单和未排数量。"),
                self._choose(language, "Use order code to drill into weaving part orders and planned tasks before changing any schedule.", "在改排程前，用订单号下钻织造部件单和计划任务。"),
            ],
            drilldowns=[
                self._choose(language, "Open Weaving_Part_Order by produce_order_code.", "按 produce_order_code 打开 Weaving_Part_Order。"),
                self._choose(language, "Open Planned_Task by produce_order_code and weaving_part_order_id.", "按 produce_order_code 和 weaving_part_order_id 打开 Planned_Task。"),
            ],
        )

    def _answer_delivery_reconciliation(self, tables: dict[str, list[dict[str, str]]], language: str, question: str) -> dict:
        orders = self._order_aggregates(tables)
        candidates = [order for order in orders if self._has_delivery_reconciliation_driver(order)]
        mentioned_codes = set(re.findall(r"\b\d{6,}\b", question))
        if mentioned_codes:
            candidates = [order for order in candidates if order.get("produce_order_code") in mentioned_codes]
        cards = [self._delivery_reconciliation_card(order, language) for order in candidates]
        cards = sorted(
            cards,
            key=lambda item: (
                item.get("days_to_due") if item.get("days_to_due") is not None else 9999,
                -abs(item.get("quantity_report_gap", 0) or 0),
                -int(item.get("unscheduled_quantity", 0) or 0),
            ),
        )[:5]
        root_causes = [
            self._root_cause_from_chain(
                index,
                "delivery_evidence_review",
                self._choose(language, "Evidence review", "璇佹嵁澶嶆牳"),
                card["why_not_delivery_risk"],
                card,
            )
            for index, card in enumerate(cards, start=1)
        ]
        return self._actual_answer(
            language=language,
            metric="evidence_review",
            summary=self._choose(
                language,
                f"{len(cards)} delivery evidence records are reconciliation candidates, not confirmed hard delivery risks.",
                f"{len(cards)} 条交付证据属于复核候选，不是已确认的硬性交付风险。",
            ),
            snapshot={
                "review_candidate_count": len(cards),
                "total_reconciliation_candidate_count": len([order for order in orders if self._has_delivery_reconciliation_driver(order)]),
                "source": "Tianpai APS Export",
            },
            root_causes=root_causes,
            evidence=cards,
            actions=[
                self._choose(language, "Ask the planning owner to confirm order status, split-task policy, and quantity reporting scope.", "?????????????????????????"),
                self._choose(language, "Do not change schedule or claim delivery risk until the reconciliation owner confirms the evidence.", "??????????????????????????"),
            ],
            drilldowns=[
                self._choose(language, "Drill into Produce_Order, Weaving_Part_Order, Planned_Task, and Manual_Machine_Production by produce_order_code.", "按 produce_order_code 下钻 Produce_Order、Weaving_Part_Order、Planned_Task 和 Manual_Machine_Production。"),
            ],
        )

    def _answer_unscheduled_parts(self, tables: dict[str, list[dict[str, str]]], language: str) -> dict:
        parts = []
        for row in tables["Weaving_Part_Order"]:
            quantity = self._to_int(row.get("quantity"))
            planned = self._to_int(row.get("planned_quantity"))
            gap = quantity - planned
            if gap <= 0:
                continue
            parts.append(
                {
                    "produce_order_code": row.get("produce_order_code"),
                    "weaving_part_order_id": row.get("id"),
                    "sku_code": row.get("sku_code"),
                    "part": row.get("part"),
                    "quantity": quantity,
                    "planned_quantity": planned,
                    "unscheduled_quantity": gap,
                    "finish_time": row.get("finish_time"),
                    "field_source": "Weaving_Part_Order.quantity - Weaving_Part_Order.planned_quantity",
                    "evidence_refs": [f"Weaving_Part_Order.id={row.get('id')}"],
                }
            )
        parts = sorted(
            parts,
            key=lambda item: (
                self._parse_date(item.get("finish_time")) or datetime.max,
                -item["unscheduled_quantity"],
            ),
        )[:5]
        root_causes = [
            self._root_cause_from_chain(
                index,
                "unscheduled_weaving_part_order",
                self._choose(language, "Unscheduled part order", "未排满织造部件单"),
                self._choose(
                    language,
                    f"Part order {chain['weaving_part_order_id']} still has {chain['unscheduled_quantity']} pieces not scheduled.",
                    f"部件单 {chain['weaving_part_order_id']} 仍有 {chain['unscheduled_quantity']} 件未排。",
                ),
                chain,
            )
            for index, chain in enumerate(parts, start=1)
        ]
        return self._actual_answer(
            language,
            "unscheduled_weaving_part_order",
            self._choose(language, f"{len(parts)} top unscheduled part-order candidates are listed by due date and gap.", f"按交期和缺口列出 {len(parts)} 个未排满部件单候选。"),
            {"top_candidate_count": len(parts), "source": "Tianpai APS Export"},
            root_causes,
            parts,
            [self._choose(language, "Ask planning to confirm whether these part orders need rescheduling or are intentionally left open.", "请计划负责人确认这些部件单是否需要重排，还是故意保留未排。")],
            [self._choose(language, "Drill into Planned_Task by weaving_part_order_id.", "按 weaving_part_order_id 下钻 Planned_Task。")],
        )

    def _answer_machine_load(self, tables: dict[str, list[dict[str, str]]], language: str) -> dict:
        load = self._machine_plan_load(tables["Planned_Task"], tables["T_Machine_Info"])[:5]
        evidence = [
            {
                **item,
                "field_source": "sum(Planned_Task.planned_quantity) by Planned_Task.machine_id joined to T_Machine_Info.f_machine_id",
            }
            for item in load
        ]
        root_causes = [
            self._root_cause_from_chain(
                index,
                "machine_plan_load",
                self._choose(language, "Machine plan load", "机台计划负载"),
                self._choose(
                    language,
                    f"Machine {chain['machine_code']} has planned quantity {chain['planned_quantity']} across {chain['task_count']} tasks.",
                    f"机台 {chain['machine_code']} 计划量 {chain['planned_quantity']}，关联 {chain['task_count']} 个任务。",
                ),
                chain,
            )
            for index, chain in enumerate(evidence, start=1)
        ]
        return self._actual_answer(
            language,
            "machine_plan_load",
            self._choose(language, f"{len(load)} machines have the highest planned load in the current export.", f"{len(load)} machines have the highest planned load in the current export."),
            {"machine_count": len(load), "top_machine": load[0]["machine_code"] if load else ""},
            root_causes,
            evidence,
            [self._choose(language, "Confirm whether high planned load is intentional capacity concentration or a scheduling risk.", "确认高计划负载是有意集中产能，还是排程风险。")],
            [self._choose(language, "Drill into Planned_Task.id evidence refs for each machine.", "按每台机的 Planned_Task.id 证据下钻。")],
        )

    def _answer_machine_style_mismatch(self, tables: dict[str, list[dict[str, str]]], language: str) -> dict:
        mismatch = self._machine_style_mismatch_candidates(
            tables["Planned_Task"], tables["Weaving_Part_Order"], tables["Style_Component"], tables["T_Machine_Info"]
        )
        evidence = mismatch["candidates"][:5]
        root_causes = [
            self._root_cause_from_chain(
                index,
                "machine_style_spec_mismatch",
                self._choose(language, "Machine/style spec mismatch", "机台/款式规格不匹配"),
                self._choose(
                    language,
                    self._machine_style_mismatch_cause(chain, "en"),
                    self._machine_style_mismatch_cause(chain, "zh"),
                ),
                chain,
            )
            for index, chain in enumerate(evidence, start=1)
        ]
        return self._actual_answer(
            language,
            "machine_style_mismatch",
            self._choose(language, f"{mismatch['candidate_count_total']} machine/style spec mismatch candidates were found.", f"发现 {mismatch['candidate_count_total']} 个机台/款式规格不匹配候选。"),
            {"candidate_count_total": mismatch["candidate_count_total"], "sample_count": len(evidence)},
            root_causes,
            evidence,
            [self._choose(language, "Ask APS or production engineering to confirm whether these are real mismatches or allowed substitutions.", "请 APS 或生产工程确认这些是真实不匹配，还是允许的替代机台。")],
            [self._choose(language, "Compare Style_Component cylinder/needle fields with T_Machine_Info machine fields.", "对比 Style_Component 的筒径/针距字段和 T_Machine_Info 的机台字段。")],
        )

    def _answer_quantity_report_gap(self, tables: dict[str, list[dict[str, str]]], language: str) -> dict:
        orders = self._order_aggregates(tables)
        gaps = []
        for order in orders:
            gap = order["manual_report_good_quantity"] - order["planned_quantity"]
            if gap == 0:
                continue
            sanity_flags = list(order.get("data_sanity_flags", []))
            gap_status = "needs_reconciliation" if self._is_extreme_quantity_gap(gap, order["planned_quantity"]) else "usable_quantity_gap"
            gaps.append(
                {
                    **order,
                    "quantity_report_gap": gap,
                    "abs_quantity_report_gap": abs(gap),
                    "quantity_gap_review_status": gap_status,
                    "data_sanity_flags": sanity_flags,
                    "field_source": "sum(Manual_Machine_Production.operator_quantity) - sum(Planned_Task.planned_quantity) by produce_order_code",
                }
            )
        gaps = sorted(gaps, key=lambda item: item["abs_quantity_report_gap"], reverse=True)[:5]
        evidence = [
            self._order_evidence_chain(item)
            | {
                "quantity_report_gap": item["quantity_report_gap"],
                "quantity_gap_review_status": item["quantity_gap_review_status"],
                "field_source": item["field_source"],
            }
            for item in gaps
        ]
        root_causes = [
            self._root_cause_from_chain(
                index,
                "quantity_report_gap",
                self._choose(language, "Plan/report quantity gap", "计划/报工数量差异"),
                self._choose(
                    language,
                    f"订单 {chain['produce_order_code']} 的报工量与计划量差异为 {chain['quantity_report_gap']}；在判断生产损失前，应先作为数量口径复核候选。",
                    f"Order {chain['produce_order_code']} has report-plan gap {chain['quantity_report_gap']}; treat it as a quantity reconciliation candidate before claiming production loss.",
                ),
                chain,
            )
            for index, chain in enumerate(evidence, start=1)
        ]
        return self._actual_answer(
            language,
            "quantity_report_gap",
            self._choose(language, f"{len(evidence)} orders have the largest planned-vs-reported quantity gaps.", f"列出 {len(evidence)} 个计划量与报工量差异最大的订单。"),
            {"top_gap_count": len(evidence), "source": "Tianpai APS Export"},
            root_causes,
            evidence,
            [self._choose(language, "Confirm whether manual reports can exceed planned quantity because of split tasks, rework, or reporting timing.", "确认报工量超过计划量是否由拆分任务、返工或报工时间差造成。")],
            [self._choose(language, "Drill by produce_order_code into Planned_Task and Manual_Machine_Production rows.", "按 produce_order_code 下钻 Planned_Task 和 Manual_Machine_Production 行。")],
        )

    def _actual_answer(
        self,
        language: str,
        metric: str,
        summary: str,
        snapshot: dict,
        root_causes: list[dict],
        evidence: list[dict],
        actions: list[str],
        drilldowns: list[str],
    ) -> dict:
        evidence_data_gaps = []
        needs_reconciliation = False
        for chain in evidence:
            evidence_data_gaps.extend(chain.get("data_gaps", []))
            if (
                chain.get("evidence_credibility") == "needs_reconciliation"
                or chain.get("quantity_gap_review_status") == "needs_reconciliation"
            ):
                needs_reconciliation = True
        evidence_log = [
            {
                "evidence_id": f"ACTUAL-{metric.upper()}-{index:03d}",
                "claim": root_causes[index - 1]["cause"] if index <= len(root_causes) else metric,
                "source": chain.get("field_source", "Tianpai APS Export"),
                "adapter_status": "read_only_external_csv",
                "evidence_chain": chain,
            }
            for index, chain in enumerate(evidence, start=1)
        ]
        return {
            "language": language,
            "metric": metric,
            "actual_data_mode": True,
            "answer_summary": summary,
            "metric_snapshot": snapshot,
            "root_causes": root_causes,
            "recommended_actions": actions,
            "next_drilldowns": drilldowns,
            "data_gaps": [
                self._choose(language, "This answer uses APS/ERP export data only; live IOT alarms, OEE, downtime, quality defects, and costs are not included.", "本回答仅使用 APS/ERP 导出数据；不包含实时 IOT 报警、OEE、停机、质量缺陷和成本。")
            ] + list(dict.fromkeys(evidence_data_gaps)),
            "confidence": "medium_with_reconciliation_needed" if needs_reconciliation else "medium_high",
            "source_objects": ["Tianpai APS Export", "Produce_Order", "Weaving_Part_Order", "Planned_Task", "Manual_Machine_Production", "T_Machine_Info", "Style_Component"],
            "actual_evidence_chains": evidence,
            "evidence_log": evidence_log,
        }

    def _root_cause_from_chain(self, rank: int, category: str, label: str, cause: str, chain: dict) -> dict:
        data_points = []
        for key in [
            "produce_order_code",
            "weaving_part_order_id",
            "planned_task_id",
            "machine_code",
            "sku_code",
            "part",
            "planned_quantity",
            "produced_quantity",
            "manual_report_good_quantity",
            "quantity_report_gap",
            "quantity_gap_review_status",
            "unscheduled_quantity",
            "evidence_credibility",
            "data_sanity_flags",
            "delivery_risk_drivers",
            "mismatch_details",
            "field_source",
        ]:
            value = chain.get(key)
            if value is not None and value != "":
                data_points.append(f"{key}: {value}")
        return {
            "rank": rank,
            "category": category,
            "category_label": label,
            "cause": cause,
            "impact": {key: chain.get(key) for key in chain if key not in {"evidence_refs"}},
            "data_points": data_points,
            "evidence_refs": chain.get("evidence_refs", []),
            "evidence_chain": chain,
        }

    def _machine_style_mismatch_cause(self, chain: dict, language: str) -> str:
        details = chain.get("mismatch_details", [])
        if not details:
            fields = ", ".join(chain.get("mismatch_fields", []))
            return self._choose(
                language,
                f"Task {chain.get('planned_task_id')} uses machine {chain.get('machine_code')} with mismatch fields {fields}.",
                f"Task {chain.get('planned_task_id')} uses machine {chain.get('machine_code')} with mismatch fields {fields}.",
            )
        parts = []
        for item in details:
            label = item.get("field") if language == "en" else item.get("field_label_zh", item.get("field"))
            required = item.get("required_value") or "-"
            actual = item.get("actual_machine_value") or "-"
            if language == "en":
                parts.append(
                    f"{label} requires {required} from {item.get('required_field_source')}, "
                    f"but machine {chain.get('machine_code')} has {actual} from {item.get('actual_field_source')}"
                )
            else:
                parts.append(
                    f"{label} requires {required} from {item.get('required_field_source')}, "
                    f"but machine {chain.get('machine_code')} has {actual} from {item.get('actual_field_source')}"
                )
        return f"Task {chain.get('planned_task_id')} has machine/style spec mismatch: " + "; ".join(parts) + "."

    def _order_aggregates(self, tables: dict[str, list[dict[str, str]]]) -> list[dict]:
        order_by_code = {row.get("code"): row for row in tables["Produce_Order"] if row.get("code")}
        wpo_by_order = self._group_by(tables["Weaving_Part_Order"], "produce_order_code")
        tasks_by_order = self._group_by(tables["Planned_Task"], "produce_order_code")
        reports_by_order = self._group_by(tables["Manual_Machine_Production"], "produce_order_code")
        aggregates = []
        for code, order in order_by_code.items():
            wpos = wpo_by_order.get(code, [])
            tasks = tasks_by_order.get(code, [])
            reports = reports_by_order.get(code, [])
            quantity = sum(self._to_int(row.get("quantity")) for row in wpos)
            wpo_planned = sum(self._to_int(row.get("planned_quantity")) for row in wpos)
            wpo_produced = sum(self._to_int(row.get("produced_quantity")) for row in wpos)
            task_planned = sum(self._to_int(row.get("planned_quantity")) for row in tasks)
            task_produced = sum(self._to_int(row.get("produced_quantity")) for row in tasks)
            manual_good = sum(self._to_int(row.get("operator_quantity")) for row in reports)
            due = self._parse_date(order.get("delivery_time"))
            days_to_due = (due.date() - datetime.now().date()).days if due else None
            report_gap = manual_good - task_planned
            data_sanity_flags = self._order_data_sanity_flags(
                days_to_due=days_to_due,
                planned_quantity=task_planned,
                produced_quantity=task_produced,
                manual_good_quantity=manual_good,
                quantity=quantity,
                wpo_planned_quantity=wpo_planned,
            )
            aggregate = {
                "produce_order_code": code,
                "delivery_time": order.get("delivery_time"),
                "days_to_due": days_to_due,
                "order_status": order.get("status"),
                "wpo_count": len(wpos),
                "planned_task_count": len(tasks),
                "report_row_count": len(reports),
                "quantity": quantity,
                "wpo_planned_quantity": wpo_planned,
                "wpo_produced_quantity": wpo_produced,
                "planned_quantity": task_planned,
                "produced_quantity": task_produced,
                "manual_report_good_quantity": manual_good,
                "quantity_report_gap": report_gap,
                "quantity_report_gap_ratio": self._ratio(abs(report_gap), task_planned) if task_planned else 0,
                "unscheduled_quantity": max(quantity - wpo_planned, 0),
                "remaining_quantity": max(quantity - max(wpo_produced, manual_good), 0),
                "plan_completion_rate": self._ratio(task_produced, task_planned),
                "evidence_credibility": "needs_reconciliation" if data_sanity_flags else "usable_export_evidence",
                "data_sanity_flags": data_sanity_flags,
                "data_gaps": self._order_data_gap_notes(data_sanity_flags),
                "sample_weaving_part_order_ids": self._sample([row.get("id") for row in wpos], 3),
                "sample_planned_task_ids": self._sample([row.get("id") for row in tasks], 3),
                "sample_machine_ids": self._sample([row.get("machine_id") for row in tasks], 3),
                "field_source": "Produce_Order.delivery_time + active Weaving_Part_Order quantities + active Planned_Task quantities + active Manual_Machine_Production.operator_quantity",
            }
            aggregate["delivery_risk_drivers"] = self._delivery_risk_drivers(aggregate)
            aggregates.append(aggregate)
        return aggregates

    def _order_evidence_chain(self, order: dict) -> dict:
        return {
            "produce_order_code": order.get("produce_order_code"),
            "delivery_time": order.get("delivery_time"),
            "days_to_due": order.get("days_to_due"),
            "order_status": order.get("order_status"),
            "weaving_part_order_ids": order.get("sample_weaving_part_order_ids", []),
            "planned_task_ids": order.get("sample_planned_task_ids", []),
            "machine_ids": order.get("sample_machine_ids", []),
            "quantity": order.get("quantity"),
            "planned_quantity": order.get("planned_quantity"),
            "produced_quantity": order.get("produced_quantity"),
            "manual_report_good_quantity": order.get("manual_report_good_quantity"),
            "quantity_report_gap": order.get("quantity_report_gap"),
            "quantity_report_gap_ratio": order.get("quantity_report_gap_ratio"),
            "unscheduled_quantity": order.get("unscheduled_quantity"),
            "remaining_quantity": order.get("remaining_quantity"),
            "plan_completion_rate": order.get("plan_completion_rate"),
            "evidence_credibility": order.get("evidence_credibility"),
            "delivery_risk_drivers": order.get("delivery_risk_drivers", []),
            "data_sanity_flags": order.get("data_sanity_flags", []),
            "data_gaps": order.get("data_gaps", []),
            "field_source": order.get("field_source"),
            "evidence_refs": [
                f"Produce_Order.code={order.get('produce_order_code')}",
                *[f"Weaving_Part_Order.id={item}" for item in order.get("sample_weaving_part_order_ids", [])],
                *[f"Planned_Task.id={item}" for item in order.get("sample_planned_task_ids", [])],
            ],
        }

    def _is_current_delivery_risk_candidate(self, order: dict) -> bool:
        return any(driver.get("classification") == "delivery_risk" for driver in order.get("delivery_risk_drivers", self._delivery_risk_drivers(order)))

    def _has_delivery_reconciliation_driver(self, order: dict) -> bool:
        return any(driver.get("classification") == "data_reconciliation" for driver in order.get("delivery_risk_drivers", self._delivery_risk_drivers(order)))

    def _delivery_risk_drivers(self, order: dict) -> list[dict]:
        days_to_due = order.get("days_to_due")
        completion = order.get("plan_completion_rate", 0) or 0
        unscheduled = order.get("unscheduled_quantity", 0) or 0
        drivers: list[dict] = []
        if days_to_due is not None and days_to_due <= CURRENT_DELIVERY_OVERDUE_REVIEW_DAYS:
            drivers.append(
                self._delivery_driver(
                    "stale_due_date_status_review",
                    "data_reconciliation",
                    "Produce_Order.delivery_time",
                    days_to_due,
                    f"<= {CURRENT_DELIVERY_OVERDUE_REVIEW_DAYS} days",
                    "Delivery date is 30 or more days overdue, so Athena needs order-status confirmation before showing it as a current delivery risk.",
                    "交期已经逾期 30 天或以上，Athena 需要先确认订单是否已关闭、取消或属于历史遗留，不能直接当作当前交付风险。",
                )
            )
            return drivers
        if completion >= COMPLETED_PLAN_RATE_THRESHOLD:
            if unscheduled > 0:
                drivers.append(
                    self._delivery_driver(
                        "plan_complete_but_part_order_unscheduled_quantity",
                        "data_reconciliation",
                        "Planned_Task.produced_quantity / Planned_Task.planned_quantity + Weaving_Part_Order.quantity - Weaving_Part_Order.planned_quantity",
                        {"plan_completion_rate": completion, "unscheduled_quantity": unscheduled},
                        f"completion >= {COMPLETED_PLAN_RATE_THRESHOLD:.0%}",
                        "Planned tasks are essentially complete while part-order quantity still appears unscheduled; this is a planning/status reconciliation candidate, not a delivery-risk conclusion.",
                        "计划任务基本完成，但部件单仍显示未排数量；这属于排产/状态口径复核候选，不应直接归类为交付风险。",
                    )
                )
            if order.get("data_sanity_flags"):
                drivers.append(
                    self._delivery_driver(
                        "plan_complete_but_export_needs_reconciliation",
                        "data_reconciliation",
                        "Manual_Machine_Production.operator_quantity + Planned_Task.planned_quantity + data_sanity_flags",
                        order.get("data_sanity_flags", []),
                        "no sanity flags",
                        "Plan completion is essentially complete, but quantity evidence has sanity flags; reconcile the export before claiming delivery risk.",
                        "计划完成率基本完成，但数量证据存在复核标记；需要先复核导出口径，不能直接声称交付风险。",
                    )
                )
            return drivers
        if days_to_due is not None and days_to_due <= 14:
            drivers.append(
                self._delivery_driver(
                    "near_due_incomplete_plan",
                    "delivery_risk",
                    "Produce_Order.delivery_time + Planned_Task.produced_quantity / Planned_Task.planned_quantity",
                    {"days_to_due": days_to_due, "plan_completion_rate": completion},
                    "days_to_due <= 14 and completion < 98%",
                    "Order is due within 14 days or already overdue inside the current review window, and planned-task completion is not close to complete.",
                    "订单在 14 天内到期或处于当前复核窗口内逾期，同时计划任务完成率尚未接近完成。",
                )
            )
        if unscheduled > 0 and (days_to_due is None or days_to_due <= CURRENT_DELIVERY_LOOKAHEAD_DAYS):
            drivers.append(
                self._delivery_driver(
                    "unscheduled_quantity_in_delivery_window",
                    "delivery_risk",
                    "Weaving_Part_Order.quantity - Weaving_Part_Order.planned_quantity",
                    unscheduled,
                    f"> 0 within {CURRENT_DELIVERY_LOOKAHEAD_DAYS} days",
                    "Part-order quantity is still not fully scheduled inside the delivery lookahead window.",
                    "交付观察窗口内仍有部件单数量未排满。",
                )
            )
        if completion < 0.8 and (days_to_due is None or days_to_due <= CURRENT_DELIVERY_LOOKAHEAD_DAYS):
            drivers.append(
                self._delivery_driver(
                    "low_plan_completion_in_delivery_window",
                    "delivery_risk",
                    "Planned_Task.produced_quantity / Planned_Task.planned_quantity",
                    completion,
                    "< 80% within delivery lookahead window",
                    "Planned-task completion is below the management warning threshold inside the delivery lookahead window.",
                    "交付观察窗口内计划任务完成率低于管理预警阈值。",
                )
            )
        return drivers

    def _delivery_driver(
        self,
        driver: str,
        classification: str,
        field_source: str,
        value,
        threshold: str,
        explanation_en: str,
        explanation_zh: str,
    ) -> dict:
        return {
            "driver": driver,
            "classification": classification,
            "field_source": field_source,
            "value": value,
            "threshold": threshold,
            "explanation_en": explanation_en,
            "explanation_zh": explanation_zh,
        }

    def _delivery_reconciliation_card(self, order: dict, language: str) -> dict:
        chain = self._order_evidence_chain(order)
        drivers = [driver for driver in order.get("delivery_risk_drivers", []) if driver.get("classification") == "data_reconciliation"]
        driver_text = self._driver_explanations(drivers, language)
        why_not = self._choose(
            language,
            (
                f"Order {order.get('produce_order_code')} is not a confirmed hard delivery risk yet. "
                f"Plan completion is {order.get('plan_completion_rate', 0):.1%}, but the export evidence has reconciliation drivers: {driver_text}. "
                "Athena should ask planning to confirm order status and quantity scope before claiming delivery risk."
            ),
            (
                f"订单 {order.get('produce_order_code')} 目前不能直接算硬性交付风险。"
                f"计划完成率为 {order.get('plan_completion_rate', 0):.1%}，但导出证据存在复核触发项：{driver_text}。"
                "Athena 需要先请计划负责人确认订单状态和数量口径，再判断是否真的影响交付。"
            ),
        )
        cannot_conclude = self._choose(
            language,
            "Athena cannot conclude delivery risk because completion, due-date status, unscheduled quantity, or reporting quantity evidence is internally inconsistent.",
            "Athena 不能直接下交付风险结论，因为完成率、交期状态、未排量或报工量证据之间存在口径冲突。",
        )
        action = self._choose(
            language,
            "Confirm whether the order is closed, split, historically overdue, intentionally left open, or using a different quantity-reporting scope.",
            "确认订单是否已关闭、拆单、历史逾期、故意保留未排，或使用了不同的数量报工口径。",
        )
        return {
            "card_id": f"EVID-REVIEW-{order.get('produce_order_code')}",
            "object_type": "produce_order",
            "object_id": order.get("produce_order_code"),
            "produce_order_code": order.get("produce_order_code"),
            "review_type": "delivery_status_or_quantity_reconciliation",
            "status": "needs_planning_confirmation",
            "why_not_delivery_risk": why_not,
            "reconciliation_drivers": drivers,
            "plan_completion_rate": order.get("plan_completion_rate"),
            "days_to_due": order.get("days_to_due"),
            "delivery_time": order.get("delivery_time"),
            "unscheduled_quantity": order.get("unscheduled_quantity"),
            "quantity_report_gap": order.get("quantity_report_gap"),
            "quantity_report_gap_ratio": order.get("quantity_report_gap_ratio"),
            "quantity_gap_review_status": order.get("quantity_gap_review_status"),
            "evidence_credibility": order.get("evidence_credibility", "needs_reconciliation"),
            "sanity_flags": order.get("data_sanity_flags", []),
            "field_source": order.get("field_source"),
            "field_sources": self._unique_refs([order.get("field_source")] + [driver.get("field_source") for driver in drivers]),
            "suggested_confirmation_owner": "Planning Manager / APS Owner",
            "suggested_confirmation_action": action,
            "cannot_conclude_reason": cannot_conclude,
            "read_only_boundary": {
                "read_only": True,
                "blocked_actions": ["write_aps", "write_erp", "write_iot", "change_schedule", "dispatch_service"],
            },
            "drilldown_question": self._choose(
                language,
                f"Why is order {order.get('produce_order_code')} an evidence review candidate instead of a hard delivery risk?",
                f"为什么订单 {order.get('produce_order_code')} 不是硬性交付风险，而是数据复核候选？",
            ),
            "evidence_chain": chain,
            "evidence_refs": chain.get("evidence_refs", []),
            "data_gaps": order.get("data_gaps", []),
        }

    def _driver_explanations(self, drivers: list[dict], language: str) -> str:
        if not drivers:
            return self._choose(language, "no explicit reconciliation driver", "娌℃湁鏄庣‘澶嶆牳瑙﹀彂椤?")
        key = "explanation_en" if language == "en" else "explanation_zh"
        return "; ".join(driver.get(key, driver.get("driver", "")) for driver in drivers)

    def _delivery_risk_cause(self, chain: dict, language: str) -> str:
        drivers = [driver for driver in chain.get("delivery_risk_drivers", []) if driver.get("classification") == "delivery_risk"]
        if not drivers:
            return self._choose(
                language,
                f"Order {chain['produce_order_code']} needs delivery evidence review, but no hard delivery-risk driver is available after completion and sanity checks.",
                f"订单 {chain['produce_order_code']} 需要做交付证据复核；经过完成率和数据口径检查后，目前没有足够证据把它作为硬性交付风险。",
            )
        key = "explanation_en" if language == "en" else "explanation_zh"
        driver_text = "; ".join(driver.get(key, driver.get("driver", "")) for driver in drivers)
        return self._choose(
            language,
            f"Order {chain['produce_order_code']} is a delivery-risk candidate because: {driver_text} Plan completion is {chain.get('plan_completion_rate'):.1%}; evidence credibility is {chain.get('evidence_credibility')}.",
            f"订单 {chain['produce_order_code']} 进入交付风险候选的原因是：{driver_text} 计划完成率为 {chain.get('plan_completion_rate'):.1%}；证据可信度为 {chain.get('evidence_credibility')}。",
        )

    def _order_data_sanity_flags(
        self,
        *,
        days_to_due: int | None,
        planned_quantity: int,
        produced_quantity: int,
        manual_good_quantity: int,
        quantity: int,
        wpo_planned_quantity: int,
    ) -> list[str]:
        flags: list[str] = []
        if days_to_due is not None and days_to_due <= CURRENT_DELIVERY_OVERDUE_REVIEW_DAYS:
            flags.append("stale_delivery_date_needs_order_status_review")
        report_gap = manual_good_quantity - planned_quantity
        if self._is_extreme_quantity_gap(report_gap, planned_quantity):
            flags.append("extreme_manual_report_vs_plan_gap_needs_reconciliation")
        if planned_quantity and produced_quantity > planned_quantity * 1.2:
            flags.append("produced_quantity_exceeds_plan_needs_reconciliation")
        if quantity and wpo_planned_quantity > max(quantity * 1.2, quantity + EXTREME_QUANTITY_GAP_ABSOLUTE):
            flags.append("planned_part_quantity_exceeds_order_quantity_needs_reconciliation")
        return flags

    def _is_extreme_quantity_gap(self, gap: int, planned_quantity: int) -> bool:
        if not planned_quantity:
            return False
        return abs(gap) > EXTREME_QUANTITY_GAP_ABSOLUTE or abs(gap) > planned_quantity * EXTREME_QUANTITY_GAP_RATIO

    def _order_data_gap_notes(self, flags: list[str]) -> list[str]:
        notes = {
            "stale_delivery_date_needs_order_status_review": "Delivery date is more than 30 days overdue; confirm whether the order is closed, cancelled, deleted, or historical before showing it as a current risk.",
            "extreme_manual_report_vs_plan_gap_needs_reconciliation": "Manual report quantity and planned quantity differ beyond the sanity threshold; reconcile by task_id, barcode, reporting date, and split-task policy before claiming production loss.",
            "produced_quantity_exceeds_plan_needs_reconciliation": "Produced quantity exceeds planned quantity beyond the sanity threshold; confirm reporting and split-plan rules.",
            "planned_part_quantity_exceeds_order_quantity_needs_reconciliation": "Part-order planned quantity exceeds order quantity beyond the sanity threshold; confirm whether quantity fields use the same unit and scope.",
        }
        return [notes[flag] for flag in flags if flag in notes]

    def _group_by(self, rows: list[dict[str, str]], field: str) -> dict[str, list[dict[str, str]]]:
        output: dict[str, list[dict[str, str]]] = {}
        for row in rows:
            key = row.get(field)
            if key:
                output.setdefault(key, []).append(row)
        return output

    def _unique_refs(self, refs: list[str | None]) -> list[str]:
        return [item for item in dict.fromkeys(ref for ref in refs if ref)]

    def _choose(self, language: str, en: str, zh: str) -> str:
        return zh if language == "zh" else en

    def _cache_signature(self) -> tuple[str, tuple[tuple[str, float | None], ...]]:
        paths = [self.export_dir / "field_schema.sql", self.export_dir / FIELD_SCHEMA_FILE_NAME] + [
            self.export_dir / file_name for file_name in TABLE_FILE_NAMES.values()
        ]
        mtimes = []
        for path in paths:
            mtimes.append((path.name, path.stat().st_mtime if path.exists() else None))
        return (str(self.export_dir), tuple(mtimes))

    def _missing_report(self, loads: dict[str, TableLoad], unavailable: list[str]) -> dict:
        return {
            "adapter_id": self.adapter_id,
            "version": ADAPTER_VERSION,
            "source": "Tianpai APS/ERP CSV export",
            "adapter_status": "missing_external_csv",
            "read_only": True,
            "raw_file_stored_in_repo": False,
            "export_dir": str(self.export_dir),
            "table_field_source": "field schema DDL order",
            "schema_source_file": FIELD_SCHEMA_FILE_NAME,
            "tables": {
                name: {
                    "file_name": load.file_name,
                    "row_count": len(load.rows),
                    "field_count": len(load.fields),
                    "fields": load.fields,
                    "exists": load.exists,
                    "error": load.error,
                }
                for name, load in loads.items()
            },
            "standard_objects": {},
            "data_quality_report": {
                "status": "missing_external_source",
                "unavailable_tables": unavailable,
                "join_quality": [],
                "missing_fields": [],
                "unmatched_records": [],
            },
            "capability_boundary": {
                "available": [],
                "unavailable": [
                    "Actual APS/ERP snapshot cannot be calculated until all required external CSV files are present.",
                ],
            },
            "blocked_actions": [
                "copy_raw_customer_csv_into_repo",
                "write_back_to_erp_or_aps",
                "confirm_schedule",
                "release_order_to_machine",
                "modify_customer_data",
            ],
        }

    def _load_tables(self) -> dict[str, TableLoad]:
        signature = self._cache_signature()
        if signature in _TABLE_LOAD_CACHE:
            return _TABLE_LOAD_CACHE[signature]
        ddl_fields = self._parse_ddl_fields()
        loads: dict[str, TableLoad] = {}
        for table_name, file_name in TABLE_FILE_NAMES.items():
            fields = ddl_fields.get(table_name) or FALLBACK_FIELD_ORDER[table_name]
            path = self.export_dir / file_name
            if not path.exists():
                loads[table_name] = TableLoad(table_name, file_name, fields, [], False, "file_not_found")
                continue
            try:
                rows = self._read_no_header_csv(path, fields)
                loads[table_name] = TableLoad(table_name, file_name, fields, rows, True)
            except Exception as exc:  # pragma: no cover - defensive file adapter
                loads[table_name] = TableLoad(table_name, file_name, fields, [], True, repr(exc))
        _TABLE_LOAD_CACHE[signature] = loads
        return loads

    def _parse_ddl_fields(self) -> dict[str, list[str]]:
        path = self.export_dir / FIELD_SCHEMA_FILE_NAME
        if not path.exists():
            path = self.export_dir / "field_schema.sql"
        if not path.exists():
            return {}
        text = path.read_text(encoding="utf-8")
        result: dict[str, list[str]] = {}
        matches = re.finditer(
            r"create\s+table\s+(?:aps\.)?`?(?P<table>[A-Za-z_]+)`?\s*\((?P<body>.*?)\)\s*;",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        for match in matches:
            table = match.group("table")
            body = match.group("body")
            fields = []
            for raw_line in body.splitlines():
                line = raw_line.strip().rstrip(",")
                if not line or line.lower().startswith(("primary key", "constraint", "unique", "index")):
                    continue
                token = line.split(None, 1)[0].strip("`")
                if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", token):
                    fields.append(token)
            if fields:
                result[table] = fields
        return result

    def _read_no_header_csv(self, path: Path, fields: list[str]) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            for values in reader:
                row = {field: values[index] if index < len(values) else "" for index, field in enumerate(fields)}
                if len(values) > len(fields):
                    row["_extra_columns"] = str(len(values) - len(fields))
                rows.append(row)
        return rows

    def _active_rows(self, table_name: str, rows: list[dict[str, str]]) -> list[dict[str, str]]:
        if table_name == "T_Machine_Info":
            return [row for row in rows if self._is_active_flag(row.get("f_deleted"))]
        if rows and "deleted_at" in rows[0]:
            return [row for row in rows if self._is_active_flag(row.get("deleted_at"))]
        return rows

    @staticmethod
    def _is_active_flag(value: str | None) -> bool:
        text = str(value or "").strip()
        return text in {"", "0", "0.0", "false", "False", "FALSE"}

    def _normalized_objects(self, tables: dict[str, list[dict[str, str]]]) -> dict:
        produce_orders = tables["Produce_Order"]
        weaving_orders = tables["Weaving_Part_Order"]
        tasks = tables["Planned_Task"]
        reports = tables["Manual_Machine_Production"]
        components = tables["Style_Component"]
        skus = tables["Style_Sku"]
        machines = tables["T_Machine_Info"]
        machine_ids = {row.get("f_machine_id") for row in machines if row.get("f_machine_id")}
        machine_plan_load = self._machine_plan_load(tasks, machines)
        machine_style_mismatches = self._machine_style_mismatch_candidates(tasks, weaving_orders, components, machines)

        planned_quantity = sum(self._to_int(row.get("planned_quantity")) for row in tasks)
        task_produced_quantity = sum(self._to_int(row.get("produced_quantity")) for row in tasks)
        report_good_quantity = sum(self._to_int(row.get("operator_quantity")) for row in reports)
        report_defects = sum(
            self._to_int(row.get("operator_defects")) + self._to_int(row.get("inspector_defects"))
            for row in reports
        )
        scheduled_weaving_orders = len([
            row for row in weaving_orders if self._to_int(row.get("planned_quantity")) > 0
        ])
        unscheduled_weaving_orders = len(weaving_orders) - scheduled_weaving_orders
        near_due_orders = len([
            row for row in produce_orders if self._days_until(row.get("delivery_time")) is not None and self._days_until(row.get("delivery_time")) <= 14
        ])

        return {
            "schema_id": "athena.tianpai_aps_erp_standard_objects.v1",
            "object_counts": {
                "production_order": len(produce_orders),
                "weaving_part_order": len(weaving_orders),
                "planned_task": len(tasks),
                "machine_production_report": len(reports),
                "style_component": len(components),
                "style_sku": len(skus),
                "machine": len(machines),
            },
            "canonical_join_chain": [
                "Produce_Order.code",
                "Weaving_Part_Order.produce_order_code",
                "Planned_Task.weaving_part_order_id",
                "Manual_Machine_Production.task_id",
            ],
            "actual_snapshot_metrics": {
                "total_order_count": len(produce_orders),
                "near_due_order_count": near_due_orders,
                "weaving_part_order_count": len(weaving_orders),
                "scheduled_weaving_part_order_count": scheduled_weaving_orders,
                "unscheduled_weaving_part_order_count": unscheduled_weaving_orders,
                "planned_task_count": len(tasks),
                "machine_count": len({row.get("f_machine_code") for row in machines if row.get("f_machine_code")}),
                "planned_quantity": planned_quantity,
                "planned_task_produced_quantity": task_produced_quantity,
                "manual_report_good_quantity": report_good_quantity,
                "manual_report_defect_quantity": report_defects,
                "plan_completion_rate": self._ratio(task_produced_quantity, planned_quantity),
                "manual_report_completion_rate": self._ratio(report_good_quantity, planned_quantity),
                "task_machine_coverage_rate": self._ratio(
                    len([row for row in tasks if row.get("machine_id") in machine_ids]),
                    len(tasks),
                ),
                "machine_plan_load_candidate_count": len(machine_plan_load),
                "top_machine_planned_quantity": machine_plan_load[0]["planned_quantity"] if machine_plan_load else 0,
                "machine_style_spec_mismatch_candidate_count": machine_style_mismatches["candidate_count_total"],
            },
            "machine_plan_load": machine_plan_load[:10],
            "machine_style_spec_mismatch_candidates": machine_style_mismatches,
            "sample_keys": {
                "produce_order_codes": self._sample([row.get("code") for row in produce_orders]),
                "weaving_part_order_ids": self._sample([row.get("id") for row in weaving_orders]),
                "planned_task_ids": self._sample([row.get("id") for row in tasks]),
                "machine_codes": self._sample([row.get("f_machine_code") for row in machines]),
            },
        }

    def _machine_plan_load(self, tasks: list[dict[str, str]], machines: list[dict[str, str]]) -> list[dict]:
        machine_by_id = {row.get("f_machine_id"): row for row in machines if row.get("f_machine_id")}
        load_by_machine: dict[str, dict] = {}
        for task in tasks:
            machine_id = task.get("machine_id")
            if not machine_id:
                continue
            machine = machine_by_id.get(machine_id, {})
            load = load_by_machine.setdefault(
                machine_id,
                {
                    "machine_id": machine_id,
                    "machine_code": machine.get("f_machine_code") or machine_id,
                    "machine_type": machine.get("f_machine_type") or "",
                    "task_count": 0,
                    "planned_quantity": 0,
                    "produced_quantity": 0,
                    "completion_rate": 0,
                    "plan_start_time_min": None,
                    "plan_end_time_max": None,
                    "evidence_refs": [],
                },
            )
            load["task_count"] += 1
            load["planned_quantity"] += self._to_int(task.get("planned_quantity"))
            load["produced_quantity"] += self._to_int(task.get("produced_quantity"))
            start = self._parse_date(task.get("plan_start_time"))
            end = self._parse_date(task.get("plan_end_time"))
            if start and (load["plan_start_time_min"] is None or start < load["plan_start_time_min"]):
                load["plan_start_time_min"] = start
            if end and (load["plan_end_time_max"] is None or end > load["plan_end_time_max"]):
                load["plan_end_time_max"] = end
            if len(load["evidence_refs"]) < 5 and task.get("id"):
                load["evidence_refs"].append(f"Planned_Task.id={task.get('id')}")

        output = []
        for load in load_by_machine.values():
            load["completion_rate"] = self._ratio(load["produced_quantity"], load["planned_quantity"])
            load["plan_start_time_min"] = load["plan_start_time_min"].strftime("%Y-%m-%d") if load["plan_start_time_min"] else None
            load["plan_end_time_max"] = load["plan_end_time_max"].strftime("%Y-%m-%d") if load["plan_end_time_max"] else None
            output.append(load)
        return sorted(output, key=lambda item: (item["planned_quantity"], item["task_count"]), reverse=True)

    def _machine_style_mismatch_candidates(
        self,
        tasks: list[dict[str, str]],
        weaving_orders: list[dict[str, str]],
        components: list[dict[str, str]],
        machines: list[dict[str, str]],
    ) -> dict:
        weaving_by_id = {row.get("id"): row for row in weaving_orders if row.get("id")}
        component_by_key = {
            self._component_key(row.get("produce_order_code"), row.get("sku_code"), row.get("part")): row
            for row in components
        }
        machine_by_id = {row.get("f_machine_id"): row for row in machines if row.get("f_machine_id")}
        candidates = []
        total = 0

        for task in tasks:
            machine = machine_by_id.get(task.get("machine_id"))
            if not machine:
                continue
            weaving = weaving_by_id.get(task.get("weaving_part_order_id"), {})
            component = component_by_key.get(
                self._component_key(
                    weaving.get("produce_order_code") or task.get("produce_order_code"),
                    weaving.get("sku_code") or task.get("sku_code"),
                    weaving.get("part") or task.get("part"),
                )
            )
            if not component:
                continue
            required_diameter = self._normalize_spec_number(component.get("cylinder_diameter"))
            machine_diameter = self._normalize_spec_number(machine.get("f_cylinder_diameter"))
            required_needle = self._normalize_spec_number(component.get("needle_spacing"))
            machine_needle = self._normalize_spec_number(machine.get("f_needle_spacing"))
            diameter_mismatch = required_diameter is not None and machine_diameter is not None and required_diameter != machine_diameter
            needle_mismatch = required_needle is not None and machine_needle is not None and required_needle != machine_needle
            if not diameter_mismatch and not needle_mismatch:
                continue
            mismatch_details = []
            if diameter_mismatch:
                mismatch_details.append(
                    {
                        "field": "cylinder_diameter",
                        "field_label_zh": "绛掑緞",
                        "required_value": component.get("cylinder_diameter"),
                        "actual_machine_value": machine.get("f_cylinder_diameter"),
                        "required_field_source": "Style_Component.cylinder_diameter",
                        "actual_field_source": "T_Machine_Info.f_cylinder_diameter",
                    }
                )
            if needle_mismatch:
                mismatch_details.append(
                    {
                        "field": "needle_spacing",
                        "field_label_zh": "閽堣窛",
                        "required_value": component.get("needle_spacing"),
                        "actual_machine_value": machine.get("f_needle_spacing"),
                        "required_field_source": "Style_Component.needle_spacing",
                        "actual_field_source": "T_Machine_Info.f_needle_spacing",
                    }
                )
            total += 1
            if len(candidates) >= 20:
                continue
            candidates.append(
                {
                    "produce_order_code": task.get("produce_order_code") or weaving.get("produce_order_code"),
                    "weaving_part_order_id": task.get("weaving_part_order_id"),
                    "planned_task_id": task.get("id"),
                    "machine_id": task.get("machine_id"),
                    "machine_code": machine.get("f_machine_code"),
                    "style_code": task.get("style_code") or weaving.get("style_code"),
                    "sku_code": task.get("sku_code") or weaving.get("sku_code"),
                    "part": task.get("part") or weaving.get("part"),
                    "required_cylinder_diameter": component.get("cylinder_diameter"),
                    "machine_cylinder_diameter": machine.get("f_cylinder_diameter"),
                    "required_needle_spacing": component.get("needle_spacing"),
                    "machine_needle_spacing": machine.get("f_needle_spacing"),
                    "mismatch_details": mismatch_details,
                    "mismatch_fields": [
                        field
                        for field, flag in {
                            "cylinder_diameter": diameter_mismatch,
                            "needle_spacing": needle_mismatch,
                        }.items()
                        if flag
                    ],
                    "evidence_refs": [
                        f"Planned_Task.id={task.get('id')}",
                        f"Style_Component.id={component.get('id')}",
                        f"T_Machine_Info.f_machine_id={machine.get('f_machine_id')}",
                    ],
                    "field_source": "Style_Component.cylinder_diameter/needle_spacing vs T_Machine_Info.f_cylinder_diameter/f_needle_spacing",
                }
            )

        return {
            "candidate_count_total": total,
            "sample_limit": 20,
            "candidates": candidates,
        }

    def _data_quality(self, tables: dict[str, list[dict[str, str]]]) -> dict:
        produce_orders = tables["Produce_Order"]
        weaving_orders = tables["Weaving_Part_Order"]
        tasks = tables["Planned_Task"]
        reports = tables["Manual_Machine_Production"]
        components = tables["Style_Component"]
        machines = tables["T_Machine_Info"]

        produce_order_codes = {row.get("code") for row in produce_orders if row.get("code")}
        weaving_ids = {row.get("id") for row in weaving_orders if row.get("id")}
        task_ids = {row.get("id") for row in tasks if row.get("id")}
        machine_ids = {row.get("f_machine_id") for row in machines if row.get("f_machine_id")}
        component_keys = {
            self._component_key(row.get("produce_order_code"), row.get("sku_code"), row.get("part"))
            for row in components
        }

        wpo_order_matches = [row for row in weaving_orders if row.get("produce_order_code") in produce_order_codes]
        task_wpo_matches = [row for row in tasks if row.get("weaving_part_order_id") in weaving_ids]
        report_task_matches = [row for row in reports if row.get("task_id") in task_ids]
        task_machine_matches = [row for row in tasks if row.get("machine_id") in machine_ids]
        wpo_component_matches = [
            row
            for row in weaving_orders
            if self._component_key(row.get("produce_order_code"), row.get("sku_code"), row.get("part")) in component_keys
        ]
        defect_rows = [
            row
            for row in reports
            if self._to_float(row.get("operator_defects")) > 0
            or self._to_float(row.get("inspector_defects")) > 0
            or self._to_float(row.get("operator_discards")) > 0
        ]

        return {
            "schema_id": "athena.tianpai_aps_erp_data_quality.v1",
            "status": "actual_export_loaded",
            "join_quality": [
                self._join_metric("weaving_part_order_to_produce_order", len(wpo_order_matches), len(weaving_orders), "Weaving_Part_Order.produce_order_code -> Produce_Order.code"),
                self._join_metric("planned_task_to_weaving_part_order", len(task_wpo_matches), len(tasks), "Planned_Task.weaving_part_order_id -> Weaving_Part_Order.id"),
                self._join_metric("manual_report_to_planned_task", len(report_task_matches), len(reports), "Manual_Machine_Production.task_id -> Planned_Task.id"),
                self._join_metric("planned_task_to_machine", len(task_machine_matches), len(tasks), "Planned_Task.machine_id -> T_Machine_Info.f_machine_id"),
                self._join_metric("weaving_part_order_to_style_component", len(wpo_component_matches), len(weaving_orders), "produce_order_code + sku_code + part -> Style_Component"),
            ],
            "missing_fields": self._missing_required_fields(tables),
            "unmatched_records": [
                self._unmatched_metric("weaving_part_order_without_produce_order", len(weaving_orders) - len(wpo_order_matches)),
                self._unmatched_metric("planned_task_without_weaving_part_order", len(tasks) - len(task_wpo_matches)),
                self._unmatched_metric("manual_report_without_planned_task", len(reports) - len(report_task_matches)),
                self._unmatched_metric("planned_task_without_machine", len(tasks) - len(task_machine_matches)),
                self._unmatched_metric("weaving_part_order_without_style_component", len(weaving_orders) - len(wpo_component_matches)),
            ],
            "field_quality_notes": [
                {
                    "field_group": "quality_defect_fields",
                    "status": "not_useful_yet" if not defect_rows else "available",
                    "detail": "Manual_Machine_Production defect/discard fields are all zero in the current export." if not defect_rows else "Defect/discard rows are present.",
                    "nonzero_row_count": len(defect_rows),
                },
                {
                    "field_group": "iot_runtime_fields",
                    "status": "not_in_export",
                    "detail": "This APS/ERP export does not contain live OEE, alarm, downtime, or service-ticket records.",
                },
            ],
            "date_ranges": {
                "order_delivery_time": self._date_range([row.get("delivery_time") for row in produce_orders]),
                "weaving_finish_time": self._date_range([row.get("finish_time") for row in weaving_orders]),
                "task_plan_start_time": self._date_range([row.get("plan_start_time") for row in tasks]),
                "task_plan_end_time": self._date_range([row.get("plan_end_time") for row in tasks]),
                "manual_report_date": self._date_range([row.get("date") for row in reports]),
            },
            "status_counts": {
                "produce_order_status": self._counter(produce_orders, "status"),
                "weaving_part_order_status": self._counter(weaving_orders, "status"),
                "planned_task_status": self._counter(tasks, "status"),
            },
        }

    def _capability_boundary(self, tables: dict[str, list[dict[str, str]]], quality: dict) -> dict:
        defect_note = quality["field_quality_notes"][0]
        return {
            "available": [
                "Actual production order count and delivery-time distribution.",
                "Actual weaving part order progress and scheduled/unscheduled part counts.",
                "Actual planned task quantity, produced quantity, and plan completion rate.",
                "Actual manual production report aggregation by task/order/sku/part/machine code.",
                "Machine-to-task coverage and machine load candidates.",
                "Style component machine-spec requirement checks using cylinder diameter and needle spacing.",
            ],
            "unavailable": [
                "Quality scrap root cause from this export." if defect_note["status"] == "not_useful_yet" else "",
                "Live OEE, downtime, alarm, and service escalation root cause without IOT runtime data.",
                "Purchasing/labor/freight cost root cause without cost records.",
                "Automatic schedule modification or ERP/APS write-back.",
            ],
            "next_prd_step": "Use the v0.113.3 delivery risk driver guard and actual-data Q&A evidence chains as the regression baseline for management question training.",
        }

    def _missing_required_fields(self, tables: dict[str, list[dict[str, str]]]) -> list[dict]:
        required = {
            "Produce_Order": ["code", "delivery_time", "status"],
            "Weaving_Part_Order": ["id", "produce_order_code", "sku_code", "part", "quantity", "planned_quantity", "produced_quantity", "finish_time"],
            "Planned_Task": ["id", "produce_order_code", "weaving_part_order_id", "machine_id", "planned_quantity", "produced_quantity", "plan_start_time", "plan_end_time"],
            "Manual_Machine_Production": ["task_id", "produce_order_code", "sku_code", "part", "device_id", "date", "operator_quantity"],
            "Style_Component": ["produce_order_code", "sku_code", "part", "cylinder_diameter", "needle_spacing", "expected_produce_time", "yarn_usage"],
            "T_Machine_Info": ["f_machine_id", "f_machine_code", "f_cylinder_diameter", "f_needle_spacing"],
        }
        missing = []
        for table, fields in required.items():
            rows = tables.get(table, [])
            for field in fields:
                blank_count = len([row for row in rows if not row.get(field)])
                if blank_count:
                    missing.append(
                        {
                            "table": table,
                            "field": field,
                            "blank_count": blank_count,
                            "row_count": len(rows),
                            "blank_rate": self._ratio(blank_count, len(rows)),
                        }
                    )
        return missing

    def _join_metric(self, join_id: str, matched: int, total: int, key: str) -> dict:
        return {
            "join_id": join_id,
            "key": key,
            "matched_records": matched,
            "total_records": total,
            "unmatched_records": max(total - matched, 0),
            "match_rate": self._ratio(matched, total),
        }

    def _unmatched_metric(self, name: str, count: int) -> dict:
        return {"name": name, "count": count}

    def _component_key(self, produce_order_code: str | None, sku_code: str | None, part: str | None) -> str:
        return f"{produce_order_code or ''}|{sku_code or ''}|{part or ''}"

    def _ratio(self, numerator: int | float, denominator: int | float) -> float:
        return round((float(numerator) / float(denominator)), 4) if denominator else 0.0

    def _to_int(self, value: str | None) -> int:
        try:
            return int(float(value or 0))
        except (TypeError, ValueError):
            return 0

    def _to_float(self, value: str | None) -> float:
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0

    def _normalize_spec_number(self, value: str | None) -> int | None:
        if value is None:
            return None
        match = re.search(r"\d+", str(value))
        return int(match.group(0)) if match else None

    def _parse_date(self, value: str | None) -> datetime | None:
        if not value:
            return None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(value.strip(), fmt)
            except ValueError:
                continue
        return None

    def _days_until(self, value: str | None) -> int | None:
        parsed = self._parse_date(value)
        if not parsed:
            return None
        return (parsed.date() - datetime.now().date()).days

    def _date_range(self, values: list[str | None]) -> dict:
        dates = sorted(parsed for parsed in (self._parse_date(value) for value in values) if parsed)
        if not dates:
            return {"start": None, "end": None}
        return {"start": dates[0].strftime("%Y-%m-%d"), "end": dates[-1].strftime("%Y-%m-%d")}

    def _counter(self, rows: list[dict[str, str]], field: str) -> dict:
        return dict(Counter(row.get(field, "") for row in rows).most_common(10))

    def _sample(self, values: list[str | None], limit: int = 5) -> list[str]:
        output = []
        seen = set()
        for value in values:
            if value and value not in seen:
                output.append(value)
                seen.add(value)
            if len(output) >= limit:
                break
        return output




