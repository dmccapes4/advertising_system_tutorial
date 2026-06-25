#!/usr/bin/env python3
"""
TartaurusLoop (Anthropic SDK) — tutorial slim variant.

Lineage: PortalVision/distributions/tartaurus_loop_package/tartaurus_loop.py
Adapted for Anthropic Messages API + the 10-book advertising RAG stages.

Phases per stage:
  SPECIFY  — optional LLM polish (skipped in --rag-only mode)
  VALIDATE — deterministic checks on RAG output
  INTEGRATE— append to state_graph.json + checklist.json

The inner agentic loop (Module 4) lives in anthropic_agent_loop.py; this orchestrates
multi-stage pipelines with resumable checkpoints.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# RAG stages (pure Python)
RAG_ROOT = Path(__file__).resolve().parents[2] / "rag"
sys.path.insert(0, str(RAG_ROOT))
from advertising_knowledge import route, probe, gap, synthesize  # noqa: E402

VERSION = "tutorial-1.0.0"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path, default: Any) -> Any:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


class TartaurusLoopAnthropic:
    """Spec-driven stage runner with checklist + session log."""

    def __init__(
        self,
        spec: Dict[str, Any],
        output_dir: Path,
        query: str,
        client: Any = None,
        model: str = "claude-sonnet-4-20250514",
        use_llm_synth: bool = False,
    ):
        self.spec = spec
        self.output_dir = output_dir
        self.query = query
        self.client = client
        self.model = model
        self.use_llm_synth = use_llm_synth and client is not None
        self.checklist = load_json(output_dir / "checklist.json", {})
        self.state_graph = load_json(output_dir / "state_graph.json", {"nodes": {}, "edges": []})
        self.session: List[Dict[str, Any]] = load_json(output_dir / "session_log.json", [])
        self.run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.context: Dict[str, Any] = {"query": query, "passages": [], "books": []}

    def log(self, phase: str, stage_key: str, detail: str) -> None:
        entry = {"timestamp": _utc_now(), "phase": phase, "stage": stage_key, "detail": detail}
        self.session.append(entry)
        print(f"[{phase:8}] {stage_key}: {detail}")

    # ── Stage implementations (deterministic RAG) ─────────────────────────────

    def stage_route(self) -> None:
        books = route(self.query)
        self.context["books"] = books
        self.log("SPECIFY", "route", f"selected books: {books}")

    def stage_probe(self) -> None:
        passages = []
        for book in self.context["books"]:
            passages.extend(probe(book, self.query))
        self.context["passages"] = passages
        self.log("SPECIFY", "probe", f"{len(passages)} passages")

    def stage_gap(self) -> None:
        extra = []
        for book in self.context["books"]:
            found = [p for p in self.context["passages"] if p["book"] == book]
            extra.extend(gap(book, found, self.query))
        self.context["passages"].extend(extra)
        self.log("SPECIFY", "gap", f"+{len(extra)} gap passages")

    def stage_synthesize(self) -> None:
        briefing = synthesize(self.context["passages"])
        if self.use_llm_synth:
            briefing = self._llm_polish(briefing)
        self.context["briefing"] = briefing
        self.log("SPECIFY", "synthesize", f"{len(briefing)} chars")

    def _llm_polish(self, raw_briefing: str) -> str:
        """Optional Anthropic pass — Module 6 integration."""
        msg = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": (
                    f"Polish this advertising briefing for clarity. Keep all citations.\n\n{raw_briefing}"
                ),
            }],
        )
        return msg.content[0].text

    STAGE_FN = {
        "route": stage_route,
        "probe": stage_probe,
        "gap": stage_gap,
        "synthesize": stage_synthesize,
    }

    def validate(self, stage: Dict[str, Any]) -> Tuple[bool, str]:
        key = stage["stage_key"]
        rules = stage.get("validate", {})
        if key == "route" and rules.get("min_books"):
            if len(self.context.get("books", [])) < rules["min_books"]:
                return False, "no books selected"
        if key == "probe" and rules.get("min_passages"):
            if len(self.context.get("passages", [])) < rules["min_passages"]:
                return False, "no passages found"
        if key == "synthesize":
            if rules.get("require_citations") and not self.context.get("passages"):
                return False, "briefing has no citations"
            max_c = rules.get("max_briefing_chars")
            if max_c and len(self.context.get("briefing", "")) > max_c:
                return False, f"briefing exceeds {max_c} chars"
        return True, "ok"

    def integrate(self, stage: Dict[str, Any]) -> None:
        key = stage["stage_key"]
        node_id = f"{key}_{self.run_id}"
        self.state_graph["nodes"][node_id] = {
            "stage": key,
            "timestamp": _utc_now(),
            "summary": self.context.get("briefing", str(self.context.get("books", "")))[:200],
        }
        if len(self.state_graph["nodes"]) > 1:
            prev = list(self.state_graph["nodes"].keys())[-2]
            self.state_graph["edges"].append({"from": prev, "to": node_id, "type": "next_stage"})

    def run(self) -> Dict[str, Any]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"TartaurusLoop Anthropic {VERSION} — {self.spec.get('experiment_id')}")
        print(f"Query: {self.query}\n")

        for stage in self.spec.get("stages", []):
            key = stage["stage_key"]
            if self.checklist.get(key) == "done":
                self.log("SKIP", key, "already done")
                continue

            fn = self.STAGE_FN.get(key)
            if not fn:
                self.log("ERROR", key, "unknown stage")
                continue

            fn(self)
            ok, reason = self.validate(stage)
            if not ok:
                self.log("VALIDATE", key, f"FAIL — {reason}")
                save_json(self.output_dir / "session_log.json", self.session)
                raise RuntimeError(f"Validation failed at {key}: {reason}")

            self.log("VALIDATE", key, "PASS")
            self.integrate(stage)
            self.checklist[key] = "done"
            save_json(self.output_dir / "checklist.json", self.checklist)
            save_json(self.output_dir / "state_graph.json", self.state_graph)

        save_json(self.output_dir / "session_log.json", self.session)
        save_json(self.output_dir / "result.json", {
            "query": self.query,
            "books": self.context.get("books"),
            "citations": [{"book": p["book"], "page": p["page"]} for p in self.context.get("passages", [])],
            "briefing": self.context.get("briefing", ""),
        })
        return self.context
