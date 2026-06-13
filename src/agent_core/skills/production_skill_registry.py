"""Production skill contracts for Athena's general-manager workflow."""

from __future__ import annotations

from copy import deepcopy


PRODUCTION_SKILL_VERSION = "v0.113.3"

READ_ONLY_BOUNDARY = [
    "read_erp_aps_iot_or_export_evidence_only",
    "do_not_write_aps",
    "do_not_write_erp",
    "do_not_write_iot",
    "do_not_modify_schedule",
    "do_not_dispatch_service",
    "do_not_upload_co_or_cx",
    "do_not_claim_certainty_without_evidence",
]


_SKILLS: list[dict] = [
    {
        "skill_id": "gm_daily_brief_skill",
        "name_zh": "总经理每日三件事技能",
        "name_en": "GM Daily Brief Skill",
        "purpose": "Rank the top three evidence-backed production priorities for a general manager within three minutes.",
        "input_objects": ["management_priority_brief", "production_overview", "actual_data_snapshot", "evidence_log"],
        "required_fields": ["top_priorities", "risk_level", "affected_objects", "evidence_refs", "owner_role"],
        "optional_fields": ["actual_evidence_chains", "field_sources", "data_gaps", "follow_up_contract"],
        "output_contract": ["top_three_risk_cards", "daily_brief_summary", "recommended_sequence"],
        "evidence_requirements": ["ranked risk cards must include evidence_refs and owner confirmation requirement"],
        "read_only_boundary": READ_ONLY_BOUNDARY,
        "demo_status": "internal_demo_ready",
        "limitations": "The ranking is export/mock evidence based and must be validated by a production owner before action.",
    },
    {
        "skill_id": "delivery_risk_skill",
        "name_zh": "交付风险技能",
        "name_en": "Delivery Risk Skill",
        "purpose": "Identify orders or weaving part orders that may affect delivery because of due date, unscheduled quantity, or low plan completion.",
        "input_objects": ["Produce_Order", "Weaving_Part_Order", "Planned_Task", "production_order"],
        "required_fields": ["produce_order_code", "delivery_time", "planned_quantity", "produced_quantity"],
        "optional_fields": ["plan_start_time", "plan_end_time", "weaving_part_order_id", "machine_id"],
        "output_contract": ["delivery_risk_card", "affected_orders", "evidence_chain", "data_gaps"],
        "evidence_requirements": ["order row", "weaving part order or planned task row", "field source"],
        "read_only_boundary": READ_ONLY_BOUNDARY,
        "demo_status": "internal_demo_ready",
        "limitations": "Shipment confirmation and downstream process timestamps are not yet connected.",
    },
    {
        "skill_id": "machine_fit_skill",
        "name_zh": "机台适配技能",
        "name_en": "Machine Fit Skill",
        "purpose": "Check whether machine cylinder diameter and needle spacing match the style/component requirements.",
        "input_objects": ["Style_Component", "T_Machine_Info", "Planned_Task"],
        "required_fields": ["f_cylinder_diameter", "f_needle_spacing", "machine_id", "style_component"],
        "optional_fields": ["sku_code", "part", "machine_code", "task_id"],
        "output_contract": ["machine_style_match_risk", "mismatch_fields", "engineering_confirmation_action"],
        "evidence_requirements": ["style component row", "machine info row", "planned task join"],
        "read_only_boundary": READ_ONLY_BOUNDARY,
        "demo_status": "internal_demo_ready",
        "limitations": "Allowed substitutions and onsite engineering exceptions still require human confirmation.",
    },
    {
        "skill_id": "material_constraint_skill",
        "name_zh": "物料约束技能",
        "name_en": "Material Constraint Skill",
        "purpose": "Identify material, yarn, quantity, or part-order constraints that may block weaving execution.",
        "input_objects": ["Weaving_Part_Order", "Yarn_Product", "material_inventory", "aps_yarn_forecast"],
        "required_fields": ["produce_order_code", "planned_quantity", "scheduled_quantity"],
        "optional_fields": ["yarn_code", "batch", "balance_qty", "supplier_code"],
        "output_contract": ["material_or_quantity_risk", "affected_part_orders", "planner_confirmation_action"],
        "evidence_requirements": ["part-order row or material balance row", "field source", "data gap when true yarn demand is missing"],
        "read_only_boundary": READ_ONLY_BOUNDARY,
        "demo_status": "internal_demo_ready",
        "limitations": "True BOM demand and purchasing ETA are not fully connected.",
    },
    {
        "skill_id": "bottleneck_detection_skill",
        "name_zh": "瓶颈识别技能",
        "name_en": "Bottleneck Detection Skill",
        "purpose": "Find capacity concentration, plan/report gaps, high machine load, or output bottlenecks.",
        "input_objects": ["Planned_Task", "Manual_Machine_Production", "T_Machine_Info", "machine_status"],
        "required_fields": ["task_id", "machine_id", "planned_quantity", "produced_quantity"],
        "optional_fields": ["manual_report_quantity", "machine_code", "oee", "downtime_minutes"],
        "output_contract": ["bottleneck_candidate", "quantity_gap", "capacity_owner_confirmation"],
        "evidence_requirements": ["planned task row", "manual production row when reporting gap is claimed"],
        "read_only_boundary": READ_ONLY_BOUNDARY,
        "demo_status": "internal_demo_ready",
        "limitations": "Live IOT and maintenance closure history are not yet joined to the actual export path.",
    },
    {
        "skill_id": "quality_or_scrap_skill",
        "name_zh": "质量/废品分析技能",
        "name_en": "Quality or Scrap Skill",
        "purpose": "Prepare quality, scrap, yield, defect, and replenishment root-cause analysis when real quality data is available.",
        "input_objects": ["quality_inspection", "defect_reason", "garment_output", "iot_quality_signal"],
        "required_fields": ["order_id", "defect_reason", "scrap_quantity", "yield_rate"],
        "optional_fields": ["style_code", "machine_id", "process_stage", "replenishment_order"],
        "output_contract": ["quality_risk_card", "defect_concentration", "quality_owner_confirmation"],
        "evidence_requirements": ["inspection row or explicit mock/planned status"],
        "read_only_boundary": READ_ONLY_BOUNDARY,
        "demo_status": "contract_ready_needs_real_quality_data",
        "limitations": "Current Tianpai actual export does not contain enough quality inspection rows for production-grade root cause.",
    },
    {
        "skill_id": "service_escalation_skill",
        "name_zh": "服务升级技能",
        "name_en": "Service Escalation Skill",
        "purpose": "Turn production-impacting equipment alarms or stoppage into a service request candidate without dispatching.",
        "input_objects": ["machine_alarm", "service_escalations", "production_priority"],
        "required_fields": ["machine_id", "alarm", "downtime_minutes", "order_id"],
        "optional_fields": ["program_evidence", "operator_note", "service_case_match"],
        "output_contract": ["service_request_candidate", "blocked_dispatch_actions", "service_owner_confirmation"],
        "evidence_requirements": ["machine alarm or stopped-machine evidence", "production impact link"],
        "read_only_boundary": READ_ONLY_BOUNDARY,
        "demo_status": "internal_demo_ready",
        "limitations": "No real service ticket is created in the demo.",
    },
    {
        "skill_id": "follow_up_action_skill",
        "name_zh": "本地跟进行动技能",
        "name_en": "Follow-up Action Skill",
        "purpose": "Convert a risk card into a local metadata-only follow-up item linked to evidence.",
        "input_objects": ["risk_card", "action_candidate", "decision_loop", "production_follow_up_reviews"],
        "required_fields": ["action_id", "owner_role", "linked_risk_card_id", "evidence_refs"],
        "optional_fields": ["review_status", "evidence_note", "reviewed_at"],
        "output_contract": ["local_follow_up_candidate", "human_confirmation_gate", "blocked_real_system_writes"],
        "evidence_requirements": ["linked risk card", "linked evidence refs", "write_scope local_metadata_only"],
        "read_only_boundary": READ_ONLY_BOUNDARY,
        "demo_status": "internal_demo_ready",
        "limitations": "Follow-up status is local demo metadata and is not a real workflow-system task.",
    },
]


_THEME_SKILLS = {
    "delivery": ["gm_daily_brief_skill", "delivery_risk_skill", "follow_up_action_skill"],
    "equipment": ["gm_daily_brief_skill", "machine_fit_skill", "bottleneck_detection_skill", "service_escalation_skill", "follow_up_action_skill"],
    "machine": ["gm_daily_brief_skill", "machine_fit_skill", "bottleneck_detection_skill", "service_escalation_skill", "follow_up_action_skill"],
    "material": ["gm_daily_brief_skill", "material_constraint_skill", "follow_up_action_skill"],
    "cost": ["gm_daily_brief_skill", "bottleneck_detection_skill", "follow_up_action_skill"],
    "quality": ["gm_daily_brief_skill", "quality_or_scrap_skill", "follow_up_action_skill"],
    "labor": ["gm_daily_brief_skill", "bottleneck_detection_skill", "follow_up_action_skill"],
}


def production_skill_registry() -> dict:
    """Return the read-only skill registry used by the Production workflow."""

    return {
        "schema_id": "athena.production_skill_registry.v1",
        "version": PRODUCTION_SKILL_VERSION,
        "positioning": "Athena uses production-management skills to inspect evidence, not free-form chatbot guesses.",
        "read_only": True,
        "skill_count": len(_SKILLS),
        "skills": deepcopy(_SKILLS),
        "theme_skill_map": deepcopy(_THEME_SKILLS),
        "blocked_actions": READ_ONLY_BOUNDARY,
    }


def production_skills_for_theme(theme: str) -> list[dict]:
    registry = production_skill_registry()
    by_id = {item["skill_id"]: item for item in registry["skills"]}
    skill_ids = _THEME_SKILLS.get(theme, ["gm_daily_brief_skill", "follow_up_action_skill"])
    return [deepcopy(by_id[skill_id]) for skill_id in skill_ids if skill_id in by_id]


def production_skill_trace_for_priority(priority: dict) -> list[dict]:
    """Build a human-readable skill execution trace for a risk card."""

    theme = priority.get("risk_theme") or priority.get("management_theme") or "delivery"
    skills = production_skills_for_theme(theme)
    evidence_refs = list(priority.get("evidence_refs", []))
    data_objects = list(priority.get("source_objects", [])) or ["management_priority_brief", "evidence_log"]
    field_sources = list(priority.get("field_sources", []))
    chains = list(priority.get("actual_evidence_chains", []))
    trace: list[dict] = []

    for index, skill in enumerate(skills, start=1):
        if skill["skill_id"] == "gm_daily_brief_skill":
            checked = "Ranked this item against today's delivery, quality, cost, equipment, labor, and material risks."
            checked_zh = "把该事项放入今天交付、质量、成本、设备、人工、物料风险中排序。"
            result = f"Selected as priority #{priority.get('rank', index)} with risk level {priority.get('risk_level_label', priority.get('priority', 'P1'))}."
            result_zh = f"该事项被选为第 {priority.get('rank', index)} 优先级，风险等级为 {priority.get('risk_level_label', priority.get('priority', 'P1'))}。"
        elif skill["skill_id"] == "follow_up_action_skill":
            checked = "Converted the risk card into a local follow-up candidate and blocked real-system writes."
            checked_zh = "把风险卡片转成本地跟进候选，并阻止真实系统写入。"
            action = priority.get("action_candidate", {})
            result = f"Follow-up owner: {action.get('owner_role') or priority.get('owner_role', 'Production Owner')}."
            result_zh = f"建议跟进负责人：{action.get('owner_role') or priority.get('owner_role', 'Production Owner')}。"
        else:
            checked = f"Checked {', '.join(skill.get('input_objects', [])[:4])} for this {theme} risk."
            checked_zh = f"围绕 {priority.get('risk_theme_label') or theme} 风险检查 {', '.join(skill.get('input_objects', [])[:4])}。"
            result = priority.get("reason") or priority.get("conclusion") or "Evidence supports visibility, but owner confirmation is still required."
            result_zh = priority.get("reason_zh") or priority.get("conclusion_zh") or "证据支持进入可视范围，但仍需要负责人确认。"

        trace.append(
            {
                "step_id": f"TRACE-{priority.get('priority_id', 'PRIORITY')}-{index:02d}",
                "skill_id": skill["skill_id"],
                "skill_name_zh": skill["name_zh"],
                "skill_name_en": skill["name_en"],
                "step_name_zh": f"步骤 {index}: {skill['name_zh']}",
                "step_name_en": f"Step {index}: {skill['name_en']}",
                "what_athena_checked": checked,
                "what_athena_checked_zh": checked_zh,
                "data_objects_checked": data_objects or skill.get("input_objects", []),
                "field_sources": field_sources,
                "evidence_refs": evidence_refs,
                "actual_evidence_chain_count": len(chains),
                "evidence_level": priority.get("evidence_level", "Level 1: mock / demo evidence"),
                "confidence": priority.get("confidence", "medium"),
                "result_summary": result,
                "result_summary_zh": result_zh,
                "limitation_or_data_gap": "; ".join(priority.get("data_gaps", [])[:2])
                or skill.get("limitations", ""),
                "read_only": True,
            }
        )
    return trace


