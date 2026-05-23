"""Run the zero-dependency local web demo."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
WEB_ROOT = SRC / "web_app"
APP_VERSION = "v0.20.1"


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
        os.environ.setdefault(key, value)


load_local_env()
sys.path.insert(0, str(SRC))

from agent_core.main_agent import AgentRequest, MainAgent  # noqa: E402
from agent_core.operating_model import operating_model_progress, project_documentation  # noqa: E402
from agent_core.tools.service_case_knowledge import ServiceCaseKnowledgeBase  # noqa: E402


def safe_print(message: str) -> None:
    try:
        print(message)
    except OSError:
        pass


class DemoHandler(SimpleHTTPRequestHandler):
    agent = MainAgent()
    service_case_knowledge = ServiceCaseKnowledgeBase()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/api/reset":
            self._handle_reset()
            return

        if path == "/api/service-cases/review":
            self._handle_service_case_review()
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

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/api/status":
            self._send_json(
                {
                    "version": APP_VERSION,
                    "openai_key_configured": bool(os.environ.get("OPENAI_API_KEY")),
                    "openai_model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                    "llm_provider": os.environ.get("LLM_PROVIDER", "openai"),
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

        self.path = path
        super().do_GET()

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
