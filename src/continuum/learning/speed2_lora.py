"""Geschwindigkeit 2 — Faehigkeitsaufbau (LoRA-Adapter, taeglich-woechentlich).

Siehe ARCHITECTURE.md, Abschnitt 2, und Konzeptpapier Kapitel 5.3.

STATUS: Absichtlich NICHT implementiert in Phase 0 — siehe CLAUDE.md,
Prinzip 4 (Phasendisziplin), und TASKS.md, Block F2. Dieses Modul definiert
das Interface, das eine spaetere Phase-2-Implementierung erfuellen muss,
mit den konkret vorgesehenen Techniken:

- LoRA-Adapter (~0.1-1% der Parameterzahl) via PEFT/transformers
- Contextual Experience Replay (CER): Training auf zusammengefassten,
  realen Erfahrungssequenzen aus memory.episodic
- Orthogonal Subspace Learning (O-LoRA): neue Adapter fuer Teildomaenen
  werden orthogonal zu bestehenden Adapter-Gradientenrichtungen trainiert,
  um gegenseitiges Ueberschreiben zu verhindern

Bevor dieses Modul implementiert wird, muessen die Go/No-Go-Kriterien aus
ROADMAP.md fuer Phase 0 erfuellt sein UND ein GPU-faehiges Trainings-Setup
vorhanden sein (siehe pyproject.toml, optionale Abhaengigkeit "phase2").
"""

from __future__ import annotations

from continuum.memory.store import MemoryStore


class Speed2LoRALearner:
    """Interface fuer das woechentliche Adapter-Training.

    TODO(Phase 2): Implementieren mit `peft.LoraConfig` + O-LoRA-
    Orthogonalitaetsbeschraenkung. Trainingsdaten kommen aus
    `memory.episodic.EpisodicMemory.recall_similar` (CER-Muster: nur
    validierte, zusammengefasste Erfahrungssequenzen, kein rohes Replay
    ganzer Rohdaten aus Datenschutzgruenden — siehe Konzeptpapier,
    Tradeoff-Tabelle in Kapitel 5.3).
    """

    def __init__(self, base_model_ref: str, memory_store: MemoryStore) -> None:
        self._base_model_ref = base_model_ref
        self._memory_store = memory_store

    def train_adapter(self, domain_tag: str) -> None:
        raise NotImplementedError(
            "Speed2LoRALearner.train_adapter ist fuer Phase 2 vorgesehen. "
            "Siehe ARCHITECTURE.md Abschnitt 2 und TASKS.md Block F2. "
            "Nicht in Phase 0 implementieren (CLAUDE.md, Phasendisziplin)."
        )
