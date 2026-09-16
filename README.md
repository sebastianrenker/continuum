# CONTINUUM

![CI](https://github.com/sebastianrenker/continuum/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-Phase%200%20prototype-orange)

> Architecture prototype of a continually learning autonomous research system — honestly labelled as Phase 0.

## Overview

A software prototype (Phase 0) of a continually learning autonomous research
system, instantiated on the example of autonomous materials discovery. Full
technical rationale:
[`docs/CONTINUUM_Konzeptpapier.docx`](docs/CONTINUUM_Konzeptpapier.docx).

> **Honest status:** this is a concept and architecture prototype — not a
> validated scientific result and not a production system. In Phase 0 every
> "experiment" runs against a simulated objective function, not real lab
> hardware (see `ROADMAP.md`). The goal is to show *how* an architecture for
> genuine continual learning could look — not to be a finished product.

> **For Claude Code / other AI coding agents:** read `CLAUDE.md` first — it
> holds the binding working rules for this repository.

## Features

**What works (no API key, no GPU, no hardware):**

- Four-layer memory system (SQLite backend, two-buffer consolidation)
- Bayesian world model (Gaussian process) with uncertainty estimation and a
  proposal function for the next experiment
- Simulated lab as a placeholder for real robotics
- Verification layer that lets no unsupported claim through
- Hazardous-material screening and a governance gate with an audit log
- Multi-agent hypothesis pipeline (runnable with a mock LLM)
- Four-layer evaluation stack

**What deliberately does not work yet:** genuine continual weight learning
(LoRA adapters, consolidation) and the connection to real lab hardware are later
phases (see `ROADMAP.md`) — laid out as documented interfaces, not as code
(the "phase discipline" principle, see `CLAUDE.md`).

## Architecture

```
src/continuum/
├── llm/            # Provider-agnostic LLM interface + mock
├── memory/         # Working/Episodic/Semantic/Procedural memory
├── learning/       # Three-speed learning system
├── hypothesis/     # Multi-agent hypothesis tournament
├── worldmodel/     # Bayesian surrogate model
├── verification/   # Anti-hallucination layer
├── safety/         # Hazardous-material screening & governance
├── eval/           # Four-level evaluation
└── data/           # Simulated lab (Phase-0 placeholder for hardware)
```

Full per-module specification in `ARCHITECTURE.md`, current backlog in `TASKS.md`.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

python scripts/run_demo_loop.py     # full cycle on simulated data
```

## Tests

```bash
pytest
```

## License

MIT — see [`LICENSE`](LICENSE). © 2026 Sebastian Renker.

Research/concept prototype, not a production system. The safety-relevant
components (`safety/hazard_screening.py`) contain only an example rule set and
must be reviewed and extended by domain experts before any use with real
materials (see `TASKS.md`, D5).
