# 05 · Decorators, OOP, and Pydantic

> **Abstract.** Classes, decorators, and schema libraries — recognize and write the patterns in
> MCP servers and structured output. **OOP is necessary** for reading real codebases; Pydantic
> and `@dataclass` (Module 2) are how Python defines API/DB contracts.

**Time:** ~75 min

---

## OOP — classes hold state and behavior

You don't need deep inheritance hierarchies. You **do** need to read (and write simple) classes:

```python
from dataclasses import dataclass

@dataclass
class KnowledgeEntry:
    label: str
    alpha: float = 2.0
    beta: float = 2.0

    @property
    def weight(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    def update(self, success: bool) -> None:
        if success:
            self.alpha += 1
        else:
            self.beta += 1
```

An **object** is a dict with named fields *and* methods attached. Module 8 uses six such
classes as database contracts.

## Imports

Every file starts with imports — they load libraries:

```python
import json
from pathlib import Path
from anthropic import Anthropic
```

**AI angle:** `from anthropic import Anthropic` is the client you'll use in Module 6.

## Decorators

```python
@something
def my_function():
    ...
```

Means: "wrap `my_function` with extra behavior." You don't need to write decorators — recognize
them.

## MCP pattern

Module 3 walks the full server: `code/mcp/server.py`. Here is the decorator you need to
**recognize** — `@mcp.tool()` registers a function as an MCP tool:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("advertising-knowledge")

@mcp.tool()
def advertising_knowledge(query: str) -> dict:
    """Search the 10-book library; return cited briefing."""
    ...
```

`@mcp.tool()` = **register this function as a tool Claude can call.** (Module 3 explains how
this connects to imports and `mcp.run()`.)

## Pydantic — JSON schema without hand-writing JSON

```python
from pydantic import BaseModel, Field

class AdBriefingRequest(BaseModel):
    query: str = Field(description="Question about advertising strategy or compliance")
    top_k: int = Field(default=5, ge=1, le=20)
```

Same information as a JSON Schema, less error-prone. Domain 4.3–4.4 (structured output,
validation loops).

## Side-by-side exercise

Left: hand-written JSON Schema for `AdBriefingRequest`. Right: Pydantic model above. Same
result, different effort.

## What we skip

Writing custom decorators from scratch, async MCP internals, Generic types, metaclasses.

## Bridge to Modules 7–8

- Module 7: TartaurusLoop `VALIDATE` phase checks briefing shape.
- Module 8: six `@dataclass` schemas for the Bayesian score-keeping loop.
