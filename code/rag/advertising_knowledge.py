"""10-book advertising knowledge tool — staged reduction (tutorial corpus).

Pure Python; no API keys. Used by Modules 3, 6, 7 and anthropic_agent_loop.py.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGES = json.loads((HERE / "mock_pages.json").read_text(encoding="utf-8"))
LIBRARY = json.loads((HERE / "library_dictionary.json").read_text(encoding="utf-8"))


def route(query: str) -> list[str]:
    """Stage 1: pick books whose strengths overlap query words."""
    words = set(query.lower().split())
    chosen = []
    for book, meta in LIBRARY.items():
        topics = set(t.lower() for t in meta["strengths"])
        if words & topics:
            chosen.append(book)
    return chosen or list(LIBRARY.keys())[:3]


def probe(book: str, query: str, top_k: int = 2) -> list[dict]:
    """Stage 2: simple keyword overlap ranking (stand-in for BM25 + ANN)."""
    q = set(query.lower().split())
    scored = []
    for p in PAGES:
        if p["book"] != book:
            continue
        pt = set(t.lower() for t in p["topics"]) | set(p["text"].lower().split())
        score = len(q & pt)
        if score > 0:
            scored.append((score, p))
    scored.sort(key=lambda x: -x[0])
    return [p for _, p in scored[:top_k]]


def gap(book: str, found: list[dict], query: str) -> list[dict]:
    """Stage 3: if a query word isn't covered, fetch one more page for it."""
    covered = set()
    for p in found:
        covered |= set(t.lower() for t in p["topics"])
    extra = []
    for word in query.lower().split():
        if word in covered:
            continue
        for p in PAGES:
            if p["book"] == book and word in p["text"].lower() and p not in found:
                extra.append(p)
                covered.add(word)
                break
    return extra


def synthesize(passages: list[dict]) -> str:
    """Stage 4: short cited briefing."""
    if not passages:
        return "No relevant passages found in the selected books."
    lines = ["Advertising knowledge briefing (cited):", ""]
    for p in passages:
        cite = f"{p['book']} p.{p['page']}"
        lines.append(f"- [{cite}] {p['text']}")
    return "\n".join(lines)


def advertising_knowledge(query: str, top_k: int = 2) -> dict:
    """One tool, one job — MCP surface for the 10-book library."""
    books = route(query)
    all_passages: list[dict] = []
    trace = []
    for book in books:
        found = probe(book, query, top_k=top_k)
        extra = gap(book, found, query)
        merged = found + [p for p in extra if p not in found]
        all_passages.extend(merged)
        trace.append({"book": book, "found": len(found), "gap_added": len(extra)})
    # de-dupe by book+page
    seen = set()
    unique = []
    for p in all_passages:
        key = (p["book"], p["page"])
        if key not in seen:
            seen.add(key)
            unique.append(p)
    briefing = synthesize(unique)
    return {
        "query": query,
        "books_consulted": books,
        "citations": [{"book": p["book"], "page": p["page"]} for p in unique],
        "briefing": briefing,
        "trace": trace,
    }


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "copyright fair use ad headlines"
    result = advertising_knowledge(q)
    print(result["briefing"])
