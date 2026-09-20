"""Semantic memory: knowledge abstracted and decontextualized from episodes.

See ARCHITECTURE.md, section 1. Phase 0: rule-based aggregation
(a frequency threshold). A later phase can replace this with LLM-supported
summarization (via `LLMClient`) without changing the interface.
"""

from __future__ import annotations

from collections import Counter

from continuum.memory.models import MemoryKind, MemoryRecord, SemanticFact
from continuum.memory.store import MemoryStore

_MIN_SUPPORT = 3  # the minimum number of matching episodes for an abstraction


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
            validated=True,  # semantic facts arise only after validation of the episodes
        )
        return self._store.write(record)

    def recall(self, query: str, k: int = 5):
        return self._store.search(query, k=k, kind=MemoryKind.SEMANTIC, validated_only=True)

    def abstract_from_tags(self, tag_texts: list[str]) -> SemanticFact | None:
        """A very simple rule-based abstraction (phase 0).

        Counts frequent phrasings in a list of episode texts and
        produces a SemanticFact if a phrasing occurs more often than
        `_MIN_SUPPORT`. No substitute for real NLU — deliberately simple,
        see the docstring header.
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
