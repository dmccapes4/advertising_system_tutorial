#!/usr/bin/env python3
"""MCP server — exposes advertising_knowledge (Module 3 teaching example).

Path A from Module 3: import the function, register with @mcp.tool(), run the server.

  pip install mcp
  python code/mcp/server.py

Wire in Claude Desktop / Cursor MCP config pointing at this script.
  Full production notes: md/TUTORIAL_IMPLEMENTATION_PLAN.md Phase 5.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "rag"))
from advertising_knowledge import advertising_knowledge as _advertising_knowledge  # noqa: E402

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    raise SystemExit("pip install mcp   # MCP SDK for Module 3 example")

mcp = FastMCP("advertising-knowledge")


@mcp.tool()
def advertising_knowledge(query: str) -> dict:
    """Search the company's 10-book advertising library for passages relevant to the query.

    Returns a short cited briefing — not full book text.
    Use for: ad copy, compliance, retention, offers, audience strategy, fair use.
    """
    return _advertising_knowledge(query)


if __name__ == "__main__":
    mcp.run()
