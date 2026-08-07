"""Semantisches Gedaechtnis: aus Episoden abstrahiertes, dekontextualisiertes Wissen.

Siehe ARCHITECTURE.md, Abschnitt 1. Phase 0: regelbasierte Aggregation
(Haeufigkeitsschwelle). Eine spaetere Phase kann dies durch LLM-gestuetzte
Zusammenfassung ersetzen (via `LLMClient`), ohne die Schnittstelle zu aendern.
"""

from __future__ import annotations

from collections import Counter

from continuum.memory.models import MemoryKind, MemoryRecord, SemanticFact
from continuum.memory.store import MemoryStore

_MIN_SUPPORT = 3  # Mindestanzahl uebereinstimmender Episoden fuer eine Abstraktion


class SemanticMemory:
    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    def write_fact(self, fact: SemanticFact, source: str = "consolidation") -> MemoryRecord:
        record = MemoryRecord(
            text=fact.statement,
            kind=MemoryKind.SEMANTIC,
            source=source,
            importance=min(1.0, fact.confidence),
            tags=("semantic", *fact.supporting_episode_ids),
            validated=True,  # semantische Fakten entstehen erst nach Validierung der Episoden
        )
        return self._store.write(record)

    def recall(self, query: str, k: int = 5):
        return self._store.search(query, k=k, kind=MemoryKind.SEMANTIC, validated_only=True)

    def abstract_from_tags(self, tag_texts: list[str]) -> SemanticFact | None:
        """Sehr einfache regelbasierte Abstraktion (Phase 0).

        Zaehlt haeufige Formulierungen in einer Liste von Episoden-Texten und
        erzeugt einen SemanticFact, wenn eine Formulierung oefter als
        `_MIN_SUPPORT` vorkommt. Kein Ersatz fuer echte NLU — bewusst simpel,
        siehe Docstring-Kopf.
        """
        counter = Counter(tag_texts)
        if not counter:
            return None
        statement, count = counter.most_common(1)[0]
        if count < _MIN_SUPPORT:
            return None
        confidence = min(1.0, count / max(len(tag_texts), 1))
        return SemanticFact(
            statement=statement,
            confidence=confidence,
            supporting_episode_ids=(),
        )
