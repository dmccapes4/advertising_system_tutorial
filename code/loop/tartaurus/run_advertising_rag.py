#!/usr/bin/env python3
"""Run the 10-book RAG pipeline via TartaurusLoop (Anthropic SDK variant).

  python run_advertising_rag.py --dry-run
  python run_advertising_rag.py --query "retention email after purchase"
  python run_advertising_rag.py --query "..." --llm-polish   # optional Anthropic polish
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tartaurus_loop import TartaurusLoopAnthropic

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from env_loader import load_env
load_env()

HERE = Path(__file__).resolve().parent
DEFAULT_SPEC = HERE / "advertising_rag_spec.json"
DEFAULT_OUT = HERE / "output"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--query", default="fair use in social ad headlines")
    p.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    p.add_argument("--output", type=Path, default=DEFAULT_OUT)
    p.add_argument("--dry-run", action="store_true", help="RAG stages only, no Anthropic API")
    p.add_argument("--llm-polish", action="store_true", help="Optional LLM polish on briefing")
    p.add_argument("--model", default="claude-sonnet-4-20250514")
    args = p.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    client = None
    if args.llm_polish and not args.dry_run:
        try:
            from anthropic import Anthropic
            client = Anthropic()
        except ImportError:
            raise SystemExit("pip install anthropic")

    loop = TartaurusLoopAnthropic(
        spec=spec,
        output_dir=args.output,
        query=args.query,
        client=client,
        model=args.model,
        use_llm_synth=args.llm_polish,
    )
    ctx = loop.run()
    print("\n" + "=" * 60)
    print(ctx.get("briefing", ""))
    print("=" * 60)
    print(f"\nArtifacts: {args.output}/checklist.json, session_log.json, result.json")


if __name__ == "__main__":
    main()
