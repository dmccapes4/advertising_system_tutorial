# 00 · Overview & the Running Example

> **Abstract.** This tutorial prepares the AJA cohort for the **Claude Certified Architect —
> Foundations (CCA-F)** exam by teaching the Python you need to *read* Skilljar course code —
> not Python for its own sake. The running example throughout is a **10-book advertising
> knowledge assistant**: one tool that returns a short, cited briefing so agents never paste
> whole books into context.
>
> **Prerequisite (Session 1):** read [`FOUNDATION_FOR_AI_SYSTEMS.md`](FOUNDATION_FOR_AI_SYSTEMS.md) — systems, LLMs,
> inference, precision — then [`FOUNDATION_COMPUTER_ENGINEERING.md`](FOUNDATION_COMPUTER_ENGINEERING.md) — the machine
> underneath (ports, daemons, kernel, storage, networking, HTTP, streams). This overview assumes both.

---

## The strategic reframe (read this first)

**The CCA-F exam does not test Python.** Sample questions are architecture questions. But
Skilljar gates two of four canonical courses on Python:

| Course | Python prerequisite |
|--------|---------------------|
| Building with the Claude API | Proficiency in Python |
| Introduction to MCP | Working knowledge of Python |

So this tutorial's job is **not** "Python to pass CCA-F." It is **"Python to absorb Skilljar
without getting lost in syntax."** Every module maps a Python construct to an AI-systems
*why*.

## Environment setup — name your venv

Create a virtual environment with a **meaningful name**, not a generic folder:

```bash
python -m venv aja-cca-f          # good — you know what this is
source aja-cca-f/bin/activate     # Linux / macOS / WSL
# aja-cca-f\Scripts\activate      # Windows

pip install -r requirements.txt
```

Naming costs nothing and saves confusion when you have three projects open. A folder called
`.venv` tells you nothing six months later.

> **Shortcut:** `source setup_venv.sh` does all of the above — creates `aja-cca-f` if it's
> missing, activates it in your shell, and installs `requirements.txt`. Run it **sourced** (not
> `./setup_venv.sh`) so the activation sticks; a script in a child shell can't activate yours.

Copy `.env.example` → `.env` for `ANTHROPIC_API_KEY`, or `export` it in your shell (Module 6).

## The running example: 10-book advertising RAG

You own ~10 excellent advertising books. Agents need cited passages — not whole books.

```
Agent  ──question──▶  advertising_knowledge (tool)  ──curated briefing──▶  Agent
```

Behind the tool (Modules 6–7):

1. **Route** — pick which books to open (library dictionary).
2. **Probe** — hybrid search per book (keyword hooks + semantic query).
3. **Gap** — what's still missing? fetch only that.
4. **Synthesize** — one concise, cited briefing.

Module 8 closes the loop: briefing → decision → metrics → **score keeping** on the pages
that were cited.

## Modules

| Module | File | Time | Focus |
|--------|------|------|-------|
| — | `FOUNDATION_FOR_AI_SYSTEMS.md` | 20 min | AI systems — read first |
| — | `FOUNDATION_COMPUTER_ENGINEERING.md` | 40 min | The machine — Session 1 |
| 1 | `01_PYTHON_SURVIVAL_KIT.md` | 45 min | Read exam code samples |
| 2 | `02_DICTIONARIES_LISTS_JSON.md` | 60 min | Dicts, JSON, **`@dataclass` contracts** |
| 3 | `03_FUNCTIONS_TYPE_HINTS_TOOLS.md` | 60 min | Tools = functions (Domain 2) |
| 4 | `04_CONTROL_FLOW_AND_THE_AGENTIC_LOOP.md` | 60 min | Agentic loops (Domain 1) |
| 5 | `05_DECORATORS_IMPORTS_PYDANTIC.md` | 75 min | OOP, decorators, Pydantic |
| 6 | `06_READING_REAL_ANTHROPIC_SDK_CODE.md` | 60 min | SDK + env vars |
| 7 | `07_TEN_BOOK_RAG_WITH_TARTAURUSLOOP.md` | — | Full RAG + TartaurusLoop |
| 8 | `08_BAYESIAN_SIX_SCHEMA_LOOP.md` | — | Six-schema score keeping |

**Source brief:** `Python_for_CCA-F_Teaching_Brief.docx` (extended with dataclasses, named
venvs, OOP, and Module 8).

## What we teach beyond the brief

- **Named virtualenvs** — always; zero downside.
- **`@dataclass`** — JSON dicts with structure; **database and API contracts** (most important
  shape after raw dicts).
- **OOP basics** — classes hold state and behavior; you will read and write simple ones.

## What we still skip

Async beyond recognition, web frameworks (Flask/FastAPI/Django), pytest, generics, metaclasses,
performance profiling. **Read fluently, write minimally where the exam allows — but write
dataclasses and named envs for real work.**

## Legacy material

Deeper graph/decay/OGrE content: `../advertising_systems_tutorial_legacy/`
