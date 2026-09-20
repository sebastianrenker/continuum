"""Four-level evaluation stack + domain-specific metrics.

See ARCHITECTURE.md, section 8, and the concept paper chapter 6.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TaskEffectivenessReport:
    """Level 1: task success."""

    n_hypotheses_tested: int
    n_confirmed: int

    @property
    def hit_rate(self) -> float:
        return self.n_confirmed / self.n_hypotheses_tested if self.n_hypotheses_tested else 0.0


@dataclass
class MemoryQualityReport:
    """Level 2: memory quality."""

    precision_at_k: float
    contradiction_rate: float


@dataclass
class EfficiencyReport:
    """Level 3: efficiency."""

    cost_per_validated_hypothesis: float
    mean_latency_ms: float


@dataclass
class GovernanceReport:
    """Level 4: governance."""

    total_events: int
    audit_coverage: float  # the fraction of events with complete mandatory fields


@dataclass
class CalibrationReport:
    """Domain-specific: prediction vs. actual material property."""

    mean_absolute_error: float
    within_uncertainty_band_fraction: float  # the fraction where |pred - actual| <= std


def task_effectiveness(records: list[dict]) -> TaskEffectivenessReport:
    """`records`: a list of {"tested": bool, "confirmed": bool}."""
    tested = [r for r in records if r.get("tested")]
    confirmed = [r for r in tested if r.get("confirmed")]
    return TaskEffectivenessReport(n_hypotheses_tested=len(tested), n_confirmed=len(confirmed))


def memory_quality(retrieved_ids: list[str], relevant_ids: list[str]) -> MemoryQualityReport:
    if not retrieved_ids:
        return MemoryQualityReport(precision_at_k=0.0, contradiction_rate=0.0)
    relevant_set = set(relevant_ids)
    hits = sum(1 for rid in retrieved_ids if rid in relevant_set)
    precision = hits / len(retrieved_ids)
    return MemoryQualityReport(precision_at_k=precision, contradiction_rate=0.0)


def efficiency(run_log: list[dict]) -> EfficiencyReport:
    """`run_log`: a list of {"cost": float, "latency_ms": float, "validated": bool}."""
    if not run_log:
        return EfficiencyReport(cost_per_validated_hypothesis=0.0, mean_latency_ms=0.0)
    total_cost = sum(r.get("cost", 0.0) for r in run_log)
    n_validated = sum(1 for r in run_log if r.get("validated"))
    mean_latency = sum(r.get("latency_ms", 0.0) for r in run_log) / len(run_log)
    cost_per_validated = total_cost / n_validated if n_validated else float("inf")
    return EfficiencyReport(cost_per_validated_hypothesis=cost_per_validated, mean_latency_ms=mean_latency)


def governance_compliance(audit_events: list[dict]) -> GovernanceReport:
    required_fields = {"timestamp", "event"}
    if not audit_events:
        return GovernanceReport(total_events=0, audit_coverage=1.0)
    complete = sum(1 for e in audit_events if required_fields.issubset(e.keys()))
    return GovernanceReport(total_events=len(audit_events), audit_coverage=complete / len(audit_events))


def calibration_curve(predictions: list[tuple[float, float]], outcomes: list[float]) -> CalibrationReport:
    """`predictions`: a list of (mean, std) per prediction; `outcomes`: the actual values."""
    if not predictions or len(predictions) != len(outcomes):
        return CalibrationReport(mean_absolute_error=float("nan"), within_uncertainty_band_fraction=0.0)
    errors = []
    within_band = 0
    for (mean, std), actual in zip(predictions, outcomes, strict=True):
        error = abs(mean - actual)
        errors.append(error)
        if error <= max(std, 1e-9):
            within_band += 1
    return CalibrationReport(
        mean_absolute_error=sum(errors) / len(errors),
        within_uncertainty_band_fraction=within_band / len(predictions),
    )


def forgetting_rate(pre_scores: list[float], post_scores: list[float]) -> float:
    """The fraction of capability loss on a reference task set.

    0.0 = no forgetting, 1.0 = complete loss. See the concept paper
    chapter 5.3/9: with EWC empirically about 0.0685 instead of 0.1262 without protection —
    this module measures the same metric for the own implementation.
    """
    if not pre_scores or len(pre_scores) != len(post_scores):
        return float("nan")
    pre_mean = sum(pre_scores) / len(pre_scores)
    post_mean = sum(post_scores) / len(post_scores)
    if pre_mean == 0:
        return float("nan")
    return max(0.0, (pre_mean - post_mean) / pre_mean)
