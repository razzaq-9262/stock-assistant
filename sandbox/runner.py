"""Isolated Python runner: executes code in a separate process with a timeout."""
import subprocess
import sys
import tempfile

BLOCKED = ("import os", "import subprocess", "import socket", "open(",
           "__import__", "eval(", "exec(")


def run_code(code: str, timeout: int = 10) -> dict:
    """Run untrusted analysis code safely-ish.

    Isolation: separate process, timeout, blocked keywords, temp dir.
    In production this would run inside a Docker container / AWS Fargate task.
    """
    for word in BLOCKED:
        if word in code:
            return {"ok": False, "output": f"Blocked: '{word}' is not allowed"}

    with tempfile.TemporaryDirectory() as tmp:
        try:
            result = subprocess.run(
                [sys.executable, "-I", "-c", code],
                capture_output=True, text=True, timeout=timeout, cwd=tmp,
            )
        except subprocess.TimeoutExpired:
            return {"ok": False, "output": f"Timed out after {timeout}s"}
    ok = result.returncode == 0
    return {"ok": ok, "output": result.stdout if ok else result.stderr}
