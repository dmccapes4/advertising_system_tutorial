# 02 · Dictionaries, Lists, and JSON

> **Abstract.** If you learn **one thing** in this module, learn **JSON**. Tool schemas, API
> bodies, MCP definitions, and Claude responses are all JSON-shaped data. This module starts
> there, then maps JSON to Python dicts and lists.

**Time:** ~60 min

---

## JSON — start here

**JSON** stands for **JavaScript Object Notation**. Despite the name, it is not "for
JavaScript only" — it is the standard text format for sending structured data between
services, agents, databases, and tools.

### Disclaimer — JSON vs SQL

**SQL is older and more important.** It is how relational databases store, query, and join
the rows that power almost every business system — including the advertising knowledge base
we build in later modules. If software had a single native language for data, SQL would win on
seniority and depth.

**SQL can also be very tedious.** `SELECT`, `JOIN`, `WHERE`, migrations, indexes — powerful,
but a lot of ceremony for reading one shaped blob of data. You will touch SQL in this project;
you do not need to master it to read Claude API code.

**JSON is easy.** Plain text. One object notation. Keys and values you can read without a
compiler. That is why JSON sits on every API boundary — including the one between your agent
and our tools — even when SQL sits underneath.

**For this cohort:** learn JSON first and well. Respect SQL as the foundation; let the system
handle the tedious parts until you need to go deeper.

JSON is plain text you can read in any editor. It has only a few building blocks:

| Notation | Name | What it holds |
|----------|------|----------------|
| `{` … `}` | **object** | named fields — **key: value** pairs |
| `[` … `]` | **array** | ordered list of values |
| `"text"` | **string** | text (keys are always strings in JSON) |
| `42`, `3.14` | **number** | integer or decimal |
| `true` / `false` | **boolean** | yes / no |
| `null` | **null** | intentionally empty / missing |

### Objects — `{` starts a new object notation

Curly braces **`{`** open an **object**. Everything inside is **`"key": value`** — a label,
a colon, then a value. Keys are always written in double quotes. Values can be:

- a **basic type** (string, number, boolean, `null`)
- an **array** `[ ... ]`
- **another JSON object** `{ ... }` nested inside

Commas separate entries. No comma after the last one (trailing commas are invalid in strict JSON).

### Example — one book (read the shape)

```json
{
  "title": "Breakthrough Copy",
  "topics": ["copywriting", "hooks"]
}
```

Line by line:

- **`{`** — start object.
- **`"title": "Breakthrough Copy"`** — key `title`, value is a **string** (the book name).
- **`"topics": ["copywriting", "hooks"]`** — key `topics`, value is an **array** of two strings.
- **`}`** — end object.

Two keys at the top level. One value is basic (string); one value is an array. Same object,
mixed value types — that is normal.

### Example — tool use (nested objects)

This is the shape Claude returns when it wants to call a tool:

```json
{
  "type": "tool_use",
  "name": "advertising_knowledge",
  "input": {
    "query": "copyright risks in ad copy"
  }
}
```

Line by line:

- Top-level object — three keys: `type`, `name`, `input`.
- **`"type": "tool_use"`** — basic string; tells you *what kind of block* this is.
- **`"name": "advertising_knowledge"`** — basic string; *which tool* Claude chose.
- **`"input": { ... }`** — value is **another whole object**, not a string. That inner object
  holds the tool's arguments.
- Inside `input`: **`"query": "copyright risks in ad copy"`** — one argument, string value.

To reach the query text by hand: open the outer object → find key `input` → open that inner
object → find key `query`. Nesting is just objects inside objects. Four levels deep is
common in API work; do not be alarmed by depth — follow one key at a time.

**Arrays in the wild** — a list of books might look like:

```json
{
  "books": ["Breakthrough Copy", "Audience First", "The Legal Ad"]
}
```

Here `"books"` is the key; the value is an array of strings, not a nested object.

---

## Python — JSON objects are called dicts

When JSON is loaded into Python, an object `{ ... }` becomes a **dict** (dictionary). An array
`[ ... ]` becomes a **list**. The mental model is identical; only the punctuation changes
(JSON uses double quotes on keys; Python allows single quotes too).

Same book, in Python:

```python
book = {"title": "Breakthrough Copy", "topics": ["copywriting", "hooks"]}
book["title"]           # "Breakthrough Copy"  — key lookup
book.get("year", 2010)  # safe default if key missing
```

Same tool-use block:

```python
tool_use = {
    "type": "tool_use",
    "name": "advertising_knowledge",
    "input": {"query": "copyright risks in ad copy"},
}
tool_use["input"]["query"]   # "copyright risks in ad copy"
```

**Reading nested dicts:** each `[key]` drills one level — `tool_use["input"]` gives you the
inner dict; `["query"]` on that gives you the string. Same path you traced in JSON by eye.

## Lists (JSON arrays)

```python
books = ["Breakthrough Copy", "Audience First", "The Legal Ad"]
books[0]                  # first item — "Breakthrough Copy"
for title in books:
    print(title)
```

In JSON, that list is `"books": [ ... ]` inside an object. In Python, you often hold the
list alone or as a dict value — same data, same order.

## Moving between JSON text and Python — `json` module

On the wire (HTTP, files, logs), JSON is a **string**. Python dicts live in memory.

```python
import json

payload = {"query": "retention email sequence", "top_k": 5}
text = json.dumps(payload)       # dict → JSON string (for request body)
back = json.loads(text)          # JSON string → dict again
```

`library_dictionary.json` in `code/rag/` is a real file on disk — JSON text. When the RAG
code loads it, `json.loads` (or `json.load`) turns it into nested Python dicts the router
can read.

## Objects = dicts with structure — `@dataclass`

Raw dicts are fine for one-off API payloads. **Production code uses typed objects** for
database rows and API contracts — at minimum Python's `@dataclass`:

```python
from dataclasses import dataclass, asdict

@dataclass
class AdBriefingRequest:
    query: str
    top_k: int = 5

req = AdBriefingRequest(query="retention email", top_k=3)
asdict(req)   # {'query': '...', 'top_k': 3}  — serializes like JSON
```

**Why this matters:** Postgres rows, MCP tool inputs, webhook payloads, and belief-update
records are all *shaped data*. A dataclass documents the fields, gives defaults, and can
carry methods (see Module 8 `KnowledgeEntry.update()`). Pydantic (Module 5) adds validation;
dataclass is the floor.

This is the most important step after "JSON is the shape."

## Relational IDs {#relational-ids}

Real systems split data across **tables** (orders, customers, campaigns). Each row has an
**ID** — its primary key. Rows also reference other rows via **foreign keys**: the order
stores a `customer_id` that *belongs to* a customer, not the other way around.

```python
# Same order_id string — two different lookups (Module 1, third block)
customer = get_customer_by_order_id(order_id)  # order → customer_id → customer row
order = get_order(order_id)                      # order_id → order row directly
```

| Function | ID you pass | What the database does |
|----------|-------------|-------------------------|
| `get_order(order_id)` | order's primary key | One table: fetch that order |
| `get_customer_by_order_id(order_id)` | order's primary key | Order first, then follow `customer_id` to the customer |
| `get_customer(customer_id)` | customer's primary key | One table: fetch that customer — **different ID** |

**Read function names as relationship hints.** If the name says `by_order_id`, the path goes
through the order table even though the return value is a customer dict. Module 8's six schemas
(`Decision`, `FeedbackEvent`, `KnowledgeEntry`, …) are the same idea at scale: typed rows
linked by ID columns, modeled as `@dataclass` objects in Python.

## Running example — library dictionary

See `code/rag/library_dictionary.json`. The router agent reads this JSON file to pick books:

```json
{
  "Breakthrough Copy": {
    "strengths": ["copywriting", "hooks", "headlines"]
  },
  "The Legal Ad": {
    "strengths": ["copyright", "compliance", "disclaimers"]
  }
}
```

This is JSON all the way down:

- Top-level keys are **book titles** (strings).
- Each value is a **nested object** with one key so far: `"strengths"`.
- `"strengths"` values are **arrays** of topic strings the router matches against queries.

No Python yet — just notation. When ingested, it becomes nested dicts exactly like the book
and tool-use examples above.

## System design — map of objects vs array of objects

The same ten books can be stored two different ways. Both are valid JSON. The choice affects
how you **look up**, **iterate**, and **change** data — a real architecture decision, not
style.

### Pattern A — one object, keys *are* the identifiers (what we use today)

This is `library_dictionary.json`: a single JSON **object** whose keys are book titles.
You iterate by **pulling keys** (and their values):

```json
{
  "Breakthrough Copy": {
    "strengths": ["copywriting", "hooks", "headlines"]
  },
  "The Legal Ad": {
    "strengths": ["copyright", "compliance", "disclaimers"]
  }
}
```

```python
library = json.loads(path.read_text())

for title, meta in library.items():       # pull each key + its nested object
    print(title, meta["strengths"])

legal = library["The Legal Ad"]           # direct lookup by title — O(1)
```

**When this wins:** small, stable catalogs (~10 books); the name *is* the handle; you often
want "give me everything about **this** book" by title. Our router reads the whole map once
and matches query words against each book's `strengths`.

**Trade-offs:**

| Pros | Cons |
|------|------|
| Instant lookup: `library["The Legal Ad"]` | Keys must be unique — duplicate titles impossible |
| No redundant `title` field inside each value | Renaming a book means changing a key everywhere it is referenced |
| Compact for a fixed set you address by name | Order is not meaningful (you are not "book #3") |
| Reads naturally as a **dictionary** / registry | Awkward if items arrive from SQL as **rows** (rows want to be lists) |

### Pattern B — array of objects (same books, different shape)

Same information as a **JSON array** — each book is one object in the list, usually with an
explicit `title` (or `slug`) field inside:

```json
[
  {
    "title": "Breakthrough Copy",
    "strengths": ["copywriting", "hooks", "headlines"]
  },
  {
    "title": "The Legal Ad",
    "strengths": ["copyright", "compliance", "disclaimers"]
  }
]
```

```python
books = json.loads(path.read_text())

for book in books:                        # iterate the list — each item is an object
    print(book["title"], book["strengths"])

legal = next(b for b in books if b["title"] == "The Legal Ad")   # scan to find one
```

**When this wins:** data from APIs and databases (Postgres returns **rows** → JSON arrays);
ordered pipelines ("process books in this sequence"); every item has the **same fields** —
easy to validate with `@dataclass` / Pydantic; stable `slug` survives a title edit.

**Trade-offs:**

| Pros | Cons |
|------|------|
| Order is explicit — `[0]`, `[1]`, or "first match in loop" | Lookup by title requires a loop (or building a map yourself) |
| Same shape every row — `{title, strengths, ...}` | Slightly more bytes — `title` repeated in every object |
| Matches SQL `SELECT * FROM books` → list of rows | Two books with the same title are possible (sometimes a bug) |
| Natural for "return all citations" tool output | One more nesting level if wrapped: `{"books": [...]}` |

### Side by side — one operation, two shapes

| Task | Pattern A (map) | Pattern B (array) |
|------|-----------------|-------------------|
| Loop over all books | `for title, meta in library.items()` | `for book in books` |
| Get one book by title | `library["The Legal Ad"]` | scan or build `{b["title"]: b for b in books}` |
| Append a new book | `library["New Book"] = {...}` | `books.append({...})` |
| Router reads strengths | key + `meta["strengths"]` | `book["title"]` + `book["strengths"]` |

### Why our tutorial uses both

- **`library_dictionary.json`** — Pattern A. Ten known books, looked up by name, loaded once
  for routing. The map *is* the library index.
- **`mock_pages.json` / future corpus** — Pattern B. Each **page** is a row-shaped object
  `{book, page, text, topics}` in an array — same shape repeated, easy to filter in a loop
  (`if p["book"] == book` in `advertising_knowledge.py`).
- **Tool responses** — often Pattern B or nested objects: a briefing returns `"citations": [
  {"book": "...", "page": 42}, ... ]` — ordered list of uniform objects.

**Rule of thumb:** use a **map** when names are the handles and the set is small and stable;
use an **array of objects** when rows stream from a database, order matters, or every item
shares the same schema. Wrong choice is not fatal — you can convert — but picking the shape
that matches your lookup pattern saves loops and confusion later.

### Session log — `session_log.json` / `session_log.jsonl`

**This is not a formatting detail. It is how agentic systems stay sane.**

Every system we build in this tutorial — and TartaurusLoop in production — writes a
**session log**: an append-only record of what happened, in order, with timestamps. I use it
in TartaurusLoop and in most systems I ship. You should too.

#### Why an agentic loop without a session log is dangerous

Module 4 introduces the canonical pattern:

```python
while response.stop_reason == "tool_use":
    tool_results = execute_tools(response)
    response = client.messages.create(...)
```

That `while` loop is powerful — and **unbounded by default**. If `stop_reason` never becomes
`end_turn`, the loop never exits. Same failure mode as `while True:` in ordinary Python: the
process spins until the **OS kills it**, and every iteration allocates more messages, tool
results, and context in RAM. An infinite agentic loop **eats memory as fast as any infinite
loop** — often faster, because each lap calls an API and grows the transcript.

A session log does not *by itself* stop the loop — you still need max iterations, timeouts, and
validation (Module 4). But **without** a log you are flying blind: you cannot see *how many*
laps ran, *which* tool fired repeatedly, or *what* error the agent kept ignoring. Operators
find out when the machine slows down or the process disappears. That is not operable.

#### Three jobs of the session log

1. **Audit** — Don's team (and you, six months later) can answer: *what did the system actually
   do before this briefing or campaign decision?* Not what the model *said* it did — what the
   pipeline recorded. Pairs with Module 8 `BeliefLog` for belief updates; session log covers
   the run itself.

2. **Debug** — "Why did it pick *The Legal Ad*?" → open the log, find the `route` entry. No
   guessing from the final JSON response.

3. **Break repetition** — agents repeat mistakes when they have no memory of failure. The log
   gives the *next* lap (or the next run, or a human operator) structured evidence: *we already
   tried probe with these hooks and got zero passages; do not retry the same plan.* In advanced
   setups you feed log excerpts back into the prompt; at minimum the log prevents you from
   manually re-running the same broken pipeline three times.

TartaurusLoop writes one log entry per phase (SPECIFY, VALIDATE, INTEGRATE) per stage. When
validation fails, the log shows **FAIL** before the loop retries — so you see the mistake
*before* context balloons.

#### The shape — Pattern B, uniform events

Each line in the log is the same JSON object shape (array in `.json`, one object per line in
`.jsonl`):

```json
[
  {
    "timestamp": "2026-06-23T03:34:41.907524+00:00",
    "phase": "SPECIFY",
    "stage": "route",
    "detail": "selected books: ['The Legal Ad', 'Breakthrough Copy']"
  },
  {
    "timestamp": "2026-06-23T03:34:41.909944+00:00",
    "phase": "SPECIFY",
    "stage": "probe",
    "detail": "4 passages"
  },
  {
    "timestamp": "2026-06-23T03:34:41.913840+00:00",
    "phase": "VALIDATE",
    "stage": "synthesize",
    "detail": "PASS"
  }
]
```

This is **not** the chat transcript the model sees. It is **operator provenance** — compact,
grep-friendly, same keys every time: `timestamp`, `phase`, `stage`, `detail`.

Live file in this repo: `code/loop/tartaurus/output/session_log.json` after a Tartaurus run.

#### Choosing `.json` vs `.jsonl`

Both are JSON. The difference is **how you append** as the run grows:

| Format | File | How it grows | Best for |
|--------|------|--------------|----------|
| **JSON array** | `session_log.json` | Load array, append entry, rewrite whole file | Tutorial runs, short pipelines, read entire run in one editor tab |
| **JSON Lines** | `session_log.jsonl` | Append one JSON object + newline — never rewrite the file | Long agentic runs, production, `tail -f session_log.jsonl` while it runs |

**JSON Lines** — same events, one object per line, no wrapping `[ ]`:

```
{"timestamp": "...", "phase": "SPECIFY", "stage": "route", "detail": "selected books: ['The Legal Ad']"}
{"timestamp": "...", "phase": "VALIDATE", "stage": "route", "detail": "FAIL: min_books not met"}
{"timestamp": "...", "phase": "SPECIFY", "stage": "route", "detail": "retry: expanded query hooks"}
```

```python
with open("session_log.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(entry) + "\n")
```

Use **`.jsonl`** when the agent might loop dozens of times and you need crash-safe append
without loading megabytes into RAM just to add one line. Use **`.json`** when the run is short
and you want one pretty file to hand Don. **Same schema either way** — pick the file format
for how the run scales, not for what you log.

#### Name it honestly

Prefer **`session_log.json`** or **`session_log.jsonl`**. The filename should say *log*. A
generic `session.json` hides the purpose. In this tutorial TartaurusLoop writes
`session_log.json` alongside `checklist.json` (what finished) and `result.json` (final output).
**Log = story of the run. Checklist = resume points. Result = deliverable.**

**Rule of thumb for agentic work:** if a system has a `while` loop and calls tools, it should
have a session log. No log → no audit trail, no repetition guard, no way to diagnose a runaway
loop except Task Manager.

## Exercise — predict the value

Given:

```python
response = {
    "type": "tool_use",
    "name": "lookup_order",
    "input": {"order_id": "12345"},
}
```

What does `response["input"]["order_id"]` return? *(Build intuition by prediction, not lecture.)*

Trace it in JSON terms first: object → key `input` → inner object → key `order_id`.

## AI systems angle

Every Anthropic `messages.create(...)` call sends a **JSON array** of message objects. Every
tool definition is a **JSON object**. Every `tool_use` block in the response is a **JSON
object** — often nested like the example above. Module 6 walks a full request/response pair
on the advertising tool.

**SQL stores the rows; JSON carries the conversation; `session_log` carries the truth about
what your pipeline actually did.** Without that log, an agentic `while` loop is an infinite
loop waiting to happen — Module 4 caps iterations; Module 7 writes the receipt.
