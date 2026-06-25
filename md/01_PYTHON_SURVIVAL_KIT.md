# 01 · Python Survival Kit

> **Abstract.** Read Python aloud without getting lost. No writing yet — literacy first.
> Every CCA-F sample question contains Python; if you can't read it, the question is unfair.

**Time:** ~45 min · **Goal:** read code line-by-line

---

## Why this matters for AI systems

When you open Skilljar or the exam guide, you see Python immediately. Your job in this module
is **pattern recognition**, not memorization.

## Indentation = scope

**Scope** means: *which lines of code belong together, and which thing "owns" them.*

Think of it like nesting folders. A function is a folder. An `if` inside the function is a
subfolder. A line of code lives inside whatever folder it is indented under. Python does not
use `{` and `}` curly braces to draw those boxes — other languages do. Python uses
**indentation** (usually four spaces, shown here as one tab). If two lines start at the same
column, they are **siblings**: same level, same owner. If a line starts one tab further
right, it is **inside** whatever sits above it.

Walk through the example:

```python
def process_refund(order_id: str) -> dict:
    customer = get_customer(order_id)      # inside the function
    if customer["balance"] < 0:
        return {"status": "denied"}          # inside the if
    return {"status": "approved"}          # inside the function
```

1. **`def process_refund(...)`** — this *starts* a function definition. Everything that
   follows, as long as it stays one tab forward, is **inside that function's scope**. Those
   lines run only when something *calls* `process_refund`. They are not loose code sitting
   at the top of the file.

2. **`customer = get_customer(...)`** — one tab in, so it belongs to the function. When the
   function runs, this line runs first (among the body lines).

3. **`if customer["balance"] < 0:`** — still inside the function, but this *starts a second
   scope*: a **conditional** block. The `if` asks a yes/no question. Lines one tab further
   in (the `return {"status": "denied"}` line) belong to the `if` — they run **only if** the
   balance is negative.

4. **`return {"status": "approved"}`** — back to the same indent as the `if`, so it is still
   inside the **function**, but **outside** the `if`. It runs when the function runs and the
   `if` condition was false (balance was not negative).

So: **`def` = "everything indented under me is this function."** **`if` = "everything
indented under me runs only when this condition is true."** Read the left edge of the screen
first — that tells you the boxes before you read the words on each line.

**Second block — add `else`, and watch what `return` does.**

*This example is intentionally bad code. Read it to learn scope and `return` — do not copy it.*

```python
def process_refund(order_id: str) -> dict:
    customer = get_customer(order_id)
    if customer["balance"] < 0:
        return {"status": "denied"}                              # inside the if
    else:
        return {"status": "error", "message": "account on hold"}  # inside the else
    return {"status": "approved"}                              # ⚠ unreachable — never runs
```

Here the conditional is a **pair**: `if` / `else` sit at the **same indent** — they are
siblings, two branches of one decision. Only one branch runs.

- **`else`** means "otherwise." If the balance is **not** negative, Python skips the `if`
  body and runs the `else` body instead.

- **`return` exits the whole function immediately.** The moment a `return` runs, the function
  is done. No line below it executes on that path.

Trace each path:

| What happened | Branch that runs | Function returns | Does `approved` run? |
|---------------|------------------|------------------|----------------------|
| Balance is negative | `if` | `denied` | **No** — function already exited |
| Balance is zero or positive | `else` | `error` | **No** — function already exited |

Every possible input goes through `if` **or** `else`, and **both branches `return`.** So the
`approved` line at the bottom can **never** run. Python will not crash — it just silently
ignores that line forever. That is **unreachable code** (also called **dead code**): it looks
like it belongs to the function, but no execution path ever reaches it.

### Teaching moment — why this is bad, and how to fix it

Two separate bugs, one lesson:

1. **Unreachable happy path.** Someone started with the first block (deny if negative,
   otherwise approve) and pasted an `else` error return without deleting the old `approved`
   line. The bottom `return` is a fossil — it looks plausible, but it is a lie.

2. **The `else` is too broad.** In the first block, "balance not negative" meant **approve
   the refund.** Here, `else` catches *every* non-negative balance and returns an error —
   including customers who should be approved. The logic is wrong *and* it makes `approved`
   unreachable.

**How to read code like a debugger:** for each branch, ask *"does this path `return`? what
is left after all branches?"* If every branch exits the function, anything below the whole
`if`/`else` is dead unless you meant to leave a fall-through happy path.

**Fixed version** — separate checks, early returns for bad cases, happy path last:

```python
def process_refund(order_id: str) -> dict:
    customer = get_customer(order_id)
    if customer["balance"] < 0:
        return {"status": "denied"}
    if customer["on_hold"]:
        return {"status": "error", "message": "account on hold"}
    return {"status": "approved"}          # runs when neither bad case matched
```

Now there is no `else` swallowing healthy customers. Each `if` guards one failure mode.
If neither fires, execution **falls through** to `approved` — and that line is reachable.

You will see this pattern everywhere in Skilljar: **guard clauses** (early returns for errors)
at the top, **one happy-path return** at the bottom. When you spot unreachable code in the
wild, someone usually merged two versions or made an `else` too greedy.

**Third block — scoped variables, `elif`, and fall-through to the happy path.**

*Good code this time. Same refund function, now with real arithmetic and a warning that does
not stop the refund.*

```python
def process_refund(order_id: str) -> dict:
    customer = get_customer_by_order_id(order_id)
    order = get_order(order_id)

    balance = customer["balance"]              # scoped to this function call
    order_price = order["total"]             # scoped to this function call
    remaining = balance - order_price        # what is left after the refund
    notice = ""                                # empty until a branch sets it

    if balance < order_price:
        return {
            "status": "denied",
            "reason": "insufficient_balance",
            "shortfall": order_price - balance,
        }
    elif remaining < 50:
        notice = "Low account balance after refund — flag for review."
    else:
        log("this is an unnecessary condition")

    return {"status": "approved", "notice": notice}
```

Everything from `balance = ...` through the final `return` lives in **function scope** —
those variables exist only while `process_refund` runs. They are not visible outside the
function. That is why we **assign first, decide second**: read the numbers once, name them,
then use the names in the conditionals.

Walk the branches:

| Situation | Branch | `return` now? | `notice` after branch | Bottom line runs? |
|-----------|--------|---------------|------------------------|-------------------|
| Balance cannot cover refund | `if` | **Yes** → `denied` | — | **No** — function exited |
| Refund OK but `< $50` left | `elif` | No | set to warning text | **Yes** → `approved` + notice |
| Refund OK and `≥ $50` left | `else` | No | still `""` | **Yes** → `approved`, empty notice |

**`if` / `elif` / `else` chain:** Python checks top to bottom and takes **one** branch.

- **`if balance < order_price`** — hard stop. Customer cannot cover the refund; return
  `denied` with the **shortfall** (how many dollars they are short). Same early-exit idea as
  the fixed second block.

- **`elif remaining < 50`** — only evaluated when the `if` was false (balance was enough).
  This branch **does not `return`.** It only assigns `notice`. Execution drops out of the
  conditional block and continues to the bottom — that is **fall-through**. The refund is
  still approved; the caller gets a human-readable warning in `notice`.

- **`else`** — runs only when balance covers the refund **and** `remaining ≥ 50`. The only
  thing inside is a log line saying *"this is an unnecessary condition."* That is deliberate:
  this branch does nothing the fall-through could not do. If `notice` is already `""` and you
  are not returning, you can **delete the `else` entirely** and behavior is identical. Keeping
  it here is a teaching flag — when you see an `else` that only logs or passes, ask whether
  the author meant to set something or just did not trust fall-through.

**Why `notice` and not `status`?** `"status"` already means the outcome (`denied` vs
`approved`). Mixing a warning sentence into a field called `status` confuses readers and
API consumers. **`notice`** holds optional context; **`status`** stays the verdict.

### Disclaimer — the same `order_id`, two different lookups

Notice both lines take **`order_id`**, but the function names are not interchangeable:

```python
customer = get_customer_by_order_id(order_id)   # find the customer *via* the order
order = get_order(order_id)                     # find the order row itself
```

That is not a Python quirk — it mirrors how a **relational database** stores data. An **order**
row and a **customer** row are separate tables. Each row has its own **primary key** (its ID).
The order row also carries a **foreign key** — usually something like `customer_id` — that
*points at* which customer placed it.

So when you pass `order_id` into `get_order`, the database looks up one table: *"give me the
order with this ID."* When you pass the **same** `order_id` into `get_customer_by_order_id`,
the code (or SQL join under the hood) does something different: *"find the order, read its
`customer_id`, then fetch that customer."* Same string in your Python function — two different
relationships in the data.

**Do not read `get_customer(order_id)` and `get_customer_by_order_id(order_id)` as the same
call.** The first name is misleading unless `order_id` literally *is* the customer's primary
key (it usually is not). The second name tells the truth: you are resolving a customer **through**
an order link.

> **Disclaimer — `customer["balance"]` assumes a dict.** In the third block we wrote
> `customer["balance"]` and `order["total"]`. Bracket syntax means `customer` is a **dict** —
> the JSON-shaped data from Module 2. In production code, `get_customer_by_order_id` is more
> likely to return an **object** (a `@dataclass`, database row, or Pydantic model). You then
> read fields with **dot notation**: `customer.balance`, `order.total`. Same customer, same
> balance — two ways to access it. We use dicts in these early examples because tool results and
> API payloads arrive as JSON dicts first. **Object access is covered in Module 5 (OOP /
> dataclasses) and Module 8 (schema contracts).** When you see dots instead of brackets in
> Skilljar, that is usually why.

You do not need SQL yet — just recognize the pattern when you see IDs in Skilljar or our
advertising system code. Full explanation (foreign keys, joins, dataclass rows):
**Module 2 — [Relational IDs](02_DICTIONARIES_LISTS_JSON.md#relational-ids)**.

**AI systems angle:** tool handlers are functions. Indentation tells you what runs *inside* the
tool vs. what runs in the caller. Early `return` from an error branch is how tools bail out
without running the happy path — but branches that only *enrich* the response (like `notice`)
should fall through to one shared success `return`, not duplicate it.

## Variables and basic types

Python is **imperative**: the interpreter runs your file **line by line, top to bottom** (modulo
functions, which run when called). A variable is not a labeled box you declare upfront — it is
a **name** that gets bound to a **value** the moment that assignment line **actually runs**.

```python
count = 3           # right now, count refers to an int
price = 19.99       # float
title = "Breakthrough Copy"   # str
active = True       # bool
missing = None      # None — "no value yet"
```

**The type lives on the value, not on the name.** Python figures out `int`, `str`, etc. from
what is on the right side of `=`. The name `count` does not "stay an int forever" — if a later
line ran `count = "three"`, that would be legal; `count` would now refer to a string. (You
will see **type hints** like `count: int = 3` in Skilljar code — those document intent for
humans and tools; Module 3 covers them. They do not stop this reassignment at runtime.)

Because types are decided **at execution time**, a mistake may not show up until a line runs:

```python
count = 3
title = count + "times"    # 💥 TypeError when this line runs
```

`count` is an `int`. `"times"` is a `str`. Python will not silently mash them together — there
is no automatic conversion. **`+` means "add numbers" or "join strings," not both.** When the
interpreter hits this line, it raises **`TypeError`** and stops.

**How to reconcile it** — convert explicitly so both sides agree:

```python
count = 3
title = str(count) + " times"           # "3 times"
title = f"{count} times"                # same result — f-string (Module 3)
title = "{} times".format(count)        # older style — still common in the wild
```

You are telling Python: *treat the number as text before joining.* That is the imperative
pattern — **do the conversion on the line where you need it**, not in a separate declaration.

### More examples — read what each line *does* at runtime

**Strings that look like numbers are still strings:**

```python
order_id = "12345"
campaign_id = 12345
order_id + campaign_id    # 💥 TypeError — str + int
int(order_id) + campaign_id   # 24690 — parse the string first
```

**Division is not always "math class" division:**

```python
7 / 2    # 3.5  — true division, always float
7 // 2   # 3    — floor division, whole units
```

**Truthiness — not everything is compared with `== True`:**

```python
notice = ""
if notice:
    print("has text")    # skipped — empty string is "falsy"
if balance:
    ...                  # 0 is falsy; negative numbers are truthy
```

**A name only exists after its line runs:**

```python
if balance < order_price:
    shortfall = order_price - balance
return shortfall   # 💥 NameError if the if branch never ran — shortfall was never assigned
```

That last one is scope *and* imperative flow: the variable is not "declared" in the function —
it appears only if execution passes through the line that creates it.

**AI systems angle:** tool inputs arrive as JSON — numbers often show up as **strings**
(`"top_k": "5"`). Code that assumes an `int` and does math without converting looks fine until
a real request hits it. When you read handlers, ask: *what type is this value **at this line**?*

```python
# one-line comment — humans only

def advertising_knowledge(query: str) -> dict:
    """Return a cited briefing from the 10-book library."""
    ...
```

**Exam tip:** docstrings are how Claude learns what a tool *does*. You'll own this in Module 3.

## Exercise — read aloud

From the exam pattern (refund scenario), narrate each line. Then open
`code/rag/advertising_knowledge.py` and read the top-level function signature only — don't
run it yet.

## REPL — Read–Eval–Print Loop

The **REPL** is Python's interactive mode: you type one line, Python runs it **immediately**,
prints the result, and waits for the next line. No file to save, no script to run — a sandbox
for trying syntax before Module 2.

### Requirements

From the tutorial folder, with your **named venv activated** (Module 00):

```bash
python -m venv aja-cca-f
source aja-cca-f/bin/activate     # WSL / Linux / macOS
# aja-cca-f\Scripts\activate      # Windows

pip install -r requirements.txt   # once per venv
cd random/advertising_system_tutorial   # or your path to this repo
python                            # start the REPL — no filename after python
```

You need **Python 3.10+** on your PATH. The prompt should show your venv name, e.g.
`(aja-cca-f) $` — same idea as `(foundation)` in the example below.

### How to exit

| Platform | Action |
|----------|--------|
| Any | Type `exit()` or `quit()` and press Enter |
| Linux / macOS / WSL | **Ctrl+D** (EOF — end of input) |
| Windows | **Ctrl+Z** then Enter |

Until you exit, Python keeps your variables — the session is **stateful** across lines.

### Interactive — more than one line

The REPL is not a one-liner demo. Each `>>>` prompt is one statement; **names you assign
stay in memory** for the next line. That is how you build up dicts and test bracket access
before Module 2:

```
(foundation) debian-dylan@magnifying-ocean:.../advertising_system_tutorial$ python
Python 3.11.2 (main, ...) [GCC 12.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> hammer = {"category": "tool", "uses": ["insert nail", "pull nail"]}
>>> hammer["uses"]
['insert nail', 'pull nail']
>>> hammer["materials"] = ["wood", "steel"]
>>> hammer
{'category': 'tool', 'uses': ['insert nail', 'pull nail'], 'materials': ['wood', 'steel']}
>>> exit()
```

Read what happened:

1. **`hammer = {...}`** — bind a dict to the name `hammer` (Module 2 JSON shape).
2. **`hammer["uses"]`** — bracket lookup on a key; REPL prints the list.
3. **`hammer["materials"] = [...]`** — add a new key to the **same** dict in memory.
4. **`hammer`** — typing a name alone prints its current value — now three keys.
5. **`exit()`** — leave the REPL; `hammer` is gone when you start `python` again.

Same pattern with a book from our running example:

```
>>> {"book": "Audience First"}["book"]
'Audience First'
```

Use the REPL to poke at dicts, lists, and `2 + 2` before Module 2. If you get
`TypeError` on `count + "times"`, try the fix from the variables section — that is the REPL
doing its job.
