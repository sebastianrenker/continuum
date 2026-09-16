# ARCHITECTURE.md — CONTINUUM technical specification (engineering edition)

A condensed, code-level version of the concept paper
(`docs/CONTINUUM_Konzeptpapier.docx`). Chapter numbers map to chapters 4–7 there.
Each section below names the corresponding Python module explicitly.

## 0. Closed control loop (reference for all modules)

```
1  Literature/memory retrieval             → memory.semantic, memory.episodic
2  Hypothesis generation (tournament)      → hypothesis.tournament
3  Novelty/safety screening                → verification.checker, safety.hazard_screening
4  Human approval (threshold)              → safety.governance
5  Experiment planning (Bayesian opt.)     → worldmodel.surrogate
6  Robotic execution [Phase 0: MOCK]       → data.simulated_materials
7  Sensing/characterization [MOCK]         → data.simulated_materials
8  Reconcile prediction vs. result         → worldmodel.surrogate, eval.metrics
9  Immediate update (speed 1)              → learning.speed1_context
10 Weekly adapter training (speed 2)       → learning.speed2_lora
11 Quarterly consolidation (speed 3)       → learning.speed3_consolidation
   → back to step 1
```

`scripts/run_demo_loop.py` implements exactly these eleven steps end-to-end on
simulated data (steps 6/7 mocked, all others real).

## 1. Memory system (`memory/`)

Four layers over one shared SQLite store (`memory/store.py`) as the persistence
layer (swappable for a real vector DB in later phases — the `MemoryStore`
interface must not change in the process).

- **`memory/models.py`** — data classes: `MemoryRecord` (id, text, embedding,
  timestamp, kind, importance, source, tags), `EpisodicEvent`, `SemanticFact`,
  `ProceduralSkill`.
- **`memory/store.py`** — `MemoryStore`: CRUD + `search(query, k)` via cosine
  similarity over embeddings (the embedding function is injectable; default: a
  deterministic hashing embedder for offline operation without an API key, see
  `memory/embeddings.py`).
- **`memory/working.py`** — context-window simulation for the currently running
  task; capacity-limited (LRU).
- **`memory/episodic.py`** — writing/retrieving concrete experiment events.
- **`memory/semantic.py`** — abstraction: aggregates several `EpisodicEvent`s
  into a `SemanticFact` once a pattern exceeds a confidence threshold
  (rule-based in Phase 0, LLM-assisted from Phase 2).
- **`memory/procedural.py`** — registry of callable lab protocols (Python
  callables with metadata), not just text descriptions.
- **`memory/consolidation.py`** — two-buffer model: `HotBuffer` (new, unvalidated
  records) → validation (duplicate check, minimum evidence) →
  `promote_to_long_term()`. No entry into long-term memory without validation.

**Phase 0 acceptance criterion:** `MemoryStore` supports at least 10,000 records
with retrieval latency < 200 ms on a local machine (no distributed system needed).

## 2. Learning system — three speeds (`learning/`)

| Module | Speed | Mechanism | Phase |
|---|---|---|---|
| `speed1_context.py` | seconds–minutes | tool-call-based read/write in core memory (Letta style), no gradient update | **0 — implement now** |
| `speed2_lora.py` | daily–weekly | LoRA adapters (PEFT) + contextual experience replay from `memory.episodic`, O-LoRA orthogonality between sub-domains | 2 — interface now, real training later |
| `speed3_consolidation.py` | quarterly | distillation of the adapters into the core model, EWC regularization (Fisher information) against catastrophic forgetting | 3 — interface now, real consolidation later |

`speed1_context.py` is the only learning component that must be fully functional
in Phase 0 — it needs no training, only the memory store. `speed2_lora.py` and
`speed3_consolidation.py` are deliberately laid out as clearly documented
interfaces that raise `NotImplementedError`; their docstrings point to the exact
techniques (EWC, O-LoRA, CER, Titans) to be used in a later phase.

## 3. Hypothesis engine (`hypothesis/`)

Multi-agent tournament following the AI co-scientist pattern:

- `GenerationAgent.propose(context) -> list[Hypothesis]`
- `ReflectionAgent.critique(hypothesis) -> Critique`
- `RankingAgent.rank(hypotheses) -> list[RankedHypothesis]`
- `EvolutionAgent.refine(top_k) -> list[Hypothesis]`

All four agents take an `LLMClient` (see `llm/client.py`) in the constructor. In
Phase 0 the entire pipeline runs with `MockLLMClient`, so that
`scripts/run_demo_loop.py` runs without an API key. `tournament.py::run_tournament()`
orchestrates the four agents over a configurable number of rounds.

## 4. World model (`worldmodel/surrogate.py`)

Not a general physical world model (see concept paper ch. 5.1 — deliberately
*not* the unsolved IntPhys problem, but a narrowly scoped, tractable prediction
task). `SurrogateModel`:

- `fit(X, y)` — Gaussian-process regression (scikit-learn) over synthesis
  parameters → material property.
- `predict(X) -> (mean, std)` — **always** returns an uncertainty estimate, never
  just a point value.
- `suggest_next(bounds, n) -> X_next` — Bayesian optimization (expected-improvement
  acquisition function) for the next experiment proposal.

## 5. Robotics/sensing mock (`data/simulated_materials.py`)

Replaces chapter 5.5 in Phase 0. `SimulatedLab.run_experiment(params) ->
ExperimentResult` evaluates a fixed but noisy objective function (deterministic
with a seed, but with realistic measurement noise), so the world model has
something real to learn without needing hardware. The class is cut so it can be
replaced 1:1 by a real lab connection (`run_experiment` stays the interface).

## 6. Verification / anti-hallucination layer (`verification/`)

- `evidence.py` — `Evidence` (enum: `EXPERIMENTAL`, `PREDICTED`, `LITERATURE`),
  `Claim` (text, evidence_kind, confidence, source_ref).
- `checker.py` — `ClaimChecker.verify(claim) -> VerificationResult`: checks whether
  a `Claim` has a valid provenance label *and* a matching piece of evidence in the
  `MemoryStore`/evidence graph. Claims without a valid label are hard-rejected
  (`raises InvalidClaimError`), not merely flagged with a warning — this enforces
  the "no unsupported claims" principle technically.

## 7. Safety / governance layer (`safety/`)

- `hazard_screening.py` — `screen(composition) -> HazardAssessment`: rule-based
  matching against a denylist of dangerous elements/compounds
  (`data/hazard_denylist.json`, in Phase 0 a deliberately small example set,
  **not** a complete safety rule set — to be extended by domain experts before
  Phase 1).
- `governance.py` — `GovernanceGate.request_approval(experiment) ->
  ApprovalDecision`: in Phase 0 always enforces manual/simulated approval for
  experiments above a cost threshold; `audit_log(event)` writes every event
  (memory write, consolidation, approval decision) as a JSON line to `audit.log`.

## 8. Evaluation (`eval/metrics.py`, `eval/harness.py`)

The four-level stack from the concept paper (ch. 6), as concrete functions:

```python
task_effectiveness(records) -> TaskEffectivenessReport        # level 1
memory_quality(store, gold_queries) -> MemoryQualityReport    # level 2
efficiency(run_log) -> EfficiencyReport                       # level 3
governance_compliance(audit_log_path) -> GovernanceReport     # level 4
calibration_curve(predictions, outcomes) -> CalibrationReport # domain-specific
forgetting_rate(pre_scores, post_scores) -> float             # domain-specific
```

`eval/harness.py::run_full_eval()` calls all six functions and writes a summary
report (JSON + plain text) — the basis for the go/no-go decision at the end of
each roadmap phase.

## 9. LLM abstraction (`llm/client.py`)

```python
class LLMClient(Protocol):
    def complete(self, prompt: str, **kwargs) -> str: ...
    def embed(self, text: str) -> list[float]: ...

class MockLLMClient:  # deterministic, no network, for tests/demo
    ...

class AnthropicClient:  # TODO(Phase 1): real integration
    ...
```

Every component that needs LLM capabilities receives an `LLMClient` via dependency
injection — never instantiated directly. This keeps the entire pipeline testable
and provider-agnostic.
