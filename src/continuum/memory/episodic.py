"""Episodisches Gedaechtnis: konkrete, zeitgestempelte Experimentereignisse.

Siehe ARCHITECTURE.md, Abschnitt 1.
"""

from __future__ import annotations

import json

from continuum.memory.models import EpisodicEvent, MemoryKind, MemoryRecord
from continuum.memory.store import MemoryStore


class EpisodicMemory:
    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    def record_event(self, event: EpisodicEvent, source: str = "lab") -> MemoryRecord:
        """Schreibt ein Experimentereignis als neuen (unvalidierten) Record.

        Landet zunaechst im "heissen" Puffer — siehe consolidation.py.
        """
        text = (
            f"{event.description} | Parameter: {json.dumps(event.parameters)} "
            f"| Ergebnis: {json.dumps(event.outcome)}"
        )
        record = MemoryRecord(
            text=text,
            kind=MemoryKind.EPISODIC,
            source=source,
            importance=0.5,
            tags=("episode", event.id),
            validated=False,
        )
        return self._store.write(record)

    def recall_similar(self, query: str, k: int = 5, validated_only: bool = True):
        return self._store.search(query, k=k, kind=MemoryKind.EPISODIC, validated_only=validated_only)
