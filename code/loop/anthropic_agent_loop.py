#!/usr/bin/env python3
"""Minimal Anthropic agent loop — Module 4 teaching example.

One tool: advertising_knowledge (10-book RAG). Use --dry-run to exercise without API key.

  python anthropic_agent_loop.py --dry-run
  python anthropic_agent_loop.py --query "fair use in headlines"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Load .env from tutorial root (optional; export still works)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from env_loader import load_env
load_env()

# Allow import from sibling rag package
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "rag"))
from advertising_knowledge import advertising_knowledge  # noqa: E402

TOOLS = [{
    "name": "advertising_knowledge",
    "description": (
        "Search the company's 10-book advertising library. Returns a short cited briefing — "
        "not full book text. Use for: ad copy, compliance, retention, offers, audience strategy."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The advertising question to answer"},
        },
        "required": ["query"],
    },
}]


def execute_tool(name: str, tool_input: dict) -> str:
    if name == "advertising_knowledge":
        result = advertising_knowledge(tool_input["query"])
        return json.dumps(result, indent=2)
    return json.dumps({"error": f"unknown tool {name}"})


def run_dry_run(query: str) -> None:
    """No API — show what the loop would do on first tool call."""
    print("=== DRY RUN (no Anthropic API) ===")
    print(f"User: {query}\n")
    print("Assistant would call tool: advertising_knowledge")
    result = advertising_knowledge(query)
    print("\nTool result (truncated briefing):\n")
    print(result["briefing"][:800])
    print(f"\nBooks consulted: {result['books_consulted']}")


def run_live(query: str, model: str, max_iterations: int) -> None:
    try:
        from anthropic import Anthropic
    except ImportError:
        print("pip install anthropic")
        sys.exit(1)

    client = Anthropic()
    messages = [{"role": "user", "content": query}]
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=messages,
        tools=TOOLS,
    )

    iterations = 0
    while response.stop_reason == "tool_use":
        iterations += 1
        if iterations > max_iterations:
            raise RuntimeError(f"Exceeded max_iterations={max_iterations}")

        tool_results = []
        assistant_content = []
        for block in response.content:
            if block.type == "text":
                assistant_content.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                assistant_content.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })
                output = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output,
                })

        messages.append({"role": "assistant", "content": assistant_content})
        messages.append({"role": "user", "content": tool_results})

        response = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=messages,
            tools=TOOLS,
        )

    # Final text
    for block in response.content:
        if hasattr(block, "text"):
            print(block.text)


def main():
    p = argparse.ArgumentParser(description="Anthropic agent loop — advertising_knowledge tool")
    p.add_argument("--query", default="What does our library say about fair use in ad headlines?")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--model", default="claude-sonnet-4-20250514")
    p.add_argument("--max-iterations", type=int, default=10)
    args = p.parse_args()

    if args.dry_run:
        run_dry_run(args.query)
    else:
        run_live(args.query, args.model, args.max_iterations)


if __name__ == "__main__":
    main()
