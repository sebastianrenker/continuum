"""Four agents of the hypothesis tournament (AI-co-scientist pattern).

See ARCHITECTURE.md, section 3, and the concept paper chapter 5.4. All
agents accept an `LLMClient` (see llm/client.py) — in
phase 0 typically `MockLLMClient`, so that the pipeline stays runnable
without an API key.
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
            text = self._llm.complete(f"Propose a research hypothesis. Context: {context}")
            drafts.append(HypothesisDraft(text=text))
        return drafts


class ReflectionAgent:
    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def critique(self, hypothesis: HypothesisDraft) -> Critique:
        response = self._llm.complete(f"Critically critique this hypothesis: {hypothesis.text}")
        return Critique(hypothesis=hypothesis, concerns=[response])


class RankingAgent:
    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def rank(self, hypotheses: list[HypothesisDraft]) -> list[HypothesisDraft]:
        # Phase-0 heuristic: scores via the LLMClient (deterministically
        # simulated with MockLLMClient) and sorts descending by a
        # combined novelty/testability heuristic.
        for h in hypotheses:
            _ = self._llm.complete(f"Rate the novelty and testability of: {h.text}")
            # A deterministic placeholder score based on the text length,
            # until a real LLM score (phase 1) replaces it.
            h.novelty_score = min(1.0, len(h.text) / 200.0)
            h.testability_score = 0.7
        return sorted(hypotheses, key=lambda h: h.novelty_score + h.testability_score, reverse=True)


class EvolutionAgent:
    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def refine(self, top_hypotheses: list[HypothesisDraft]) -> list[HypothesisDraft]:
        refined = []
        for h in top_hypotheses:
            text = self._llm.complete(f"Refine and combine this hypothesis: {h.text}")
            refined.append(HypothesisDraft(text=text, novelty_score=h.novelty_score, testability_score=h.testability_score))
        return refined
