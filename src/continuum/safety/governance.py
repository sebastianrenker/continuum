"""Governance gate + audit log.

See ARCHITECTURE.md, section 7, and CLAUDE.md, principles 2+3.
Enforces in phase 0, for every (simulated) experiment above a
cost threshold, an explicit approval decision AND logs
every security-relevant event. This pattern is deliberately implemented
correctly already in phase 0, so that it does not have to be retrofitted
in phase 1 (real hardware) — see CLAUDE.md, principle 2.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class ApprovalDecision:
    experiment_id: str
    approved: bool
    reason: str
    auto_approved: bool


class GovernanceGate:
    def __init__(self, audit_log_path: str | Path = "audit.log", cost_threshold: float = 10.0) -> None:
        self._audit_log_path = Path(audit_log_path)
        self._cost_threshold = cost_threshold

    def request_approval(
        self,
        experiment_id: str,
        estimated_cost: float,
        hazard_blocked: bool,
        human_override: bool | None = None,
    ) -> ApprovalDecision:
        """Decides on the approval of a (simulated) experiment.

        Rules (see CLAUDE.md, principle 2 — safety before speed):
        - With `hazard_blocked=True` it is ALWAYS rejected, independent of
          `human_override`.
        - Below the cost threshold it is approved automatically.
        - Above the threshold `human_override` is required (in
          phase 0 simulated by the caller, in a later phase a
          real human approval step).
        """
        if hazard_blocked:
            decision = ApprovalDecision(experiment_id, False, "hazard screening blocked it", False)
        elif estimated_cost <= self._cost_threshold:
            decision = ApprovalDecision(experiment_id, True, "below the cost threshold, approved automatically", True)
        elif human_override is True:
            decision = ApprovalDecision(experiment_id, True, "manual approval above the cost threshold", False)
        else:
            decision = ApprovalDecision(
                experiment_id, False, "above the cost threshold, no manual approval present", False
            )

        self.audit_log({"event": "approval_decision", **asdict(decision), "estimated_cost": estimated_cost})
        return decision

    def audit_log(self, event: dict) -> None:
        """Writes an event as a JSON line into the audit log. See CLAUDE.md, principle 3."""
        entry = {"timestamp": time.time(), **event}
        with self._audit_log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, default=str) + "\n")

    def read_audit_log(self) -> list[dict]:
        if not self._audit_log_path.exists():
            return []
        with self._audit_log_path.open("r", encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]
