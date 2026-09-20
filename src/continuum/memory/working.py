"""Working memory: capacity-limited context of the running task.

See ARCHITECTURE.md, section 1. Deliberately NOT persisted in the MemoryStore
— working memory is ephemeral by definition (cf. CLAUDE.md,
principle 5: "long context windows are not memory"). What should
persist must be explicitly written to episodic memory.
"""

from __future__ import annotations

from collections import deque


class WorkingMemory:
    """An LRU-like short-term buffer for the currently running task."""

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
