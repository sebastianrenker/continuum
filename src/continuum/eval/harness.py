"""Evaluation harness: runs the full four-level stack.

See ARCHITECTURE.md, section 8. The basis for the go/no-go
decision at the end of each roadmap phase (see ROADMAP.md).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from continuum.eval.metrics import (
    CalibrationReport,
    EfficiencyReport,
    GovernanceReport,
    MemoryQualityReport,
    TaskEffectivenessReport,
    calibration_curve,
    efficiency,
    governance_compliance,
    memory_quality,
    task_effectiveness,
)


@dataclass
class FullEvalReport:
    task: TaskEffectivenessReport
    memory: MemoryQualityReport
    cost: EfficiencyReport
    governance: GovernanceReport
    calibration: CalibrationReport


def run_full_eval(
    hypothesis_records: list[dict],
    retrieved_ids: list[str],
    relevant_ids: list[str],
    run_log: list[dict],
    audit_events: list[dict],
    predictions: list[tuple[float, float]],
    outcomes: list[float],
) -> FullEvalReport:
    return FullEvalReport(
        task=task_effectiveness(hypothesis_records),
        memory=memory_quality(retrieved_ids, relevant_ids),
        cost=efficiency(run_log),
        governance=governance_compliance(audit_events),
        calibration=calibration_curve(predictions, outcomes),
    )


def write_report(report: FullEvalReport, path: str | Path = "eval_report.json") -> None:
    data = {
        "task": asdict(report.task),
        "memory": asdict(report.memory),
        "cost": asdict(report.cost),
        "governance": asdict(report.governance),
        "calibration": asdict(report.calibration),
    }
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def format_report(report: FullEvalReport) -> str:
    lines = [
        "=== CONTINUUM Eval Report ===",
        (
            f"Level 1 (task success):  {report.task.n_confirmed}/{report.task.n_hypotheses_tested} "
            f"confirmed (hit_rate={report.task.hit_rate:.2f})"
        ),
        f"Level 2 (memory):        precision@k={report.memory.precision_at_k:.2f}",
        (
            f"Level 3 (efficiency):    cost/validated hypothesis="
            f"{report.cost.cost_per_validated_hypothesis:.2f}, "
            f"mean latency={report.cost.mean_latency_ms:.1f}ms"
        ),
        (
            f"Level 4 (governance):    {report.governance.total_events} events, "
            f"coverage={report.governance.audit_coverage:.2%}"
        ),
        (
            f"Calibration:             MAE={report.calibration.mean_absolute_error:.4f}, "
            f"within uncertainty band={report.calibration.within_uncertainty_band_fraction:.2%}"
        ),
    ]
    return "\n".join(lines)
