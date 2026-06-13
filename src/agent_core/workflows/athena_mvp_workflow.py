"""Design intake structuring workflow for design-to-production readiness.

This workflow is intentionally deterministic for the local demo. It models a
Design Agent data-structuring layer: design inputs become auditable data
objects, tool-interface contracts, evidence logs, review gates, and KPIs.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date


WORKFLOW_TEMPLATE_ID = "athena.design_to_production_readiness.v1"


@dataclass(frozen=True)
class WorkflowStage:
    id: str
    name: str
    owner_role: str
    status: str
    output_object: str
    evidence_required: list[str]
    kpi: str


@dataclass(frozen=True)
class WorkflowTemplate:
    template_id: str
    version: str
    name: str
    positioning: str
    trigger: str
    permissions: list[str]
    escalation_path: list[str]
    input_objects: list[str]
    output_objects: list[str]
    stages: list[WorkflowStage]
    kpis: list[str]


def athena_mvp_template() -> dict:
    """Return the governed workflow template exposed by the demo API."""

    template = WorkflowTemplate(
        template_id=WORKFLOW_TEMPLATE_ID,
        version="v0.113.3",
        name="Design intake structuring to engineering handoff",
        positioning=(
            "This template is a Design Agent data-structuring middleware layer. It normalizes "
            "Style3D/CLO/AI/image/TP/design-request inputs into engineering, sampling, evidence, "
            "and future tool-handoff objects."
        ),
        trigger="New design or sample revision request with enough product/use-case context.",
        permissions=[
            "Read design-request inputs and attached asset metadata.",
            "Generate mock SWS/Arachne engineering brief candidates for demo review.",
            "Create evidence and KPI logs.",
            "No direct production-file write, machine control, ERP, APS, CRM, or CPQ write-back.",
        ],
        escalation_path=[
            "Pattern Engineering Assistant for SWS/Arachne parameter review.",
            "Application Engineer Assistant for manufacturability or sampling risk.",
            "Production Manager for production readiness gate approval.",
        ],
        input_objects=[
            "design_request",
            "source_asset",
            "technical_package",
            "sampling_feedback",
        ],
        output_objects=[
            "engineering_brief",
            "manufacturability_check",
            "revision_suggestion",
            "production_readiness_gate",
            "evidence_log",
            "kpi_log",
        ],
        stages=[
            WorkflowStage(
                id="design_intake",
                name="Design Request / Style3D-CLO-AI-Image-TP Intake",
                owner_role="Sampling Assistant",
                status="implemented_mock",
                output_object="design_request",
                evidence_required=["source type", "asset metadata", "functional requirements"],
                kpi="intake completeness",
            ),
            WorkflowStage(
                id="engineering_brief",
                name="SWS/Arachne Engineering Brief",
                owner_role="Pattern Engineering Assistant",
                status="implemented_mock",
                output_object="engineering_brief",
                evidence_required=["machine family", "zone structure map", "parameter assumptions"],
                kpi="time to first SWS/Arachne brief",
            ),
            WorkflowStage(
                id="manufacturability_check",
                name="Manufacturability Check",
                owner_role="Application Engineer Assistant",
                status="implemented_mock",
                output_object="manufacturability_check",
                evidence_required=["risk rules", "parameter range", "engineer review gate"],
                kpi="risk detected before first sample",
            ),
            WorkflowStage(
                id="sampling_feedback",
                name="Sampling Feedback Capture",
                owner_role="Sampling Engineer",
                status="implemented_mock",
                output_object="sampling_feedback",
                evidence_required=["round number", "defect signal", "measurement or photo note"],
                kpi="sample-round learning captured",
            ),
            WorkflowStage(
                id="revision_suggestion",
                name="Revision Suggestion",
                owner_role="Pattern Engineering Assistant",
                status="implemented_mock",
                output_object="revision_suggestion",
                evidence_required=["change reason", "parameter delta", "customer-facing tradeoff"],
                kpi="revision turnaround time",
            ),
            WorkflowStage(
                id="production_readiness",
                name="Production Readiness Gate",
                owner_role="Production Manager",
                status="implemented_mock",
                output_object="production_readiness_gate",
                evidence_required=["checklist", "open risks", "approval state"],
                kpi="production readiness cycle time",
            ),
        ],
        kpis=[
            "time_from_input_to_engineering_brief",
            "sample_rounds_reduced",
            "rework_risk_detected_before_sampling",
            "production_readiness_score",
            "expert_review_minutes_saved",
        ],
    )
    return asdict(template)


class AthenaMvpWorkflow:
    """Deterministic Design Intake Structuring workflow implementation."""

    def template(self) -> dict:
        return athena_mvp_template()

    def run(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        design_request = self._build_design_request(payload)
        engineering_brief = self._build_engineering_brief(design_request)
        manufacturability = self._build_manufacturability_check(design_request, engineering_brief)
        sampling_feedback = self._build_sampling_feedback(payload, manufacturability)
        revision = self._build_revision_suggestion(engineering_brief, manufacturability, sampling_feedback)
        production_readiness = self._build_production_readiness(manufacturability, sampling_feedback, revision)
        evidence_log = self._build_evidence_log(
            design_request,
            engineering_brief,
            manufacturability,
            sampling_feedback,
            revision,
            production_readiness,
        )
        kpi_log = self._build_kpis(manufacturability, sampling_feedback, production_readiness)
        stages = self._stage_states(production_readiness)

        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": WORKFLOW_TEMPLATE_ID,
                "status": production_readiness["gate"],
                "business_positioning": "design_intake_structuring_middleware",
                "not_a_chatbot": True,
                "not_a_generic_design_agent": True,
                "generated_on": date.today().isoformat(),
            },
            "stages": stages,
            "data_objects": {
                "design_request": design_request,
                "engineering_brief": engineering_brief,
                "manufacturability_check": manufacturability,
                "sampling_feedback": sampling_feedback,
                "revision_suggestion": revision,
                "production_readiness": production_readiness,
            },
            "tool_interfaces": self._tool_interfaces(),
            "evidence_log": evidence_log,
            "kpi_log": kpi_log,
        }

    def _build_design_request(self, payload: dict) -> dict:
        source_type = payload.get("source_type") or "design_request"
        functional_requirements = self._split_list(
            payload.get("functional_requirements"),
            ["breathability", "quick dry", "light compression"],
        )
        constraints = self._split_list(
            payload.get("constraints"),
            ["use approved seamless template", "avoid unvalidated production-file changes"],
        )
        assets = self._split_list(payload.get("source_assets"), ["reference image", "technical-package note"])

        return {
            "object_type": "design_request",
            "source_type": source_type,
            "customer_or_project": payload.get("customer_or_project") or "Demo OEM sampling project",
            "product_category": payload.get("product_category") or "seamless running top",
            "target_user": payload.get("target_user") or "performance running consumer",
            "use_case": payload.get("use_case") or "summer running and high-sweat training",
            "functional_requirements": functional_requirements,
            "material_preferences": self._split_list(payload.get("material_preferences"), ["polyamide/elastane quick-dry blend"]),
            "constraints": constraints,
            "source_assets": [{"asset_type": asset, "status": "metadata_only_demo"} for asset in assets],
            "acceptance_target": payload.get("acceptance_target") or "engineering brief ready for SWS/Arachne review",
            "missing_info": self._missing_design_info(payload),
        }

    def _build_engineering_brief(self, design_request: dict) -> dict:
        functions = " ".join(design_request["functional_requirements"]).lower()
        product = design_request["product_category"].lower()

        if "sock" in product:
            machine_model = "Santoni hosiery machine mock family"
            gauge = "14-18 gauge assumption"
        elif "top" in product or "shirt" in product:
            machine_model = "SM8-TOP2V / seamlesswear mock family"
            gauge = "15 gauge assumption"
        else:
            machine_model = "Santoni seamless/circular mock family"
            gauge = "application-engineer review required"

        zone_structure_map = [
            {
                "zone": "body base",
                "structure": "balanced jersey with stable recovery",
                "reason": "baseline comfort and dimensional control",
            },
            {
                "zone": "underarm / heat zones",
                "structure": "engineered mesh",
                "reason": "breathability and fast moisture release",
            },
        ]
        if "compression" in functions or "support" in functions:
            zone_structure_map.append(
                {
                    "zone": "support zones",
                    "structure": "graduated elastic structure",
                    "reason": "controlled support without full-garment stiffness",
                }
            )
        if "logo" in functions or "jacquard" in functions or "pattern" in functions:
            zone_structure_map.append(
                {
                    "zone": "visual area",
                    "structure": "low-risk jacquard or plated color zone",
                    "reason": "visual expression with engineer review before sampling",
                }
            )

        return {
            "object_type": "engineering_brief",
            "target_system": "SWS/Arachne",
            "machine_model": machine_model,
            "gauge": gauge,
            "recommended_yarn_package": [
                "quick-dry PA base yarn",
                "covered elastane for recovery",
                "optional recycled polyester if brand constraint requires it",
            ],
            "zone_structure_map": zone_structure_map,
            "parameter_hints": {
                "density_range": "medium-open in ventilation zones, stable base density elsewhere",
                "tension_range": "standard tension first, reduce only after first sample feedback",
                "speed_range": "demo assumes conservative sampling speed",
                "production_file_ref": "mock:SWS_ARACHNE_BRIEF_001",
            },
            "engineer_review_required": True,
            "open_questions": design_request["missing_info"],
        }

    def _build_manufacturability_check(self, design_request: dict, engineering_brief: dict) -> dict:
        risks = []
        score = 84
        functions = " ".join(design_request["functional_requirements"]).lower()
        constraints = " ".join(design_request["constraints"]).lower()

        if "compression" in functions and "mesh" in str(engineering_brief["zone_structure_map"]).lower():
            score -= 6
            risks.append(
                {
                    "risk": "compression and open mesh may conflict in the same zone",
                    "severity": "medium",
                    "mitigation": "separate support and ventilation zones before sample round 1",
                }
            )
        if "jacquard" in functions or "logo" in functions or "pattern" in functions:
            score -= 5
            risks.append(
                {
                    "risk": "visual pattern may create float or elasticity variation",
                    "severity": "medium",
                    "mitigation": "limit long floats and review color-zone transition before SWS/Arachne output",
                }
            )
        if "cost" in constraints:
            score -= 4
            risks.append(
                {
                    "risk": "cost target may limit yarn and structure options",
                    "severity": "low",
                    "mitigation": "keep first sample to one approved yarn package",
                }
            )
        if not risks:
            risks.append(
                {
                    "risk": "no high-risk blocker detected in mock rules",
                    "severity": "low",
                    "mitigation": "continue with engineer review before physical sampling",
                }
            )

        gate = "conditional_pass" if score >= 78 else "engineering_review_required"
        return {
            "object_type": "manufacturability_check",
            "score": score,
            "gate": gate,
            "risk_checks": risks,
            "blocked_actions": [
                "No direct production-file generation in MVP.",
                "No machine-control or order-system write-back.",
            ],
            "required_human_review": [
                "SWS/Arachne engineer validates zone structure map.",
                "Application engineer confirms yarn and tension assumptions.",
            ],
        }

    def _build_sampling_feedback(self, payload: dict, manufacturability: dict) -> dict:
        feedback = payload.get("sampling_feedback") or "first sample not yet produced; use mock expected feedback"
        defect_signals = self._split_list(payload.get("defect_signals"), [])
        if not defect_signals:
            if manufacturability["score"] < 80:
                defect_signals = ["ventilation/support tradeoff requires sample validation"]
            else:
                defect_signals = ["no physical-sample issue recorded yet"]

        return {
            "object_type": "sampling_feedback",
            "round": payload.get("sample_round") or "mock_round_0",
            "status": "captured_mock",
            "feedback_summary": feedback,
            "defect_signals": defect_signals,
            "evidence_refs": ["EV-004"],
            "missing_info": [
                "physical sample photos",
                "measurement table",
                "wear-test comments",
            ]
            if "not yet" in feedback
            else [],
        }

    def _build_revision_suggestion(self, engineering_brief: dict, manufacturability: dict, sampling_feedback: dict) -> dict:
        changes = [
            {
                "target": "ventilation zone",
                "change": "keep engineered mesh but separate it from support zones",
                "reason": "reduce conflict between breathability and elasticity recovery",
            },
            {
                "target": "sampling speed",
                "change": "start conservative and increase only after stable sample review",
                "reason": "protect first-sample stability before optimizing output",
            },
        ]
        if manufacturability["score"] >= 82:
            changes.append(
                {
                    "target": "SWS/Arachne brief",
                    "change": "move to engineer review with current zone map",
                    "reason": "mock manufacturability score supports conditional pass",
                }
            )
        else:
            changes.append(
                {
                    "target": "structure map",
                    "change": "simplify high-risk visual or compression zones before first sample",
                    "reason": "reduce sample rework risk",
                }
            )

        return {
            "object_type": "revision_suggestion",
            "status": "ready_for_engineer_review",
            "parameter_deltas": changes,
            "customer_facing_tradeoff": (
                "Athena keeps the design intent but separates performance zones so the sample has a higher chance "
                "of matching comfort, elasticity, and production stability targets."
            ),
            "next_owner": "Pattern Engineering Assistant",
            "related_brief_ref": engineering_brief["parameter_hints"]["production_file_ref"],
        }

    def _build_production_readiness(self, manufacturability: dict, sampling_feedback: dict, revision: dict) -> dict:
        readiness_score = manufacturability["score"] - (8 if sampling_feedback["missing_info"] else 0)
        if readiness_score >= 82 and not sampling_feedback["missing_info"]:
            gate = "ready_for_pilot_production"
        elif readiness_score >= 74:
            gate = "sample_round_required"
        else:
            gate = "engineering_revision_required"

        checklist = [
            {
                "item": "Design request mapped to structured engineering brief",
                "status": "done",
            },
            {
                "item": "Manufacturability risks scored before sample",
                "status": "done",
            },
            {
                "item": "Sampling evidence attached",
                "status": "pending" if sampling_feedback["missing_info"] else "done",
            },
            {
                "item": "Revision suggestion reviewed by engineer",
                "status": "pending",
            },
            {
                "item": "Production manager gate approval",
                "status": "pending",
            },
        ]

        return {
            "object_type": "production_readiness_gate",
            "readiness_score": readiness_score,
            "gate": gate,
            "checklist": checklist,
            "blocked_by": sampling_feedback["missing_info"] + ["human engineer approval"],
            "next_decision": revision["next_owner"],
        }

    def _build_evidence_log(self, *objects: dict) -> list[dict]:
        labels = [
            ("EV-001", "design_intake", "Design input was converted into a structured design_request object."),
            ("EV-002", "engineering_brief", "SWS/Arachne engineering brief generated from Santoni mock rules."),
            ("EV-003", "manufacturability_check", "Manufacturability gate calculated from explicit risk rules."),
            ("EV-004", "sampling_feedback", "Sampling feedback captured as a workflow object, not free text."),
            ("EV-005", "revision_suggestion", "Revision suggestion includes parameter target, reason, and tradeoff."),
            ("EV-006", "production_readiness", "Production readiness gate keeps approval separate from generation."),
        ]
        evidence = []
        for (evidence_id, source, claim), obj in zip(labels, objects, strict=True):
            evidence.append(
                {
                    "evidence_id": evidence_id,
                    "source": source,
                    "object_type": obj["object_type"],
                    "claim": claim,
                    "status": "mock_evidence",
                }
            )
        return evidence

    def _build_kpis(self, manufacturability: dict, sampling_feedback: dict, production_readiness: dict) -> list[dict]:
        sample_round_target = "1-2 rounds" if production_readiness["readiness_score"] >= 78 else "2-3 rounds"
        return [
            {
                "kpi": "time_from_input_to_engineering_brief",
                "baseline": "manual handoff: 1-3 days",
                "demo_target": "structured brief in minutes",
                "evidence_ref": "EV-002",
            },
            {
                "kpi": "sample_rounds_reduced",
                "baseline": "2-4 rounds",
                "demo_target": sample_round_target,
                "evidence_ref": "EV-005",
            },
            {
                "kpi": "rework_risk_detected_before_sampling",
                "baseline": "risk found after physical sample",
                "demo_target": f"{len(manufacturability['risk_checks'])} risk checks logged before sampling",
                "evidence_ref": "EV-003",
            },
            {
                "kpi": "production_readiness_score",
                "baseline": "subjective readiness",
                "demo_target": str(production_readiness["readiness_score"]),
                "evidence_ref": "EV-006",
            },
            {
                "kpi": "sample_feedback_capture",
                "baseline": "feedback stored in chat or email",
                "demo_target": "captured" if not sampling_feedback["missing_info"] else "pending physical evidence",
                "evidence_ref": "EV-004",
            },
        ]

    def _stage_states(self, production_readiness: dict) -> list[dict]:
        output = []
        for stage in self.template()["stages"]:
            status = "done"
            if stage["id"] in {"sampling_feedback", "revision_suggestion", "production_readiness"}:
                status = "pending_review"
            output.append(
                {
                    "id": stage["id"],
                    "name": stage["name"],
                    "owner_role": stage["owner_role"],
                    "status": status,
                    "output_object": stage["output_object"],
                    "gate": production_readiness["gate"] if stage["id"] == "production_readiness" else "",
                    "evidence_required": stage["evidence_required"],
                    "kpi": stage["kpi"],
                }
            )
        return output

    def _tool_interfaces(self) -> list[dict]:
        return [
            {
                "tool": "Style3D/CLO/AI/Image/TP Intake Adapter",
                "status": "mock_contract",
                "input": "source_asset metadata and design_request fields",
                "output": "normalized design_request",
                "write_permission": "none",
            },
            {
                "tool": "SWS/Arachne Engineering Brief Adapter",
                "status": "mock_contract",
                "input": "design_request and zone_structure_map",
                "output": "engineering_brief",
                "write_permission": "no production file write in MVP",
            },
            {
                "tool": "Manufacturability Rule Check",
                "status": "implemented_mock",
                "input": "engineering_brief",
                "output": "risk_checks and gate",
                "write_permission": "none",
            },
            {
                "tool": "Sampling Feedback Capture",
                "status": "implemented_mock",
                "input": "sample round, defect signal, photo/measurement note",
                "output": "sampling_feedback and evidence_ref",
                "write_permission": "local demo object only",
            },
            {
                "tool": "Production Readiness Gate",
                "status": "implemented_mock",
                "input": "risk, revision, sampling evidence, checklist",
                "output": "readiness score and next decision",
                "write_permission": "human approval required",
            },
        ]

    def _missing_design_info(self, payload: dict) -> list[str]:
        required = [
            "product_category",
            "target_user",
            "use_case",
            "functional_requirements",
            "source_type",
        ]
        return [field for field in required if not payload.get(field)]

    def _split_list(self, value, fallback: list[str]) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            normalized = value.replace("\n", ",").replace(";", ",")
            items = [item.strip() for item in normalized.split(",") if item.strip()]
            return items or fallback
        return fallback





