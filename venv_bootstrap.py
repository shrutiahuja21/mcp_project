"""Re-launch the process under `.venv` when the user runs scripts with the wrong Python."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_VENV_PYTHON = (
    _ROOT / ".venv" / "Scripts" / "python.exe"
    if sys.platform == "win32"
    else _ROOT / ".venv" / "bin" / "python"
)


def ensure_project_venv() -> None:
    if not _VENV_PYTHON.is_file():
        return
    if Path(sys.executable).resolve() == _VENV_PYTHON.resolve():
        return
    script = Path(sys.argv[0]).resolve()
    if script.suffix.lower() != ".py":
        return
    raise SystemExit(
        subprocess.call([str(_VENV_PYTHON), str(script), *sys.argv[1:]])
    )


def project_root() -> Path:
    return _ROOT
