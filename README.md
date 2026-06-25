# Python for CCA-F — AJA Tutorial

Tutorial for the **AI Jedi Academy** cohort preparing for the **Claude Certified Architect —
Foundations (CCA-F)** exam. Teaches the Python needed to read Skilljar course code, using a
**10-book advertising knowledge assistant** as the running example.

> **Private consulting deliverable.** Built for Don Ranns and his company — not for public
> release. The publishable product line lives in
> [`../advertising_systems_tutorial_legacy/`](../advertising_systems_tutorial_legacy/).

**Source brief:** `Python_for_CCA-F_Teaching_Brief.docx`

**Build plan:** [`md/TUTORIAL_IMPLEMENTATION_PLAN.md`](md/TUTORIAL_IMPLEMENTATION_PLAN.md) — phased path from mock corpus to full MCP + Postgres + Bayesian loop.

## Quick start

Two steps: **(1)** set up the named venv + deps for your OS, **(2)** build and read. Pick the row
for your system — the helper scripts are idempotent (safe to re-run) and create your `.env` for you.

> If you run into issues simply double-click index.html. The mermaid diagrams may not render, but all material will.

### Step 1 — set up the venv (choose your OS)

| OS / shell | Command (run from this folder) |
|------------|--------------------------------|
| **macOS / Linux / WSL** | `source setup_venv.sh` |
| **Windows (PowerShell)** | `. .\setup_venv.ps1` |

> **Run them "sourced" / "dot-sourced"** — `source ...` on bash/zsh, `. .\...` on PowerShell —
> so the `(aja-cca-f)` prefix sticks in your prompt. Running them plainly still builds the venv and
> installs deps; you'd just activate manually afterward (the script prints the exact line).

> **WSL users (important):** if this project sits on a Windows drive (a `/mnt/c/...` path),
> `setup_venv.sh` **automatically puts the venv on fast native-Linux storage** (`~/venvs/aja-cca-f`).
> Building a venv directly on `/mnt/c` goes through WSL's slow filesystem bridge and can take
> *45 minutes*; off the bridge it's seconds. The script handles this for you.

### Step 2 — build and read

```bash
python build_reader.py            # generates index.html
```

Then **open `index.html`** in any browser — that's enough to read the whole tutorial offline.

### By hand (if you'd rather see each step)

```bash
# macOS / Linux / WSL
python3 -m venv aja-cca-f                 # name it — not .venv
source aja-cca-f/bin/activate
pip install -r requirements.txt
python build_reader.py
```

```powershell
# Windows (PowerShell)
python -m venv aja-cca-f
.\aja-cca-f\Scripts\Activate.ps1
pip install -r requirements.txt
python build_reader.py
```

## Serving / sharing the tutorial

Reading only needs `index.html` opened directly. To **serve** it (so phones/PCs on the same Wi-Fi
can read it, or to demo HTTP live):

| OS | Quiet | Live request log (demo) |
|----|-------|--------------------------|
| **Windows** | double-click `serve.bat` | double-click `serve-log.bat` |
| **macOS / Linux / WSL** | `python -m http.server 8000` | `python -m http.server 8000` (logs requests by default) |

`serve-log.bat` prints every page users open as they navigate — `time  client-IP  method  path -> status` —
which is a nice live demo of "HTTP is one request, one response." Both Windows scripts show a
"Share on Wi-Fi" link; the `serve.ps1 -Log` form is what the demo bat calls under the hood.

## Modules

| # | File | Topic |
|---|------|-------|
| — | [`md/FOUNDATION_FOR_AI_SYSTEMS.md`](md/FOUNDATION_FOR_AI_SYSTEMS.md) | **Read first** — AI systems foundation |
| — | [`md/FOUNDATION_COMPUTER_ENGINEERING.md`](md/FOUNDATION_COMPUTER_ENGINEERING.md) | **Session 1** — ports, daemons, kernel, storage, networking, HTTP, streams |
| 00 | `md/00_OVERVIEW_AND_RUNNING_EXAMPLE.md` | Reframe + 10-book RAG intro |
| 01 | `md/01_PYTHON_SURVIVAL_KIT.md` | Read Python (45 min) |
| 02 | `md/02_DICTIONARIES_LISTS_JSON.md` | Dicts, JSON, `@dataclass` (60 min) |
| 03 | `md/03_FUNCTIONS_TYPE_HINTS_TOOLS.md` | Functions & tools (60 min) |
| 04 | `md/04_CONTROL_FLOW_AND_THE_AGENTIC_LOOP.md` | Agentic loop (60 min) |
| 05 | `md/05_DECORATORS_IMPORTS_PYDANTIC.md` | OOP, decorators, Pydantic (75 min) |
| 06 | `md/06_READING_REAL_ANTHROPIC_SDK_CODE.md` | SDK + env vars (60 min) |
| 07 | `md/07_TEN_BOOK_RAG_WITH_TARTAURUSLOOP.md` | Full RAG + TartaurusLoop |
| 08 | `md/08_BAYESIAN_SIX_SCHEMA_LOOP.md` | Six-schema score keeping |

```bash
python code/rag/advertising_knowledge.py "fair use in ad copy"
python code/mcp/server.py                        # MCP server (pip install mcp)
python code/loop/tartaurus/run_advertising_rag.py --dry-run
python code/schemas/bayesian_loop.py
```

## Layout

```
README.md              # entry point (stays at root)
md/                    # all tutorial prose (modules, foundations, manifest, plan)
html/                  # visual explainers (right pane in index.html)
code/                  # runnable examples
build_reader.py        # md/ + html/ → index.html
index.html             # offline reader (double-click or serve)
```

## Code layout

```
code/
  rag/
  mcp/           # Module 3 — MCP server example
  loop/
  schemas/       # Module 8 — six @dataclass Bayesian contracts
```

## Legacy

Prior advertising-systems engineering tutorial (Bayesian loops, graphs, decay):
`../advertising_systems_tutorial_legacy/`

## Dependencies

All pinned in `requirements.txt` (installed by the Step 1 scripts above): `markdown` (builds the
reader), `anthropic` (live Claude/TartaurusLoop runs), `mcp` (Module 3 MCP server). `anthropic` and
`mcp` are only needed for the live code runs, not for reading the tutorial.
