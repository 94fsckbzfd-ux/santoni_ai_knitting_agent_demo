"""Automatic training loop contract for Athena.

The current loop is a deterministic local evaluator over structured training
packs. It is not model-weight fine tuning and it is not connected to live
Hermes yet. The goal is to make training progress visible, repeatable, and
ready for a future Hermes runner that returns JSON evaluation results.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean

from agent_core.workflows.hermes_integration_workflow import HermesIntegrationWorkflow


TRAINING_VERSION = "v0.113.0"
TRAINING_TEMPLATE_ID = "athena.training_automation.v1"
TRAINING_PACK_PATH = Path(__file__).resolve().parents[3] / "docs" / "training" / "tianpai_training_pack_v0_1.json"
TRAINING_REVIEW_PATH = Path(__file__).resolve().parents[2] / "mock_data" / "training_task_reviews.json"


@dataclass(frozen=True)
class TrainingStage:
    id: str
    name: str
    status: str
    owner: str
    input_object: str
    output_object: str
    evidence_ref: str


DATA_NEEDED_BY_TASK = {
    "TPI-GM-DELIVERY-001": "Detailed APS weaving schedule rows and an order_id join rule are still needed before Athena can calculate order-level delivery root cause.",
    "TPI-GM-COST-001": "Purchasing, labor, and per-order cost records are still needed before Athena can calculate real-time per-garment cost.",
    "TPI-PROCESS-STAGES-001": "Stage-level timestamps, quantities, WIP, hold, defect, and rework records are still needed before downstream bottleneck training.",
}


CAPABILITY_GROUPS = {
    "manager_priority_understanding": "management_priority",
    "data_gap_explanation": "data_boundary",
    "machine_downtime_ranking": "machine_monitoring",
    "scrap_root_cause_seed": "quality_and_scrap",
    "fault_root_cause_seed": "service_signal",
    "cost_capability_boundary": "cost_boundary",
    "order_mainline_workflow_understanding": "workflow_boundary",
    "tenant_workflow_boundary": "workflow_boundary",
    "physical_process_stage_mapping": "process_mapping",
}


def training_automation_template() -> dict:
    stages = [
        TrainingStage(
            "load_training_pack",
            "Load Tianpai training pack",
            "implemented_mock",
            "Athena Training Console",
            "tianpai_training_pack",
            "training_context",
            "EV-TRAIN-001",
        ),
        TrainingStage(
            "generate_tasks",
            "Generate capability training tasks",
            "implemented_mock",
            "Athena Training Console",
            "candidate_training_tasks",
            "training_task_queue",
            "EV-TRAIN-002",
        ),
        TrainingStage(
            "auto_evaluate",
            "Run automatic evidence evaluation",
            "implemented_mock",
            "Athena Training Evaluator",
            "training_task_queue",
            "evaluation_json",
            "EV-TRAIN-003",
        ),
        TrainingStage(
            "hermes_result_contract",
            "Prepare Hermes result payload",
            "mock_contract",
            "Hermes Adapter",
            "evaluation_json",
            "hermes_training_result",
            "EV-TRAIN-004",
        ),
        TrainingStage(
            "playbook_regression_queue",
            "Prepare playbook regression queue",
            "mock_contract",
            "Training Console",
            "approved_playbook_candidates",
            "playbook_regression_queue",
            "EV-TRAIN-005",
        ),
        TrainingStage(
            "automatic_regression_runner",
            "Run local regression cases",
            "implemented_mock",
            "Athena Training Evaluator",
            "approved_baseline_and_playbook_queue",
            "regression_run_result",
            "EV-TRAIN-006",
        ),
        TrainingStage(
            "regression_gate",
            "Evaluate regression gate",
            "implemented_mock",
            "Athena Training Evaluator",
            "regression_run_result",
            "regression_gate_decision",
            "EV-TRAIN-007",
        ),
        TrainingStage(
            "next_loop_handoff",
            "Prepare next-loop handoff",
            "implemented_mock",
            "Training Console",
            "regression_gate_decision",
            "next_loop_handoff",
            "EV-TRAIN-008",
        ),
        TrainingStage(
            "next_loop_handoff_review",
            "Record next-loop handoff decisions",
            "implemented_mock",
            "Product Owner",
            "next_loop_handoff",
            "handoff_review_state",
            "EV-TRAIN-009",
        ),
        TrainingStage(
            "next_loop_closure_gate",
            "Evaluate next-loop closure gate",
            "implemented_mock",
            "Athena Training Evaluator",
            "next_loop_handoff_and_review_state",
            "next_loop_closure_decision",
            "EV-TRAIN-010",
        ),
        TrainingStage(
            "training_iteration_proposal",
            "Prepare training iteration proposal",
            "implemented_mock",
            "Training Console",
            "next_loop_closure_decision",
            "training_iteration_proposal",
            "EV-TRAIN-011",
        ),
        TrainingStage(
            "training_iteration_proposal_review",
            "Record training iteration proposal decision",
            "implemented_mock",
            "Product Owner",
            "training_iteration_proposal",
            "training_iteration_proposal_review_state",
            "EV-TRAIN-012",
        ),
        TrainingStage(
            "codex_work_packet_queue",
            "Prepare Codex work packet queue",
            "mock_contract",
            "Training Console",
            "training_iteration_proposal_review_state",
            "codex_work_packet_queue",
            "EV-TRAIN-013",
        ),
        TrainingStage(
            "codex_patch_queue",
            "Prepare Codex patch queue contract",
            "mock_contract",
            "Codex",
            "codex_work_packet_queue",
            "codex_patch_queue_contract",
            "EV-TRAIN-014",
        ),
        TrainingStage(
            "human_gate",
            "Apply Codex execution gate",
            "mock_contract",
            "Product Owner",
            "codex_patch_queue_contract",
            "codex_execution_gate_decision",
            "EV-TRAIN-015",
        ),
        TrainingStage(
            "codex_execution_gate_review",
            "Record Codex execution gate decisions",
            "implemented_mock",
            "Product Owner",
            "codex_execution_gate_decision",
            "codex_execution_review_state",
            "EV-TRAIN-016",
        ),
        TrainingStage(
            "codex_worktree_preparation_queue",
            "Prepare Codex worktree preparation queue",
            "mock_contract",
            "Codex",
            "codex_execution_review_state",
            "codex_worktree_preparation_queue",
            "EV-TRAIN-017",
        ),
        TrainingStage(
            "codex_worktree_launch_gate",
            "Evaluate Codex worktree launch gate",
            "mock_contract",
            "Product Owner",
            "codex_worktree_preparation_queue",
            "codex_worktree_launch_gate",
            "EV-TRAIN-018",
        ),
        TrainingStage(
            "codex_worktree_result_intake",
            "Record Codex worktree result intake",
            "implemented_mock",
            "Codex",
            "codex_worktree_launch_gate",
            "codex_worktree_result_intake",
            "EV-TRAIN-019",
        ),
        TrainingStage(
            "codex_worktree_result_review_gate",
            "Review Codex worktree result promotion",
            "implemented_mock",
            "Product Owner",
            "codex_worktree_result_intake",
            "codex_worktree_result_review_gate",
            "EV-TRAIN-020",
        ),
        TrainingStage(
            "codex_promotion_candidate_queue",
            "Prepare Codex promotion candidate queue",
            "mock_contract",
            "Training Console",
            "codex_worktree_result_review_gate",
            "codex_promotion_candidate_queue",
            "EV-TRAIN-021",
        ),
        TrainingStage(
            "codex_promotion_approval_gate",
            "Record Codex promotion candidate approvals",
            "implemented_mock",
            "Product Owner",
            "codex_promotion_candidate_queue",
            "codex_promotion_approval_gate",
            "EV-TRAIN-022",
        ),
        TrainingStage(
            "codex_promotion_handoff_queue",
            "Prepare Codex promotion execution handoff",
            "mock_contract",
            "Training Console",
            "codex_promotion_approval_gate",
            "codex_promotion_handoff_queue",
            "EV-TRAIN-023",
        ),
        TrainingStage(
            "codex_promotion_execution_readiness_gate",
            "Evaluate Codex promotion execution readiness",
            "mock_contract",
            "Training Console",
            "codex_promotion_handoff_queue",
            "codex_promotion_execution_readiness_gate",
            "EV-TRAIN-024",
        ),
        TrainingStage(
            "codex_promotion_execution_readiness_review",
            "Record Codex promotion execution readiness review",
            "implemented_mock",
            "Product Owner",
            "codex_promotion_execution_readiness_gate",
            "codex_promotion_execution_readiness_review",
            "EV-TRAIN-025",
        ),
        TrainingStage(
            "codex_promotion_execution_result_intake",
            "Record Codex promotion execution result intake",
            "implemented_mock",
            "Product Owner",
            "codex_promotion_execution_readiness_review",
            "codex_promotion_execution_result_intake",
            "EV-TRAIN-026",
        ),
        TrainingStage(
            "codex_promotion_closure_audit",
            "Audit Codex promotion closure and Hermes sync",
            "implemented_mock",
            "Training Console",
            "codex_promotion_execution_result_intake",
            "codex_promotion_closure_audit",
            "EV-TRAIN-027",
        ),
        TrainingStage(
            "codex_promotion_sync_review_gate",
            "Record Codex promotion sync review decisions",
            "implemented_mock",
            "Product Owner",
            "codex_promotion_closure_audit",
            "codex_promotion_sync_review_gate",
            "EV-TRAIN-028",
        ),
        TrainingStage(
            "codex_promotion_sync_handoff_queue",
            "Prepare Codex promotion sync handoff",
            "mock_contract",
            "Training Console",
            "codex_promotion_sync_review_gate",
            "codex_promotion_sync_handoff_queue",
            "EV-TRAIN-029",
        ),
        TrainingStage(
            "codex_promotion_sync_execution_readiness_gate",
            "Evaluate Codex promotion sync execution readiness",
            "mock_contract",
            "Training Console",
            "codex_promotion_sync_handoff_queue",
            "codex_promotion_sync_execution_readiness_gate",
            "EV-TRAIN-030",
        ),
        TrainingStage(
            "codex_promotion_sync_execution_readiness_review",
            "Record Codex promotion sync execution readiness review",
            "implemented_mock",
            "Product Owner",
            "codex_promotion_sync_execution_readiness_gate",
            "codex_promotion_sync_execution_readiness_review",
            "EV-TRAIN-031",
        ),
        TrainingStage(
            "codex_promotion_sync_execution_result_intake",
            "Record Codex promotion sync execution result intake",
            "implemented_mock",
            "Product Owner",
            "codex_promotion_sync_execution_readiness_review",
            "codex_promotion_sync_execution_result_intake",
            "EV-TRAIN-032",
        ),
        TrainingStage(
            "codex_promotion_sync_closure_audit",
            "Audit Codex promotion sync closure",
            "implemented_mock",
            "Training Console",
            "codex_promotion_sync_execution_result_intake",
            "codex_promotion_sync_closure_audit",
            "EV-TRAIN-033",
        ),
        TrainingStage(
            "codex_promotion_sync_closure_review_gate",
            "Record Codex promotion sync closure review decisions",
            "implemented_mock",
            "Product Owner",
            "codex_promotion_sync_closure_audit",
            "codex_promotion_sync_closure_review_gate",
            "EV-TRAIN-034",
        ),
        TrainingStage(
            "codex_promotion_final_sync_handoff_queue",
            "Prepare Codex promotion final sync handoff queue",
            "mock_contract",
            "Training Console",
            "codex_promotion_sync_closure_review_gate",
            "codex_promotion_final_sync_handoff_queue",
            "EV-TRAIN-035",
        ),
        TrainingStage(
            "codex_promotion_final_sync_execution_readiness_gate",
            "Evaluate Codex promotion final sync execution readiness",
            "mock_contract",
            "Training Console",
            "codex_promotion_final_sync_handoff_queue",
            "codex_promotion_final_sync_execution_readiness_gate",
            "EV-TRAIN-036",
        ),
        TrainingStage(
            "codex_promotion_final_sync_execution_result_intake",
            "Record Codex promotion final sync execution result metadata",
            "implemented_mock",
            "Training Console",
            "codex_promotion_final_sync_execution_readiness_gate",
            "codex_promotion_final_sync_execution_result_intake",
            "EV-TRAIN-037",
        ),
        TrainingStage(
            "codex_promotion_final_sync_closure_audit",
            "Audit Codex promotion final sync closure",
            "implemented_mock",
            "Training Console",
            "codex_promotion_final_sync_execution_result_intake",
            "codex_promotion_final_sync_closure_audit",
            "EV-TRAIN-038",
        ),
        TrainingStage(
            "codex_promotion_final_completion_review_gate",
            "Record Codex promotion final completion review decisions",
            "implemented_mock",
            "Product Owner",
            "codex_promotion_final_sync_closure_audit",
            "codex_promotion_final_completion_review_gate",
            "EV-TRAIN-039",
        ),
        TrainingStage(
            "codex_promotion_final_publication_handoff_queue",
            "Prepare Codex promotion final publication handoff queue",
            "mock_contract",
            "Training Console",
            "codex_promotion_final_completion_review_gate",
            "codex_promotion_final_publication_handoff_queue",
            "EV-TRAIN-040",
        ),
        TrainingStage(
            "codex_promotion_final_publication_readiness_gate",
            "Evaluate Codex promotion final publication readiness",
            "mock_contract",
            "Training Console",
            "codex_promotion_final_publication_handoff_queue",
            "codex_promotion_final_publication_readiness_gate",
            "EV-TRAIN-041",
        ),
        TrainingStage(
            "codex_promotion_final_publication_result_intake",
            "Record Codex promotion final publication result metadata",
            "implemented_mock",
            "Training Console",
            "codex_promotion_final_publication_readiness_gate",
            "codex_promotion_final_publication_result_intake",
            "EV-TRAIN-042",
        ),
        TrainingStage(
            "codex_promotion_final_publication_closure_audit",
            "Audit Codex promotion final publication closure",
            "implemented_mock",
            "Training Console",
            "codex_promotion_final_publication_result_intake",
            "codex_promotion_final_publication_closure_audit",
            "EV-TRAIN-043",
        ),
        TrainingStage(
            "codex_promotion_final_release_review_gate",
            "Prepare Codex promotion final release and archive review gate",
            "implemented_mock",
            "Product Owner",
            "codex_promotion_final_publication_closure_audit",
            "codex_promotion_final_release_review_gate",
            "EV-TRAIN-044",
        ),
    ]
    return {
        "template_id": TRAINING_TEMPLATE_ID,
        "version": TRAINING_VERSION,
        "name": "Athena automatic training loop",
        "positioning": (
            "A local automatic evaluation console for Athena training tasks. It runs structured task checks, "
            "emits Hermes-style JSON, and prepares the next Codex/Hermes iteration queue."
        ),
        "automation_mode": "local_auto_evaluation",
        "adapter_status": "mock_contract",
        "real_hermes_connected": False,
        "model_weight_finetuning": False,
        "target_persona": "tianpai_general_manager",
        "answer_contract": ["management_summary", "reason_and_evidence", "recommended_action"],
        "capability_groups": sorted(set(CAPABILITY_GROUPS.values())),
        "stages": [asdict(stage) for stage in stages],
        "blocked_actions": [
            "write_hermes_memory_without_schema_review",
            "run_model_weight_finetuning_from_demo",
            "write_to_aps_or_iot",
            "change_production_schedule",
            "auto_patch_large_feature_without_human_confirmation",
            "promote_tenant_memory_to_domain_without_review",
            "store_credentials_or_tokens",
        ],
        "automation_boundary": {
            "automatic": [
                "run structured evaluation tasks",
                "produce JSON test results",
                "flag failed checks and missing evidence",
                "prepare small-fix patch candidates",
                "prepare next training tasks from evidence gaps",
                "prepare approved playbook candidates as regression-case candidates",
                "run local regression cases over approved baseline and approved playbook candidates",
                "evaluate regression gate before Codex/Hermes next-loop decisions",
                "prepare local next-loop handoff for automatic, human-review, and data-request queues",
                "record metadata-only handoff decisions without executing blocked work",
                "evaluate next-loop closure readiness from handoff reviews",
                "prepare read-only training iteration proposals from closure gate results",
                "record metadata-only training iteration proposal decisions",
                "prepare read-only Codex work packet queues from approved iteration proposals",
                "prepare read-only Codex patch queue contracts from ready work packets",
                "evaluate read-only Codex execution gates before any future patch execution",
                "prepare read-only Codex worktree preparation queues from approved execution reviews",
                "evaluate read-only Codex worktree launch gates before any local worktree action",
                "record metadata-only Codex worktree result summaries after explicit user-launched work",
                "record metadata-only Codex worktree result review decisions before regression or Hermes promotion",
                "prepare read-only Codex promotion candidate queues from approved result reviews",
                "record metadata-only promotion execution readiness reviews before any manual execution confirmation",
                "record metadata-only promotion execution results after explicit manual execution outside the demo",
                "audit metadata-only promotion closure and future Hermes synchronization readiness",
                "record metadata-only sync review decisions before any future baseline update or live Hermes write",
                "prepare read-only sync handoff contracts from approved future sync actions",
                "evaluate sync handoff execution readiness before any future baseline update or live Hermes write",
                "record metadata-only sync execution readiness reviews before any real synchronization",
                "record metadata-only final sync closure review decisions before any future baseline update or live Hermes write",
                "prepare read-only final sync handoff contracts from approved closure review future actions",
                "evaluate final sync execution readiness before any future baseline update or live Hermes write",
                "record metadata-only final sync execution results after explicit manual execution outside the demo",
                "audit metadata-only final sync closure readiness without claiming real baseline or Hermes success",
                "record metadata-only final completion review decisions before any project-memory, baseline, or Hermes completion claim",
            ],
            "human_confirmation_required": [
                "large feature changes",
                "new pages",
                "real data integration",
                "feature-version changes",
                "major-version changes",
                "tenant memory promotion",
            ],
        },
        "candidate_endpoints": [
            {"method": "GET", "path": "/api/training/template", "purpose": "Return the automatic training template."},
            {"method": "GET", "path": "/api/training/overview", "purpose": "Return the latest local automatic training snapshot."},
            {"method": "POST", "path": "/api/training/run", "purpose": "Run the deterministic local training evaluator and return Hermes-style JSON."},
            {"method": "GET", "path": "/api/training/reviews", "purpose": "Return task review and registered data-source status."},
            {"method": "POST", "path": "/api/training/review", "purpose": "Approve, request changes, reject, or annotate a training task."},
            {"method": "POST", "path": "/api/training/data-source", "purpose": "Register, skip, or mark unavailable a needed data source without uploading raw files."},
            {"method": "GET", "path": "/api/training/round-summary", "purpose": "Return the current training round summary and baseline-readiness status."},
            {"method": "POST", "path": "/api/training/promote-baseline", "purpose": "Promote approved training tasks into the automatic regression baseline."},
            {"method": "GET", "path": "/api/training/playbook-regression", "purpose": "Return approved Hermes playbook candidates prepared as local regression-case candidates."},
            {"method": "GET", "path": "/api/training/regression-run", "purpose": "Return the latest deterministic local regression run without live Hermes execution."},
            {"method": "POST", "path": "/api/training/regression-run", "purpose": "Run the deterministic local regression evaluator over approved baseline and playbook candidates."},
            {"method": "GET", "path": "/api/training/regression-gate", "purpose": "Return the local regression gate and Codex/Hermes next-loop decision."},
            {"method": "POST", "path": "/api/training/regression-gate", "purpose": "Evaluate the local regression gate using optional pass-rate threshold."},
            {"method": "GET", "path": "/api/training/next-loop", "purpose": "Return the local next-loop handoff with automatic, human-review, and data-request queues."},
            {"method": "POST", "path": "/api/training/next-loop", "purpose": "Prepare a local next-loop handoff using optional pass-rate threshold and focus filters."},
            {"method": "GET", "path": "/api/training/handoff-reviews", "purpose": "Return metadata-only next-loop handoff review decisions."},
            {"method": "POST", "path": "/api/training/handoff-review", "purpose": "Record a metadata-only decision for one next-loop handoff item."},
            {"method": "GET", "path": "/api/training/next-loop-closure", "purpose": "Return the local next-loop closure gate over handoff decisions."},
            {"method": "POST", "path": "/api/training/next-loop-closure", "purpose": "Evaluate the local next-loop closure gate with optional threshold and focus filters."},
            {"method": "GET", "path": "/api/training/iteration-proposal", "purpose": "Return the read-only local training iteration proposal from the closure gate."},
            {"method": "POST", "path": "/api/training/iteration-proposal", "purpose": "Prepare a read-only local training iteration proposal with optional threshold and focus filters."},
            {"method": "GET", "path": "/api/training/iteration-proposal-reviews", "purpose": "Return metadata-only training iteration proposal review decisions."},
            {"method": "POST", "path": "/api/training/iteration-proposal-review", "purpose": "Record a metadata-only review decision for one training iteration proposal."},
            {"method": "GET", "path": "/api/training/codex-work-packets", "purpose": "Return read-only Codex work packets prepared from approved training iteration proposals."},
            {"method": "POST", "path": "/api/training/codex-work-packets", "purpose": "Prepare read-only Codex work packets with optional threshold and focus filters."},
            {"method": "GET", "path": "/api/training/codex-patch-queue", "purpose": "Return read-only Codex patch candidates prepared from ready Codex work packets."},
            {"method": "POST", "path": "/api/training/codex-patch-queue", "purpose": "Prepare read-only Codex patch candidates with optional threshold and focus filters."},
            {"method": "GET", "path": "/api/training/codex-execution-gate", "purpose": "Return the read-only execution gate for Codex patch candidates."},
            {"method": "POST", "path": "/api/training/codex-execution-gate", "purpose": "Evaluate the read-only execution gate for Codex patch candidates with optional filters."},
            {"method": "GET", "path": "/api/training/codex-execution-reviews", "purpose": "Return metadata-only Codex execution gate review decisions."},
            {"method": "POST", "path": "/api/training/codex-execution-review", "purpose": "Record a metadata-only review decision for one Codex execution candidate."},
            {"method": "GET", "path": "/api/training/codex-worktree-prep", "purpose": "Return read-only Codex worktree preparation tasks from approved execution reviews."},
            {"method": "POST", "path": "/api/training/codex-worktree-prep", "purpose": "Prepare read-only Codex worktree preparation tasks with optional filters."},
            {"method": "GET", "path": "/api/training/codex-worktree-launch", "purpose": "Return the read-only launch gate for approved Codex worktree preparation tasks."},
            {"method": "POST", "path": "/api/training/codex-worktree-launch", "purpose": "Evaluate the read-only Codex worktree launch gate with optional filters."},
            {"method": "GET", "path": "/api/training/codex-worktree-results", "purpose": "Return metadata-only Codex worktree result intake state."},
            {"method": "POST", "path": "/api/training/codex-worktree-result", "purpose": "Record metadata-only Codex worktree result summary, changed-file paths, and validation status."},
            {"method": "GET", "path": "/api/training/codex-worktree-result-review-gate", "purpose": "Return metadata-only Codex worktree result review and promotion gate."},
            {"method": "GET", "path": "/api/training/codex-worktree-result-reviews", "purpose": "Return metadata-only Codex worktree result review decisions."},
            {"method": "POST", "path": "/api/training/codex-worktree-result-review", "purpose": "Record a metadata-only review decision for one Codex worktree result."},
            {"method": "GET", "path": "/api/training/codex-promotion-candidates", "purpose": "Return read-only regression and Hermes promotion candidates from approved worktree result reviews."},
            {"method": "POST", "path": "/api/training/codex-promotion-candidates", "purpose": "Prepare read-only promotion candidates with optional filters."},
            {"method": "GET", "path": "/api/training/codex-promotion-approval-gate", "purpose": "Return metadata-only promotion candidate approval gate."},
            {"method": "GET", "path": "/api/training/codex-promotion-approvals", "purpose": "Return metadata-only promotion approval decisions."},
            {"method": "POST", "path": "/api/training/codex-promotion-approval", "purpose": "Record a metadata-only product-owner decision for one promotion candidate."},
            {"method": "GET", "path": "/api/training/codex-promotion-handoff", "purpose": "Return read-only manual promotion handoff contracts."},
            {"method": "POST", "path": "/api/training/codex-promotion-handoff", "purpose": "Prepare read-only manual promotion handoff contracts with optional filters."},
            {"method": "GET", "path": "/api/training/codex-promotion-execution-readiness", "purpose": "Return promotion execution readiness gate over manual handoff items."},
            {"method": "POST", "path": "/api/training/codex-promotion-execution-readiness", "purpose": "Evaluate promotion execution readiness with optional filters."},
            {"method": "GET", "path": "/api/training/codex-promotion-readiness-reviews", "purpose": "Return metadata-only promotion execution readiness review decisions."},
            {"method": "POST", "path": "/api/training/codex-promotion-readiness-review", "purpose": "Record a metadata-only review decision for one promotion execution readiness item."},
            {"method": "GET", "path": "/api/training/codex-promotion-execution-results", "purpose": "Return metadata-only promotion execution result intake state."},
            {"method": "POST", "path": "/api/training/codex-promotion-execution-result", "purpose": "Record metadata-only result summary after explicit manual promotion execution."},
            {"method": "GET", "path": "/api/training/codex-promotion-closure-audit", "purpose": "Return the read-only closure and future Hermes sync audit over recorded promotion execution results."},
            {"method": "POST", "path": "/api/training/codex-promotion-closure-audit", "purpose": "Evaluate the read-only promotion closure audit with optional filters."},
            {"method": "GET", "path": "/api/training/codex-promotion-sync-review-gate", "purpose": "Return metadata-only product-owner sync review gate over closure audit candidates."},
            {"method": "GET", "path": "/api/training/codex-promotion-sync-reviews", "purpose": "Return metadata-only sync review decisions."},
            {"method": "POST", "path": "/api/training/codex-promotion-sync-review", "purpose": "Record a metadata-only sync review decision for one closure audit candidate."},
            {"method": "GET", "path": "/api/training/codex-promotion-sync-handoff", "purpose": "Return read-only manual sync handoff contracts from approved future sync actions."},
            {"method": "POST", "path": "/api/training/codex-promotion-sync-handoff", "purpose": "Prepare read-only manual sync handoff contracts with optional filters."},
            {"method": "GET", "path": "/api/training/codex-promotion-sync-readiness", "purpose": "Return read-only sync execution readiness over manual sync handoff items."},
            {"method": "POST", "path": "/api/training/codex-promotion-sync-readiness", "purpose": "Evaluate sync execution readiness with optional confirmed prerequisite inputs."},
            {"method": "GET", "path": "/api/training/codex-promotion-sync-readiness-reviews", "purpose": "Return metadata-only sync execution readiness review decisions."},
            {"method": "POST", "path": "/api/training/codex-promotion-sync-readiness-review", "purpose": "Record a metadata-only review decision for one sync execution readiness item."},
            {"method": "GET", "path": "/api/training/codex-promotion-sync-execution-results", "purpose": "Return metadata-only sync execution result intake state."},
            {"method": "POST", "path": "/api/training/codex-promotion-sync-execution-result", "purpose": "Record metadata-only result summary after explicit manual sync execution."},
            {"method": "GET", "path": "/api/training/codex-promotion-sync-closure-audit", "purpose": "Return the read-only closure audit over recorded sync execution results."},
            {"method": "GET", "path": "/api/training/codex-promotion-sync-closure-review-gate", "purpose": "Return metadata-only final sync closure review gate decisions and future action plans."},
            {"method": "GET", "path": "/api/training/codex-promotion-sync-closure-reviews", "purpose": "Return metadata-only final sync closure review decisions."},
            {"method": "POST", "path": "/api/training/codex-promotion-sync-closure-review", "purpose": "Record a metadata-only final sync closure review decision."},
            {"method": "GET", "path": "/api/training/codex-promotion-final-sync-handoff", "purpose": "Return read-only final sync handoff contracts from approved sync closure review actions."},
            {"method": "POST", "path": "/api/training/codex-promotion-final-sync-handoff", "purpose": "Prepare read-only final sync handoff contracts with optional filters."},
            {"method": "GET", "path": "/api/training/codex-promotion-final-sync-readiness", "purpose": "Return read-only final sync execution readiness over final sync handoff contracts."},
            {"method": "POST", "path": "/api/training/codex-promotion-final-sync-readiness", "purpose": "Evaluate final sync execution readiness with optional confirmed prerequisite inputs."},
            {"method": "GET", "path": "/api/training/codex-promotion-final-sync-execution-results", "purpose": "Return metadata-only final sync execution result intake state."},
            {"method": "POST", "path": "/api/training/codex-promotion-final-sync-execution-result", "purpose": "Record metadata-only result summary after explicit manual final sync execution."},
            {"method": "GET", "path": "/api/training/codex-promotion-final-sync-closure-audit", "purpose": "Return the read-only closure audit over recorded final sync execution results."},
            {"method": "GET", "path": "/api/training/codex-promotion-final-completion-review-gate", "purpose": "Return metadata-only final completion review gate decisions before any real publication."},
            {"method": "GET", "path": "/api/training/codex-promotion-final-completion-reviews", "purpose": "Return metadata-only final completion review decisions."},
            {"method": "POST", "path": "/api/training/codex-promotion-final-completion-review", "purpose": "Record a metadata-only final completion review decision."},
            {"method": "GET", "path": "/api/training/codex-promotion-final-publication-handoff", "purpose": "Return read-only final publication handoff contracts from approved final completion publication plans."},
            {"method": "POST", "path": "/api/training/codex-promotion-final-publication-handoff", "purpose": "Prepare read-only final publication handoff contracts with optional filters."},
            {"method": "GET", "path": "/api/training/codex-promotion-final-publication-readiness", "purpose": "Return read-only final publication readiness over final publication handoff contracts."},
            {"method": "POST", "path": "/api/training/codex-promotion-final-publication-readiness", "purpose": "Evaluate final publication readiness with optional confirmed publication inputs."},
            {"method": "GET", "path": "/api/training/codex-promotion-final-publication-results", "purpose": "Return metadata-only final publication result intake state."},
            {"method": "POST", "path": "/api/training/codex-promotion-final-publication-result", "purpose": "Record metadata-only result summary after explicit manual final publication."},
        ],
        "kpis": [
            "training_task_count",
            "auto_evaluated_task_count",
            "passed_task_count",
            "needs_data_task_count",
            "failed_task_count",
            "average_score",
            "evidence_resolution_rate",
            "governance_alignment_rate",
            "human_review_required_count",
            "baseline_regression_task_count",
            "playbook_regression_candidate_count",
            "playbook_regression_ready_count",
            "regression_case_count",
            "regression_pass_rate",
            "regression_gate_allowed",
            "next_loop_automatic_action_count",
            "next_loop_human_review_count",
            "next_loop_data_request_count",
            "next_loop_handoff_review_count",
            "next_loop_closure_open_item_count",
            "next_loop_closure_ready",
            "training_iteration_proposal_ready",
            "training_iteration_task_seed_count",
            "training_iteration_proposal_review_count",
            "training_iteration_proposal_approved",
            "codex_work_packet_queue_ready",
            "codex_work_packet_count",
            "codex_patch_queue_ready",
            "codex_patch_candidate_count",
            "codex_execution_gate_ready",
            "codex_execution_candidate_count",
            "codex_execution_review_count",
            "codex_worktree_preparation_approved_count",
            "codex_worktree_preparation_queue_ready",
            "codex_worktree_preparation_task_count",
            "codex_worktree_launch_gate_ready",
            "codex_worktree_launch_request_count",
            "codex_worktree_result_count",
            "codex_worktree_validation_passed_count",
            "codex_worktree_validation_failed_count",
            "codex_automatic_result_merge_allowed",
            "codex_worktree_result_review_count",
            "codex_worktree_regression_promotion_candidate_count",
            "codex_worktree_hermes_memory_candidate_count",
            "codex_automatic_result_promotion_allowed",
            "codex_promotion_candidate_queue_ready",
            "codex_regression_promotion_candidate_count",
            "codex_hermes_memory_promotion_candidate_count",
            "codex_promotion_execution_readiness_review_count",
            "codex_promotion_execution_readiness_confirmed_count",
            "codex_promotion_execution_result_count",
            "codex_promotion_execution_result_passed_count",
            "codex_promotion_closure_ready",
            "codex_promotion_sync_audit_candidate_count",
            "codex_promotion_sync_review_count",
            "codex_promotion_sync_approved_count",
            "codex_promotion_sync_handoff_queue_ready",
            "codex_promotion_sync_handoff_item_count",
            "codex_promotion_sync_execution_readiness_ready",
            "codex_promotion_sync_execution_readiness_item_count",
            "codex_promotion_sync_execution_blocked_item_count",
            "codex_promotion_sync_readiness_review_count",
            "codex_promotion_sync_readiness_confirmed_count",
            "codex_promotion_sync_execution_result_count",
            "codex_promotion_sync_execution_result_passed_count",
            "codex_promotion_sync_execution_result_contract_complete_count",
            "codex_promotion_sync_closure_ready",
            "codex_promotion_sync_closure_expected_result_count",
            "codex_promotion_sync_closure_complete_result_count",
            "codex_promotion_sync_closure_automatic_allowed",
            "codex_promotion_sync_closure_review_gate_ready",
            "codex_promotion_sync_closure_review_candidate_count",
            "codex_promotion_sync_closure_review_count",
            "codex_promotion_sync_closure_approved_count",
            "codex_promotion_sync_closure_review_automatic_allowed",
            "codex_promotion_final_sync_handoff_queue_ready",
            "codex_promotion_final_sync_handoff_item_count",
            "codex_promotion_final_sync_handoff_hermes_count",
            "codex_promotion_final_sync_handoff_regression_count",
            "codex_promotion_final_sync_handoff_automatic_allowed",
            "codex_promotion_final_sync_execution_readiness_ready",
            "codex_promotion_final_sync_execution_readiness_item_count",
            "codex_promotion_final_sync_execution_blocked_item_count",
            "codex_promotion_final_sync_execution_confirmed_count",
            "codex_promotion_final_sync_execution_automatic_allowed",
            "codex_promotion_final_sync_execution_result_count",
            "codex_promotion_final_sync_execution_result_passed_count",
            "codex_promotion_final_sync_execution_result_contract_complete_count",
            "codex_promotion_final_sync_execution_result_automatic_allowed",
            "codex_promotion_final_sync_closure_ready",
            "codex_promotion_final_sync_closure_expected_result_count",
            "codex_promotion_final_sync_closure_complete_result_count",
            "codex_promotion_final_sync_closure_missing_result_count",
            "codex_promotion_final_sync_closure_automatic_allowed",
            "codex_promotion_final_completion_review_gate_ready",
            "codex_promotion_final_completion_review_candidate_count",
            "codex_promotion_final_completion_review_count",
            "codex_promotion_final_completion_approved_count",
            "codex_promotion_final_completion_review_automatic_allowed",
            "codex_promotion_final_publication_handoff_ready",
            "codex_promotion_final_publication_handoff_item_count",
            "codex_promotion_final_publication_handoff_hermes_count",
            "codex_promotion_final_publication_handoff_regression_count",
            "codex_promotion_final_publication_handoff_automatic_allowed",
            "codex_promotion_final_publication_readiness_ready",
            "codex_promotion_final_publication_readiness_item_count",
            "codex_promotion_final_publication_blocked_item_count",
            "codex_promotion_final_publication_confirmed_count",
            "codex_promotion_final_publication_automatic_allowed",
            "codex_promotion_final_publication_result_count",
            "codex_promotion_final_publication_result_passed_count",
            "codex_promotion_final_publication_result_contract_complete_count",
            "codex_promotion_final_publication_result_automatic_allowed",
        ],
    }


class TrainingAutomationWorkflow:
    """Local automatic training evaluator for Athena training packs."""

    def __init__(
        self,
        training_pack_path: Path | None = None,
        review_store_path: Path | None = None,
        hermes_workflow: HermesIntegrationWorkflow | None = None,
    ) -> None:
        self.training_pack_path = training_pack_path or TRAINING_PACK_PATH
        self.review_store_path = review_store_path or TRAINING_REVIEW_PATH
        self.hermes_workflow = hermes_workflow or HermesIntegrationWorkflow()

    def template(self) -> dict:
        return training_automation_template()

    def overview(self) -> dict:
        result = self.run({"mode": "auto", "source": "overview"})
        result["overview_only"] = True
        return result

    def run(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        pack = self._load_pack()
        focus = str(payload.get("focus") or "all").strip().lower()
        tasks = self._filter_tasks(pack.get("candidate_training_tasks", []), focus)
        evidence_index = self._evidence_index(pack)
        governance = pack.get("training_governance", {})
        results = [self._evaluate_task(task, evidence_index, governance) for task in tasks]
        review_store = self._load_review_store()
        results = self._apply_review_store(results, review_store)
        playbook_regression_queue = self._playbook_regression_queue()
        summary = self._summary(pack, results, playbook_regression_queue)
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "status": "auto_evaluated",
                "automation_mode": "local_auto_evaluation",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
                "source_training_pack": self.training_pack_path.as_posix(),
                "target_persona": summary["target_persona"],
                "focus": focus,
            },
            "training_overview": summary,
            "training_stages": self._stage_progress(results),
            "training_tasks": results,
            "review_state": self._review_state(review_store),
            "capability_progress": self._capability_progress(results),
            "hermes_result_payload": self._hermes_result_payload(pack, results, summary, playbook_regression_queue),
            "playbook_regression_queue": playbook_regression_queue,
            "codex_patch_queue": self._codex_patch_queue(results, playbook_regression_queue),
            "next_training_tasks": self._next_training_tasks(results, playbook_regression_queue),
            "evidence_log": self._evidence_log(pack, results, playbook_regression_queue),
            "kpi_log": self._kpi_log(results, playbook_regression_queue),
            "blocked_actions": self.template()["blocked_actions"],
        }

    def reviews(self) -> dict:
        return self._review_state(self._load_review_store())

    def round_summary(self) -> dict:
        result = self.run({"mode": "auto", "source": "round_summary"})
        return self._round_summary_payload(result)

    def playbook_regression(self) -> dict:
        queue = self._playbook_regression_queue()
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "playbook_regression_queue",
                "status": queue["queue_status"],
                "adapter_status": "mock_contract",
                "real_hermes_connected": False,
                "write_actions_blocked": True,
            },
            "playbook_regression_queue": queue,
            "kpi_log": self._playbook_queue_kpis(queue),
            "evidence_log": self._playbook_queue_evidence(queue),
            "blocked_actions": queue["blocked_actions"],
        }

    def regression_run(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        result = self.run({"mode": "auto", "source": "regression_run", "focus": payload.get("focus", "all")})
        round_summary = self._round_summary_payload(result)
        playbook_queue = result["playbook_regression_queue"]
        cases = self._regression_cases(result, round_summary, playbook_queue)
        executable_cases = [item for item in cases if item["regression_status"] != "blocked"]
        passed = len([item for item in executable_cases if item["regression_status"] == "passed"])
        failed = len([item for item in executable_cases if item["regression_status"] == "failed"])
        blocked = len([item for item in cases if item["regression_status"] == "blocked"])
        status = "passed" if executable_cases and failed == 0 else "attention_required"
        if not executable_cases:
            status = "blocked_no_executable_cases"
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "automatic_regression_run",
                "status": status,
                "adapter_status": "mock_contract",
                "automation_mode": "local_regression_evaluation",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "regression_overview": {
                "schema_id": "athena.automatic_regression_run.v1",
                "run_id": f"TRAIN-REGRESSION-{TRAINING_VERSION}-TPI-001",
                "version": TRAINING_VERSION,
                "status": status,
                "baseline_id": round_summary.get("baseline_id"),
                "baseline_status": round_summary.get("baseline_status"),
                "total_case_count": len(cases),
                "executable_case_count": len(executable_cases),
                "passed_case_count": passed,
                "failed_case_count": failed,
                "blocked_case_count": blocked,
                "baseline_case_count": len([item for item in cases if item["source"] == "training_baseline"]),
                "playbook_ready_case_count": len([item for item in cases if item["source"] == "approved_playbook"]),
                "playbook_blocked_case_count": len([item for item in cases if item["source"] == "blocked_playbook_candidate"]),
                "pass_rate": round(passed / len(executable_cases), 3) if executable_cases else 0,
                "real_hermes_connected": False,
                "write_actions_blocked": True,
            },
            "regression_cases": cases,
            "round_summary": round_summary,
            "playbook_regression_queue": playbook_queue,
            "kpi_log": self._regression_kpi_log(cases),
            "evidence_log": self._regression_evidence_log(cases),
            "blocked_actions": [
                "write_live_hermes_memory",
                "modify_code_from_regression_without_codex_review",
                "write_to_aps_or_iot",
                "store_raw_training_files",
                "store_credentials_or_tokens",
                "run_model_weight_finetuning_from_demo",
            ],
        }

    def regression_gate(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        threshold = self._safe_float(payload.get("pass_rate_threshold"), 1.0)
        regression = self.regression_run(payload)
        overview = regression["regression_overview"]
        gate = self._regression_gate_decision(overview, regression["regression_cases"], threshold)
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "regression_gate",
                "status": gate["gate_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_regression_gate",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "regression_gate": gate,
            "source_regression_run": overview,
            "codex_next_action_queue": self._regression_gate_codex_queue(gate),
            "hermes_feedback_payload": self._regression_gate_hermes_payload(gate, overview),
            "kpi_log": self._regression_gate_kpis(gate),
            "evidence_log": self._regression_gate_evidence(gate),
            "blocked_actions": gate["blocked_actions"],
        }

    def next_loop_handoff(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        result = self.run({"mode": "auto", "source": "next_loop_handoff", "focus": payload.get("focus", "all")})
        gate_payload = self.regression_gate(payload)
        review_store = self._load_review_store()
        handoff_reviews = self._handoff_review_state(review_store)
        handoff = self._next_loop_handoff_payload(result, gate_payload, handoff_reviews)
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "next_loop_handoff",
                "status": handoff["handoff_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_next_loop_handoff",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "next_loop_handoff": handoff,
            "handoff_review_state": handoff_reviews,
            "source_regression_gate": gate_payload["regression_gate"],
            "source_training_overview": result["training_overview"],
            "hermes_handoff_payload": self._next_loop_hermes_payload(handoff),
            "kpi_log": self._next_loop_kpis(handoff),
            "evidence_log": self._next_loop_evidence(handoff),
            "blocked_actions": handoff["blocked_actions"],
        }

    def handoff_reviews(self) -> dict:
        store = self._load_review_store()
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "next_loop_handoff_review",
                "status": "metadata_review_state",
                "adapter_status": "mock_contract",
                "automation_mode": "local_handoff_review_state",
                "real_hermes_connected": False,
                "write_actions_blocked": True,
            },
            "handoff_review_state": self._handoff_review_state(store),
            "blocked_actions": [
                "execute_handoff_item_from_review_store",
                "auto_promote_blocked_playbook_to_regression",
                "write_live_hermes_memory",
                "store_raw_training_files",
                "store_credentials_or_tokens",
            ],
        }

    def apply_handoff_review(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        handoff_item_id = self._clean(payload.get("handoff_item_id"))
        review_status = self._clean(payload.get("review_status"))
        review_note = self._clean(payload.get("review_note"))
        reviewer = self._clean(payload.get("reviewer") or "product_owner")
        item_type = self._clean(payload.get("item_type"))
        source = self._clean(payload.get("source"))
        related_case_id = self._clean(payload.get("related_case_id"))
        related_task_id = self._clean(payload.get("related_task_id"))

        allowed = {"approved_for_next_loop", "resolved", "deferred", "needs_data", "rejected", "note_only"}
        if not handoff_item_id:
            raise ValueError("handoff_item_id is required")
        if review_status not in allowed:
            raise ValueError(f"review_status must be one of {sorted(allowed)}")
        for value in [review_note, item_type, source, related_case_id, related_task_id]:
            self._ensure_safe_text(value)

        store = self._load_review_store()
        decision = {
            "handoff_item_id": handoff_item_id,
            "review_status": review_status,
            "review_note": review_note,
            "reviewer": reviewer,
            "item_type": item_type,
            "source": source,
            "related_case_id": related_case_id,
            "related_task_id": related_task_id,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
            "updated_at": self._now(),
        }
        store.setdefault("handoff_reviews", {})[handoff_item_id] = decision
        store["updated_at"] = self._now()
        self._write_review_store(store)
        return {
            "status": "saved",
            "handoff_item_id": handoff_item_id,
            "handoff_review": decision,
            "handoff_review_state": self._handoff_review_state(store),
            "review_state": self._review_state(store),
        }

    def next_loop_closure(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        handoff_payload = self.next_loop_handoff(payload)
        closure = self._next_loop_closure_decision(handoff_payload["next_loop_handoff"])
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "next_loop_closure_gate",
                "status": closure["closure_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_next_loop_closure_gate",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "next_loop_closure": closure,
            "source_next_loop_handoff": handoff_payload["next_loop_handoff"],
            "source_handoff_review_state": handoff_payload["handoff_review_state"],
            "hermes_closure_payload": self._next_loop_closure_hermes_payload(closure),
            "kpi_log": self._next_loop_closure_kpis(closure),
            "evidence_log": self._next_loop_closure_evidence(closure),
            "blocked_actions": closure["blocked_actions"],
        }

    def iteration_proposal(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        closure_payload = self.next_loop_closure(payload)
        review_store = self._load_review_store()
        proposal_review_state = self._iteration_proposal_review_state(review_store)
        proposal = self._training_iteration_proposal(closure_payload["next_loop_closure"])
        proposal = self._apply_iteration_proposal_review(proposal, proposal_review_state)
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "training_iteration_proposal",
                "status": proposal["proposal_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_training_iteration_proposal",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "training_iteration_proposal": proposal,
            "proposal_review_state": proposal_review_state,
            "source_next_loop_closure": closure_payload["next_loop_closure"],
            "hermes_iteration_payload": self._training_iteration_hermes_payload(proposal),
            "kpi_log": self._training_iteration_kpis(proposal),
            "evidence_log": self._training_iteration_evidence(proposal),
            "blocked_actions": proposal["blocked_actions"],
        }

    def iteration_proposal_reviews(self) -> dict:
        store = self._load_review_store()
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "training_iteration_proposal_review",
                "status": "metadata_review_state",
                "adapter_status": "mock_contract",
                "automation_mode": "local_iteration_proposal_review_state",
                "real_hermes_connected": False,
                "write_actions_blocked": True,
            },
            "proposal_review_state": self._iteration_proposal_review_state(store),
            "blocked_actions": [
                "execute_iteration_proposal_from_review_store",
                "auto_write_code_from_iteration_proposal_review",
                "write_live_hermes_memory",
                "store_raw_training_files",
                "store_credentials_or_tokens",
            ],
        }

    def codex_work_packets(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        proposal_payload = self.iteration_proposal(payload)
        proposal = proposal_payload["training_iteration_proposal"]
        queue = self._codex_work_packet_queue(proposal)
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_work_packet_queue",
                "status": queue["queue_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_work_packet_queue",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_work_packet_queue": queue,
            "source_training_iteration_proposal": proposal,
            "hermes_work_packet_payload": self._codex_work_packet_hermes_payload(queue),
            "kpi_log": self._codex_work_packet_kpis(queue),
            "evidence_log": self._codex_work_packet_evidence(queue),
            "blocked_actions": queue["blocked_actions"],
        }

    def codex_patch_queue(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        packet_payload = self.codex_work_packets(payload)
        training_result = self.run({"mode": "auto", "source": "codex_patch_queue", "focus": payload.get("focus", "all")})
        queue = self._codex_patch_queue_contract(
            packet_payload["codex_work_packet_queue"],
            training_result.get("codex_patch_queue", []),
        )
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_patch_queue_contract",
                "status": queue["queue_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_patch_queue_contract",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_patch_queue_contract": queue,
            "source_codex_work_packet_queue": packet_payload["codex_work_packet_queue"],
            "source_training_signal_queue": training_result.get("codex_patch_queue", []),
            "hermes_patch_queue_payload": self._codex_patch_queue_hermes_payload(queue),
            "kpi_log": self._codex_patch_queue_kpis(queue),
            "evidence_log": self._codex_patch_queue_evidence(queue),
            "blocked_actions": queue["blocked_actions"],
        }

    def codex_execution_gate(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        patch_payload = self.codex_patch_queue(payload)
        review_store = self._load_review_store()
        execution_review_state = self._codex_execution_review_state(review_store)
        gate = self._codex_execution_gate(patch_payload["codex_patch_queue_contract"])
        gate = self._apply_codex_execution_reviews(gate, execution_review_state)
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_execution_gate",
                "status": gate["gate_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_execution_gate",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_execution_gate": gate,
            "execution_review_state": execution_review_state,
            "source_codex_patch_queue_contract": patch_payload["codex_patch_queue_contract"],
            "hermes_execution_gate_payload": self._codex_execution_gate_hermes_payload(gate),
            "kpi_log": self._codex_execution_gate_kpis(gate),
            "evidence_log": self._codex_execution_gate_evidence(gate),
            "blocked_actions": gate["blocked_actions"],
        }

    def codex_execution_reviews(self) -> dict:
        store = self._load_review_store()
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_execution_gate_review",
                "status": "metadata_review_state",
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_execution_review_state",
                "real_hermes_connected": False,
                "write_actions_blocked": True,
            },
            "execution_review_state": self._codex_execution_review_state(store),
            "blocked_actions": [
                "execute_codex_patch_from_review_store",
                "auto_create_branch_or_commit_from_execution_review",
                "auto_push_or_open_pr_from_execution_review",
                "write_live_hermes_memory",
                "store_raw_training_files",
                "store_credentials_or_tokens",
            ],
        }

    def apply_codex_execution_review(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        candidate_id = self._clean(payload.get("execution_candidate_id") or payload.get("candidate_id"))
        review_status = self._clean(payload.get("review_status"))
        review_note = self._clean(payload.get("review_note"))
        reviewer = self._clean(payload.get("reviewer") or "product_owner")
        source_patch_candidate_id = self._clean(payload.get("source_patch_candidate_id"))
        source_packet_id = self._clean(payload.get("source_packet_id"))
        gate_status = self._clean(payload.get("gate_status"))
        candidate_type = self._clean(payload.get("candidate_type"))
        priority = self._clean(payload.get("priority"))

        allowed = {"approved_for_worktree_preparation", "needs_changes", "deferred", "rejected", "note_only"}
        if not candidate_id:
            raise ValueError("execution_candidate_id is required")
        if review_status not in allowed:
            raise ValueError(f"review_status must be one of {sorted(allowed)}")
        for value in [review_note, source_patch_candidate_id, source_packet_id, gate_status, candidate_type, priority]:
            self._ensure_safe_text(value)

        store = self._load_review_store()
        decision = {
            "execution_candidate_id": candidate_id,
            "review_status": review_status,
            "review_note": review_note,
            "reviewer": reviewer,
            "source_patch_candidate_id": source_patch_candidate_id,
            "source_packet_id": source_packet_id,
            "gate_status": gate_status,
            "candidate_type": candidate_type,
            "priority": priority,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
            "updated_at": self._now(),
        }
        store.setdefault("codex_execution_reviews", {})[candidate_id] = decision
        store["updated_at"] = self._now()
        self._write_review_store(store)
        return {
            "status": "saved",
            "execution_candidate_id": candidate_id,
            "execution_review": decision,
            "execution_review_state": self._codex_execution_review_state(store),
            "review_state": self._review_state(store),
        }

    def codex_worktree_preparation_queue(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        gate_payload = self.codex_execution_gate(payload)
        queue = self._codex_worktree_preparation_queue(gate_payload["codex_execution_gate"])
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_worktree_preparation_queue",
                "status": queue["queue_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_worktree_preparation_queue",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_worktree_preparation_queue": queue,
            "source_codex_execution_gate": gate_payload["codex_execution_gate"],
            "hermes_worktree_preparation_payload": self._codex_worktree_preparation_hermes_payload(queue),
            "kpi_log": self._codex_worktree_preparation_kpis(queue),
            "evidence_log": self._codex_worktree_preparation_evidence(queue),
            "blocked_actions": queue["blocked_actions"],
        }

    def codex_worktree_launch_gate(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        prep_payload = self.codex_worktree_preparation_queue(payload)
        gate = self._codex_worktree_launch_gate(prep_payload["codex_worktree_preparation_queue"])
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_worktree_launch_gate",
                "status": gate["launch_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_worktree_launch_gate",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_worktree_launch_gate": gate,
            "source_codex_worktree_preparation_queue": prep_payload["codex_worktree_preparation_queue"],
            "hermes_worktree_launch_payload": self._codex_worktree_launch_hermes_payload(gate),
            "kpi_log": self._codex_worktree_launch_kpis(gate),
            "evidence_log": self._codex_worktree_launch_evidence(gate),
            "blocked_actions": gate["blocked_actions"],
        }

    def codex_worktree_results(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        launch_payload = self.codex_worktree_launch_gate(payload)
        store = self._load_review_store()
        intake = self._codex_worktree_result_intake(store, launch_payload["codex_worktree_launch_gate"])
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_worktree_result_intake",
                "status": intake["intake_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_worktree_result_intake",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_worktree_result_intake": intake,
            "source_codex_worktree_launch_gate": launch_payload["codex_worktree_launch_gate"],
            "hermes_worktree_result_payload": self._codex_worktree_result_hermes_payload(intake),
            "kpi_log": self._codex_worktree_result_kpis(intake),
            "evidence_log": self._codex_worktree_result_evidence(intake),
            "blocked_actions": intake["blocked_actions"],
        }

    def apply_codex_worktree_result(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        launch_request_id = self._clean(payload.get("launch_request_id"))
        result_status = self._clean(payload.get("result_status"))
        result_summary = self._clean(payload.get("result_summary"))
        reviewer = self._clean(payload.get("reviewer") or "codex")
        source_preparation_task_id = self._clean(payload.get("source_preparation_task_id"))
        source_execution_candidate_id = self._clean(payload.get("source_execution_candidate_id"))
        source_patch_candidate_id = self._clean(payload.get("source_patch_candidate_id"))
        source_packet_id = self._clean(payload.get("source_packet_id"))

        allowed = {"validation_passed", "validation_failed", "blocked", "needs_review", "note_only"}
        if not launch_request_id:
            raise ValueError("launch_request_id is required")
        if result_status not in allowed:
            raise ValueError(f"result_status must be one of {sorted(allowed)}")
        if payload.get("contains_raw_file") or payload.get("contains_credentials"):
            raise ValueError("Codex worktree result intake is metadata-only; do not store raw files or credentials.")

        raw_changed_files = payload.get("changed_files", [])
        raw_blocked_actions = payload.get("blocked_actions", [])
        if not isinstance(raw_changed_files, list):
            raw_changed_files = []
        if not isinstance(raw_blocked_actions, list):
            raw_blocked_actions = []
        changed_files = [self._clean(item) for item in raw_changed_files[:30] if self._clean(item)]
        blocked_actions = [self._clean(item) for item in raw_blocked_actions[:30] if self._clean(item)]
        validation_results = self._normalize_worktree_validation_results(payload.get("validation_results", []))
        for value in [
            launch_request_id,
            result_status,
            result_summary,
            reviewer,
            source_preparation_task_id,
            source_execution_candidate_id,
            source_patch_candidate_id,
            source_packet_id,
            *changed_files,
            *blocked_actions,
        ]:
            self._ensure_safe_text(value)

        validation_contract = self._worktree_result_contract_status(result_status, changed_files, validation_results)
        result_record = {
            "launch_request_id": launch_request_id,
            "result_status": result_status,
            "result_summary": result_summary,
            "reviewer": reviewer,
            "source_preparation_task_id": source_preparation_task_id,
            "source_execution_candidate_id": source_execution_candidate_id,
            "source_patch_candidate_id": source_patch_candidate_id,
            "source_packet_id": source_packet_id,
            "changed_files": changed_files,
            "changed_file_count": len(changed_files),
            "validation_results": validation_results,
            "validation_contract": validation_contract,
            "blocked_actions": blocked_actions,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
            "updated_at": self._now(),
        }
        store = self._load_review_store()
        store.setdefault("codex_worktree_results", {})[launch_request_id] = result_record
        store["updated_at"] = self._now()
        self._write_review_store(store)
        result_state = self._codex_worktree_result_state(store)
        return {
            "status": "saved",
            "launch_request_id": launch_request_id,
            "codex_worktree_result": result_record,
            "codex_worktree_result_state": result_state,
            "review_state": self._review_state(store),
        }

    def codex_worktree_result_reviews(self) -> dict:
        store = self._load_review_store()
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_worktree_result_review_state",
                "status": "metadata_review_state",
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_worktree_result_review_state",
                "real_hermes_connected": False,
                "write_actions_blocked": True,
            },
            "codex_worktree_result_review_state": self._codex_worktree_result_review_state(store),
            "blocked_actions": [
                "auto_promote_worktree_result_to_regression",
                "auto_write_worktree_result_to_hermes",
                "auto_merge_codex_worktree_result",
                "auto_commit_push_or_open_pr_from_result_review",
                "store_raw_patch_or_diff",
                "store_raw_training_files",
                "store_credentials_or_tokens",
            ],
        }

    def apply_codex_worktree_result_review(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        launch_request_id = self._clean(payload.get("launch_request_id"))
        review_status = self._clean(payload.get("review_status"))
        review_note = self._clean(payload.get("review_note"))
        reviewer = self._clean(payload.get("reviewer") or "product_owner")
        result_status = self._clean(payload.get("result_status"))
        changed_file_count = self._safe_int(payload.get("changed_file_count"), 0)
        validation_contract_complete = bool(payload.get("validation_contract_complete"))

        allowed = {
            "approved_for_regression_baseline",
            "approved_for_hermes_memory_candidate",
            "approved_for_regression_and_memory",
            "needs_changes",
            "deferred",
            "rejected",
            "note_only",
        }
        if not launch_request_id:
            raise ValueError("launch_request_id is required")
        if review_status not in allowed:
            raise ValueError(f"review_status must be one of {sorted(allowed)}")
        if payload.get("contains_raw_file") or payload.get("contains_credentials"):
            raise ValueError("Codex worktree result review is metadata-only; do not store raw files or credentials.")
        for value in [launch_request_id, review_status, review_note, reviewer, result_status]:
            self._ensure_safe_text(value)

        decision = {
            "launch_request_id": launch_request_id,
            "review_status": review_status,
            "review_note": review_note,
            "reviewer": reviewer,
            "result_status": result_status,
            "changed_file_count": changed_file_count,
            "validation_contract_complete": validation_contract_complete,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
            "updated_at": self._now(),
        }
        store = self._load_review_store()
        store.setdefault("codex_worktree_result_reviews", {})[launch_request_id] = decision
        store["updated_at"] = self._now()
        self._write_review_store(store)
        return {
            "status": "saved",
            "launch_request_id": launch_request_id,
            "codex_worktree_result_review": decision,
            "codex_worktree_result_review_state": self._codex_worktree_result_review_state(store),
            "review_state": self._review_state(store),
        }

    def codex_worktree_result_review_gate(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        result_payload = self.codex_worktree_results(payload)
        store = self._load_review_store()
        gate = self._codex_worktree_result_review_gate(result_payload["codex_worktree_result_intake"], store)
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_worktree_result_review_gate",
                "status": gate["gate_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_worktree_result_review_gate",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_worktree_result_review_gate": gate,
            "source_codex_worktree_result_intake": result_payload["codex_worktree_result_intake"],
            "hermes_worktree_result_review_payload": self._codex_worktree_result_review_hermes_payload(gate),
            "kpi_log": self._codex_worktree_result_review_kpis(gate),
            "evidence_log": self._codex_worktree_result_review_evidence(gate),
            "blocked_actions": gate["blocked_actions"],
        }

    def codex_promotion_candidates(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        review_gate_payload = self.codex_worktree_result_review_gate(payload)
        queue = self._codex_promotion_candidate_queue(review_gate_payload["codex_worktree_result_review_gate"])
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_candidate_queue",
                "status": queue["queue_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_candidate_queue",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_candidate_queue": queue,
            "source_codex_worktree_result_review_gate": review_gate_payload["codex_worktree_result_review_gate"],
            "hermes_promotion_candidate_payload": self._codex_promotion_candidate_hermes_payload(queue),
            "kpi_log": self._codex_promotion_candidate_kpis(queue),
            "evidence_log": self._codex_promotion_candidate_evidence(queue),
            "blocked_actions": queue["blocked_actions"],
        }

    def codex_promotion_approvals(self) -> dict:
        store = self._load_review_store()
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_approval_state",
                "status": "metadata_review_state",
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_approval_state",
                "real_hermes_connected": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_approval_state": self._codex_promotion_approval_state(store),
            "blocked_actions": [
                "auto_execute_codex_promotion",
                "auto_promote_regression_baseline",
                "auto_write_live_hermes_memory",
                "auto_merge_codex_worktree_result",
                "auto_commit_push_or_open_pr_from_promotion_approval",
                "store_raw_patch_or_diff",
                "store_raw_training_files",
                "store_credentials_or_tokens",
            ],
        }

    def apply_codex_promotion_approval(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        promotion_candidate_id = self._clean(payload.get("promotion_candidate_id"))
        promotion_type = self._clean(payload.get("promotion_type"))
        launch_request_id = self._clean(payload.get("launch_request_id"))
        source_patch_candidate_id = self._clean(payload.get("source_patch_candidate_id"))
        source_packet_id = self._clean(payload.get("source_packet_id"))
        review_status = self._clean(payload.get("review_status"))
        review_note = self._clean(payload.get("review_note"))
        reviewer = self._clean(payload.get("reviewer") or "product_owner")
        changed_file_count = self._safe_int(payload.get("changed_file_count"), 0)

        allowed = {
            "approved_for_future_promotion",
            "hold_for_later",
            "skipped_for_now",
            "needs_changes",
            "rejected",
            "note_only",
        }
        allowed_types = {"regression_baseline_candidate", "hermes_memory_candidate"}
        if not promotion_candidate_id:
            raise ValueError("promotion_candidate_id is required")
        if promotion_type not in allowed_types:
            raise ValueError(f"promotion_type must be one of {sorted(allowed_types)}")
        if review_status not in allowed:
            raise ValueError(f"review_status must be one of {sorted(allowed)}")
        if payload.get("contains_raw_file") or payload.get("contains_credentials"):
            raise ValueError("Codex promotion approval is metadata-only; do not store raw files or credentials.")
        for value in [
            promotion_candidate_id,
            promotion_type,
            launch_request_id,
            source_patch_candidate_id,
            source_packet_id,
            review_status,
            review_note,
            reviewer,
        ]:
            self._ensure_safe_text(value)

        future_action = {
            "regression_baseline_candidate": "manual_regression_baseline_promotion",
            "hermes_memory_candidate": "manual_hermes_memory_write",
        }[promotion_type]
        decision = {
            "promotion_candidate_id": promotion_candidate_id,
            "promotion_type": promotion_type,
            "launch_request_id": launch_request_id,
            "source_patch_candidate_id": source_patch_candidate_id,
            "source_packet_id": source_packet_id,
            "review_status": review_status,
            "review_note": review_note,
            "reviewer": reviewer,
            "future_action": future_action,
            "changed_file_count": changed_file_count,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
            "updated_at": self._now(),
        }
        store = self._load_review_store()
        store.setdefault("codex_promotion_approvals", {})[promotion_candidate_id] = decision
        store["updated_at"] = self._now()
        self._write_review_store(store)
        return {
            "status": "saved",
            "promotion_candidate_id": promotion_candidate_id,
            "codex_promotion_approval": decision,
            "codex_promotion_approval_state": self._codex_promotion_approval_state(store),
            "review_state": self._review_state(store),
        }

    def codex_promotion_approval_gate(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        candidate_payload = self.codex_promotion_candidates(payload)
        store = self._load_review_store()
        gate = self._codex_promotion_approval_gate(
            candidate_payload["codex_promotion_candidate_queue"],
            store,
        )
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_approval_gate",
                "status": gate["gate_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_approval_gate",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_approval_gate": gate,
            "source_codex_promotion_candidate_queue": candidate_payload["codex_promotion_candidate_queue"],
            "hermes_promotion_approval_payload": self._codex_promotion_approval_hermes_payload(gate),
            "kpi_log": self._codex_promotion_approval_kpis(gate),
            "evidence_log": self._codex_promotion_approval_evidence(gate),
            "blocked_actions": gate["blocked_actions"],
        }

    def codex_promotion_handoff(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        approval_payload = self.codex_promotion_approval_gate(payload)
        queue = self._codex_promotion_handoff_queue(approval_payload["codex_promotion_approval_gate"])
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_handoff_queue",
                "status": queue["handoff_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_handoff_queue",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_handoff_queue": queue,
            "source_codex_promotion_approval_gate": approval_payload["codex_promotion_approval_gate"],
            "hermes_promotion_handoff_payload": self._codex_promotion_handoff_hermes_payload(queue),
            "kpi_log": self._codex_promotion_handoff_kpis(queue),
            "evidence_log": self._codex_promotion_handoff_evidence(queue),
            "blocked_actions": queue["blocked_actions"],
        }

    def codex_promotion_execution_readiness(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        handoff_payload = self.codex_promotion_handoff(payload)
        store = self._load_review_store()
        gate = self._codex_promotion_execution_readiness_gate(handoff_payload["codex_promotion_handoff_queue"], store)
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_execution_readiness_gate",
                "status": gate["readiness_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_execution_readiness_gate",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_execution_readiness_gate": gate,
            "source_codex_promotion_handoff_queue": handoff_payload["codex_promotion_handoff_queue"],
            "hermes_promotion_execution_readiness_payload": self._codex_promotion_execution_readiness_hermes_payload(gate),
            "kpi_log": self._codex_promotion_execution_readiness_kpis(gate),
            "evidence_log": self._codex_promotion_execution_readiness_evidence(gate),
            "codex_promotion_readiness_review_state": self._codex_promotion_readiness_review_state(store),
            "blocked_actions": gate["blocked_actions"],
        }

    def codex_promotion_readiness_reviews(self) -> dict:
        store = self._load_review_store()
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_readiness_review_state",
                "status": "metadata_review_state",
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_readiness_review_state",
                "real_hermes_connected": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_readiness_review_state": self._codex_promotion_readiness_review_state(store),
            "blocked_actions": [
                "auto_execute_promotion_readiness_review",
                "auto_promote_regression_baseline",
                "auto_write_live_hermes_memory",
                "auto_commit_push_or_open_pr_from_readiness_review",
                "store_raw_patch_or_diff",
                "store_raw_training_files",
                "store_credentials_or_tokens",
            ],
        }

    def apply_codex_promotion_readiness_review(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        readiness_item_id = self._clean(payload.get("readiness_item_id"))
        source_handoff_id = self._clean(payload.get("source_handoff_id"))
        promotion_candidate_id = self._clean(payload.get("promotion_candidate_id"))
        promotion_type = self._clean(payload.get("promotion_type"))
        review_status = self._clean(payload.get("review_status"))
        review_note = self._clean(payload.get("review_note"))
        reviewer = self._clean(payload.get("reviewer") or "product_owner")
        validation_summary = self._clean(payload.get("validation_summary"))
        rollback_summary = self._clean(payload.get("rollback_summary"))
        execution_evidence_plan = self._clean(payload.get("execution_evidence_plan"))
        confirmed_inputs = payload.get("confirmed_inputs") or []
        if isinstance(confirmed_inputs, str):
            confirmed_inputs = [item.strip() for item in confirmed_inputs.split("|") if item.strip()]
        confirmed_inputs = [self._clean(item) for item in confirmed_inputs]

        allowed = {"confirmed_ready_for_manual_execution", "needs_execution_inputs", "deferred", "rejected", "note_only"}
        allowed_types = {"regression_baseline_candidate", "hermes_memory_candidate"}
        if not readiness_item_id:
            raise ValueError("readiness_item_id is required")
        if promotion_type and promotion_type not in allowed_types:
            raise ValueError(f"promotion_type must be one of {sorted(allowed_types)}")
        if review_status not in allowed:
            raise ValueError(f"review_status must be one of {sorted(allowed)}")
        if payload.get("contains_raw_file") or payload.get("contains_credentials"):
            raise ValueError("Codex promotion readiness review is metadata-only; do not store raw files or credentials.")
        for value in [
            readiness_item_id,
            source_handoff_id,
            promotion_candidate_id,
            promotion_type,
            review_status,
            review_note,
            reviewer,
            validation_summary,
            rollback_summary,
            execution_evidence_plan,
            *confirmed_inputs,
        ]:
            self._ensure_safe_text(value)

        decision = {
            "readiness_item_id": readiness_item_id,
            "source_handoff_id": source_handoff_id,
            "promotion_candidate_id": promotion_candidate_id,
            "promotion_type": promotion_type,
            "review_status": review_status,
            "review_note": review_note,
            "reviewer": reviewer,
            "confirmed_inputs": confirmed_inputs,
            "validation_summary": validation_summary,
            "rollback_summary": rollback_summary,
            "execution_evidence_plan": execution_evidence_plan,
            "manual_execution_confirmation_only": True,
            "automatic_execution_allowed": False,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
            "updated_at": self._now(),
        }
        store = self._load_review_store()
        store.setdefault("codex_promotion_readiness_reviews", {})[readiness_item_id] = decision
        store["updated_at"] = self._now()
        self._write_review_store(store)
        return {
            "status": "saved",
            "readiness_item_id": readiness_item_id,
            "codex_promotion_readiness_review": decision,
            "codex_promotion_readiness_review_state": self._codex_promotion_readiness_review_state(store),
            "review_state": self._review_state(store),
        }

    def codex_promotion_execution_results(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        readiness_payload = self.codex_promotion_execution_readiness(payload)
        store = self._load_review_store()
        intake = self._codex_promotion_execution_result_intake(
            store,
            readiness_payload["codex_promotion_execution_readiness_gate"],
        )
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_execution_result_intake",
                "status": intake["intake_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_execution_result_intake",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_execution_result_intake": intake,
            "source_codex_promotion_execution_readiness_gate": readiness_payload["codex_promotion_execution_readiness_gate"],
            "hermes_promotion_execution_result_payload": self._codex_promotion_execution_result_hermes_payload(intake),
            "kpi_log": self._codex_promotion_execution_result_kpis(intake),
            "evidence_log": self._codex_promotion_execution_result_evidence(intake),
            "blocked_actions": intake["blocked_actions"],
        }

    def codex_promotion_closure_audit(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        result_payload = self.codex_promotion_execution_results(payload)
        audit = self._codex_promotion_closure_audit(
            result_payload["codex_promotion_execution_result_intake"],
            result_payload["source_codex_promotion_execution_readiness_gate"],
        )
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_closure_audit",
                "status": audit["closure_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_closure_audit",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_closure_audit": audit,
            "source_codex_promotion_execution_result_intake": result_payload["codex_promotion_execution_result_intake"],
            "source_codex_promotion_execution_readiness_gate": result_payload["source_codex_promotion_execution_readiness_gate"],
            "hermes_promotion_closure_audit_payload": self._codex_promotion_closure_audit_hermes_payload(audit),
            "kpi_log": self._codex_promotion_closure_audit_kpis(audit),
            "evidence_log": self._codex_promotion_closure_audit_evidence(audit),
            "blocked_actions": audit["blocked_actions"],
        }

    def codex_promotion_sync_review_gate(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        closure_payload = self.codex_promotion_closure_audit(payload)
        store = self._load_review_store()
        gate = self._codex_promotion_sync_review_gate(
            closure_payload["codex_promotion_closure_audit"],
            store,
        )
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_sync_review_gate",
                "status": gate["gate_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_sync_review_gate",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_sync_review_gate": gate,
            "source_codex_promotion_closure_audit": closure_payload["codex_promotion_closure_audit"],
            "hermes_promotion_sync_review_payload": self._codex_promotion_sync_review_hermes_payload(gate),
            "kpi_log": self._codex_promotion_sync_review_kpis(gate),
            "evidence_log": self._codex_promotion_sync_review_evidence(gate),
            "blocked_actions": gate["blocked_actions"],
        }

    def codex_promotion_sync_reviews(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        store = self._load_review_store()
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_sync_review_state",
                "status": "metadata_only",
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_sync_review_state",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_sync_review_state": self._codex_promotion_sync_review_state(store),
        }

    def codex_promotion_sync_handoff(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        sync_gate_payload = self.codex_promotion_sync_review_gate(payload)
        queue = self._codex_promotion_sync_handoff_queue(
            sync_gate_payload["codex_promotion_sync_review_gate"],
        )
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_sync_handoff_queue",
                "status": queue["handoff_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_sync_handoff_queue",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_sync_handoff_queue": queue,
            "source_codex_promotion_sync_review_gate": sync_gate_payload["codex_promotion_sync_review_gate"],
            "hermes_promotion_sync_handoff_payload": self._codex_promotion_sync_handoff_hermes_payload(queue),
            "kpi_log": self._codex_promotion_sync_handoff_kpis(queue),
            "evidence_log": self._codex_promotion_sync_handoff_evidence(queue),
            "blocked_actions": queue["blocked_actions"],
        }

    def codex_promotion_sync_execution_readiness(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        handoff_payload = self.codex_promotion_sync_handoff(payload)
        store = self._load_review_store()
        gate = self._codex_promotion_sync_execution_readiness_gate(
            handoff_payload["codex_promotion_sync_handoff_queue"],
            store,
            payload,
        )
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_sync_execution_readiness_gate",
                "status": gate["readiness_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_sync_execution_readiness_gate",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_sync_execution_readiness_gate": gate,
            "source_codex_promotion_sync_handoff_queue": handoff_payload["codex_promotion_sync_handoff_queue"],
            "hermes_promotion_sync_execution_readiness_payload": self._codex_promotion_sync_execution_readiness_hermes_payload(gate),
            "kpi_log": self._codex_promotion_sync_execution_readiness_kpis(gate),
            "evidence_log": self._codex_promotion_sync_execution_readiness_evidence(gate),
            "codex_promotion_sync_readiness_review_state": self._codex_promotion_sync_readiness_review_state(store),
            "blocked_actions": gate["blocked_actions"],
        }

    def codex_promotion_sync_readiness_reviews(self) -> dict:
        store = self._load_review_store()
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_sync_readiness_review_state",
                "status": "metadata_review_state",
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_sync_readiness_review_state",
                "real_hermes_connected": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_sync_readiness_review_state": self._codex_promotion_sync_readiness_review_state(store),
            "blocked_actions": [
                "auto_execute_sync_readiness_review",
                "auto_update_regression_baseline_from_sync_readiness_review",
                "auto_write_live_hermes_memory_from_sync_readiness_review",
                "auto_commit_push_or_open_pr_from_sync_readiness_review",
                "store_raw_patch_or_diff",
                "store_raw_training_files",
                "store_credentials_or_tokens",
            ],
        }

    def codex_promotion_sync_execution_results(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        readiness_payload = self.codex_promotion_sync_execution_readiness(payload)
        store = self._load_review_store()
        intake = self._codex_promotion_sync_execution_result_intake(
            store,
            readiness_payload["codex_promotion_sync_execution_readiness_gate"],
        )
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_sync_execution_result_intake",
                "status": intake["intake_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_sync_execution_result_intake",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_sync_execution_result_intake": intake,
            "source_codex_promotion_sync_execution_readiness_gate": readiness_payload["codex_promotion_sync_execution_readiness_gate"],
            "hermes_promotion_sync_execution_result_payload": self._codex_promotion_sync_execution_result_hermes_payload(intake),
            "kpi_log": self._codex_promotion_sync_execution_result_kpis(intake),
            "evidence_log": self._codex_promotion_sync_execution_result_evidence(intake),
            "blocked_actions": intake["blocked_actions"],
        }

    def codex_promotion_sync_closure_audit(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        result_payload = self.codex_promotion_sync_execution_results(payload)
        audit = self._codex_promotion_sync_closure_audit(
            result_payload["codex_promotion_sync_execution_result_intake"],
            result_payload["source_codex_promotion_sync_execution_readiness_gate"],
        )
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_sync_closure_audit",
                "status": audit["closure_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_sync_closure_audit",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_sync_closure_audit": audit,
            "source_codex_promotion_sync_execution_result_intake": result_payload["codex_promotion_sync_execution_result_intake"],
            "source_codex_promotion_sync_execution_readiness_gate": result_payload["source_codex_promotion_sync_execution_readiness_gate"],
            "hermes_promotion_sync_closure_audit_payload": self._codex_promotion_sync_closure_audit_hermes_payload(audit),
            "kpi_log": self._codex_promotion_sync_closure_audit_kpis(audit),
            "evidence_log": self._codex_promotion_sync_closure_audit_evidence(audit),
            "blocked_actions": audit["blocked_actions"],
        }

    def codex_promotion_sync_closure_review_gate(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        audit_payload = self.codex_promotion_sync_closure_audit(payload)
        store = self._load_review_store()
        gate = self._codex_promotion_sync_closure_review_gate(
            audit_payload["codex_promotion_sync_closure_audit"],
            store,
        )
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_sync_closure_review_gate",
                "status": gate["gate_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_sync_closure_review_gate",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_sync_closure_review_gate": gate,
            "source_codex_promotion_sync_closure_audit": audit_payload["codex_promotion_sync_closure_audit"],
            "hermes_promotion_sync_closure_review_payload": self._codex_promotion_sync_closure_review_hermes_payload(gate),
            "kpi_log": self._codex_promotion_sync_closure_review_kpis(gate),
            "evidence_log": self._codex_promotion_sync_closure_review_evidence(gate),
            "blocked_actions": gate["blocked_actions"],
        }

    def codex_promotion_sync_closure_reviews(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        store = self._load_review_store()
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_sync_closure_review_state",
                "status": "metadata_review_state",
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_sync_closure_review_state",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_sync_closure_review_state": self._codex_promotion_sync_closure_review_state(store),
            "blocked_actions": [
                "auto_execute_final_sync_closure_review",
                "auto_update_regression_baseline_from_sync_closure_review",
                "auto_write_live_hermes_memory_from_sync_closure_review",
                "auto_commit_push_or_open_pr_from_sync_closure_review",
                "store_raw_patch_or_diff",
                "store_raw_training_files",
                "store_credentials_or_tokens",
            ],
        }

    def codex_promotion_final_sync_handoff(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        review_gate_payload = self.codex_promotion_sync_closure_review_gate(payload)
        queue = self._codex_promotion_final_sync_handoff_queue(
            review_gate_payload["codex_promotion_sync_closure_review_gate"],
        )
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_final_sync_handoff_queue",
                "status": queue["handoff_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_final_sync_handoff_queue",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_final_sync_handoff_queue": queue,
            "source_codex_promotion_sync_closure_review_gate": review_gate_payload["codex_promotion_sync_closure_review_gate"],
            "hermes_promotion_final_sync_handoff_payload": self._codex_promotion_final_sync_handoff_hermes_payload(queue),
            "kpi_log": self._codex_promotion_final_sync_handoff_kpis(queue),
            "evidence_log": self._codex_promotion_final_sync_handoff_evidence(queue),
            "blocked_actions": queue["blocked_actions"],
        }

    def codex_promotion_final_sync_execution_readiness(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        handoff_payload = self.codex_promotion_final_sync_handoff(payload)
        gate = self._codex_promotion_final_sync_execution_readiness_gate(
            handoff_payload["codex_promotion_final_sync_handoff_queue"],
            payload,
        )
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_final_sync_execution_readiness_gate",
                "status": gate["readiness_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_final_sync_execution_readiness_gate",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_final_sync_execution_readiness_gate": gate,
            "source_codex_promotion_final_sync_handoff_queue": handoff_payload["codex_promotion_final_sync_handoff_queue"],
            "hermes_promotion_final_sync_execution_readiness_payload": self._codex_promotion_final_sync_execution_readiness_hermes_payload(gate),
            "kpi_log": self._codex_promotion_final_sync_execution_readiness_kpis(gate),
            "evidence_log": self._codex_promotion_final_sync_execution_readiness_evidence(gate),
            "blocked_actions": gate["blocked_actions"],
        }

    def codex_promotion_final_sync_execution_results(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        readiness_payload = self.codex_promotion_final_sync_execution_readiness(payload)
        store = self._load_review_store()
        intake = self._codex_promotion_final_sync_execution_result_intake(
            store,
            readiness_payload["codex_promotion_final_sync_execution_readiness_gate"],
        )
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_final_sync_execution_result_intake",
                "status": intake["intake_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_final_sync_execution_result_intake",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_final_sync_execution_result_intake": intake,
            "source_codex_promotion_final_sync_execution_readiness_gate": readiness_payload["codex_promotion_final_sync_execution_readiness_gate"],
            "hermes_promotion_final_sync_execution_result_payload": self._codex_promotion_final_sync_execution_result_hermes_payload(intake),
            "kpi_log": self._codex_promotion_final_sync_execution_result_kpis(intake),
            "evidence_log": self._codex_promotion_final_sync_execution_result_evidence(intake),
            "blocked_actions": intake["blocked_actions"],
        }

    def codex_promotion_final_sync_closure_audit(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        result_payload = self.codex_promotion_final_sync_execution_results(payload)
        audit = self._codex_promotion_final_sync_closure_audit(
            result_payload["codex_promotion_final_sync_execution_result_intake"],
            result_payload["source_codex_promotion_final_sync_execution_readiness_gate"],
        )
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_final_sync_closure_audit",
                "status": audit["closure_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_final_sync_closure_audit",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_final_sync_closure_audit": audit,
            "source_codex_promotion_final_sync_execution_result_intake": result_payload["codex_promotion_final_sync_execution_result_intake"],
            "source_codex_promotion_final_sync_execution_readiness_gate": result_payload["source_codex_promotion_final_sync_execution_readiness_gate"],
            "hermes_promotion_final_sync_closure_audit_payload": self._codex_promotion_final_sync_closure_audit_hermes_payload(audit),
            "kpi_log": self._codex_promotion_final_sync_closure_audit_kpis(audit),
            "evidence_log": self._codex_promotion_final_sync_closure_audit_evidence(audit),
            "blocked_actions": audit["blocked_actions"],
        }

    def codex_promotion_final_completion_review_gate(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        audit_payload = self.codex_promotion_final_sync_closure_audit(payload)
        store = self._load_review_store()
        gate = self._codex_promotion_final_completion_review_gate(
            audit_payload["codex_promotion_final_sync_closure_audit"],
            store,
        )
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_final_completion_review_gate",
                "status": gate["gate_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_final_completion_review_gate",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_final_completion_review_gate": gate,
            "source_codex_promotion_final_sync_closure_audit": audit_payload["codex_promotion_final_sync_closure_audit"],
            "hermes_promotion_final_completion_review_payload": self._codex_promotion_final_completion_review_hermes_payload(gate),
            "kpi_log": self._codex_promotion_final_completion_review_kpis(gate),
            "evidence_log": self._codex_promotion_final_completion_review_evidence(gate),
            "blocked_actions": gate["blocked_actions"],
        }

    def codex_promotion_final_completion_reviews(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        store = self._load_review_store()
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_final_completion_review_state",
                "status": "metadata_review_state",
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_final_completion_review_state",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_final_completion_review_state": self._codex_promotion_final_completion_review_state(store),
            "blocked_actions": [
                "auto_execute_final_completion_review",
                "auto_update_regression_baseline_from_final_completion_review",
                "auto_write_live_hermes_memory_from_final_completion_review",
                "auto_publish_project_memory_from_final_completion_review",
                "auto_commit_push_or_open_pr_from_final_completion_review",
                "store_raw_patch_or_diff",
                "store_raw_training_files",
                "store_credentials_or_tokens",
            ],
        }

    def codex_promotion_final_publication_handoff(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        review_gate_payload = self.codex_promotion_final_completion_review_gate(payload)
        queue = self._codex_promotion_final_publication_handoff_queue(
            review_gate_payload["codex_promotion_final_completion_review_gate"],
        )
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_final_publication_handoff_queue",
                "status": queue["handoff_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_final_publication_handoff_queue",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_final_publication_handoff_queue": queue,
            "source_codex_promotion_final_completion_review_gate": review_gate_payload["codex_promotion_final_completion_review_gate"],
            "hermes_promotion_final_publication_handoff_payload": self._codex_promotion_final_publication_handoff_hermes_payload(queue),
            "kpi_log": self._codex_promotion_final_publication_handoff_kpis(queue),
            "evidence_log": self._codex_promotion_final_publication_handoff_evidence(queue),
            "blocked_actions": queue["blocked_actions"],
        }

    def codex_promotion_final_publication_readiness(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        handoff_payload = self.codex_promotion_final_publication_handoff(payload)
        gate = self._codex_promotion_final_publication_readiness_gate(
            handoff_payload["codex_promotion_final_publication_handoff_queue"],
            payload,
        )
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_final_publication_readiness_gate",
                "status": gate["readiness_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_final_publication_readiness_gate",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_final_publication_readiness_gate": gate,
            "source_codex_promotion_final_publication_handoff_queue": handoff_payload["codex_promotion_final_publication_handoff_queue"],
            "hermes_promotion_final_publication_readiness_payload": self._codex_promotion_final_publication_readiness_hermes_payload(gate),
            "kpi_log": self._codex_promotion_final_publication_readiness_kpis(gate),
            "evidence_log": self._codex_promotion_final_publication_readiness_evidence(gate),
            "blocked_actions": gate["blocked_actions"],
        }

    def codex_promotion_final_publication_results(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        readiness_payload = self.codex_promotion_final_publication_readiness(payload)
        store = self._load_review_store()
        intake = self._codex_promotion_final_publication_result_intake(
            store,
            readiness_payload["codex_promotion_final_publication_readiness_gate"],
        )
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_final_publication_result_intake",
                "status": intake["intake_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_final_publication_result_intake",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_final_publication_result_intake": intake,
            "source_codex_promotion_final_publication_readiness_gate": readiness_payload["codex_promotion_final_publication_readiness_gate"],
            "hermes_promotion_final_publication_result_payload": self._codex_promotion_final_publication_result_hermes_payload(intake),
            "kpi_log": self._codex_promotion_final_publication_result_kpis(intake),
            "evidence_log": self._codex_promotion_final_publication_result_evidence(intake),
            "blocked_actions": intake["blocked_actions"],
        }

    def codex_promotion_final_publication_closure_audit(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        result_payload = self.codex_promotion_final_publication_results(payload)
        audit = self._codex_promotion_final_publication_closure_audit(
            result_payload["codex_promotion_final_publication_result_intake"],
            result_payload["source_codex_promotion_final_publication_readiness_gate"],
        )
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_final_publication_closure_audit",
                "status": audit["closure_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_final_publication_closure_audit",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_final_publication_closure_audit": audit,
            "source_codex_promotion_final_publication_result_intake": result_payload["codex_promotion_final_publication_result_intake"],
            "source_codex_promotion_final_publication_readiness_gate": result_payload["source_codex_promotion_final_publication_readiness_gate"],
            "hermes_promotion_final_publication_closure_audit_payload": self._codex_promotion_final_publication_closure_audit_hermes_payload(audit),
            "kpi_log": self._codex_promotion_final_publication_closure_audit_kpis(audit),
            "evidence_log": self._codex_promotion_final_publication_closure_audit_evidence(audit),
            "blocked_actions": audit["blocked_actions"],
        }

    def codex_promotion_final_release_review_gate(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        closure_payload = self.codex_promotion_final_publication_closure_audit(payload)
        gate = self._codex_promotion_final_release_review_gate(
            closure_payload["codex_promotion_final_publication_closure_audit"],
        )
        return {
            "workflow_template": self.template(),
            "workflow_instance": {
                "template_id": TRAINING_TEMPLATE_ID,
                "version": TRAINING_VERSION,
                "scenario": "codex_promotion_final_release_review_gate",
                "status": gate["gate_status"],
                "adapter_status": "mock_contract",
                "automation_mode": "local_codex_promotion_final_release_review_gate",
                "real_hermes_connected": False,
                "model_weight_finetuning": False,
                "write_actions_blocked": True,
            },
            "codex_promotion_final_release_review_gate": gate,
            "source_codex_promotion_final_publication_closure_audit": closure_payload["codex_promotion_final_publication_closure_audit"],
            "hermes_promotion_final_release_review_payload": self._codex_promotion_final_release_review_hermes_payload(gate),
            "kpi_log": self._codex_promotion_final_release_review_kpis(gate),
            "evidence_log": self._codex_promotion_final_release_review_evidence(gate),
            "blocked_actions": gate["blocked_actions"],
        }

    def apply_codex_promotion_final_completion_review(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        final_sync_completion_id = self._clean(payload.get("final_sync_completion_id"))
        readiness_item_id = self._clean(payload.get("readiness_item_id"))
        final_closure_id = self._clean(payload.get("final_closure_id"))
        source_action_id = self._clean(payload.get("source_action_id"))
        source_sync_audit_id = self._clean(payload.get("source_sync_audit_id"))
        promotion_candidate_id = self._clean(payload.get("promotion_candidate_id"))
        promotion_type = self._clean(payload.get("promotion_type"))
        target_system = self._clean(payload.get("target_system"))
        review_status = self._clean(payload.get("review_status"))
        review_note = self._clean(payload.get("review_note"))
        reviewer = self._clean(payload.get("reviewer") or "product_owner")
        validation_summary = self._clean(payload.get("validation_summary"))
        rollback_summary = self._clean(payload.get("rollback_summary"))
        raw_completion_checks = payload.get("confirmed_completion_checks") or []
        if isinstance(raw_completion_checks, str):
            raw_completion_checks = [item.strip() for item in raw_completion_checks.split("|") if item.strip()]
        if not isinstance(raw_completion_checks, list):
            raw_completion_checks = []
        confirmed_completion_checks = [self._clean(item) for item in raw_completion_checks[:30] if self._clean(item)]

        allowed_statuses = {"approved_final_completion", "needs_completion_inputs", "deferred", "rejected", "note_only"}
        allowed_types = {"regression_baseline_candidate", "hermes_memory_candidate"}
        allowed_targets = {"", "local_regression_baseline_store", "live_hermes_memory"}
        if not final_sync_completion_id:
            raise ValueError("final_sync_completion_id is required")
        if promotion_type and promotion_type not in allowed_types:
            raise ValueError(f"promotion_type must be one of {sorted(allowed_types)}")
        if target_system not in allowed_targets:
            raise ValueError(f"target_system must be one of {sorted(allowed_targets)}")
        if review_status not in allowed_statuses:
            raise ValueError(f"review_status must be one of {sorted(allowed_statuses)}")
        if payload.get("contains_raw_file") or payload.get("contains_credentials"):
            raise ValueError("Codex promotion final completion review is metadata-only; do not store raw files or credentials.")
        for value in [
            final_sync_completion_id,
            readiness_item_id,
            final_closure_id,
            source_action_id,
            source_sync_audit_id,
            promotion_candidate_id,
            promotion_type,
            target_system,
            review_status,
            review_note,
            reviewer,
            validation_summary,
            rollback_summary,
            *confirmed_completion_checks,
        ]:
            self._ensure_safe_text(value)

        decision = {
            "final_sync_completion_id": final_sync_completion_id,
            "readiness_item_id": readiness_item_id,
            "final_closure_id": final_closure_id,
            "source_action_id": source_action_id,
            "source_sync_audit_id": source_sync_audit_id,
            "promotion_candidate_id": promotion_candidate_id,
            "promotion_type": promotion_type,
            "target_system": target_system,
            "review_status": review_status,
            "review_note": review_note,
            "reviewer": reviewer,
            "confirmed_completion_checks": confirmed_completion_checks,
            "validation_summary": validation_summary,
            "rollback_summary": rollback_summary,
            "metadata_only": True,
            "manual_final_completion_review_only": True,
            "automatic_completion_allowed": False,
            "automatic_project_memory_write_allowed": False,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
            "updated_at": self._now(),
        }
        store = self._load_review_store()
        store.setdefault("codex_promotion_final_completion_reviews", {})[final_sync_completion_id] = decision
        store["updated_at"] = self._now()
        self._write_review_store(store)
        return {
            "status": "saved",
            "final_sync_completion_id": final_sync_completion_id,
            "codex_promotion_final_completion_review": decision,
            "codex_promotion_final_completion_review_state": self._codex_promotion_final_completion_review_state(store),
            "review_state": self._review_state(store),
        }

    def apply_codex_promotion_sync_closure_review(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        final_closure_id = self._clean(payload.get("final_closure_id"))
        readiness_item_id = self._clean(payload.get("readiness_item_id"))
        source_sync_audit_id = self._clean(payload.get("source_sync_audit_id"))
        promotion_candidate_id = self._clean(payload.get("promotion_candidate_id"))
        promotion_type = self._clean(payload.get("promotion_type"))
        target_system = self._clean(payload.get("target_system"))
        review_status = self._clean(payload.get("review_status"))
        review_note = self._clean(payload.get("review_note"))
        reviewer = self._clean(payload.get("reviewer") or "product_owner")
        validation_summary = self._clean(payload.get("validation_summary"))
        rollback_summary = self._clean(payload.get("rollback_summary"))
        raw_final_checks = payload.get("confirmed_final_checks") or []
        if isinstance(raw_final_checks, str):
            raw_final_checks = [item.strip() for item in raw_final_checks.split("|") if item.strip()]
        if not isinstance(raw_final_checks, list):
            raw_final_checks = []
        confirmed_final_checks = [self._clean(item) for item in raw_final_checks[:30] if self._clean(item)]

        allowed_statuses = {"approved_for_final_sync", "needs_final_sync_inputs", "deferred", "rejected", "note_only"}
        allowed_targets = {"", "local_regression_baseline_store", "live_hermes_memory"}
        if not final_closure_id:
            raise ValueError("final_closure_id is required")
        if target_system not in allowed_targets:
            raise ValueError(f"target_system must be one of {sorted(allowed_targets)}")
        if review_status not in allowed_statuses:
            raise ValueError(f"review_status must be one of {sorted(allowed_statuses)}")
        if payload.get("contains_raw_file") or payload.get("contains_credentials"):
            raise ValueError("Codex promotion sync closure review is metadata-only; do not store raw files or credentials.")
        for value in [
            final_closure_id,
            readiness_item_id,
            source_sync_audit_id,
            promotion_candidate_id,
            promotion_type,
            target_system,
            review_status,
            review_note,
            reviewer,
            validation_summary,
            rollback_summary,
            *confirmed_final_checks,
        ]:
            self._ensure_safe_text(value)

        decision = {
            "final_closure_id": final_closure_id,
            "readiness_item_id": readiness_item_id,
            "source_sync_audit_id": source_sync_audit_id,
            "promotion_candidate_id": promotion_candidate_id,
            "promotion_type": promotion_type,
            "target_system": target_system,
            "review_status": review_status,
            "review_note": review_note,
            "reviewer": reviewer,
            "confirmed_final_checks": confirmed_final_checks,
            "validation_summary": validation_summary,
            "rollback_summary": rollback_summary,
            "manual_final_sync_review_only": True,
            "automatic_final_sync_allowed": False,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
            "updated_at": self._now(),
        }
        store = self._load_review_store()
        store.setdefault("codex_promotion_sync_closure_reviews", {})[final_closure_id] = decision
        store["updated_at"] = self._now()
        self._write_review_store(store)
        return {
            "status": "saved",
            "final_closure_id": final_closure_id,
            "codex_promotion_sync_closure_review": decision,
            "codex_promotion_sync_closure_review_state": self._codex_promotion_sync_closure_review_state(store),
            "review_state": self._review_state(store),
        }

    def apply_codex_promotion_sync_readiness_review(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        readiness_item_id = self._clean(payload.get("readiness_item_id"))
        source_sync_handoff_item_id = self._clean(payload.get("source_sync_handoff_item_id"))
        source_sync_audit_id = self._clean(payload.get("source_sync_audit_id"))
        promotion_candidate_id = self._clean(payload.get("promotion_candidate_id"))
        promotion_type = self._clean(payload.get("promotion_type"))
        target_system = self._clean(payload.get("target_system"))
        review_status = self._clean(payload.get("review_status"))
        review_note = self._clean(payload.get("review_note"))
        reviewer = self._clean(payload.get("reviewer") or "product_owner")
        validation_summary = self._clean(payload.get("validation_summary"))
        rollback_summary = self._clean(payload.get("rollback_summary"))
        execution_evidence_plan = self._clean(payload.get("execution_evidence_plan"))
        confirmed_inputs = payload.get("confirmed_inputs") or []
        if isinstance(confirmed_inputs, str):
            confirmed_inputs = [item.strip() for item in confirmed_inputs.split("|") if item.strip()]
        confirmed_inputs = [self._clean(item) for item in confirmed_inputs]

        allowed_statuses = {"confirmed_ready_for_manual_sync_execution", "needs_sync_execution_inputs", "deferred", "rejected", "note_only"}
        allowed_targets = {"", "local_regression_baseline_store", "live_hermes_memory"}
        if not readiness_item_id:
            raise ValueError("readiness_item_id is required")
        if target_system not in allowed_targets:
            raise ValueError(f"target_system must be one of {sorted(allowed_targets)}")
        if review_status not in allowed_statuses:
            raise ValueError(f"review_status must be one of {sorted(allowed_statuses)}")
        if payload.get("contains_raw_file") or payload.get("contains_credentials"):
            raise ValueError("Codex promotion sync readiness review is metadata-only; do not store raw files or credentials.")
        for value in [
            readiness_item_id,
            source_sync_handoff_item_id,
            source_sync_audit_id,
            promotion_candidate_id,
            promotion_type,
            target_system,
            review_status,
            review_note,
            reviewer,
            validation_summary,
            rollback_summary,
            execution_evidence_plan,
            *confirmed_inputs,
        ]:
            self._ensure_safe_text(value)

        decision = {
            "readiness_item_id": readiness_item_id,
            "source_sync_handoff_item_id": source_sync_handoff_item_id,
            "source_sync_audit_id": source_sync_audit_id,
            "promotion_candidate_id": promotion_candidate_id,
            "promotion_type": promotion_type,
            "target_system": target_system,
            "review_status": review_status,
            "review_note": review_note,
            "reviewer": reviewer,
            "confirmed_inputs": confirmed_inputs,
            "validation_summary": validation_summary,
            "rollback_summary": rollback_summary,
            "execution_evidence_plan": execution_evidence_plan,
            "manual_sync_execution_confirmation_only": True,
            "automatic_sync_execution_allowed": False,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
            "updated_at": self._now(),
        }
        store = self._load_review_store()
        store.setdefault("codex_promotion_sync_readiness_reviews", {})[readiness_item_id] = decision
        store["updated_at"] = self._now()
        self._write_review_store(store)
        return {
            "status": "saved",
            "readiness_item_id": readiness_item_id,
            "codex_promotion_sync_readiness_review": decision,
            "codex_promotion_sync_readiness_review_state": self._codex_promotion_sync_readiness_review_state(store),
            "review_state": self._review_state(store),
        }

    def apply_codex_promotion_sync_execution_result(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        readiness_item_id = self._clean(payload.get("readiness_item_id"))
        source_sync_handoff_item_id = self._clean(payload.get("source_sync_handoff_item_id"))
        source_sync_audit_id = self._clean(payload.get("source_sync_audit_id"))
        promotion_candidate_id = self._clean(payload.get("promotion_candidate_id"))
        promotion_type = self._clean(payload.get("promotion_type"))
        target_system = self._clean(payload.get("target_system"))
        result_status = self._clean(payload.get("result_status"))
        result_summary = self._clean(payload.get("result_summary"))
        reviewer = self._clean(payload.get("reviewer") or "product_owner")
        execution_reference = self._clean(payload.get("execution_reference"))
        validation_summary = self._clean(payload.get("validation_summary"))
        rollback_summary = self._clean(payload.get("rollback_summary"))

        allowed_statuses = {"manual_sync_execution_recorded", "manual_sync_execution_failed", "manual_sync_execution_skipped", "needs_review", "note_only"}
        allowed_types = {"regression_baseline_candidate", "hermes_memory_candidate"}
        allowed_targets = {"", "local_regression_baseline_store", "live_hermes_memory"}
        if not readiness_item_id:
            raise ValueError("readiness_item_id is required")
        if promotion_type and promotion_type not in allowed_types:
            raise ValueError(f"promotion_type must be one of {sorted(allowed_types)}")
        if target_system not in allowed_targets:
            raise ValueError(f"target_system must be one of {sorted(allowed_targets)}")
        if result_status not in allowed_statuses:
            raise ValueError(f"result_status must be one of {sorted(allowed_statuses)}")
        if payload.get("contains_raw_file") or payload.get("contains_credentials"):
            raise ValueError("Codex promotion sync execution result intake is metadata-only; do not store raw files or credentials.")

        raw_changed_records = payload.get("changed_records", [])
        if not isinstance(raw_changed_records, list):
            raw_changed_records = []
        changed_records = [self._clean(item) for item in raw_changed_records[:30] if self._clean(item)]
        validation_results = self._normalize_worktree_validation_results(payload.get("validation_results", []))
        for value in [
            readiness_item_id,
            source_sync_handoff_item_id,
            source_sync_audit_id,
            promotion_candidate_id,
            promotion_type,
            target_system,
            result_status,
            result_summary,
            reviewer,
            execution_reference,
            validation_summary,
            rollback_summary,
            *changed_records,
        ]:
            self._ensure_safe_text(value)

        result_record = {
            "readiness_item_id": readiness_item_id,
            "source_sync_handoff_item_id": source_sync_handoff_item_id,
            "source_sync_audit_id": source_sync_audit_id,
            "promotion_candidate_id": promotion_candidate_id,
            "promotion_type": promotion_type,
            "target_system": target_system,
            "result_status": result_status,
            "result_summary": result_summary,
            "reviewer": reviewer,
            "execution_reference": execution_reference,
            "changed_records": changed_records,
            "changed_record_count": len(changed_records),
            "validation_summary": validation_summary,
            "rollback_summary": rollback_summary,
            "validation_results": validation_results,
            "result_contract": self._promotion_sync_execution_result_contract_status(result_status, changed_records, validation_results),
            "metadata_only": True,
            "manual_sync_execution_record_only": True,
            "automatic_sync_execution_allowed": False,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
            "updated_at": self._now(),
        }
        store = self._load_review_store()
        store.setdefault("codex_promotion_sync_execution_results", {})[readiness_item_id] = result_record
        store["updated_at"] = self._now()
        self._write_review_store(store)
        result_state = self._codex_promotion_sync_execution_result_state(store)
        return {
            "status": "saved",
            "readiness_item_id": readiness_item_id,
            "codex_promotion_sync_execution_result": result_record,
            "codex_promotion_sync_execution_result_state": result_state,
            "review_state": self._review_state(store),
        }

    def apply_codex_promotion_final_sync_execution_result(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        readiness_item_id = self._clean(payload.get("readiness_item_id"))
        source_final_sync_handoff_item_id = self._clean(payload.get("source_final_sync_handoff_item_id"))
        source_action_id = self._clean(payload.get("source_action_id"))
        final_closure_id = self._clean(payload.get("final_closure_id"))
        source_sync_audit_id = self._clean(payload.get("source_sync_audit_id"))
        promotion_candidate_id = self._clean(payload.get("promotion_candidate_id"))
        promotion_type = self._clean(payload.get("promotion_type"))
        target_system = self._clean(payload.get("target_system"))
        result_status = self._clean(payload.get("result_status"))
        result_summary = self._clean(payload.get("result_summary"))
        reviewer = self._clean(payload.get("reviewer") or "product_owner")
        execution_reference = self._clean(payload.get("execution_reference"))
        validation_summary = self._clean(payload.get("validation_summary"))
        rollback_summary = self._clean(payload.get("rollback_summary"))

        allowed_statuses = {"manual_final_sync_execution_recorded", "manual_final_sync_execution_failed", "manual_final_sync_execution_skipped", "note_only"}
        allowed_types = {"regression_baseline_candidate", "hermes_memory_candidate"}
        allowed_targets = {"", "local_regression_baseline_store", "live_hermes_memory"}
        if not readiness_item_id:
            raise ValueError("readiness_item_id is required")
        if promotion_type and promotion_type not in allowed_types:
            raise ValueError(f"promotion_type must be one of {sorted(allowed_types)}")
        if target_system not in allowed_targets:
            raise ValueError(f"target_system must be one of {sorted(allowed_targets)}")
        if result_status not in allowed_statuses:
            raise ValueError(f"result_status must be one of {sorted(allowed_statuses)}")
        if payload.get("contains_raw_file") or payload.get("contains_credentials"):
            raise ValueError("Codex promotion final sync execution result intake is metadata-only; do not store raw files or credentials.")

        raw_changed_records = payload.get("changed_records", [])
        if isinstance(raw_changed_records, str):
            raw_changed_records = [item.strip() for item in raw_changed_records.split("|") if item.strip()]
        if not isinstance(raw_changed_records, list):
            raw_changed_records = []
        changed_records = [self._clean(item) for item in raw_changed_records[:50] if self._clean(item)]
        validation_results = self._normalize_worktree_validation_results(payload.get("validation_results", []))
        for value in [
            readiness_item_id,
            source_final_sync_handoff_item_id,
            source_action_id,
            final_closure_id,
            source_sync_audit_id,
            promotion_candidate_id,
            promotion_type,
            target_system,
            result_status,
            result_summary,
            reviewer,
            execution_reference,
            validation_summary,
            rollback_summary,
            *changed_records,
        ]:
            self._ensure_safe_text(value)

        result_record = {
            "readiness_item_id": readiness_item_id,
            "source_final_sync_handoff_item_id": source_final_sync_handoff_item_id,
            "source_action_id": source_action_id,
            "final_closure_id": final_closure_id,
            "source_sync_audit_id": source_sync_audit_id,
            "promotion_candidate_id": promotion_candidate_id,
            "promotion_type": promotion_type,
            "target_system": target_system,
            "result_status": result_status,
            "result_summary": result_summary,
            "reviewer": reviewer,
            "execution_reference": execution_reference,
            "changed_records": changed_records,
            "changed_record_count": len(changed_records),
            "validation_summary": validation_summary,
            "rollback_summary": rollback_summary,
            "validation_results": validation_results,
            "result_contract": self._final_sync_execution_result_contract_status(result_status, changed_records, validation_results),
            "metadata_only": True,
            "manual_final_sync_execution_only": True,
            "automatic_execution_allowed": False,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
            "updated_at": self._now(),
        }
        store = self._load_review_store()
        store.setdefault("codex_promotion_final_sync_execution_results", {})[readiness_item_id] = result_record
        store["updated_at"] = self._now()
        self._write_review_store(store)
        result_state = self._codex_promotion_final_sync_execution_result_state(store)
        return {
            "status": "saved",
            "readiness_item_id": readiness_item_id,
            "codex_promotion_final_sync_execution_result": result_record,
            "codex_promotion_final_sync_execution_result_state": result_state,
            "review_state": self._review_state(store),
        }

    def apply_codex_promotion_final_publication_result(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        readiness_item_id = self._clean(payload.get("readiness_item_id"))
        source_final_publication_handoff_item_id = self._clean(payload.get("source_final_publication_handoff_item_id"))
        source_publication_action_id = self._clean(payload.get("source_publication_action_id"))
        source_action_id = self._clean(payload.get("source_action_id"))
        final_sync_completion_id = self._clean(payload.get("final_sync_completion_id"))
        final_closure_id = self._clean(payload.get("final_closure_id"))
        source_sync_audit_id = self._clean(payload.get("source_sync_audit_id"))
        promotion_candidate_id = self._clean(payload.get("promotion_candidate_id"))
        promotion_type = self._clean(payload.get("promotion_type"))
        target_system = self._clean(payload.get("target_system"))
        result_status = self._clean(payload.get("result_status"))
        result_summary = self._clean(payload.get("result_summary"))
        reviewer = self._clean(payload.get("reviewer") or "product_owner")
        publication_reference = self._clean(payload.get("publication_reference"))
        validation_summary = self._clean(payload.get("validation_summary") or payload.get("post_publication_validation_summary"))
        rollback_summary = self._clean(payload.get("rollback_summary"))

        allowed_statuses = {"manual_final_publication_recorded", "manual_final_publication_failed", "manual_final_publication_skipped", "note_only"}
        allowed_types = {"regression_baseline_candidate", "hermes_memory_candidate"}
        allowed_targets = {"", "local_regression_baseline_store", "live_hermes_memory"}
        if not readiness_item_id:
            raise ValueError("readiness_item_id is required")
        if promotion_type and promotion_type not in allowed_types:
            raise ValueError(f"promotion_type must be one of {sorted(allowed_types)}")
        if target_system not in allowed_targets:
            raise ValueError(f"target_system must be one of {sorted(allowed_targets)}")
        if result_status not in allowed_statuses:
            raise ValueError(f"result_status must be one of {sorted(allowed_statuses)}")
        if payload.get("contains_raw_file") or payload.get("contains_credentials"):
            raise ValueError("Codex promotion final publication result intake is metadata-only; do not store raw files or credentials.")

        raw_published_records = (
            payload.get("published_records")
            or payload.get("published_memory_event_ids")
            or payload.get("published_baseline_id")
            or []
        )
        if isinstance(raw_published_records, str):
            raw_published_records = [item.strip() for item in raw_published_records.split("|") if item.strip()]
        if not isinstance(raw_published_records, list):
            raw_published_records = []
        published_records = [self._clean(item) for item in raw_published_records[:50] if self._clean(item)]
        validation_results = self._normalize_worktree_validation_results(payload.get("validation_results", []))
        for value in [
            readiness_item_id,
            source_final_publication_handoff_item_id,
            source_publication_action_id,
            source_action_id,
            final_sync_completion_id,
            final_closure_id,
            source_sync_audit_id,
            promotion_candidate_id,
            promotion_type,
            target_system,
            result_status,
            result_summary,
            reviewer,
            publication_reference,
            validation_summary,
            rollback_summary,
            *published_records,
        ]:
            self._ensure_safe_text(value)

        result_record = {
            "readiness_item_id": readiness_item_id,
            "source_final_publication_handoff_item_id": source_final_publication_handoff_item_id,
            "source_publication_action_id": source_publication_action_id,
            "source_action_id": source_action_id,
            "final_sync_completion_id": final_sync_completion_id,
            "final_closure_id": final_closure_id,
            "source_sync_audit_id": source_sync_audit_id,
            "promotion_candidate_id": promotion_candidate_id,
            "promotion_type": promotion_type,
            "target_system": target_system,
            "result_status": result_status,
            "result_summary": result_summary,
            "reviewer": reviewer,
            "publication_reference": publication_reference,
            "published_records": published_records,
            "published_record_count": len(published_records),
            "validation_summary": validation_summary,
            "rollback_summary": rollback_summary,
            "validation_results": validation_results,
            "result_contract": self._final_publication_result_contract_status(
                result_status,
                publication_reference,
                published_records,
                validation_summary,
                validation_results,
            ),
            "metadata_only": True,
            "manual_final_publication_only": True,
            "automatic_publication_allowed": False,
            "project_memory_publication_allowed": False,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
            "updated_at": self._now(),
        }
        store = self._load_review_store()
        store.setdefault("codex_promotion_final_publication_results", {})[readiness_item_id] = result_record
        store["updated_at"] = self._now()
        self._write_review_store(store)
        result_state = self._codex_promotion_final_publication_result_state(store)
        return {
            "status": "saved",
            "readiness_item_id": readiness_item_id,
            "codex_promotion_final_publication_result": result_record,
            "codex_promotion_final_publication_result_state": result_state,
            "review_state": self._review_state(store),
        }

    def apply_codex_promotion_execution_result(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        readiness_item_id = self._clean(payload.get("readiness_item_id"))
        promotion_candidate_id = self._clean(payload.get("promotion_candidate_id"))
        promotion_type = self._clean(payload.get("promotion_type"))
        result_status = self._clean(payload.get("result_status"))
        result_summary = self._clean(payload.get("result_summary"))
        reviewer = self._clean(payload.get("reviewer") or "product_owner")
        execution_reference = self._clean(payload.get("execution_reference"))
        validation_summary = self._clean(payload.get("validation_summary"))
        rollback_summary = self._clean(payload.get("rollback_summary"))

        allowed_statuses = {"manual_execution_recorded", "manual_execution_failed", "manual_execution_skipped", "needs_review", "note_only"}
        allowed_types = {"regression_baseline_candidate", "hermes_memory_candidate"}
        if not readiness_item_id:
            raise ValueError("readiness_item_id is required")
        if promotion_type and promotion_type not in allowed_types:
            raise ValueError(f"promotion_type must be one of {sorted(allowed_types)}")
        if result_status not in allowed_statuses:
            raise ValueError(f"result_status must be one of {sorted(allowed_statuses)}")
        if payload.get("contains_raw_file") or payload.get("contains_credentials"):
            raise ValueError("Codex promotion execution result intake is metadata-only; do not store raw files or credentials.")

        raw_changed_records = payload.get("changed_records", [])
        if not isinstance(raw_changed_records, list):
            raw_changed_records = []
        changed_records = [self._clean(item) for item in raw_changed_records[:30] if self._clean(item)]
        validation_results = self._normalize_worktree_validation_results(payload.get("validation_results", []))
        for value in [
            readiness_item_id,
            promotion_candidate_id,
            promotion_type,
            result_status,
            result_summary,
            reviewer,
            execution_reference,
            validation_summary,
            rollback_summary,
            *changed_records,
        ]:
            self._ensure_safe_text(value)

        result_record = {
            "readiness_item_id": readiness_item_id,
            "promotion_candidate_id": promotion_candidate_id,
            "promotion_type": promotion_type,
            "result_status": result_status,
            "result_summary": result_summary,
            "reviewer": reviewer,
            "execution_reference": execution_reference,
            "changed_records": changed_records,
            "changed_record_count": len(changed_records),
            "validation_summary": validation_summary,
            "rollback_summary": rollback_summary,
            "validation_results": validation_results,
            "result_contract": self._promotion_execution_result_contract_status(result_status, changed_records, validation_results),
            "metadata_only": True,
            "manual_execution_record_only": True,
            "automatic_execution_allowed": False,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
            "updated_at": self._now(),
        }
        store = self._load_review_store()
        store.setdefault("codex_promotion_execution_results", {})[readiness_item_id] = result_record
        store["updated_at"] = self._now()
        self._write_review_store(store)
        result_state = self._codex_promotion_execution_result_state(store)
        return {
            "status": "saved",
            "readiness_item_id": readiness_item_id,
            "codex_promotion_execution_result": result_record,
            "codex_promotion_execution_result_state": result_state,
            "review_state": self._review_state(store),
        }

    def apply_codex_promotion_sync_review(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        sync_audit_id = self._clean(payload.get("sync_audit_id"))
        readiness_item_id = self._clean(payload.get("readiness_item_id"))
        promotion_candidate_id = self._clean(payload.get("promotion_candidate_id"))
        promotion_type = self._clean(payload.get("promotion_type"))
        target_system = self._clean(payload.get("target_system"))
        review_status = self._clean(payload.get("review_status"))
        review_note = self._clean(payload.get("review_note"))
        reviewer = self._clean(payload.get("reviewer") or "product_owner")

        allowed_statuses = {"approved_for_future_sync", "needs_sync_inputs", "deferred", "rejected", "note_only"}
        allowed_types = {"regression_baseline_candidate", "hermes_memory_candidate"}
        allowed_targets = {"local_regression_baseline_store", "live_hermes_memory"}
        if not sync_audit_id:
            raise ValueError("sync_audit_id is required")
        if promotion_type and promotion_type not in allowed_types:
            raise ValueError(f"promotion_type must be one of {sorted(allowed_types)}")
        if target_system and target_system not in allowed_targets:
            raise ValueError(f"target_system must be one of {sorted(allowed_targets)}")
        if review_status not in allowed_statuses:
            raise ValueError(f"review_status must be one of {sorted(allowed_statuses)}")
        if payload.get("contains_raw_file") or payload.get("contains_credentials"):
            raise ValueError("Codex promotion sync review is metadata-only; do not store raw files or credentials.")

        raw_confirmed_checks = payload.get("confirmed_sync_checks", [])
        if isinstance(raw_confirmed_checks, str):
            raw_confirmed_checks = [item.strip() for item in raw_confirmed_checks.split("|") if item.strip()]
        if not isinstance(raw_confirmed_checks, list):
            raw_confirmed_checks = []
        confirmed_sync_checks = [self._clean(item) for item in raw_confirmed_checks[:20] if self._clean(item)]
        for value in [
            sync_audit_id,
            readiness_item_id,
            promotion_candidate_id,
            promotion_type,
            target_system,
            review_status,
            review_note,
            reviewer,
            *confirmed_sync_checks,
        ]:
            self._ensure_safe_text(value)

        decision = {
            "sync_audit_id": sync_audit_id,
            "readiness_item_id": readiness_item_id,
            "promotion_candidate_id": promotion_candidate_id,
            "promotion_type": promotion_type,
            "target_system": target_system,
            "review_status": review_status,
            "review_note": review_note,
            "reviewer": reviewer,
            "confirmed_sync_checks": confirmed_sync_checks,
            "metadata_only": True,
            "future_sync_only": True,
            "automatic_sync_allowed": False,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
            "updated_at": self._now(),
        }
        store = self._load_review_store()
        store.setdefault("codex_promotion_sync_reviews", {})[sync_audit_id] = decision
        store["updated_at"] = self._now()
        self._write_review_store(store)
        return {
            "status": "saved",
            "sync_audit_id": sync_audit_id,
            "codex_promotion_sync_review": decision,
            "codex_promotion_sync_review_state": self._codex_promotion_sync_review_state(store),
            "review_state": self._review_state(store),
        }

    def apply_iteration_proposal_review(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        proposal_id = self._clean(payload.get("proposal_id"))
        review_status = self._clean(payload.get("review_status"))
        review_note = self._clean(payload.get("review_note"))
        reviewer = self._clean(payload.get("reviewer") or "product_owner")
        proposal_status = self._clean(payload.get("proposal_status"))
        task_seed_count = self._safe_int(payload.get("task_seed_count"), 0)
        open_watch_item_count = self._safe_int(payload.get("open_watch_item_count"), 0)

        allowed = {"approved_for_codex_queue", "needs_changes", "deferred", "rejected", "note_only"}
        if not proposal_id:
            raise ValueError("proposal_id is required")
        if review_status not in allowed:
            raise ValueError(f"review_status must be one of {sorted(allowed)}")
        for value in [review_note, proposal_status]:
            self._ensure_safe_text(value)

        store = self._load_review_store()
        decision = {
            "proposal_id": proposal_id,
            "review_status": review_status,
            "review_note": review_note,
            "reviewer": reviewer,
            "proposal_status": proposal_status,
            "task_seed_count": task_seed_count,
            "open_watch_item_count": open_watch_item_count,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
            "updated_at": self._now(),
        }
        store.setdefault("iteration_proposal_reviews", {})[proposal_id] = decision
        store["updated_at"] = self._now()
        self._write_review_store(store)
        return {
            "status": "saved",
            "proposal_id": proposal_id,
            "proposal_review": decision,
            "proposal_review_state": self._iteration_proposal_review_state(store),
            "review_state": self._review_state(store),
        }

    def promote_baseline(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        result = self.run({"mode": "auto", "source": "promote_baseline"})
        summary = self._round_summary_payload(result)
        if summary["baseline_status"] != "ready_for_regression":
            raise ValueError("Training round is not ready for baseline promotion")

        store = self._load_review_store()
        baseline_id = self._clean(payload.get("baseline_id")) or summary["baseline_id"]
        promoted_at = self._now()
        record = {
            "baseline_id": baseline_id,
            "version": TRAINING_VERSION,
            "promotion_status": "approved",
            "promoted_by": self._clean(payload.get("promoted_by") or "product_owner"),
            "promoted_at": promoted_at,
            "task_count": summary["promoted_task_count"],
            "capability_regression_count": summary["capability_regression_count"],
            "data_gap_regression_count": summary["data_gap_regression_count"],
            "data_decision_count": len(summary["data_decisions"]),
            "contains_raw_file": False,
            "contains_credentials": False,
            "notes": self._clean(payload.get("notes")),
        }
        store.setdefault("baseline_promotions", {})[baseline_id] = record
        store["updated_at"] = promoted_at
        self._write_review_store(store)
        return {
            **summary,
            "status": "baseline_promoted",
            "promotion_record": record,
            "review_state": self._review_state(store),
        }

    def apply_task_review(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        task_id = self._clean(payload.get("task_id"))
        review_status = self._clean(payload.get("review_status"))
        review_note = self._clean(payload.get("review_note"))
        reviewer = self._clean(payload.get("reviewer") or "product_owner")

        allowed = {"approved", "needs_changes", "rejected", "note_only"}
        if not task_id:
            raise ValueError("task_id is required")
        if review_status not in allowed:
            raise ValueError(f"review_status must be one of {sorted(allowed)}")
        self._ensure_safe_text(review_note)

        store = self._load_review_store()
        store.setdefault("task_reviews", {})[task_id] = {
            "task_id": task_id,
            "review_status": review_status,
            "review_note": review_note,
            "reviewer": reviewer,
            "updated_at": self._now(),
        }
        store["updated_at"] = self._now()
        self._write_review_store(store)
        return {
            "status": "saved",
            "task_id": task_id,
            "review": store["task_reviews"][task_id],
            "review_state": self._review_state(store),
        }

    def register_data_source(self, payload: dict | None = None) -> dict:
        payload = payload or {}
        task_id = self._clean(payload.get("task_id"))
        data_status = self._clean(payload.get("data_status") or "registered")
        source_type = self._clean(payload.get("source_type") or "unknown")
        source_label = self._clean(payload.get("source_label"))
        source_reference = self._clean(payload.get("source_reference"))
        owner = self._clean(payload.get("owner"))
        field_notes = self._clean(payload.get("field_notes"))
        skip_reason = self._clean(payload.get("skip_reason"))
        sensitivity_level = self._clean(payload.get("sensitivity_level") or "internal")

        allowed = {"registered", "skipped_for_now", "not_available"}
        if not task_id:
            raise ValueError("task_id is required")
        if data_status not in allowed:
            raise ValueError(f"data_status must be one of {sorted(allowed)}")
        for value in [source_label, source_reference, owner, field_notes, skip_reason]:
            self._ensure_safe_text(value)

        store = self._load_review_store()
        source_id = self._data_source_id(task_id, data_status, store)
        source = {
            "data_source_id": source_id,
            "task_id": task_id,
            "data_status": data_status,
            "source_type": source_type,
            "source_label": source_label,
            "source_reference": source_reference,
            "owner": owner,
            "field_notes": field_notes,
            "skip_reason": skip_reason,
            "sensitivity_level": sensitivity_level,
            "retention_policy": "training_lifecycle",
            "contains_raw_file": False,
            "contains_credentials": False,
            "updated_at": self._now(),
        }
        store.setdefault("data_sources", {})[source_id] = source
        store["updated_at"] = self._now()
        self._write_review_store(store)
        return {
            "status": "saved",
            "task_id": task_id,
            "data_source": source,
            "review_state": self._review_state(store),
        }

    def _round_summary_payload(self, result: dict) -> dict:
        overview = result.get("training_overview", {})
        tasks = result.get("training_tasks", [])
        approved_tasks = [item for item in tasks if item.get("review", {}).get("review_status") == "approved"]
        review_blocked = [
            item
            for item in tasks
            if item.get("review", {}).get("review_status") in {"needs_changes", "rejected", "pending_review"}
            or item.get("human_review_required")
        ]
        failed_tasks = [item for item in tasks if item.get("status") == "failed"]
        baseline_status = "ready_for_regression"
        if not tasks:
            baseline_status = "no_training_tasks"
        elif review_blocked:
            baseline_status = "review_or_data_decision_required"
        elif failed_tasks:
            baseline_status = "failed_task_blocked"
        elif len(approved_tasks) != len(tasks):
            baseline_status = "approval_incomplete"

        promoted_tasks = [self._baseline_task(item) for item in approved_tasks]
        data_decisions = self._baseline_data_decisions(tasks)
        capability_count = len([item for item in promoted_tasks if item["baseline_role"] == "capability_regression"])
        data_gap_count = len([item for item in promoted_tasks if item["baseline_role"] == "data_gap_regression"])
        baseline_id = f"TRAIN-BASELINE-{TRAINING_VERSION}-TPI-001"
        return {
            "schema": "athena.training_round_summary.v1",
            "baseline_id": baseline_id,
            "version": TRAINING_VERSION,
            "baseline_status": baseline_status,
            "round_id": overview.get("run_id", f"TRAIN-RUN-{TRAINING_VERSION}-TPI-001"),
            "tenant_id": overview.get("tenant_id"),
            "factory_id": overview.get("factory_id"),
            "target_persona": overview.get("target_persona"),
            "answer_contract": ["management_summary", "reason_and_evidence", "recommended_action"],
            "promoted_task_count": len(promoted_tasks),
            "total_task_count": overview.get("total_task_count", 0),
            "approved_task_count": len(approved_tasks),
            "capability_regression_count": capability_count,
            "data_gap_regression_count": data_gap_count,
            "pending_or_blocked_task_count": len(review_blocked) + len(failed_tasks),
            "promoted_tasks": promoted_tasks,
            "data_decisions": data_decisions,
            "automatic_regression_set": {
                "regression_set_id": "TPI-AUTO-REGRESSION-001",
                "task_ids": [item["task_id"] for item in promoted_tasks],
                "rerun_policy": "Rerun after every Athena production, Hermes, training-pack, or adapter-contract change.",
                "expected_behavior": (
                    "Passed capability tasks must keep their evidence/governance checks. Data-gap tasks must keep "
                    "clear limitation statements instead of inventing missing customer data."
                ),
            },
            "hermes_baseline_payload": {
                "schema": "hermes.baseline_promotion.v1",
                "source": "demo",
                "scope": "tenant",
                "tenant_id": overview.get("tenant_id"),
                "factory_id": overview.get("factory_id"),
                "retention_policy": "training_lifecycle",
                "sensitivity_level": "internal",
                "promotion_status": "approved" if baseline_status == "ready_for_regression" else "reviewed",
                "baseline_id": baseline_id,
                "version": TRAINING_VERSION,
                "summary": {
                    "promoted_task_count": len(promoted_tasks),
                    "capability_regression_count": capability_count,
                    "data_gap_regression_count": data_gap_count,
                    "data_decision_count": len(data_decisions),
                },
            },
            "blocked_actions": [
                "store_raw_training_files",
                "store_customer_credentials",
                "write_to_aps_or_iot",
                "write_live_hermes_memory_without_connector_review",
                "treat_unavailable_cost_or_stage_records_as_real_data",
            ],
        }

    @staticmethod
    def _baseline_task(item: dict) -> dict:
        status = item.get("status", "")
        return {
            "task_id": item.get("task_id", ""),
            "capability": item.get("capability", ""),
            "capability_group": item.get("capability_group", ""),
            "source_status": status,
            "baseline_role": "data_gap_regression" if status == "needs_data" else "capability_regression",
            "score": item.get("score", 0),
            "evidence_refs": item.get("evaluation_checks", {}).get("resolved_evidence_refs", []),
            "locked_next_action": item.get("next_action", ""),
        }

    @staticmethod
    def _baseline_data_decisions(tasks: list[dict]) -> list[dict]:
        decisions = []
        task_names = {
            "TPI-GM-DELIVERY-001": "APS schedule and delivery-time coverage",
            "TPI-GM-COST-001": "Customer purchasing and labor cost coverage",
            "TPI-PROCESS-STAGES-001": "Stage-level downstream process coverage",
        }
        for task in tasks:
            task_id = task.get("task_id", "")
            if task_id not in DATA_NEEDED_BY_TASK:
                continue
            data_sources = task.get("data_intake", {}).get("data_sources", [])
            latest = sorted(data_sources, key=lambda source: source.get("updated_at", ""))[-1] if data_sources else {}
            data_status = latest.get("data_status", "not_registered")
            coverage = "missing"
            remaining_gap = DATA_NEEDED_BY_TASK.get(task_id, "")
            if task_id == "TPI-GM-DELIVERY-001" and data_status == "registered":
                coverage = "partial_aps_schedule_delivery_coverage"
                remaining_gap = "IOT still needs an order/work-order join rule before full order-level root-cause analysis."
            elif task_id == "TPI-GM-COST-001" and data_status == "not_available":
                coverage = "not_available_customer_cost_data"
                remaining_gap = "Athena must state that true purchasing, labor, and per-garment cost cannot be calculated from current data."
            elif task_id == "TPI-PROCESS-STAGES-001" and data_status == "not_available":
                coverage = "not_available_stage_level_records"
                remaining_gap = "Athena must limit downstream bottleneck analysis until stage timestamps, WIP, hold, defect, and rework data exist."
            elif data_status == "skipped_for_now":
                coverage = "deferred_by_product_owner"
            decisions.append(
                {
                    "task_id": task_id,
                    "decision_name": task_names[task_id],
                    "data_status": data_status,
                    "coverage": coverage,
                    "source_type": latest.get("source_type", ""),
                    "source_label": latest.get("source_label", ""),
                    "source_reference": latest.get("source_reference", ""),
                    "field_notes": latest.get("field_notes", ""),
                    "remaining_gap": remaining_gap,
                    "contains_raw_file": latest.get("contains_raw_file", False),
                    "contains_credentials": latest.get("contains_credentials", False),
                }
            )
        return decisions

    def _load_pack(self) -> dict:
        if not self.training_pack_path.exists():
            return {
                "schema_version": "missing",
                "tenant_id": "unknown",
                "factory_id": None,
                "candidate_training_tasks": [],
                "training_governance": {},
            }
        try:
            return json.loads(self.training_pack_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {
                "schema_version": "invalid_json",
                "tenant_id": "unknown",
                "factory_id": None,
                "candidate_training_tasks": [],
                "training_governance": {},
            }

    def _load_review_store(self) -> dict:
        if not self.review_store_path.exists():
            return self._empty_review_store()
        try:
            loaded = json.loads(self.review_store_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError:
            return self._empty_review_store()
        loaded.setdefault("schema_version", "athena.training_task_reviews.v1")
        loaded.setdefault("version", TRAINING_VERSION)
        loaded.setdefault("task_reviews", {})
        loaded.setdefault("data_sources", {})
        loaded.setdefault("baseline_promotions", {})
        loaded.setdefault("handoff_reviews", {})
        loaded.setdefault("iteration_proposal_reviews", {})
        loaded.setdefault("codex_execution_reviews", {})
        loaded.setdefault("codex_worktree_results", {})
        loaded.setdefault("codex_worktree_result_reviews", {})
        loaded.setdefault("codex_promotion_approvals", {})
        loaded.setdefault("codex_promotion_readiness_reviews", {})
        loaded.setdefault("codex_promotion_execution_results", {})
        loaded.setdefault("codex_promotion_sync_reviews", {})
        loaded.setdefault("codex_promotion_sync_readiness_reviews", {})
        loaded.setdefault("codex_promotion_sync_execution_results", {})
        loaded.setdefault("codex_promotion_sync_closure_reviews", {})
        loaded.setdefault("codex_promotion_final_sync_execution_results", {})
        loaded.setdefault("codex_promotion_final_completion_reviews", {})
        loaded.setdefault("codex_promotion_final_publication_results", {})
        loaded.setdefault("updated_at", "")
        return loaded

    def _write_review_store(self, store: dict) -> None:
        self.review_store_path.parent.mkdir(parents=True, exist_ok=True)
        store["version"] = TRAINING_VERSION
        self.review_store_path.write_text(json.dumps(store, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    @staticmethod
    def _empty_review_store() -> dict:
        return {
            "schema_version": "athena.training_task_reviews.v1",
            "version": TRAINING_VERSION,
            "updated_at": "",
            "task_reviews": {},
            "data_sources": {},
            "baseline_promotions": {},
            "handoff_reviews": {},
            "iteration_proposal_reviews": {},
            "codex_execution_reviews": {},
            "codex_worktree_results": {},
            "codex_worktree_result_reviews": {},
            "codex_promotion_approvals": {},
            "codex_promotion_readiness_reviews": {},
            "codex_promotion_execution_results": {},
            "codex_promotion_sync_reviews": {},
            "codex_promotion_sync_readiness_reviews": {},
            "codex_promotion_sync_execution_results": {},
            "codex_promotion_sync_closure_reviews": {},
            "codex_promotion_final_sync_execution_results": {},
            "codex_promotion_final_completion_reviews": {},
            "codex_promotion_final_publication_results": {},
        }

    @staticmethod
    def _apply_review_store(results: list[dict], store: dict) -> list[dict]:
        task_reviews = store.get("task_reviews", {})
        sources_by_task: dict[str, list[dict]] = {}
        for source in store.get("data_sources", {}).values():
            sources_by_task.setdefault(source.get("task_id", ""), []).append(source)

        enriched = []
        for item in results:
            task_id = item["task_id"]
            review = task_reviews.get(task_id, {})
            data_sources = sorted(sources_by_task.get(task_id, []), key=lambda source: source.get("updated_at", ""))
            latest_data = data_sources[-1] if data_sources else {}
            review_status = review.get("review_status")
            if not review_status:
                review_status = "pending_review" if item["human_review_required"] else "auto_regression"
            human_review_required = item["human_review_required"] and review_status != "approved"
            enriched.append(
                {
                    **item,
                    "human_review_required": human_review_required,
                    "review": {
                        "review_status": review_status,
                        "review_note": review.get("review_note", ""),
                        "reviewer": review.get("reviewer", ""),
                        "updated_at": review.get("updated_at", ""),
                    },
                    "data_intake": {
                        "can_register_data": item["status"] == "needs_data",
                        "latest_data_status": latest_data.get("data_status", "not_registered"),
                        "registered_count": len([source for source in data_sources if source.get("data_status") == "registered"]),
                        "skipped_count": len([source for source in data_sources if source.get("data_status") == "skipped_for_now"]),
                        "not_available_count": len([source for source in data_sources if source.get("data_status") == "not_available"]),
                        "data_sources": data_sources,
                    },
                }
            )
        return enriched

    @staticmethod
    def _review_state(store: dict) -> dict:
        reviews = list(store.get("task_reviews", {}).values())
        data_sources = list(store.get("data_sources", {}).values())
        baseline_promotions = list(store.get("baseline_promotions", {}).values())
        handoff_reviews = list(store.get("handoff_reviews", {}).values())
        proposal_reviews = list(store.get("iteration_proposal_reviews", {}).values())
        execution_reviews = list(store.get("codex_execution_reviews", {}).values())
        worktree_results = list(store.get("codex_worktree_results", {}).values())
        worktree_result_reviews = list(store.get("codex_worktree_result_reviews", {}).values())
        promotion_approvals = list(store.get("codex_promotion_approvals", {}).values())
        promotion_readiness_reviews = list(store.get("codex_promotion_readiness_reviews", {}).values())
        promotion_execution_results = list(store.get("codex_promotion_execution_results", {}).values())
        promotion_sync_reviews = list(store.get("codex_promotion_sync_reviews", {}).values())
        promotion_sync_readiness_reviews = list(store.get("codex_promotion_sync_readiness_reviews", {}).values())
        promotion_sync_execution_results = list(store.get("codex_promotion_sync_execution_results", {}).values())
        promotion_sync_closure_reviews = list(store.get("codex_promotion_sync_closure_reviews", {}).values())
        promotion_final_sync_execution_results = list(store.get("codex_promotion_final_sync_execution_results", {}).values())
        promotion_final_completion_reviews = list(store.get("codex_promotion_final_completion_reviews", {}).values())
        promotion_final_publication_results = list(store.get("codex_promotion_final_publication_results", {}).values())
        return {
            "schema_version": store.get("schema_version", "athena.training_task_reviews.v1"),
            "version": store.get("version", TRAINING_VERSION),
            "updated_at": store.get("updated_at", ""),
            "review_count": len(reviews),
            "approved_count": len([item for item in reviews if item.get("review_status") == "approved"]),
            "needs_changes_count": len([item for item in reviews if item.get("review_status") == "needs_changes"]),
            "rejected_count": len([item for item in reviews if item.get("review_status") == "rejected"]),
            "note_count": len([item for item in reviews if item.get("review_status") == "note_only"]),
            "data_source_count": len(data_sources),
            "registered_data_source_count": len([item for item in data_sources if item.get("data_status") == "registered"]),
            "skipped_data_source_count": len([item for item in data_sources if item.get("data_status") == "skipped_for_now"]),
            "not_available_data_source_count": len([item for item in data_sources if item.get("data_status") == "not_available"]),
            "baseline_promotion_count": len(baseline_promotions),
            "handoff_review_count": len(handoff_reviews),
            "handoff_resolved_count": len([item for item in handoff_reviews if item.get("review_status") in {"approved_for_next_loop", "resolved"}]),
            "handoff_deferred_count": len([item for item in handoff_reviews if item.get("review_status") == "deferred"]),
            "handoff_needs_data_count": len([item for item in handoff_reviews if item.get("review_status") == "needs_data"]),
            "iteration_proposal_review_count": len(proposal_reviews),
            "iteration_proposal_approved_count": len([item for item in proposal_reviews if item.get("review_status") == "approved_for_codex_queue"]),
            "iteration_proposal_needs_changes_count": len([item for item in proposal_reviews if item.get("review_status") == "needs_changes"]),
            "iteration_proposal_rejected_count": len([item for item in proposal_reviews if item.get("review_status") == "rejected"]),
            "codex_execution_review_count": len(execution_reviews),
            "codex_worktree_preparation_approved_count": len([item for item in execution_reviews if item.get("review_status") == "approved_for_worktree_preparation"]),
            "codex_execution_needs_changes_count": len([item for item in execution_reviews if item.get("review_status") == "needs_changes"]),
            "codex_execution_deferred_count": len([item for item in execution_reviews if item.get("review_status") == "deferred"]),
            "codex_worktree_result_count": len(worktree_results),
            "codex_worktree_validation_passed_count": len([item for item in worktree_results if item.get("result_status") == "validation_passed"]),
            "codex_worktree_validation_failed_count": len([item for item in worktree_results if item.get("result_status") == "validation_failed"]),
            "codex_worktree_result_review_count": len(worktree_result_reviews),
            "codex_worktree_regression_promotion_review_count": len([item for item in worktree_result_reviews if item.get("review_status") in {"approved_for_regression_baseline", "approved_for_regression_and_memory"}]),
            "codex_worktree_hermes_memory_review_count": len([item for item in worktree_result_reviews if item.get("review_status") in {"approved_for_hermes_memory_candidate", "approved_for_regression_and_memory"}]),
            "codex_promotion_approval_count": len(promotion_approvals),
            "codex_future_promotion_approved_count": len([item for item in promotion_approvals if item.get("review_status") == "approved_for_future_promotion"]),
            "codex_promotion_hold_count": len([item for item in promotion_approvals if item.get("review_status") == "hold_for_later"]),
            "codex_promotion_skipped_count": len([item for item in promotion_approvals if item.get("review_status") == "skipped_for_now"]),
            "codex_promotion_needs_changes_count": len([item for item in promotion_approvals if item.get("review_status") == "needs_changes"]),
            "codex_promotion_readiness_review_count": len(promotion_readiness_reviews),
            "codex_promotion_readiness_confirmed_count": len([item for item in promotion_readiness_reviews if item.get("review_status") == "confirmed_ready_for_manual_execution"]),
            "codex_promotion_readiness_needs_inputs_count": len([item for item in promotion_readiness_reviews if item.get("review_status") == "needs_execution_inputs"]),
            "codex_promotion_readiness_deferred_count": len([item for item in promotion_readiness_reviews if item.get("review_status") == "deferred"]),
            "codex_promotion_execution_result_count": len(promotion_execution_results),
            "codex_promotion_execution_result_passed_count": len([item for item in promotion_execution_results if item.get("result_status") == "manual_execution_recorded"]),
            "codex_promotion_execution_result_failed_count": len([item for item in promotion_execution_results if item.get("result_status") == "manual_execution_failed"]),
            "codex_promotion_sync_review_count": len(promotion_sync_reviews),
            "codex_promotion_sync_approved_count": len([item for item in promotion_sync_reviews if item.get("review_status") == "approved_for_future_sync"]),
            "codex_promotion_sync_needs_inputs_count": len([item for item in promotion_sync_reviews if item.get("review_status") == "needs_sync_inputs"]),
            "codex_promotion_sync_deferred_count": len([item for item in promotion_sync_reviews if item.get("review_status") == "deferred"]),
            "codex_promotion_sync_rejected_count": len([item for item in promotion_sync_reviews if item.get("review_status") == "rejected"]),
            "codex_promotion_sync_readiness_review_count": len(promotion_sync_readiness_reviews),
            "codex_promotion_sync_readiness_confirmed_count": len([item for item in promotion_sync_readiness_reviews if item.get("review_status") == "confirmed_ready_for_manual_sync_execution"]),
            "codex_promotion_sync_readiness_needs_inputs_count": len([item for item in promotion_sync_readiness_reviews if item.get("review_status") == "needs_sync_execution_inputs"]),
            "codex_promotion_sync_readiness_deferred_count": len([item for item in promotion_sync_readiness_reviews if item.get("review_status") == "deferred"]),
            "codex_promotion_sync_readiness_rejected_count": len([item for item in promotion_sync_readiness_reviews if item.get("review_status") == "rejected"]),
            "codex_promotion_sync_execution_result_count": len(promotion_sync_execution_results),
            "codex_promotion_sync_execution_result_passed_count": len([item for item in promotion_sync_execution_results if item.get("result_status") == "manual_sync_execution_recorded"]),
            "codex_promotion_sync_execution_result_failed_count": len([item for item in promotion_sync_execution_results if item.get("result_status") == "manual_sync_execution_failed"]),
            "codex_promotion_sync_execution_result_contract_complete_count": len([item for item in promotion_sync_execution_results if item.get("result_contract", {}).get("contract_complete")]),
            "codex_promotion_sync_closure_review_count": len(promotion_sync_closure_reviews),
            "codex_promotion_sync_closure_approved_count": len([item for item in promotion_sync_closure_reviews if item.get("review_status") == "approved_for_final_sync"]),
            "codex_promotion_sync_closure_needs_inputs_count": len([item for item in promotion_sync_closure_reviews if item.get("review_status") == "needs_final_sync_inputs"]),
            "codex_promotion_sync_closure_deferred_count": len([item for item in promotion_sync_closure_reviews if item.get("review_status") == "deferred"]),
            "codex_promotion_sync_closure_rejected_count": len([item for item in promotion_sync_closure_reviews if item.get("review_status") == "rejected"]),
            "codex_promotion_final_sync_execution_result_count": len(promotion_final_sync_execution_results),
            "codex_promotion_final_sync_execution_result_passed_count": len([item for item in promotion_final_sync_execution_results if item.get("result_status") == "manual_final_sync_execution_recorded"]),
            "codex_promotion_final_sync_execution_result_failed_count": len([item for item in promotion_final_sync_execution_results if item.get("result_status") == "manual_final_sync_execution_failed"]),
            "codex_promotion_final_sync_execution_result_contract_complete_count": len([item for item in promotion_final_sync_execution_results if item.get("result_contract", {}).get("contract_complete")]),
            "codex_promotion_final_completion_review_count": len(promotion_final_completion_reviews),
            "codex_promotion_final_completion_approved_count": len([item for item in promotion_final_completion_reviews if item.get("review_status") == "approved_final_completion"]),
            "codex_promotion_final_completion_needs_inputs_count": len([item for item in promotion_final_completion_reviews if item.get("review_status") == "needs_completion_inputs"]),
            "codex_promotion_final_completion_rejected_count": len([item for item in promotion_final_completion_reviews if item.get("review_status") == "rejected"]),
            "codex_promotion_final_publication_result_count": len(promotion_final_publication_results),
            "codex_promotion_final_publication_result_passed_count": len([item for item in promotion_final_publication_results if item.get("result_status") == "manual_final_publication_recorded"]),
            "codex_promotion_final_publication_result_failed_count": len([item for item in promotion_final_publication_results if item.get("result_status") == "manual_final_publication_failed"]),
            "codex_promotion_final_publication_result_contract_complete_count": len([item for item in promotion_final_publication_results if item.get("result_contract", {}).get("contract_complete")]),
            "task_reviews": store.get("task_reviews", {}),
            "data_sources": store.get("data_sources", {}),
            "baseline_promotions": store.get("baseline_promotions", {}),
            "handoff_reviews": store.get("handoff_reviews", {}),
            "iteration_proposal_reviews": store.get("iteration_proposal_reviews", {}),
            "codex_execution_reviews": store.get("codex_execution_reviews", {}),
            "codex_worktree_results": store.get("codex_worktree_results", {}),
            "codex_worktree_result_reviews": store.get("codex_worktree_result_reviews", {}),
            "codex_promotion_approvals": store.get("codex_promotion_approvals", {}),
            "codex_promotion_readiness_reviews": store.get("codex_promotion_readiness_reviews", {}),
            "codex_promotion_execution_results": store.get("codex_promotion_execution_results", {}),
            "codex_promotion_sync_reviews": store.get("codex_promotion_sync_reviews", {}),
            "codex_promotion_sync_readiness_reviews": store.get("codex_promotion_sync_readiness_reviews", {}),
            "codex_promotion_sync_execution_results": store.get("codex_promotion_sync_execution_results", {}),
            "codex_promotion_sync_closure_reviews": store.get("codex_promotion_sync_closure_reviews", {}),
            "codex_promotion_final_sync_execution_results": store.get("codex_promotion_final_sync_execution_results", {}),
            "codex_promotion_final_completion_reviews": store.get("codex_promotion_final_completion_reviews", {}),
            "codex_promotion_final_publication_results": store.get("codex_promotion_final_publication_results", {}),
        }

    @staticmethod
    def _filter_tasks(tasks: list[dict], focus: str) -> list[dict]:
        if focus in {"", "all", "auto"}:
            return list(tasks)
        return [
            task
            for task in tasks
            if focus in str(task.get("capability", "")).lower()
            or focus in CAPABILITY_GROUPS.get(task.get("capability", ""), "").lower()
            or focus in str(task.get("task_id", "")).lower()
        ] or list(tasks)

    @staticmethod
    def _evidence_index(pack: dict) -> dict[str, dict]:
        index: dict[str, dict] = {}
        for key in [
            "source_files",
            "data_quality_findings",
            "voc_insights",
            "aps_workflow_insights",
            "hermes_memory_events",
        ]:
            for item in pack.get(key, []):
                for id_key in ["source_id", "finding_id", "insight_id", "event_id"]:
                    value = item.get(id_key)
                    if value:
                        index[value] = {"collection": key, **item}
        return index

    def _evaluate_task(self, task: dict, evidence_index: dict[str, dict], governance: dict) -> dict:
        evidence_refs = task.get("evidence_refs", [])
        resolved = [ref for ref in evidence_refs if ref in evidence_index]
        missing = [ref for ref in evidence_refs if ref not in evidence_index]
        expected = task.get("expected_behavior", [])
        task_id = task.get("task_id", "")
        capability = task.get("capability", "unknown")
        capability_group = CAPABILITY_GROUPS.get(capability, "other")
        governance_checks = self._governance_checks(governance, expected)
        status = "passed"
        if missing:
            status = "failed"
        elif task_id in DATA_NEEDED_BY_TASK:
            status = "needs_data"

        score = self._score(status, resolved, evidence_refs, governance_checks)
        return {
            "task_id": task_id,
            "capability": capability,
            "capability_group": capability_group,
            "question": task.get("question", ""),
            "status": status,
            "score": score,
            "auto_evaluated": True,
            "human_review_required": status in {"failed", "needs_data"},
            "expected_behavior": expected,
            "evaluation_checks": {
                "evidence_resolved": not missing and bool(evidence_refs),
                "evidence_ref_count": len(evidence_refs),
                "resolved_evidence_refs": resolved,
                "missing_evidence_refs": missing,
                "governance_aligned": all(item["passed"] for item in governance_checks),
                "governance_checks": governance_checks,
                "data_gap_known": task_id in DATA_NEEDED_BY_TASK,
                "data_gap_note": DATA_NEEDED_BY_TASK.get(task_id, ""),
            },
            "answer_contract": self._answer_contract(task, evidence_refs, status),
            "next_action": self._task_next_action(task_id, status),
        }

    @staticmethod
    def _governance_checks(governance: dict, expected_behavior: list[str]) -> list[dict]:
        answer_format = governance.get("answer_format", [])
        kpi_priority = governance.get("kpi_priority", [])
        data_policy = governance.get("data_insufficiency_policy", {})
        terminology = governance.get("terminology_policy", {})
        behavior_text = " ".join(expected_behavior).lower()
        return [
            {
                "check": "answer_format_summary_evidence_action",
                "passed": answer_format == ["management_summary", "reason_and_evidence", "recommended_action"],
            },
            {
                "check": "kpi_priority_delivery_quality_cost",
                "passed": kpi_priority == ["delivery", "quality", "cost"],
            },
            {
                "check": "data_insufficiency_allowed",
                "passed": data_policy.get("allowed") is True,
            },
            {
                "check": "terminology_standard_field_site_term",
                "passed": "standard_field_name (site_term)" in str(terminology.get("format", "")),
            },
            {
                "check": "avoid_overclaiming_or_request_missing_data",
                "passed": any(token in behavior_text for token in ["avoid", "state", "request", "ask", "answer no"]),
            },
        ]

    @staticmethod
    def _score(status: str, resolved: list[str], evidence_refs: list[str], governance_checks: list[dict]) -> float:
        evidence_score = len(resolved) / len(evidence_refs) if evidence_refs else 0
        governance_score = len([item for item in governance_checks if item["passed"]]) / len(governance_checks)
        base = (evidence_score * 0.55) + (governance_score * 0.35)
        if status == "passed":
            base += 0.10
        elif status == "needs_data":
            base += 0.02
        return round(min(base, 1.0), 3)

    @staticmethod
    def _answer_contract(task: dict, evidence_refs: list[str], status: str) -> dict:
        return {
            "management_summary": f"Evaluate {task.get('capability', 'training capability')} for Tianpai general-manager use.",
            "reason_and_evidence": {
                "must_use_evidence_refs": evidence_refs,
                "must_state_data_gap": status == "needs_data",
            },
            "recommended_action": "Use the result as training/evaluation evidence; do not write APS/IOT/Hermes or dispatch service automatically.",
        }

    @staticmethod
    def _task_next_action(task_id: str, status: str) -> str:
        if status == "failed":
            return "Fix missing evidence references or update the training pack before rerunning."
        if task_id in DATA_NEEDED_BY_TASK:
            return DATA_NEEDED_BY_TASK[task_id]
        return "Keep task in the automatic regression set for the next Hermes/Codex loop."

    @staticmethod
    def _summary(pack: dict, results: list[dict], playbook_regression_queue: dict | None = None) -> dict:
        playbook_regression_queue = playbook_regression_queue or {}
        passed = len([item for item in results if item["status"] == "passed"])
        needs_data = len([item for item in results if item["status"] == "needs_data"])
        failed = len([item for item in results if item["status"] == "failed"])
        approved = len([item for item in results if item.get("review", {}).get("review_status") == "approved"])
        needs_changes = len([item for item in results if item.get("review", {}).get("review_status") == "needs_changes"])
        rejected = len([item for item in results if item.get("review", {}).get("review_status") == "rejected"])
        pending_review = len([item for item in results if item.get("review", {}).get("review_status") == "pending_review"])
        human_review_required = len([item for item in results if item.get("human_review_required")])
        registered_data = sum(item.get("data_intake", {}).get("registered_count", 0) for item in results)
        skipped_data = sum(item.get("data_intake", {}).get("skipped_count", 0) for item in results)
        not_available_data = sum(item.get("data_intake", {}).get("not_available_count", 0) for item in results)
        scores = [item["score"] for item in results]
        governance = pack.get("training_governance", {})
        target_persona = governance.get("first_training_persona", {}).get("role", "tianpai_general_manager")
        return {
            "run_id": f"TRAIN-RUN-{TRAINING_VERSION}-TPI-001",
            "tenant_id": pack.get("tenant_id"),
            "factory_id": pack.get("factory_id"),
            "schema_version": pack.get("schema_version"),
            "target_persona": target_persona,
            "automation_state": "auto_training_available",
            "training_type": "automatic_evaluation_loop",
            "model_weight_finetuning": False,
            "real_hermes_connected": False,
            "total_task_count": len(results),
            "auto_evaluated_task_count": len(results),
            "passed_task_count": passed,
            "needs_data_task_count": needs_data,
            "failed_task_count": failed,
            "average_score": round(mean(scores), 3) if scores else 0,
            "progress_percent": round((len(results) / len(results)) * 100, 1) if results else 0,
            "human_review_required_count": human_review_required,
            "pending_review_count": pending_review,
            "approved_review_count": approved,
            "needs_changes_review_count": needs_changes,
            "rejected_review_count": rejected,
            "registered_data_source_count": registered_data,
            "skipped_data_source_count": skipped_data,
            "not_available_data_source_count": not_available_data,
            "playbook_candidate_count": playbook_regression_queue.get("candidate_count", 0),
            "playbook_ready_regression_count": playbook_regression_queue.get("ready_regression_count", 0),
            "playbook_blocked_regression_count": playbook_regression_queue.get("blocked_regression_count", 0),
            "current_boundary": "Local automatic evaluator is active; live Hermes runner and model fine-tuning are not connected.",
        }

    def _stage_progress(self, results: list[dict]) -> list[dict]:
        stages = self.template()["stages"]
        failed = any(item["status"] == "failed" for item in results)
        needs_data = any(item["status"] == "needs_data" for item in results)
        enriched = []
        for stage in stages:
            status = "completed"
            if stage["id"] == "codex_patch_queue" and needs_data:
                status = "needs_data"
            if stage["id"] == "human_gate" and (failed or needs_data):
                status = "human_or_data_review_required"
            enriched.append({**stage, "run_status": status})
        return enriched

    @staticmethod
    def _capability_progress(results: list[dict]) -> list[dict]:
        groups = sorted({item["capability_group"] for item in results})
        progress = []
        for group in groups:
            group_results = [item for item in results if item["capability_group"] == group]
            progress.append(
                {
                    "capability_group": group,
                    "task_count": len(group_results),
                    "passed": len([item for item in group_results if item["status"] == "passed"]),
                    "needs_data": len([item for item in group_results if item["status"] == "needs_data"]),
                    "failed": len([item for item in group_results if item["status"] == "failed"]),
                    "average_score": round(mean(item["score"] for item in group_results), 3),
                }
            )
        return progress

    @staticmethod
    def _hermes_result_payload(pack: dict, results: list[dict], summary: dict, playbook_regression_queue: dict) -> dict:
        return {
            "schema": "hermes.training_result.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": pack.get("tenant_id"),
            "factory_id": pack.get("factory_id"),
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "candidate",
            "run_id": summary["run_id"],
            "version": TRAINING_VERSION,
            "summary": summary,
            "playbook_regression_queue": {
                "schema_id": playbook_regression_queue.get("schema_id"),
                "candidate_count": playbook_regression_queue.get("candidate_count", 0),
                "ready_regression_count": playbook_regression_queue.get("ready_regression_count", 0),
                "blocked_regression_count": playbook_regression_queue.get("blocked_regression_count", 0),
                "ready_case_ids": [
                    item.get("regression_id")
                    for item in playbook_regression_queue.get("regression_candidates", [])
                    if item.get("ready_for_regression")
                ],
            },
            "results": [
                {
                    "task_id": item["task_id"],
                    "capability": item["capability"],
                    "status": item["status"],
                    "score": item["score"],
                    "evidence_refs": item["evaluation_checks"]["resolved_evidence_refs"],
                    "next_action": item["next_action"],
                }
                for item in results
            ],
        }

    @staticmethod
    def _codex_patch_queue(results: list[dict], playbook_regression_queue: dict | None = None) -> list[dict]:
        playbook_regression_queue = playbook_regression_queue or {}
        queue = []
        ready_playbooks = [
            item
            for item in playbook_regression_queue.get("regression_candidates", [])
            if item.get("ready_for_regression")
        ]
        if ready_playbooks:
            queue.append(
                {
                    "queue_id": "CODEX-PLAYBOOK-REGRESSION-001",
                    "type": "playbook_regression_candidate",
                    "priority": "P1",
                    "summary": "Approved Hermes playbook candidates are ready to be converted into local automatic regression tasks.",
                    "related_regression_case_ids": [item.get("regression_id") for item in ready_playbooks],
                    "human_review_required": True,
                }
            )
        if any(item["status"] == "failed" for item in results):
            queue.append(
                {
                    "queue_id": "CODEX-TRAIN-001",
                    "type": "training_pack_fix",
                    "priority": "P0",
                    "summary": "Fix missing evidence references before the next automatic training run.",
                    "human_review_required": False,
                }
            )
        needs_data = [item for item in results if item["status"] == "needs_data"]
        for index, item in enumerate(needs_data, start=1):
            data_intake = item.get("data_intake", {})
            latest_status = data_intake.get("latest_data_status", "not_registered")
            if latest_status == "registered":
                queue_type = "data_ingestion_candidate"
                summary = "Registered data source is ready for schema review and future ingestion; raw file content is not stored in this repo."
            elif latest_status == "skipped_for_now":
                queue_type = "data_skipped_for_now"
                summary = "Data request was skipped for now; keep Athena's answer as a known data-gap explanation."
            elif latest_status == "not_available":
                queue_type = "data_not_available"
                summary = "Data source is marked not available; keep the limitation in future Athena answers."
            else:
                queue_type = "data_request"
                summary = item["next_action"]
            queue.append(
                {
                    "queue_id": f"DATA-TRAIN-{index:03d}",
                    "type": queue_type,
                    "priority": "P1",
                    "summary": summary,
                    "related_task_id": item["task_id"],
                    "human_review_required": True,
                }
            )
        if not queue:
            queue.append(
                {
                    "queue_id": "CODEX-TRAIN-REGRESSION-001",
                    "type": "regression_set",
                    "priority": "P2",
                    "summary": "Keep all passed tasks in the automatic regression set for future Athena changes.",
                    "human_review_required": False,
                }
            )
        return queue

    @staticmethod
    def _next_training_tasks(results: list[dict], playbook_regression_queue: dict | None = None) -> list[dict]:
        playbook_regression_queue = playbook_regression_queue or {}
        next_tasks = [
            {
                "task_id": "TPI-AUTO-REGRESSION-001",
                "capability": "automatic_regression",
                "prompt": "Rerun all passed Tianpai tasks after each Athena production or Hermes update.",
                "source": "demo",
            }
        ]
        for item in results:
            if item["status"] == "needs_data":
                latest_status = item.get("data_intake", {}).get("latest_data_status", "not_registered")
                if latest_status in {"skipped_for_now", "not_available"}:
                    continue
                next_tasks.append(
                    {
                        "task_id": item["task_id"].replace("TPI-", "TPI-DATA-NEXT-"),
                        "capability": item["capability"],
                        "prompt": (
                            "Review registered data source and field notes before ingestion."
                            if latest_status == "registered"
                            else item["next_action"]
                        ),
                        "source": "registered_data" if latest_status == "registered" else "data_gap",
                    }
                )
        for item in playbook_regression_queue.get("regression_candidates", []):
            if not item.get("ready_for_regression"):
                continue
            next_tasks.append(
                {
                    "task_id": item.get("regression_id", ""),
                    "capability": "playbook_regression",
                    "prompt": item.get("prompt_family") or "Rerun approved Hermes playbook pattern as a regression case.",
                    "source": "approved_playbook",
                    "source_playbook_candidate_id": item.get("playbook_candidate_id", ""),
                    "expected_fields": item.get("expected_fields", []),
                }
            )
        return next_tasks

    @staticmethod
    def _evidence_log(pack: dict, results: list[dict], playbook_regression_queue: dict | None = None) -> list[dict]:
        playbook_regression_queue = playbook_regression_queue or {}
        return [
            {
                "evidence_id": "EV-TRAIN-001",
                "source": "docs/training/tianpai_training_pack_v0_1.json",
                "summary": f"Loaded schema {pack.get('schema_version')} with {len(pack.get('candidate_training_tasks', []))} candidate tasks.",
                "status": "available",
            },
            {
                "evidence_id": "EV-TRAIN-002",
                "source": "training_governance",
                "summary": "Tianpai training governance defines persona, answer format, KPI priority, data-insufficiency behavior, terminology, and automation boundary.",
                "status": "available",
            },
            {
                "evidence_id": "EV-TRAIN-003",
                "source": "automatic_evaluator",
                "summary": f"Auto-evaluated {len(results)} tasks and produced Hermes-style JSON without live Hermes writeback.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-004",
                "source": "hermes.organization_memory_playbook",
                "summary": (
                    f"Loaded {playbook_regression_queue.get('candidate_count', 0)} playbook candidates and "
                    f"prepared {playbook_regression_queue.get('ready_regression_count', 0)} approved regression cases."
                ),
                "status": "completed",
            },
        ]

    @staticmethod
    def _kpi_log(results: list[dict], playbook_regression_queue: dict | None = None) -> list[dict]:
        playbook_regression_queue = playbook_regression_queue or {}
        total = len(results)
        passed = len([item for item in results if item["status"] == "passed"])
        needs_data = len([item for item in results if item["status"] == "needs_data"])
        failed = len([item for item in results if item["status"] == "failed"])
        pending_review = len([item for item in results if item.get("review", {}).get("review_status") == "pending_review"])
        human_review_required = len([item for item in results if item.get("human_review_required")])
        approved = len([item for item in results if item.get("review", {}).get("review_status") == "approved"])
        registered_data = sum(item.get("data_intake", {}).get("registered_count", 0) for item in results)
        evidence_ok = len([item for item in results if item["evaluation_checks"]["evidence_resolved"]])
        governance_ok = len([item for item in results if item["evaluation_checks"]["governance_aligned"]])
        average_score = round(mean(item["score"] for item in results), 3) if results else 0
        return [
            {"kpi": "training_task_count", "value": total, "target": ">=1", "status": "ok" if total else "failed"},
            {"kpi": "auto_evaluated_task_count", "value": total, "target": str(total), "status": "ok"},
            {"kpi": "passed_task_count", "value": passed, "target": ">=1", "status": "ok" if passed else "attention"},
            {"kpi": "needs_data_task_count", "value": needs_data, "target": "tracked", "status": "attention" if needs_data else "ok"},
            {"kpi": "failed_task_count", "value": failed, "target": "0", "status": "ok" if failed == 0 else "failed"},
            {"kpi": "average_score", "value": average_score, "target": ">=0.75", "status": "ok" if average_score >= 0.75 else "attention"},
            {"kpi": "evidence_resolution_rate", "value": round(evidence_ok / total, 3) if total else 0, "target": "1.0", "status": "ok" if evidence_ok == total else "failed"},
            {"kpi": "governance_alignment_rate", "value": round(governance_ok / total, 3) if total else 0, "target": "1.0", "status": "ok" if governance_ok == total else "attention"},
            {"kpi": "human_review_required_count", "value": human_review_required, "target": "tracked", "status": "attention" if human_review_required else "ok"},
            {"kpi": "pending_review_count", "value": pending_review, "target": "tracked", "status": "attention" if pending_review else "ok"},
            {"kpi": "approved_review_count", "value": approved, "target": "tracked", "status": "ok"},
            {"kpi": "registered_data_source_count", "value": registered_data, "target": "tracked", "status": "ok" if registered_data else "attention"},
            {"kpi": "playbook_regression_candidate_count", "value": playbook_regression_queue.get("candidate_count", 0), "target": "tracked", "status": "ok"},
            {
                "kpi": "playbook_regression_ready_count",
                "value": playbook_regression_queue.get("ready_regression_count", 0),
                "target": "approved only",
                "status": "ok" if playbook_regression_queue.get("ready_regression_count", 0) else "attention",
            },
        ]

    def _playbook_regression_queue(self) -> dict:
        playbook_payload = self.hermes_workflow.playbook()
        playbook = playbook_payload.get("organization_memory_playbook", {})
        candidates = playbook.get("playbook_candidates", [])
        regression_candidates = [self._playbook_candidate_to_regression(item) for item in candidates]
        ready_count = len([item for item in regression_candidates if item["ready_for_regression"]])
        blocked_count = len(regression_candidates) - ready_count
        queue_status = "ready_for_regression" if ready_count else "blocked_pending_playbook_approval"
        return {
            "schema_id": "athena.playbook_regression_queue.v1",
            "version": TRAINING_VERSION,
            "queue_id": f"TRAIN-PLAYBOOK-REGRESSION-{TRAINING_VERSION}",
            "queue_status": queue_status,
            "adapter_status": "mock_contract",
            "source": "hermes.organization_memory_playbook",
            "source_playbook_engine_id": playbook.get("engine_id"),
            "source_decision_loop_id": playbook.get("source_decision_loop_id"),
            "real_hermes_connected": False,
            "write_actions_blocked": True,
            "candidate_count": len(regression_candidates),
            "ready_regression_count": ready_count,
            "blocked_regression_count": blocked_count,
            "regression_candidates": regression_candidates,
            "blocked_actions": [
                "auto_generate_regression_without_approved_playbook",
                "write_live_hermes_memory",
                "store_raw_customer_data",
                "store_credentials_or_tokens",
                "modify_code_without_codex_review",
                "write_to_aps_or_iot",
            ],
            "next_actions": self._playbook_regression_next_actions(regression_candidates),
        }

    @staticmethod
    def _playbook_candidate_to_regression(candidate: dict) -> dict:
        memory_event = candidate.get("memory_event_candidate", {})
        regression_case = candidate.get("regression_case_candidate", {})
        promotion_status = candidate.get("promotion_status", "candidate")
        ready_for_review = candidate.get("ready_for_playbook_review") is True
        ready_for_regression = ready_for_review and promotion_status == "approved"
        blockers = list(candidate.get("blocked_until", []))
        if not ready_for_review and "closed_follow_up_with_accepted_evidence" not in blockers:
            blockers.append("closed_follow_up_with_accepted_evidence")
        if promotion_status != "approved" and "approved_playbook_candidate" not in blockers:
            blockers.append("approved_playbook_candidate")

        return {
            "regression_id": regression_case.get("case_id") or f"REG-{candidate.get('candidate_id', 'UNKNOWN')}",
            "playbook_candidate_id": candidate.get("candidate_id"),
            "source_follow_up_id": candidate.get("source_follow_up_id"),
            "source_action_id": candidate.get("source_action_id"),
            "promotion_status": promotion_status,
            "review_status": candidate.get("review_status", "not_reviewed"),
            "ready_for_regression": ready_for_regression,
            "blockers": [] if ready_for_regression else blockers,
            "prompt_family": regression_case.get("prompt_family") or candidate.get("management_theme"),
            "trigger_signal": candidate.get("trigger_signal"),
            "recommended_action_pattern": candidate.get("recommended_action_pattern"),
            "owner_role": candidate.get("owner_role"),
            "expected_fields": regression_case.get("expected_fields", []),
            "source_evidence_refs": candidate.get("evidence_refs", []),
            "memory_scope": memory_event.get("scope"),
            "tenant_id": memory_event.get("tenant_id"),
            "factory_id": memory_event.get("factory_id"),
            "source": memory_event.get("source", "demo"),
            "retention_policy": memory_event.get("retention_policy", "review_before_promotion"),
            "sensitivity_level": memory_event.get("sensitivity_level", "internal"),
            "contains_raw_user_message": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _playbook_regression_next_actions(regression_candidates: list[dict]) -> list[str]:
        if not regression_candidates:
            return ["Generate Production decision-loop follow-ups before preparing playbook regression cases."]
        if any(item["ready_for_regression"] for item in regression_candidates):
            return ["Convert approved playbook regression candidates into local automatic regression tasks after Codex review."]
        return ["Close follow-ups with accepted evidence and approve playbook candidates before generating regression cases."]

    @staticmethod
    def _playbook_queue_kpis(queue: dict) -> list[dict]:
        return [
            {"kpi": "playbook_regression_candidate_count", "value": queue.get("candidate_count", 0), "target": "tracked", "status": "ok"},
            {
                "kpi": "playbook_regression_ready_count",
                "value": queue.get("ready_regression_count", 0),
                "target": "approved only",
                "status": "ok" if queue.get("ready_regression_count", 0) else "attention",
            },
            {
                "kpi": "playbook_regression_blocked_count",
                "value": queue.get("blocked_regression_count", 0),
                "target": "tracked",
                "status": "attention" if queue.get("blocked_regression_count", 0) else "ok",
            },
        ]

    @staticmethod
    def _playbook_queue_evidence(queue: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-PLAYBOOK-001",
                "source": queue.get("source", "hermes.organization_memory_playbook"),
                "summary": (
                    f"{queue.get('ready_regression_count', 0)} of {queue.get('candidate_count', 0)} "
                    "playbook candidates are ready for regression."
                ),
                "status": "completed",
            }
        ]

    def _regression_cases(self, result: dict, round_summary: dict, playbook_queue: dict) -> list[dict]:
        tasks_by_id = {item["task_id"]: item for item in result.get("training_tasks", [])}
        cases = []
        for baseline_task in round_summary.get("promoted_tasks", []):
            task = tasks_by_id.get(baseline_task.get("task_id", ""), {})
            checks = self._baseline_regression_checks(task)
            cases.append(
                {
                    "case_id": f"REG-{baseline_task.get('task_id', 'UNKNOWN')}",
                    "source": "training_baseline",
                    "source_task_id": baseline_task.get("task_id"),
                    "capability": baseline_task.get("capability"),
                    "capability_group": baseline_task.get("capability_group"),
                    "baseline_role": baseline_task.get("baseline_role"),
                    "regression_status": "passed" if all(item["passed"] for item in checks) else "failed",
                    "score": task.get("score", baseline_task.get("score", 0)),
                    "checks": checks,
                    "evidence_refs": baseline_task.get("evidence_refs", []),
                    "expected_behavior": task.get("expected_behavior", []),
                    "locked_next_action": baseline_task.get("locked_next_action", ""),
                    "write_actions_blocked": True,
                }
            )

        for playbook_case in playbook_queue.get("regression_candidates", []):
            if playbook_case.get("ready_for_regression"):
                checks = self._playbook_regression_checks(playbook_case)
                cases.append(
                    {
                        "case_id": playbook_case.get("regression_id", ""),
                        "source": "approved_playbook",
                        "source_playbook_candidate_id": playbook_case.get("playbook_candidate_id"),
                        "capability": "playbook_regression",
                        "capability_group": playbook_case.get("prompt_family"),
                        "regression_status": "passed" if all(item["passed"] for item in checks) else "failed",
                        "score": 1.0 if all(item["passed"] for item in checks) else 0.6,
                        "checks": checks,
                        "evidence_refs": playbook_case.get("source_evidence_refs", []),
                        "expected_fields": playbook_case.get("expected_fields", []),
                        "locked_next_action": "Keep approved playbook behavior in the automatic regression set.",
                        "write_actions_blocked": True,
                    }
                )
            else:
                cases.append(
                    {
                        "case_id": playbook_case.get("regression_id", ""),
                        "source": "blocked_playbook_candidate",
                        "source_playbook_candidate_id": playbook_case.get("playbook_candidate_id"),
                        "capability": "playbook_regression",
                        "capability_group": playbook_case.get("prompt_family"),
                        "regression_status": "blocked",
                        "score": 0,
                        "checks": [
                            {"check": "approved_playbook_candidate", "passed": False},
                            {"check": "closed_follow_up_with_accepted_evidence", "passed": False},
                        ],
                        "blockers": playbook_case.get("blockers", []),
                        "evidence_refs": playbook_case.get("source_evidence_refs", []),
                        "locked_next_action": "Approve the evidence-backed playbook candidate before regression execution.",
                        "write_actions_blocked": True,
                    }
                )
        return cases

    @staticmethod
    def _baseline_regression_checks(task: dict) -> list[dict]:
        status = task.get("status", "")
        review_status = task.get("review", {}).get("review_status", "")
        checks = [
            {"check": "current_evaluation_not_failed", "passed": status != "failed"},
            {"check": "review_status_approved", "passed": review_status == "approved"},
            {
                "check": "evidence_refs_resolved",
                "passed": bool(task.get("evaluation_checks", {}).get("resolved_evidence_refs")),
            },
            {
                "check": "governance_alignment_kept",
                "passed": task.get("evaluation_checks", {}).get("governance_aligned") is True,
            },
        ]
        if status == "needs_data":
            latest_data_status = task.get("data_intake", {}).get("latest_data_status", "not_registered")
            checks.append(
                {
                    "check": "known_data_gap_has_reviewed_decision",
                    "passed": latest_data_status in {"registered", "skipped_for_now", "not_available"},
                }
            )
        return checks

    @staticmethod
    def _playbook_regression_checks(playbook_case: dict) -> list[dict]:
        return [
            {"check": "ready_for_regression", "passed": playbook_case.get("ready_for_regression") is True},
            {"check": "approved_playbook_candidate", "passed": playbook_case.get("promotion_status") == "approved"},
            {"check": "evidence_refs_present", "passed": bool(playbook_case.get("source_evidence_refs"))},
            {"check": "expected_fields_present", "passed": bool(playbook_case.get("expected_fields"))},
            {"check": "no_raw_user_message_or_credentials", "passed": not playbook_case.get("contains_credentials") and not playbook_case.get("contains_raw_user_message")},
        ]

    @staticmethod
    def _regression_kpi_log(cases: list[dict]) -> list[dict]:
        executable = [item for item in cases if item["regression_status"] != "blocked"]
        passed = len([item for item in executable if item["regression_status"] == "passed"])
        failed = len([item for item in executable if item["regression_status"] == "failed"])
        blocked = len([item for item in cases if item["regression_status"] == "blocked"])
        pass_rate = round(passed / len(executable), 3) if executable else 0
        return [
            {"kpi": "regression_case_count", "value": len(cases), "target": ">=1", "status": "ok" if cases else "failed"},
            {"kpi": "regression_executable_case_count", "value": len(executable), "target": ">=1", "status": "ok" if executable else "attention"},
            {"kpi": "regression_passed_case_count", "value": passed, "target": "all executable", "status": "ok" if failed == 0 else "failed"},
            {"kpi": "regression_failed_case_count", "value": failed, "target": "0", "status": "ok" if failed == 0 else "failed"},
            {"kpi": "regression_blocked_case_count", "value": blocked, "target": "tracked", "status": "attention" if blocked else "ok"},
            {"kpi": "regression_pass_rate", "value": pass_rate, "target": "1.0", "status": "ok" if executable and pass_rate == 1 else "attention"},
        ]

    @staticmethod
    def _regression_evidence_log(cases: list[dict]) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-REGRESSION-001",
                "source": "training_task_reviews_and_tianpai_training_pack",
                "summary": f"Built {len([item for item in cases if item['source'] == 'training_baseline'])} baseline regression cases from approved training tasks.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-REGRESSION-002",
                "source": "hermes.organization_memory_playbook",
                "summary": f"Tracked {len([item for item in cases if 'playbook' in item['source']])} playbook regression candidates without live Hermes writeback.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _regression_gate_decision(overview: dict, cases: list[dict], threshold: float) -> dict:
        failed_cases = [item for item in cases if item.get("regression_status") == "failed"]
        blocked_cases = [item for item in cases if item.get("regression_status") == "blocked"]
        executable_count = int(overview.get("executable_case_count", 0))
        pass_rate = float(overview.get("pass_rate", 0))

        if executable_count == 0:
            gate_status = "blocked_no_executable_regression"
            automatic_loop_allowed = False
            human_review_required = True
        elif failed_cases or pass_rate < threshold:
            gate_status = "regression_failed_human_review_required"
            automatic_loop_allowed = False
            human_review_required = True
        elif blocked_cases:
            gate_status = "ready_for_next_loop_with_blocked_playbooks"
            automatic_loop_allowed = True
            human_review_required = True
        else:
            gate_status = "ready_for_next_automatic_loop"
            automatic_loop_allowed = True
            human_review_required = False

        review_required = [
            {
                "case_id": item.get("case_id"),
                "source": item.get("source"),
                "status": item.get("regression_status"),
                "reason": item.get("locked_next_action") or ", ".join(item.get("blockers", [])),
            }
            for item in failed_cases + blocked_cases
        ]
        return {
            "schema_id": "athena.regression_gate.v1",
            "version": TRAINING_VERSION,
            "gate_id": f"TRAIN-REGRESSION-GATE-{TRAINING_VERSION}-TPI-001",
            "gate_status": gate_status,
            "pass_rate_threshold": threshold,
            "automatic_loop_allowed": automatic_loop_allowed,
            "codex_patch_allowed": "small_fix_only" if automatic_loop_allowed else "blocked_until_review",
            "human_review_required": human_review_required,
            "failed_case_count": len(failed_cases),
            "blocked_case_count": len(blocked_cases),
            "executable_case_count": executable_count,
            "pass_rate": pass_rate,
            "review_required_items": review_required,
            "decision_rules": [
                "failed executable regression cases block the next Codex/Hermes loop",
                "blocked playbook candidates remain visible but are not executed",
                "small fixes may continue only when executable regression cases pass",
                "large feature changes, new pages, real data integration, and tenant-memory promotion still require user confirmation",
            ],
            "next_loop_contract": {
                "allowed_scope": "local_small_fix_or_next_training_task_preparation" if automatic_loop_allowed else "review_failed_or_blocked_cases",
                "live_hermes_execution": False,
                "code_change_automatic": False,
                "requires_user_confirmation_for_feature_version": True,
            },
            "blocked_actions": [
                "auto_modify_code_from_failed_regression",
                "auto_approve_blocked_playbook",
                "write_live_hermes_memory",
                "write_to_aps_or_iot",
                "run_model_weight_finetuning_from_demo",
                "start_real_data_integration_without_user_confirmation",
            ],
        }

    @staticmethod
    def _regression_gate_codex_queue(gate: dict) -> list[dict]:
        queue = []
        if gate["automatic_loop_allowed"]:
            queue.append(
                {
                    "queue_id": "CODEX-REGRESSION-GATE-001",
                    "type": "continue_next_iteration",
                    "priority": "P2",
                    "summary": "Executable regression cases passed; Codex may prepare the next local small-fix or training-task iteration under the existing automation boundary.",
                    "automation_allowed": True,
                    "human_review_required": False,
                }
            )
        else:
            queue.append(
                {
                    "queue_id": "CODEX-REGRESSION-GATE-REVIEW-001",
                    "type": "regression_review_required",
                    "priority": "P0",
                    "summary": "Executable regression gate is blocked; review failed or missing regression evidence before continuing.",
                    "automation_allowed": False,
                    "human_review_required": True,
                }
            )
        if gate["review_required_items"]:
            queue.append(
                {
                    "queue_id": "HUMAN-REGRESSION-REVIEW-001",
                    "type": "human_review_queue",
                    "priority": "P1",
                    "summary": "Review failed or blocked regression cases; blocked playbook candidates need evidence closure and approval before execution.",
                    "related_case_ids": [item["case_id"] for item in gate["review_required_items"]],
                    "automation_allowed": False,
                    "human_review_required": True,
                }
            )
        return queue

    @staticmethod
    def _regression_gate_hermes_payload(gate: dict, overview: dict) -> dict:
        return {
            "schema": "hermes.regression_gate_feedback.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed",
            "version": TRAINING_VERSION,
            "gate_id": gate["gate_id"],
            "source_regression_run_id": overview.get("run_id"),
            "gate_status": gate["gate_status"],
            "automatic_loop_allowed": gate["automatic_loop_allowed"],
            "summary": {
                "pass_rate": gate["pass_rate"],
                "failed_case_count": gate["failed_case_count"],
                "blocked_case_count": gate["blocked_case_count"],
                "review_required_count": len(gate["review_required_items"]),
            },
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _regression_gate_kpis(gate: dict) -> list[dict]:
        return [
            {"kpi": "regression_gate_allowed", "value": gate["automatic_loop_allowed"], "target": True, "status": "ok" if gate["automatic_loop_allowed"] else "failed"},
            {"kpi": "regression_gate_failed_case_count", "value": gate["failed_case_count"], "target": 0, "status": "ok" if gate["failed_case_count"] == 0 else "failed"},
            {"kpi": "regression_gate_blocked_case_count", "value": gate["blocked_case_count"], "target": "tracked", "status": "attention" if gate["blocked_case_count"] else "ok"},
            {"kpi": "regression_gate_pass_rate", "value": gate["pass_rate"], "target": gate["pass_rate_threshold"], "status": "ok" if gate["pass_rate"] >= gate["pass_rate_threshold"] else "failed"},
        ]

    @staticmethod
    def _regression_gate_evidence(gate: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-GATE-001",
                "source": "athena.automatic_regression_run.v1",
                "summary": f"Regression gate {gate['gate_status']} with pass rate {gate['pass_rate']} and {len(gate['review_required_items'])} review-required cases.",
                "status": "completed",
            }
        ]

    @staticmethod
    def _next_loop_handoff_payload(result: dict, gate_payload: dict, handoff_reviews: dict) -> dict:
        gate = gate_payload["regression_gate"]
        gate_queue = gate_payload.get("codex_next_action_queue", [])
        patch_queue = result.get("codex_patch_queue", [])
        next_tasks = result.get("next_training_tasks", [])
        review_records = handoff_reviews.get("handoff_reviews", {})

        automatic_work_queue = []
        if gate["automatic_loop_allowed"]:
            automatic_work_queue.append(
                {
                    "handoff_item_id": "NEXT-LOOP-AUTO-001",
                    "type": "prepare_next_training_iteration",
                    "priority": "P2",
                    "source": "regression_gate",
                    "summary": "Executable regression cases passed; prepare the next local training iteration under the small-fix automation boundary.",
                    "automation_allowed": True,
                    "code_change_automatic": False,
                    "human_review_required": False,
                }
            )
            automatic_work_queue.extend(
                {
                    "handoff_item_id": f"NEXT-LOOP-TASK-{index:03d}",
                    "type": "next_training_task_seed",
                    "priority": "P2",
                    "source": item.get("source", "demo"),
                    "related_task_id": item.get("task_id"),
                    "summary": item.get("prompt", ""),
                    "automation_allowed": True,
                    "code_change_automatic": False,
                    "human_review_required": False,
                }
                for index, item in enumerate(next_tasks, start=1)
                if item.get("source") == "demo"
            )

        human_review_queue = [
            {
                "handoff_item_id": f"NEXT-LOOP-REVIEW-{index:03d}",
                "type": "regression_case_review",
                "priority": "P1",
                "related_case_id": item.get("case_id"),
                "source": item.get("source"),
                "summary": item.get("reason") or "Review the blocked or failed regression case before execution.",
                "automation_allowed": False,
                "human_review_required": True,
            }
            for index, item in enumerate(gate.get("review_required_items", []), start=1)
        ]
        human_review_queue.extend(
            {
                "handoff_item_id": f"NEXT-LOOP-GATE-{index:03d}",
                "type": item.get("type", "gate_review_required"),
                "priority": item.get("priority", "P1"),
                "source": "regression_gate_codex_queue",
                "summary": item.get("summary", ""),
                "automation_allowed": bool(item.get("automation_allowed", False)),
                "human_review_required": bool(item.get("human_review_required", True)),
            }
            for index, item in enumerate(gate_queue, start=1)
            if item.get("human_review_required")
        )

        data_request_queue = [
            {
                "handoff_item_id": f"NEXT-LOOP-DATA-{index:03d}",
                "type": item.get("type", "data_request"),
                "priority": item.get("priority", "P1"),
                "related_task_id": item.get("related_task_id"),
                "summary": item.get("summary", ""),
                "automation_allowed": False,
                "human_review_required": True,
            }
            for index, item in enumerate(patch_queue, start=1)
            if str(item.get("type", "")).startswith("data_")
        ]

        automatic_work_queue = TrainingAutomationWorkflow._apply_handoff_item_reviews(automatic_work_queue, review_records)
        human_review_queue = TrainingAutomationWorkflow._apply_handoff_item_reviews(human_review_queue, review_records)
        data_request_queue = TrainingAutomationWorkflow._apply_handoff_item_reviews(data_request_queue, review_records)
        review_summary = TrainingAutomationWorkflow._handoff_queue_review_summary(
            automatic_work_queue + human_review_queue + data_request_queue
        )

        if not gate["automatic_loop_allowed"]:
            handoff_status = "blocked_until_review"
        elif human_review_queue or data_request_queue:
            handoff_status = "automatic_small_fix_ready_with_review_items"
        else:
            handoff_status = "automatic_loop_ready"

        return {
            "schema_id": "athena.next_loop_handoff.v1",
            "version": TRAINING_VERSION,
            "handoff_id": f"TRAIN-NEXT-LOOP-{TRAINING_VERSION}-TPI-001",
            "handoff_status": handoff_status,
            "source_gate_id": gate["gate_id"],
            "source_gate_status": gate["gate_status"],
            "automatic_loop_allowed": gate["automatic_loop_allowed"],
            "code_change_automatic": False,
            "real_hermes_connected": False,
            "write_actions_blocked": True,
            "large_change_requires_user_confirmation": True,
            "automatic_work_queue": automatic_work_queue,
            "human_review_queue": human_review_queue,
            "data_request_queue": data_request_queue,
            "queue_summary": {
                "automatic_action_count": len(automatic_work_queue),
                "human_review_count": len(human_review_queue),
                "data_request_count": len(data_request_queue),
                **review_summary,
            },
            "decision_rules": [
                "only automatic work queue items may continue without new user input",
                "automatic work prepares local training tasks only; it does not patch code by itself",
                "human review queue items must be resolved before blocked playbooks become executable regression cases",
                "data request queue records source/status needs only and must not store raw files or credentials",
            ],
            "blocked_actions": [
                "auto_write_code_from_next_loop_handoff",
                "auto_promote_blocked_playbook_to_regression",
                "write_live_hermes_memory",
                "store_raw_training_files",
                "store_credentials_or_tokens",
                "start_real_data_integration_without_user_confirmation",
                "run_model_weight_finetuning_from_demo",
            ],
        }

    @staticmethod
    def _apply_handoff_item_reviews(items: list[dict], review_records: dict) -> list[dict]:
        enriched = []
        for item in items:
            review = review_records.get(item.get("handoff_item_id", ""), {})
            default_status = "pending_handoff_review" if item.get("human_review_required") else "auto_allowed"
            enriched.append(
                {
                    **item,
                    "handoff_review": {
                        "review_status": review.get("review_status", default_status),
                        "review_note": review.get("review_note", ""),
                        "reviewer": review.get("reviewer", ""),
                        "updated_at": review.get("updated_at", ""),
                    },
                }
            )
        return enriched

    @staticmethod
    def _handoff_queue_review_summary(items: list[dict]) -> dict:
        reviews = [item.get("handoff_review", {}) for item in items]
        resolved_statuses = {"approved_for_next_loop", "resolved"}
        return {
            "handoff_review_count": len([item for item in reviews if item.get("reviewer")]),
            "handoff_resolved_count": len([item for item in reviews if item.get("review_status") in resolved_statuses]),
            "handoff_deferred_count": len([item for item in reviews if item.get("review_status") == "deferred"]),
            "handoff_needs_data_count": len([item for item in reviews if item.get("review_status") == "needs_data"]),
            "handoff_rejected_count": len([item for item in reviews if item.get("review_status") == "rejected"]),
        }

    @staticmethod
    def _handoff_review_state(store: dict) -> dict:
        reviews = list(store.get("handoff_reviews", {}).values())
        return {
            "schema_id": "athena.next_loop_handoff_review_state.v1",
            "version": store.get("version", TRAINING_VERSION),
            "updated_at": store.get("updated_at", ""),
            "review_count": len(reviews),
            "approved_for_next_loop_count": len([item for item in reviews if item.get("review_status") == "approved_for_next_loop"]),
            "resolved_count": len([item for item in reviews if item.get("review_status") == "resolved"]),
            "deferred_count": len([item for item in reviews if item.get("review_status") == "deferred"]),
            "needs_data_count": len([item for item in reviews if item.get("review_status") == "needs_data"]),
            "rejected_count": len([item for item in reviews if item.get("review_status") == "rejected"]),
            "note_count": len([item for item in reviews if item.get("review_status") == "note_only"]),
            "handoff_reviews": store.get("handoff_reviews", {}),
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _next_loop_hermes_payload(handoff: dict) -> dict:
        return {
            "schema": "hermes.next_loop_handoff.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed",
            "version": TRAINING_VERSION,
            "handoff_id": handoff["handoff_id"],
            "source_gate_id": handoff["source_gate_id"],
            "handoff_status": handoff["handoff_status"],
            "automatic_loop_allowed": handoff["automatic_loop_allowed"],
            "queue_summary": handoff["queue_summary"],
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _next_loop_kpis(handoff: dict) -> list[dict]:
        summary = handoff["queue_summary"]
        return [
            {"kpi": "next_loop_allowed", "value": handoff["automatic_loop_allowed"], "target": True, "status": "ok" if handoff["automatic_loop_allowed"] else "failed"},
            {"kpi": "next_loop_automatic_action_count", "value": summary["automatic_action_count"], "target": "tracked", "status": "ok" if summary["automatic_action_count"] else "attention"},
            {"kpi": "next_loop_human_review_count", "value": summary["human_review_count"], "target": "tracked", "status": "attention" if summary["human_review_count"] else "ok"},
            {"kpi": "next_loop_data_request_count", "value": summary["data_request_count"], "target": "tracked", "status": "attention" if summary["data_request_count"] else "ok"},
            {"kpi": "next_loop_handoff_review_count", "value": summary["handoff_review_count"], "target": "tracked", "status": "ok" if summary["handoff_review_count"] else "attention"},
        ]

    @staticmethod
    def _next_loop_evidence(handoff: dict) -> list[dict]:
        summary = handoff["queue_summary"]
        return [
            {
                "evidence_id": "EV-TRAIN-HANDOFF-001",
                "source": "athena.regression_gate.v1",
                "summary": f"Next-loop handoff uses gate {handoff['source_gate_status']} from {handoff['source_gate_id']}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-HANDOFF-002",
                "source": "training_console_queue_split",
                "summary": f"Prepared {summary['automatic_action_count']} automatic, {summary['human_review_count']} human-review, and {summary['data_request_count']} data-request handoff items.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-HANDOFF-003",
                "source": "training_task_reviews.handoff_reviews",
                "summary": f"Loaded {summary['handoff_review_count']} metadata-only handoff review decisions without executing blocked work.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _next_loop_closure_decision(handoff: dict) -> dict:
        automatic_items = handoff.get("automatic_work_queue", [])
        review_items = handoff.get("human_review_queue", [])
        data_items = handoff.get("data_request_queue", [])
        controlled_items = review_items + data_items
        resolved_statuses = {"approved_for_next_loop", "resolved"}
        open_statuses = {"pending_handoff_review", "needs_data", "deferred", "note_only"}

        rejected_items = [
            item for item in controlled_items if item.get("handoff_review", {}).get("review_status") == "rejected"
        ]
        unresolved_items = [
            item
            for item in controlled_items
            if item.get("handoff_review", {}).get("review_status", "pending_handoff_review") in open_statuses
        ]
        resolved_items = [
            item for item in controlled_items if item.get("handoff_review", {}).get("review_status") in resolved_statuses
        ]

        if not handoff.get("automatic_loop_allowed"):
            closure_status = "blocked_by_regression_gate"
            local_iteration_allowed = False
            closure_complete = False
        elif rejected_items:
            closure_status = "blocked_by_rejected_handoff_item"
            local_iteration_allowed = False
            closure_complete = False
        elif unresolved_items:
            closure_status = "ready_for_local_iteration_with_open_handoff_items"
            local_iteration_allowed = True
            closure_complete = False
        else:
            closure_status = "ready_for_local_iteration"
            local_iteration_allowed = True
            closure_complete = True

        return {
            "schema_id": "athena.next_loop_closure_gate.v1",
            "version": TRAINING_VERSION,
            "closure_id": f"TRAIN-NEXT-LOOP-CLOSURE-{TRAINING_VERSION}-TPI-001",
            "source_handoff_id": handoff.get("handoff_id"),
            "source_handoff_status": handoff.get("handoff_status"),
            "closure_status": closure_status,
            "closure_complete": closure_complete,
            "local_iteration_allowed": local_iteration_allowed,
            "code_change_automatic": False,
            "live_hermes_execution": False,
            "real_data_integration_allowed": False,
            "automatic_action_count": len(automatic_items),
            "resolved_item_count": len(resolved_items),
            "open_item_count": len(unresolved_items),
            "rejected_item_count": len(rejected_items),
            "open_items": TrainingAutomationWorkflow._closure_item_refs(unresolved_items),
            "rejected_items": TrainingAutomationWorkflow._closure_item_refs(rejected_items),
            "local_iteration_plan": {
                "plan_id": f"TRAIN-LOCAL-ITERATION-{TRAINING_VERSION}-TPI-001",
                "allowed": local_iteration_allowed,
                "scope": "local_training_task_preparation_only" if local_iteration_allowed else "review_or_fix_blocking_handoff_items",
                "automatic_items": TrainingAutomationWorkflow._closure_item_refs(automatic_items),
                "must_keep_visible": TrainingAutomationWorkflow._closure_item_refs(unresolved_items + rejected_items),
            },
            "decision_rules": [
                "rejected handoff review items block the local next-loop closure",
                "pending, deferred, needs-data, and note-only handoff items remain visible as open work",
                "open handoff items do not disappear when local small-fix iteration is allowed",
                "closure gate never writes code, live Hermes memory, APS, IOT, or raw training files",
            ],
            "blocked_actions": [
                "auto_execute_local_iteration_plan",
                "auto_write_code_from_closure_gate",
                "write_live_hermes_memory",
                "auto_resolve_open_handoff_items",
                "store_raw_training_files",
                "store_credentials_or_tokens",
                "start_real_data_integration_without_user_confirmation",
            ],
        }

    @staticmethod
    def _closure_item_refs(items: list[dict]) -> list[dict]:
        return [
            {
                "handoff_item_id": item.get("handoff_item_id"),
                "type": item.get("type"),
                "priority": item.get("priority"),
                "source": item.get("source"),
                "related_case_id": item.get("related_case_id", ""),
                "related_task_id": item.get("related_task_id", ""),
                "review_status": item.get("handoff_review", {}).get("review_status", ""),
                "summary": item.get("summary", ""),
            }
            for item in items
        ]

    @staticmethod
    def _next_loop_closure_hermes_payload(closure: dict) -> dict:
        return {
            "schema": "hermes.next_loop_closure_gate.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed",
            "version": TRAINING_VERSION,
            "closure_id": closure["closure_id"],
            "source_handoff_id": closure["source_handoff_id"],
            "closure_status": closure["closure_status"],
            "local_iteration_allowed": closure["local_iteration_allowed"],
            "open_item_count": closure["open_item_count"],
            "rejected_item_count": closure["rejected_item_count"],
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _next_loop_closure_kpis(closure: dict) -> list[dict]:
        return [
            {"kpi": "next_loop_closure_ready", "value": closure["local_iteration_allowed"], "target": True, "status": "ok" if closure["local_iteration_allowed"] else "failed"},
            {"kpi": "next_loop_closure_complete", "value": closure["closure_complete"], "target": True, "status": "ok" if closure["closure_complete"] else "attention"},
            {"kpi": "next_loop_closure_open_item_count", "value": closure["open_item_count"], "target": 0, "status": "attention" if closure["open_item_count"] else "ok"},
            {"kpi": "next_loop_closure_rejected_item_count", "value": closure["rejected_item_count"], "target": 0, "status": "failed" if closure["rejected_item_count"] else "ok"},
        ]

    @staticmethod
    def _next_loop_closure_evidence(closure: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CLOSURE-001",
                "source": "athena.next_loop_handoff.v1",
                "summary": f"Closure gate evaluated {closure['source_handoff_id']} as {closure['closure_status']}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CLOSURE-002",
                "source": "athena.next_loop_handoff_review_state.v1",
                "summary": f"Closure has {closure['open_item_count']} open and {closure['rejected_item_count']} rejected handoff items.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _training_iteration_proposal(closure: dict) -> dict:
        plan = closure.get("local_iteration_plan", {})
        automatic_items = plan.get("automatic_items", [])
        watchlist = closure.get("open_items", []) + closure.get("rejected_items", [])
        task_seed_queue = [
            {
                "proposal_item_id": f"ITER-SEED-{index:03d}",
                "source_handoff_item_id": item.get("handoff_item_id"),
                "type": "local_training_iteration_seed",
                "priority": item.get("priority", "P2"),
                "source": item.get("source", "closure_gate"),
                "summary": item.get("summary", ""),
                "automation_allowed": bool(closure.get("local_iteration_allowed")),
                "code_change_automatic": False,
                "human_review_required": False,
            }
            for index, item in enumerate(automatic_items, start=1)
        ]

        if not closure.get("local_iteration_allowed"):
            proposal_status = "blocked_until_closure_review"
        elif watchlist:
            proposal_status = "proposal_ready_with_open_items"
        else:
            proposal_status = "proposal_ready"

        return {
            "schema_id": "athena.training_iteration_proposal.v1",
            "version": TRAINING_VERSION,
            "proposal_id": f"TRAIN-ITERATION-PROPOSAL-{TRAINING_VERSION}-TPI-001",
            "source_closure_id": closure.get("closure_id"),
            "source_closure_status": closure.get("closure_status"),
            "proposal_status": proposal_status,
            "proposal_ready": bool(closure.get("local_iteration_allowed")),
            "closure_complete": bool(closure.get("closure_complete")),
            "task_seed_count": len(task_seed_queue),
            "open_watch_item_count": len(watchlist),
            "rejected_item_count": int(closure.get("rejected_item_count", 0)),
            "task_seed_queue": task_seed_queue,
            "open_item_watchlist": watchlist,
            "next_iteration_contract": {
                "scope": "local_training_preparation_only" if closure.get("local_iteration_allowed") else "closure_review_required",
                "live_hermes_execution": False,
                "code_change_automatic": False,
                "real_data_integration": False,
                "requires_user_confirmation_for_large_change": True,
                "requires_user_confirmation_for_real_data": True,
            },
            "user_confirmation_required_for": [
                "large feature changes",
                "new pages",
                "real Hermes runner execution",
                "real APS/IOT/ERP data integration",
                "automatic code modification",
                "tenant memory promotion",
            ],
            "decision_rules": [
                "proposal_ready means Athena may prepare local training tasks only",
                "open handoff watchlist items stay visible and do not block local preparation unless rejected",
                "rejected or closure-blocked items require review before proposal execution",
                "the proposal never applies code changes, writes Hermes memory, or stores raw files",
            ],
            "blocked_actions": [
                "auto_execute_training_iteration_proposal",
                "auto_write_code_from_iteration_proposal",
                "write_live_hermes_memory",
                "store_raw_training_files",
                "store_credentials_or_tokens",
                "start_real_data_integration_without_user_confirmation",
                "promote_tenant_memory_without_review",
            ],
        }

    @staticmethod
    def _apply_iteration_proposal_review(proposal: dict, review_state: dict) -> dict:
        review = review_state.get("iteration_proposal_reviews", {}).get(proposal.get("proposal_id", ""), {})
        review_status = review.get("review_status", "pending_proposal_review")
        approved_for_codex_queue = review_status == "approved_for_codex_queue" and proposal.get("proposal_ready")
        return {
            **proposal,
            "proposal_review": {
                "review_status": review_status,
                "review_note": review.get("review_note", ""),
                "reviewer": review.get("reviewer", ""),
                "updated_at": review.get("updated_at", ""),
            },
            "approved_for_codex_queue": approved_for_codex_queue,
            "codex_queue_allowed": approved_for_codex_queue,
        }

    @staticmethod
    def _iteration_proposal_review_state(store: dict) -> dict:
        reviews = list(store.get("iteration_proposal_reviews", {}).values())
        return {
            "schema_id": "athena.training_iteration_proposal_review_state.v1",
            "version": store.get("version", TRAINING_VERSION),
            "updated_at": store.get("updated_at", ""),
            "review_count": len(reviews),
            "approved_for_codex_queue_count": len([item for item in reviews if item.get("review_status") == "approved_for_codex_queue"]),
            "needs_changes_count": len([item for item in reviews if item.get("review_status") == "needs_changes"]),
            "deferred_count": len([item for item in reviews if item.get("review_status") == "deferred"]),
            "rejected_count": len([item for item in reviews if item.get("review_status") == "rejected"]),
            "note_count": len([item for item in reviews if item.get("review_status") == "note_only"]),
            "iteration_proposal_reviews": store.get("iteration_proposal_reviews", {}),
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _training_iteration_hermes_payload(proposal: dict) -> dict:
        return {
            "schema": "hermes.training_iteration_proposal.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed",
            "version": TRAINING_VERSION,
            "proposal_id": proposal["proposal_id"],
            "source_closure_id": proposal["source_closure_id"],
            "proposal_status": proposal["proposal_status"],
            "proposal_ready": proposal["proposal_ready"],
            "approved_for_codex_queue": proposal.get("approved_for_codex_queue", False),
            "task_seed_count": proposal["task_seed_count"],
            "open_watch_item_count": proposal["open_watch_item_count"],
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _training_iteration_kpis(proposal: dict) -> list[dict]:
        return [
            {"kpi": "training_iteration_proposal_ready", "value": proposal["proposal_ready"], "target": True, "status": "ok" if proposal["proposal_ready"] else "failed"},
            {"kpi": "training_iteration_proposal_approved", "value": proposal.get("approved_for_codex_queue", False), "target": "reviewed", "status": "ok" if proposal.get("approved_for_codex_queue") else "attention"},
            {"kpi": "training_iteration_task_seed_count", "value": proposal["task_seed_count"], "target": "tracked", "status": "ok" if proposal["task_seed_count"] else "attention"},
            {"kpi": "training_iteration_open_watch_item_count", "value": proposal["open_watch_item_count"], "target": "tracked", "status": "attention" if proposal["open_watch_item_count"] else "ok"},
        ]

    @staticmethod
    def _training_iteration_evidence(proposal: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-ITERATION-001",
                "source": "athena.next_loop_closure_gate.v1",
                "summary": f"Prepared iteration proposal {proposal['proposal_status']} from closure {proposal['source_closure_id']}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-ITERATION-002",
                "source": "training_iteration_proposal_guardrail",
                "summary": "Proposal is read-only local training preparation and blocks code, live Hermes, raw-file, credential, and real-data writes.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-ITERATION-003",
                "source": "training_task_reviews.iteration_proposal_reviews",
                "summary": f"Proposal review status is {proposal.get('proposal_review', {}).get('review_status', 'pending_proposal_review')}; approval still does not execute code automatically.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _codex_work_packet_queue(proposal: dict) -> dict:
        review_status = proposal.get("proposal_review", {}).get("review_status", "pending_proposal_review")
        seeds = proposal.get("task_seed_queue", [])
        approved = bool(proposal.get("approved_for_codex_queue")) and bool(proposal.get("proposal_ready"))

        if approved and seeds:
            queue_status = "ready_for_codex_worktree_preparation"
        elif approved:
            queue_status = "ready_but_no_task_seeds"
        elif review_status == "needs_changes":
            queue_status = "blocked_proposal_needs_changes"
        elif review_status == "rejected":
            queue_status = "blocked_proposal_rejected"
        elif review_status == "deferred":
            queue_status = "deferred_by_proposal_review"
        else:
            queue_status = "blocked_until_proposal_review"

        queue_ready = queue_status == "ready_for_codex_worktree_preparation"
        packet_blocked_actions = [
            "auto_execute_codex_work_packet",
            "auto_create_branch_or_commit_from_work_packet",
            "write_live_hermes_memory",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        work_packets = [
            {
                "packet_id": f"CODEX-WORK-PACKET-{TRAINING_VERSION}-{index:03d}",
                "source_proposal_id": proposal.get("proposal_id"),
                "source_seed_id": seed.get("proposal_item_id"),
                "title": "Prepare local Athena training iteration seed",
                "summary": seed.get("summary", ""),
                "priority": seed.get("priority", "P2"),
                "scope": "local_training_task_preparation_only",
                "execution_status": "not_started",
                "queue_status": "codex_work_packet",
                "automation_allowed": False,
                "requires_human_approval_before_execution": True,
                "code_change_automatic": False,
                "real_hermes_execution": False,
                "real_data_integration": False,
                "required_validation": [
                    "python -m compileall src scripts tests",
                    "tests/test_main_agent.py harness",
                ],
                "blocked_actions": packet_blocked_actions,
            }
            for index, seed in enumerate(seeds, start=1)
            if queue_ready
        ]

        return {
            "schema_id": "athena.codex_work_packet_queue.v1",
            "version": TRAINING_VERSION,
            "queue_id": f"CODEX-WORK-PACKET-QUEUE-{TRAINING_VERSION}-TPI-001",
            "source_proposal_id": proposal.get("proposal_id"),
            "source_proposal_status": proposal.get("proposal_status"),
            "source_proposal_review_status": review_status,
            "queue_status": queue_status,
            "queue_ready": queue_ready,
            "packet_count": len(work_packets),
            "work_packets": work_packets,
            "open_item_watchlist": proposal.get("open_item_watchlist", []),
            "decision_rules": [
                "only approved_for_codex_queue proposals can prepare Codex work packets",
                "work packets are task drafts and never execute code automatically",
                "large feature changes, new pages, real Hermes runner jobs, and real APS/IOT/ERP integrations still require user confirmation",
                "all packet execution must preserve validation evidence before any future promotion",
            ],
            "blocked_actions": packet_blocked_actions,
        }

    @staticmethod
    def _codex_work_packet_hermes_payload(queue: dict) -> dict:
        return {
            "schema": "hermes.codex_work_packet_queue.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if queue.get("queue_ready") else "candidate",
            "version": TRAINING_VERSION,
            "queue_id": queue["queue_id"],
            "source_proposal_id": queue.get("source_proposal_id"),
            "source_proposal_review_status": queue.get("source_proposal_review_status"),
            "queue_status": queue.get("queue_status"),
            "queue_ready": queue.get("queue_ready"),
            "packet_count": queue.get("packet_count", 0),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_work_packet_kpis(queue: dict) -> list[dict]:
        return [
            {"kpi": "codex_work_packet_queue_ready", "value": queue["queue_ready"], "target": True, "status": "ok" if queue["queue_ready"] else "attention"},
            {"kpi": "codex_work_packet_count", "value": queue["packet_count"], "target": "tracked", "status": "ok" if queue["packet_count"] else "attention"},
        ]

    @staticmethod
    def _codex_work_packet_evidence(queue: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-WORK-PACKET-001",
                "source": "athena.training_iteration_proposal.v1",
                "summary": f"Prepared work packet queue {queue['queue_status']} from proposal {queue.get('source_proposal_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-WORK-PACKET-002",
                "source": "codex_work_packet_guardrail",
                "summary": "Queue is read-only and blocks automatic code execution, branch creation, live Hermes writes, raw-file storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _codex_patch_queue_contract(work_packet_queue: dict, training_signal_queue: list[dict]) -> dict:
        source_status = work_packet_queue.get("queue_status", "blocked_until_proposal_review")
        work_packets = work_packet_queue.get("work_packets", [])

        if work_packet_queue.get("queue_ready") and work_packets:
            queue_status = "ready_for_codex_patch_review"
        elif source_status == "ready_but_no_task_seeds":
            queue_status = "blocked_no_work_packets"
        elif source_status == "blocked_proposal_needs_changes":
            queue_status = "blocked_patch_proposal_needs_changes"
        elif source_status == "blocked_proposal_rejected":
            queue_status = "blocked_patch_proposal_rejected"
        elif source_status == "deferred_by_proposal_review":
            queue_status = "deferred_by_work_packet_review"
        else:
            queue_status = "blocked_until_codex_work_packet_queue_ready"

        queue_ready = queue_status == "ready_for_codex_patch_review"
        blocked_actions = [
            "auto_apply_codex_patch",
            "auto_create_branch_or_commit_from_patch_queue",
            "auto_push_or_open_pr_from_patch_queue",
            "write_live_hermes_memory",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        patch_candidates = [
            {
                "candidate_id": f"CODEX-PATCH-CANDIDATE-{TRAINING_VERSION}-{index:03d}",
                "source_packet_id": packet.get("packet_id"),
                "source_proposal_id": packet.get("source_proposal_id"),
                "type": "local_codex_patch_candidate",
                "priority": packet.get("priority", "P2"),
                "title": "Prepare patch plan for Athena local training iteration",
                "summary": packet.get("summary", ""),
                "change_scope": "local_training_iteration_preparation",
                "execution_status": "not_started",
                "human_review_required": True,
                "code_change_automatic": False,
                "branch_creation_automatic": False,
                "commit_automatic": False,
                "real_hermes_execution": False,
                "real_data_integration": False,
                "required_validation": packet.get("required_validation", []),
                "blocked_actions": blocked_actions,
            }
            for index, packet in enumerate(work_packets, start=1)
            if queue_ready
        ]
        return {
            "schema_id": "athena.codex_patch_queue_contract.v1",
            "version": TRAINING_VERSION,
            "queue_id": f"CODEX-PATCH-QUEUE-{TRAINING_VERSION}-TPI-001",
            "source_work_packet_queue_id": work_packet_queue.get("queue_id"),
            "source_work_packet_queue_status": source_status,
            "queue_status": queue_status,
            "queue_ready": queue_ready,
            "patch_candidate_count": len(patch_candidates),
            "training_signal_count": len(training_signal_queue),
            "patch_candidates": patch_candidates,
            "training_signal_queue": training_signal_queue,
            "decision_rules": [
                "only ready Codex work packets can become patch candidates",
                "patch candidates are preparation records and never apply code automatically",
                "branch creation, commits, pushes, PRs, live Hermes writes, and real data integration require explicit user confirmation",
                "each candidate must keep compileall and harness validation evidence before future promotion",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _codex_patch_queue_hermes_payload(queue: dict) -> dict:
        return {
            "schema": "hermes.codex_patch_queue_contract.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if queue.get("queue_ready") else "candidate",
            "version": TRAINING_VERSION,
            "queue_id": queue["queue_id"],
            "source_work_packet_queue_id": queue.get("source_work_packet_queue_id"),
            "source_work_packet_queue_status": queue.get("source_work_packet_queue_status"),
            "queue_status": queue.get("queue_status"),
            "queue_ready": queue.get("queue_ready"),
            "patch_candidate_count": queue.get("patch_candidate_count", 0),
            "training_signal_count": queue.get("training_signal_count", 0),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_patch_queue_kpis(queue: dict) -> list[dict]:
        return [
            {"kpi": "codex_patch_queue_ready", "value": queue["queue_ready"], "target": True, "status": "ok" if queue["queue_ready"] else "attention"},
            {"kpi": "codex_patch_candidate_count", "value": queue["patch_candidate_count"], "target": "tracked", "status": "ok" if queue["patch_candidate_count"] else "attention"},
            {"kpi": "codex_patch_training_signal_count", "value": queue["training_signal_count"], "target": "tracked", "status": "ok"},
        ]

    @staticmethod
    def _codex_patch_queue_evidence(queue: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PATCH-QUEUE-001",
                "source": "athena.codex_work_packet_queue.v1",
                "summary": f"Prepared patch queue {queue['queue_status']} from work packet queue {queue.get('source_work_packet_queue_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PATCH-QUEUE-002",
                "source": "codex_patch_queue_guardrail",
                "summary": "Patch queue is read-only and blocks automatic code application, branch creation, commits, pushes, PRs, live Hermes writes, raw-file storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _codex_execution_gate(patch_queue: dict) -> dict:
        source_status = patch_queue.get("queue_status", "blocked_until_codex_patch_queue_ready")
        patch_candidates = patch_queue.get("patch_candidates", [])

        if patch_queue.get("queue_ready") and patch_candidates:
            gate_status = "ready_for_human_execution_review"
        elif source_status == "blocked_no_work_packets":
            gate_status = "blocked_no_patch_candidates"
        elif source_status == "blocked_patch_proposal_needs_changes":
            gate_status = "blocked_execution_proposal_needs_changes"
        elif source_status == "blocked_patch_proposal_rejected":
            gate_status = "blocked_execution_proposal_rejected"
        elif source_status == "deferred_by_work_packet_review":
            gate_status = "deferred_by_patch_queue"
        else:
            gate_status = "blocked_until_codex_patch_queue_ready"

        gate_ready = gate_status == "ready_for_human_execution_review"
        blocked_actions = [
            "auto_execute_codex_patch",
            "auto_create_branch_or_commit_from_execution_gate",
            "auto_push_or_open_pr_from_execution_gate",
            "write_live_hermes_memory",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        execution_candidates = [
            {
                "execution_candidate_id": f"CODEX-EXECUTION-CANDIDATE-{TRAINING_VERSION}-{index:03d}",
                "source_patch_candidate_id": candidate.get("candidate_id"),
                "source_packet_id": candidate.get("source_packet_id"),
                "type": "human_reviewed_small_fix_candidate",
                "priority": candidate.get("priority", "P2"),
                "summary": candidate.get("summary", ""),
                "approval_status": "pending_human_confirmation",
                "execution_status": "blocked_until_user_confirmation",
                "automatic_execution_allowed": False,
                "human_confirmation_required": True,
                "branch_creation_automatic": False,
                "commit_automatic": False,
                "real_hermes_execution": False,
                "real_data_integration": False,
                "required_validation": candidate.get("required_validation", []),
                "allowed_future_actions_after_confirmation": [
                    "prepare_codex_worktree",
                    "apply_small_patch",
                    "run_compileall_and_harness",
                    "return_patch_result_for_review",
                ],
                "blocked_actions": blocked_actions,
            }
            for index, candidate in enumerate(patch_candidates, start=1)
            if gate_ready
        ]

        return {
            "schema_id": "athena.codex_execution_gate.v1",
            "version": TRAINING_VERSION,
            "gate_id": f"CODEX-EXECUTION-GATE-{TRAINING_VERSION}-TPI-001",
            "source_patch_queue_id": patch_queue.get("queue_id"),
            "source_patch_queue_status": source_status,
            "gate_status": gate_status,
            "gate_ready": gate_ready,
            "automatic_execution_allowed": False,
            "human_confirmation_required": bool(execution_candidates),
            "execution_candidate_count": len(execution_candidates),
            "execution_candidates": execution_candidates,
            "decision_rules": [
                "ready patch candidates may only become pending human execution candidates",
                "no code execution, branch creation, commit, push, PR, live Hermes write, or real data integration is automatic",
                "future small-fix execution must be explicitly confirmed and followed by compileall plus harness validation",
                "large feature changes, new pages, real data integration, and live Hermes runner changes still require user confirmation before worktree execution",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _codex_execution_gate_hermes_payload(gate: dict) -> dict:
        review_summary = gate.get("execution_review_summary", {})
        return {
            "schema": "hermes.codex_execution_gate.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if gate.get("gate_ready") else "candidate",
            "version": TRAINING_VERSION,
            "gate_id": gate["gate_id"],
            "source_patch_queue_id": gate.get("source_patch_queue_id"),
            "source_patch_queue_status": gate.get("source_patch_queue_status"),
            "gate_status": gate.get("gate_status"),
            "gate_ready": gate.get("gate_ready"),
            "automatic_execution_allowed": gate.get("automatic_execution_allowed"),
            "human_confirmation_required": gate.get("human_confirmation_required"),
            "execution_candidate_count": gate.get("execution_candidate_count", 0),
            "execution_review_count": review_summary.get("review_count", 0),
            "worktree_preparation_allowed_count": review_summary.get("worktree_preparation_allowed_count", 0),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_execution_gate_kpis(gate: dict) -> list[dict]:
        review_summary = gate.get("execution_review_summary", {})
        return [
            {"kpi": "codex_execution_gate_ready", "value": gate["gate_ready"], "target": True, "status": "ok" if gate["gate_ready"] else "attention"},
            {"kpi": "codex_execution_candidate_count", "value": gate["execution_candidate_count"], "target": "tracked", "status": "ok" if gate["execution_candidate_count"] else "attention"},
            {"kpi": "codex_automatic_execution_allowed", "value": gate["automatic_execution_allowed"], "target": False, "status": "ok" if gate["automatic_execution_allowed"] is False else "failed"},
            {"kpi": "codex_execution_review_count", "value": review_summary.get("review_count", 0), "target": "tracked", "status": "ok"},
            {"kpi": "codex_worktree_preparation_approved_count", "value": review_summary.get("worktree_preparation_allowed_count", 0), "target": "tracked", "status": "ok"},
        ]

    @staticmethod
    def _codex_execution_gate_evidence(gate: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-EXECUTION-GATE-001",
                "source": "athena.codex_patch_queue_contract.v1",
                "summary": f"Evaluated execution gate {gate['gate_status']} from patch queue {gate.get('source_patch_queue_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-EXECUTION-GATE-002",
                "source": "codex_execution_gate_guardrail",
                "summary": "Execution gate blocks automatic code execution, branch creation, commits, pushes, PRs, live Hermes writes, raw-file storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _apply_codex_execution_reviews(gate: dict, review_state: dict) -> dict:
        records = review_state.get("codex_execution_reviews", {})
        reviewed_candidates = []
        allowed_count = 0
        for candidate in gate.get("execution_candidates", []):
            review = records.get(candidate.get("execution_candidate_id", ""), {})
            review_status = review.get("review_status", "pending_execution_review")
            worktree_allowed = review_status == "approved_for_worktree_preparation" and gate.get("gate_ready")
            if worktree_allowed:
                allowed_count += 1
            reviewed_candidates.append(
                {
                    **candidate,
                    "execution_review": {
                        "review_status": review_status,
                        "review_note": review.get("review_note", ""),
                        "reviewer": review.get("reviewer", ""),
                        "updated_at": review.get("updated_at", ""),
                    },
                    "worktree_preparation_allowed": worktree_allowed,
                    "worktree_preparation_status": "approved_pending_user_execution_command" if worktree_allowed else "blocked_until_execution_review",
                }
            )
        return {
            **gate,
            "execution_candidates": reviewed_candidates,
            "execution_review_summary": {
                "schema_id": review_state.get("schema_id", "athena.codex_execution_review_state.v1"),
                "review_count": review_state.get("review_count", 0),
                "approved_for_worktree_preparation_count": review_state.get("approved_for_worktree_preparation_count", 0),
                "needs_changes_count": review_state.get("needs_changes_count", 0),
                "deferred_count": review_state.get("deferred_count", 0),
                "rejected_count": review_state.get("rejected_count", 0),
                "worktree_preparation_allowed_count": allowed_count,
            },
        }

    @staticmethod
    def _codex_execution_review_state(store: dict) -> dict:
        reviews = list(store.get("codex_execution_reviews", {}).values())
        return {
            "schema_id": "athena.codex_execution_review_state.v1",
            "version": store.get("version", TRAINING_VERSION),
            "updated_at": store.get("updated_at", ""),
            "review_count": len(reviews),
            "approved_for_worktree_preparation_count": len([item for item in reviews if item.get("review_status") == "approved_for_worktree_preparation"]),
            "needs_changes_count": len([item for item in reviews if item.get("review_status") == "needs_changes"]),
            "deferred_count": len([item for item in reviews if item.get("review_status") == "deferred"]),
            "rejected_count": len([item for item in reviews if item.get("review_status") == "rejected"]),
            "note_count": len([item for item in reviews if item.get("review_status") == "note_only"]),
            "codex_execution_reviews": store.get("codex_execution_reviews", {}),
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _codex_worktree_preparation_queue(gate: dict) -> dict:
        gate_status = gate.get("gate_status", "blocked_until_codex_execution_gate_ready")
        approved_candidates = [
            item
            for item in gate.get("execution_candidates", [])
            if item.get("worktree_preparation_allowed")
        ]
        if approved_candidates:
            queue_status = "ready_for_codex_worktree_preparation"
        elif gate.get("gate_ready"):
            queue_status = "blocked_until_execution_review_approval"
        elif gate_status == "blocked_execution_proposal_needs_changes":
            queue_status = "blocked_worktree_proposal_needs_changes"
        elif gate_status == "blocked_execution_proposal_rejected":
            queue_status = "blocked_worktree_proposal_rejected"
        elif gate_status == "deferred_by_patch_queue":
            queue_status = "deferred_by_execution_gate"
        else:
            queue_status = "blocked_until_codex_execution_gate_ready"

        queue_ready = queue_status == "ready_for_codex_worktree_preparation"
        blocked_actions = [
            "auto_create_codex_worktree",
            "auto_switch_branch_from_worktree_queue",
            "auto_apply_patch_from_worktree_queue",
            "auto_commit_push_or_open_pr_from_worktree_queue",
            "write_live_hermes_memory",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        preparation_tasks = [
            {
                "task_id": f"CODEX-WORKTREE-PREP-{TRAINING_VERSION}-{index:03d}",
                "source_execution_candidate_id": candidate.get("execution_candidate_id"),
                "source_patch_candidate_id": candidate.get("source_patch_candidate_id"),
                "source_packet_id": candidate.get("source_packet_id"),
                "type": "codex_worktree_preparation_task",
                "priority": candidate.get("priority", "P2"),
                "summary": candidate.get("summary", ""),
                "preparation_status": "pending_user_worktree_command",
                "worktree_creation_automatic": False,
                "patch_application_automatic": False,
                "commit_automatic": False,
                "push_or_pr_automatic": False,
                "human_confirmation_required": True,
                "required_validation": candidate.get("required_validation", []),
                "expected_result_contract": {
                    "return_patch_summary": True,
                    "return_changed_files": True,
                    "return_validation_output": True,
                    "return_blocked_actions": True,
                },
                "blocked_actions": blocked_actions,
            }
            for index, candidate in enumerate(approved_candidates, start=1)
            if queue_ready
        ]
        return {
            "schema_id": "athena.codex_worktree_preparation_queue.v1",
            "version": TRAINING_VERSION,
            "queue_id": f"CODEX-WORKTREE-PREPARATION-{TRAINING_VERSION}-TPI-001",
            "source_execution_gate_id": gate.get("gate_id"),
            "source_execution_gate_status": gate_status,
            "source_execution_review_summary": gate.get("execution_review_summary", {}),
            "queue_status": queue_status,
            "queue_ready": queue_ready,
            "preparation_task_count": len(preparation_tasks),
            "approved_execution_candidate_count": len(approved_candidates),
            "preparation_tasks": preparation_tasks,
            "decision_rules": [
                "only execution candidates approved_for_worktree_preparation can become worktree preparation tasks",
                "worktree preparation tasks are command drafts and never create a worktree automatically",
                "patch application, commits, pushes, PRs, live Hermes writes, and real data integration require a later explicit user command",
                "returned worktree results must include changed files and compileall plus harness validation evidence",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _codex_worktree_preparation_hermes_payload(queue: dict) -> dict:
        return {
            "schema": "hermes.codex_worktree_preparation_queue.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if queue.get("queue_ready") else "candidate",
            "version": TRAINING_VERSION,
            "queue_id": queue["queue_id"],
            "source_execution_gate_id": queue.get("source_execution_gate_id"),
            "source_execution_gate_status": queue.get("source_execution_gate_status"),
            "queue_status": queue.get("queue_status"),
            "queue_ready": queue.get("queue_ready"),
            "preparation_task_count": queue.get("preparation_task_count", 0),
            "approved_execution_candidate_count": queue.get("approved_execution_candidate_count", 0),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_worktree_preparation_kpis(queue: dict) -> list[dict]:
        return [
            {"kpi": "codex_worktree_preparation_queue_ready", "value": queue["queue_ready"], "target": True, "status": "ok" if queue["queue_ready"] else "attention"},
            {"kpi": "codex_worktree_preparation_task_count", "value": queue["preparation_task_count"], "target": "tracked", "status": "ok" if queue["preparation_task_count"] else "attention"},
        ]

    @staticmethod
    def _codex_worktree_preparation_evidence(queue: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-WORKTREE-PREP-001",
                "source": "athena.codex_execution_review_state.v1",
                "summary": f"Prepared worktree queue {queue['queue_status']} from execution gate {queue.get('source_execution_gate_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-WORKTREE-PREP-002",
                "source": "codex_worktree_preparation_guardrail",
                "summary": "Worktree preparation queue is read-only and blocks automatic worktree creation, patch application, commits, pushes, PRs, live Hermes writes, raw-file storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _codex_worktree_launch_gate(queue: dict) -> dict:
        source_status = queue.get("queue_status", "blocked_until_codex_worktree_preparation_ready")
        preparation_tasks = queue.get("preparation_tasks", [])

        if queue.get("queue_ready") and preparation_tasks:
            launch_status = "ready_for_user_worktree_launch_confirmation"
        elif source_status == "blocked_until_execution_review_approval":
            launch_status = "blocked_until_worktree_preparation_approval"
        elif source_status == "blocked_worktree_proposal_needs_changes":
            launch_status = "blocked_launch_proposal_needs_changes"
        elif source_status == "blocked_worktree_proposal_rejected":
            launch_status = "blocked_launch_proposal_rejected"
        elif source_status == "deferred_by_execution_gate":
            launch_status = "deferred_by_worktree_preparation_queue"
        else:
            launch_status = "blocked_until_codex_worktree_preparation_ready"

        launch_ready = launch_status == "ready_for_user_worktree_launch_confirmation"
        blocked_actions = [
            "auto_launch_codex_worktree",
            "auto_run_git_worktree_add",
            "auto_switch_branch_from_launch_gate",
            "auto_apply_patch_from_launch_gate",
            "auto_commit_push_or_open_pr_from_launch_gate",
            "write_live_hermes_memory",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        launch_requests = [
            {
                "launch_request_id": f"CODEX-WORKTREE-LAUNCH-{TRAINING_VERSION}-{index:03d}",
                "source_preparation_task_id": task.get("task_id"),
                "source_execution_candidate_id": task.get("source_execution_candidate_id"),
                "source_patch_candidate_id": task.get("source_patch_candidate_id"),
                "source_packet_id": task.get("source_packet_id"),
                "type": "codex_worktree_launch_request",
                "priority": task.get("priority", "P2"),
                "summary": task.get("summary", ""),
                "launch_status": "pending_explicit_user_launch_command",
                "suggested_user_instruction": (
                    "Ask Codex to create a separate worktree for this approved small-fix task, "
                    "implement only the approved scope, run compileall plus the existing harness, "
                    "and return changed files, validation output, and blocked actions."
                ),
                "required_preflight_checks": [
                    "user explicitly confirms local worktree launch",
                    "scope remains an approved small fix from the execution review",
                    "no credentials, API keys, raw customer files, APS/IOT writes, or live Hermes writes are required",
                    "changed files and validation output will be returned for product-owner review",
                ],
                "worktree_creation_automatic": False,
                "branch_switch_automatic": False,
                "patch_application_automatic": False,
                "commit_automatic": False,
                "push_or_pr_automatic": False,
                "human_confirmation_required": True,
                "required_validation": task.get("required_validation", []),
                "expected_result_contract": task.get(
                    "expected_result_contract",
                    {
                        "return_patch_summary": True,
                        "return_changed_files": True,
                        "return_validation_output": True,
                        "return_blocked_actions": True,
                    },
                ),
                "blocked_actions": blocked_actions,
            }
            for index, task in enumerate(preparation_tasks, start=1)
            if launch_ready
        ]
        return {
            "schema_id": "athena.codex_worktree_launch_gate.v1",
            "version": TRAINING_VERSION,
            "launch_gate_id": f"CODEX-WORKTREE-LAUNCH-GATE-{TRAINING_VERSION}-TPI-001",
            "source_worktree_preparation_queue_id": queue.get("queue_id"),
            "source_worktree_preparation_status": source_status,
            "launch_status": launch_status,
            "launch_ready": launch_ready,
            "automatic_launch_allowed": False,
            "human_confirmation_required": bool(launch_requests),
            "launch_request_count": len(launch_requests),
            "preparation_task_count": queue.get("preparation_task_count", 0),
            "launch_requests": launch_requests,
            "decision_rules": [
                "only ready worktree preparation tasks can become launch requests",
                "launch requests are user-instruction drafts and never run git, create worktrees, apply patches, or switch branches automatically",
                "actual local worktree creation requires an explicit user command in the active Codex conversation",
                "large features, new pages, real data integration, and live Hermes runner changes still require product-owner confirmation before any worktree launch",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _codex_worktree_launch_hermes_payload(gate: dict) -> dict:
        return {
            "schema": "hermes.codex_worktree_launch_gate.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if gate.get("launch_ready") else "candidate",
            "version": TRAINING_VERSION,
            "launch_gate_id": gate["launch_gate_id"],
            "source_worktree_preparation_queue_id": gate.get("source_worktree_preparation_queue_id"),
            "source_worktree_preparation_status": gate.get("source_worktree_preparation_status"),
            "launch_status": gate.get("launch_status"),
            "launch_ready": gate.get("launch_ready"),
            "automatic_launch_allowed": gate.get("automatic_launch_allowed"),
            "human_confirmation_required": gate.get("human_confirmation_required"),
            "launch_request_count": gate.get("launch_request_count", 0),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_worktree_launch_kpis(gate: dict) -> list[dict]:
        return [
            {"kpi": "codex_worktree_launch_gate_ready", "value": gate["launch_ready"], "target": True, "status": "ok" if gate["launch_ready"] else "attention"},
            {"kpi": "codex_worktree_launch_request_count", "value": gate["launch_request_count"], "target": "tracked", "status": "ok" if gate["launch_request_count"] else "attention"},
            {"kpi": "codex_automatic_worktree_launch_allowed", "value": gate["automatic_launch_allowed"], "target": False, "status": "ok" if gate["automatic_launch_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_worktree_launch_evidence(gate: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-WORKTREE-LAUNCH-001",
                "source": "athena.codex_worktree_preparation_queue.v1",
                "summary": f"Evaluated worktree launch gate {gate['launch_status']} from preparation queue {gate.get('source_worktree_preparation_queue_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-WORKTREE-LAUNCH-002",
                "source": "codex_worktree_launch_guardrail",
                "summary": "Worktree launch gate blocks automatic git worktree creation, branch switching, patch application, commits, pushes, PRs, live Hermes writes, raw-file storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @classmethod
    def _normalize_worktree_validation_results(cls, raw_results: object) -> list[dict]:
        allowed = {"passed", "failed", "blocked", "not_run"}
        if not isinstance(raw_results, list):
            return []
        normalized = []
        for item in raw_results[:10]:
            if not isinstance(item, dict):
                continue
            command = cls._clean(item.get("command"))
            status = cls._clean(item.get("status"))
            summary = cls._clean(item.get("summary"))
            if status not in allowed:
                status = "not_run"
            for value in [command, status, summary]:
                cls._ensure_safe_text(value)
            normalized.append(
                {
                    "command": command,
                    "status": status,
                    "summary": summary,
                    "contains_raw_log": False,
                    "contains_credentials": False,
                }
            )
        return normalized

    @staticmethod
    def _worktree_result_contract_status(result_status: str, changed_files: list[str], validation_results: list[dict]) -> dict:
        commands = [
            f"{item.get('command', '')} {item.get('summary', '')}".lower()
            for item in validation_results
            if item.get("status") == "passed"
        ]
        compileall_passed = any("compileall" in item for item in commands)
        harness_passed = any("harness" in item or "test_main_agent" in item for item in commands)
        changed_files_reported = bool(changed_files)
        contract_complete = result_status == "validation_passed" and changed_files_reported and compileall_passed and harness_passed
        return {
            "contract_complete": contract_complete,
            "changed_files_reported": changed_files_reported,
            "compileall_passed": compileall_passed,
            "harness_passed": harness_passed,
            "missing_items": [
                item
                for item, ok in [
                    ("changed_files", changed_files_reported),
                    ("compileall_passed", compileall_passed),
                    ("harness_passed", harness_passed),
                ]
                if not ok
            ],
        }

    @staticmethod
    def _codex_worktree_result_state(store: dict) -> dict:
        results = list(store.get("codex_worktree_results", {}).values())
        passed = [item for item in results if item.get("result_status") == "validation_passed"]
        failed = [item for item in results if item.get("result_status") == "validation_failed"]
        blocked = [item for item in results if item.get("result_status") == "blocked"]
        contract_complete = [
            item
            for item in passed
            if item.get("validation_contract", {}).get("contract_complete")
        ]
        return {
            "schema_id": "athena.codex_worktree_result_state.v1",
            "version": store.get("version", TRAINING_VERSION),
            "updated_at": store.get("updated_at", ""),
            "result_count": len(results),
            "validation_passed_count": len(passed),
            "validation_failed_count": len(failed),
            "blocked_result_count": len(blocked),
            "contract_complete_count": len(contract_complete),
            "codex_worktree_results": store.get("codex_worktree_results", {}),
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _codex_worktree_result_intake(store: dict, launch_gate: dict) -> dict:
        result_state = TrainingAutomationWorkflow._codex_worktree_result_state(store)
        source_status = launch_gate.get("launch_status", "blocked_until_codex_worktree_launch_ready")
        if result_state["validation_failed_count"]:
            intake_status = "worktree_result_validation_failed"
        elif result_state["contract_complete_count"]:
            intake_status = "worktree_result_validation_passed"
        elif result_state["result_count"]:
            intake_status = "worktree_result_review_required"
        elif launch_gate.get("launch_ready"):
            intake_status = "waiting_for_codex_worktree_result"
        else:
            intake_status = "blocked_until_codex_worktree_launch_ready"

        blocked_actions = [
            "auto_merge_codex_worktree_result",
            "auto_commit_push_or_open_pr_from_worktree_result",
            "auto_write_hermes_memory_from_worktree_result",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_worktree_result_intake.v1",
            "version": TRAINING_VERSION,
            "intake_id": f"CODEX-WORKTREE-RESULT-INTAKE-{TRAINING_VERSION}-TPI-001",
            "source_worktree_launch_gate_id": launch_gate.get("launch_gate_id"),
            "source_worktree_launch_status": source_status,
            "intake_status": intake_status,
            "result_state": result_state,
            "result_count": result_state["result_count"],
            "validation_passed_count": result_state["validation_passed_count"],
            "validation_failed_count": result_state["validation_failed_count"],
            "contract_complete_count": result_state["contract_complete_count"],
            "automatic_merge_allowed": False,
            "human_review_required": bool(result_state["result_count"]),
            "codex_worktree_results": result_state["codex_worktree_results"],
            "decision_rules": [
                "Codex worktree results are metadata-only summaries with changed-file paths and validation statuses",
                "raw diffs, raw logs, raw files, credentials, API keys, and platform credentials must not be stored in the result intake",
                "validation_passed requires changed files, compileall passed, and harness/test passed evidence",
                "result intake never commits, pushes, opens PRs, writes live Hermes memory, or starts real data integration automatically",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _codex_worktree_result_hermes_payload(intake: dict) -> dict:
        return {
            "schema": "hermes.codex_worktree_result_intake.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if intake.get("contract_complete_count") else "candidate",
            "version": TRAINING_VERSION,
            "intake_id": intake["intake_id"],
            "source_worktree_launch_gate_id": intake.get("source_worktree_launch_gate_id"),
            "source_worktree_launch_status": intake.get("source_worktree_launch_status"),
            "intake_status": intake.get("intake_status"),
            "result_count": intake.get("result_count", 0),
            "validation_passed_count": intake.get("validation_passed_count", 0),
            "validation_failed_count": intake.get("validation_failed_count", 0),
            "automatic_merge_allowed": intake.get("automatic_merge_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_worktree_result_kpis(intake: dict) -> list[dict]:
        return [
            {"kpi": "codex_worktree_result_count", "value": intake["result_count"], "target": "tracked", "status": "ok" if intake["result_count"] else "attention"},
            {"kpi": "codex_worktree_validation_passed_count", "value": intake["validation_passed_count"], "target": "tracked", "status": "ok" if intake["validation_passed_count"] else "attention"},
            {"kpi": "codex_worktree_validation_failed_count", "value": intake["validation_failed_count"], "target": 0, "status": "ok" if intake["validation_failed_count"] == 0 else "failed"},
            {"kpi": "codex_automatic_result_merge_allowed", "value": intake["automatic_merge_allowed"], "target": False, "status": "ok" if intake["automatic_merge_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_worktree_result_evidence(intake: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-WORKTREE-RESULT-001",
                "source": "athena.codex_worktree_launch_gate.v1",
                "summary": f"Prepared worktree result intake {intake['intake_status']} from launch gate {intake.get('source_worktree_launch_gate_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-WORKTREE-RESULT-002",
                "source": "codex_worktree_result_guardrail",
                "summary": "Worktree result intake is metadata-only and blocks automatic merge, commits, pushes, PRs, live Hermes writes, raw patch storage, raw-file storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _codex_worktree_result_review_state(store: dict) -> dict:
        reviews = list(store.get("codex_worktree_result_reviews", {}).values())
        regression = [
            item
            for item in reviews
            if item.get("review_status") in {"approved_for_regression_baseline", "approved_for_regression_and_memory"}
        ]
        memory = [
            item
            for item in reviews
            if item.get("review_status") in {"approved_for_hermes_memory_candidate", "approved_for_regression_and_memory"}
        ]
        return {
            "schema_id": "athena.codex_worktree_result_review_state.v1",
            "version": store.get("version", TRAINING_VERSION),
            "updated_at": store.get("updated_at", ""),
            "review_count": len(reviews),
            "approved_for_regression_baseline_count": len(regression),
            "approved_for_hermes_memory_candidate_count": len(memory),
            "needs_changes_count": len([item for item in reviews if item.get("review_status") == "needs_changes"]),
            "deferred_count": len([item for item in reviews if item.get("review_status") == "deferred"]),
            "rejected_count": len([item for item in reviews if item.get("review_status") == "rejected"]),
            "note_count": len([item for item in reviews if item.get("review_status") == "note_only"]),
            "codex_worktree_result_reviews": store.get("codex_worktree_result_reviews", {}),
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _codex_worktree_result_review_gate(intake: dict, store: dict) -> dict:
        result_records = list(intake.get("codex_worktree_results", {}).values())
        review_state = TrainingAutomationWorkflow._codex_worktree_result_review_state(store)
        reviews = review_state.get("codex_worktree_result_reviews", {})
        eligible_results = [
            item
            for item in result_records
            if item.get("result_status") == "validation_passed"
            and item.get("validation_contract", {}).get("contract_complete")
        ]

        candidates = []
        regression_candidates = []
        memory_candidates = []
        for result in eligible_results:
            launch_request_id = result.get("launch_request_id", "")
            review = reviews.get(launch_request_id, {})
            review_status = review.get("review_status", "pending_result_review")
            candidate = {
                "review_candidate_id": f"CODEX-WORKTREE-RESULT-REVIEW-{TRAINING_VERSION}-{len(candidates) + 1:03d}",
                "launch_request_id": launch_request_id,
                "source_preparation_task_id": result.get("source_preparation_task_id", ""),
                "source_execution_candidate_id": result.get("source_execution_candidate_id", ""),
                "source_patch_candidate_id": result.get("source_patch_candidate_id", ""),
                "source_packet_id": result.get("source_packet_id", ""),
                "type": "codex_worktree_result_review_candidate",
                "result_status": result.get("result_status", ""),
                "result_summary": result.get("result_summary", ""),
                "changed_files": result.get("changed_files", []),
                "changed_file_count": result.get("changed_file_count", 0),
                "validation_contract": result.get("validation_contract", {}),
                "review": {
                    "review_status": review_status,
                    "review_note": review.get("review_note", ""),
                    "reviewer": review.get("reviewer", ""),
                    "updated_at": review.get("updated_at", ""),
                },
                "regression_baseline_candidate": review_status in {"approved_for_regression_baseline", "approved_for_regression_and_memory"},
                "hermes_memory_candidate": review_status in {"approved_for_hermes_memory_candidate", "approved_for_regression_and_memory"},
                "automatic_promotion_allowed": False,
                "human_review_required": review_status == "pending_result_review",
            }
            if candidate["regression_baseline_candidate"]:
                regression_candidates.append(candidate)
            if candidate["hermes_memory_candidate"]:
                memory_candidates.append(candidate)
            candidates.append(candidate)

        if intake.get("validation_failed_count"):
            gate_status = "blocked_result_validation_failed"
        elif regression_candidates or memory_candidates:
            gate_status = "result_review_approved_for_promotion_candidates"
        elif candidates:
            gate_status = "ready_for_worktree_result_review"
        elif intake.get("result_count"):
            gate_status = "blocked_result_contract_incomplete"
        elif intake.get("intake_status") == "waiting_for_codex_worktree_result":
            gate_status = "waiting_for_codex_worktree_result"
        else:
            gate_status = "blocked_until_codex_worktree_result_ready"

        blocked_actions = [
            "auto_promote_worktree_result_to_regression",
            "auto_write_worktree_result_to_hermes",
            "auto_merge_codex_worktree_result",
            "auto_commit_push_or_open_pr_from_result_review",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_worktree_result_review_gate.v1",
            "version": TRAINING_VERSION,
            "gate_id": f"CODEX-WORKTREE-RESULT-REVIEW-GATE-{TRAINING_VERSION}-TPI-001",
            "source_result_intake_id": intake.get("intake_id"),
            "source_result_intake_status": intake.get("intake_status"),
            "gate_status": gate_status,
            "gate_ready": bool(candidates),
            "review_candidate_count": len(candidates),
            "pending_review_count": len([item for item in candidates if item["review"]["review_status"] == "pending_result_review"]),
            "regression_promotion_candidate_count": len(regression_candidates),
            "hermes_memory_candidate_count": len(memory_candidates),
            "automatic_promotion_allowed": False,
            "human_review_required": bool(candidates),
            "result_review_candidates": candidates,
            "regression_baseline_candidates": regression_candidates,
            "hermes_memory_candidates": memory_candidates,
            "result_review_state": review_state,
            "decision_rules": [
                "only validation_passed worktree results with complete validation contracts can enter result review",
                "approved reviews create regression or Hermes memory candidates only; they do not write live Hermes memory or change regression baselines automatically",
                "result review must not merge worktree changes, commit, push, open PRs, store raw diffs, store raw logs, store credentials, or start real data integration",
                "needs-changes, deferred, rejected, and note-only decisions remain visible in the review state",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _codex_worktree_result_review_hermes_payload(gate: dict) -> dict:
        return {
            "schema": "hermes.codex_worktree_result_review_gate.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if gate.get("regression_promotion_candidate_count") or gate.get("hermes_memory_candidate_count") else "candidate",
            "version": TRAINING_VERSION,
            "gate_id": gate["gate_id"],
            "source_result_intake_id": gate.get("source_result_intake_id"),
            "source_result_intake_status": gate.get("source_result_intake_status"),
            "gate_status": gate.get("gate_status"),
            "review_candidate_count": gate.get("review_candidate_count", 0),
            "regression_promotion_candidate_count": gate.get("regression_promotion_candidate_count", 0),
            "hermes_memory_candidate_count": gate.get("hermes_memory_candidate_count", 0),
            "automatic_promotion_allowed": gate.get("automatic_promotion_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_worktree_result_review_kpis(gate: dict) -> list[dict]:
        return [
            {"kpi": "codex_worktree_result_review_count", "value": gate["result_review_state"]["review_count"], "target": "tracked", "status": "ok" if gate["result_review_state"]["review_count"] else "attention"},
            {"kpi": "codex_worktree_regression_promotion_candidate_count", "value": gate["regression_promotion_candidate_count"], "target": "tracked", "status": "ok" if gate["regression_promotion_candidate_count"] else "attention"},
            {"kpi": "codex_worktree_hermes_memory_candidate_count", "value": gate["hermes_memory_candidate_count"], "target": "tracked", "status": "ok" if gate["hermes_memory_candidate_count"] else "attention"},
            {"kpi": "codex_automatic_result_promotion_allowed", "value": gate["automatic_promotion_allowed"], "target": False, "status": "ok" if gate["automatic_promotion_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_worktree_result_review_evidence(gate: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-WORKTREE-RESULT-REVIEW-001",
                "source": "athena.codex_worktree_result_intake.v1",
                "summary": f"Evaluated worktree result review gate {gate['gate_status']} from result intake {gate.get('source_result_intake_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-WORKTREE-RESULT-REVIEW-002",
                "source": "codex_worktree_result_review_guardrail",
                "summary": "Result review gate creates regression and Hermes memory candidates only after metadata review; it blocks automatic promotion, merges, commits, pushes, PRs, raw patch storage, credentials, and live Hermes writes.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _codex_promotion_candidate_queue(gate: dict) -> dict:
        regression_candidates = [
            {
                "promotion_candidate_id": f"CODEX-REGRESSION-PROMOTION-{TRAINING_VERSION}-{index:03d}",
                "promotion_type": "regression_baseline_candidate",
                "launch_request_id": candidate.get("launch_request_id", ""),
                "source_patch_candidate_id": candidate.get("source_patch_candidate_id", ""),
                "source_packet_id": candidate.get("source_packet_id", ""),
                "result_summary": candidate.get("result_summary", ""),
                "changed_files": candidate.get("changed_files", []),
                "changed_file_count": candidate.get("changed_file_count", 0),
                "validation_contract": candidate.get("validation_contract", {}),
                "promotion_status": "candidate_pending_future_regression_promotion",
                "automatic_promotion_allowed": False,
                "human_confirmation_required": True,
            }
            for index, candidate in enumerate(gate.get("regression_baseline_candidates", []), start=1)
        ]
        memory_candidates = [
            {
                "promotion_candidate_id": f"CODEX-HERMES-MEMORY-PROMOTION-{TRAINING_VERSION}-{index:03d}",
                "promotion_type": "hermes_memory_candidate",
                "launch_request_id": candidate.get("launch_request_id", ""),
                "source_patch_candidate_id": candidate.get("source_patch_candidate_id", ""),
                "source_packet_id": candidate.get("source_packet_id", ""),
                "result_summary": candidate.get("result_summary", ""),
                "changed_files": candidate.get("changed_files", []),
                "changed_file_count": candidate.get("changed_file_count", 0),
                "validation_contract": candidate.get("validation_contract", {}),
                "promotion_status": "candidate_pending_future_hermes_memory_write",
                "automatic_promotion_allowed": False,
                "human_confirmation_required": True,
            }
            for index, candidate in enumerate(gate.get("hermes_memory_candidates", []), start=1)
        ]

        if regression_candidates or memory_candidates:
            queue_status = "ready_for_promotion_candidate_handoff"
        elif gate.get("review_candidate_count"):
            queue_status = "blocked_until_result_review_approval"
        elif gate.get("gate_status") == "blocked_result_validation_failed":
            queue_status = "blocked_result_validation_failed"
        elif gate.get("gate_status") == "blocked_result_contract_incomplete":
            queue_status = "blocked_result_contract_incomplete"
        else:
            queue_status = "blocked_until_codex_result_review_ready"

        blocked_actions = [
            "auto_promote_regression_baseline",
            "auto_write_live_hermes_memory",
            "auto_merge_codex_worktree_result",
            "auto_commit_push_or_open_pr_from_promotion_queue",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_promotion_candidate_queue.v1",
            "version": TRAINING_VERSION,
            "queue_id": f"CODEX-PROMOTION-CANDIDATE-QUEUE-{TRAINING_VERSION}-TPI-001",
            "source_result_review_gate_id": gate.get("gate_id"),
            "source_result_review_gate_status": gate.get("gate_status"),
            "queue_status": queue_status,
            "queue_ready": queue_status == "ready_for_promotion_candidate_handoff",
            "regression_promotion_candidate_count": len(regression_candidates),
            "hermes_memory_promotion_candidate_count": len(memory_candidates),
            "promotion_candidate_count": len(regression_candidates) + len(memory_candidates),
            "regression_baseline_promotion_candidates": regression_candidates,
            "hermes_memory_promotion_candidates": memory_candidates,
            "automatic_promotion_allowed": False,
            "human_confirmation_required": bool(regression_candidates or memory_candidates),
            "decision_rules": [
                "promotion candidate queue is read-only and created only from approved worktree result reviews",
                "regression candidates do not update baselines until a future explicit promotion action is defined",
                "Hermes memory candidates do not write live Hermes memory until endpoint, schema, retention, and approval policy are confirmed",
                "candidate queue must not merge worktree changes, commit, push, open PRs, store raw diffs, store credentials, or start real data integration",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _codex_promotion_candidate_hermes_payload(queue: dict) -> dict:
        return {
            "schema": "hermes.codex_promotion_candidate_queue.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if queue.get("queue_ready") else "candidate",
            "version": TRAINING_VERSION,
            "queue_id": queue["queue_id"],
            "source_result_review_gate_id": queue.get("source_result_review_gate_id"),
            "source_result_review_gate_status": queue.get("source_result_review_gate_status"),
            "queue_status": queue.get("queue_status"),
            "queue_ready": queue.get("queue_ready"),
            "regression_promotion_candidate_count": queue.get("regression_promotion_candidate_count", 0),
            "hermes_memory_promotion_candidate_count": queue.get("hermes_memory_promotion_candidate_count", 0),
            "automatic_promotion_allowed": queue.get("automatic_promotion_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_promotion_candidate_kpis(queue: dict) -> list[dict]:
        return [
            {"kpi": "codex_promotion_candidate_queue_ready", "value": queue["queue_ready"], "target": True, "status": "ok" if queue["queue_ready"] else "attention"},
            {"kpi": "codex_regression_promotion_candidate_count", "value": queue["regression_promotion_candidate_count"], "target": "tracked", "status": "ok" if queue["regression_promotion_candidate_count"] else "attention"},
            {"kpi": "codex_hermes_memory_promotion_candidate_count", "value": queue["hermes_memory_promotion_candidate_count"], "target": "tracked", "status": "ok" if queue["hermes_memory_promotion_candidate_count"] else "attention"},
            {"kpi": "codex_automatic_result_promotion_allowed", "value": queue["automatic_promotion_allowed"], "target": False, "status": "ok" if queue["automatic_promotion_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_promotion_candidate_evidence(queue: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-CANDIDATE-001",
                "source": "athena.codex_worktree_result_review_gate.v1",
                "summary": f"Prepared promotion candidate queue {queue['queue_status']} from result review gate {queue.get('source_result_review_gate_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-CANDIDATE-002",
                "source": "codex_promotion_candidate_guardrail",
                "summary": "Promotion candidate queue is read-only and blocks automatic regression baseline promotion, live Hermes memory writes, merges, commits, pushes, PRs, raw patch storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _codex_promotion_approval_state(store: dict) -> dict:
        approvals = list(store.get("codex_promotion_approvals", {}).values())
        approved = [item for item in approvals if item.get("review_status") == "approved_for_future_promotion"]
        return {
            "schema_id": "athena.codex_promotion_approval_state.v1",
            "version": store.get("version", TRAINING_VERSION),
            "updated_at": store.get("updated_at", ""),
            "approval_count": len(approvals),
            "approved_for_future_promotion_count": len(approved),
            "regression_future_action_count": len([item for item in approved if item.get("promotion_type") == "regression_baseline_candidate"]),
            "hermes_memory_future_action_count": len([item for item in approved if item.get("promotion_type") == "hermes_memory_candidate"]),
            "hold_count": len([item for item in approvals if item.get("review_status") == "hold_for_later"]),
            "skipped_count": len([item for item in approvals if item.get("review_status") == "skipped_for_now"]),
            "needs_changes_count": len([item for item in approvals if item.get("review_status") == "needs_changes"]),
            "rejected_count": len([item for item in approvals if item.get("review_status") == "rejected"]),
            "note_count": len([item for item in approvals if item.get("review_status") == "note_only"]),
            "codex_promotion_approvals": store.get("codex_promotion_approvals", {}),
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _codex_promotion_approval_gate(queue: dict, store: dict) -> dict:
        approval_state = TrainingAutomationWorkflow._codex_promotion_approval_state(store)
        approvals = approval_state.get("codex_promotion_approvals", {})
        candidate_records = [
            *queue.get("regression_baseline_promotion_candidates", []),
            *queue.get("hermes_memory_promotion_candidates", []),
        ]

        approval_candidates = []
        future_action_plan = []
        for index, candidate in enumerate(candidate_records, start=1):
            candidate_id = candidate.get("promotion_candidate_id", "")
            approval = approvals.get(candidate_id, {})
            review_status = approval.get("review_status", "pending_promotion_approval")
            future_action = candidate.get("promotion_type") == "regression_baseline_candidate" and "manual_regression_baseline_promotion" or "manual_hermes_memory_write"
            approved_for_future_action = review_status == "approved_for_future_promotion"
            approval_candidate = {
                **candidate,
                "approval_candidate_id": f"CODEX-PROMOTION-APPROVAL-{TRAINING_VERSION}-{index:03d}",
                "review": {
                    "review_status": review_status,
                    "review_note": approval.get("review_note", ""),
                    "reviewer": approval.get("reviewer", ""),
                    "updated_at": approval.get("updated_at", ""),
                },
                "future_action": future_action,
                "approved_for_future_action": approved_for_future_action,
                "automatic_execution_allowed": False,
                "human_review_required": review_status == "pending_promotion_approval",
            }
            if approved_for_future_action:
                future_action_plan.append(
                    {
                        "plan_id": f"CODEX-PROMOTION-FUTURE-ACTION-{TRAINING_VERSION}-{len(future_action_plan) + 1:03d}",
                        "promotion_candidate_id": candidate_id,
                        "promotion_type": candidate.get("promotion_type", ""),
                        "launch_request_id": candidate.get("launch_request_id", ""),
                        "source_patch_candidate_id": candidate.get("source_patch_candidate_id", ""),
                        "source_packet_id": candidate.get("source_packet_id", ""),
                        "future_action": future_action,
                        "execution_status": "approved_but_not_executed",
                        "manual_confirmation_required": True,
                        "automatic_execution_allowed": False,
                    }
                )
            approval_candidates.append(approval_candidate)

        pending_count = len([item for item in approval_candidates if item["review"]["review_status"] == "pending_promotion_approval"])
        approved_count = len(future_action_plan)
        active_non_approved = [
            item
            for item in approval_candidates
            if item["review"]["review_status"] in {"hold_for_later", "needs_changes", "note_only"}
        ]
        closed_count = len([
            item
            for item in approval_candidates
            if item["review"]["review_status"] in {"skipped_for_now", "rejected"}
        ])
        if not queue.get("queue_ready"):
            gate_status = "blocked_until_promotion_candidates_ready"
        elif pending_count:
            gate_status = "ready_for_promotion_approval"
        elif approved_count:
            gate_status = "promotion_candidates_approved_for_future_action"
        elif active_non_approved:
            gate_status = "promotion_approval_waiting_for_follow_up"
        elif closed_count:
            gate_status = "promotion_approval_closed_without_execution"
        else:
            gate_status = "blocked_until_promotion_candidates_ready"

        blocked_actions = [
            "auto_execute_codex_promotion",
            "auto_promote_regression_baseline",
            "auto_write_live_hermes_memory",
            "auto_merge_codex_worktree_result",
            "auto_commit_push_or_open_pr_from_promotion_approval",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_promotion_approval_gate.v1",
            "version": TRAINING_VERSION,
            "gate_id": f"CODEX-PROMOTION-APPROVAL-GATE-{TRAINING_VERSION}-TPI-001",
            "source_promotion_candidate_queue_id": queue.get("queue_id"),
            "source_promotion_candidate_queue_status": queue.get("queue_status"),
            "gate_status": gate_status,
            "gate_ready": bool(approval_candidates),
            "promotion_candidate_count": len(approval_candidates),
            "pending_approval_count": pending_count,
            "approved_future_action_count": approved_count,
            "regression_future_action_count": len([item for item in future_action_plan if item.get("promotion_type") == "regression_baseline_candidate"]),
            "hermes_memory_future_action_count": len([item for item in future_action_plan if item.get("promotion_type") == "hermes_memory_candidate"]),
            "hold_count": len([item for item in approval_candidates if item["review"]["review_status"] == "hold_for_later"]),
            "skipped_count": len([item for item in approval_candidates if item["review"]["review_status"] == "skipped_for_now"]),
            "needs_changes_count": len([item for item in approval_candidates if item["review"]["review_status"] == "needs_changes"]),
            "rejected_count": len([item for item in approval_candidates if item["review"]["review_status"] == "rejected"]),
            "note_count": len([item for item in approval_candidates if item["review"]["review_status"] == "note_only"]),
            "automatic_execution_allowed": False,
            "human_confirmation_required": bool(approval_candidates),
            "approval_candidates": approval_candidates,
            "future_action_plan": future_action_plan,
            "approval_state": approval_state,
            "decision_rules": [
                "only candidates from the read-only promotion candidate queue can enter promotion approval",
                "approved candidates become future action plans only; they do not execute baseline promotion or Hermes memory writes",
                "held, skipped, rejected, needs-changes, and note-only decisions remain visible in the approval state",
                "promotion approval must not merge worktree changes, commit, push, open PRs, store raw diffs, store credentials, or start real data integration",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _codex_promotion_approval_hermes_payload(gate: dict) -> dict:
        return {
            "schema": "hermes.codex_promotion_approval_gate.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "approved" if gate.get("approved_future_action_count") else "reviewed" if gate.get("gate_ready") else "candidate",
            "version": TRAINING_VERSION,
            "gate_id": gate["gate_id"],
            "source_promotion_candidate_queue_id": gate.get("source_promotion_candidate_queue_id"),
            "source_promotion_candidate_queue_status": gate.get("source_promotion_candidate_queue_status"),
            "gate_status": gate.get("gate_status"),
            "promotion_candidate_count": gate.get("promotion_candidate_count", 0),
            "approved_future_action_count": gate.get("approved_future_action_count", 0),
            "regression_future_action_count": gate.get("regression_future_action_count", 0),
            "hermes_memory_future_action_count": gate.get("hermes_memory_future_action_count", 0),
            "automatic_execution_allowed": gate.get("automatic_execution_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_promotion_approval_kpis(gate: dict) -> list[dict]:
        return [
            {"kpi": "codex_promotion_approval_gate_ready", "value": gate["gate_ready"], "target": True, "status": "ok" if gate["gate_ready"] else "attention"},
            {"kpi": "codex_promotion_approval_pending_count", "value": gate["pending_approval_count"], "target": 0, "status": "ok" if gate["pending_approval_count"] == 0 else "attention"},
            {"kpi": "codex_promotion_approved_future_action_count", "value": gate["approved_future_action_count"], "target": "tracked", "status": "ok" if gate["approved_future_action_count"] else "attention"},
            {"kpi": "codex_promotion_automatic_execution_allowed", "value": gate["automatic_execution_allowed"], "target": False, "status": "ok" if gate["automatic_execution_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_promotion_approval_evidence(gate: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-APPROVAL-001",
                "source": "athena.codex_promotion_candidate_queue.v1",
                "summary": f"Evaluated promotion approval gate {gate['gate_status']} from candidate queue {gate.get('source_promotion_candidate_queue_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-APPROVAL-002",
                "source": "codex_promotion_approval_guardrail",
                "summary": "Promotion approval gate stores metadata decisions and future action plans only; it blocks automatic baseline promotion, live Hermes writes, merges, commits, pushes, PRs, raw patch storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _codex_promotion_handoff_queue(gate: dict) -> dict:
        future_actions = gate.get("future_action_plan", [])
        handoff_items = []
        for index, item in enumerate(future_actions, start=1):
            is_regression = item.get("promotion_type") == "regression_baseline_candidate"
            target_system = "local_regression_baseline_store" if is_regression else "live_hermes_memory"
            owner_role = "product_owner" if is_regression else "hermes_admin"
            required_preflight = [
                "confirm promotion candidate approval is still valid",
                "confirm no raw patch, raw file, credential, or customer-sensitive payload is included",
                "rerun python -m compileall src scripts tests",
                "rerun tests/test_main_agent.py harness",
            ]
            if is_regression:
                required_preflight.extend(
                    [
                        "confirm regression baseline scope and version label",
                        "confirm rollback path before updating any baseline record",
                    ]
                )
                suggested_instruction = "Confirm this regression baseline promotion and ask Codex to update the approved baseline records after validation."
            else:
                required_preflight.extend(
                    [
                        "confirm Hermes endpoint, schema, retention policy, sensitivity level, and tenant/factory scope",
                        "confirm live Hermes write permission and rollback procedure",
                    ]
                )
                suggested_instruction = "Confirm this Hermes memory promotion and provide the approved live Hermes connector details before any write."
            handoff_items.append(
                {
                    "handoff_id": f"CODEX-PROMOTION-HANDOFF-{TRAINING_VERSION}-{index:03d}",
                    "source_plan_id": item.get("plan_id", ""),
                    "promotion_candidate_id": item.get("promotion_candidate_id", ""),
                    "promotion_type": item.get("promotion_type", ""),
                    "launch_request_id": item.get("launch_request_id", ""),
                    "source_patch_candidate_id": item.get("source_patch_candidate_id", ""),
                    "source_packet_id": item.get("source_packet_id", ""),
                    "future_action": item.get("future_action", ""),
                    "target_system": target_system,
                    "owner_role": owner_role,
                    "handoff_status": "waiting_manual_execution",
                    "manual_execution_required": True,
                    "automatic_execution_allowed": False,
                    "required_preflight_checks": required_preflight,
                    "suggested_user_instruction": suggested_instruction,
                    "execution_evidence_required": [
                        "final validation command output",
                        "product-owner confirmation",
                        "exact files or memory-event ids changed by the future manual action",
                    ],
                    "retention_policy": "training_lifecycle",
                    "sensitivity_level": "internal",
                    "contains_raw_file": False,
                    "contains_credentials": False,
                }
            )

        if handoff_items:
            handoff_status = "ready_for_manual_promotion_handoff"
        elif gate.get("gate_status") == "blocked_until_promotion_candidates_ready":
            handoff_status = "blocked_until_promotion_candidates_ready"
        elif gate.get("promotion_candidate_count"):
            handoff_status = "blocked_until_promotion_approval"
        else:
            handoff_status = "blocked_until_promotion_approval"

        blocked_actions = [
            "auto_execute_codex_promotion_handoff",
            "auto_promote_regression_baseline",
            "auto_write_live_hermes_memory",
            "auto_merge_codex_worktree_result",
            "auto_commit_push_or_open_pr_from_promotion_handoff",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_promotion_handoff_queue.v1",
            "version": TRAINING_VERSION,
            "handoff_id": f"CODEX-PROMOTION-HANDOFF-QUEUE-{TRAINING_VERSION}-TPI-001",
            "source_promotion_approval_gate_id": gate.get("gate_id"),
            "source_promotion_approval_gate_status": gate.get("gate_status"),
            "handoff_status": handoff_status,
            "handoff_ready": bool(handoff_items),
            "handoff_item_count": len(handoff_items),
            "regression_handoff_count": len([item for item in handoff_items if item.get("promotion_type") == "regression_baseline_candidate"]),
            "hermes_memory_handoff_count": len([item for item in handoff_items if item.get("promotion_type") == "hermes_memory_candidate"]),
            "automatic_execution_allowed": False,
            "manual_execution_required": bool(handoff_items),
            "handoff_items": handoff_items,
            "decision_rules": [
                "only approved-but-not-executed future actions from the promotion approval gate can enter handoff",
                "handoff items are explicit manual action contracts and do not execute baseline or Hermes writes",
                "baseline promotion requires validation rerun and product-owner confirmation before any future state change",
                "Hermes memory write requires confirmed endpoint, schema, retention, sensitivity, tenant scope, permission, and rollback procedure before any future write",
                "handoff must not merge worktree changes, commit, push, open PRs, store raw diffs, store credentials, or start real data integration",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _codex_promotion_handoff_hermes_payload(queue: dict) -> dict:
        return {
            "schema": "hermes.codex_promotion_handoff_queue.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "approved" if queue.get("handoff_ready") else "reviewed",
            "version": TRAINING_VERSION,
            "handoff_id": queue["handoff_id"],
            "source_promotion_approval_gate_id": queue.get("source_promotion_approval_gate_id"),
            "source_promotion_approval_gate_status": queue.get("source_promotion_approval_gate_status"),
            "handoff_status": queue.get("handoff_status"),
            "handoff_item_count": queue.get("handoff_item_count", 0),
            "regression_handoff_count": queue.get("regression_handoff_count", 0),
            "hermes_memory_handoff_count": queue.get("hermes_memory_handoff_count", 0),
            "automatic_execution_allowed": queue.get("automatic_execution_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_promotion_handoff_kpis(queue: dict) -> list[dict]:
        return [
            {"kpi": "codex_promotion_handoff_queue_ready", "value": queue["handoff_ready"], "target": True, "status": "ok" if queue["handoff_ready"] else "attention"},
            {"kpi": "codex_promotion_handoff_item_count", "value": queue["handoff_item_count"], "target": "tracked", "status": "ok" if queue["handoff_item_count"] else "attention"},
            {"kpi": "codex_promotion_handoff_manual_execution_required", "value": queue["manual_execution_required"], "target": True, "status": "ok" if queue["manual_execution_required"] or not queue["handoff_item_count"] else "failed"},
            {"kpi": "codex_promotion_handoff_automatic_execution_allowed", "value": queue["automatic_execution_allowed"], "target": False, "status": "ok" if queue["automatic_execution_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_promotion_handoff_evidence(queue: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-HANDOFF-001",
                "source": "athena.codex_promotion_approval_gate.v1",
                "summary": f"Prepared promotion handoff queue {queue['handoff_status']} from approval gate {queue.get('source_promotion_approval_gate_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-HANDOFF-002",
                "source": "codex_promotion_handoff_guardrail",
                "summary": "Promotion handoff queue provides manual execution contracts only and blocks automatic baseline promotion, live Hermes writes, merges, commits, pushes, PRs, raw patch storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _codex_promotion_readiness_review_state(store: dict) -> dict:
        reviews = list(store.get("codex_promotion_readiness_reviews", {}).values())
        confirmed = [item for item in reviews if item.get("review_status") == "confirmed_ready_for_manual_execution"]
        return {
            "schema_id": "athena.codex_promotion_readiness_review_state.v1",
            "version": store.get("version", TRAINING_VERSION),
            "updated_at": store.get("updated_at", ""),
            "readiness_review_count": len(reviews),
            "confirmed_ready_count": len(confirmed),
            "needs_inputs_count": len([item for item in reviews if item.get("review_status") == "needs_execution_inputs"]),
            "deferred_count": len([item for item in reviews if item.get("review_status") == "deferred"]),
            "rejected_count": len([item for item in reviews if item.get("review_status") == "rejected"]),
            "note_count": len([item for item in reviews if item.get("review_status") == "note_only"]),
            "automatic_execution_allowed": False,
            "manual_execution_confirmation_only": True,
            "codex_promotion_readiness_reviews": store.get("codex_promotion_readiness_reviews", {}),
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _codex_promotion_execution_readiness_gate(queue: dict, store: dict | None = None) -> dict:
        store = store or {}
        readiness_review_state = TrainingAutomationWorkflow._codex_promotion_readiness_review_state(store)
        readiness_reviews = readiness_review_state.get("codex_promotion_readiness_reviews", {})
        readiness_items = []
        for index, item in enumerate(queue.get("handoff_items", []), start=1):
            is_regression = item.get("promotion_type") == "regression_baseline_candidate"
            missing_inputs = [
                "explicit_product_owner_execution_confirmation",
                "current_compileall_validation_output",
                "current_test_harness_validation_output",
                "execution_evidence_capture_plan",
                "rollback_or_reversal_plan",
            ]
            if is_regression:
                missing_inputs.extend(
                    [
                        "baseline_update_target_contract",
                        "baseline_version_label_confirmation",
                    ]
                )
            else:
                missing_inputs.extend(
                    [
                        "live_hermes_endpoint",
                        "live_hermes_auth_scope",
                        "live_hermes_memory_schema",
                        "live_hermes_retention_policy",
                        "live_hermes_tenant_factory_scope",
                    ]
                )
            readiness_item_id = f"CODEX-PROMOTION-READINESS-{TRAINING_VERSION}-{index:03d}"
            review = readiness_reviews.get(readiness_item_id, {})
            confirmed_inputs = review.get("confirmed_inputs", [])
            remaining_inputs = [value for value in missing_inputs if value not in confirmed_inputs]
            review_status = review.get("review_status", "pending_readiness_review")
            if review_status == "confirmed_ready_for_manual_execution" and not remaining_inputs:
                item_readiness_status = "execution_prerequisites_confirmed"
            elif review_status == "rejected":
                item_readiness_status = "blocked_by_readiness_review_rejection"
            elif review_status == "deferred":
                item_readiness_status = "deferred_by_readiness_review"
            else:
                item_readiness_status = "blocked_missing_execution_prerequisites"
            readiness_items.append(
                {
                    "readiness_item_id": readiness_item_id,
                    "source_handoff_id": item.get("handoff_id", ""),
                    "promotion_candidate_id": item.get("promotion_candidate_id", ""),
                    "promotion_type": item.get("promotion_type", ""),
                    "future_action": item.get("future_action", ""),
                    "target_system": item.get("target_system", ""),
                    "owner_role": item.get("owner_role", ""),
                    "readiness_status": item_readiness_status,
                    "manual_execution_required": True,
                    "automatic_execution_allowed": False,
                    "missing_readiness_inputs": remaining_inputs,
                    "original_missing_readiness_inputs": missing_inputs,
                    "readiness_review": {
                        "review_status": review_status,
                        "review_note": review.get("review_note", ""),
                        "reviewer": review.get("reviewer", ""),
                        "updated_at": review.get("updated_at", ""),
                        "confirmed_inputs": confirmed_inputs,
                        "validation_summary": review.get("validation_summary", ""),
                        "rollback_summary": review.get("rollback_summary", ""),
                        "execution_evidence_plan": review.get("execution_evidence_plan", ""),
                    },
                    "required_preflight_checks": item.get("required_preflight_checks", []),
                    "execution_evidence_required": item.get("execution_evidence_required", []),
                    "suggested_user_instruction": item.get("suggested_user_instruction", ""),
                    "retention_policy": "training_lifecycle",
                    "sensitivity_level": "internal",
                    "contains_raw_file": False,
                    "contains_credentials": False,
                }
            )

        unconfirmed_count = len([item for item in readiness_items if item["readiness_status"] != "execution_prerequisites_confirmed"])
        blocked_count = len([item for item in readiness_items if item["readiness_status"].startswith("blocked") or item.get("missing_readiness_inputs")])
        rejected_count = len([item for item in readiness_items if item["readiness_status"] == "blocked_by_readiness_review_rejection"])
        if readiness_items and unconfirmed_count == 0:
            readiness_status = "ready_for_manual_execution_confirmation"
        elif readiness_items and rejected_count:
            readiness_status = "blocked_by_readiness_review_rejection"
        elif readiness_items and blocked_count:
            readiness_status = "blocked_until_execution_prerequisites_confirmed"
        elif queue.get("handoff_status") in {"blocked_until_promotion_candidates_ready", "blocked_until_promotion_approval"}:
            readiness_status = queue.get("handoff_status")
        else:
            readiness_status = "blocked_until_promotion_handoff_ready"

        blocked_actions = [
            "auto_execute_promotion_readiness_gate",
            "auto_promote_regression_baseline",
            "auto_write_live_hermes_memory",
            "auto_merge_codex_worktree_result",
            "auto_commit_push_or_open_pr_from_readiness_gate",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_promotion_execution_readiness_gate.v1",
            "version": TRAINING_VERSION,
            "gate_id": f"CODEX-PROMOTION-EXECUTION-READINESS-{TRAINING_VERSION}-TPI-001",
            "source_promotion_handoff_id": queue.get("handoff_id"),
            "source_promotion_handoff_status": queue.get("handoff_status"),
            "readiness_status": readiness_status,
            "readiness_ready": readiness_status == "ready_for_manual_execution_confirmation",
            "readiness_item_count": len(readiness_items),
            "blocked_readiness_item_count": blocked_count,
            "unconfirmed_readiness_item_count": unconfirmed_count,
            "confirmed_readiness_item_count": len([item for item in readiness_items if item["readiness_status"] == "execution_prerequisites_confirmed"]),
            "regression_readiness_count": len([item for item in readiness_items if item.get("promotion_type") == "regression_baseline_candidate"]),
            "hermes_memory_readiness_count": len([item for item in readiness_items if item.get("promotion_type") == "hermes_memory_candidate"]),
            "automatic_execution_allowed": False,
            "manual_execution_required": bool(readiness_items),
            "readiness_items": readiness_items,
            "readiness_review_state": readiness_review_state,
            "decision_rules": [
                "promotion handoff is not execution permission; execution readiness requires fresh validation, explicit product-owner confirmation, evidence capture, and rollback planning",
                "regression baseline promotion additionally requires a baseline target contract and version label confirmation",
                "Hermes memory promotion additionally requires live endpoint, auth scope, memory schema, retention policy, and tenant/factory scope confirmation",
                "readiness review stores metadata only and can mark prerequisites confirmed, needs-inputs, deferred, rejected, or note-only",
                "readiness gate must not execute baseline promotion, write live Hermes memory, merge worktree changes, commit, push, open PRs, store raw diffs, store credentials, or start real data integration",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _codex_promotion_execution_readiness_hermes_payload(gate: dict) -> dict:
        return {
            "schema": "hermes.codex_promotion_execution_readiness_gate.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if gate.get("readiness_item_count") else "candidate",
            "version": TRAINING_VERSION,
            "gate_id": gate["gate_id"],
            "source_promotion_handoff_id": gate.get("source_promotion_handoff_id"),
            "source_promotion_handoff_status": gate.get("source_promotion_handoff_status"),
            "readiness_status": gate.get("readiness_status"),
            "readiness_item_count": gate.get("readiness_item_count", 0),
            "blocked_readiness_item_count": gate.get("blocked_readiness_item_count", 0),
            "confirmed_readiness_item_count": gate.get("confirmed_readiness_item_count", 0),
            "readiness_review_count": gate.get("readiness_review_state", {}).get("readiness_review_count", 0),
            "automatic_execution_allowed": gate.get("automatic_execution_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_promotion_execution_readiness_kpis(gate: dict) -> list[dict]:
        return [
            {"kpi": "codex_promotion_execution_readiness_ready", "value": gate["readiness_ready"], "target": True, "status": "ok" if gate["readiness_ready"] else "attention"},
            {"kpi": "codex_promotion_execution_readiness_item_count", "value": gate["readiness_item_count"], "target": "tracked", "status": "ok" if gate["readiness_item_count"] else "attention"},
            {"kpi": "codex_promotion_execution_blocked_item_count", "value": gate["blocked_readiness_item_count"], "target": 0, "status": "ok" if gate["blocked_readiness_item_count"] == 0 else "attention"},
            {"kpi": "codex_promotion_execution_automatic_allowed", "value": gate["automatic_execution_allowed"], "target": False, "status": "ok" if gate["automatic_execution_allowed"] is False else "failed"},
            {"kpi": "codex_promotion_execution_readiness_review_count", "value": gate["readiness_review_state"]["readiness_review_count"], "target": "tracked", "status": "ok" if gate["readiness_review_state"]["readiness_review_count"] else "attention"},
            {"kpi": "codex_promotion_execution_readiness_confirmed_count", "value": gate["confirmed_readiness_item_count"], "target": gate["readiness_item_count"], "status": "ok" if gate["readiness_item_count"] and gate["confirmed_readiness_item_count"] == gate["readiness_item_count"] else "attention"},
        ]

    @staticmethod
    def _codex_promotion_execution_readiness_evidence(gate: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-READINESS-001",
                "source": "athena.codex_promotion_handoff_queue.v1",
                "summary": f"Evaluated promotion execution readiness {gate['readiness_status']} from handoff queue {gate.get('source_promotion_handoff_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-READINESS-002",
                "source": "codex_promotion_execution_readiness_guardrail",
                "summary": "Execution readiness gate identifies missing prerequisites only and blocks automatic baseline promotion, live Hermes writes, merges, commits, pushes, PRs, raw patch storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _promotion_execution_result_contract_status(result_status: str, changed_records: list[str], validation_results: list[dict]) -> dict:
        commands = [
            f"{item.get('command', '')} {item.get('summary', '')}".lower()
            for item in validation_results
            if item.get("status") == "passed"
        ]
        compileall_passed = any("compileall" in item for item in commands)
        harness_passed = any("harness" in item or "test_main_agent" in item for item in commands)
        changed_records_reported = bool(changed_records)
        contract_complete = result_status == "manual_execution_recorded" and changed_records_reported and compileall_passed and harness_passed
        return {
            "contract_complete": contract_complete,
            "changed_records_reported": changed_records_reported,
            "compileall_passed": compileall_passed,
            "harness_passed": harness_passed,
            "missing_items": [
                item
                for item, ok in [
                    ("changed_records", changed_records_reported),
                    ("compileall_passed", compileall_passed),
                    ("harness_passed", harness_passed),
                ]
                if not ok
            ],
        }

    @staticmethod
    def _codex_promotion_execution_result_state(store: dict) -> dict:
        results = list(store.get("codex_promotion_execution_results", {}).values())
        recorded = [item for item in results if item.get("result_status") == "manual_execution_recorded"]
        failed = [item for item in results if item.get("result_status") == "manual_execution_failed"]
        skipped = [item for item in results if item.get("result_status") == "manual_execution_skipped"]
        complete = [item for item in recorded if item.get("result_contract", {}).get("contract_complete")]
        return {
            "schema_id": "athena.codex_promotion_execution_result_state.v1",
            "version": store.get("version", TRAINING_VERSION),
            "updated_at": store.get("updated_at", ""),
            "result_count": len(results),
            "manual_execution_recorded_count": len(recorded),
            "manual_execution_failed_count": len(failed),
            "manual_execution_skipped_count": len(skipped),
            "contract_complete_count": len(complete),
            "automatic_execution_allowed": False,
            "metadata_only": True,
            "codex_promotion_execution_results": store.get("codex_promotion_execution_results", {}),
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _codex_promotion_execution_result_intake(store: dict, readiness_gate: dict) -> dict:
        result_state = TrainingAutomationWorkflow._codex_promotion_execution_result_state(store)
        source_status = readiness_gate.get("readiness_status", "blocked_until_promotion_handoff_ready")
        if result_state["manual_execution_failed_count"]:
            intake_status = "promotion_execution_result_failed"
        elif result_state["contract_complete_count"]:
            intake_status = "promotion_execution_result_recorded"
        elif result_state["result_count"]:
            intake_status = "promotion_execution_result_needs_review"
        elif readiness_gate.get("readiness_ready"):
            intake_status = "waiting_for_manual_promotion_execution_result"
        elif source_status == "blocked_until_execution_prerequisites_confirmed":
            intake_status = "blocked_until_promotion_execution_readiness_confirmed"
        else:
            intake_status = "blocked_until_promotion_execution_ready"

        blocked_actions = [
            "auto_execute_recorded_promotion_result",
            "auto_promote_regression_baseline",
            "auto_write_live_hermes_memory",
            "auto_merge_commit_push_or_open_pr_from_promotion_result",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_promotion_execution_result_intake.v1",
            "version": TRAINING_VERSION,
            "intake_id": f"CODEX-PROMOTION-EXECUTION-RESULT-INTAKE-{TRAINING_VERSION}-TPI-001",
            "source_readiness_gate_id": readiness_gate.get("gate_id"),
            "source_readiness_status": source_status,
            "intake_status": intake_status,
            "result_ready_for_review": result_state["result_count"] > 0,
            "manual_execution_result_required": readiness_gate.get("readiness_ready", False),
            "automatic_execution_allowed": False,
            "result_state": result_state,
            "result_count": result_state["result_count"],
            "contract_complete_count": result_state["contract_complete_count"],
            "codex_promotion_execution_results": result_state["codex_promotion_execution_results"],
            "decision_rules": [
                "execution result intake records metadata after an explicitly manual promotion action outside the demo",
                "result intake must not perform baseline promotion, live Hermes memory write, merge, commit, push, open PR, raw patch storage, or credential storage",
                "recorded results require changed record identifiers plus current compileall and test harness validation summaries before the contract is complete",
                "future baseline or Hermes promotion closure must review these metadata records separately before any real-state claim is accepted",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _codex_promotion_execution_result_hermes_payload(intake: dict) -> dict:
        return {
            "schema": "hermes.codex_promotion_execution_result_intake.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if intake.get("result_count") else "candidate",
            "version": TRAINING_VERSION,
            "intake_id": intake["intake_id"],
            "source_readiness_gate_id": intake.get("source_readiness_gate_id"),
            "source_readiness_status": intake.get("source_readiness_status"),
            "intake_status": intake.get("intake_status"),
            "result_count": intake.get("result_count", 0),
            "contract_complete_count": intake.get("contract_complete_count", 0),
            "automatic_execution_allowed": intake.get("automatic_execution_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_promotion_execution_result_kpis(intake: dict) -> list[dict]:
        return [
            {"kpi": "codex_promotion_execution_result_count", "value": intake["result_count"], "target": "tracked", "status": "ok" if intake["result_count"] else "attention"},
            {"kpi": "codex_promotion_execution_result_passed_count", "value": intake["result_state"]["manual_execution_recorded_count"], "target": "tracked", "status": "ok" if intake["result_state"]["manual_execution_recorded_count"] else "attention"},
            {"kpi": "codex_promotion_execution_result_contract_complete_count", "value": intake["contract_complete_count"], "target": intake["result_count"], "status": "ok" if intake["result_count"] and intake["contract_complete_count"] == intake["result_count"] else "attention"},
            {"kpi": "codex_promotion_execution_result_automatic_allowed", "value": intake["automatic_execution_allowed"], "target": False, "status": "ok" if intake["automatic_execution_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_promotion_execution_result_evidence(intake: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-EXECUTION-RESULT-001",
                "source": "athena.codex_promotion_execution_readiness_gate.v1",
                "summary": f"Prepared promotion execution result intake {intake['intake_status']} from readiness gate {intake.get('source_readiness_gate_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-EXECUTION-RESULT-002",
                "source": "codex_promotion_execution_result_guardrail",
                "summary": "Promotion execution result intake stores metadata only and blocks baseline promotion, live Hermes writes, merges, commits, pushes, PRs, raw patch storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _codex_promotion_closure_audit(intake: dict, readiness_gate: dict) -> dict:
        results_by_readiness = intake.get("codex_promotion_execution_results", {})
        readiness_items = [
            item
            for item in readiness_gate.get("readiness_items", [])
            if item.get("readiness_status") == "execution_prerequisites_confirmed"
        ]
        complete_results = [
            result
            for result in results_by_readiness.values()
            if result.get("result_contract", {}).get("contract_complete")
        ]
        failed_results = [
            result
            for result in results_by_readiness.values()
            if result.get("result_status") == "manual_execution_failed"
        ]
        expected_ids = {item.get("readiness_item_id") for item in readiness_items if item.get("readiness_item_id")}
        complete_ids = {result.get("readiness_item_id") for result in complete_results if result.get("readiness_item_id")}
        missing_items = [
            {
                "readiness_item_id": item.get("readiness_item_id", ""),
                "promotion_candidate_id": item.get("promotion_candidate_id", ""),
                "promotion_type": item.get("promotion_type", ""),
                "missing_reason": "complete_manual_execution_result_required",
            }
            for item in readiness_items
            if item.get("readiness_item_id") not in complete_ids
        ]
        sync_candidates = [
            TrainingAutomationWorkflow._promotion_sync_audit_candidate(index, result)
            for index, result in enumerate(complete_results, start=1)
        ]

        if failed_results:
            closure_status = "promotion_closure_blocked_by_failed_result"
        elif readiness_items and expected_ids and expected_ids.issubset(complete_ids):
            closure_status = "promotion_closure_ready_for_sync_audit"
        elif complete_results:
            closure_status = "promotion_closure_partial_results"
        elif intake.get("manual_execution_result_required"):
            closure_status = "waiting_for_manual_promotion_execution_result"
        else:
            closure_status = "blocked_until_promotion_execution_result_ready"

        blocked_actions = [
            "auto_close_promotion_loop",
            "auto_update_regression_baseline_from_closure_audit",
            "auto_write_live_hermes_memory_from_closure_audit",
            "auto_sync_hermes_memory_without_live_contract",
            "auto_commit_push_or_open_pr_from_closure_audit",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_promotion_closure_audit.v1",
            "version": TRAINING_VERSION,
            "audit_id": f"CODEX-PROMOTION-CLOSURE-AUDIT-{TRAINING_VERSION}-TPI-001",
            "source_result_intake_id": intake.get("intake_id", ""),
            "source_result_intake_status": intake.get("intake_status", ""),
            "source_readiness_gate_id": readiness_gate.get("gate_id", ""),
            "closure_status": closure_status,
            "closure_ready": closure_status == "promotion_closure_ready_for_sync_audit",
            "expected_result_count": len(readiness_items),
            "recorded_result_count": len(results_by_readiness),
            "complete_result_count": len(complete_results),
            "failed_result_count": len(failed_results),
            "missing_result_count": len(missing_items),
            "missing_results": missing_items,
            "sync_audit_candidate_count": len(sync_candidates),
            "sync_audit_candidates": sync_candidates,
            "future_hermes_sync_audit_required": any(
                candidate.get("promotion_type") == "hermes_memory_candidate"
                for candidate in sync_candidates
            ),
            "automatic_closure_allowed": False,
            "automatic_sync_allowed": False,
            "metadata_only": True,
            "contains_raw_file": False,
            "contains_credentials": False,
            "decision_rules": [
                "promotion closure audit can only read metadata-only execution result records",
                "closure is ready only when every confirmed readiness item has a complete manual execution result contract",
                "future Hermes synchronization audit must verify live endpoint, auth scope, memory schema, retention, and tenant/factory scope before any live write",
                "future regression baseline promotion must verify baseline target contract, version label, and current validation before any baseline update",
                "closure audit must not write live Hermes memory, update baselines, run git, store raw files, or start real data integration",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _promotion_sync_audit_candidate(index: int, result: dict) -> dict:
        promotion_type = result.get("promotion_type", "")
        if promotion_type == "hermes_memory_candidate":
            target_system = "live_hermes_memory"
            required_checks = [
                "live_hermes_endpoint",
                "live_hermes_auth_scope",
                "live_hermes_memory_schema",
                "live_hermes_retention_policy",
                "live_hermes_tenant_factory_scope",
            ]
        else:
            target_system = "local_regression_baseline_store"
            required_checks = [
                "baseline_update_target_contract",
                "baseline_version_label_confirmation",
                "current_compileall_validation_output",
                "current_test_harness_validation_output",
            ]
        return {
            "sync_audit_id": f"PROMO-SYNC-AUDIT-{TRAINING_VERSION}-{index:03d}",
            "readiness_item_id": result.get("readiness_item_id", ""),
            "promotion_candidate_id": result.get("promotion_candidate_id", ""),
            "promotion_type": promotion_type,
            "target_system": target_system,
            "source_execution_reference": result.get("execution_reference", ""),
            "source_changed_records": result.get("changed_records", []),
            "source_validation_summary": result.get("validation_summary", ""),
            "required_sync_checks": required_checks,
            "sync_audit_status": "sync_audit_ready",
            "manual_review_required": True,
            "automatic_sync_allowed": False,
            "metadata_only": True,
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _codex_promotion_closure_audit_hermes_payload(audit: dict) -> dict:
        return {
            "schema": "hermes.codex_promotion_closure_audit.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if audit.get("closure_ready") else "candidate",
            "version": TRAINING_VERSION,
            "audit_id": audit["audit_id"],
            "source_result_intake_id": audit.get("source_result_intake_id"),
            "closure_status": audit.get("closure_status"),
            "closure_ready": audit.get("closure_ready"),
            "expected_result_count": audit.get("expected_result_count", 0),
            "complete_result_count": audit.get("complete_result_count", 0),
            "sync_audit_candidate_count": audit.get("sync_audit_candidate_count", 0),
            "future_hermes_sync_audit_required": audit.get("future_hermes_sync_audit_required"),
            "automatic_sync_allowed": audit.get("automatic_sync_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_promotion_closure_audit_kpis(audit: dict) -> list[dict]:
        return [
            {"kpi": "codex_promotion_closure_ready", "value": audit["closure_ready"], "target": True, "status": "ok" if audit["closure_ready"] else "attention"},
            {"kpi": "codex_promotion_closure_expected_result_count", "value": audit["expected_result_count"], "target": "tracked", "status": "ok" if audit["expected_result_count"] else "attention"},
            {"kpi": "codex_promotion_closure_complete_result_count", "value": audit["complete_result_count"], "target": audit["expected_result_count"], "status": "ok" if audit["expected_result_count"] and audit["complete_result_count"] == audit["expected_result_count"] else "attention"},
            {"kpi": "codex_promotion_sync_audit_candidate_count", "value": audit["sync_audit_candidate_count"], "target": audit["complete_result_count"], "status": "ok" if audit["sync_audit_candidate_count"] == audit["complete_result_count"] and audit["complete_result_count"] else "attention"},
            {"kpi": "codex_promotion_closure_automatic_allowed", "value": audit["automatic_sync_allowed"], "target": False, "status": "ok" if audit["automatic_sync_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_promotion_closure_audit_evidence(audit: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-CLOSURE-001",
                "source": "athena.codex_promotion_execution_result_intake.v1",
                "summary": f"Audited promotion closure as {audit['closure_status']} from result intake {audit.get('source_result_intake_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-CLOSURE-002",
                "source": "codex_promotion_closure_audit_guardrail",
                "summary": "Closure audit is metadata-only and blocks baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _codex_promotion_sync_review_state(store: dict) -> dict:
        reviews = list(store.get("codex_promotion_sync_reviews", {}).values())
        approved = [item for item in reviews if item.get("review_status") == "approved_for_future_sync"]
        needs_inputs = [item for item in reviews if item.get("review_status") == "needs_sync_inputs"]
        deferred = [item for item in reviews if item.get("review_status") == "deferred"]
        rejected = [item for item in reviews if item.get("review_status") == "rejected"]
        return {
            "schema_id": "athena.codex_promotion_sync_review_state.v1",
            "version": store.get("version", TRAINING_VERSION),
            "updated_at": store.get("updated_at", ""),
            "sync_review_count": len(reviews),
            "approved_for_future_sync_count": len(approved),
            "needs_sync_inputs_count": len(needs_inputs),
            "deferred_count": len(deferred),
            "rejected_count": len(rejected),
            "automatic_sync_allowed": False,
            "metadata_only": True,
            "codex_promotion_sync_reviews": store.get("codex_promotion_sync_reviews", {}),
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _codex_promotion_sync_review_gate(audit: dict, store: dict) -> dict:
        review_state = TrainingAutomationWorkflow._codex_promotion_sync_review_state(store)
        reviews = review_state["codex_promotion_sync_reviews"]
        candidates = []
        for candidate in audit.get("sync_audit_candidates", []):
            review = reviews.get(candidate.get("sync_audit_id", ""), {})
            review_status = review.get("review_status", "pending_sync_review")
            if review_status == "approved_for_future_sync":
                candidate_status = "approved_for_future_sync"
            elif review_status == "needs_sync_inputs":
                candidate_status = "blocked_needs_sync_inputs"
            elif review_status == "deferred":
                candidate_status = "deferred_by_sync_review"
            elif review_status == "rejected":
                candidate_status = "blocked_by_sync_review_rejection"
            elif review_status == "note_only":
                candidate_status = "sync_review_note_recorded"
            else:
                candidate_status = "pending_sync_review"
            candidates.append(
                {
                    **candidate,
                    "sync_review_status": candidate_status,
                    "sync_review": {
                        "review_status": review_status,
                        "review_note": review.get("review_note", ""),
                        "reviewer": review.get("reviewer", ""),
                        "updated_at": review.get("updated_at", ""),
                        "confirmed_sync_checks": review.get("confirmed_sync_checks", []),
                    },
                }
            )

        approved_candidates = [item for item in candidates if item["sync_review_status"] == "approved_for_future_sync"]
        rejected_candidates = [item for item in candidates if item["sync_review_status"] == "blocked_by_sync_review_rejection"]
        needs_input_candidates = [item for item in candidates if item["sync_review_status"] == "blocked_needs_sync_inputs"]
        if not audit.get("closure_ready"):
            gate_status = "blocked_until_promotion_closure_ready"
        elif rejected_candidates:
            gate_status = "blocked_by_sync_review_rejection"
        elif candidates and len(approved_candidates) == len(candidates):
            gate_status = "promotion_sync_reviews_approved_for_future_execution"
        elif review_state["sync_review_count"]:
            gate_status = "promotion_sync_review_in_progress"
        elif candidates:
            gate_status = "ready_for_promotion_sync_review"
        else:
            gate_status = "blocked_no_sync_audit_candidates"

        blocked_actions = [
            "auto_execute_promotion_sync_review_gate",
            "auto_update_regression_baseline_from_sync_review",
            "auto_write_live_hermes_memory_from_sync_review",
            "auto_sync_hermes_memory_without_live_contract",
            "auto_commit_push_or_open_pr_from_sync_review",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_promotion_sync_review_gate.v1",
            "version": TRAINING_VERSION,
            "gate_id": f"CODEX-PROMOTION-SYNC-REVIEW-GATE-{TRAINING_VERSION}-TPI-001",
            "source_closure_audit_id": audit.get("audit_id", ""),
            "source_closure_status": audit.get("closure_status", ""),
            "gate_status": gate_status,
            "gate_ready": audit.get("closure_ready", False) and bool(candidates),
            "sync_candidate_count": len(candidates),
            "approved_future_sync_count": len(approved_candidates),
            "needs_sync_inputs_count": len(needs_input_candidates),
            "rejected_sync_count": len(rejected_candidates),
            "future_sync_action_count": len(approved_candidates),
            "future_sync_action_plan": [
                {
                    "sync_audit_id": item.get("sync_audit_id", ""),
                    "promotion_candidate_id": item.get("promotion_candidate_id", ""),
                    "promotion_type": item.get("promotion_type", ""),
                    "target_system": item.get("target_system", ""),
                    "execution_status": "approved_but_not_executed",
                    "manual_execution_required": True,
                    "automatic_sync_allowed": False,
                    "required_sync_checks": item.get("required_sync_checks", []),
                }
                for item in approved_candidates
            ],
            "sync_review_candidates": candidates,
            "sync_review_state": review_state,
            "automatic_sync_allowed": False,
            "metadata_only": True,
            "contains_raw_file": False,
            "contains_credentials": False,
            "decision_rules": [
                "sync review can approve future synchronization work only as metadata",
                "approved future sync actions still require live-system contracts, fresh validation, rollback planning, and explicit user confirmation before execution",
                "Hermes memory candidates require endpoint, auth scope, memory schema, retention, and tenant/factory scope before live write",
                "regression baseline candidates require baseline target contract and version label confirmation before baseline update",
                "sync review must not update baselines, write live Hermes memory, run git, store raw files, or start real data integration",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _codex_promotion_sync_review_hermes_payload(gate: dict) -> dict:
        return {
            "schema": "hermes.codex_promotion_sync_review_gate.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if gate.get("future_sync_action_count") else "candidate",
            "version": TRAINING_VERSION,
            "gate_id": gate["gate_id"],
            "source_closure_audit_id": gate.get("source_closure_audit_id"),
            "gate_status": gate.get("gate_status"),
            "sync_candidate_count": gate.get("sync_candidate_count", 0),
            "approved_future_sync_count": gate.get("approved_future_sync_count", 0),
            "future_sync_action_count": gate.get("future_sync_action_count", 0),
            "automatic_sync_allowed": gate.get("automatic_sync_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_promotion_sync_review_kpis(gate: dict) -> list[dict]:
        return [
            {"kpi": "codex_promotion_sync_review_gate_ready", "value": gate["gate_ready"], "target": True, "status": "ok" if gate["gate_ready"] else "attention"},
            {"kpi": "codex_promotion_sync_candidate_count", "value": gate["sync_candidate_count"], "target": "tracked", "status": "ok" if gate["sync_candidate_count"] else "attention"},
            {"kpi": "codex_promotion_sync_review_count", "value": gate["sync_review_state"]["sync_review_count"], "target": gate["sync_candidate_count"], "status": "ok" if gate["sync_candidate_count"] and gate["sync_review_state"]["sync_review_count"] >= gate["sync_candidate_count"] else "attention"},
            {"kpi": "codex_promotion_sync_approved_count", "value": gate["approved_future_sync_count"], "target": gate["sync_candidate_count"], "status": "ok" if gate["sync_candidate_count"] and gate["approved_future_sync_count"] == gate["sync_candidate_count"] else "attention"},
            {"kpi": "codex_promotion_sync_automatic_allowed", "value": gate["automatic_sync_allowed"], "target": False, "status": "ok" if gate["automatic_sync_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_promotion_sync_review_evidence(gate: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-SYNC-REVIEW-001",
                "source": "athena.codex_promotion_closure_audit.v1",
                "summary": f"Prepared sync review gate {gate['gate_status']} from closure audit {gate.get('source_closure_audit_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-SYNC-REVIEW-002",
                "source": "codex_promotion_sync_review_guardrail",
                "summary": "Sync review stores metadata only and blocks baseline updates, live Hermes writes, git actions, raw file storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _codex_promotion_sync_handoff_queue(sync_gate: dict) -> dict:
        future_actions = sync_gate.get("future_sync_action_plan", [])
        handoff_items = [
            TrainingAutomationWorkflow._promotion_sync_handoff_item(index, item)
            for index, item in enumerate(future_actions, start=1)
        ]
        gate_status = sync_gate.get("gate_status", "")
        if handoff_items:
            handoff_status = "ready_for_manual_sync_handoff"
        elif gate_status == "blocked_until_promotion_closure_ready":
            handoff_status = "blocked_until_promotion_closure_ready"
        elif gate_status in {"ready_for_promotion_sync_review", "promotion_sync_review_in_progress"}:
            handoff_status = "blocked_until_sync_review_approval"
        elif gate_status == "blocked_by_sync_review_rejection":
            handoff_status = "blocked_by_sync_review_rejection"
        else:
            handoff_status = "blocked_until_sync_reviews_ready"

        blocked_actions = [
            "auto_execute_promotion_sync_handoff",
            "auto_update_regression_baseline_from_sync_handoff",
            "auto_write_live_hermes_memory_from_sync_handoff",
            "auto_commit_push_or_open_pr_from_sync_handoff",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_promotion_sync_handoff_queue.v1",
            "version": TRAINING_VERSION,
            "handoff_id": f"CODEX-PROMOTION-SYNC-HANDOFF-{TRAINING_VERSION}-TPI-001",
            "source_sync_review_gate_id": sync_gate.get("gate_id", ""),
            "source_sync_review_status": gate_status,
            "handoff_status": handoff_status,
            "handoff_ready": bool(handoff_items),
            "handoff_item_count": len(handoff_items),
            "regression_sync_handoff_count": len([item for item in handoff_items if item.get("target_system") == "local_regression_baseline_store"]),
            "hermes_sync_handoff_count": len([item for item in handoff_items if item.get("target_system") == "live_hermes_memory"]),
            "manual_execution_required": bool(handoff_items),
            "automatic_execution_allowed": False,
            "handoff_items": handoff_items,
            "decision_rules": [
                "sync handoff converts approved future sync actions into manual execution contracts only",
                "handoff items must keep target system, owner role, preflight checks, suggested instruction, and required execution evidence visible",
                "sync handoff must not update regression baselines, write live Hermes memory, run git, store raw files, or start real data integration",
                "future execution still requires explicit user confirmation and fresh validation evidence outside this demo",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _promotion_sync_handoff_item(index: int, action: dict) -> dict:
        target_system = action.get("target_system", "")
        promotion_type = action.get("promotion_type", "")
        if target_system == "live_hermes_memory":
            owner_role = "hermes_admin"
            required_preflight_checks = [
                "live_hermes_endpoint",
                "live_hermes_auth_scope",
                "live_hermes_memory_schema",
                "live_hermes_retention_policy",
                "live_hermes_tenant_factory_scope",
                "rollback_or_reversal_plan",
                "current_test_harness_validation_output",
            ]
            suggested_user_instruction = (
                "After live Hermes endpoint, auth scope, memory schema, retention policy, tenant/factory scope, "
                "rollback plan, and validation evidence are confirmed, manually execute the approved Hermes memory sync outside this demo."
            )
        else:
            owner_role = "regression_maintainer"
            required_preflight_checks = [
                "baseline_update_target_contract",
                "baseline_version_label_confirmation",
                "current_compileall_validation_output",
                "current_test_harness_validation_output",
                "rollback_or_reversal_plan",
            ]
            suggested_user_instruction = (
                "After baseline target contract, version label, compileall, harness validation, and rollback plan are confirmed, "
                "manually update the regression baseline outside this demo."
            )
        return {
            "sync_handoff_item_id": f"SYNC-HANDOFF-{TRAINING_VERSION}-{index:03d}",
            "source_sync_audit_id": action.get("sync_audit_id", ""),
            "promotion_candidate_id": action.get("promotion_candidate_id", ""),
            "promotion_type": promotion_type,
            "target_system": target_system,
            "owner_role": owner_role,
            "execution_status": "waiting_manual_sync_execution",
            "manual_execution_required": True,
            "automatic_execution_allowed": False,
            "required_preflight_checks": required_preflight_checks,
            "execution_evidence_required": [
                "execution_reference",
                "changed_records",
                "validation_summary",
                "rollback_summary",
                "product_owner_confirmation",
            ],
            "suggested_user_instruction": suggested_user_instruction,
            "source_required_sync_checks": action.get("required_sync_checks", []),
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _codex_promotion_sync_handoff_hermes_payload(queue: dict) -> dict:
        return {
            "schema": "hermes.codex_promotion_sync_handoff_queue.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if queue.get("handoff_ready") else "candidate",
            "version": TRAINING_VERSION,
            "handoff_id": queue["handoff_id"],
            "source_sync_review_gate_id": queue.get("source_sync_review_gate_id"),
            "handoff_status": queue.get("handoff_status"),
            "handoff_item_count": queue.get("handoff_item_count", 0),
            "regression_sync_handoff_count": queue.get("regression_sync_handoff_count", 0),
            "hermes_sync_handoff_count": queue.get("hermes_sync_handoff_count", 0),
            "manual_execution_required": queue.get("manual_execution_required"),
            "automatic_execution_allowed": queue.get("automatic_execution_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_promotion_sync_handoff_kpis(queue: dict) -> list[dict]:
        return [
            {"kpi": "codex_promotion_sync_handoff_queue_ready", "value": queue["handoff_ready"], "target": True, "status": "ok" if queue["handoff_ready"] else "attention"},
            {"kpi": "codex_promotion_sync_handoff_item_count", "value": queue["handoff_item_count"], "target": "tracked", "status": "ok" if queue["handoff_item_count"] else "attention"},
            {"kpi": "codex_promotion_sync_handoff_hermes_count", "value": queue["hermes_sync_handoff_count"], "target": "tracked", "status": "ok" if queue["hermes_sync_handoff_count"] else "attention"},
            {"kpi": "codex_promotion_sync_handoff_regression_count", "value": queue["regression_sync_handoff_count"], "target": "tracked", "status": "ok" if queue["regression_sync_handoff_count"] else "attention"},
            {"kpi": "codex_promotion_sync_handoff_automatic_allowed", "value": queue["automatic_execution_allowed"], "target": False, "status": "ok" if queue["automatic_execution_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_promotion_sync_handoff_evidence(queue: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-SYNC-HANDOFF-001",
                "source": "athena.codex_promotion_sync_review_gate.v1",
                "summary": f"Prepared sync handoff queue {queue['handoff_status']} from sync review gate {queue.get('source_sync_review_gate_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-SYNC-HANDOFF-002",
                "source": "codex_promotion_sync_handoff_guardrail",
                "summary": "Sync handoff creates manual execution contracts only and blocks baseline updates, live Hermes writes, git actions, raw file storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _codex_promotion_sync_readiness_review_state(store: dict) -> dict:
        reviews = list(store.get("codex_promotion_sync_readiness_reviews", {}).values())
        confirmed = [item for item in reviews if item.get("review_status") == "confirmed_ready_for_manual_sync_execution"]
        return {
            "schema_id": "athena.codex_promotion_sync_readiness_review_state.v1",
            "version": store.get("version", TRAINING_VERSION),
            "updated_at": store.get("updated_at", ""),
            "readiness_review_count": len(reviews),
            "confirmed_ready_count": len(confirmed),
            "needs_inputs_count": len([item for item in reviews if item.get("review_status") == "needs_sync_execution_inputs"]),
            "deferred_count": len([item for item in reviews if item.get("review_status") == "deferred"]),
            "rejected_count": len([item for item in reviews if item.get("review_status") == "rejected"]),
            "note_count": len([item for item in reviews if item.get("review_status") == "note_only"]),
            "automatic_sync_execution_allowed": False,
            "manual_sync_execution_confirmation_only": True,
            "codex_promotion_sync_readiness_reviews": store.get("codex_promotion_sync_readiness_reviews", {}),
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _codex_promotion_sync_execution_readiness_gate(queue: dict, store: dict | None = None, payload: dict | None = None) -> dict:
        store = store or {}
        payload = payload or {}
        readiness_review_state = TrainingAutomationWorkflow._codex_promotion_sync_readiness_review_state(store)
        readiness_reviews = readiness_review_state.get("codex_promotion_sync_readiness_reviews", {})
        confirmed_by_item = payload.get("confirmed_inputs_by_item") or {}
        global_confirmed = payload.get("confirmed_inputs") or []
        if isinstance(global_confirmed, str):
            global_confirmed = [item.strip() for item in global_confirmed.split("|") if item.strip()]
        if not isinstance(confirmed_by_item, dict):
            confirmed_by_item = {}

        readiness_items = []
        for index, item in enumerate(queue.get("handoff_items", []), start=1):
            readiness_item_id = f"CODEX-PROMOTION-SYNC-READINESS-{TRAINING_VERSION}-{index:03d}"
            target_system = item.get("target_system", "")
            missing_inputs = [
                "explicit_product_owner_sync_execution_confirmation",
                "sync_execution_evidence_capture_plan",
                "rollback_or_reversal_plan",
            ]
            missing_inputs.extend(item.get("required_preflight_checks", []))
            missing_inputs.extend(item.get("execution_evidence_required", []))
            if target_system == "live_hermes_memory":
                missing_inputs.extend(
                    [
                        "live_hermes_endpoint",
                        "live_hermes_auth_scope",
                        "live_hermes_memory_schema",
                        "live_hermes_retention_policy",
                        "live_hermes_tenant_factory_scope",
                    ]
                )
            else:
                missing_inputs.extend(
                    [
                        "baseline_update_target_contract",
                        "baseline_version_label_confirmation",
                    ]
                )
            missing_inputs = list(dict.fromkeys(missing_inputs))

            item_confirmed = confirmed_by_item.get(readiness_item_id, [])
            if isinstance(item_confirmed, str):
                item_confirmed = [value.strip() for value in item_confirmed.split("|") if value.strip()]
            review = readiness_reviews.get(readiness_item_id, {})
            review_status = review.get("review_status", "pending_sync_readiness_review")
            confirmed_inputs = list(dict.fromkeys([*global_confirmed, *item_confirmed, *review.get("confirmed_inputs", [])]))
            remaining_inputs = [value for value in missing_inputs if value not in confirmed_inputs]
            if review_status == "confirmed_ready_for_manual_sync_execution" and not remaining_inputs:
                item_readiness_status = "sync_execution_prerequisites_confirmed"
            elif review_status == "rejected":
                item_readiness_status = "blocked_by_sync_readiness_review_rejection"
            elif review_status == "deferred":
                item_readiness_status = "deferred_by_sync_readiness_review"
            elif review_status == "needs_sync_execution_inputs":
                item_readiness_status = "blocked_needs_sync_execution_inputs"
            else:
                item_readiness_status = "blocked_missing_sync_execution_prerequisites"
            readiness_items.append(
                {
                    "readiness_item_id": readiness_item_id,
                    "source_sync_handoff_item_id": item.get("sync_handoff_item_id", ""),
                    "source_sync_audit_id": item.get("source_sync_audit_id", ""),
                    "promotion_candidate_id": item.get("promotion_candidate_id", ""),
                    "promotion_type": item.get("promotion_type", ""),
                    "target_system": target_system,
                    "owner_role": item.get("owner_role", ""),
                    "readiness_status": item_readiness_status,
                    "manual_sync_execution_required": True,
                    "automatic_sync_execution_allowed": False,
                    "missing_readiness_inputs": remaining_inputs,
                    "original_missing_readiness_inputs": missing_inputs,
                    "confirmed_inputs": confirmed_inputs,
                    "readiness_review": {
                        "review_status": review_status,
                        "review_note": review.get("review_note", ""),
                        "reviewer": review.get("reviewer", ""),
                        "updated_at": review.get("updated_at", ""),
                        "confirmed_inputs": review.get("confirmed_inputs", []),
                        "validation_summary": review.get("validation_summary", ""),
                        "rollback_summary": review.get("rollback_summary", ""),
                        "execution_evidence_plan": review.get("execution_evidence_plan", ""),
                    },
                    "required_preflight_checks": item.get("required_preflight_checks", []),
                    "execution_evidence_required": item.get("execution_evidence_required", []),
                    "suggested_user_instruction": item.get("suggested_user_instruction", ""),
                    "retention_policy": "training_lifecycle",
                    "sensitivity_level": "internal",
                    "contains_raw_file": False,
                    "contains_credentials": False,
                }
            )

        unconfirmed_count = len([item for item in readiness_items if item["readiness_status"] != "sync_execution_prerequisites_confirmed"])
        blocked_count = len([item for item in readiness_items if item.get("missing_readiness_inputs")])
        rejected_count = len([item for item in readiness_items if item["readiness_status"] == "blocked_by_sync_readiness_review_rejection"])
        if readiness_items and unconfirmed_count == 0:
            readiness_status = "ready_for_manual_sync_execution_confirmation"
        elif readiness_items and rejected_count:
            readiness_status = "blocked_by_sync_readiness_review_rejection"
        elif readiness_items:
            readiness_status = "blocked_until_sync_execution_prerequisites_confirmed"
        elif queue.get("handoff_status") in {
            "blocked_until_promotion_closure_ready",
            "blocked_until_sync_review_approval",
            "blocked_by_sync_review_rejection",
            "blocked_until_sync_reviews_ready",
        }:
            readiness_status = queue.get("handoff_status")
        else:
            readiness_status = "blocked_until_sync_handoff_ready"

        blocked_actions = [
            "auto_execute_sync_readiness_gate",
            "auto_update_regression_baseline_from_sync_readiness",
            "auto_write_live_hermes_memory_from_sync_readiness",
            "auto_commit_push_or_open_pr_from_sync_readiness",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_promotion_sync_execution_readiness_gate.v1",
            "version": TRAINING_VERSION,
            "gate_id": f"CODEX-PROMOTION-SYNC-EXECUTION-READINESS-{TRAINING_VERSION}-TPI-001",
            "source_sync_handoff_id": queue.get("handoff_id"),
            "source_sync_handoff_status": queue.get("handoff_status"),
            "readiness_status": readiness_status,
            "readiness_ready": readiness_status == "ready_for_manual_sync_execution_confirmation",
            "readiness_item_count": len(readiness_items),
            "blocked_readiness_item_count": blocked_count,
            "unconfirmed_readiness_item_count": unconfirmed_count,
            "confirmed_readiness_item_count": len([item for item in readiness_items if item["readiness_status"] == "sync_execution_prerequisites_confirmed"]),
            "regression_sync_readiness_count": len([item for item in readiness_items if item.get("target_system") == "local_regression_baseline_store"]),
            "hermes_sync_readiness_count": len([item for item in readiness_items if item.get("target_system") == "live_hermes_memory"]),
            "manual_sync_execution_required": bool(readiness_items),
            "automatic_sync_execution_allowed": False,
            "readiness_items": readiness_items,
            "readiness_review_state": readiness_review_state,
            "decision_rules": [
                "sync handoff is not execution permission; sync readiness requires explicit product-owner confirmation, validation evidence, evidence-capture planning, and rollback planning",
                "regression baseline sync additionally requires baseline target and version-label confirmation",
                "live Hermes sync additionally requires endpoint, auth scope, memory schema, retention policy, and tenant/factory scope confirmation",
                "sync readiness review stores metadata only and can mark prerequisites confirmed, needs-inputs, deferred, rejected, or note-only",
                "sync readiness gate must not update baselines, write live Hermes memory, run git, store raw files, store credentials, or start real data integration",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _codex_promotion_sync_execution_readiness_hermes_payload(gate: dict) -> dict:
        return {
            "schema": "hermes.codex_promotion_sync_execution_readiness_gate.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if gate.get("readiness_item_count") else "candidate",
            "version": TRAINING_VERSION,
            "gate_id": gate["gate_id"],
            "source_sync_handoff_id": gate.get("source_sync_handoff_id"),
            "source_sync_handoff_status": gate.get("source_sync_handoff_status"),
            "readiness_status": gate.get("readiness_status"),
            "readiness_item_count": gate.get("readiness_item_count", 0),
            "blocked_readiness_item_count": gate.get("blocked_readiness_item_count", 0),
            "confirmed_readiness_item_count": gate.get("confirmed_readiness_item_count", 0),
            "readiness_review_count": gate.get("readiness_review_state", {}).get("readiness_review_count", 0),
            "manual_sync_execution_required": gate.get("manual_sync_execution_required"),
            "automatic_sync_execution_allowed": gate.get("automatic_sync_execution_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_promotion_sync_execution_readiness_kpis(gate: dict) -> list[dict]:
        return [
            {"kpi": "codex_promotion_sync_execution_readiness_ready", "value": gate["readiness_ready"], "target": True, "status": "ok" if gate["readiness_ready"] else "attention"},
            {"kpi": "codex_promotion_sync_execution_readiness_item_count", "value": gate["readiness_item_count"], "target": "tracked", "status": "ok" if gate["readiness_item_count"] else "attention"},
            {"kpi": "codex_promotion_sync_execution_blocked_item_count", "value": gate["blocked_readiness_item_count"], "target": 0, "status": "ok" if gate["blocked_readiness_item_count"] == 0 else "attention"},
            {"kpi": "codex_promotion_sync_execution_confirmed_count", "value": gate["confirmed_readiness_item_count"], "target": gate["readiness_item_count"], "status": "ok" if gate["readiness_item_count"] and gate["confirmed_readiness_item_count"] == gate["readiness_item_count"] else "attention"},
            {"kpi": "codex_promotion_sync_readiness_review_count", "value": gate["readiness_review_state"]["readiness_review_count"], "target": "tracked", "status": "ok" if gate["readiness_review_state"]["readiness_review_count"] else "attention"},
            {"kpi": "codex_promotion_sync_readiness_confirmed_count", "value": gate["readiness_review_state"]["confirmed_ready_count"], "target": gate["readiness_item_count"], "status": "ok" if gate["readiness_item_count"] and gate["readiness_review_state"]["confirmed_ready_count"] == gate["readiness_item_count"] else "attention"},
            {"kpi": "codex_promotion_sync_execution_automatic_allowed", "value": gate["automatic_sync_execution_allowed"], "target": False, "status": "ok" if gate["automatic_sync_execution_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_promotion_sync_execution_readiness_evidence(gate: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-SYNC-READINESS-001",
                "source": "athena.codex_promotion_sync_handoff_queue.v1",
                "summary": f"Evaluated sync execution readiness {gate['readiness_status']} from handoff queue {gate.get('source_sync_handoff_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-SYNC-READINESS-002",
                "source": "codex_promotion_sync_execution_readiness_guardrail",
                "summary": "Sync readiness identifies missing prerequisites only and blocks baseline updates, live Hermes writes, git actions, raw file storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _promotion_sync_execution_result_contract_status(result_status: str, changed_records: list[str], validation_results: list[dict]) -> dict:
        commands = [
            f"{item.get('command', '')} {item.get('summary', '')}".lower()
            for item in validation_results
            if item.get("status") == "passed"
        ]
        compileall_passed = any("compileall" in item for item in commands)
        harness_passed = any("harness" in item or "test_main_agent" in item for item in commands)
        changed_records_reported = bool(changed_records)
        contract_complete = result_status == "manual_sync_execution_recorded" and changed_records_reported and compileall_passed and harness_passed
        return {
            "contract_complete": contract_complete,
            "changed_records_reported": changed_records_reported,
            "compileall_passed": compileall_passed,
            "harness_passed": harness_passed,
            "missing_items": [
                item
                for item, ok in [
                    ("changed_records", changed_records_reported),
                    ("compileall_passed", compileall_passed),
                    ("harness_passed", harness_passed),
                ]
                if not ok
            ],
        }

    @staticmethod
    def _codex_promotion_sync_execution_result_state(store: dict) -> dict:
        results = list(store.get("codex_promotion_sync_execution_results", {}).values())
        recorded = [item for item in results if item.get("result_status") == "manual_sync_execution_recorded"]
        failed = [item for item in results if item.get("result_status") == "manual_sync_execution_failed"]
        skipped = [item for item in results if item.get("result_status") == "manual_sync_execution_skipped"]
        complete = [item for item in recorded if item.get("result_contract", {}).get("contract_complete")]
        return {
            "schema_id": "athena.codex_promotion_sync_execution_result_state.v1",
            "version": store.get("version", TRAINING_VERSION),
            "updated_at": store.get("updated_at", ""),
            "result_count": len(results),
            "manual_sync_execution_recorded_count": len(recorded),
            "manual_sync_execution_failed_count": len(failed),
            "manual_sync_execution_skipped_count": len(skipped),
            "contract_complete_count": len(complete),
            "automatic_sync_execution_allowed": False,
            "metadata_only": True,
            "codex_promotion_sync_execution_results": store.get("codex_promotion_sync_execution_results", {}),
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _codex_promotion_sync_execution_result_intake(store: dict, readiness_gate: dict) -> dict:
        result_state = TrainingAutomationWorkflow._codex_promotion_sync_execution_result_state(store)
        source_status = readiness_gate.get("readiness_status", "blocked_until_sync_handoff_ready")
        readiness_items = [
            item
            for item in readiness_gate.get("readiness_items", [])
            if item.get("readiness_status") == "sync_execution_prerequisites_confirmed"
        ]
        if result_state["manual_sync_execution_failed_count"]:
            intake_status = "sync_execution_result_failed"
        elif result_state["contract_complete_count"]:
            intake_status = "sync_execution_result_recorded"
        elif result_state["result_count"]:
            intake_status = "sync_execution_result_needs_review"
        elif readiness_gate.get("readiness_ready"):
            intake_status = "waiting_for_manual_sync_execution_result"
        elif source_status == "blocked_until_sync_execution_prerequisites_confirmed":
            intake_status = "blocked_until_sync_execution_readiness_confirmed"
        else:
            intake_status = "blocked_until_sync_execution_ready"

        blocked_actions = [
            "auto_execute_recorded_sync_result",
            "auto_update_regression_baseline_from_sync_result",
            "auto_write_live_hermes_memory_from_sync_result",
            "auto_commit_push_or_open_pr_from_sync_result",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_promotion_sync_execution_result_intake.v1",
            "version": TRAINING_VERSION,
            "intake_id": f"CODEX-PROMOTION-SYNC-EXECUTION-RESULT-INTAKE-{TRAINING_VERSION}-TPI-001",
            "source_readiness_gate_id": readiness_gate.get("gate_id"),
            "source_readiness_status": source_status,
            "intake_status": intake_status,
            "result_ready_for_review": result_state["result_count"] > 0,
            "manual_sync_execution_result_required": readiness_gate.get("readiness_ready", False),
            "automatic_sync_execution_allowed": False,
            "expected_result_count": len(readiness_items),
            "result_state": result_state,
            "result_count": result_state["result_count"],
            "contract_complete_count": result_state["contract_complete_count"],
            "codex_promotion_sync_execution_results": result_state["codex_promotion_sync_execution_results"],
            "decision_rules": [
                "sync execution result intake records metadata after an explicitly manual sync action outside the demo",
                "result intake must not update regression baselines, write live Hermes memory, commit, push, open PR, store raw files, or store credentials",
                "recorded sync results require changed record identifiers plus current compileall and test harness validation summaries before the contract is complete",
                "future baseline or Hermes sync closure must review these metadata records separately before any real-state claim is accepted",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _codex_promotion_sync_execution_result_hermes_payload(intake: dict) -> dict:
        return {
            "schema": "hermes.codex_promotion_sync_execution_result_intake.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if intake.get("result_count") else "candidate",
            "version": TRAINING_VERSION,
            "intake_id": intake["intake_id"],
            "source_readiness_gate_id": intake.get("source_readiness_gate_id"),
            "source_readiness_status": intake.get("source_readiness_status"),
            "intake_status": intake.get("intake_status"),
            "result_count": intake.get("result_count", 0),
            "contract_complete_count": intake.get("contract_complete_count", 0),
            "automatic_sync_execution_allowed": intake.get("automatic_sync_execution_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_promotion_sync_execution_result_kpis(intake: dict) -> list[dict]:
        return [
            {"kpi": "codex_promotion_sync_execution_result_count", "value": intake["result_count"], "target": "tracked", "status": "ok" if intake["result_count"] else "attention"},
            {"kpi": "codex_promotion_sync_execution_result_passed_count", "value": intake["result_state"]["manual_sync_execution_recorded_count"], "target": "tracked", "status": "ok" if intake["result_state"]["manual_sync_execution_recorded_count"] else "attention"},
            {"kpi": "codex_promotion_sync_execution_result_contract_complete_count", "value": intake["contract_complete_count"], "target": intake["result_count"], "status": "ok" if intake["result_count"] and intake["contract_complete_count"] == intake["result_count"] else "attention"},
            {"kpi": "codex_promotion_sync_execution_result_automatic_allowed", "value": intake["automatic_sync_execution_allowed"], "target": False, "status": "ok" if intake["automatic_sync_execution_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_promotion_sync_execution_result_evidence(intake: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-SYNC-EXECUTION-RESULT-001",
                "source": "athena.codex_promotion_sync_execution_readiness_gate.v1",
                "summary": f"Prepared sync execution result intake {intake['intake_status']} from readiness gate {intake.get('source_readiness_gate_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-SYNC-EXECUTION-RESULT-002",
                "source": "codex_promotion_sync_execution_result_guardrail",
                "summary": "Sync execution result intake stores metadata only and blocks baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _codex_promotion_sync_closure_audit(intake: dict, readiness_gate: dict) -> dict:
        results_by_readiness = intake.get("codex_promotion_sync_execution_results", {})
        readiness_items = [
            item
            for item in readiness_gate.get("readiness_items", [])
            if item.get("readiness_status") == "sync_execution_prerequisites_confirmed"
        ]
        expected_ids = {item.get("readiness_item_id") for item in readiness_items if item.get("readiness_item_id")}
        relevant_results = [
            result
            for result in results_by_readiness.values()
            if result.get("readiness_item_id") in expected_ids
        ]
        complete_results = [
            result
            for result in relevant_results
            if result.get("result_contract", {}).get("contract_complete")
        ]
        failed_results = [
            result
            for result in relevant_results
            if result.get("result_status") == "manual_sync_execution_failed"
        ]
        complete_ids = {result.get("readiness_item_id") for result in complete_results if result.get("readiness_item_id")}
        missing_results = [
            {
                "readiness_item_id": item.get("readiness_item_id", ""),
                "promotion_candidate_id": item.get("promotion_candidate_id", ""),
                "promotion_type": item.get("promotion_type", ""),
                "target_system": item.get("target_system", ""),
                "missing_reason": "complete_sync_execution_result_required",
            }
            for item in readiness_items
            if item.get("readiness_item_id") not in complete_ids
        ]
        final_closure_candidates = [
            {
                "final_closure_id": f"FINAL-SYNC-CLOSURE-{TRAINING_VERSION}-{index:03d}",
                "readiness_item_id": result.get("readiness_item_id", ""),
                "source_sync_audit_id": result.get("source_sync_audit_id", ""),
                "promotion_candidate_id": result.get("promotion_candidate_id", ""),
                "promotion_type": result.get("promotion_type", ""),
                "target_system": result.get("target_system", ""),
                "closure_candidate_status": "ready_for_final_manual_sync_review",
                "final_review_required": True,
                "automatic_final_sync_allowed": False,
                "changed_records": result.get("changed_records", []),
                "validation_summary": result.get("validation_summary", ""),
                "rollback_summary": result.get("rollback_summary", ""),
                "required_final_checks": [
                    "product_owner_final_sync_closure_confirmation",
                    "post_sync_validation_summary",
                    "rollback_reversal_verification",
                ],
                "retention_policy": "training_lifecycle",
                "sensitivity_level": "internal",
                "contains_raw_file": False,
                "contains_credentials": False,
            }
            for index, result in enumerate(complete_results, start=1)
        ]

        if failed_results:
            closure_status = "sync_closure_blocked_by_failed_result"
        elif readiness_items and expected_ids == complete_ids:
            closure_status = "sync_closure_ready_for_final_review"
        elif complete_results:
            closure_status = "sync_closure_partial_results"
        else:
            closure_status = "blocked_until_sync_execution_result_ready"

        blocked_actions = [
            "auto_mark_sync_complete_without_closure_audit",
            "auto_update_regression_baseline_from_sync_closure",
            "auto_write_live_hermes_memory_from_sync_closure",
            "auto_commit_push_or_open_pr_from_sync_closure",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_promotion_sync_closure_audit.v1",
            "version": TRAINING_VERSION,
            "audit_id": f"CODEX-PROMOTION-SYNC-CLOSURE-AUDIT-{TRAINING_VERSION}-TPI-001",
            "source_sync_execution_result_intake_id": intake.get("intake_id"),
            "source_readiness_gate_id": readiness_gate.get("gate_id"),
            "source_readiness_status": readiness_gate.get("readiness_status"),
            "closure_status": closure_status,
            "closure_ready": closure_status == "sync_closure_ready_for_final_review",
            "expected_result_count": len(readiness_items),
            "recorded_result_count": len(relevant_results),
            "complete_result_count": len(complete_results),
            "failed_result_count": len(failed_results),
            "missing_result_count": len(missing_results),
            "final_closure_candidate_count": len(final_closure_candidates),
            "future_real_sync_review_required": bool(final_closure_candidates),
            "automatic_sync_allowed": False,
            "automatic_final_sync_allowed": False,
            "missing_results": missing_results,
            "failed_results": failed_results,
            "final_sync_closure_candidates": final_closure_candidates,
            "decision_rules": [
                "sync closure audit can only close after every confirmed sync readiness item has a complete metadata-only manual sync execution result",
                "failed sync execution results block closure until a reviewer records a corrected result or explicitly defers the item",
                "closure-ready means ready for final manual sync review only; it is not permission to update a baseline or write live Hermes memory",
                "final real-state sync requires separate endpoint, schema, tenant/factory scope, auth, retention, and rollback confirmation outside the demo",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _codex_promotion_sync_closure_audit_hermes_payload(audit: dict) -> dict:
        return {
            "schema": "hermes.codex_promotion_sync_closure_audit.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if audit.get("closure_ready") else "candidate",
            "version": TRAINING_VERSION,
            "audit_id": audit["audit_id"],
            "source_sync_execution_result_intake_id": audit.get("source_sync_execution_result_intake_id"),
            "source_readiness_gate_id": audit.get("source_readiness_gate_id"),
            "closure_status": audit.get("closure_status"),
            "expected_result_count": audit.get("expected_result_count", 0),
            "complete_result_count": audit.get("complete_result_count", 0),
            "final_closure_candidate_count": audit.get("final_closure_candidate_count", 0),
            "automatic_sync_allowed": audit.get("automatic_sync_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_promotion_sync_closure_audit_kpis(audit: dict) -> list[dict]:
        return [
            {"kpi": "codex_promotion_sync_closure_ready", "value": audit["closure_ready"], "target": True, "status": "ok" if audit["closure_ready"] else "attention"},
            {"kpi": "codex_promotion_sync_closure_expected_result_count", "value": audit["expected_result_count"], "target": "tracked", "status": "ok" if audit["expected_result_count"] else "attention"},
            {"kpi": "codex_promotion_sync_closure_complete_result_count", "value": audit["complete_result_count"], "target": audit["expected_result_count"], "status": "ok" if audit["expected_result_count"] and audit["complete_result_count"] == audit["expected_result_count"] else "attention"},
            {"kpi": "codex_promotion_sync_closure_missing_result_count", "value": audit["missing_result_count"], "target": 0, "status": "ok" if audit["missing_result_count"] == 0 else "attention"},
            {"kpi": "codex_promotion_sync_closure_automatic_allowed", "value": audit["automatic_sync_allowed"], "target": False, "status": "ok" if audit["automatic_sync_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_promotion_sync_closure_audit_evidence(audit: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-SYNC-CLOSURE-001",
                "source": "athena.codex_promotion_sync_execution_result_intake.v1",
                "summary": f"Audited sync closure {audit['closure_status']} from result intake {audit.get('source_sync_execution_result_intake_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-SYNC-CLOSURE-002",
                "source": "codex_promotion_sync_closure_guardrail",
                "summary": "Sync closure audit prepares final review candidates only and blocks baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _codex_promotion_sync_closure_review_state(store: dict) -> dict:
        reviews = list(store.get("codex_promotion_sync_closure_reviews", {}).values())
        approved = [item for item in reviews if item.get("review_status") == "approved_for_final_sync"]
        needs_inputs = [item for item in reviews if item.get("review_status") == "needs_final_sync_inputs"]
        deferred = [item for item in reviews if item.get("review_status") == "deferred"]
        rejected = [item for item in reviews if item.get("review_status") == "rejected"]
        note_only = [item for item in reviews if item.get("review_status") == "note_only"]
        return {
            "schema_id": "athena.codex_promotion_sync_closure_review_state.v1",
            "version": store.get("version", TRAINING_VERSION),
            "updated_at": store.get("updated_at", ""),
            "closure_review_count": len(reviews),
            "approved_for_final_sync_count": len(approved),
            "needs_final_sync_inputs_count": len(needs_inputs),
            "deferred_count": len(deferred),
            "rejected_count": len(rejected),
            "note_count": len(note_only),
            "automatic_final_sync_allowed": False,
            "manual_final_sync_review_only": True,
            "metadata_only": True,
            "codex_promotion_sync_closure_reviews": store.get("codex_promotion_sync_closure_reviews", {}),
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _codex_promotion_sync_closure_review_gate(audit: dict, store: dict) -> dict:
        review_state = TrainingAutomationWorkflow._codex_promotion_sync_closure_review_state(store)
        reviews = review_state["codex_promotion_sync_closure_reviews"]
        candidates = []
        for candidate in audit.get("final_sync_closure_candidates", []):
            final_closure_id = candidate.get("final_closure_id", "")
            review = reviews.get(final_closure_id, {})
            review_status = review.get("review_status", "pending_sync_closure_review")
            required_checks = candidate.get("required_final_checks", [])
            confirmed_checks = review.get("confirmed_final_checks", [])
            remaining_checks = [item for item in required_checks if item not in confirmed_checks]
            if review_status == "approved_for_final_sync" and not remaining_checks:
                candidate_status = "approved_but_not_executed"
            elif review_status in {"approved_for_final_sync", "needs_final_sync_inputs"}:
                candidate_status = "blocked_needs_final_sync_inputs"
            elif review_status == "deferred":
                candidate_status = "deferred_by_sync_closure_review"
            elif review_status == "rejected":
                candidate_status = "blocked_by_sync_closure_review_rejection"
            elif review_status == "note_only":
                candidate_status = "sync_closure_review_note_recorded"
            else:
                candidate_status = "pending_sync_closure_review"
            candidates.append(
                {
                    **candidate,
                    "sync_closure_review_status": candidate_status,
                    "remaining_final_checks": remaining_checks,
                    "sync_closure_review": {
                        "review_status": review_status,
                        "review_note": review.get("review_note", ""),
                        "reviewer": review.get("reviewer", ""),
                        "updated_at": review.get("updated_at", ""),
                        "confirmed_final_checks": confirmed_checks,
                        "validation_summary": review.get("validation_summary", ""),
                        "rollback_summary": review.get("rollback_summary", ""),
                    },
                }
            )

        approved_candidates = [item for item in candidates if item["sync_closure_review_status"] == "approved_but_not_executed"]
        rejected_candidates = [item for item in candidates if item["sync_closure_review_status"] == "blocked_by_sync_closure_review_rejection"]
        needs_input_candidates = [item for item in candidates if item["sync_closure_review_status"] == "blocked_needs_final_sync_inputs"]
        if not audit.get("closure_ready"):
            gate_status = "blocked_until_sync_closure_ready"
        elif rejected_candidates:
            gate_status = "blocked_by_sync_closure_review_rejection"
        elif candidates and len(approved_candidates) == len(candidates):
            gate_status = "sync_closure_reviews_approved_for_future_execution"
        elif review_state["closure_review_count"]:
            gate_status = "sync_closure_review_in_progress"
        elif candidates:
            gate_status = "ready_for_sync_closure_review"
        else:
            gate_status = "blocked_no_sync_closure_candidates"

        future_action_plan = [
            TrainingAutomationWorkflow._final_sync_action_plan_item(index, item)
            for index, item in enumerate(approved_candidates, start=1)
        ]
        blocked_actions = [
            "auto_execute_final_sync_closure_review",
            "auto_update_regression_baseline_from_sync_closure_review",
            "auto_write_live_hermes_memory_from_sync_closure_review",
            "auto_commit_push_or_open_pr_from_sync_closure_review",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_promotion_sync_closure_review_gate.v1",
            "version": TRAINING_VERSION,
            "gate_id": f"CODEX-PROMOTION-SYNC-CLOSURE-REVIEW-GATE-{TRAINING_VERSION}-TPI-001",
            "source_sync_closure_audit_id": audit.get("audit_id", ""),
            "source_sync_closure_status": audit.get("closure_status", ""),
            "gate_status": gate_status,
            "gate_ready": audit.get("closure_ready", False) and bool(candidates),
            "candidate_count": len(candidates),
            "sync_closure_review_candidate_count": len(candidates),
            "approved_final_sync_count": len(approved_candidates),
            "approved_future_sync_count": len(approved_candidates),
            "needs_final_sync_inputs_count": len(needs_input_candidates),
            "rejected_final_sync_count": len(rejected_candidates),
            "future_real_sync_action_count": len(future_action_plan),
            "future_sync_action_count": len(future_action_plan),
            "future_real_sync_action_plan": future_action_plan,
            "sync_closure_review_candidates": candidates,
            "sync_closure_review_state": review_state,
            "manual_final_sync_review_required": bool(candidates),
            "automatic_final_sync_allowed": False,
            "automatic_sync_allowed": False,
            "metadata_only": True,
            "contains_raw_file": False,
            "contains_credentials": False,
            "decision_rules": [
                "sync closure review can approve future synchronization actions only as metadata",
                "approved final sync closure candidates remain approved_but_not_executed until real endpoint, schema, auth, tenant/factory scope, retention, validation, and rollback inputs are confirmed outside this demo",
                "local regression baseline candidates require baseline target/store, version label, fresh validation, and rollback planning before baseline update",
                "live Hermes memory candidates require endpoint, auth scope, memory schema, retention policy, tenant/factory scope, fresh validation, and rollback planning before live write",
                "sync closure review must not update baselines, write live Hermes memory, run git, store raw files, store credentials, or start real data integration",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _final_sync_action_plan_item(index: int, candidate: dict) -> dict:
        target_system = candidate.get("target_system", "")
        if target_system == "live_hermes_memory":
            owner_role = "hermes_admin"
            required_real_sync_inputs = [
                "live_hermes_endpoint",
                "live_hermes_auth_scope",
                "live_hermes_memory_schema",
                "live_hermes_retention_policy",
                "live_hermes_tenant_factory_scope",
                "live_hermes_rollback_plan",
                "post_sync_validation_summary",
            ]
        else:
            owner_role = "regression_maintainer"
            required_real_sync_inputs = [
                "baseline_update_endpoint_or_store",
                "baseline_version_label",
                "baseline_rollback_plan",
                "post_sync_validation_summary",
            ]
        return {
            "action_id": f"FINAL-SYNC-ACTION-{TRAINING_VERSION}-{index:03d}",
            "final_closure_id": candidate.get("final_closure_id", ""),
            "readiness_item_id": candidate.get("readiness_item_id", ""),
            "source_sync_audit_id": candidate.get("source_sync_audit_id", ""),
            "promotion_candidate_id": candidate.get("promotion_candidate_id", ""),
            "promotion_type": candidate.get("promotion_type", ""),
            "target_system": target_system,
            "owner_role": owner_role,
            "execution_status": "approved_but_not_executed",
            "manual_execution_required": True,
            "automatic_final_sync_allowed": False,
            "required_final_checks": candidate.get("required_final_checks", []),
            "required_real_sync_inputs": required_real_sync_inputs,
            "changed_records": candidate.get("changed_records", []),
            "validation_summary": candidate.get("validation_summary", ""),
            "rollback_summary": candidate.get("rollback_summary", ""),
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _codex_promotion_sync_closure_review_hermes_payload(gate: dict) -> dict:
        return {
            "schema": "hermes.codex_promotion_sync_closure_review_gate.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if gate.get("future_real_sync_action_count") else "candidate",
            "version": TRAINING_VERSION,
            "gate_id": gate["gate_id"],
            "source_sync_closure_audit_id": gate.get("source_sync_closure_audit_id"),
            "gate_status": gate.get("gate_status"),
            "candidate_count": gate.get("candidate_count", 0),
            "approved_final_sync_count": gate.get("approved_final_sync_count", 0),
            "future_real_sync_action_count": gate.get("future_real_sync_action_count", 0),
            "automatic_final_sync_allowed": gate.get("automatic_final_sync_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_promotion_sync_closure_review_kpis(gate: dict) -> list[dict]:
        return [
            {"kpi": "codex_promotion_sync_closure_review_gate_ready", "value": gate["gate_ready"], "target": True, "status": "ok" if gate["gate_ready"] else "attention"},
            {"kpi": "codex_promotion_sync_closure_review_candidate_count", "value": gate["candidate_count"], "target": "tracked", "status": "ok" if gate["candidate_count"] else "attention"},
            {"kpi": "codex_promotion_sync_closure_review_count", "value": gate["sync_closure_review_state"]["closure_review_count"], "target": gate["candidate_count"], "status": "ok" if gate["candidate_count"] and gate["sync_closure_review_state"]["closure_review_count"] >= gate["candidate_count"] else "attention"},
            {"kpi": "codex_promotion_sync_closure_approved_count", "value": gate["approved_final_sync_count"], "target": gate["candidate_count"], "status": "ok" if gate["candidate_count"] and gate["approved_final_sync_count"] == gate["candidate_count"] else "attention"},
            {"kpi": "codex_promotion_sync_closure_review_automatic_allowed", "value": gate["automatic_final_sync_allowed"], "target": False, "status": "ok" if gate["automatic_final_sync_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_promotion_sync_closure_review_evidence(gate: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-SYNC-CLOSURE-REVIEW-001",
                "source": "athena.codex_promotion_sync_closure_audit.v1",
                "summary": f"Prepared final sync closure review gate {gate['gate_status']} from sync closure audit {gate.get('source_sync_closure_audit_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-SYNC-CLOSURE-REVIEW-002",
                "source": "codex_promotion_sync_closure_review_guardrail",
                "summary": "Final sync closure review stores metadata only and blocks baseline updates, live Hermes writes, git actions, raw file storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _codex_promotion_final_sync_handoff_queue(gate: dict) -> dict:
        future_actions = gate.get("future_real_sync_action_plan", [])
        handoff_items = [
            TrainingAutomationWorkflow._final_sync_handoff_item(index, item)
            for index, item in enumerate(future_actions, start=1)
        ]
        gate_status = gate.get("gate_status", "")
        if handoff_items:
            handoff_status = "ready_for_manual_final_sync_handoff"
        elif gate_status == "blocked_until_sync_closure_ready":
            handoff_status = "blocked_until_sync_closure_ready"
        elif gate_status in {"ready_for_sync_closure_review", "sync_closure_review_in_progress"}:
            handoff_status = "blocked_until_sync_closure_review_approval"
        elif gate_status == "blocked_by_sync_closure_review_rejection":
            handoff_status = "blocked_by_sync_closure_review_rejection"
        else:
            handoff_status = "blocked_until_final_sync_actions_ready"

        blocked_actions = [
            "auto_execute_final_sync_handoff",
            "auto_update_regression_baseline_from_final_sync_handoff",
            "auto_write_live_hermes_memory_from_final_sync_handoff",
            "auto_commit_push_or_open_pr_from_final_sync_handoff",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_promotion_final_sync_handoff_queue.v1",
            "version": TRAINING_VERSION,
            "handoff_id": f"CODEX-PROMOTION-FINAL-SYNC-HANDOFF-{TRAINING_VERSION}-TPI-001",
            "source_sync_closure_review_gate_id": gate.get("gate_id", ""),
            "source_sync_closure_review_status": gate_status,
            "handoff_status": handoff_status,
            "handoff_ready": bool(handoff_items),
            "handoff_item_count": len(handoff_items),
            "regression_final_sync_handoff_count": len([item for item in handoff_items if item.get("target_system") == "local_regression_baseline_store"]),
            "hermes_final_sync_handoff_count": len([item for item in handoff_items if item.get("target_system") == "live_hermes_memory"]),
            "manual_execution_required": bool(handoff_items),
            "automatic_execution_allowed": False,
            "handoff_items": handoff_items,
            "decision_rules": [
                "final sync handoff converts approved sync closure review actions into manual execution contracts only",
                "handoff items must keep target system, owner role, real-sync inputs, suggested instruction, and required execution evidence visible",
                "baseline final sync handoff still requires target/store contract, version label, validation, and rollback confirmation before any baseline update",
                "Hermes final sync handoff still requires endpoint, auth scope, memory schema, retention policy, tenant/factory scope, validation, and rollback confirmation before any live write",
                "final sync handoff must not update regression baselines, write live Hermes memory, run git, store raw files, store credentials, or start real data integration",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _final_sync_handoff_item(index: int, action: dict) -> dict:
        target_system = action.get("target_system", "")
        owner_role = action.get("owner_role", "")
        if target_system == "live_hermes_memory":
            suggested_user_instruction = (
                "After live Hermes endpoint, auth scope, memory schema, retention policy, tenant/factory scope, "
                "rollback plan, and post-sync validation evidence are confirmed, manually execute the final Hermes memory sync outside this demo."
            )
        else:
            suggested_user_instruction = (
                "After baseline target/store contract, version label, rollback plan, and post-sync validation evidence are confirmed, "
                "manually update the regression baseline outside this demo."
            )
        return {
            "final_sync_handoff_item_id": f"FINAL-SYNC-HANDOFF-{TRAINING_VERSION}-{index:03d}",
            "source_action_id": action.get("action_id", ""),
            "final_closure_id": action.get("final_closure_id", ""),
            "readiness_item_id": action.get("readiness_item_id", ""),
            "source_sync_audit_id": action.get("source_sync_audit_id", ""),
            "promotion_candidate_id": action.get("promotion_candidate_id", ""),
            "promotion_type": action.get("promotion_type", ""),
            "target_system": target_system,
            "owner_role": owner_role,
            "execution_status": "waiting_manual_final_sync_execution",
            "manual_execution_required": True,
            "automatic_execution_allowed": False,
            "required_real_sync_inputs": action.get("required_real_sync_inputs", []),
            "execution_evidence_required": [
                "execution_reference",
                "changed_records",
                "post_sync_validation_summary",
                "rollback_summary",
                "product_owner_confirmation",
            ],
            "suggested_user_instruction": suggested_user_instruction,
            "source_required_final_checks": action.get("required_final_checks", []),
            "source_changed_records": action.get("changed_records", []),
            "source_validation_summary": action.get("validation_summary", ""),
            "source_rollback_summary": action.get("rollback_summary", ""),
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _codex_promotion_final_sync_handoff_hermes_payload(queue: dict) -> dict:
        return {
            "schema": "hermes.codex_promotion_final_sync_handoff_queue.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if queue.get("handoff_ready") else "candidate",
            "version": TRAINING_VERSION,
            "handoff_id": queue["handoff_id"],
            "source_sync_closure_review_gate_id": queue.get("source_sync_closure_review_gate_id"),
            "handoff_status": queue.get("handoff_status"),
            "handoff_item_count": queue.get("handoff_item_count", 0),
            "regression_final_sync_handoff_count": queue.get("regression_final_sync_handoff_count", 0),
            "hermes_final_sync_handoff_count": queue.get("hermes_final_sync_handoff_count", 0),
            "manual_execution_required": queue.get("manual_execution_required"),
            "automatic_execution_allowed": queue.get("automatic_execution_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_promotion_final_sync_handoff_kpis(queue: dict) -> list[dict]:
        return [
            {"kpi": "codex_promotion_final_sync_handoff_queue_ready", "value": queue["handoff_ready"], "target": True, "status": "ok" if queue["handoff_ready"] else "attention"},
            {"kpi": "codex_promotion_final_sync_handoff_item_count", "value": queue["handoff_item_count"], "target": "tracked", "status": "ok" if queue["handoff_item_count"] else "attention"},
            {"kpi": "codex_promotion_final_sync_handoff_hermes_count", "value": queue["hermes_final_sync_handoff_count"], "target": "tracked", "status": "ok" if queue["hermes_final_sync_handoff_count"] else "attention"},
            {"kpi": "codex_promotion_final_sync_handoff_regression_count", "value": queue["regression_final_sync_handoff_count"], "target": "tracked", "status": "ok" if queue["regression_final_sync_handoff_count"] else "attention"},
            {"kpi": "codex_promotion_final_sync_handoff_automatic_allowed", "value": queue["automatic_execution_allowed"], "target": False, "status": "ok" if queue["automatic_execution_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_promotion_final_sync_handoff_evidence(queue: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-FINAL-SYNC-HANDOFF-001",
                "source": "athena.codex_promotion_sync_closure_review_gate.v1",
                "summary": f"Prepared final sync handoff queue {queue['handoff_status']} from sync closure review gate {queue.get('source_sync_closure_review_gate_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-FINAL-SYNC-HANDOFF-002",
                "source": "codex_promotion_final_sync_handoff_guardrail",
                "summary": "Final sync handoff creates manual execution contracts only and blocks baseline updates, live Hermes writes, git actions, raw file storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _confirmed_final_sync_inputs(payload: dict | None) -> list[str]:
        payload = payload or {}
        raw_inputs = payload.get("confirmed_real_sync_inputs") or payload.get("confirmed_inputs") or []
        if isinstance(raw_inputs, str):
            raw_inputs = [item.strip() for item in raw_inputs.split("|") if item.strip()]
        if not isinstance(raw_inputs, list):
            raw_inputs = []
        return [str(item).strip() for item in raw_inputs if str(item).strip()]

    @staticmethod
    def _codex_promotion_final_sync_execution_readiness_gate(queue: dict, payload: dict | None = None) -> dict:
        confirmed_inputs = TrainingAutomationWorkflow._confirmed_final_sync_inputs(payload)
        readiness_items = [
            TrainingAutomationWorkflow._final_sync_execution_readiness_item(index, item, confirmed_inputs)
            for index, item in enumerate(queue.get("handoff_items", []), start=1)
        ]
        handoff_status = queue.get("handoff_status", "")
        confirmed_count = len([item for item in readiness_items if item["readiness_status"] == "final_sync_execution_prerequisites_confirmed"])
        blocked_count = len([item for item in readiness_items if item.get("missing_real_sync_inputs")])
        if readiness_items and confirmed_count == len(readiness_items):
            readiness_status = "ready_for_manual_final_sync_execution_confirmation"
        elif readiness_items:
            readiness_status = "blocked_until_final_sync_execution_prerequisites_confirmed"
        elif handoff_status == "blocked_until_sync_closure_ready":
            readiness_status = "blocked_until_sync_closure_ready"
        elif handoff_status == "blocked_until_sync_closure_review_approval":
            readiness_status = "blocked_until_sync_closure_review_approval"
        elif handoff_status == "blocked_by_sync_closure_review_rejection":
            readiness_status = "blocked_by_sync_closure_review_rejection"
        else:
            readiness_status = "blocked_until_final_sync_handoff_ready"

        blocked_actions = [
            "auto_execute_final_sync_execution_readiness",
            "auto_update_regression_baseline_from_final_sync_readiness",
            "auto_write_live_hermes_memory_from_final_sync_readiness",
            "auto_commit_push_or_open_pr_from_final_sync_readiness",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_promotion_final_sync_execution_readiness_gate.v1",
            "version": TRAINING_VERSION,
            "gate_id": f"CODEX-PROMOTION-FINAL-SYNC-READINESS-GATE-{TRAINING_VERSION}-TPI-001",
            "source_final_sync_handoff_id": queue.get("handoff_id", ""),
            "source_final_sync_handoff_status": handoff_status,
            "readiness_status": readiness_status,
            "readiness_ready": readiness_status == "ready_for_manual_final_sync_execution_confirmation",
            "readiness_item_count": len(readiness_items),
            "blocked_readiness_item_count": blocked_count,
            "confirmed_readiness_item_count": confirmed_count,
            "regression_final_sync_readiness_count": len([item for item in readiness_items if item.get("target_system") == "local_regression_baseline_store"]),
            "hermes_final_sync_readiness_count": len([item for item in readiness_items if item.get("target_system") == "live_hermes_memory"]),
            "confirmed_real_sync_inputs": confirmed_inputs,
            "manual_final_sync_execution_required": bool(readiness_items),
            "automatic_execution_allowed": False,
            "readiness_items": readiness_items,
            "metadata_only": True,
            "contains_raw_file": False,
            "contains_credentials": False,
            "decision_rules": [
                "final sync execution readiness can only evaluate prerequisites for a future manual action",
                "readiness requires target-system contract details, explicit product-owner execution confirmation, rollback planning, current validation output, and execution evidence plan before any real-state change is considered",
                "local regression baseline final sync must not run until baseline store, version label, rollback, validation, and owner confirmation are present",
                "live Hermes final sync must not run until endpoint, auth scope, memory schema, retention policy, tenant/factory scope, rollback, validation, and owner confirmation are present",
                "final sync execution readiness must not update baselines, write live Hermes memory, run git, store raw files, store credentials, or start real data integration",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _final_sync_execution_readiness_item(index: int, handoff_item: dict, confirmed_inputs: list[str]) -> dict:
        required_inputs = list(dict.fromkeys(
            [
                *handoff_item.get("required_real_sync_inputs", []),
                "explicit_product_owner_final_sync_execution_confirmation",
                "current_compileall_validation_output",
                "current_test_harness_validation_output",
                "execution_evidence_capture_plan",
            ]
        ))
        missing_inputs = [item for item in required_inputs if item not in confirmed_inputs]
        readiness_status = (
            "final_sync_execution_prerequisites_confirmed"
            if not missing_inputs
            else "blocked_missing_final_sync_execution_prerequisites"
        )
        return {
            "readiness_item_id": f"FINAL-SYNC-READINESS-{TRAINING_VERSION}-{index:03d}",
            "source_final_sync_handoff_item_id": handoff_item.get("final_sync_handoff_item_id", ""),
            "source_action_id": handoff_item.get("source_action_id", ""),
            "final_closure_id": handoff_item.get("final_closure_id", ""),
            "readiness_item_source_id": handoff_item.get("readiness_item_id", ""),
            "source_sync_audit_id": handoff_item.get("source_sync_audit_id", ""),
            "promotion_candidate_id": handoff_item.get("promotion_candidate_id", ""),
            "promotion_type": handoff_item.get("promotion_type", ""),
            "target_system": handoff_item.get("target_system", ""),
            "owner_role": handoff_item.get("owner_role", ""),
            "readiness_status": readiness_status,
            "manual_final_sync_execution_required": True,
            "automatic_execution_allowed": False,
            "required_real_sync_inputs": required_inputs,
            "confirmed_real_sync_inputs": [item for item in confirmed_inputs if item in required_inputs],
            "missing_real_sync_inputs": missing_inputs,
            "execution_evidence_required": handoff_item.get("execution_evidence_required", []),
            "suggested_user_instruction": handoff_item.get("suggested_user_instruction", ""),
            "source_changed_records": handoff_item.get("source_changed_records", []),
            "source_validation_summary": handoff_item.get("source_validation_summary", ""),
            "source_rollback_summary": handoff_item.get("source_rollback_summary", ""),
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _codex_promotion_final_sync_execution_readiness_hermes_payload(gate: dict) -> dict:
        return {
            "schema": "hermes.codex_promotion_final_sync_execution_readiness_gate.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if gate.get("readiness_ready") else "candidate",
            "version": TRAINING_VERSION,
            "gate_id": gate["gate_id"],
            "source_final_sync_handoff_id": gate.get("source_final_sync_handoff_id"),
            "readiness_status": gate.get("readiness_status"),
            "readiness_item_count": gate.get("readiness_item_count", 0),
            "blocked_readiness_item_count": gate.get("blocked_readiness_item_count", 0),
            "confirmed_readiness_item_count": gate.get("confirmed_readiness_item_count", 0),
            "automatic_execution_allowed": gate.get("automatic_execution_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_promotion_final_sync_execution_readiness_kpis(gate: dict) -> list[dict]:
        return [
            {"kpi": "codex_promotion_final_sync_execution_readiness_ready", "value": gate["readiness_ready"], "target": True, "status": "ok" if gate["readiness_ready"] else "attention"},
            {"kpi": "codex_promotion_final_sync_execution_readiness_item_count", "value": gate["readiness_item_count"], "target": "tracked", "status": "ok" if gate["readiness_item_count"] else "attention"},
            {"kpi": "codex_promotion_final_sync_execution_blocked_item_count", "value": gate["blocked_readiness_item_count"], "target": 0, "status": "ok" if gate["blocked_readiness_item_count"] == 0 else "attention"},
            {"kpi": "codex_promotion_final_sync_execution_confirmed_count", "value": gate["confirmed_readiness_item_count"], "target": gate["readiness_item_count"], "status": "ok" if gate["readiness_item_count"] and gate["confirmed_readiness_item_count"] == gate["readiness_item_count"] else "attention"},
            {"kpi": "codex_promotion_final_sync_execution_automatic_allowed", "value": gate["automatic_execution_allowed"], "target": False, "status": "ok" if gate["automatic_execution_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_promotion_final_sync_execution_readiness_evidence(gate: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-FINAL-SYNC-READINESS-001",
                "source": "athena.codex_promotion_final_sync_handoff_queue.v1",
                "summary": f"Evaluated final sync execution readiness {gate['readiness_status']} from final sync handoff queue {gate.get('source_final_sync_handoff_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-FINAL-SYNC-READINESS-002",
                "source": "codex_promotion_final_sync_execution_readiness_guardrail",
                "summary": "Final sync execution readiness evaluates prerequisites only and blocks baseline updates, live Hermes writes, git actions, raw file storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _final_sync_execution_result_contract_status(result_status: str, changed_records: list[str], validation_results: list[dict]) -> dict:
        commands = [
            f"{item.get('command', '')} {item.get('summary', '')}".lower()
            for item in validation_results
            if item.get("status") == "passed"
        ]
        compileall_passed = any("compileall" in item for item in commands)
        harness_passed = any("harness" in item or "test_main_agent" in item for item in commands)
        changed_records_reported = bool(changed_records)
        contract_complete = result_status == "manual_final_sync_execution_recorded" and changed_records_reported and compileall_passed and harness_passed
        return {
            "contract_complete": contract_complete,
            "changed_records_reported": changed_records_reported,
            "compileall_passed": compileall_passed,
            "harness_passed": harness_passed,
            "missing_items": [
                item
                for item, ok in [
                    ("changed_records", changed_records_reported),
                    ("compileall_passed", compileall_passed),
                    ("harness_passed", harness_passed),
                ]
                if not ok
            ],
        }

    @staticmethod
    def _codex_promotion_final_sync_execution_result_state(store: dict) -> dict:
        results = list(store.get("codex_promotion_final_sync_execution_results", {}).values())
        recorded = [item for item in results if item.get("result_status") == "manual_final_sync_execution_recorded"]
        failed = [item for item in results if item.get("result_status") == "manual_final_sync_execution_failed"]
        skipped = [item for item in results if item.get("result_status") == "manual_final_sync_execution_skipped"]
        complete = [item for item in recorded if item.get("result_contract", {}).get("contract_complete")]
        return {
            "schema_id": "athena.codex_promotion_final_sync_execution_result_state.v1",
            "version": store.get("version", TRAINING_VERSION),
            "updated_at": store.get("updated_at", ""),
            "result_count": len(results),
            "manual_final_sync_execution_recorded_count": len(recorded),
            "manual_final_sync_execution_failed_count": len(failed),
            "manual_final_sync_execution_skipped_count": len(skipped),
            "contract_complete_count": len(complete),
            "automatic_execution_allowed": False,
            "metadata_only": True,
            "codex_promotion_final_sync_execution_results": store.get("codex_promotion_final_sync_execution_results", {}),
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _codex_promotion_final_sync_execution_result_intake(store: dict, readiness_gate: dict) -> dict:
        result_state = TrainingAutomationWorkflow._codex_promotion_final_sync_execution_result_state(store)
        source_status = readiness_gate.get("readiness_status", "blocked_until_final_sync_handoff_ready")
        readiness_items = [
            item
            for item in readiness_gate.get("readiness_items", [])
            if item.get("readiness_status") == "final_sync_execution_prerequisites_confirmed"
        ]
        if result_state["manual_final_sync_execution_failed_count"]:
            intake_status = "final_sync_execution_result_failed"
        elif result_state["contract_complete_count"]:
            intake_status = "final_sync_execution_result_recorded"
        elif result_state["result_count"]:
            intake_status = "final_sync_execution_result_needs_review"
        elif readiness_gate.get("readiness_ready"):
            intake_status = "waiting_for_manual_final_sync_execution_result"
        elif source_status == "blocked_until_final_sync_execution_prerequisites_confirmed":
            intake_status = "blocked_until_final_sync_execution_readiness_confirmed"
        else:
            intake_status = "blocked_until_final_sync_execution_ready"

        blocked_actions = [
            "auto_execute_recorded_final_sync_result",
            "auto_update_regression_baseline_from_final_sync_result",
            "auto_write_live_hermes_memory_from_final_sync_result",
            "auto_commit_push_or_open_pr_from_final_sync_result",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_promotion_final_sync_execution_result_intake.v1",
            "version": TRAINING_VERSION,
            "intake_id": f"CODEX-PROMOTION-FINAL-SYNC-EXECUTION-RESULT-INTAKE-{TRAINING_VERSION}-TPI-001",
            "source_readiness_gate_id": readiness_gate.get("gate_id"),
            "source_readiness_status": source_status,
            "intake_status": intake_status,
            "result_ready_for_review": result_state["result_count"] > 0,
            "manual_final_sync_execution_result_required": readiness_gate.get("readiness_ready", False),
            "automatic_execution_allowed": False,
            "expected_result_count": len(readiness_items),
            "result_state": result_state,
            "result_count": result_state["result_count"],
            "contract_complete_count": result_state["contract_complete_count"],
            "codex_promotion_final_sync_execution_results": result_state["codex_promotion_final_sync_execution_results"],
            "decision_rules": [
                "final sync execution result intake records metadata after an explicitly manual final sync action outside the demo",
                "result intake must not update regression baselines, write live Hermes memory, commit, push, open PR, store raw files, or store credentials",
                "recorded final sync results require changed record identifiers plus current compileall and test harness validation summaries before the contract is complete",
                "future completion claims must review these metadata records separately before any real baseline or Hermes sync success is accepted",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _codex_promotion_final_sync_execution_result_hermes_payload(intake: dict) -> dict:
        return {
            "schema": "hermes.codex_promotion_final_sync_execution_result_intake.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if intake.get("result_count") else "candidate",
            "version": TRAINING_VERSION,
            "intake_id": intake["intake_id"],
            "source_readiness_gate_id": intake.get("source_readiness_gate_id"),
            "source_readiness_status": intake.get("source_readiness_status"),
            "intake_status": intake.get("intake_status"),
            "result_count": intake.get("result_count", 0),
            "contract_complete_count": intake.get("contract_complete_count", 0),
            "automatic_execution_allowed": intake.get("automatic_execution_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_promotion_final_sync_execution_result_kpis(intake: dict) -> list[dict]:
        return [
            {"kpi": "codex_promotion_final_sync_execution_result_count", "value": intake["result_count"], "target": "tracked", "status": "ok" if intake["result_count"] else "attention"},
            {"kpi": "codex_promotion_final_sync_execution_result_passed_count", "value": intake["result_state"]["manual_final_sync_execution_recorded_count"], "target": "tracked", "status": "ok" if intake["result_state"]["manual_final_sync_execution_recorded_count"] else "attention"},
            {"kpi": "codex_promotion_final_sync_execution_result_contract_complete_count", "value": intake["contract_complete_count"], "target": intake["result_count"], "status": "ok" if intake["result_count"] and intake["contract_complete_count"] == intake["result_count"] else "attention"},
            {"kpi": "codex_promotion_final_sync_execution_result_automatic_allowed", "value": intake["automatic_execution_allowed"], "target": False, "status": "ok" if intake["automatic_execution_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_promotion_final_sync_execution_result_evidence(intake: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-FINAL-SYNC-EXECUTION-RESULT-001",
                "source": "athena.codex_promotion_final_sync_execution_readiness_gate.v1",
                "summary": f"Prepared final sync execution result intake {intake['intake_status']} from readiness gate {intake.get('source_readiness_gate_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-FINAL-SYNC-EXECUTION-RESULT-002",
                "source": "codex_promotion_final_sync_execution_result_guardrail",
                "summary": "Final sync execution result intake stores metadata only and blocks baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _codex_promotion_final_sync_closure_audit(intake: dict, readiness_gate: dict) -> dict:
        results_by_readiness = intake.get("codex_promotion_final_sync_execution_results", {})
        readiness_items = [
            item
            for item in readiness_gate.get("readiness_items", [])
            if item.get("readiness_status") == "final_sync_execution_prerequisites_confirmed"
        ]
        expected_ids = {item.get("readiness_item_id") for item in readiness_items if item.get("readiness_item_id")}
        relevant_results = [
            result
            for result in results_by_readiness.values()
            if result.get("readiness_item_id") in expected_ids
        ]
        complete_results = [
            result
            for result in relevant_results
            if result.get("result_contract", {}).get("contract_complete")
        ]
        failed_results = [
            result
            for result in relevant_results
            if result.get("result_status") == "manual_final_sync_execution_failed"
        ]
        complete_ids = {result.get("readiness_item_id") for result in complete_results if result.get("readiness_item_id")}
        recorded_ids = {result.get("readiness_item_id") for result in relevant_results if result.get("readiness_item_id")}
        missing_results = [
            {
                "readiness_item_id": item.get("readiness_item_id", ""),
                "promotion_candidate_id": item.get("promotion_candidate_id", ""),
                "promotion_type": item.get("promotion_type", ""),
                "target_system": item.get("target_system", ""),
                "missing_reason": "complete_final_sync_execution_result_required"
                if item.get("readiness_item_id") in recorded_ids
                else "final_sync_execution_result_missing",
            }
            for item in readiness_items
            if item.get("readiness_item_id") not in complete_ids
        ]
        final_closure_candidates = [
            {
                "final_sync_completion_id": f"FINAL-SYNC-COMPLETION-{TRAINING_VERSION}-{index:03d}",
                "readiness_item_id": result.get("readiness_item_id", ""),
                "source_final_sync_handoff_item_id": result.get("source_final_sync_handoff_item_id", ""),
                "source_action_id": result.get("source_action_id", ""),
                "final_closure_id": result.get("final_closure_id", ""),
                "source_sync_audit_id": result.get("source_sync_audit_id", ""),
                "promotion_candidate_id": result.get("promotion_candidate_id", ""),
                "promotion_type": result.get("promotion_type", ""),
                "target_system": result.get("target_system", ""),
                "closure_candidate_status": "metadata_ready_for_final_completion_review",
                "changed_records": result.get("changed_records", []),
                "validation_summary": result.get("validation_summary", ""),
                "rollback_summary": result.get("rollback_summary", ""),
                "required_completion_checks": [
                    "product_owner_final_completion_confirmation",
                    "post_final_sync_validation_summary",
                    "rollback_reversal_verification",
                    "no_raw_file_or_credentials",
                ],
                "retention_policy": "training_lifecycle",
                "sensitivity_level": "internal",
                "contains_raw_file": False,
                "contains_credentials": False,
            }
            for index, result in enumerate(complete_results, start=1)
        ]

        if failed_results:
            closure_status = "final_sync_closure_blocked_by_failed_result"
        elif readiness_items and expected_ids == complete_ids:
            closure_status = "final_sync_closure_ready_for_completion_review"
        elif complete_results:
            closure_status = "final_sync_closure_partial_results"
        else:
            closure_status = "blocked_until_final_sync_execution_result_ready"

        blocked_actions = [
            "auto_mark_final_sync_complete_without_closure_audit",
            "auto_update_regression_baseline_from_final_sync_closure",
            "auto_write_live_hermes_memory_from_final_sync_closure",
            "auto_commit_push_or_open_pr_from_final_sync_closure",
            "auto_publish_project_memory_from_final_sync_closure",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_promotion_final_sync_closure_audit.v1",
            "version": TRAINING_VERSION,
            "audit_id": f"CODEX-PROMOTION-FINAL-SYNC-CLOSURE-AUDIT-{TRAINING_VERSION}-TPI-001",
            "source_final_sync_execution_result_intake_id": intake.get("intake_id"),
            "source_readiness_gate_id": readiness_gate.get("gate_id"),
            "source_readiness_status": readiness_gate.get("readiness_status"),
            "closure_status": closure_status,
            "closure_ready": closure_status == "final_sync_closure_ready_for_completion_review",
            "expected_result_count": len(readiness_items),
            "recorded_result_count": len(relevant_results),
            "complete_result_count": len(complete_results),
            "failed_result_count": len(failed_results),
            "missing_result_count": len(missing_results),
            "final_closure_candidate_count": len(final_closure_candidates),
            "future_completion_review_required": bool(final_closure_candidates),
            "automatic_closure_allowed": False,
            "automatic_project_memory_write_allowed": False,
            "metadata_only": True,
            "contains_raw_file": False,
            "contains_credentials": False,
            "missing_results": missing_results,
            "failed_results": failed_results,
            "final_closure_candidates": final_closure_candidates,
            "decision_rules": [
                "final sync closure audit can only close after every confirmed final sync readiness item has a complete metadata-only manual final sync execution result",
                "failed final sync execution results block closure until a corrected result or explicit deferral is recorded",
                "closure-ready means ready for final completion review only; it is not permission to update a baseline, write live Hermes memory, publish project memory, or run git",
                "final completion claims require separate product-owner review and post-final-sync validation evidence outside this audit",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _codex_promotion_final_sync_closure_audit_hermes_payload(audit: dict) -> dict:
        return {
            "schema": "hermes.codex_promotion_final_sync_closure_audit.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if audit.get("closure_ready") else "candidate",
            "version": TRAINING_VERSION,
            "audit_id": audit["audit_id"],
            "source_final_sync_execution_result_intake_id": audit.get("source_final_sync_execution_result_intake_id"),
            "source_readiness_gate_id": audit.get("source_readiness_gate_id"),
            "closure_status": audit.get("closure_status"),
            "expected_result_count": audit.get("expected_result_count", 0),
            "complete_result_count": audit.get("complete_result_count", 0),
            "final_closure_candidate_count": audit.get("final_closure_candidate_count", 0),
            "automatic_closure_allowed": audit.get("automatic_closure_allowed"),
            "automatic_project_memory_write_allowed": audit.get("automatic_project_memory_write_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_promotion_final_sync_closure_audit_kpis(audit: dict) -> list[dict]:
        return [
            {"kpi": "codex_promotion_final_sync_closure_ready", "value": audit["closure_ready"], "target": True, "status": "ok" if audit["closure_ready"] else "attention"},
            {"kpi": "codex_promotion_final_sync_closure_expected_result_count", "value": audit["expected_result_count"], "target": "tracked", "status": "ok" if audit["expected_result_count"] else "attention"},
            {"kpi": "codex_promotion_final_sync_closure_complete_result_count", "value": audit["complete_result_count"], "target": audit["expected_result_count"], "status": "ok" if audit["expected_result_count"] and audit["complete_result_count"] == audit["expected_result_count"] else "attention"},
            {"kpi": "codex_promotion_final_sync_closure_missing_result_count", "value": audit["missing_result_count"], "target": 0, "status": "ok" if audit["missing_result_count"] == 0 else "attention"},
            {"kpi": "codex_promotion_final_sync_closure_automatic_allowed", "value": audit["automatic_closure_allowed"], "target": False, "status": "ok" if audit["automatic_closure_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_promotion_final_sync_closure_audit_evidence(audit: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-FINAL-SYNC-CLOSURE-001",
                "source": "athena.codex_promotion_final_sync_execution_result_intake.v1",
                "summary": f"Audited final sync closure {audit['closure_status']} from result intake {audit.get('source_final_sync_execution_result_intake_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-FINAL-SYNC-CLOSURE-002",
                "source": "codex_promotion_final_sync_closure_audit_guardrail",
                "summary": "Final sync closure audit prepares completion-review candidates only and blocks baseline updates, live Hermes writes, project-memory publication, commits, pushes, PRs, raw file storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _codex_promotion_final_completion_review_state(store: dict) -> dict:
        reviews = list(store.get("codex_promotion_final_completion_reviews", {}).values())
        approved = [item for item in reviews if item.get("review_status") == "approved_final_completion"]
        needs_inputs = [item for item in reviews if item.get("review_status") == "needs_completion_inputs"]
        deferred = [item for item in reviews if item.get("review_status") == "deferred"]
        rejected = [item for item in reviews if item.get("review_status") == "rejected"]
        note_only = [item for item in reviews if item.get("review_status") == "note_only"]
        return {
            "schema_id": "athena.codex_promotion_final_completion_review_state.v1",
            "version": store.get("version", TRAINING_VERSION),
            "updated_at": store.get("updated_at", ""),
            "final_completion_review_count": len(reviews),
            "approved_final_completion_count": len(approved),
            "needs_completion_inputs_count": len(needs_inputs),
            "deferred_count": len(deferred),
            "rejected_count": len(rejected),
            "note_count": len(note_only),
            "automatic_completion_allowed": False,
            "automatic_project_memory_write_allowed": False,
            "manual_final_completion_review_only": True,
            "metadata_only": True,
            "codex_promotion_final_completion_reviews": store.get("codex_promotion_final_completion_reviews", {}),
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _codex_promotion_final_completion_review_gate(audit: dict, store: dict) -> dict:
        review_state = TrainingAutomationWorkflow._codex_promotion_final_completion_review_state(store)
        reviews = review_state["codex_promotion_final_completion_reviews"]
        candidates = []
        for candidate in audit.get("final_closure_candidates", []):
            final_sync_completion_id = candidate.get("final_sync_completion_id", "")
            review = reviews.get(final_sync_completion_id, {})
            review_status = review.get("review_status", "pending_final_completion_review")
            required_checks = candidate.get("required_completion_checks", [])
            confirmed_checks = review.get("confirmed_completion_checks", [])
            remaining_checks = [item for item in required_checks if item not in confirmed_checks]
            if review_status == "approved_final_completion" and not remaining_checks:
                candidate_status = "approved_but_not_published"
            elif review_status in {"approved_final_completion", "needs_completion_inputs"}:
                candidate_status = "blocked_needs_completion_inputs"
            elif review_status == "deferred":
                candidate_status = "deferred_by_final_completion_review"
            elif review_status == "rejected":
                candidate_status = "blocked_by_final_completion_review_rejection"
            elif review_status == "note_only":
                candidate_status = "final_completion_review_note_recorded"
            else:
                candidate_status = "pending_final_completion_review"
            candidates.append(
                {
                    **candidate,
                    "final_completion_review_status": candidate_status,
                    "remaining_completion_checks": remaining_checks,
                    "final_completion_review": {
                        "review_status": review_status,
                        "review_note": review.get("review_note", ""),
                        "reviewer": review.get("reviewer", ""),
                        "updated_at": review.get("updated_at", ""),
                        "confirmed_completion_checks": confirmed_checks,
                        "validation_summary": review.get("validation_summary", ""),
                        "rollback_summary": review.get("rollback_summary", ""),
                    },
                }
            )

        approved_candidates = [item for item in candidates if item["final_completion_review_status"] == "approved_but_not_published"]
        rejected_candidates = [item for item in candidates if item["final_completion_review_status"] == "blocked_by_final_completion_review_rejection"]
        needs_input_candidates = [item for item in candidates if item["final_completion_review_status"] == "blocked_needs_completion_inputs"]
        if not audit.get("closure_ready"):
            gate_status = "blocked_until_final_sync_closure_ready"
        elif rejected_candidates:
            gate_status = "blocked_by_final_completion_review_rejection"
        elif candidates and len(approved_candidates) == len(candidates):
            gate_status = "final_completion_reviews_approved_for_future_publication"
        elif review_state["final_completion_review_count"]:
            gate_status = "final_completion_review_in_progress"
        elif candidates:
            gate_status = "ready_for_final_completion_review"
        else:
            gate_status = "blocked_no_final_completion_candidates"

        publication_plan = [
            TrainingAutomationWorkflow._final_completion_publication_plan_item(index, item)
            for index, item in enumerate(approved_candidates, start=1)
        ]
        blocked_actions = [
            "auto_execute_final_completion_review",
            "auto_update_regression_baseline_from_final_completion_review",
            "auto_write_live_hermes_memory_from_final_completion_review",
            "auto_publish_project_memory_from_final_completion_review",
            "auto_commit_push_or_open_pr_from_final_completion_review",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_promotion_final_completion_review_gate.v1",
            "version": TRAINING_VERSION,
            "gate_id": f"CODEX-PROMOTION-FINAL-COMPLETION-REVIEW-GATE-{TRAINING_VERSION}-TPI-001",
            "source_final_sync_closure_audit_id": audit.get("audit_id", ""),
            "source_final_sync_closure_status": audit.get("closure_status", ""),
            "gate_status": gate_status,
            "gate_ready": audit.get("closure_ready", False) and bool(candidates),
            "candidate_count": len(candidates),
            "final_completion_review_candidate_count": len(candidates),
            "approved_final_completion_count": len(approved_candidates),
            "needs_completion_inputs_count": len(needs_input_candidates),
            "rejected_final_completion_count": len(rejected_candidates),
            "future_publication_action_count": len(publication_plan),
            "final_completion_publication_plan": publication_plan,
            "final_completion_review_candidates": candidates,
            "final_completion_review_state": review_state,
            "manual_final_completion_review_required": bool(candidates),
            "automatic_completion_allowed": False,
            "automatic_project_memory_write_allowed": False,
            "metadata_only": True,
            "contains_raw_file": False,
            "contains_credentials": False,
            "decision_rules": [
                "final completion review can approve future publication requests only as metadata",
                "approved final completion candidates remain approved_but_not_published until real endpoint/store, schema, auth, scope, retention, validation, and rollback inputs are confirmed outside this demo",
                "local regression baseline candidates require a target store, version label, fresh validation, rollback planning, and product-owner publication confirmation before any baseline update",
                "live Hermes memory candidates require endpoint, auth scope, memory schema, retention policy, tenant/factory scope, fresh validation, rollback planning, and product-owner publication confirmation before any live write",
                "final completion review must not publish project memory, update baselines, write live Hermes memory, run git, store raw files, store credentials, or start real data integration",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _final_completion_publication_plan_item(index: int, candidate: dict) -> dict:
        target_system = candidate.get("target_system", "")
        if target_system == "live_hermes_memory":
            owner_role = "hermes_admin"
            required_publication_inputs = [
                "live_hermes_endpoint",
                "live_hermes_auth_scope",
                "live_hermes_memory_schema",
                "live_hermes_retention_policy",
                "live_hermes_tenant_factory_scope",
                "live_hermes_rollback_plan",
                "post_final_sync_validation_summary",
                "project_memory_publication_scope",
            ]
        else:
            owner_role = "regression_maintainer"
            required_publication_inputs = [
                "baseline_update_endpoint_or_store",
                "baseline_version_label",
                "baseline_rollback_plan",
                "post_final_sync_validation_summary",
                "project_memory_publication_scope",
            ]
        return {
            "action_id": f"FINAL-COMPLETION-PUBLICATION-{TRAINING_VERSION}-{index:03d}",
            "final_sync_completion_id": candidate.get("final_sync_completion_id", ""),
            "readiness_item_id": candidate.get("readiness_item_id", ""),
            "final_closure_id": candidate.get("final_closure_id", ""),
            "source_action_id": candidate.get("source_action_id", ""),
            "source_sync_audit_id": candidate.get("source_sync_audit_id", ""),
            "promotion_candidate_id": candidate.get("promotion_candidate_id", ""),
            "promotion_type": candidate.get("promotion_type", ""),
            "target_system": target_system,
            "owner_role": owner_role,
            "execution_status": "approved_but_not_published",
            "manual_publication_required": True,
            "automatic_completion_allowed": False,
            "automatic_project_memory_write_allowed": False,
            "required_completion_checks": candidate.get("required_completion_checks", []),
            "required_publication_inputs": required_publication_inputs,
            "changed_records": candidate.get("changed_records", []),
            "validation_summary": candidate.get("validation_summary", ""),
            "rollback_summary": candidate.get("rollback_summary", ""),
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _codex_promotion_final_completion_review_hermes_payload(gate: dict) -> dict:
        return {
            "schema": "hermes.codex_promotion_final_completion_review_gate.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if gate.get("future_publication_action_count") else "candidate",
            "version": TRAINING_VERSION,
            "gate_id": gate["gate_id"],
            "source_final_sync_closure_audit_id": gate.get("source_final_sync_closure_audit_id"),
            "gate_status": gate.get("gate_status"),
            "candidate_count": gate.get("candidate_count", 0),
            "approved_final_completion_count": gate.get("approved_final_completion_count", 0),
            "future_publication_action_count": gate.get("future_publication_action_count", 0),
            "automatic_completion_allowed": gate.get("automatic_completion_allowed"),
            "automatic_project_memory_write_allowed": gate.get("automatic_project_memory_write_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_promotion_final_completion_review_kpis(gate: dict) -> list[dict]:
        review_count = gate["final_completion_review_state"]["final_completion_review_count"]
        return [
            {"kpi": "codex_promotion_final_completion_review_gate_ready", "value": gate["gate_ready"], "target": True, "status": "ok" if gate["gate_ready"] else "attention"},
            {"kpi": "codex_promotion_final_completion_review_candidate_count", "value": gate["candidate_count"], "target": "tracked", "status": "ok" if gate["candidate_count"] else "attention"},
            {"kpi": "codex_promotion_final_completion_review_count", "value": review_count, "target": gate["candidate_count"], "status": "ok" if gate["candidate_count"] and review_count >= gate["candidate_count"] else "attention"},
            {"kpi": "codex_promotion_final_completion_approved_count", "value": gate["approved_final_completion_count"], "target": gate["candidate_count"], "status": "ok" if gate["candidate_count"] and gate["approved_final_completion_count"] == gate["candidate_count"] else "attention"},
            {"kpi": "codex_promotion_final_completion_review_automatic_allowed", "value": gate["automatic_completion_allowed"], "target": False, "status": "ok" if gate["automatic_completion_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_promotion_final_completion_review_evidence(gate: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-FINAL-COMPLETION-REVIEW-001",
                "source": "athena.codex_promotion_final_sync_closure_audit.v1",
                "summary": f"Prepared final completion review gate {gate['gate_status']} from final sync closure audit {gate.get('source_final_sync_closure_audit_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-FINAL-COMPLETION-REVIEW-002",
                "source": "codex_promotion_final_completion_review_guardrail",
                "summary": "Final completion review stores metadata only and blocks project-memory publication, baseline updates, live Hermes writes, git actions, raw file storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _codex_promotion_final_publication_handoff_queue(gate: dict) -> dict:
        publication_actions = gate.get("final_completion_publication_plan", [])
        handoff_items = [
            TrainingAutomationWorkflow._final_publication_handoff_item(index, item)
            for index, item in enumerate(publication_actions, start=1)
        ]
        gate_status = gate.get("gate_status", "")
        if handoff_items:
            handoff_status = "ready_for_manual_final_publication_handoff"
        elif gate_status == "blocked_until_final_sync_closure_ready":
            handoff_status = "blocked_until_final_sync_closure_ready"
        elif gate_status in {"ready_for_final_completion_review", "final_completion_review_in_progress"}:
            handoff_status = "blocked_until_final_completion_review_approval"
        elif gate_status == "blocked_by_final_completion_review_rejection":
            handoff_status = "blocked_by_final_completion_review_rejection"
        elif gate_status == "blocked_no_final_completion_candidates":
            handoff_status = "blocked_no_final_completion_candidates"
        else:
            handoff_status = "blocked_until_final_publication_actions_ready"

        blocked_actions = [
            "auto_execute_final_publication_handoff",
            "auto_publish_project_memory_from_final_publication_handoff",
            "auto_update_regression_baseline_from_final_publication_handoff",
            "auto_write_live_hermes_memory_from_final_publication_handoff",
            "auto_commit_push_or_open_pr_from_final_publication_handoff",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_promotion_final_publication_handoff_queue.v1",
            "version": TRAINING_VERSION,
            "handoff_id": f"CODEX-PROMOTION-FINAL-PUBLICATION-HANDOFF-{TRAINING_VERSION}-TPI-001",
            "source_final_completion_review_gate_id": gate.get("gate_id", ""),
            "source_final_completion_review_status": gate_status,
            "handoff_status": handoff_status,
            "handoff_ready": bool(handoff_items),
            "handoff_item_count": len(handoff_items),
            "regression_publication_handoff_count": len([item for item in handoff_items if item.get("target_system") == "local_regression_baseline_store"]),
            "hermes_publication_handoff_count": len([item for item in handoff_items if item.get("target_system") == "live_hermes_memory"]),
            "manual_publication_required": bool(handoff_items),
            "automatic_publication_allowed": False,
            "project_memory_publication_allowed": False,
            "metadata_only": True,
            "contains_raw_file": False,
            "contains_credentials": False,
            "handoff_items": handoff_items,
            "decision_rules": [
                "final publication handoff converts approved final completion publication plans into manual handoff contracts only",
                "handoff items must keep target system, owner role, required publication inputs, suggested instruction, and required publication evidence visible",
                "local regression baseline publication still requires target store, version label, rollback plan, validation evidence, and product-owner publication confirmation",
                "live Hermes memory publication still requires endpoint, auth scope, memory schema, retention policy, tenant/factory scope, rollback plan, validation evidence, and product-owner publication confirmation",
                "final publication handoff must not publish project memory, update baselines, write live Hermes memory, run git, store raw files, store credentials, or start real data integration",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _final_publication_handoff_item(index: int, action: dict) -> dict:
        target_system = action.get("target_system", "")
        owner_role = action.get("owner_role", "")
        if target_system == "live_hermes_memory":
            suggested_user_instruction = (
                "After live Hermes endpoint, auth scope, memory schema, retention policy, tenant/factory scope, "
                "rollback plan, publication scope, and post-publication validation evidence are confirmed, manually publish the approved Hermes memory outside this demo."
            )
            publication_evidence_required = [
                "publication_reference",
                "published_memory_event_ids",
                "post_publication_validation_summary",
                "rollback_summary",
                "product_owner_publication_confirmation",
            ]
        else:
            suggested_user_instruction = (
                "After baseline target/store, version label, rollback plan, publication scope, and post-publication validation evidence are confirmed, "
                "manually publish the approved regression baseline outside this demo."
            )
            publication_evidence_required = [
                "publication_reference",
                "published_baseline_id",
                "post_publication_validation_summary",
                "rollback_summary",
                "product_owner_publication_confirmation",
            ]
        return {
            "final_publication_handoff_item_id": f"FINAL-PUBLICATION-HANDOFF-{TRAINING_VERSION}-{index:03d}",
            "source_publication_action_id": action.get("action_id", ""),
            "source_action_id": action.get("source_action_id", ""),
            "final_sync_completion_id": action.get("final_sync_completion_id", ""),
            "final_closure_id": action.get("final_closure_id", ""),
            "readiness_item_id": action.get("readiness_item_id", ""),
            "source_sync_audit_id": action.get("source_sync_audit_id", ""),
            "promotion_candidate_id": action.get("promotion_candidate_id", ""),
            "promotion_type": action.get("promotion_type", ""),
            "target_system": target_system,
            "owner_role": owner_role,
            "publication_status": "waiting_manual_final_publication",
            "manual_publication_required": True,
            "automatic_publication_allowed": False,
            "project_memory_publication_allowed": False,
            "required_publication_inputs": action.get("required_publication_inputs", []),
            "publication_evidence_required": publication_evidence_required,
            "suggested_user_instruction": suggested_user_instruction,
            "source_required_completion_checks": action.get("required_completion_checks", []),
            "source_changed_records": action.get("changed_records", []),
            "source_validation_summary": action.get("validation_summary", ""),
            "source_rollback_summary": action.get("rollback_summary", ""),
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _codex_promotion_final_publication_handoff_hermes_payload(queue: dict) -> dict:
        return {
            "schema": "hermes.codex_promotion_final_publication_handoff_queue.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if queue.get("handoff_ready") else "candidate",
            "version": TRAINING_VERSION,
            "handoff_id": queue["handoff_id"],
            "source_final_completion_review_gate_id": queue.get("source_final_completion_review_gate_id"),
            "handoff_status": queue.get("handoff_status"),
            "handoff_item_count": queue.get("handoff_item_count", 0),
            "regression_publication_handoff_count": queue.get("regression_publication_handoff_count", 0),
            "hermes_publication_handoff_count": queue.get("hermes_publication_handoff_count", 0),
            "manual_publication_required": queue.get("manual_publication_required"),
            "automatic_publication_allowed": queue.get("automatic_publication_allowed"),
            "project_memory_publication_allowed": queue.get("project_memory_publication_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_promotion_final_publication_handoff_kpis(queue: dict) -> list[dict]:
        return [
            {"kpi": "codex_promotion_final_publication_handoff_ready", "value": queue["handoff_ready"], "target": True, "status": "ok" if queue["handoff_ready"] else "attention"},
            {"kpi": "codex_promotion_final_publication_handoff_item_count", "value": queue["handoff_item_count"], "target": "tracked", "status": "ok" if queue["handoff_item_count"] else "attention"},
            {"kpi": "codex_promotion_final_publication_handoff_hermes_count", "value": queue["hermes_publication_handoff_count"], "target": "tracked", "status": "ok" if queue["hermes_publication_handoff_count"] else "attention"},
            {"kpi": "codex_promotion_final_publication_handoff_regression_count", "value": queue["regression_publication_handoff_count"], "target": "tracked", "status": "ok" if queue["regression_publication_handoff_count"] else "attention"},
            {"kpi": "codex_promotion_final_publication_handoff_automatic_allowed", "value": queue["automatic_publication_allowed"], "target": False, "status": "ok" if queue["automatic_publication_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_promotion_final_publication_handoff_evidence(queue: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-FINAL-PUBLICATION-HANDOFF-001",
                "source": "athena.codex_promotion_final_completion_review_gate.v1",
                "summary": f"Prepared final publication handoff queue {queue['handoff_status']} from final completion review gate {queue.get('source_final_completion_review_gate_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-FINAL-PUBLICATION-HANDOFF-002",
                "source": "codex_promotion_final_publication_handoff_guardrail",
                "summary": "Final publication handoff creates manual publication contracts only and blocks project-memory publication, baseline updates, live Hermes writes, git actions, raw file storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _confirmed_final_publication_inputs(payload: dict | None) -> list[str]:
        payload = payload or {}
        raw_inputs = payload.get("confirmed_publication_inputs") or payload.get("confirmed_inputs") or []
        if isinstance(raw_inputs, str):
            raw_inputs = [item.strip() for item in raw_inputs.split("|") if item.strip()]
        if not isinstance(raw_inputs, list):
            raw_inputs = []
        return [str(item).strip() for item in raw_inputs if str(item).strip()]

    @staticmethod
    def _codex_promotion_final_publication_readiness_gate(queue: dict, payload: dict | None = None) -> dict:
        confirmed_inputs = TrainingAutomationWorkflow._confirmed_final_publication_inputs(payload)
        readiness_items = [
            TrainingAutomationWorkflow._final_publication_readiness_item(index, item, confirmed_inputs)
            for index, item in enumerate(queue.get("handoff_items", []), start=1)
        ]
        handoff_status = queue.get("handoff_status", "")
        confirmed_count = len([item for item in readiness_items if item["readiness_status"] == "final_publication_prerequisites_confirmed"])
        blocked_count = len([item for item in readiness_items if item.get("missing_publication_inputs")])
        if readiness_items and confirmed_count == len(readiness_items):
            readiness_status = "ready_for_manual_final_publication_confirmation"
        elif readiness_items:
            readiness_status = "blocked_until_final_publication_prerequisites_confirmed"
        elif handoff_status == "blocked_until_final_sync_closure_ready":
            readiness_status = "blocked_until_final_sync_closure_ready"
        elif handoff_status == "blocked_until_final_completion_review_approval":
            readiness_status = "blocked_until_final_completion_review_approval"
        elif handoff_status == "blocked_by_final_completion_review_rejection":
            readiness_status = "blocked_by_final_completion_review_rejection"
        elif handoff_status == "blocked_no_final_completion_candidates":
            readiness_status = "blocked_no_final_completion_candidates"
        else:
            readiness_status = "blocked_until_final_publication_handoff_ready"

        blocked_actions = [
            "auto_execute_final_publication_readiness",
            "auto_publish_project_memory_from_final_publication_readiness",
            "auto_update_regression_baseline_from_final_publication_readiness",
            "auto_write_live_hermes_memory_from_final_publication_readiness",
            "auto_commit_push_or_open_pr_from_final_publication_readiness",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_promotion_final_publication_readiness_gate.v1",
            "version": TRAINING_VERSION,
            "gate_id": f"CODEX-PROMOTION-FINAL-PUBLICATION-READINESS-GATE-{TRAINING_VERSION}-TPI-001",
            "source_final_publication_handoff_id": queue.get("handoff_id", ""),
            "source_final_publication_handoff_status": handoff_status,
            "readiness_status": readiness_status,
            "readiness_ready": readiness_status == "ready_for_manual_final_publication_confirmation",
            "readiness_item_count": len(readiness_items),
            "blocked_readiness_item_count": blocked_count,
            "confirmed_readiness_item_count": confirmed_count,
            "regression_final_publication_readiness_count": len([item for item in readiness_items if item.get("target_system") == "local_regression_baseline_store"]),
            "hermes_final_publication_readiness_count": len([item for item in readiness_items if item.get("target_system") == "live_hermes_memory"]),
            "confirmed_publication_inputs": confirmed_inputs,
            "manual_final_publication_required": bool(readiness_items),
            "automatic_publication_allowed": False,
            "project_memory_publication_allowed": False,
            "readiness_items": readiness_items,
            "metadata_only": True,
            "contains_raw_file": False,
            "contains_credentials": False,
            "decision_rules": [
                "final publication readiness can only evaluate prerequisites for a future manual publication action",
                "readiness requires target-system contract details, explicit product-owner publication confirmation, rollback planning, current validation output, and publication evidence plan before any real-state change is considered",
                "local regression baseline final publication must not run until baseline store, version label, rollback, validation, publication evidence, and owner confirmation are present",
                "live Hermes memory final publication must not run until endpoint, auth scope, memory schema, retention policy, tenant/factory scope, rollback, validation, publication evidence, and owner confirmation are present",
                "final publication readiness must not publish project memory, update baselines, write live Hermes memory, run git, store raw files, store credentials, or start real data integration",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _final_publication_readiness_item(index: int, handoff_item: dict, confirmed_inputs: list[str]) -> dict:
        required_inputs = list(dict.fromkeys(
            [
                *handoff_item.get("required_publication_inputs", []),
                "explicit_product_owner_final_publication_confirmation",
                "current_compileall_validation_output",
                "current_test_harness_validation_output",
                "publication_evidence_capture_plan",
                "publication_rollback_plan",
            ]
        ))
        missing_inputs = [item for item in required_inputs if item not in confirmed_inputs]
        readiness_status = (
            "final_publication_prerequisites_confirmed"
            if not missing_inputs
            else "blocked_missing_final_publication_prerequisites"
        )
        return {
            "readiness_item_id": f"FINAL-PUBLICATION-READINESS-{TRAINING_VERSION}-{index:03d}",
            "source_final_publication_handoff_item_id": handoff_item.get("final_publication_handoff_item_id", ""),
            "source_publication_action_id": handoff_item.get("source_publication_action_id", ""),
            "source_action_id": handoff_item.get("source_action_id", ""),
            "final_sync_completion_id": handoff_item.get("final_sync_completion_id", ""),
            "final_closure_id": handoff_item.get("final_closure_id", ""),
            "readiness_item_source_id": handoff_item.get("readiness_item_id", ""),
            "source_sync_audit_id": handoff_item.get("source_sync_audit_id", ""),
            "promotion_candidate_id": handoff_item.get("promotion_candidate_id", ""),
            "promotion_type": handoff_item.get("promotion_type", ""),
            "target_system": handoff_item.get("target_system", ""),
            "owner_role": handoff_item.get("owner_role", ""),
            "readiness_status": readiness_status,
            "manual_final_publication_required": True,
            "automatic_publication_allowed": False,
            "project_memory_publication_allowed": False,
            "required_publication_inputs": required_inputs,
            "confirmed_publication_inputs": [item for item in confirmed_inputs if item in required_inputs],
            "missing_publication_inputs": missing_inputs,
            "publication_evidence_required": handoff_item.get("publication_evidence_required", []),
            "suggested_user_instruction": handoff_item.get("suggested_user_instruction", ""),
            "source_changed_records": handoff_item.get("source_changed_records", []),
            "source_validation_summary": handoff_item.get("source_validation_summary", ""),
            "source_rollback_summary": handoff_item.get("source_rollback_summary", ""),
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _codex_promotion_final_publication_readiness_hermes_payload(gate: dict) -> dict:
        return {
            "schema": "hermes.codex_promotion_final_publication_readiness_gate.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if gate.get("readiness_ready") else "candidate",
            "version": TRAINING_VERSION,
            "gate_id": gate["gate_id"],
            "source_final_publication_handoff_id": gate.get("source_final_publication_handoff_id"),
            "readiness_status": gate.get("readiness_status"),
            "readiness_item_count": gate.get("readiness_item_count", 0),
            "blocked_readiness_item_count": gate.get("blocked_readiness_item_count", 0),
            "confirmed_readiness_item_count": gate.get("confirmed_readiness_item_count", 0),
            "automatic_publication_allowed": gate.get("automatic_publication_allowed"),
            "project_memory_publication_allowed": gate.get("project_memory_publication_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_promotion_final_publication_readiness_kpis(gate: dict) -> list[dict]:
        return [
            {"kpi": "codex_promotion_final_publication_readiness_ready", "value": gate["readiness_ready"], "target": True, "status": "ok" if gate["readiness_ready"] else "attention"},
            {"kpi": "codex_promotion_final_publication_readiness_item_count", "value": gate["readiness_item_count"], "target": "tracked", "status": "ok" if gate["readiness_item_count"] else "attention"},
            {"kpi": "codex_promotion_final_publication_blocked_item_count", "value": gate["blocked_readiness_item_count"], "target": 0, "status": "ok" if gate["blocked_readiness_item_count"] == 0 else "attention"},
            {"kpi": "codex_promotion_final_publication_confirmed_count", "value": gate["confirmed_readiness_item_count"], "target": gate["readiness_item_count"], "status": "ok" if gate["readiness_item_count"] and gate["confirmed_readiness_item_count"] == gate["readiness_item_count"] else "attention"},
            {"kpi": "codex_promotion_final_publication_automatic_allowed", "value": gate["automatic_publication_allowed"], "target": False, "status": "ok" if gate["automatic_publication_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_promotion_final_publication_readiness_evidence(gate: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-FINAL-PUBLICATION-READINESS-001",
                "source": "athena.codex_promotion_final_publication_handoff_queue.v1",
                "summary": f"Evaluated final publication readiness {gate['readiness_status']} from final publication handoff queue {gate.get('source_final_publication_handoff_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-FINAL-PUBLICATION-READINESS-002",
                "source": "codex_promotion_final_publication_readiness_guardrail",
                "summary": "Final publication readiness evaluates prerequisites only and blocks project-memory publication, baseline updates, live Hermes writes, git actions, raw file storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _final_publication_result_contract_status(
        result_status: str,
        publication_reference: str,
        published_records: list[str],
        validation_summary: str,
        validation_results: list[dict],
    ) -> dict:
        commands = [
            f"{item.get('command', '')} {item.get('summary', '')}".lower()
            for item in validation_results
            if item.get("status") == "passed"
        ]
        compileall_passed = any("compileall" in item for item in commands)
        harness_passed = any("harness" in item or "test_main_agent" in item for item in commands)
        publication_reference_reported = bool(publication_reference)
        published_records_reported = bool(published_records)
        validation_summary_reported = bool(validation_summary)
        contract_complete = (
            result_status == "manual_final_publication_recorded"
            and publication_reference_reported
            and published_records_reported
            and validation_summary_reported
            and compileall_passed
            and harness_passed
        )
        return {
            "contract_complete": contract_complete,
            "publication_reference_reported": publication_reference_reported,
            "published_records_reported": published_records_reported,
            "validation_summary_reported": validation_summary_reported,
            "compileall_passed": compileall_passed,
            "harness_passed": harness_passed,
            "missing_items": [
                item
                for item, ok in [
                    ("publication_reference", publication_reference_reported),
                    ("published_records", published_records_reported),
                    ("post_publication_validation_summary", validation_summary_reported),
                    ("compileall_passed", compileall_passed),
                    ("harness_passed", harness_passed),
                ]
                if not ok
            ],
        }

    @staticmethod
    def _codex_promotion_final_publication_result_state(store: dict) -> dict:
        results = list(store.get("codex_promotion_final_publication_results", {}).values())
        recorded = [item for item in results if item.get("result_status") == "manual_final_publication_recorded"]
        failed = [item for item in results if item.get("result_status") == "manual_final_publication_failed"]
        skipped = [item for item in results if item.get("result_status") == "manual_final_publication_skipped"]
        complete = [item for item in recorded if item.get("result_contract", {}).get("contract_complete")]
        return {
            "schema_id": "athena.codex_promotion_final_publication_result_state.v1",
            "version": store.get("version", TRAINING_VERSION),
            "updated_at": store.get("updated_at", ""),
            "result_count": len(results),
            "manual_final_publication_recorded_count": len(recorded),
            "manual_final_publication_failed_count": len(failed),
            "manual_final_publication_skipped_count": len(skipped),
            "contract_complete_count": len(complete),
            "automatic_publication_allowed": False,
            "project_memory_publication_allowed": False,
            "metadata_only": True,
            "codex_promotion_final_publication_results": store.get("codex_promotion_final_publication_results", {}),
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _codex_promotion_final_publication_result_intake(store: dict, readiness_gate: dict) -> dict:
        result_state = TrainingAutomationWorkflow._codex_promotion_final_publication_result_state(store)
        source_status = readiness_gate.get("readiness_status", "blocked_until_final_publication_handoff_ready")
        readiness_items = [
            item
            for item in readiness_gate.get("readiness_items", [])
            if item.get("readiness_status") == "final_publication_prerequisites_confirmed"
        ]
        if result_state["manual_final_publication_failed_count"]:
            intake_status = "final_publication_result_failed"
        elif result_state["contract_complete_count"]:
            intake_status = "final_publication_result_recorded"
        elif result_state["result_count"]:
            intake_status = "final_publication_result_needs_review"
        elif readiness_gate.get("readiness_ready"):
            intake_status = "waiting_for_manual_final_publication_result"
        elif source_status == "blocked_until_final_publication_prerequisites_confirmed":
            intake_status = "blocked_until_final_publication_readiness_confirmed"
        else:
            intake_status = "blocked_until_final_publication_ready"

        blocked_actions = [
            "auto_execute_recorded_final_publication_result",
            "auto_publish_project_memory_from_final_publication_result",
            "auto_update_regression_baseline_from_final_publication_result",
            "auto_write_live_hermes_memory_from_final_publication_result",
            "auto_commit_push_or_open_pr_from_final_publication_result",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_promotion_final_publication_result_intake.v1",
            "version": TRAINING_VERSION,
            "intake_id": f"CODEX-PROMOTION-FINAL-PUBLICATION-RESULT-INTAKE-{TRAINING_VERSION}-TPI-001",
            "source_readiness_gate_id": readiness_gate.get("gate_id"),
            "source_readiness_status": source_status,
            "intake_status": intake_status,
            "result_ready_for_review": result_state["result_count"] > 0,
            "manual_final_publication_result_required": readiness_gate.get("readiness_ready", False),
            "automatic_publication_allowed": False,
            "project_memory_publication_allowed": False,
            "expected_result_count": len(readiness_items),
            "result_state": result_state,
            "result_count": result_state["result_count"],
            "contract_complete_count": result_state["contract_complete_count"],
            "codex_promotion_final_publication_results": result_state["codex_promotion_final_publication_results"],
            "decision_rules": [
                "final publication result intake records metadata after an explicitly manual final publication action outside the demo",
                "result intake must not publish project memory, update regression baselines, write live Hermes memory, commit, push, open PR, store raw files, or store credentials",
                "recorded final publication results require a publication reference, published record identifiers, post-publication validation summary, and current compileall/test harness validation summaries before the contract is complete",
                "future closure or release claims must review these metadata records separately before any real publication success is accepted",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _codex_promotion_final_publication_result_hermes_payload(intake: dict) -> dict:
        return {
            "schema": "hermes.codex_promotion_final_publication_result_intake.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if intake.get("result_count") else "candidate",
            "version": TRAINING_VERSION,
            "intake_id": intake["intake_id"],
            "source_readiness_gate_id": intake.get("source_readiness_gate_id"),
            "source_readiness_status": intake.get("source_readiness_status"),
            "intake_status": intake.get("intake_status"),
            "result_count": intake.get("result_count", 0),
            "contract_complete_count": intake.get("contract_complete_count", 0),
            "automatic_publication_allowed": intake.get("automatic_publication_allowed"),
            "project_memory_publication_allowed": intake.get("project_memory_publication_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_promotion_final_publication_result_kpis(intake: dict) -> list[dict]:
        return [
            {"kpi": "codex_promotion_final_publication_result_count", "value": intake["result_count"], "target": "tracked", "status": "ok" if intake["result_count"] else "attention"},
            {"kpi": "codex_promotion_final_publication_result_passed_count", "value": intake["result_state"]["manual_final_publication_recorded_count"], "target": "tracked", "status": "ok" if intake["result_state"]["manual_final_publication_recorded_count"] else "attention"},
            {"kpi": "codex_promotion_final_publication_result_contract_complete_count", "value": intake["contract_complete_count"], "target": intake["result_count"], "status": "ok" if intake["result_count"] and intake["contract_complete_count"] == intake["result_count"] else "attention"},
            {"kpi": "codex_promotion_final_publication_result_automatic_allowed", "value": intake["automatic_publication_allowed"], "target": False, "status": "ok" if intake["automatic_publication_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_promotion_final_publication_result_evidence(intake: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-FINAL-PUBLICATION-RESULT-001",
                "source": "athena.codex_promotion_final_publication_readiness_gate.v1",
                "summary": f"Prepared final publication result intake {intake['intake_status']} from readiness gate {intake.get('source_readiness_gate_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-FINAL-PUBLICATION-RESULT-002",
                "source": "codex_promotion_final_publication_result_guardrail",
                "summary": "Final publication result intake stores metadata only and blocks project-memory publication, baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _codex_promotion_final_publication_closure_audit(intake: dict, readiness_gate: dict) -> dict:
        readiness_items = [
            item
            for item in readiness_gate.get("readiness_items", [])
            if item.get("readiness_status") == "final_publication_prerequisites_confirmed"
        ]
        expected_result_ids = [item.get("readiness_item_id", "") for item in readiness_items if item.get("readiness_item_id")]
        results = list(intake.get("codex_promotion_final_publication_results", {}).values())
        relevant_results = [item for item in results if item.get("readiness_item_id") in expected_result_ids]
        complete_results = [item for item in relevant_results if item.get("result_contract", {}).get("contract_complete")]
        failed_results = [item for item in relevant_results if item.get("result_status") == "manual_final_publication_failed"]
        complete_ids = {item.get("readiness_item_id") for item in complete_results}
        result_ids = {item.get("readiness_item_id") for item in relevant_results}
        missing_results = []
        for item in readiness_items:
            readiness_item_id = item.get("readiness_item_id", "")
            if readiness_item_id in complete_ids:
                continue
            missing_reason = (
                "complete_final_publication_result_required"
                if readiness_item_id in result_ids
                else "final_publication_result_missing"
            )
            missing_results.append(
                {
                    "readiness_item_id": readiness_item_id,
                    "source_final_publication_handoff_item_id": item.get("source_final_publication_handoff_item_id", ""),
                    "promotion_candidate_id": item.get("promotion_candidate_id", ""),
                    "promotion_type": item.get("promotion_type", ""),
                    "target_system": item.get("target_system", ""),
                    "missing_reason": missing_reason,
                }
            )

        if failed_results:
            closure_status = "final_publication_closure_blocked_by_failed_result"
        elif readiness_items and len(complete_results) == len(readiness_items):
            closure_status = "final_publication_closure_ready_for_archive_review"
        elif complete_results:
            closure_status = "final_publication_closure_partial_results"
        else:
            closure_status = "blocked_until_final_publication_result_ready"

        final_closure_candidates = [
            TrainingAutomationWorkflow._final_publication_closure_candidate(index, item)
            for index, item in enumerate(complete_results, start=1)
        ]
        blocked_actions = [
            "auto_mark_final_publication_complete_without_closure_audit",
            "auto_publish_project_memory_from_final_publication_closure",
            "auto_update_regression_baseline_from_final_publication_closure",
            "auto_write_live_hermes_memory_from_final_publication_closure",
            "auto_commit_push_or_open_pr_from_final_publication_closure",
            "store_raw_patch_or_diff",
            "store_raw_training_files",
            "store_credentials_or_tokens",
            "start_real_data_integration_without_user_confirmation",
        ]
        return {
            "schema_id": "athena.codex_promotion_final_publication_closure_audit.v1",
            "version": TRAINING_VERSION,
            "audit_id": f"CODEX-PROMOTION-FINAL-PUBLICATION-CLOSURE-AUDIT-{TRAINING_VERSION}-TPI-001",
            "source_final_publication_result_intake_id": intake.get("intake_id", ""),
            "source_final_publication_result_intake_status": intake.get("intake_status", ""),
            "source_readiness_gate_id": readiness_gate.get("gate_id", ""),
            "source_readiness_status": readiness_gate.get("readiness_status", ""),
            "closure_status": closure_status,
            "closure_ready": closure_status == "final_publication_closure_ready_for_archive_review",
            "expected_result_count": len(readiness_items),
            "recorded_result_count": len(relevant_results),
            "complete_result_count": len(complete_results),
            "failed_result_count": len(failed_results),
            "missing_result_count": len(missing_results),
            "final_closure_candidate_count": len(final_closure_candidates),
            "automatic_closure_allowed": False,
            "automatic_project_memory_write_allowed": False,
            "project_memory_publication_allowed": False,
            "metadata_only": True,
            "contains_raw_file": False,
            "contains_credentials": False,
            "final_closure_candidates": final_closure_candidates,
            "missing_results": missing_results,
            "failed_results": [
                {
                    "readiness_item_id": item.get("readiness_item_id", ""),
                    "promotion_candidate_id": item.get("promotion_candidate_id", ""),
                    "promotion_type": item.get("promotion_type", ""),
                    "target_system": item.get("target_system", ""),
                    "result_summary": item.get("result_summary", ""),
                }
                for item in failed_results
            ],
            "decision_rules": [
                "final publication closure audit can only review metadata captured after manual final publication outside the demo",
                "each confirmed readiness item requires a complete final publication result contract before closure can be considered ready",
                "complete final publication result contracts require publication reference, published record identifiers, post-publication validation summary, compileall summary, and test harness summary",
                "final publication closure audit must not publish project memory, update baselines, write live Hermes memory, run git, store raw files, store credentials, or start real data integration",
            ],
            "blocked_actions": blocked_actions,
        }

    @staticmethod
    def _final_publication_closure_candidate(index: int, result: dict) -> dict:
        return {
            "final_publication_completion_id": f"FINAL-PUBLICATION-COMPLETION-{TRAINING_VERSION}-{index:03d}",
            "readiness_item_id": result.get("readiness_item_id", ""),
            "source_final_publication_handoff_item_id": result.get("source_final_publication_handoff_item_id", ""),
            "source_publication_action_id": result.get("source_publication_action_id", ""),
            "source_action_id": result.get("source_action_id", ""),
            "final_sync_completion_id": result.get("final_sync_completion_id", ""),
            "final_closure_id": result.get("final_closure_id", ""),
            "source_sync_audit_id": result.get("source_sync_audit_id", ""),
            "promotion_candidate_id": result.get("promotion_candidate_id", ""),
            "promotion_type": result.get("promotion_type", ""),
            "target_system": result.get("target_system", ""),
            "publication_reference": result.get("publication_reference", ""),
            "published_records": result.get("published_records", []),
            "validation_summary": result.get("validation_summary", ""),
            "rollback_summary": result.get("rollback_summary", ""),
            "validation_results": result.get("validation_results", []),
            "closure_candidate_status": "metadata_ready_for_final_release_review",
            "required_final_closure_checks": [
                "product_owner_final_publication_closure_confirmation",
                "post_publication_validation_summary",
                "rollback_reversal_verification",
                "no_raw_file_or_credentials",
            ],
            "metadata_only": True,
            "automatic_closure_allowed": False,
            "automatic_project_memory_write_allowed": False,
            "project_memory_publication_allowed": False,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "contains_raw_file": False,
            "contains_credentials": False,
        }

    @staticmethod
    def _codex_promotion_final_publication_closure_audit_hermes_payload(audit: dict) -> dict:
        return {
            "schema": "hermes.codex_promotion_final_publication_closure_audit.v1",
            "source": "demo",
            "scope": "tenant",
            "tenant_id": "tianpai",
            "factory_id": None,
            "retention_policy": "training_lifecycle",
            "sensitivity_level": "internal",
            "promotion_status": "reviewed" if audit.get("closure_ready") else "candidate",
            "version": TRAINING_VERSION,
            "audit_id": audit["audit_id"],
            "source_final_publication_result_intake_id": audit.get("source_final_publication_result_intake_id"),
            "closure_status": audit.get("closure_status"),
            "expected_result_count": audit.get("expected_result_count", 0),
            "recorded_result_count": audit.get("recorded_result_count", 0),
            "complete_result_count": audit.get("complete_result_count", 0),
            "missing_result_count": audit.get("missing_result_count", 0),
            "failed_result_count": audit.get("failed_result_count", 0),
            "automatic_closure_allowed": audit.get("automatic_closure_allowed"),
            "automatic_project_memory_write_allowed": audit.get("automatic_project_memory_write_allowed"),
            "contains_raw_file": False,
            "contains_credentials": False,
            "write_actions_blocked": True,
        }

    @staticmethod
    def _codex_promotion_final_publication_closure_audit_kpis(audit: dict) -> list[dict]:
        return [
            {"kpi": "codex_promotion_final_publication_closure_ready", "value": audit["closure_ready"], "target": True, "status": "ok" if audit["closure_ready"] else "attention"},
            {"kpi": "codex_promotion_final_publication_closure_expected_result_count", "value": audit["expected_result_count"], "target": "tracked", "status": "ok" if audit["expected_result_count"] else "attention"},
            {"kpi": "codex_promotion_final_publication_closure_complete_result_count", "value": audit["complete_result_count"], "target": audit["expected_result_count"], "status": "ok" if audit["expected_result_count"] and audit["complete_result_count"] == audit["expected_result_count"] else "attention"},
            {"kpi": "codex_promotion_final_publication_closure_missing_result_count", "value": audit["missing_result_count"], "target": 0, "status": "ok" if audit["missing_result_count"] == 0 else "attention"},
            {"kpi": "codex_promotion_final_publication_closure_automatic_allowed", "value": audit["automatic_closure_allowed"], "target": False, "status": "ok" if audit["automatic_closure_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_promotion_final_publication_closure_audit_evidence(audit: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-FINAL-PUBLICATION-CLOSURE-001",
                "source": "athena.codex_promotion_final_publication_result_intake.v1",
                "summary": f"Audited final publication closure {audit['closure_status']} from result intake {audit.get('source_final_publication_result_intake_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-FINAL-PUBLICATION-CLOSURE-002",
                "source": "codex_promotion_final_publication_closure_guardrail",
                "summary": "Final publication closure audit reviews metadata only and blocks project-memory publication, baseline updates, live Hermes writes, commits, pushes, PRs, raw file storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _codex_promotion_final_release_review_gate(closure_audit: dict) -> dict:
        candidates = closure_audit.get("final_closure_candidates", [])
        failed_results = closure_audit.get("failed_results", [])
        missing_results = closure_audit.get("missing_results", [])
        closure_status = closure_audit.get("closure_status", "blocked_until_final_publication_result_ready")

        if failed_results:
            gate_status = "final_release_review_blocked_by_failed_publication_result"
        elif closure_status == "final_publication_closure_ready_for_archive_review" and candidates:
            gate_status = "ready_for_product_owner_final_release_review"
        elif closure_status == "final_publication_closure_partial_results":
            gate_status = "blocked_until_final_publication_closure_complete"
        else:
            gate_status = "blocked_until_final_publication_closure_ready"

        review_candidates = [
            TrainingAutomationWorkflow._final_release_review_candidate(index, item)
            for index, item in enumerate(candidates, start=1)
        ]
        blocked_actions = [
            "auto_mark_athena_release_complete_from_release_review_gate",
            "auto_archive_project_memory_from_release_review_gate",
            "auto_publish_project_memory_from_release_review_gate",
            "auto_update_regression_baseline_from_release_review_gate",
            "auto_write_live_hermes_memory_from_release_review_gate",
            "auto_commit_push_or_open_pr_from_release_review_gate",
            "auto_store_raw_publication_artifacts_from_release_review_gate",
            "auto_start_real_aps_iot_or_hermes_integration_from_release_review_gate",
        ]
        return {
            "schema_id": "athena.codex_promotion_final_release_review_gate.v1",
            "version": TRAINING_VERSION,
            "gate_id": f"CODEX-PROMOTION-FINAL-RELEASE-REVIEW-GATE-{TRAINING_VERSION}-TPI-001",
            "source_final_publication_closure_audit_id": closure_audit.get("audit_id", ""),
            "source_final_publication_closure_status": closure_status,
            "gate_status": gate_status,
            "gate_ready": gate_status == "ready_for_product_owner_final_release_review",
            "release_review_candidate_count": len(review_candidates),
            "blocked_release_review_candidate_count": len(missing_results) + len(failed_results),
            "missing_publication_result_count": len(missing_results),
            "failed_publication_result_count": len(failed_results),
            "release_review_candidates": review_candidates,
            "missing_results": missing_results,
            "failed_results": failed_results,
            "required_human_review": [
                "product_owner_final_release_confirmation",
                "archive_reference_or_release_note",
                "post_release_monitoring_owner",
                "rollback_owner_confirmation",
            ],
            "automatic_release_allowed": False,
            "automatic_archive_allowed": False,
            "project_memory_publication_allowed": False,
            "regression_baseline_update_allowed": False,
            "live_hermes_write_allowed": False,
            "git_action_allowed": False,
            "raw_artifact_storage_allowed": False,
            "real_data_integration_allowed": False,
            "blocked_actions": blocked_actions,
            "guardrails": [
                "final release review gate is a metadata-only product-owner review checkpoint",
                "release-ready means ready for human archive/release review, not permission to publish project memory or update live Hermes",
                "all final publication closure candidates must remain traceable to publication_reference, published_records, validation_summary, compileall summary, and test harness summary",
                "the demo must not create archive artifacts, update baselines, write live Hermes memory, run git, store raw files, store credentials, or start real data integration",
            ],
        }

    @staticmethod
    def _final_release_review_candidate(index: int, candidate: dict) -> dict:
        return {
            "release_review_candidate_id": f"FINAL-RELEASE-REVIEW-{TRAINING_VERSION}-{index:03d}",
            "source_final_publication_completion_id": candidate.get("final_publication_completion_id", ""),
            "source_final_publication_result_id": candidate.get("source_final_publication_result_id", ""),
            "target_system": candidate.get("target_system", ""),
            "promotion_candidate_id": candidate.get("promotion_candidate_id", ""),
            "promotion_type": candidate.get("promotion_type", ""),
            "publication_reference": candidate.get("publication_reference", ""),
            "published_records": candidate.get("published_records", []),
            "validation_summary": candidate.get("validation_summary", ""),
            "compileall_summary": candidate.get("compileall_summary", ""),
            "test_harness_summary": candidate.get("test_harness_summary", ""),
            "candidate_status": "pending_product_owner_final_release_review",
            "required_review_inputs": [
                "product_owner_final_release_confirmation",
                "archive_reference_or_release_note",
                "post_release_monitoring_owner",
                "rollback_owner_confirmation",
            ],
            "suggested_user_instruction": "Review the final publication metadata, confirm release/archive evidence, and explicitly approve or reject final release closure.",
            "automatic_release_allowed": False,
            "project_memory_publication_allowed": False,
            "live_hermes_write_allowed": False,
        }

    @staticmethod
    def _codex_promotion_final_release_review_hermes_payload(gate: dict) -> dict:
        return {
            "schema": "hermes.codex_promotion_final_release_review_gate.v1",
            "version": TRAINING_VERSION,
            "scope": "product",
            "tenant_id": None,
            "factory_id": None,
            "source": "demo",
            "retention_policy": "keep_metadata_until_product_owner_release_review",
            "sensitivity_level": "internal",
            "promotion_status": "candidate",
            "gate_status": gate.get("gate_status"),
            "release_review_candidate_count": gate.get("release_review_candidate_count"),
            "blocked_release_review_candidate_count": gate.get("blocked_release_review_candidate_count"),
            "automatic_release_allowed": gate.get("automatic_release_allowed"),
            "project_memory_publication_allowed": gate.get("project_memory_publication_allowed"),
            "live_hermes_write_allowed": gate.get("live_hermes_write_allowed"),
            "blocked_actions": gate.get("blocked_actions", []),
        }

    @staticmethod
    def _codex_promotion_final_release_review_kpis(gate: dict) -> list[dict]:
        return [
            {"kpi": "codex_promotion_final_release_review_gate_ready", "value": gate["gate_ready"], "target": True, "status": "ok" if gate["gate_ready"] else "attention"},
            {"kpi": "codex_promotion_final_release_review_candidate_count", "value": gate["release_review_candidate_count"], "target": "tracked", "status": "ok" if gate["release_review_candidate_count"] else "attention"},
            {"kpi": "codex_promotion_final_release_review_blocked_candidate_count", "value": gate["blocked_release_review_candidate_count"], "target": 0, "status": "ok" if gate["blocked_release_review_candidate_count"] == 0 else "attention"},
            {"kpi": "codex_promotion_final_release_review_automatic_release_allowed", "value": gate["automatic_release_allowed"], "target": False, "status": "ok" if gate["automatic_release_allowed"] is False else "failed"},
        ]

    @staticmethod
    def _codex_promotion_final_release_review_evidence(gate: dict) -> list[dict]:
        return [
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-FINAL-RELEASE-REVIEW-001",
                "source": "athena.codex_promotion_final_publication_closure_audit.v1",
                "summary": f"Prepared final release review gate {gate['gate_status']} from final publication closure audit {gate.get('source_final_publication_closure_audit_id')}.",
                "status": "completed",
            },
            {
                "evidence_id": "EV-TRAIN-CODEX-PROMOTION-FINAL-RELEASE-REVIEW-002",
                "source": "codex_promotion_final_release_review_guardrail",
                "summary": "Final release review gate is metadata-only and blocks archive creation, project-memory publication, baseline updates, live Hermes writes, commits, pushes, PRs, raw artifact storage, credentials, and real data integration.",
                "status": "completed",
            },
        ]

    @staticmethod
    def _safe_float(value: object, default: float) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _safe_int(value: object, default: int) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _data_source_id(task_id: str, data_status: str, store: dict) -> str:
        count = len(store.get("data_sources", {})) + 1
        clean_task = task_id.replace("/", "-").replace(" ", "-")
        return f"DS-{clean_task}-{data_status}-{count:03d}"

    @staticmethod
    def _clean(value: object) -> str:
        return str(value or "").strip()

    @staticmethod
    def _now() -> str:
        return datetime.now().replace(microsecond=0).isoformat()

    @staticmethod
    def _ensure_safe_text(value: str) -> None:
        lowered = str(value or "").lower()
        blocked = ["password", "passwd", "token", "api_key", "apikey", "secret", "1qaz"]
        if any(word in lowered for word in blocked):
            raise ValueError("Do not store credentials, tokens, passwords, API keys, or test account secrets in training review records.")




