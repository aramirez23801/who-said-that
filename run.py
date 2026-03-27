"""
run.py — launch backend + frontend together.

Usage:
    uv run python run.py

Starts:
  • FastAPI backend  on http://localhost:8000
  • Flet  frontend   as a desktop window

Ctrl-C shuts both down cleanly.
"""

import subprocess
import sys
import time
import signal
import os


def main() -> None:
    backend_cmd = [
        sys.executable, "-m", "uvicorn",
        "backend.main:app",
        "--reload",
        "--port", "8000",
        "--log-level", "warning",
    ]
    frontend_cmd = [
        sys.executable, "-m", "frontend.main",
    ]

    print("Starting backend …")
    backend = subprocess.Popen(backend_cmd)

    # Give uvicorn a moment to bind the port before the frontend tries to connect
    time.sleep(1.5)

    print("Starting frontend …")
    frontend = subprocess.Popen(frontend_cmd)

    def shutdown(sig, frame):  # noqa: ARG001
        print("\nShutting down …")
        frontend.terminate()
        backend.terminate()
        frontend.wait()
        backend.wait()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Keep alive until the frontend window is closed
    frontend.wait()
    backend.terminate()
    backend.wait()


if __name__ == "__main__":
    # Ensure the src/ packages are importable when run directly
    src_path = os.path.join(os.path.dirname(__file__), "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    main()
