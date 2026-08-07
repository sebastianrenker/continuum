"""Herkunftskennzeichnung fuer jede Aussage des Systems.

Siehe ARCHITECTURE.md, Abschnitt 6, und Konzeptpapier Kapitel 5.6:
"keine unbelegte Behauptung". Jede Aussage traegt genau eine der drei
Kategorien in `Evidence`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Evidence(str, Enum):
    EXPERIMENTAL = "experimental"  # direkte Messung, mit Verweis auf Reproduzierbarkeit
    PREDICTED = "predicted"        # Modellvorhersage MIT kalibrierter Unsicherheit
    LITERATURE = "literature"      # Zitat mit Quellenangabe


@dataclass
class Claim:
    """Eine einzelne, ueberpruefbare Aussage des Systems."""

    text: str
    evidence_kind: Evidence
    confidence: float  # in [0, 1]; bei EXPERIMENTAL i. d. R. nahe 1.0
    source_ref: str  # Record-ID im MemoryStore, Zitat-Key oder Modell-Run-ID

    def __post_init__(self) -> None:
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence muss in [0, 1] liegen, war {self.confidence}")
        if not self.source_ref:
            raise ValueError("source_ref darf nicht leer sein — jede Aussage braucht einen Beleg.")
