"""Vier Agenten des Hypothesen-Turniers (AI-Co-Scientist-Muster).

Siehe ARCHITECTURE.md, Abschnitt 3, und Konzeptpapier Kapitel 5.4. Alle
Agenten nehmen einen `LLMClient` entgegen (siehe llm/client.py) — in
Phase 0 typischerweise `MockLLMClient`, damit die Pipeline ohne API-Key
lauffaehig bleibt.
"""

from __future__ import annotations

from dataclasses import dataclass

from continuum.llm.client import LLMClient


@dataclass
class HypothesisDraft:
    text: str
    novelty_score: float = 0.0
    testability_score: float = 0.0


@dataclass
class Critique:
    hypothesis: HypothesisDraft
    concerns: list[str]


class GenerationAgent:
    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def propose(self, context: str, n: int = 3) -> list[HypothesisDraft]:
        drafts = []
        for _ in range(n):
            text = self._llm.complete(f"Schlage eine Forschungshypothese vor. Kontext: {context}")
            drafts.append(HypothesisDraft(text=text))
        return drafts


class ReflectionAgent:
    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def critique(self, hypothesis: HypothesisDraft) -> Critique:
        response = self._llm.complete(f"Kritisiere kritisch diese Hypothese: {hypothesis.text}")
        return Critique(hypothesis=hypothesis, concerns=[response])


class RankingAgent:
    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def rank(self, hypotheses: list[HypothesisDraft]) -> list[HypothesisDraft]:
        # Phase-0-Heuristik: bewertet ueber den LLMClient (bei MockLLMClient
        # deterministisch simuliert) und sortiert absteigend nach einer
        # kombinierten Neuheits-/Testbarkeits-Heuristik.
        for h in hypotheses:
            _ = self._llm.complete(f"Bewerte Neuheit und Testbarkeit von: {h.text}")
            # Deterministische Platzhalter-Bewertung auf Basis der Textlaenge,
            # bis eine echte LLM-Bewertung (Phase 1) das ersetzt.
            h.novelty_score = min(1.0, len(h.text) / 200.0)
            h.testability_score = 0.7
        return sorted(hypotheses, key=lambda h: h.novelty_score + h.testability_score, reverse=True)


class EvolutionAgent:
    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def refine(self, top_hypotheses: list[HypothesisDraft]) -> list[HypothesisDraft]:
        refined = []
        for h in top_hypotheses:
            text = self._llm.complete(f"Verfeinere und kombiniere diese Hypothese: {h.text}")
            refined.append(HypothesisDraft(text=text, novelty_score=h.novelty_score, testability_score=h.testability_score))
        return refined
