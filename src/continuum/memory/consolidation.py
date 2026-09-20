"""Two-buffer consolidation: a hot trial buffer -> validated long-term memory.

See ARCHITECTURE.md, section 1, and the concept paper chapter 5.2. New
records are by default `validated=False` (see memory/models.py) and
only become visible to `validated_only=True` searches after this check
(see memory/store.py::search).
"""

from __future__ import annotations

from dataclasses import dataclass

from continuum.memory.models import MemoryRecord
from continuum.memory.store import MemoryStore

_DUPLICATE_SIMILARITY_THRESHOLD = 0.98
_MIN_IMPORTANCE_FOR_PROMOTION = 0.2


@dataclass
class ConsolidationReport:
    promoted: list[str]
    rejected_duplicates: list[str]
    rejected_low_importance: list[str]


class Consolidator:
    """Checks records from the hot buffer and promotes valid entries.

    Usage:
        consolidator = Consolidator(store)
        report = consolidator.run_consolidation_pass()
    """

    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    def run_consolidation_pass(self) -> ConsolidationReport:
        candidates = self._pending_records()
        promoted: list[str] = []
        rejected_duplicates: list[str] = []
        rejected_low_importance: list[str] = []

        for record in candidates:
            if record.importance < _MIN_IMPORTANCE_FOR_PROMOTION:
                rejected_low_importance.append(record.id)
                continue
            if self._is_duplicate(record):
                rejected_duplicates.append(record.id)
                continue
            self._store.mark_validated(record.id)
            promoted.append(record.id)

        return ConsolidationReport(
            promoted=promoted,
            rejected_duplicates=rejected_duplicates,
            rejected_low_importance=rejected_low_importance,
        )

    def _pending_records(self) -> list[MemoryRecord]:
        # Phase-0 implementation: a simple scan over all unvalidated
        # records via a search with an empty query text is imprecise; instead
        # direct SQL access via a helper method would be cleaner,
        # but stays here deliberately on the public store API, to keep the
        # interface stable.
        results = self._store.search("", k=10_000, validated_only=False)
        return [rec for rec, _ in results if not rec.validated]

    def _is_duplicate(self, record: MemoryRecord) -> bool:
        similar = self._store.search(record.text, k=3, validated_only=True)
        for other, score in similar:
            if other.id != record.id and score >= _DUPLICATE_SIMILARITY_THRESHOLD:
                return True
        return False
