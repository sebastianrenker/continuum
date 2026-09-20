"""Speed 1 — instant learning (token space, no gradient update).

See ARCHITECTURE.md, section 2, and the concept paper chapter 5.3.
Letta/MemGPT style: the system itself decides via tool calls what
is written, retrieved, or forgotten. These three functions ARE the
"tools" that can be made available to an agent (or `hypothesis`
agent).

This is the only learning component that must be fully functional
in phase 0 — no training needed, only the MemoryStore.
"""

from __future__ import annotations

from continuum.memory.models import MemoryKind, MemoryRecord
from continuum.memory.store import MemoryStore


def remember(store: MemoryStore, text: str, *, source: str = "agent", importance: float = 0.5) -> MemoryRecord:
    """Writes a new observation into the (unvalidated) core memory.

    Lands first in the hot buffer — see memory/consolidation.py for
    the path into long-term memory.
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
    """Retrieves the `k` most relevant records for `query`, independent of the layer."""
    return store.search(query, k=k)


def forget(store: MemoryStore, record_id: str) -> None:
    """Removes a record explicitly. Deliberately no "silent" forgetting —
    every call should be audited in a later phase (see
    safety/governance.py::audit_log), once `forget` is called from an
    agent context instead of directly."""
    store.delete(record_id)
