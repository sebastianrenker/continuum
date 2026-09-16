# Contributing to CONTINUUM

Thanks for your interest. CONTINUUM is a phase-0 architecture prototype with
deliberately strict discipline — contributions are measured against a high bar.
Before your first commit, read the binding working rules in
[`CLAUDE.md`](CLAUDE.md) and the design truth in [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Ground rules (non-negotiable)

- **No unsubstantiated claim.** Every statement about a material/hypothesis/model is
  tagged via `verification/evidence.py` with `EXPERIMENTAL`/`PREDICTED`/`LITERATURE`.
  Not mergeable without provenance.
- **Safety gates are never bypassed** — not even in tests or demos. Every "experiment
  approval" passes through `safety/governance.py`.
- **Everything is auditable.** No silent state change; store, consolidation, and
  governance steps are logged.
- **Phase discipline.** Do not build anything from phase 2/3 (real LoRA training,
  robotics connection) before the acceptance criteria of the prior phase in
  [`TASKS.md`](TASKS.md) are met. If a task looks like a later phase: say so
  explicitly, do not implement it along the way.
- **Mocks stay swappable.** LLM access only via `llm/client.py::LLMClient`;
  `MockLLMClient` must keep the pipeline runnable without an API key at all times.
- **No secrets** in commits.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Python ≥ 3.10. Phase-2 dependencies (torch/transformers/peft) are deliberately
optional (`.[phase2]`) and not needed for phase-0 work.

## Local checks (must be green)

```bash
ruff format --check .
ruff check .
pytest
python scripts/run_demo_loop.py     # end-to-end demo on simulated data
```

CI runs `ruff check`, `pytest`, and the demo smoke test
(`run_demo_loop.py --rounds 5`) on every pull request; `ruff format --check` is a local
convention.

## Security-relevant changes

Anything touching `safety/governance.py`, `safety/hazard_screening.py`, or
`verification/` must:

1. include a test that specifically challenges the boundary (a bypass attempt), and
2. keep every existing security test green.

Please report vulnerabilities **privately** — see [`SECURITY.md`](SECURITY.md), not as
a public issue/PR.

## Definition of Done

A task from [`TASKS.md`](TASKS.md) is only done when the implementation matches the
interface/docstring, a test exists and `pytest` is green, no ground rule is violated,
and `TASKS.md` is updated.

## Style

- Identifiers (functions, variables, classes) in **English**; docstrings and comments
  in **English** as well.
- Explicit type annotations, `ruff` (line length 100, target `py310`).
- Interface before implementation: `TODO(Phase X): ...` in docstrings is deliberately
  open and to be implemented per the referenced architecture.
