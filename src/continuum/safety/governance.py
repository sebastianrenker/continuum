"""Governance-Gate + Audit-Log.

Siehe ARCHITECTURE.md, Abschnitt 7, und CLAUDE.md, Prinzipien 2+3.
Erzwingt in Phase 0 fuer jedes (simulierte) Experiment oberhalb eines
Kostenschwellenwerts eine explizite Freigabe-Entscheidung UND protokolliert
jedes sicherheitsrelevante Ereignis. Dieses Muster wird bewusst schon in
Phase 0 korrekt implementiert, damit es in Phase 1 (echte Hardware) nicht
nachgeruestet werden muss — siehe CLAUDE.md, Prinzip 2.
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
        """Entscheidet ueber die Freigabe eines (simulierten) Experiments.

        Regeln (siehe CLAUDE.md, Prinzip 2 — Sicherheit vor Geschwindigkeit):
        - Bei `hazard_blocked=True` wird IMMER abgelehnt, unabhaengig von
          `human_override`.
        - Unterhalb der Kostenschwelle wird automatisch genehmigt.
        - Oberhalb der Schwelle ist `human_override` erforderlich (in
          Phase 0 durch den Aufrufer simuliert, in einer spaeteren Phase ein
          echter menschlicher Freigabeschritt).
        """
        if hazard_blocked:
            decision = ApprovalDecision(experiment_id, False, "Gefahrstoff-Screening hat blockiert", False)
        elif estimated_cost <= self._cost_threshold:
            decision = ApprovalDecision(experiment_id, True, "unterhalb Kostenschwelle, automatisch genehmigt", True)
        elif human_override is True:
            decision = ApprovalDecision(experiment_id, True, "manuelle Freigabe oberhalb Kostenschwelle", False)
        else:
            decision = ApprovalDecision(
                experiment_id, False, "oberhalb Kostenschwelle, keine manuelle Freigabe vorhanden", False
            )

        self.audit_log({"event": "approval_decision", **asdict(decision), "estimated_cost": estimated_cost})
        return decision

    def audit_log(self, event: dict) -> None:
        """Schreibt ein Ereignis als JSON-Zeile ins Audit-Log. Siehe CLAUDE.md, Prinzip 3."""
        entry = {"timestamp": time.time(), **event}
        with self._audit_log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, default=str) + "\n")

    def read_audit_log(self) -> list[dict]:
        if not self._audit_log_path.exists():
            return []
        with self._audit_log_path.open("r", encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]
