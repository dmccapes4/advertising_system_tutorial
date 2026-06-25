# 06 · Reading Real Anthropic SDK Code

> **Abstract.** Apply Modules 1–5 to real SDK code: a complete agent loop, tool definitions,
> and the 10-book `advertising_knowledge` tool end-to-end.

**Time:** ~60 min · **Mode:** code-walking only — no new concepts

---

## Message list shape

```python
messages = [
    {"role": "user", "content": "What does our library say about email retention?"},
]
```

After a tool call, you append assistant + user tool_result messages (see
`anthropic_agent_loop.py`).

## Tool definition shape (Anthropic)

```python
tools = [{
    "name": "advertising_knowledge",
    "description": "Search the 10-book advertising library...",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The question to answer"},
        },
        "required": ["query"],
    },
}]
```

This is a **nested dict** (Module 2) describing a **function** (Module 3) Claude may invoke in a
**loop** (Module 4).

## Walkthrough checklist

Open `code/loop/anthropic_agent_loop.py` and answer:

1. Where is `Anthropic()` constructed?
2. Where is the `while response.stop_reason == "tool_use"` loop?
3. What dict keys does `advertising_knowledge()` return?
4. Where would you add `max_iterations = 10`?

## Walkthrough — RAG tool only

Open `code/rag/advertising_knowledge.py`:

1. `route(query)` — returns list of book names (Module 2: list of strings).
2. `probe(book, query)` — returns list of passage dicts.
3. `gap(book, found, query)` — conditional fetches (Module 4: if missing topic…).
4. `synthesize(passages)` — returns final briefing dict.

## async / await — recognition only

You may see:

```python
async def handle_request(...):
    response = await client.messages.create(...)
```

**Meaning:** network I/O in flight. You don't need to write it for CCA-F; don't panic when you
see it in Skilljar.

## API keys — `.env` vs `export $VAR` (basics)

Skilljar and our tutorial scripts need `ANTHROPIC_API_KEY`. **Never paste keys into Python
files or commit them to git.**

### Option A — `.env` file (recommended for local work)

1. Copy `.env.example` → `.env` in the tutorial root.
2. Put your key on one line: `ANTHROPIC_API_KEY=sk-ant-...`
3. Our scripts call `code/env_loader.py`, which reads `.env` into the environment.

`.env` is listed in `.gitignore`. Claude Code can *see* a `.env` in your project — that's
fine locally; just don't push it.

### Option B — export in the shell (Linux / macOS / WSL)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
echo $ANTHROPIC_API_KEY    # prints the value (careful in shared screens)
python code/loop/anthropic_agent_loop.py --query "retention email"
```

- **`export`** puts the variable in the environment for this shell session and child processes.
- **`$ANTHROPIC_API_KEY`** (or `$VAR` in general) expands to the value when the shell runs a
  command.

Windows PowerShell equivalent:

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
echo $env:ANTHROPIC_API_KEY
```

### What not to do

- Don't store secrets in markdown notes (easy to share by accident).
- Don't hardcode keys in `anthropic_agent_loop.py`.
- If a key ever appears in chat, logs, or a screenshot — **rotate it** in the Anthropic console.

## Consolidation exercise

Pick any Python snippet in the CCA-F exam guide. Identify: dict access, function def, loop,
conditional, import. If you can label all five, Module 6 succeeded.
