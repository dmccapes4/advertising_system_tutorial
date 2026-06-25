# Foundation for AI Systems

**Read this before everything else.** It's short, blunt, and foundational — the ideas the
rest of this tutorial quietly assumes.

> **The running example.** This is a *tutorial* for Don's team (AJA / UndrDog Hemp & Primal
> Queen), not a product pitch. To keep every idea concrete, the whole thing is built around
> one running example: agents that improve advertising using a **~10-book knowledge base** —
> one tool returns a **curated, cited briefing** instead of pasting whole books into context.
> TartaurusLoop orchestrates the pipeline; a six-schema loop score-keeps what works. Whenever
> a chapter needs specifics — data shapes, metrics, schemas — we **assume something reasonable
> and say so**. The example is a vehicle for the concepts.

---

## 1. What a system actually is

Formally, a **system** is a set of interacting components that **maintain state over time**
and transform inputs into outputs to provide a service. The load-bearing words are
*maintain state over time* — at bottom, a system is **a service that persists user data**.
Strip away the framing and that's the job.

Which means the **primary responsibility of any system is to manage data honestly.**
Everything good or bad about a system follows from how it treats the data entrusted to it:

- **Drop data, or mutate it without provenance**, and you degrade trust — the user can no
  longer believe what the system tells them, because they can't see *why* it says it.
- **Persist and propagate data that's no longer relevant**, and you create **entropy**:
  noise that, for an AI system, becomes **model-context degradation** — the agent reasons
  over junk and gets worse.

The way out is an **epistemic approach**: treat every stored fact as a claim with a basis,
a timestamp, and a reason it's still here. This is exactly why **skills** are so useful — a
skill can *automatically attach epistemic lineage* (what was decided, on what evidence, when)
to actions where a human would usually be too lazy to write it down. This is also why we insist
on **`session_log.json`** (Module 2) and **`BeliefLog`** (Module 8): honest data management
stops being discipline you have to remember and becomes a property of the tooling.

## 2. What an LLM actually is

An LLM is **heuristic-management infrastructure.** That's the most useful way to think
about it. Building systems used to mean writing and maintaining mountains of brittle
heuristics; an LLM absorbs that overhead:

- **Regex becomes optional.** Instead of fragile pattern code that breaks when the input
  shape changes, you describe what you want. Regex drops to a *performance optimization*
  you reach for when you need it — not a tedious necessity.
- **Conditional nightmares evaporate.** A sprawling `if/elif` tree collapses into a
  sentence in a system prompt.
- **Retrieval is offloaded to an agent**, which can compose better queries than
  hand-written deterministic logic ever could.

You spend your effort on intent and contracts, not on the heuristic scaffolding.

## 3. Where the "knowledge" lives (and why it matters)

The pipeline is:

```
training data  →  weighted parameters  →  system prompt  →  user prompt  →  context
```

Here's the part people get wrong: **the agent does not know what is in its training
data.** (That's essentially correct — the one nuance: a model can sometimes *reproduce*
memorized text, but it has no queryable index of its corpus and can't reliably tell you
what it was trained on.) The training data shaped the **parameters** — billions or
trillions of **tensor weights** on a transformer — and was then, in effect, thrown away.
Your prompts and context are interpreted *across those weights* to predict the next token.
There is **no step where the model reviews your context against a stored copy of the
training data** — the training data is far too massive to load onto a transformer.
The knowledge isn't *retrieved*; it's *baked into the weights*.

This is why a small **llama model running locally and offline** can quote Shakespeare in
German one query and write a Python script the next, with nothing fetched from anywhere.
**The magic is in the parameters.**

Two consequences fall out of this, and they're the whole point of the tutorial:

**(a) Overloading context hurts reasoning.** Every token of context is interpreted
across all those weights. Hand the agent an entire book to use one legitimate page of
evidence and you've made it *harder* for the model to reason about the actual problem —
often a **net negative**, especially with stronger models that could already half-recall
the book anyway. Our 10-book RAG exists to fight exactly this.

**(b) A slight misquote is not a hallucination.** If you *didn't* give the model the
text and it quotes a book *almost* right, that isn't fabrication — it means the book was
in its training data and the model predicted each next token *close* to the real text.
It's next-token prediction working as designed, with a small error bar. (Hallucination
is when it invents something with no basis — different failure entirely.) That gap
between "almost the real words" and "the real words" is the clearest possible picture of
what these models do: **predict, not look up.** Citations from *your* library fix this.

## 4. Inference

**Inference** is filling a gap by predicting the most likely completion from limited
signal plus prior knowledge. For an LLM, *every output is inference* — next-token
prediction conditioned on the prompt. For a person, it's the same act: when someone
describes a problem, you infer the real issue, the feature underneath it, and the likely
codebase structure involved.

It's also where it goes wrong. When you don't catch yourself, you **start guessing beyond
what you actually know** — and the output drifts. An agent does the identical thing: give it
an unclear prompt and thin context and it keeps inferring past the evidence — a "helpful"
helper function that's never called, code that's plausible but wrong. Same mechanism, same
failure: **inference is powerful right up until it runs out of signal, and then it bluffs.**

## 5. Precision (ask for it, not permission)

**Precision** is using the **minimal amount of context required to successfully complete
an operation** — no more, no less. It's the direct antidote to §3(a): give the model
exactly what the task needs so its reasoning lands on *your* problem.

The mantra: **AI engineers ask for precision, not permission.**

Bluntly: this is the line between being in the loop and not. A vibe coder who prompts
without understanding writes **bloated, imprecise** prompts — they don't ask for *"a feature
with this contract and this endpoint, wired into the app here."* They ask **"AI, go do it,"**
and accept whatever comes back. That's **asking permission** — handing over authorship and
accountability and hoping. It works until it doesn't, and when it breaks they can't debug
what they never specified. Precision keeps *you* the author of intent; the agent executes
a contract you defined. Permission outsources the thinking and quietly removes you from
the loop.

Everything after this document — JSON, tools, agentic loops, RAG, score keeping — is
*precision applied at scale*: give each part of the system the smallest sufficient context,
with honest provenance, and let the agents do the rest.

---

*Next (still Session 1): [`FOUNDATION_COMPUTER_ENGINEERING.md`](FOUNDATION_COMPUTER_ENGINEERING.md)
— the machine under the system: ports, daemons, kernel, storage, networking, HTTP, streams.*

*Then: [`00_OVERVIEW_AND_RUNNING_EXAMPLE.md`](00_OVERVIEW_AND_RUNNING_EXAMPLE.md) — CCA-F
reframe, named venv, module map.*

*Origin: adapted from `../advertising_systems_tutorial_legacy/00_INTRODUCTION_TO_AI_SYSTEMS.md`.*
