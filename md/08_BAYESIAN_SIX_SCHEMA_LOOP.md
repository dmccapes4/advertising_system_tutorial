# 08 · The Six-Schema Bayesian Loop (Score Keeping)

> **Abstract.** After the RAG pipeline produces a cited briefing, the system *learns*: every
> briefing is a **hypothesis** (`Decision`), campaign metrics are **evidence** (`FeedbackEvent`),
> and the book pages that informed the call get **score-keeping** updates (`KnowledgeEntry`
> α/β). Six small tables — modeled as **`@dataclass` contracts** — record the full loop with
> append-only provenance (`BeliefLog`).

---

## The loop in one breath

```
RAG briefing  →  Decision (hypothesis)  →  campaign runs  →  FeedbackEvent (evidence)
       ↑                                                          │
       └──────── KnowledgeEntry re-weighted ← BeliefLog (receipt) ┘
```

This is **not** black-box RL. Every update names the entry, the decision, and the outcome.

## The six schemas (Postgres flavor → Python `@dataclass`)

| # | Table / class | Role |
|---|---------------|------|
| 1 | `KnowledgeEntry` | Book-page belief (α, β, weight) |
| 2 | `Edge` | Graph links between entries |
| 3 | `Decision` | Agent judgment = hypothesis |
| 4 | `DecisionEntry` | Which entries informed the decision |
| 5 | `FeedbackEvent` | Metrics = evidence |
| 6 | `BeliefLog` | Append-only audit of every update |

See `code/schemas/bayesian_loop.py` — runnable dry demo:

```bash
python code/schemas/bayesian_loop.py
```

## Score keeping (the math, kept simple)

Each `KnowledgeEntry` carries a Beta belief over "does relying on this page lead to good
outcomes?"

- **Prior:** `α = β = 2` (weakly optimistic).
- **Evidence:** one campaign settles → success/failure draw.
- **Update:** success → `α += 1`; failure → `β += 1`.
- **Weight:** `α / (α + β)` — used to re-rank retrieval.

That's it. Thompson sampling and decay are optional extensions (legacy tutorial doc 04).

## Wiring to Module 7

| Tartaurus / RAG stage | Bayesian stage |
|-----------------------|----------------|
| SYNTHESIZE → briefing | feeds into `Decision.summary` |
| citations in briefing | become `DecisionEntry` rows |
| campaign metrics webhook | inserts `FeedbackEvent` |
| nightly job | runs `apply_feedback`, writes `BeliefLog` |

Two graphs, one loop (conceptual):

- **`ad_knowledge_graph`** — stable book pages (`KnowledgeEntry`); re-ranked, never deleted.
- **`commerce_graph`** — campaigns and metrics (busy); see legacy doc 06 for decay/eviction.

## SQL reference (production)

The full DDL lives in `../advertising_systems_tutorial_legacy/04_BAYESIAN_LEARNING_LOOP.md`
§7. In Python we prefer dataclasses + an ORM or raw SQL — the *shapes* are what matter.

## Exercise

1. Run `python code/schemas/bayesian_loop.py` and read the printed dicts.
2. Change `baseline` in `FeedbackEvent.from_metric` so success flips — watch α/β move.
3. Name which class is the **hypothesis** and which is the **evidence**.

## Why dataclasses here

Module 2: JSON ≈ dict. Module 8: **production contracts ≈ `@dataclass`** — typed fields,
defaults, methods like `update()` and `weight`. Same data as the database row; honest state
with receipts in `BeliefLog`.
