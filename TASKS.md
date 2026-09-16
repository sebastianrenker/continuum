# TASKS.md — Phase 0 backlog

Concrete, actionable tasks in recommended order. This repository already ships a
skeleton for each task (interfaces, partly working code, partly `TODO` markers) —
see the "Status in repo" note. Tick a box once the Definition of Done is met.

## Block A — foundation

- [x] **A1. Project setup.** `pyproject.toml`, `src` layout, `pytest` config.
      *Status: done.*
- [x] **A2. LLM abstraction.** `llm/client.py` with the `LLMClient` protocol and
      `MockLLMClient`. *Status: done, `AnthropicClient` is TODO(Phase 1).*
- [x] **A3. Embedding function.** `memory/embeddings.py` with a deterministic
      offline hashing embedder. *Status: done.*

## Block B — memory system

- [x] **B1. Data models.** `memory/models.py`. *Status: done.*
- [x] **B2. `MemoryStore` (SQLite + cosine search).** `memory/store.py`.
      *Status: done, test in `tests/test_memory_store.py`.*
- [x] **B3. Working/episodic/semantic/procedural wrappers.**
      `memory/working.py`, `episodic.py`, `semantic.py`, `procedural.py`.
      *Status: done.*
- [x] **B4. Two-buffer consolidation.** `memory/consolidation.py`.
      *Status: done, test in `tests/test_consolidation.py`.*
- [ ] **B5. Scaling test.** Load 10,000 synthetic records, measure `search()`
      latency. Acceptance criterion: < 200 ms p95 on a standard development
      machine (see `ARCHITECTURE.md` section 1). *Status: TODO — no load test yet,
      only a functional test.*

## Block C — world model & simulated lab

- [x] **C1. `SimulatedLab`.** `data/simulated_materials.py` with a fixed, noisy
      objective function. *Status: done.*
- [x] **C2. `SurrogateModel` (Gaussian process).** `worldmodel/surrogate.py` with
      `fit`, `predict` (incl. uncertainty), `suggest_next` (expected improvement).
      *Status: done, test in `tests/test_worldmodel.py`.*
- [ ] **C3. Calibration report over a real demo run.** After 20+ rounds of the demo
      loop, check: does the surrogate model's mean prediction error decrease? Feed
      the result into `eval/harness.py::calibration_curve`. *Status: TODO — the
      function exists but has not yet been evaluated systematically over many
      rounds.*

## Block D — verification & safety

- [x] **D1. `Claim`/`Evidence` data model.** `verification/evidence.py`.
      *Status: done.*
- [x] **D2. `ClaimChecker`.** `verification/checker.py`, hard failure on a missing
      provenance label. *Status: done, test in `tests/test_verification.py`.*
- [x] **D3. Hazardous-material screening (example denylist).**
      `safety/hazard_screening.py` + `data/hazard_denylist.json`. *Status: done,
      a deliberately small example set — see the warning below.*
- [x] **D4. `GovernanceGate` + audit log.** `safety/governance.py`.
      *Status: done, test in `tests/test_governance.py`.*
- [ ] **D5. Have domain experts extend the denylist** before this repository is
      tested even on simulated data with more realistic compositions that go
      beyond the demo example set. *Status: deliberately open — a human expert
      review, not an automated task.*

## Block E — hypothesis engine

- [x] **E1. Four agent interfaces.** `hypothesis/agents.py` (`GenerationAgent`,
      `ReflectionAgent`, `RankingAgent`, `EvolutionAgent`), runnable with
      `MockLLMClient`. *Status: done.*
- [x] **E2. `run_tournament()` orchestration.** `hypothesis/tournament.py`.
      *Status: done, test in `tests/test_hypothesis.py`.*
- [ ] **E3. Prompt polishing for a real `LLMClient`.** The current prompts are
      sufficient for `MockLLMClient` but not yet tuned for quality with a real
      language model. *Status: TODO(Phase 1) — only relevant once `AnthropicClient`
      is implemented.*

## Block F — learning system

- [x] **F1. Speed 1 (immediate learning).** `learning/speed1_context.py` —
      tool-call functions `remember()`, `recall()`, `forget()` on top of
      `MemoryStore`. *Status: done, test in `tests/test_speed1.py`.*
- [ ] **F2. Speed 2 (LoRA adapters).** `learning/speed2_lora.py` is a documented
      interface that raises `NotImplementedError`. *Status: deliberately
      TODO(Phase 2) — see `ARCHITECTURE.md` section 2. Do not implement in Phase 0
      (phase discipline).*
- [ ] **F3. Speed 3 (consolidation).** `learning/speed3_consolidation.py`, also an
      interface. *Status: deliberately TODO(Phase 3).*

## Block G — evaluation

- [x] **G1. Four-level metrics + domain-specific metrics.** `eval/metrics.py`.
      *Status: done, test in `tests/test_eval_metrics.py`.*
- [x] **G2. `run_full_eval()` harness.** `eval/harness.py`. *Status: done.*
- [ ] **G3. Persist report history across several demo runs** (`eval_history.jsonl`)
      so that trends (calibration, forgetting rate) become visible over time rather
      than only snapshots. *Status: TODO.*

## Block H — integration & quality

- [x] **H1. `scripts/run_demo_loop.py`** — full 11-step cycle end-to-end.
      *Status: done.*
- [x] **H2. Test suite green.** `pytest` runs without errors. *Status: done at the
      time of repo creation — re-check after every change.*
- [x] **H3. CI workflow** (GitHub Actions: `ruff` + `pytest` + demo smoke test on
      every push/PR). *Status: done, see `.github/workflows/ci.yml`.*
- [ ] **H4. Type checking** with `mypy` or `pyright` added to CI. *Status: TODO.*

---

## Getting started

Opening this repo for the first time: run `pytest`, read the output of
`python scripts/run_demo_loop.py`, then start with **B5** or **C3** (open items
with no dependency on later phases). Avoid **F2/F3** — those are deliberately
reserved for later phases.
