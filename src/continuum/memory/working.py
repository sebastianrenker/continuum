"""Arbeitsgedaechtnis: kapazitaetsbegrenzter Kontext der laufenden Aufgabe.

Siehe ARCHITECTURE.md, Abschnitt 1. Bewusst NICHT im MemoryStore persistiert
— das Arbeitsgedaechtnis ist fluechtig per Definition (vgl. CLAUDE.md,
Prinzip 5: "lange Kontextfenster sind kein Gedaechtnis"). Was ueberdauern
soll, muss explizit ins episodische Gedaechtnis geschrieben werden.
"""

from __future__ import annotations

from collections import deque


class WorkingMemory:
    """LRU-artiger Kurzzeitpuffer fuer die aktuell laufende Aufgabe."""

    def __init__(self, capacity: int = 20) -> None:
        self._capacity = capacity
        self._buffer: deque[str] = deque(maxlen=capacity)

    def add(self, item: str) -> None:
        self._buffer.append(item)

    def snapshot(self) -> list[str]:
        return list(self._buffer)

    def clear(self) -> None:
        self._buffer.clear()

    def __len__(self) -> int:
        return len(self._buffer)
