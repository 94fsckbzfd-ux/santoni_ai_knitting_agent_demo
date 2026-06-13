from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


class AthenaPMOHandler(SimpleHTTPRequestHandler):
    server_version = "AthenaPMOServer/0.1"

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    @property
    def data_file(self) -> Path:
        return self.server.data_file  # type: ignore[attr-defined]

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/health":
            self._send_json({"ok": True, "dataFile": str(self.data_file)})
            return
        if path == "/api/athena-project-data":
            self._send_file_json(self.data_file)
            return
        if path == "/":
            self.path = "/Athena.html"
        super().do_GET()

    def do_PUT(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/athena-project-data":
            self.send_error(404, "Unknown API endpoint")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = self.rfile.read(length).decode("utf-8")
            data = json.loads(payload)
            if not isinstance(data, dict) or not isinstance(data.get("modules"), list):
                raise ValueError("Data must contain a modules array")
        except Exception as exc:
            self.send_error(400, f"Invalid JSON: {exc}")
            return

        self._backup_current_data()
        data["updatedAt"] = datetime.now().isoformat(timespec="seconds")
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.data_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        self._send_json({"ok": True, "updatedAt": data["updatedAt"]})

    def _send_file_json(self, path: Path) -> None:
        if not path.exists():
            self.send_error(404, f"Missing data file: {path}")
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            self.send_error(500, f"Cannot read data file: {exc}")
            return
        self._send_json(data)

    def _send_json(self, data: object) -> None:
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _backup_current_data(self) -> None:
        if not self.data_file.exists():
            return
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.data_file.parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.data_file, backup_dir / f"athena_project_data_{stamp}.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve Athena HTML files and shared PMO data.")
    parser.add_argument("--root", default="docs", help="Directory containing Athena HTML files.")
    parser.add_argument("--data", default="data/athena_project_data.json", help="Data file path relative to root.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    data_file = (root / args.data).resolve()
    handler = lambda *handler_args, **handler_kwargs: AthenaPMOHandler(
        *handler_args,
        directory=str(root),
        **handler_kwargs,
    )
    server = ThreadingHTTPServer((args.host, args.port), handler)
    server.data_file = data_file  # type: ignore[attr-defined]
    print(f"Athena PMO Server: http://{args.host}:{args.port}/Athena.html")
    print(f"Data file: {data_file}")
    server.serve_forever()


if __name__ == "__main__":
    main()
