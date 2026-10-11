#!/usr/bin/env python3
"""
Local development runner for the AI Video Generator API.

Starts the FastAPI server with auto-reload and opens a local browser.
Requires: uvicorn, fastapi, and other dependencies from requirements-dev.txt

Usage:
  python3 run_dev.py
"""

import os
import sys
import subprocess
from pathlib import Path

def run_dev_server():
    """Start the development server."""
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Ensure WORK_DIR exists
    work_dir = Path("/tmp/ai-video-gen")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    env = os.environ.copy()
    env["WORK_DIR"] = str(work_dir)
    env["DEVICE"] = "cpu"
    env["FPS"] = "8"
    
    print("=" * 60)
    print("AI Video Generator - Development Server")
    print("=" * 60)
    print(f"Work directory: {work_dir}")
    print("Backend running on: http://localhost:8000")
    print("API docs: http://localhost:8000/docs")
    print("Frontend: http://localhost:3000 (run separately or use docker-compose)")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    # Run uvicorn with auto-reload
    cmd = [
        sys.executable,
        "-m", "uvicorn",
        "main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ]
    
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)

if __name__ == "__main__":
    run_dev_server()
