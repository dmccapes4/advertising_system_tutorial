# 03 · Functions, Type Hints, and Tools

> **Abstract.** In agent systems, a **tool** is either a **function** (imported and called by
> code) or a **file** (run as a script). Same Python file can be both. Read definitions,
> understand type hints and docstrings, and see why Claude picks one tool over another
> (Domain 2 — Tool Design, 18%).

**Time:** ~60 min

---

## Tools are functions — or files

When Skilljar or MCP talks about a "tool," it almost always boils down to one of these:

| What the agent sees | What it really is | How it runs |
|---------------------|-------------------|-------------|
| **Function tool** | A `def` in a `.py` file | Another module **imports** the function and calls it |
| **Script / CLI tool** | A `.py` file with a `main` entry | You (or the agent) **run the file**: `python something.py` |

Both are just Python. The difference is **how execution starts** — not a different language feature.

---

## Functions

```python
def advertising_knowledge(query: str, top_k: int = 5) -> dict:
    """Search the 10-book library and return a cited briefing."""
    passages = search_books(query, limit=top_k)
    return {"briefing": synthesize(passages), "citations": passages}
```

- **`def`** — defines a callable unit (a tool handler is just a function).
- **`query: str`** — type hint: expected string.
- **`top_k: int = 5`** — default parameter.
- **`-> dict`** — return type hint.
- **Docstring** — natural-language description; **this is how Claude selects tools.**

---

## Two ways to use the same file

Take `code/rag/advertising_knowledge.py`. It defines a function **and** can be run from the
terminal. Those are two different paths into the same code.

### Path A — import the function (agent / MCP / another module)

```python
from advertising_knowledge import advertising_knowledge

result = advertising_knowledge("fair use in ad headlines")
print(result["briefing"])
```

Here Python **loads the file as a module** and gives you the function. The agent loop (Module 4)
registers this function as a tool — when Claude calls `advertising_knowledge`, the runtime
invokes the `def`, not the whole file as a subprocess.

**When this wins:** MCP servers, Anthropic tool lists, unit tests, TartaurusLoop importing stage
helpers. One process, direct function call, return value is a Python dict (→ JSON to the model).

### Path B — run the file (CLI / operator / quick test)

```bash
python code/rag/advertising_knowledge.py "fair use in ad headlines"
```

At the bottom of that file:

```python
if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "copyright fair use ad headlines"
    result = advertising_knowledge(q)
    print(result["briefing"])
```

**`if __name__ == "__main__":`** means: *only run this block when someone executes this file
directly* — not when another file imports it.

| How the file is used | Value of `__name__` | Does the `__main__` block run? |
|----------------------|----------------------|--------------------------------|
| `python advertising_knowledge.py ...` | `"__main__"` | **Yes** — CLI path |
| `from advertising_knowledge import advertising_knowledge` | `"advertising_knowledge"` (module name) | **No** — import path only |

**When this wins:** you want a script operators can run without writing import code;
`run_advertising_rag.py` (Module 7) uses the same pattern with a `main()` function and
`if __name__ == "__main__": main()`.

### Side by side

| | **Import the function** | **Run the file** |
|---|-------------------------|------------------|
| Command | `from x import fn; fn(args)` | `python x.py args` |
| Entry point | the `def` | `__main__` block (often calls the same `def`) |
| Typical caller | agent loop, MCP, tests | human in terminal, cron, shell script |
| Return value | Python dict/object in memory | usually **printed** stdout (text) |
| Same file? | Yes — one file, two doors | Yes |

**Teaching moment:** MCP tool handlers are almost always **Path A** — a function the server
imports once and calls many times. Path B is how you smoke-test the same logic before wiring
it into the agent.

---

## Example MCP server — same function, exposed to Claude

**MCP** (Model Context Protocol) is how Claude Desktop, Cursor, and other clients **discover
and call** your tools over a standard wire. Under the hood it is still Path A: a Python
process imports your function and invokes it when the model asks.

Full runnable example: `code/mcp/server.py`

```python
#!/usr/bin/env python3
"""MCP server — advertising_knowledge tool (Module 3)."""
from __future__ import annotations

import sys
from pathlib import Path

# Make the RAG module importable (same pattern as anthropic_agent_loop.py)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "rag"))
from advertising_knowledge import advertising_knowledge as _advertising_knowledge

from mcp.server.fastmcp import FastMCP

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
```

Read it in layers:

| Lines | What they do |
|-------|----------------|
| `sys.path.insert(...)` | Python can find `code/rag/advertising_knowledge.py` |
| `from advertising_knowledge import ... as _advertising_knowledge` | **Path A** — import the real function |
| `FastMCP("advertising-knowledge")` | Create an MCP server other apps can connect to |
| `@mcp.tool()` | Register the function below as a callable tool (Module 5: this is a **decorator**) |
| `def advertising_knowledge(query: str) -> dict:` | Same type hints as Module 3 — MCP uses them for the tool schema |
| docstring | Same job as Anthropic SDK `description` — Claude reads this to pick the tool |
| `return _advertising_knowledge(query)` | Delegate to the RAG function — one line, no duplicate logic |
| `mcp.run()` | **Path B for the server file** — start listening when you `python server.py` |

Run it (after `pip install mcp`):

```bash
python code/mcp/server.py
```

The process stays up; Claude (or another MCP client) sends tool calls; the server imports and
runs your function for each call.

### MCP vs Anthropic SDK tool list — same tool, two registrations

Module 4's `anthropic_agent_loop.py` registers the **same** tool manually as JSON:

```python
TOOLS = [{
    "name": "advertising_knowledge",
    "description": "Search the company's 10-book advertising library...",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The advertising question to answer"},
        },
        "required": ["query"],
    },
}]

def execute_tool(name: str, tool_input: dict) -> str:
    if name == "advertising_knowledge":
        result = advertising_knowledge(tool_input["query"])
        return json.dumps(result, indent=2)
```

| | **Anthropic SDK (Module 4)** | **MCP (this section)** |
|---|------------------------------|-------------------------|
| Who registers the tool | You hand-write `TOOLS` JSON | `@mcp.tool()` + type hints + docstring |
| Who calls the function | Your `while` loop → `execute_tool()` | MCP runtime when Claude requests the tool |
| Same RAG function? | Yes — `advertising_knowledge(query)` | Yes — `_advertising_knowledge(query)` |
| Typical use | Script you own end-to-end | Shared tool other apps (Desktop, IDE) can reuse |

Both are Path A at the Python level. MCP adds a **standard socket** so multiple clients can share
the same tool server without each one copy-pasting the JSON schema.

### What happens when a user asks for a tool — full MCP path

This is the sequence to internalize. **Claude never runs your Python.** The model **asks** for
a tool; the **host application** (Claude Desktop, Cursor, etc.) **runs** it via MCP and feeds
the result back.

#### Who is in the room

| Role | What it is | Our tutorial |
|------|------------|--------------|
| **User** | Human typing the question | Don's team in Desktop / Cursor |
| **Host app** | UI + MCP **client** + Anthropic API caller | Claude Desktop, Cursor chat |
| **Model** | Claude on the API — reads, plans, writes | Decides *whether* to call a tool |
| **MCP server** | Separate Python process you wrote | `python code/mcp/server.py` |
| **Tool function** | Plain `def` inside the server | `_advertising_knowledge(query)` |

The host sits in the middle. It talks to Claude **and** to your MCP server. The model never
opens `advertising_knowledge.py` directly.

#### Phase 0 — before the user asks (startup)

1. You (or the host app on launch) start the MCP server: `python code/mcp/server.py`.
2. The host's MCP **client** connects to that process (stdio, socket, or config the app manages).
3. The client calls **`tools/list`** — "what tools do you expose?"
4. FastMCP answers from your `@mcp.tool()` registrations — name, description, JSON Schema for
   `query: str` (built from type hints + docstring).
5. The host now knows `advertising_knowledge` exists and what arguments it accepts.

Nothing runs yet except discovery. Your RAG code is loaded in the server process but idle.

#### Phase 1 — user message

User types:

> Is this headline OK under fair use? Check our ad library.

The host sends a **`messages.create`** (or equivalent chat request) to Anthropic with:

- the user's text (and system prompt, history, etc.)
- the **tool definitions** it learned from MCP in Phase 0 (same shape as Module 4's `TOOLS` JSON)

Claude reads the question and the available tools. **No tool runs yet** — this is inference only.

#### Phase 2 — model activates the tool (decision, not execution)

Claude returns a response where `stop_reason == "tool_use"`. Inside the response content is a
block like Module 2's JSON example:

```json
{
  "type": "tool_use",
  "id": "toolu_01ABC...",
  "name": "advertising_knowledge",
  "input": {
    "query": "fair use in advertising headlines"
  }
}
```

**This is activation at the model layer:** Claude chose the tool name and filled `input` from
your schema. It did **not** execute Python — it emitted a structured *request*.

Think: the model wrote a form that says *"please run advertising_knowledge with this query."*

#### Phase 3 — host executes via MCP (real run)

The host app (not Claude) sees `tool_use` and:

1. Parses `name` → `"advertising_knowledge"` and `input` → `{"query": "..."}`.
2. Sends MCP **`tools/call`** to your server with those arguments.
3. FastMCP dispatches to your decorated function:
   `_advertising_knowledge("fair use in advertising headlines")`.
4. Inside Python: `route` → `probe` → `gap` → `synthesize` (Module 7 pipeline).
5. The function returns a **dict** (briefing, citations, books consulted).
6. MCP serializes that to JSON and sends it back to the host as the **tool result**.

Your code ran **once**, in the MCP server process, because the **host** bridged model → server.

#### Phase 4 — result back to the model (second inference)

The host appends to the conversation:

- assistant message with the `tool_use` block (what Claude asked for)
- user message with **`tool_result`** — the JSON from your server, tied to `tool_use_id`

Then it calls **`messages.create` again** with the longer transcript.

Claude reads the briefing — now it has **grounded evidence** from your library, not weights-only
guesswork — and writes a natural-language answer for the user. Usually `stop_reason == "end_turn"`.

The user sees something like: *"Based on The Legal Ad p.15, fair use in advertising is narrow…"*

#### Phase 5 — if Claude needs another tool (loop)

If the second response is **another** `tool_use` (different tool or retry), the host repeats
Phase 3–4. That is the **agentic loop** (Module 4) — except the host app's loop calls MCP
`tools/call` instead of your inline `execute_tool()`.

Cap iterations. Log to `session_log.json` (Module 2).

#### End-to-end diagram

```
User: "Check fair use in this headline"
         │
         ▼
┌──────────────── Host app (MCP client + API) ────────────────┐
│  messages.create(tools=[advertising_knowledge, ...])         │
└────────────────────────────┬────────────────────────────────┘
                             ▼
                    ┌─────────────────┐
                    │  Claude (model)  │
                    │  stop_reason:    │
                    │  "tool_use"      │
                    │  input: {query}  │
                    └────────┬─────────┘
                             │ model REQUESTS tool — does not run Python
                             ▼
┌──────────────── Host app ────────────────────────────────────┐
│  MCP tools/call("advertising_knowledge", {query: "..."})       │
└────────────────────────────┬─────────────────────────────────┘
                             ▼
┌──────────────── MCP server (server.py) ──────────────────────┐
│  @mcp.tool() → _advertising_knowledge(query) → dict result    │
└────────────────────────────┬─────────────────────────────────┘
                             ▼
┌──────────────── Host app ────────────────────────────────────┐
│  tool_result JSON appended → messages.create again           │
└────────────────────────────┬─────────────────────────────────┘
                             ▼
                    ┌─────────────────┐
                    │  Claude (model)  │
                    │  stop_reason:    │
                    │  "end_turn"      │
                    │  → answer user   │
                    └─────────────────┘
```

#### One sentence summary

**The user asks the host; the host asks Claude; Claude names a tool and arguments; the host runs
that tool on your MCP server; the host gives the result back to Claude; Claude answers the user.**

The **agent activates** the tool by emitting `tool_use` in its response. **Execution** is always
the host calling MCP → your function. That split is why tool design (name, docstring, schema)
matters: it is the only signal Claude has when deciding whether to reach for your library.

---

## Bad vs. good tool descriptions

```python
def analyze_content(text):          # vague — Claude guesses wrong
    ...

def search_ad_library(query: str) -> dict:
    """
    Search the company's 10-book advertising library for passages relevant to
    the query. Returns a short cited briefing — not full book text.
    Use for: ad copy, compliance, retention, offers, audience strategy.
    """
    ...
```

**Teaching moment:** which would Claude invoke for "Is this headline OK under fair use?"?

## Snake_case and verb-first names

Exam and SDK samples use `lookup_order`, `process_refund`, `search_ad_library`. Match that
pattern when you name tools.

## Wiring to the 10-book RAG

In `code/rag/advertising_knowledge.py`:

```python
def advertising_knowledge(query: str) -> dict:
    """One tool, one job — MCP surface for the 10-book library."""
    ...
```

- **As a tool (Path A):** `anthropic_agent_loop.py` (SDK) and `code/mcp/server.py` (MCP) import and register this function.
- **As a script (Path B):** `python advertising_knowledge.py "your query"` hits `__main__`.

Everything else (`route`, `probe`, `gap`, `synthesize`) stays *behind* that door — one tool, one
job; the file holds many functions, but only one is the external tool surface.

## Exercise

1. Write a one-sentence docstring for a tool named `get_campaign_metrics` that returns ROAS and
   spend for a campaign ID. No implementation — docstring only.
2. **Read aloud:** In `advertising_knowledge.py`, what runs when you `import advertising_knowledge`
   from another file — the whole file top to bottom, or only the definitions? What *extra* runs
   when you `python advertising_knowledge.py`?
3. Open `code/mcp/server.py` — trace from `@mcp.tool()` to `_advertising_knowledge(query)`.
4. **Trace the MCP path:** for "Check fair use in this headline," who runs Python first — Claude,
   the host app, or the MCP server? At which step does `stop_reason` become `"tool_use"`?
