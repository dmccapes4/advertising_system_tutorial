"""Load ANTHROPIC_API_KEY from .env (tutorial root) without extra dependencies."""
from __future__ import annotations

import os
from pathlib import Path


def load_env() -> None:
    """Read KEY=value lines from .env into os.environ (setdefault — won't override export)."""
    root = Path(__file__).resolve().parents[1]
    env_file = root / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        val = val.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), val)
