# 07 · The 10-Book RAG System & TartaurusLoop

> **Abstract.** Put it together: staged-reduction RAG as the main example, orchestrated by a
> clean **TartaurusLoop** using the **Anthropic SDK** — spec-driven stages, checklist
> persistence, and an inner agentic tool loop per stage.

---

## The pipeline (one tool, four stages)

```
Query
  → ROUTE    (pick books from library_dictionary.json)
  → PROBE    (keyword hooks + semantic search per book)
  → GAP      (per-book: what's still missing?)
  → SYNTH    (cited briefing for the agent)
```

Each stage is a **TartaurusLoop stage** with `FETCH → SPECIFY → VALIDATE → INTEGRATE`.

## Why TartaurusLoop here

CCA-F teaches the inner `while` loop (Module 4). Production pipelines add:

- **Resumability** — `checklist.json` skips completed stages.
- **Session log** — `session_log.json` records every decision (provenance for operators).
- **Validation** — briefing must have citations before integration.
- **Spec as contract** — `advertising_rag_spec.json` is the single source of truth.

Full implementation lineage: `PortalVision/FullMetalPacket` and
`PortalVision/distributions/tartaurus_loop_package/tartaurus_loop.py`. This tutorial ships an
**Anthropic-native** slim variant.

## Files

| Path | Purpose |
|------|---------|
| `code/rag/library_dictionary.json` | Router input — what each book covers |
| `code/rag/mock_pages.json` | Demo corpus (replace with Postgres/pgvector in production) |
| `code/rag/advertising_knowledge.py` | Pure Python RAG stages (no LLM required) |
| `code/loop/tartaurus/tartaurus_loop.py` | Anthropic SDK TartaurusLoop |
| `code/loop/tartaurus/advertising_rag_spec.json` | Stage definitions |
| `code/loop/tartaurus/run_advertising_rag.py` | Entry point |

## Run it

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-...

cd code/loop/tartaurus
python run_advertising_rag.py --dry-run          # no API — runs RAG stages only
python run_advertising_rag.py --query "fair use in ad headlines"
```

## Stage → Python concept map

| Stage | Teaches |
|-------|---------|
| ROUTE | dict lookup, list filtering |
| PROBE | loops over books, nested dict results |
| GAP | if/else — topic coverage |
| SYNTH | function composition, return dict |
| Tartaurus VALIDATE | Pydantic-style constraints (Module 5) |
| Tartaurus SPECIFY | agentic while loop (Module 4) |

## Production notes (not exam scope)

- Swap `mock_pages.json` for Postgres + `pgvector`.
- Expose `advertising_knowledge` via MCP (`@server.tool()`).
- Add max token budgets per stage (staged reduction — see legacy tutorial doc 02).

## Legacy deep-dive

Bayesian score-keeping, living graphs, and connascence:
`../advertising_systems_tutorial_legacy/`
