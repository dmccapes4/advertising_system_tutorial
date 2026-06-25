"""Six-table Bayesian loop — dataclass contracts (Module 8).

Maps the legacy six-schema design to typed Python objects. JSON on the wire;
@dataclass in code. Score keeping = Beta-Bernoulli update on KnowledgeEntry.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class KnowledgeEntry:
    """A page-level claim/strategy from the ad_knowledge_graph."""
    label: str
    entry_type: str  # principle | strategy | tactic | claim
    source: str      # book + page
    id: Optional[int] = None
    status: str = "active"
    alpha: float = 2.0
    beta: float = 2.0
    reference_count: int = 0
    salience: float = 0.0

    @property
    def weight(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    def update(self, success: bool) -> None:
        if success:
            self.alpha += 1.0
        else:
            self.beta += 1.0


@dataclass
class Edge:
    src_id: int
    dst_id: int
    relation: str  # supports | contradicts | cites | relates
    weight: float = 1.0
    id: Optional[int] = None


@dataclass
class Decision:
    """Agent judgment call — the HYPOTHESIS after a curated briefing."""
    query: str
    summary: str
    agent: str
    campaign_id: str
    id: Optional[int] = None
    created_at: datetime = field(default_factory=_now)


@dataclass
class DecisionEntry:
    """Credit assignment: which entries informed this decision."""
    decision_id: int
    entry_id: int
    contribution_weight: float = 1.0


@dataclass
class FeedbackEvent:
    """Real-world outcome — the EVIDENCE."""
    metric_name: str  # ctr | cvr | roas
    metric_value: float
    baseline: float
    success: bool
    decision_id: Optional[int] = None
    sample_size: Optional[int] = None
    id: Optional[int] = None
    observed_at: datetime = field(default_factory=_now)

    @classmethod
    def from_metric(cls, decision_id: int, name: str, value: float, baseline: float) -> FeedbackEvent:
        return cls(
            decision_id=decision_id,
            metric_name=name,
            metric_value=value,
            baseline=baseline,
            success=value >= baseline,
        )


@dataclass
class BeliefLog:
    """Append-only provenance of every belief change."""
    entry_id: int
    event: str  # update | decay | orphan | evict
    decision_id: Optional[int] = None
    success: Optional[bool] = None
    alpha_before: float = 0.0
    alpha_after: float = 0.0
    beta_before: float = 0.0
    beta_after: float = 0.0
    weight_after: float = 0.0
    id: Optional[int] = None
    at: datetime = field(default_factory=_now)


def apply_feedback(
    entry: KnowledgeEntry,
    event: FeedbackEvent,
    decision_id: int,
) -> BeliefLog:
    """Score keeping: one settled outcome updates one entry; log the receipt."""
    ab, bb, wb = entry.alpha, entry.beta, entry.weight
    entry.update(event.success)
    log = BeliefLog(
        entry_id=entry.id or 0,
        decision_id=decision_id,
        event="update",
        success=event.success,
        alpha_before=ab,
        alpha_after=entry.alpha,
        beta_before=bb,
        beta_after=entry.beta,
        weight_after=entry.weight,
    )
    return log


def run_mini_loop() -> None:
    """Dry-run: briefing → decision → feedback → belief update."""
    entry = KnowledgeEntry(
        id=1,
        label="scarcity framing for limited offers",
        entry_type="strategy",
        source="Breakthrough Copy p.42",
    )
    decision = Decision(
        id=10,
        query="headline for limited drop",
        summary="Use scarcity framing",
        agent="campaign-agent",
        campaign_id="camp-001",
    )
    link = DecisionEntry(decision_id=10, entry_id=1, contribution_weight=1.0)
    feedback = FeedbackEvent.from_metric(10, "cvr", value=0.04, baseline=0.025)
    wb_before = entry.weight
    log = apply_feedback(entry, feedback, decision.id)

    print("=== Six-schema score-keeping loop (dry run) ===")
    print("Decision:", asdict(decision))
    print("DecisionEntry:", asdict(link))
    print("FeedbackEvent:", asdict(feedback))
    print(f"KnowledgeEntry weight: {wb_before:.3f} -> {entry.weight:.3f}")
    print("BeliefLog:", asdict(log))


if __name__ == "__main__":
    run_mini_loop()
