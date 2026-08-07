from continuum.hypothesis.tournament import run_tournament
from continuum.llm.client import MockLLMClient


def test_run_tournament_returns_final_hypotheses():
    llm = MockLLMClient(seed=1)
    result = run_tournament("Festkoerperelektrolyte mit hoher Ionenleitfaehigkeit", llm, n_initial=4, top_k=2, rounds=2)

    assert result.rounds_run == 2
    assert len(result.final_hypotheses) == 2
    for h in result.final_hypotheses:
        assert isinstance(h.text, str) and h.text
