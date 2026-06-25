# Manifest — Python for CCA-F Tutorial

## Purpose

Python literacy for the AJA cohort — **read Skilljar code, recognize patterns**, not become a
Python engineer. Running example: **10-book advertising RAG** (`advertising_knowledge` tool).

**Distribution:** private consulting deliverable for Don Ranns and company — not public.
Publishable architecture: `../advertising_systems_tutorial_legacy/`.

## Documents

All tutorial prose lives in `md/` (this folder). `README.md` stays at the project root.

| File | Module | ~Time |
|------|--------|-------|
| `md/FOUNDATION_FOR_AI_SYSTEMS.md` | Foundation | 20 min |
| `md/FOUNDATION_COMPUTER_ENGINEERING.md` | Foundation | 40 min |
| `md/00_OVERVIEW_AND_RUNNING_EXAMPLE.md` | Overview | — |
| `md/01_PYTHON_SURVIVAL_KIT.md` | 1 | 45 min |
| `md/02_DICTIONARIES_LISTS_JSON.md` | 2 | 60 min |
| `md/03_FUNCTIONS_TYPE_HINTS_TOOLS.md` | 3 | 60 min |
| `md/04_CONTROL_FLOW_AND_THE_AGENTIC_LOOP.md` | 4 | 60 min |
| `md/05_DECORATORS_IMPORTS_PYDANTIC.md` | 5 | 75 min |
| `md/06_READING_REAL_ANTHROPIC_SDK_CODE.md` | 6 | 60 min |
| `md/07_TEN_BOOK_RAG_WITH_TARTAURUSLOOP.md` | 7 | — |
| `md/08_BAYESIAN_SIX_SCHEMA_LOOP.md` | 8 | — |

## Code

| Path | Used in |
|------|---------|
| `code/rag/advertising_knowledge.py` | Modules 3, 6, 7 |
| `code/mcp/server.py` | Module 3 — MCP example |
| `code/loop/anthropic_agent_loop.py` | Modules 4, 6 |
| `code/loop/tartaurus/` | Module 7 |
| `code/schemas/bayesian_loop.py` | Module 8 |

## TartaurusLoop lineage

Canonical: `PortalVision/distributions/tartaurus_loop_package/` and
`PortalVision/FullMetalPacket/`. Tutorial variant uses **Anthropic SDK**.

## Legacy archive

`../advertising_systems_tutorial_legacy/` — prior 00–06 advertising systems tutorial.

## Teaching brief

`Python_for_CCA-F_Teaching_Brief.docx` — authoritative outline from Qui-Gon Don brief.

## Implementation plan

`md/TUTORIAL_IMPLEMENTATION_PLAN.md` — seven phases to build the full system (corpus → Postgres → LLM stages → MCP → Bayesian wiring).
