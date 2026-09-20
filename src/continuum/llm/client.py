"""Provider-independent LLM interface.

See ARCHITECTURE.md, section 9. Every component that needs language-model
capabilities (hypothesis agents, semantic abstraction, ...)
gets an instance of `LLMClient` via dependency injection — never
instantiated directly. This keeps the pipeline testable and provider-independent
(principle from CLAUDE.md, section 3.5).
"""

from __future__ import annotations

import hashlib
import random
from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    """The minimal interface every LLM connection must fulfill."""

    def complete(self, prompt: str, *, temperature: float = 0.7, max_tokens: int = 512) -> str:
        """Produces a text completion for `prompt`."""
        ...

    def embed(self, text: str) -> list[float]:
        """Produces an embedding vector for `text`."""
        ...


class MockLLMClient:
    """A deterministic, network-free substitute for tests and demos.

    Produces plausible-looking but not "intelligent" answers following
    simple text patterns. This keeps the entire pipeline
    (`scripts/run_demo_loop.py`) runnable without an API key — see
    CLAUDE.md, section 3.5.
    """

    def __init__(self, seed: int = 42) -> None:
        self._rng = random.Random(seed)

    def complete(self, prompt: str, *, temperature: float = 0.7, max_tokens: int = 512) -> str:
        # A very simple, deterministic heuristic: extracts the last
        # "keyword" from the prompt and builds a placeholder answer from it.
        # Does NOT replace real LLM quality — only meant for tests/demo.
        keyword = prompt.strip().split()[-1] if prompt.strip() else "hypothesis"
        variants = [
            (
                f"Mock hypothesis based on '{keyword}': doping with element X "
                f"could improve the target quantity."
            ),
            (
                f"Mock critique of '{keyword}': plausible, but the synthesis conditions "
                f"are unclearly specified."
            ),
            f"Mock evaluation of '{keyword}': medium novelty, high testability.",
        ]
        return variants[self._rng.randrange(len(variants))]

    def embed(self, text: str) -> list[float]:
        return _hash_embed(text)


class AnthropicClient:
    """A real connection to a language model (e.g. the Anthropic API).

    TODO(Phase 1): implement as soon as the project goes beyond the pure
    software prototype (phase 0). Must fulfill `LLMClient` exactly,
    so that `MockLLMClient` stays 1:1 swappable. Deliberately not yet
    implemented — see TASKS.md, block E3, and CLAUDE.md,
    the "phase discipline" principle.
    """

    def __init__(self, api_key: str | None = None, model: str = "claude-sonnet-5") -> None:
        raise NotImplementedError(
            "AnthropicClient is intended for phase 1. In phase 0 use "
            "MockLLMClient. See ARCHITECTURE.md, section 9."
        )


def _hash_embed(text: str, dim: int = 64) -> list[float]:
    """A deterministic offline embedder based on hashing.

    No semantic understanding, but stable, fast, and without an external
    dependency — sufficient to test `MemoryStore.search()` in phase 0.
    Replaced in a later phase by real embeddings
    (e.g. via `LLMClient.embed`).
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
