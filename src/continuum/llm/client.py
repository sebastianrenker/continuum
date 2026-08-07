"""Anbieterunabhängige LLM-Schnittstelle.

Siehe ARCHITECTURE.md, Abschnitt 9. Jede Komponente, die Sprachmodell-
Fähigkeiten braucht (Hypothesen-Agenten, semantische Abstraktion, ...),
bekommt eine Instanz von `LLMClient` per Dependency Injection — niemals
direkt instanziiert. Das hält die Pipeline testbar und anbieterunabhängig
(Prinzip aus CLAUDE.md, Abschnitt 3.5).
"""

from __future__ import annotations

import hashlib
import random
from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    """Minimales Interface, das jede LLM-Anbindung erfüllen muss."""

    def complete(self, prompt: str, *, temperature: float = 0.7, max_tokens: int = 512) -> str:
        """Erzeugt eine Text-Vervollständigung für `prompt`."""
        ...

    def embed(self, text: str) -> list[float]:
        """Erzeugt einen Embedding-Vektor für `text`."""
        ...


class MockLLMClient:
    """Deterministischer, netzwerkfreier Ersatz für Tests und Demos.

    Erzeugt plausibel aussehende, aber nicht "intelligente" Antworten nach
    einfachen Textmustern. Damit bleibt die gesamte Pipeline
    (`scripts/run_demo_loop.py`) ohne API-Key lauffähig — siehe
    CLAUDE.md, Abschnitt 3.5.
    """

    def __init__(self, seed: int = 42) -> None:
        self._rng = random.Random(seed)

    def complete(self, prompt: str, *, temperature: float = 0.7, max_tokens: int = 512) -> str:
        # Sehr einfache, deterministische Heuristik: extrahiert das letzte
        # "Stichwort" aus dem Prompt und baut daraus eine Platzhalter-Antwort.
        # Ersetzt KEINE echte LLM-Qualität — nur für Tests/Demo gedacht.
        keyword = prompt.strip().split()[-1] if prompt.strip() else "Hypothese"
        variants = [
            (
                f"Mock-Hypothese basierend auf '{keyword}': Dotierung mit Element X "
                f"koennte die Zielgroesse verbessern."
            ),
            (
                f"Mock-Kritik zu '{keyword}': Plausibel, aber Synthesebedingungen "
                f"unklar spezifiziert."
            ),
            f"Mock-Bewertung zu '{keyword}': mittlere Neuheit, hohe Testbarkeit.",
        ]
        return variants[self._rng.randrange(len(variants))]

    def embed(self, text: str) -> list[float]:
        return _hash_embed(text)


class AnthropicClient:
    """Echte Anbindung an ein Sprachmodell (z. B. die Anthropic-API).

    TODO(Phase 1): Implementieren, sobald das Projekt über den reinen
    Software-Prototyp (Phase 0) hinausgeht. Muss `LLMClient` exakt
    erfuellen, damit `MockLLMClient` 1:1 austauschbar bleibt. Bewusst noch
    nicht implementiert — siehe TASKS.md, Block E3, und CLAUDE.md,
    Prinzip "Phasendisziplin".
    """

    def __init__(self, api_key: str | None = None, model: str = "claude-sonnet-5") -> None:
        raise NotImplementedError(
            "AnthropicClient ist fuer Phase 1 vorgesehen. Verwende in Phase 0 "
            "MockLLMClient. Siehe ARCHITECTURE.md, Abschnitt 9."
        )


def _hash_embed(text: str, dim: int = 64) -> list[float]:
    """Deterministischer Offline-Embedder auf Hashing-Basis.

    Kein semantisches Verständnis, aber stabil, schnell und ohne externe
    Abhängigkeit — ausreichend, um `MemoryStore.search()` in Phase 0 zu
    testen. Wird in einer spaeteren Phase durch echte Embeddings
    (z. B. via `LLMClient.embed`) ersetzt.
    """
    vec = [0.0] * dim
    tokens = text.lower().split()
    if not tokens:
        return vec
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        for i in range(dim):
            vec[i] += digest[i % len(digest)] / 255.0
    norm = sum(v * v for v in vec) ** 0.5
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec
