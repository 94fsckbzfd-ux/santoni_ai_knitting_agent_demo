"""Hermes integration workflow for Athena local demo.

This first Hermes layer is a contract, not a live connector. It models Hermes
as Athena's optional runtime, memory, tool orchestration, and evolution loop
while keeping Santoni Agent Core responsible for domain workflow logic.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from agent_core.workflows.production_operations_workflow import ProductionOperationsWorkflow


HERMES_VERSION = "v0.113.1"
HERMES_TEMPLATE_ID = "athena.hermes_integration.v1"
HERMES_CONTRACT_ID = "athena.hermes_agent_core_contract.v1"
PROJECT_DATA_PATH = Path(__file__).resolve().parents[3] / "docs" / "data" / "athena_project_data.json"
PLAYBOOK_REVIEW_PATH = Path(__file__).resolve().parents[2] / "mock_data" / "hermes_playbook_reviews.json"


@dataclass(frozen=True)
class HermesInterface:
    name: str
    status: str
    direction: str
    source_object: str
    target_object: str
    write_policy: str
    evidence_ref: str


def hermes_template() -> dict:
    interfaces = [
        HermesInterface(
            "Hermes Runtime Adapter",
            "mock_contract",
            "Hermes -> Santoni Agent Core",
            "tool_call_request",
            "agent_core_http_or_mcp_call",
            "call_only_after_human_enabled_endpoint",
            "EV-HERMES-001",
        ),
        HermesInterface(
            "Athena Memory Adapter",
            "mock_contract",
            "Santoni Agent Core -> Hermes",
            "athena_memory_event",
            "hermes_project_memory",
            "candidate_only_until_schema_confirmed",
            "EV-HERMES-002",
        ),
        HermesInterface(
            "Development Suggestion Adapter",
            "mock_contract",
            "Hermes -> Codex / Athena PMO",
            "evolution_candidate",
            "development_suggestion",
            "proposal_only_no_auto_code_change",
            "EV-HERMES-004",
        ),
        HermesInterface(
            "Production Data Evidence Adapter",
            "read_only_planned",
            "APS/IOT exports -> Hermes -> Athena",
            "production_evidence_snapshot",
            "root_cause_and_kpi_memory",
            "read_only_no_aps_iot_write",
            "EV-HERMES-003",
        ),
    ]

    return {
        "template_id": HERMES_TEMPLATE_ID,
        "version": HERMES_VERSION,
        "name": "Hermes integration contract for Santoni Athena",
        "positioning": (
            "Hermes is an optional runtime, memory, tool orchestration, and self-evolution layer for Athena. "
            "It does not replace Santoni Agent Core, Production Operations, Service workflows, workflow templates, "
            "guardrails, evidence rules, or domain-specific adapters."
        ),
        "adapter_status": "mock_contract",
        "connection_state": {
            "real_hermes_endpoint_connected": False,
            "real_hermes_auth_configured": False,
            "writeback_enabled": False,
            "local_contract_available": True,
        },
        "primary_loop": [
            "capture_memory_event",
            "normalize_evidence",
            "score_gap_or_opportunity",
            "propose_development_suggestion",
            "human_review",
            "planned_adapter_or_workflow_update",
            "regression_test",
        ],
        "data_objects": [
            "athena_memory_event",
            "tool_call_contract",
            "evolution_candidate",
            "development_suggestion",
            "evaluation_trace",
            "evidence_log",
            "kpi_log",
            "organization_playbook_candidate",
            "playbook_review_record",
            "regression_case_candidate",
        ],
        "memory_event_schema": {
            "required_fields": [
                "event_id",
                "type",
                "summary",
                "scope",
                "tenant_id",
                "factory_id",
                "source",
                "retention_policy",
                "sensitivity_level",
                "promotion_status",
                "object_scope",
                "write_policy",
                "evidence_ref",
            ],
            "scope_values": ["product", "domain", "tenant", "session"],
            "source_values": ["demo", "APS export", "IOT export", "meeting", "user feedback"],
            "promotion_status_values": ["candidate", "reviewed", "approved"],
            "tenant_memory_rule": "Tenant memory must not be promoted to Santoni domain memory without review, anonymization when needed, and approved promotion_status.",
        },
        "interfaces": [asdict(item) for item in interfaces],
        "blocked_actions": [
            "store_hermes_token_in_repo",
            "store_platform_credentials",
            "write_to_aps_or_iot",
            "change_production_schedule",
            "upload_co_or_cx_file",
            "auto_dispatch_service_ticket",
            "auto_modify_code_without_human_review",
        ],
        "next_required_inputs": [
            "Hermes endpoint and authentication mode.",
            "Hermes memory event schema and retention policy.",
            "Decision on HTTP API versus MCP tool-call integration.",
            "APS exported table samples for recent orders.",
            "IOT exported table samples for the same order_id set.",
        ],
        "kpis": [
            "memory_event_count",
            "evidence_coverage",
            "development_suggestion_count",
            "open_decision_count",
            "adapter_contract_coverage",
            "human_review_required_count",
        ],
    }


class HermesIntegrationWorkflow:
    """Local Hermes contract and Athena self-evolution suggestion workflow."""

    def __init__(
        self,
        project_data_path: Path | None = None,
        playbook_review_path: Path | None = None,
        production_workflow: ProductionOperationsWorkflow | None = None,
    ) -> None:
        self.project_data_path = project_data_path or PROJECT_DATA_PATH
        self.playbook_review_path = playbook_review_path or PLAYBOOK_REVIEW_PATH
        self.production_workflow = production_workflow or ProductionOperationsWorkflow()

    def template(self) -> dict:
        return hermes_template()

    def overview(self) -> dict:
        project_data = self._load_project_data()
        memory_events = self._memory_events(project_data)
        evolution_candidates = self._evolution_candidates()
        development_suggestions = self._development_suggestions(evolution_candidates)
        evidence_log = self._evidence_log()
        organization_memory_playbook = self._organization_memory_playbook(self.production_workflow.follow_up_loop()["decision_loop"])
        kpi_log = self._kpi_log(memory_events, development_suggestions, evidence_log, organization_memory_playbook)

        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": HERMES_TEMPLATE_ID,
                "version": HERMES_VERSION,
                "status": "mock_contract",
                "read_only": True,
                "real_hermes_connected": False,
                "write_actions_blocked": True,
                "blocked_actions": self.template()["blocked_actions"],
            },
            "hermes_overview": {
                "runtime_position": "optional_runtime_memory_orchestration_layer",
                "agent_core_role": "domain_workflow_system_of_record",
                "self_evolution_scope": "proposal_and_evidence_loop_only",
                "project_modules_seen": len(project_data.get("modules", [])),
                "open_decision_count": self._open_decision_count(project_data),
                "adapter_status": "mock_contract",
            },
            "adapter_contract": self.adapter_contract(),
            "memory_events": memory_events,
            "organization_memory_playbook": organization_memory_playbook,
            "evolution_candidates": evolution_candidates,
            "development_suggestions": development_suggestions,
            "tool_registry_candidates": self._tool_registry_candidates(),
            "evidence_log": evidence_log,
            "kpi_log": kpi_log,
        }

    def adapter_contract(self) -> dict:
        template = self.template()
        return {
            "contract_id": HERMES_CONTRACT_ID,
            "version": HERMES_VERSION,
            "status": "mock_contract",
            "adapter_status": "mock_contract",
            "scope": "Local contract for connecting Hermes to Athena runtime, memory, tools, and development-suggestion loops.",
            "credential_policy": (
                "No Hermes token, APS/IOT credential, platform password, API key, customer-sensitive data, "
                "or exported test account is stored in code, .env, mock data, docs, logs, exported files, or API responses."
            ),
            "runtime_boundary": {
                "hermes_can": [
                    "call approved Agent Core APIs or MCP tools",
                    "store reviewed Athena memory events",
                    "rank development suggestions from evidence",
                    "prepare evaluation traces for regression tests",
                ],
                "hermes_cannot": template["blocked_actions"],
            },
            "candidate_endpoints": [
                {"method": "GET", "path": "/api/hermes/template", "purpose": "Return Hermes adapter contract template."},
                {"method": "GET", "path": "/api/hermes/overview", "purpose": "Return current local Hermes integration snapshot."},
                {"method": "GET", "path": "/api/hermes/playbook", "purpose": "Return local organization-memory playbook candidates."},
                {"method": "POST", "path": "/api/hermes/suggest", "purpose": "Return evidence-based development suggestions for a selected focus."},
                {"method": "POST", "path": "/api/hermes/playbook/review", "purpose": "Save metadata-only playbook review state without writing live Hermes memory."},
            ],
            "future_call_shape": {
                "request": ["caller", "focus", "source_object", "evidence_refs", "requested_action"],
                "response": ["status", "allowed", "result_object", "evidence_refs", "blocked_actions", "human_review_required"],
            },
            "interfaces": template["interfaces"],
        }

    def suggest(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        focus = str(payload.get("focus") or "production").strip().lower()
        overview = self.overview()
        suggestions = overview["development_suggestions"]

        if focus not in {"", "all", "athena"}:
            focused = [
                item
                for item in suggestions
                if focus in item["scope"].lower() or focus in item["title"].lower() or focus in item["reason"].lower()
            ]
            if focused:
                suggestions = focused

        return {
            "agent": {
                "agent_id": "athena.hermes_development_suggestion_agent.v1",
                "version": HERMES_VERSION,
                "name": "Hermes Adapter for Santoni Athena",
                "positioning": "Evidence-based proposal loop for Athena self-evolution.",
            },
            "analysis_request": {
                "focus": focus or "all",
                "write_actions_blocked": True,
                "real_hermes_connected": False,
            },
            "suggestions": suggestions,
            "next_required_inputs": overview["workflow_template"]["next_required_inputs"],
            "evidence_log": overview["evidence_log"],
            "blocked_actions": overview["workflow_instance"]["blocked_actions"],
        }

    def playbook(self) -> dict:
        decision_loop = self.production_workflow.follow_up_loop()["decision_loop"]
        playbook = self._organization_memory_playbook(decision_loop)
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": HERMES_TEMPLATE_ID,
                "version": HERMES_VERSION,
                "scenario": "organization_memory_playbook",
                "status": "mock_contract",
                "read_only": True,
                "real_hermes_connected": False,
                "write_actions_blocked": True,
                "blocked_actions": self.template()["blocked_actions"],
            },
            "source_decision_loop": {
                "loop_id": decision_loop.get("loop_id"),
                "status": decision_loop.get("status"),
                "follow_up_count": decision_loop.get("loop_kpis", {}).get("follow_up_count", 0),
                "closed_follow_up_count": decision_loop.get("loop_kpis", {}).get("closed_follow_up_count", 0),
            },
            "organization_memory_playbook": playbook,
            "evidence_log": self._evidence_log(),
            "blocked_actions": playbook["blocked_actions"],
        }

    def apply_playbook_review(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        candidate_id = str(payload.get("candidate_id") or "").strip()
        review_status = str(payload.get("review_status") or "").strip()
        allowed_statuses = {"reviewed", "approved", "needs_changes", "rejected"}
        if not candidate_id:
            raise ValueError("candidate_id is required")
        if review_status not in allowed_statuses:
            raise ValueError(f"review_status must be one of {sorted(allowed_statuses)}")

        review_note = str(payload.get("review_note") or "").strip()
        self._reject_sensitive_review_text("review_note", review_note)

        current = self.playbook()
        candidates = {
            item["candidate_id"]: item
            for item in current["organization_memory_playbook"]["playbook_candidates"]
        }
        if candidate_id not in candidates:
            raise ValueError(f"Unknown candidate_id: {candidate_id}")
        candidate = candidates[candidate_id]
        if review_status == "approved" and not candidate["ready_for_playbook_review"]:
            raise ValueError("playbook candidate cannot be approved before follow-up closure and accepted evidence")

        store = self._load_playbook_review_store()
        promotion_status = {
            "reviewed": "reviewed",
            "approved": "approved",
            "needs_changes": "candidate",
            "rejected": "candidate",
        }[review_status]
        review = {
            "review_id": f"PBREV-{HERMES_VERSION}-{len(store.get('reviews', [])) + 1:03d}",
            "candidate_id": candidate_id,
            "review_status": review_status,
            "promotion_status": promotion_status,
            "review_note": review_note,
            "reviewed_by": str(payload.get("reviewed_by") or "hermes_console").strip(),
            "reviewed_at": datetime.now().isoformat(timespec="seconds"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }
        store.setdefault("reviews", []).append(review)
        store["version"] = HERMES_VERSION
        store["latest_reviewed_at"] = review["reviewed_at"]
        self._save_playbook_review_store(store)
        return self.playbook()

    def _organization_memory_playbook(self, decision_loop: dict) -> dict:
        store = self._load_playbook_review_store()
        latest_reviews = self._latest_playbook_reviews_by_candidate(store)
        decisions = {item["decision_id"]: item for item in decision_loop.get("decision_items", [])}
        actions = {item["action_id"]: item for item in decision_loop.get("action_items", [])}
        memory_events = {
            item.get("linked_follow_up_id"): item
            for item in decision_loop.get("memory_event_candidates", [])
        }
        candidates = []

        for follow_up in decision_loop.get("follow_up_items", []):
            action = actions.get(follow_up.get("action_id"), {})
            decision = decisions.get(follow_up.get("decision_id"), {})
            memory_event = memory_events.get(follow_up.get("follow_up_id"), {})
            candidate_id = f"PB-{follow_up.get('follow_up_id', 'UNKNOWN').removeprefix('FU-')}"
            review = latest_reviews.get(candidate_id, {})
            readiness = self._playbook_readiness(follow_up)
            promotion_status = review.get("promotion_status") or memory_event.get("promotion_status") or "candidate"
            ready_for_review = readiness == "ready_for_playbook_review"

            candidates.append(
                {
                    "candidate_id": candidate_id,
                    "schema_id": "athena.organization_playbook_candidate.v1",
                    "source_loop_id": decision_loop.get("loop_id"),
                    "source_decision_id": follow_up.get("decision_id"),
                    "source_action_id": follow_up.get("action_id"),
                    "source_follow_up_id": follow_up.get("follow_up_id"),
                    "management_theme": decision.get("management_theme"),
                    "trigger_signal": decision.get("conclusion") or decision.get("conclusion_zh"),
                    "problem_signature": {
                        "priority": decision.get("priority"),
                        "theme": decision.get("management_theme"),
                        "affected_kpis": follow_up.get("recurrence_watch", {}).get("watch_kpis", []),
                        "evidence_refs": follow_up.get("evidence_refs", []),
                    },
                    "recommended_action_pattern": action.get("recommended_action"),
                    "owner_role": follow_up.get("owner_role"),
                    "expected_evidence": follow_up.get("expected_evidence", []),
                    "current_follow_up_status": follow_up.get("status"),
                    "evidence_status": follow_up.get("evidence_status"),
                    "readiness": readiness,
                    "ready_for_playbook_review": ready_for_review,
                    "promotion_status": promotion_status,
                    "review_status": review.get("review_status", "not_reviewed"),
                    "review_note": review.get("review_note", ""),
                    "reviewed_at": review.get("reviewed_at", ""),
                    "memory_event_candidate": {
                        "event_id": memory_event.get("memory_event_id") or f"MEM-{candidate_id}",
                        "scope": memory_event.get("scope", "tenant"),
                        "tenant_id": memory_event.get("tenant_id", "tianpai"),
                        "factory_id": memory_event.get("factory_id"),
                        "source": memory_event.get("source", "demo"),
                        "retention_policy": memory_event.get("retention_policy", "review_before_promotion"),
                        "sensitivity_level": memory_event.get("sensitivity_level", "internal"),
                        "promotion_status": promotion_status,
                        "contains_raw_user_message": False,
                        "contains_credentials": False,
                    },
                    "playbook_template": {
                        "trigger": "same management_theme and affected KPI recur with matching evidence_refs",
                        "standard_response_shape": [
                            "management_summary",
                            "reason_and_evidence",
                            "recommended_action",
                            "owner",
                            "expected_evidence",
                            "follow_up_gate",
                        ],
                        "closure_gate": follow_up.get("closure_gate"),
                        "recurrence_watch": follow_up.get("recurrence_watch", {}),
                    },
                    "regression_case_candidate": {
                        "case_id": f"REG-{candidate_id}",
                        "prompt_family": decision.get("management_theme"),
                        "expected_fields": [
                            "executive_answer",
                            "evidence_refs",
                            "decision_loop",
                            "blocked_actions",
                            "data_gaps",
                        ],
                        "promotion_required": "approved_playbook_candidate",
                    },
                    "blocked_until": self._playbook_blocked_until(readiness, review),
                    "evidence_refs": follow_up.get("evidence_refs", []),
                }
            )

        status_counts = self._count_by([item["promotion_status"] for item in candidates])
        ready_count = len([item for item in candidates if item["ready_for_playbook_review"]])
        return {
            "schema_id": "athena.organization_memory_playbook.v1",
            "version": HERMES_VERSION,
            "engine_id": f"HERMES-PLAYBOOK-{HERMES_VERSION}",
            "adapter_status": "mock_contract",
            "real_hermes_connected": False,
            "write_actions_blocked": True,
            "source_decision_loop_id": decision_loop.get("loop_id"),
            "playbook_contract": [
                "trigger_signal",
                "decision_loop",
                "follow_up_evidence",
                "human_review",
                "playbook_candidate",
                "approved_memory",
                "regression_case",
            ],
            "scope_policy": {
                "product": "Santoni product-level lessons; no tenant data unless anonymized and approved.",
                "domain": "Reusable knitting-domain patterns after review.",
                "tenant": "Customer/factory-specific playbooks; default scope for Tianpai.",
                "session": "Short-lived conversation state; never promoted directly.",
            },
            "promotion_gate": [
                "follow_up_closed",
                "accepted_evidence_note",
                "human_playbook_review",
                "sensitivity_check",
                "regression_case_prepared",
            ],
            "playbook_candidates": candidates,
            "review_state": {
                "schema": store.get("schema", "athena.hermes_playbook_reviews.v1"),
                "version": store.get("version", HERMES_VERSION),
                "review_count": len(store.get("reviews", [])),
                "latest_reviewed_at": store.get("latest_reviewed_at", ""),
                "metadata_only": True,
                "raw_files_stored": False,
                "credentials_stored": False,
            },
            "playbook_kpis": {
                "candidate_count": len(candidates),
                "ready_for_review_count": ready_count,
                "reviewed_count": status_counts.get("reviewed", 0),
                "approved_count": status_counts.get("approved", 0),
                "regression_case_candidate_count": len([item for item in candidates if item.get("regression_case_candidate")]),
            },
            "blocked_actions": [
                "write_live_hermes_memory",
                "promote_tenant_memory_without_review",
                "store_raw_customer_data",
                "store_credentials_or_tokens",
                "auto_create_regression_without_approved_playbook",
                "modify_code_from_playbook_without_codex_review",
            ],
            "next_actions": self._playbook_next_actions(candidates),
        }

    def _load_playbook_review_store(self) -> dict:
        if not self.playbook_review_path.exists():
            return {
                "schema": "athena.hermes_playbook_reviews.v1",
                "version": HERMES_VERSION,
                "metadata_only": True,
                "reviews": [],
                "latest_reviewed_at": "",
            }
        try:
            return json.loads(self.playbook_review_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {
                "schema": "athena.hermes_playbook_reviews.v1",
                "version": HERMES_VERSION,
                "metadata_only": True,
                "reviews": [],
                "latest_reviewed_at": "",
            }

    def _save_playbook_review_store(self, store: dict) -> None:
        self.playbook_review_path.parent.mkdir(parents=True, exist_ok=True)
        self.playbook_review_path.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _latest_playbook_reviews_by_candidate(store: dict) -> dict:
        latest = {}
        for review in store.get("reviews", []):
            candidate_id = review.get("candidate_id")
            if candidate_id:
                latest[candidate_id] = review
        return latest

    @staticmethod
    def _reject_sensitive_review_text(field: str, value: str) -> None:
        lowered = value.lower()
        sensitive_markers = ["password", "api key", "apikey", "token", "secret", "1qaz"]
        if any(marker in lowered for marker in sensitive_markers):
            raise ValueError(f"{field} must not contain credentials, tokens, or passwords")

    @staticmethod
    def _playbook_readiness(follow_up: dict) -> str:
        status = follow_up.get("status")
        evidence_status = follow_up.get("evidence_status")
        if status == "closed" and evidence_status == "accepted":
            return "ready_for_playbook_review"
        if status == "closed":
            return "needs_accepted_evidence_note"
        if status in {"assigned", "waiting_evidence", "confirmed", "reopened"}:
            return "needs_follow_up_completion"
        return "needs_owner_assignment"

    @staticmethod
    def _playbook_blocked_until(readiness: str, review: dict) -> list[str]:
        blocked = []
        if readiness != "ready_for_playbook_review":
            blocked.append(readiness)
        if not review:
            blocked.append("human_playbook_review")
        if review.get("review_status") != "approved":
            blocked.append("approved_promotion_status")
        return blocked

    @staticmethod
    def _count_by(values: list[str]) -> dict:
        counts = {}
        for value in values:
            counts[value] = counts.get(value, 0) + 1
        return counts

    @staticmethod
    def _playbook_next_actions(candidates: list[dict]) -> list[str]:
        if not candidates:
            return ["Generate decision_loop follow-up candidates before playbook review."]
        if any(item["ready_for_playbook_review"] for item in candidates):
            return ["Review ready playbook candidates and approve only patterns with accepted evidence."]
        return ["Close follow-up items with accepted evidence before promoting organizational playbooks."]

    def _load_project_data(self) -> dict:
        if not self.project_data_path.exists():
            return {"modules": [], "milestones": []}
        try:
            return json.loads(self.project_data_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"modules": [], "milestones": []}

    def _memory_events(self, project_data: dict) -> list[dict]:
        module_count = len(project_data.get("modules", []))
        milestone_count = len(project_data.get("milestones", []))
        return [
            {
                "event_id": "MEM-HERMES-001",
                "type": "architecture_decision",
                "summary": "Hermes should be treated as Athena runtime, memory, tool orchestration, and automation layer, not as a replacement for Santoni Agent Core.",
                "scope": "product",
                "tenant_id": None,
                "factory_id": None,
                "source": "meeting",
                "retention_policy": "project_lifecycle",
                "sensitivity_level": "internal",
                "promotion_status": "approved",
                "object_scope": ["main_agent", "runtime", "tool_orchestration"],
                "write_policy": "candidate_only_until_hermes_schema_confirmed",
                "evidence_ref": "EV-HERMES-001",
            },
            {
                "event_id": "MEM-HERMES-002",
                "type": "project_memory_snapshot",
                "summary": f"Local Athena PMO data is available for Hermes memory seeding with {module_count} modules and {milestone_count} milestones.",
                "scope": "product",
                "tenant_id": None,
                "factory_id": None,
                "source": "demo",
                "retention_policy": "project_lifecycle",
                "sensitivity_level": "internal",
                "promotion_status": "reviewed",
                "object_scope": ["pmo", "project_intelligence", "roadmap"],
                "write_policy": "read_local_json_only",
                "evidence_ref": "EV-HERMES-002",
            },
            {
                "event_id": "MEM-HERMES-003",
                "type": "production_integration_boundary",
                "summary": "Current Production Console uses static mock JSON; future production integration should read APS/IOT database views or formal APIs by canonical order_id.",
                "scope": "domain",
                "tenant_id": None,
                "factory_id": None,
                "source": "demo",
                "retention_policy": "domain_lifecycle",
                "sensitivity_level": "internal",
                "promotion_status": "reviewed",
                "object_scope": ["production", "aps", "iot", "order_id"],
                "write_policy": "read_only_no_scraping_writeback",
                "evidence_ref": "EV-HERMES-003",
            },
            {
                "event_id": "MEM-HERMES-004",
                "type": "development_direction",
                "summary": "Next Athena production loop should support main production data monitoring, exception alarms, historical comparison, and root-cause drilldown from exported APS/IOT tables.",
                "scope": "product",
                "tenant_id": None,
                "factory_id": None,
                "source": "meeting",
                "retention_policy": "project_lifecycle",
                "sensitivity_level": "internal",
                "promotion_status": "reviewed",
                "object_scope": ["production", "root_cause", "history", "exceptions"],
                "write_policy": "proposal_only",
                "evidence_ref": "EV-HERMES-004",
            },
        ]

    def _evolution_candidates(self) -> list[dict]:
        return [
            {
                "candidate_id": "EVO-HERMES-001",
                "scope": "hermes",
                "title": "Confirm Hermes transport and memory schema",
                "reason": "The demo can expose a local contract, but live Hermes needs endpoint, auth mode, schema, retention policy, and HTTP-vs-MCP decision.",
                "impact": "Unlocks real Athena memory and repeatable development suggestion loops.",
                "evidence_refs": ["EV-HERMES-001", "EV-HERMES-005"],
                "human_review_required": True,
            },
            {
                "candidate_id": "EVO-HERMES-002",
                "scope": "production",
                "title": "Build APS/IOT exported-table simulation import",
                "reason": "APS and IOT test pages contain fake data; recent exported tables from platform owners are the next realistic evidence source.",
                "impact": "Lets Athena validate order_id flow, monitoring, alarms, and root-cause analysis before database integration.",
                "evidence_refs": ["EV-HERMES-003", "EV-HERMES-004"],
                "human_review_required": True,
            },
            {
                "candidate_id": "EVO-HERMES-003",
                "scope": "production",
                "title": "Add historical comparison objects",
                "reason": "Production managers need current-vs-history comparisons to distinguish normal variance from real waste, delay, or quality drift.",
                "impact": "Improves exception alarms, KPI thresholds, and management review quality.",
                "evidence_refs": ["EV-HERMES-004"],
                "human_review_required": True,
            },
            {
                "candidate_id": "EVO-HERMES-004",
                "scope": "evaluation",
                "title": "Create Athena regression and suggestion evaluation traces",
                "reason": "Hermes self-evolution should be evidence-scored and test-backed before any workflow or adapter change becomes implemented.",
                "impact": "Prevents unreviewed roadmap drift and keeps demo behavior auditable.",
                "evidence_refs": ["EV-HERMES-001", "EV-HERMES-005"],
                "human_review_required": True,
            },
        ]

    def _development_suggestions(self, candidates: list[dict]) -> list[dict]:
        priorities = {
            "EVO-HERMES-001": "P0",
            "EVO-HERMES-002": "P0",
            "EVO-HERMES-003": "P1",
            "EVO-HERMES-004": "P1",
        }
        next_actions = {
            "EVO-HERMES-001": [
                "Ask Hermes owner for endpoint/auth/schema sample.",
                "Decide HTTP API or MCP tool-call bridge.",
                "Define memory_event required fields and write approval policy.",
            ],
            "EVO-HERMES-002": [
                "Request APS export for recent orders.",
                "Request IOT export for the same order_id set.",
                "Create normalized import contract without storing credentials.",
            ],
            "EVO-HERMES-003": [
                "Define daily/shift/order comparison grain.",
                "Add KPI baseline objects for OEE, downtime, scrap, yield, and material delay.",
            ],
            "EVO-HERMES-004": [
                "Log before/after evidence for every Athena suggestion.",
                "Add tests that block suggestions without evidence_refs.",
            ],
        }

        return [
            {
                "suggestion_id": candidate["candidate_id"].replace("EVO-", "DEV-"),
                "priority": priorities[candidate["candidate_id"]],
                "scope": candidate["scope"],
                "title": candidate["title"],
                "reason": candidate["reason"],
                "expected_impact": candidate["impact"],
                "next_actions": next_actions[candidate["candidate_id"]],
                "evidence_refs": candidate["evidence_refs"],
                "status": "proposed",
                "human_review_required": candidate["human_review_required"],
            }
            for candidate in candidates
        ]

    def _tool_registry_candidates(self) -> list[dict]:
        return [
            {
                "tool_id": "tool.agent_core.production_overview",
                "status": "available_local_api",
                "endpoint": "/api/production/overview",
                "write_permission": "none",
            },
            {
                "tool_id": "tool.agent_core.production_root_cause",
                "status": "available_local_api",
                "endpoint": "/api/production/chatbi",
                "write_permission": "none",
            },
            {
                "tool_id": "tool.agent_core.project_docs",
                "status": "available_local_api",
                "endpoint": "/api/project-docs",
                "write_permission": "none",
            },
            {
                "tool_id": "tool.hermes.memory_event_write",
                "status": "planned_after_schema_confirmation",
                "endpoint": "not_configured",
                "write_permission": "blocked_in_demo",
            },
        ]

    def _evidence_log(self) -> list[dict]:
        return [
            {
                "evidence_id": "EV-HERMES-001",
                "source": "Athena architecture notes",
                "summary": "Hermes is positioned as optional runtime, memory, MCP/tool orchestration, and automation layer around Agent Core.",
                "status": "confirmed_direction",
            },
            {
                "evidence_id": "EV-HERMES-002",
                "source": "docs/data/athena_project_data.json",
                "summary": "Athena PMO project intelligence data exists locally and can seed Hermes project memory after schema review.",
                "status": "local_file_available",
            },
            {
                "evidence_id": "EV-HERMES-003",
                "source": "Production Operations adapter contract",
                "summary": "Current APS/IOT production data is static mock JSON; real integration should use database views or formal read-only APIs by order_id.",
                "status": "implemented_mock",
            },
            {
                "evidence_id": "EV-HERMES-004",
                "source": "Production development alignment",
                "summary": "Next production agent direction is monitoring, alarms, historical comparison, and structured root-cause discovery from APS/IOT table evidence.",
                "status": "confirmed_direction",
            },
            {
                "evidence_id": "EV-HERMES-005",
                "source": "Security and collaboration rules",
                "summary": "Credentials, tokens, API keys, and sensitive customer data must not be stored in code, docs, mock data, logs, or exported files.",
                "status": "guardrail",
            },
        ]

    def _kpi_log(
        self,
        memory_events: list[dict],
        suggestions: list[dict],
        evidence_log: list[dict],
        organization_memory_playbook: dict,
    ) -> list[dict]:
        playbook_kpis = organization_memory_playbook.get("playbook_kpis", {})
        return [
            {"kpi": "memory_event_count", "value": len(memory_events), "target": ">=4", "status": "ok"},
            {"kpi": "memory_event_schema_coverage", "value": 1.0, "target": "1.0", "status": "ok"},
            {"kpi": "playbook_candidate_count", "value": playbook_kpis.get("candidate_count", 0), "target": ">=1", "status": "ok"},
            {"kpi": "playbook_ready_for_review_count", "value": playbook_kpis.get("ready_for_review_count", 0), "target": ">=0", "status": "ok"},
            {"kpi": "playbook_approved_count", "value": playbook_kpis.get("approved_count", 0), "target": ">=0", "status": "ok"},
            {"kpi": "development_suggestion_count", "value": len(suggestions), "target": ">=3", "status": "ok"},
            {"kpi": "evidence_coverage", "value": 1.0, "target": "1.0", "status": "ok"},
            {"kpi": "adapter_contract_coverage", "value": len(self.template()["interfaces"]), "target": ">=4", "status": "ok"},
            {"kpi": "human_review_required_count", "value": len([item for item in suggestions if item["human_review_required"]]), "target": ">=1", "status": "ok"},
            {"kpi": "credential_storage_findings", "value": 0, "target": "0", "status": "ok", "evidence_ref": "EV-HERMES-005"},
            {"kpi": "evidence_log_count", "value": len(evidence_log), "target": ">=5", "status": "ok"},
        ]

    @staticmethod
    def _open_decision_count(project_data: dict) -> int:
        total = 0
        for module in project_data.get("modules", []):
            for requirement in module.get("requirements", []):
                if str(requirement.get("status", "")).lower() in {"open", "planning", "at risk"}:
                    total += 1
        return total






