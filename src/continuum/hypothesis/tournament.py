"""Orchestrierung des Multi-Agenten-Hypothesen-Turniers.

Siehe ARCHITECTURE.md, Abschnitt 3.
"""

from __future__ import annotations

from dataclasses import dataclass

from continuum.hypothesis.agents import (
    EvolutionAgent,
    GenerationAgent,
    HypothesisDraft,
    RankingAgent,
    ReflectionAgent,
)
from continuum.llm.client import LLMClient

Hypothesis = HypothesisDraft


@dataclass
class TournamentResult:
    final_hypotheses: list[Hypothesis]
    rounds_run: int


def run_tournament(
    context: str,
    llm: LLMClient,
    n_initial: int = 5,
    top_k: int = 2,
    rounds: int = 2,
) -> TournamentResult:
    """Fuehrt das vierstufige Turnier ueber `rounds` Runden aus.

    Generierung -> Reflexion -> Ranking -> Evolution, wobei die
    verfeinerten Top-Hypothesen jeweils in die naechste Runde eingehen.
    """
    generation = GenerationAgent(llm)
    reflection = ReflectionAgent(llm)
    ranking = RankingAgent(llm)
    evolution = EvolutionAgent(llm)

    candidates = generation.propose(context, n=n_initial)

    for _ in range(rounds):
        for h in candidates:
            reflection.critique(h)  # Ergebnis fliesst in Phase 1 in die Bewertung ein
        ranked = ranking.rank(candidates)
        top = ranked[:top_k]
        candidates = evolution.refine(top)

    return TournamentResult(final_hypotheses=candidates, rounds_run=rounds)
