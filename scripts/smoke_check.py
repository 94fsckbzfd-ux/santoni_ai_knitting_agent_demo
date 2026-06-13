"""Fast local smoke checks for daily Santoni Athena development.

This script is intentionally lighter than the full test harness. It checks the
parts most likely to catch day-to-day regressions:
- Python compilation.
- Mojibake / malformed HTML in the current customer-facing production surface.
- Production General Manager API text that is shown in the demo.
- A small set of high-signal tests.
"""

from __future__ import annotations

import argparse
import compileall
import importlib.util
import json
import re
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CRITICAL_STATIC_FILES = [
    ROOT / "src" / "web_app" / "production.html",
    ROOT / "src" / "web_app" / "index.html",
]
MOJIBAKE_TOKENS = [
    "浠婂",
    "澶╂",
    "璁㈠",
    "鎬荤",
    "閹",
    "閻",
    "鈧",
    "鐎",
    "顓",
    "婕旂",
    "鍖",
    "娴犲",
    "绋冲",
    "鐢熶骇",
    "鍊欓",
    "鐩",
    "锛",
    "銆",
    "€?",
    "????",
]
MALFORMED_HTML_PATTERNS = [
    r"(?<!<)/title>",
    r"(?<!<)/h1>",
    r"(?<!<)/h2>",
    r"(?<!<)/span>",
    r"(?<!<)/p>",
    r"(?<!<)/button>",
]
SMOKE_TESTS = [
    "test_project_docs_track_done_and_planned_features",
    "test_customer_home_renders_production_athena_cards",
    "test_user_page_general_manager_dashboard_hierarchy_and_compact_drilldown",
    "test_production_page_defaults_to_chinese_customer_display",
    "test_tianpai_training_pack_structures_voc_and_iot_exports",
    "test_production_operations_workflow_outputs_read_only_management_console",
    "test_production_priority_brief_api_contract_is_read_only",
    "test_production_gm_priority_cards_feed_local_follow_up_contracts",
    "test_production_chatbi_answers_actual_export_management_questions_with_evidence_chains",
    "test_tianpai_aps_erp_export_adapter_machine_style_mismatch_has_required_vs_actual_values",
]


def _relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _scan_text(label: str, text: str) -> list[str]:
    findings: list[str] = []
    for token in MOJIBAKE_TOKENS:
        if token in text:
            findings.append(f"{label}: mojibake token {token!r}")
    for pattern in MALFORMED_HTML_PATTERNS:
        if re.search(pattern, text):
            findings.append(f"{label}: malformed HTML pattern {pattern!r}")
    return findings


def run_compileall() -> bool:
    print("== compileall ==")
    return compileall.compile_dir(str(ROOT / "src"), quiet=1) and compileall.compile_dir(str(ROOT / "scripts"), quiet=1) and compileall.compile_dir(str(ROOT / "tests"), quiet=1)


def run_static_mojibake_scan() -> list[str]:
    print("== static mojibake scan ==")
    findings: list[str] = []
    for path in CRITICAL_STATIC_FILES:
        if not path.exists():
            findings.append(f"{_relative(path)}: missing critical file")
            continue
        findings.extend(_scan_text(_relative(path), path.read_text(encoding="utf-8")))
    return findings


def run_production_api_text_scan() -> list[str]:
    print("== production api text scan ==")
    sys.path.insert(0, str(ROOT / "src"))
    from agent_core.workflows.production_operations_workflow import ProductionOperationsWorkflow

    overview = ProductionOperationsWorkflow().overview()
    priorities = overview.get("management_priority_brief", {}).get("top_priorities", [])
    visible_payload: list[dict[str, Any]] = []
    for item in priorities[:3]:
        visible_payload.append(
            {
                "title_zh": item.get("title_zh", ""),
                "conclusion_zh": item.get("conclusion_zh", ""),
                "reason_zh": item.get("reason_zh", ""),
                "recommended_action_zh": item.get("recommended_action_zh", ""),
                "drilldown_question": item.get("drilldown_question", ""),
            }
        )
    stable_pack = overview.get("stable_demo_story_pack", {})
    visible_payload.append({"stable_demo_story_pack": stable_pack})
    visible_payload.append({"production_overview": overview})
    return _scan_text(
        "ProductionOperationsWorkflow.production_overview",
        json.dumps(visible_payload, ensure_ascii=False),
    )


def run_smoke_tests() -> list[tuple[str, str]]:
    print("== smoke tests ==")
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("test_main_agent", ROOT / "tests" / "test_main_agent.py")
    if spec is None or spec.loader is None:
        return [("load_tests", "Could not load tests/test_main_agent.py")]
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    failures: list[tuple[str, str]] = []
    for name in SMOKE_TESTS:
        start = time.time()
        try:
            getattr(mod, name)()
            print(f"PASS {name} {time.time() - start:.2f}s")
        except Exception as exc:  # pragma: no cover - used as CLI diagnostics
            failures.append((name, repr(exc)))
            print(f"FAIL {name}: {exc!r}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Run fast daily smoke checks for Santoni Athena.")
    parser.add_argument("--skip-compile", action="store_true", help="Skip compileall.")
    parser.add_argument("--skip-tests", action="store_true", help="Skip smoke tests.")
    args = parser.parse_args()

    started = time.time()
    failures: list[str] = []

    if not args.skip_compile and not run_compileall():
        failures.append("compileall failed")

    failures.extend(run_static_mojibake_scan())
    failures.extend(run_production_api_text_scan())

    test_failures: list[tuple[str, str]] = []
    if not args.skip_tests:
        test_failures = run_smoke_tests()
        failures.extend(f"{name}: {error}" for name, error in test_failures)

    summary = {
        "status": "failed" if failures else "passed",
        "failure_count": len(failures),
        "test_failure_count": len(test_failures),
        "elapsed_seconds": round(time.time() - started, 2),
    }
    print(summary)
    if failures:
        for failure in failures:
            print(f"- {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
