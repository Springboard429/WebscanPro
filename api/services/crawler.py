import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

RESULT_FILE = Path("result.json")


def _python_exec() -> str:
    repo_root = Path(__file__).resolve().parents[2]
    venv_python = repo_root / ".venv" / "bin" / "python"
    return str(venv_python if venv_python.exists() else Path(sys.executable))


async def run_crawler(
    url: str,
    login_url: Optional[str] = None,
    username: str = "admin",
    password: str = "password",
    output_path: Optional[Path] = None,
) -> dict:
    """
    Runs the web crawler and returns the parsed result.json data.
    """
    output_file = output_path or RESULT_FILE

    cmd = [
        _python_exec(),
        "main.py",
        "--url",
        url,
        "--depth",
        "3",
        "--concurrent",
        "10",
        "--timeout",
        "30",
        "--output",
        str(output_file),
    ]

    if login_url:
        cmd.extend(["--login", "--login-url", login_url, "--username", username, "--password", password])

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=Path(__file__).parent.parent.parent,
    )

    stdout, _ = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(f"Crawler failed: {stdout.decode()}")

    if not output_file.exists():
        raise FileNotFoundError(f"Crawler did not produce {output_file}")

    with open(output_file, "r") as f:
        return json.load(f)


def load_crawler_result(path: Optional[Path] = None) -> dict:
    """Load existing crawler result from disk."""
    result_file = path or RESULT_FILE
    if not result_file.exists():
        raise FileNotFoundError(f"Crawler result not found at {result_file}")
    with open(result_file, "r") as f:
        return json.load(f)
