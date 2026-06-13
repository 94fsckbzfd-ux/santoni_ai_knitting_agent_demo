"""Run the zero-dependency local web demo."""

from __future__ import annotations

import json
import mimetypes
import os
import sys
from dataclasses import asdict
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
WEB_ROOT = SRC / "web_app"
DOCS_ROOT = ROOT / "docs"
APP_VERSION = "v0.113.0"


def load_local_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        clean = line.strip()
        if not clean or clean.startswith("#") or "=" not in clean:
            continue

        key, value = clean.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ[key] = value


load_local_env()
sys.path.insert(0, str(SRC))

from agent_core.main_agent import AgentRequest, MainAgent  # noqa: E402
from agent_core.operating_model import operating_model_progress, project_documentation  # noqa: E402
from agent_core.tools.service_case_knowledge import ServiceCaseKnowledgeBase  # noqa: E402
from agent_core.workflows.athena_mvp_workflow import AthenaMvpWorkflow  # noqa: E402
from agent_core.workflows.hermes_integration_workflow import HermesIntegrationWorkflow  # noqa: E402
from agent_core.workflows.production_operations_workflow import ProductionOperationsWorkflow  # noqa: E402
from agent_core.workflows.training_automation_workflow import TrainingAutomationWorkflow  # noqa: E402


def safe_print(message: str) -> None:
    if sys.stdout is None:
        return
    try:
        print(message)
    except Exception:
        pass


class DemoHandler(SimpleHTTPRequestHandler):
    agent = MainAgent()
    service_case_knowledge = ServiceCaseKnowledgeBase()
    athena_mvp_workflow = AthenaMvpWorkflow()
    hermes_integration_workflow = HermesIntegrationWorkflow()
    production_operations_workflow = ProductionOperationsWorkflow()
    training_automation_workflow = TrainingAutomationWorkflow()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def log_message(self, format: str, *args) -> None:
        safe_print(f"{self.address_string()} - {format % args}")

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/api/reset":
            self._handle_reset()
            return

        if path == "/api/service-cases/review":
            self._handle_service_case_review()
            return

        if path == "/api/athena-mvp/run":
            self._handle_athena_mvp_run()
            return

        if path == "/api/production/analyze":
            self._handle_production_analyze()
            return

        if path == "/api/production/chatbi":
            self._handle_production_chatbi()
            return

        if path == "/api/production/follow-up/review":
            self._handle_production_follow_up_review()
            return

        if path == "/api/hermes/suggest":
            self._handle_hermes_suggest()
            return

        if path == "/api/hermes/playbook/review":
            self._handle_hermes_playbook_review()
            return

        if path == "/api/training/run":
            self._handle_training_run()
            return

        if path == "/api/training/review":
            self._handle_training_review()
            return

        if path == "/api/training/data-source":
            self._handle_training_data_source()
            return

        if path == "/api/training/handoff-review":
            self._handle_training_handoff_review()
            return

        if path == "/api/training/promote-baseline":
            self._handle_training_promote_baseline()
            return

        if path == "/api/training/regression-run":
            self._handle_training_regression_run()
            return

        if path == "/api/training/regression-gate":
            self._handle_training_regression_gate()
            return

        if path == "/api/training/next-loop":
            self._handle_training_next_loop()
            return

        if path == "/api/training/next-loop-closure":
            self._handle_training_next_loop_closure()
            return

        if path == "/api/training/iteration-proposal":
            self._handle_training_iteration_proposal()
            return

        if path == "/api/training/iteration-proposal-review":
            self._handle_training_iteration_proposal_review()
            return

        if path == "/api/training/codex-work-packets":
            self._handle_training_codex_work_packets()
            return

        if path == "/api/training/codex-patch-queue":
            self._handle_training_codex_patch_queue()
            return

        if path == "/api/training/codex-execution-gate":
            self._handle_training_codex_execution_gate()
            return

        if path == "/api/training/codex-execution-review":
            self._handle_training_codex_execution_review()
            return

        if path == "/api/training/codex-worktree-prep":
            self._handle_training_codex_worktree_prep()
            return

        if path == "/api/training/codex-worktree-launch":
            self._handle_training_codex_worktree_launch()
            return

        if path == "/api/training/codex-worktree-result":
            self._handle_training_codex_worktree_result()
            return

        if path == "/api/training/codex-worktree-result-review":
            self._handle_training_codex_worktree_result_review()
            return

        if path == "/api/training/codex-promotion-candidates":
            self._handle_training_codex_promotion_candidates()
            return

        if path == "/api/training/codex-promotion-approval":
            self._handle_training_codex_promotion_approval()
            return

        if path == "/api/training/codex-promotion-handoff":
            self._handle_training_codex_promotion_handoff()
            return

        if path == "/api/training/codex-promotion-execution-readiness":
            self._handle_training_codex_promotion_execution_readiness()
            return

        if path == "/api/training/codex-promotion-readiness-review":
            self._handle_training_codex_promotion_readiness_review()
            return

        if path == "/api/training/codex-promotion-execution-result":
            self._handle_training_codex_promotion_execution_result()
            return

        if path == "/api/training/codex-promotion-closure-audit":
            self._handle_training_codex_promotion_closure_audit()
            return

        if path == "/api/training/codex-promotion-sync-review":
            self._handle_training_codex_promotion_sync_review()
            return

        if path == "/api/training/codex-promotion-sync-review-gate":
            self._handle_training_codex_promotion_sync_review_gate()
            return

        if path == "/api/training/codex-promotion-sync-handoff":
            self._handle_training_codex_promotion_sync_handoff()
            return

        if path == "/api/training/codex-promotion-sync-readiness":
            self._handle_training_codex_promotion_sync_readiness()
            return

        if path == "/api/training/codex-promotion-sync-readiness-review":
            self._handle_training_codex_promotion_sync_readiness_review()
            return

        if path == "/api/training/codex-promotion-sync-execution-result":
            self._handle_training_codex_promotion_sync_execution_result()
            return

        if path == "/api/training/codex-promotion-sync-closure-review":
            self._handle_training_codex_promotion_sync_closure_review()
            return

        if path == "/api/training/codex-promotion-final-sync-handoff":
            self._handle_training_codex_promotion_final_sync_handoff()
            return

        if path == "/api/training/codex-promotion-final-sync-readiness":
            self._handle_training_codex_promotion_final_sync_readiness()
            return

        if path == "/api/training/codex-promotion-final-sync-execution-result":
            self._handle_training_codex_promotion_final_sync_execution_result()
            return

        if path == "/api/training/codex-promotion-final-completion-review":
            self._handle_training_codex_promotion_final_completion_review()
            return

        if path == "/api/training/codex-promotion-final-publication-handoff":
            self._handle_training_codex_promotion_final_publication_handoff()
            return

        if path == "/api/training/codex-promotion-final-publication-readiness":
            self._handle_training_codex_promotion_final_publication_readiness()
            return

        if path == "/api/training/codex-promotion-final-publication-result":
            self._handle_training_codex_promotion_final_publication_result()
            return

        if path != "/api/chat":
            self.send_error(404, "Not found")
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")

        try:
            body = json.loads(raw_body) if raw_body else {}
            request = AgentRequest(
                user_role=body.get("role", "designer"),
                message=body.get("message", ""),
                channel="web",
                session_id=body.get("session_id", "web-demo"),
                attachments=body.get("attachments", []),
                platform_tool=body.get("platform_tool", {}),
            )
            response = self.agent.handle(request)
            self._send_json(asdict(response))
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_service_case_review(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            payload = self.service_case_knowledge.apply_review(
                case_id=body.get("case_id", ""),
                review_status=body.get("review_status", ""),
                review_note=body.get("review_note", ""),
                case_updates=body.get("case_updates", {}),
            )
            self._send_json(payload)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_reset(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            session_id = body.get("session_id", "web-demo")
            self.agent.reset_session(session_id)
            self._send_json({"status": "ok", "session_id": session_id})
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_athena_mvp_run(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.athena_mvp_workflow.run(body))
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_production_analyze(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.production_operations_workflow.analyze(body))
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_production_chatbi(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.production_operations_workflow.chatbi(body))
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_production_follow_up_review(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.production_operations_workflow.apply_follow_up_review(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_hermes_suggest(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.hermes_integration_workflow.suggest(body))
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_hermes_playbook_review(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.hermes_integration_workflow.apply_playbook_review(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_run(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.run(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_review(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.apply_task_review(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_data_source(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.register_data_source(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_handoff_review(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.apply_handoff_review(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_promote_baseline(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.promote_baseline(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_regression_run(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.regression_run(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_regression_gate(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.regression_gate(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_next_loop(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.next_loop_handoff(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_next_loop_closure(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.next_loop_closure(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_iteration_proposal(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.iteration_proposal(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_iteration_proposal_review(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.apply_iteration_proposal_review(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_work_packets(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.codex_work_packets(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_patch_queue(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.codex_patch_queue(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_execution_gate(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.codex_execution_gate(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_execution_review(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.apply_codex_execution_review(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_worktree_prep(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.codex_worktree_preparation_queue(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_worktree_launch(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.codex_worktree_launch_gate(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_worktree_result(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.apply_codex_worktree_result(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_worktree_result_review(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.apply_codex_worktree_result_review(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_promotion_candidates(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.codex_promotion_candidates(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_promotion_approval(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.apply_codex_promotion_approval(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_promotion_handoff(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.codex_promotion_handoff(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_promotion_execution_readiness(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.codex_promotion_execution_readiness(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_promotion_readiness_review(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.apply_codex_promotion_readiness_review(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_promotion_execution_result(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.apply_codex_promotion_execution_result(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_promotion_closure_audit(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.codex_promotion_closure_audit(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_promotion_sync_review_gate(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.codex_promotion_sync_review_gate(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_promotion_sync_review(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.apply_codex_promotion_sync_review(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_promotion_sync_handoff(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.codex_promotion_sync_handoff(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_promotion_sync_readiness(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.codex_promotion_sync_execution_readiness(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_promotion_sync_readiness_review(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.apply_codex_promotion_sync_readiness_review(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_promotion_sync_execution_result(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.apply_codex_promotion_sync_execution_result(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_promotion_sync_closure_review(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.apply_codex_promotion_sync_closure_review(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_promotion_final_sync_handoff(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.codex_promotion_final_sync_handoff(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_promotion_final_sync_readiness(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.codex_promotion_final_sync_execution_readiness(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_promotion_final_sync_execution_result(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.apply_codex_promotion_final_sync_execution_result(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_promotion_final_completion_review(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.apply_codex_promotion_final_completion_review(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_promotion_final_publication_handoff(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.codex_promotion_final_publication_handoff(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_promotion_final_publication_readiness(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.codex_promotion_final_publication_readiness(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def _handle_training_codex_promotion_final_publication_result(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")
        try:
            body = json.loads(raw_body) if raw_body else {}
            self._send_json(self.training_automation_workflow.apply_codex_promotion_final_publication_result(body))
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
        except Exception as exc:  # pragma: no cover - local demo guardrail
            self._send_json({"error": str(exc)}, status=500)

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/api/status":
            llm_provider = os.environ.get("LLM_PROVIDER", "openai").strip().lower()
            if llm_provider not in {"openai", "deepseek"}:
                llm_provider = "openai"
            active_model = (
                os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
                if llm_provider == "deepseek"
                else os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
            )
            active_enabled = bool(
                os.environ.get("DEEPSEEK_API_KEY")
                if llm_provider == "deepseek"
                else os.environ.get("OPENAI_API_KEY")
            )
            self._send_json(
                {
                    "version": APP_VERSION,
                    "active_llm_provider": llm_provider,
                    "active_llm_model": active_model,
                    "active_llm_enabled": active_enabled,
                    "openai_key_configured": bool(os.environ.get("OPENAI_API_KEY")),
                    "openai_model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                    "llm_provider": llm_provider,
                    "deepseek_key_configured": bool(os.environ.get("DEEPSEEK_API_KEY")),
                    "deepseek_model": os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
                }
            )
            return

        if path == "/api/operating-model":
            self._send_json(operating_model_progress())
            return

        if path == "/api/project-docs":
            self._send_json(project_documentation())
            return

        if path == "/api/service-cases":
            self._send_json(self.service_case_knowledge.review_cases())
            return

        if path == "/api/athena-mvp/template":
            self._send_json(self.athena_mvp_workflow.template())
            return

        if path == "/api/production/template":
            self._send_json(self.production_operations_workflow.template())
            return

        if path == "/api/production/adapter-contract":
            self._send_json(self.production_operations_workflow.adapter_contract())
            return

        if path == "/api/production/skills":
            self._send_json(self.production_operations_workflow.skill_registry())
            return

        if path == "/api/production/tianpai-aps-export":
            self._send_json(self.production_operations_workflow.tianpai_aps_erp_export())
            return

        if path == "/api/production/overview":
            self._send_json(self.production_operations_workflow.overview())
            return

        if path == "/api/production/priority-brief":
            self._send_json(self.production_operations_workflow.priority_brief())
            return

        if path == "/api/production/evidence-review":
            self._send_json(self.production_operations_workflow.evidence_review_queue())
            return

        if path == "/api/production/daily-brief":
            self._send_json(self.production_operations_workflow.daily_brief())
            return

        if path == "/api/production/demo-story-pack":
            self._send_json(self.production_operations_workflow.demo_story_pack())
            return

        if path == "/api/production/internal-demo-candidate":
            self._send_json(self.production_operations_workflow.internal_demo_candidate())
            return

        if path == "/api/production/follow-up":
            self._send_json(self.production_operations_workflow.follow_up_loop())
            return

        if path == "/api/production/material-risk":
            self._send_json(self.production_operations_workflow.material_risk())
            return

        if path == "/api/production/data-readiness":
            self._send_json(self.production_operations_workflow.data_readiness())
            return

        if path == "/api/production/question-bank":
            self._send_json(self.production_operations_workflow.question_bank())
            return

        if path == "/api/hermes/template":
            self._send_json(self.hermes_integration_workflow.template())
            return

        if path == "/api/hermes/overview":
            self._send_json(self.hermes_integration_workflow.overview())
            return

        if path == "/api/hermes/playbook":
            self._send_json(self.hermes_integration_workflow.playbook())
            return

        if path == "/api/training/template":
            self._send_json(self.training_automation_workflow.template())
            return

        if path == "/api/training/overview":
            self._send_json(self.training_automation_workflow.overview())
            return

        if path == "/api/training/reviews":
            self._send_json(self.training_automation_workflow.reviews())
            return

        if path == "/api/training/handoff-reviews":
            self._send_json(self.training_automation_workflow.handoff_reviews())
            return

        if path == "/api/training/round-summary":
            self._send_json(self.training_automation_workflow.round_summary())
            return

        if path == "/api/training/playbook-regression":
            self._send_json(self.training_automation_workflow.playbook_regression())
            return

        if path == "/api/training/regression-run":
            self._send_json(self.training_automation_workflow.regression_run())
            return

        if path == "/api/training/regression-gate":
            self._send_json(self.training_automation_workflow.regression_gate())
            return

        if path == "/api/training/next-loop":
            self._send_json(self.training_automation_workflow.next_loop_handoff())
            return

        if path == "/api/training/next-loop-closure":
            self._send_json(self.training_automation_workflow.next_loop_closure())
            return

        if path == "/api/training/iteration-proposal":
            self._send_json(self.training_automation_workflow.iteration_proposal())
            return

        if path == "/api/training/iteration-proposal-reviews":
            self._send_json(self.training_automation_workflow.iteration_proposal_reviews())
            return

        if path == "/api/training/codex-work-packets":
            self._send_json(self.training_automation_workflow.codex_work_packets())
            return

        if path == "/api/training/codex-patch-queue":
            self._send_json(self.training_automation_workflow.codex_patch_queue())
            return

        if path == "/api/training/codex-execution-gate":
            self._send_json(self.training_automation_workflow.codex_execution_gate())
            return

        if path == "/api/training/codex-execution-reviews":
            self._send_json(self.training_automation_workflow.codex_execution_reviews())
            return

        if path == "/api/training/codex-worktree-prep":
            self._send_json(self.training_automation_workflow.codex_worktree_preparation_queue())
            return

        if path == "/api/training/codex-worktree-launch":
            self._send_json(self.training_automation_workflow.codex_worktree_launch_gate())
            return

        if path == "/api/training/codex-worktree-results":
            self._send_json(self.training_automation_workflow.codex_worktree_results())
            return

        if path == "/api/training/codex-worktree-result-review-gate":
            self._send_json(self.training_automation_workflow.codex_worktree_result_review_gate())
            return

        if path == "/api/training/codex-worktree-result-reviews":
            self._send_json(self.training_automation_workflow.codex_worktree_result_reviews())
            return

        if path == "/api/training/codex-promotion-candidates":
            self._send_json(self.training_automation_workflow.codex_promotion_candidates())
            return

        if path == "/api/training/codex-promotion-approvals":
            self._send_json(self.training_automation_workflow.codex_promotion_approvals())
            return

        if path == "/api/training/codex-promotion-approval-gate":
            self._send_json(self.training_automation_workflow.codex_promotion_approval_gate())
            return

        if path == "/api/training/codex-promotion-handoff":
            self._send_json(self.training_automation_workflow.codex_promotion_handoff())
            return

        if path == "/api/training/codex-promotion-execution-readiness":
            self._send_json(self.training_automation_workflow.codex_promotion_execution_readiness())
            return

        if path == "/api/training/codex-promotion-readiness-reviews":
            self._send_json(self.training_automation_workflow.codex_promotion_readiness_reviews())
            return

        if path == "/api/training/codex-promotion-execution-results":
            self._send_json(self.training_automation_workflow.codex_promotion_execution_results())
            return

        if path == "/api/training/codex-promotion-closure-audit":
            self._send_json(self.training_automation_workflow.codex_promotion_closure_audit())
            return

        if path == "/api/training/codex-promotion-sync-review-gate":
            self._send_json(self.training_automation_workflow.codex_promotion_sync_review_gate())
            return

        if path == "/api/training/codex-promotion-sync-reviews":
            self._send_json(self.training_automation_workflow.codex_promotion_sync_reviews())
            return

        if path == "/api/training/codex-promotion-sync-handoff":
            self._send_json(self.training_automation_workflow.codex_promotion_sync_handoff())
            return

        if path == "/api/training/codex-promotion-sync-readiness":
            self._send_json(self.training_automation_workflow.codex_promotion_sync_execution_readiness())
            return

        if path == "/api/training/codex-promotion-sync-readiness-reviews":
            self._send_json(self.training_automation_workflow.codex_promotion_sync_readiness_reviews())
            return

        if path == "/api/training/codex-promotion-sync-execution-results":
            self._send_json(self.training_automation_workflow.codex_promotion_sync_execution_results())
            return

        if path == "/api/training/codex-promotion-sync-closure-audit":
            self._send_json(self.training_automation_workflow.codex_promotion_sync_closure_audit())
            return

        if path == "/api/training/codex-promotion-sync-closure-review-gate":
            self._send_json(self.training_automation_workflow.codex_promotion_sync_closure_review_gate())
            return

        if path == "/api/training/codex-promotion-sync-closure-reviews":
            self._send_json(self.training_automation_workflow.codex_promotion_sync_closure_reviews())
            return

        if path == "/api/training/codex-promotion-final-sync-handoff":
            self._send_json(self.training_automation_workflow.codex_promotion_final_sync_handoff())
            return

        if path == "/api/training/codex-promotion-final-sync-readiness":
            self._send_json(self.training_automation_workflow.codex_promotion_final_sync_execution_readiness())
            return

        if path == "/api/training/codex-promotion-final-sync-execution-results":
            self._send_json(self.training_automation_workflow.codex_promotion_final_sync_execution_results())
            return

        if path == "/api/training/codex-promotion-final-sync-closure-audit":
            self._send_json(self.training_automation_workflow.codex_promotion_final_sync_closure_audit())
            return

        if path == "/api/training/codex-promotion-final-completion-review-gate":
            self._send_json(self.training_automation_workflow.codex_promotion_final_completion_review_gate())
            return

        if path == "/api/training/codex-promotion-final-completion-reviews":
            self._send_json(self.training_automation_workflow.codex_promotion_final_completion_reviews())
            return

        if path == "/api/training/codex-promotion-final-publication-handoff":
            self._send_json(self.training_automation_workflow.codex_promotion_final_publication_handoff())
            return

        if path == "/api/training/codex-promotion-final-publication-readiness":
            self._send_json(self.training_automation_workflow.codex_promotion_final_publication_readiness())
            return

        if path == "/api/training/codex-promotion-final-publication-results":
            self._send_json(self.training_automation_workflow.codex_promotion_final_publication_results())
            return

        if path == "/api/training/codex-promotion-final-publication-closure-audit":
            self._send_json(self.training_automation_workflow.codex_promotion_final_publication_closure_audit())
            return

        if path == "/api/training/codex-promotion-final-release-review-gate":
            self._send_json(self.training_automation_workflow.codex_promotion_final_release_review_gate())
            return

        if self._send_docs_file(path):
            return

        self.path = path
        super().do_GET()

    def _send_docs_file(self, path: str) -> bool:
        relative = unquote(path).lstrip("/")
        if not relative:
            return False

        if relative.startswith("docs/"):
            relative = relative[len("docs/") :]

        candidate = (DOCS_ROOT / relative).resolve()
        try:
            candidate.relative_to(DOCS_ROOT)
        except ValueError:
            return False

        if not candidate.is_file():
            return False

        content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        payload = candidate.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
        return True

    def _send_json(self, payload: dict, status: int = 200) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        super().end_headers()


def main() -> None:
    host = "127.0.0.1"
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("WEB_DEMO_PORT", "8765"))
    server = ThreadingHTTPServer((host, port), DemoHandler)
    safe_print(f"AI Knitting Agent Demo running at http://{host}:{port}")
    safe_print(f"Version: {APP_VERSION}")
    safe_print(f"LLM provider: {os.environ.get('LLM_PROVIDER', 'openai')}")
    safe_print(f"OpenAI key configured: {bool(os.environ.get('OPENAI_API_KEY'))}")
    safe_print(f"OpenAI model: {os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')}")
    safe_print(f"DeepSeek key configured: {bool(os.environ.get('DEEPSEEK_API_KEY'))}")
    safe_print(f"DeepSeek model: {os.environ.get('DEEPSEEK_MODEL', 'deepseek-chat')}")
    safe_print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()




