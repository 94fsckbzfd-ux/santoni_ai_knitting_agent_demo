"""Import a service Excel file into draft service-case JSON."""

from __future__ import annotations

import argparse
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from agent_core.tools.service_case_importer import ServiceCaseExcelImporter  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Santoni service Excel into draft service cases.")
    parser.add_argument("xlsx_path", help="Path to the source .xlsx file.")
    parser.add_argument(
        "--output",
        default=str(ROOT / "src" / "mock_data" / "service_cases.draft_import.json"),
        help="Output JSON path. Defaults to src/mock_data/service_cases.draft_import.json.",
    )
    args = parser.parse_args()

    xlsx_path = Path(args.xlsx_path).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    if not xlsx_path.exists():
        raise SystemExit(f"Excel file not found: {xlsx_path}")

    summary = ServiceCaseExcelImporter().import_file(xlsx_path, output_path)
    print(asdict(summary))


if __name__ == "__main__":
    main()
