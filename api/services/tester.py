import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

from .crawler import RESULT_FILE

BASE_DIR = Path(__file__).parent.parent.parent
MODULES_DIR = BASE_DIR / "modules"


def _python_exec() -> str:
    venv_python = BASE_DIR / ".venv" / "bin" / "python"
    return str(venv_python if venv_python.exists() else Path(sys.executable))


def _module_path(name: str) -> Path:
    return MODULES_DIR / name


def _run_module_sync(script_path: Path, args: list[str]) -> dict:
    """Run a tester module synchronously and return parsed JSON output."""
    cmd = [_python_exec(), str(script_path), *args]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(BASE_DIR),
    )
    # stdout/stderr already printed by the module, we just return parsed results
    return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


async def run_sqli_tester(
    base_url: str,
    login_url: str,
    crawler_result_path: Optional[Path] = None,
) -> list[dict]:
    """Run SQL injection tester module."""
    result_file = crawler_result_path or RESULT_FILE
    script = _module_path("sqli_tester.py")
    args = [base_url, login_url, str(result_file)]

    proc = await asyncio.create_subprocess_exec(
        _python_exec(), str(script), *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=str(BASE_DIR),
    )
    await proc.communicate()

    output_file = _module_path("sqli_vulnerabilities.json")
    if not output_file.exists():
        return []
    with open(output_file, "r") as f:
        return json.load(f)


async def run_xss_tester(
    base_url: str,
    login_url: str,
    crawler_result_path: Optional[Path] = None,
) -> list[dict]:
    """Run XSS tester module."""
    result_file = crawler_result_path or RESULT_FILE
    script = _module_path("xss_tester.py")
    args = [base_url, login_url, str(result_file)]

    proc = await asyncio.create_subprocess_exec(
        _python_exec(), str(script), *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=str(BASE_DIR),
    )
    await proc.communicate()

    output_file = _module_path("xss_vulnerabilities.json")
    if not output_file.exists():
        return []
    with open(output_file, "r") as f:
        return json.load(f)


async def run_access_control_tester(
    base_url: str,
    login_url: str,
    crawler_result_path: Optional[Path] = None,
) -> list[dict]:
    """Run Access Control / IDOR tester module."""
    result_file = crawler_result_path or RESULT_FILE
    script = _module_path("access_control_tester.py")
    args = [base_url, login_url, str(result_file)]

    proc = await asyncio.create_subprocess_exec(
        _python_exec(), str(script), *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=str(BASE_DIR),
    )
    await proc.communicate()

    output_file = _module_path("access_control_vulnerabilities.json")
    if not output_file.exists():
        return []
    with open(output_file, "r") as f:
        return json.load(f)
