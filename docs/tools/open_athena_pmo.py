from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from datetime import datetime
from pathlib import Path


PORT = 8788
HOST = "127.0.0.1"


def write_log(log_file: Path, message: str) -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file.write_text(
        (log_file.read_text(encoding="utf-8") if log_file.exists() else "")
        + f"[{stamp}] {message}\n",
        encoding="utf-8",
    )


def fetch_json(url: str, timeout: float = 1.0) -> dict | None:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return None


def wait_for_health(url: str, seconds: float = 8.0) -> dict | None:
    deadline = time.time() + seconds
    while time.time() < deadline:
        health = fetch_json(url, timeout=1.0)
        if health and health.get("ok"):
            return health
        time.sleep(0.3)
    return None


def main() -> int:
    tools_dir = Path(__file__).resolve().parent
    docs_dir = tools_dir.parent
    server_py = tools_dir / "athena_pmo_server.py"
    athena_html = docs_dir / "Athena.html"
    log_file = docs_dir / "athena_pmo_launcher.log"
    url = f"http://{HOST}:{PORT}/Athena.html"
    health_url = f"http://{HOST}:{PORT}/api/health"
    self_test = os.environ.get("ATHENA_PMO_SELF_TEST") == "1"
    no_browser = os.environ.get("ATHENA_PMO_NO_BROWSER") == "1" or self_test

    print("Athena PMO Launcher")
    print(f"Document root: {docs_dir}")
    print(f"URL: {url}")
    print()

    if not athena_html.exists():
        message = f"Missing Athena.html: {athena_html}"
        print(message)
        write_log(log_file, message)
        return 1

    if not server_py.exists():
        message = f"Missing server script: {server_py}"
        print(message)
        write_log(log_file, message)
        return 1

    existing = fetch_json(health_url)
    if existing and existing.get("ok"):
        data_file = str(existing.get("dataFile", ""))
        if str(docs_dir) in data_file:
            print("Athena PMO Server is already running.")
            if not no_browser:
                print("Opening Athena in browser...")
                webbrowser.open(url)
            if self_test:
                return 0
            print()
            print("Press Enter to close this launcher window.")
            input()
            return 0

        message = (
            f"Port {PORT} is already used by another Athena server.\n"
            f"Current data file: {data_file}\n"
            "Please close the old Athena PMO Server window and run this launcher again."
        )
        print(message)
        write_log(log_file, message)
        input("Press Enter to close...")
        return 1

    command = [
        sys.executable,
        str(server_py),
        "--root",
        str(docs_dir),
        "--port",
        str(PORT),
    ]
    write_log(log_file, "Starting: " + " ".join(command))
    print("Starting Athena PMO Server...")
    process = subprocess.Popen(command)

    health = wait_for_health(health_url)
    if not health:
        message = "Athena PMO Server did not become ready. Check the server output above."
        print(message)
        write_log(log_file, message)
        if process.poll() is None:
            process.terminate()
        input("Press Enter to close...")
        return 1

    write_log(log_file, f"Started successfully: {url}")
    print("Athena PMO Server is ready.")
    if self_test:
        print("Self-test passed. Stopping test server...")
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=2)
        return 0
    if not no_browser:
        print("Opening Athena in browser...")
        webbrowser.open(url)
    print()
    print("Keep this window open while using Athena.")
    print("Press Ctrl+C in this window to stop the server.")

    try:
        return process.wait()
    except KeyboardInterrupt:
        print("\nStopping Athena PMO Server...")
        if process.poll() is None:
            process.terminate()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
