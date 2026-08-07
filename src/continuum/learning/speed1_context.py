"""Geschwindigkeit 1 — Sofortlernen (Token-Raum, kein Gradienten-Update).

Siehe ARCHITECTURE.md, Abschnitt 2, und Konzeptpapier Kapitel 5.3.
Letta/MemGPT-Stil: das System selbst entscheidet ueber Tool-Aufrufe, was
geschrieben, abgerufen oder vergessen wird. Diese drei Funktionen SIND die
"Tools", die einem Agenten (bzw. `hypothesis`-Agenten) zur Verfuegung
gestellt werden koennen.

Dies ist die einzige Lernkomponente, die in Phase 0 vollstaendig
funktionsfaehig sein muss — kein Training noetig, nur der MemoryStore.
"""

from __future__ import annotations

from continuum.memory.models import MemoryKind, MemoryRecord
from continuum.memory.store import MemoryStore


def remember(store: MemoryStore, text: str, *, source: str = "agent", importance: float = 0.5) -> MemoryRecord:
    """Schreibt eine neue Beobachtung ins (unvalidierte) Kern-Gedaechtnis.

    Landet zunaechst im heissen Puffer — siehe memory/consolidation.py fuer
    den Weg ins Langzeitgedaechtnis.
    """
    record = MemoryRecord(
        text=text,
        kind=MemoryKind.WORKING,
        source=source,
        importance=importance,
        tags=("speed1", "remember"),
        validated=False,
    )
    return store.write(record)


def recall(store: MemoryStore, query: str, k: int = 5) -> list[tuple[MemoryRecord, float]]:
    """Ruft die `k` relevantesten Records zu `query` ab, unabhaengig von der Schicht."""
    return store.search(query, k=k)


def forget(store: MemoryStore, record_id: str) -> None:
    """Entfernt einen Record explizit. Bewusst kein "stilles" Vergessen —
    jeder Aufruf sollte in einer spaeteren Phase auditiert werden (siehe
    safety/governance.py::audit_log), sobald `forget` aus einem
    Agenten-Kontext statt direkt aufgerufen wird."""
    store.delete(record_id)
