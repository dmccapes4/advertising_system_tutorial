# 04 · Control Flow and the Agentic Loop

> **Abstract.** The agentic loop is a **`while` loop with an `if` inside.** Domain 1 (Agentic
> Architecture, 27%) — highest-leverage 60 minutes in the course.

**Time:** ~60 min

---

## Conditionals

```python
if response.stop_reason == "tool_use":
    handle_tools(response)
elif response.stop_reason == "end_turn":
    done = True
else:
    log(f"unexpected: {response.stop_reason}")
```

## The canonical Anthropic agent loop

```python
while response.stop_reason == "tool_use":
    tool_results = execute_tools(response)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=messages + tool_results,
        tools=tools,
    )
# exits when stop_reason == "end_turn"
```

**Read it aloud:** while Claude wants a tool → run tool → send result back → ask again.

With **MCP** (Module 3), your script does not contain this loop — the **host app** (Desktop,
Cursor) runs it: Claude returns `tool_use` → host calls MCP `tools/call` on `server.py` →
host sends `tool_result` → Claude again. Same pattern, different owner of the `while`.

## Exam question waiting to happen

> What happens if `stop_reason` is never `end_turn`?

Answer: **infinite loop** — you need max iterations, timeouts, or escalation. Production systems
always cap the loop. Without a **session log** (Module 2), you also have no record of how many
laps ran or which tool kept firing — the process spins until the OS kills it, eating RAM each
iteration like any runaway `while`.

## Full minimal example

See `code/loop/anthropic_agent_loop.py` — a clean loop with one tool:
`advertising_knowledge`. Run locally with mock data (no API key required in `--dry-run` mode).

```bash
cd code/loop
python anthropic_agent_loop.py --dry-run
python anthropic_agent_loop.py --query "copyright risk in user-generated ad copy"
```

## TartaurusLoop — the production-shaped version

For the **10-book RAG pipeline**, stages (route → probe → gap → synthesize) map to
**TartaurusLoop stages** — spec-driven, checklist-resumable, session-logged. Module 7 runs the
full TartaurusLoop; this module teaches the *inner* `while` loop every Tartaurus `SPECIFY` phase
uses.

**Lineage:** `PortalVision/FullMetalPacket` and `PortalVision/distributions/tartaurus_loop_package/`.
This tutorial ships an **Anthropic SDK** variant in `code/loop/tartaurus/`.

## Exercise

Trace `anthropic_agent_loop.py`: find the `while`, the `if` on `stop_reason`, and where
`advertising_knowledge` gets called.
