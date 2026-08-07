"""Embedding-Funktionen fuer den MemoryStore.

Siehe ARCHITECTURE.md, Abschnitt 1. Der Default-Embedder ist deterministisch
und offline (kein API-Key noetig), damit `MemoryStore` in Phase 0 vollstaendig
lauffaehig ist. Eine spaetere Phase kann `embed_text` durch
`LLMClient.embed` ersetzen, ohne dass sich die `MemoryStore`-Schnittstelle
aendert.
"""

from __future__ import annotations

from collections.abc import Callable

from continuum.llm.client import _hash_embed

EmbedFn = Callable[[str], list[float]]


def default_embedder() -> EmbedFn:
    """Liefert den Default-Offline-Embedder (Hashing-basiert, dim=64)."""
    return _hash_embed


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
