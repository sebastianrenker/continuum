# ROADMAP.md

Phase plan from the concept paper (chapter 8), with go/no-go criteria. This
repository covers **Phase 0**.

## Phase 0 — proof of concept (months 1–3, software only)

**Goal:** memory system + speed-1 learning + world model + safety/verification
layer + evaluation harness, all runnable on simulated materials data. No hardware,
no GPU training required.

**Go/no-go criteria for Phase 1:**
- [ ] `eval.harness.run_full_eval()` runs without error and returns plausible
      (not necessarily perfect) values on all six metrics.
- [ ] `scripts/run_demo_loop.py` completes the full 11-step cycle (steps 6/7
      mocked) at least 20 times without crashing and with a decreasing world-model
      prediction error over time.
- [ ] No claim without a valid provenance label passes `ClaimChecker` (see the
      tests in `tests/test_verification.py`).
- [ ] All governance decisions are traceable in the audit log.

## Phase 1 — lab integration (months 4–9)

Connection to a real self-driving-lab partner lab (e.g. via a robotics API), a
narrowly scoped material type. `data/simulated_materials.py` is replaced by a real
implementation of `run_experiment()` without the interface changing. **Not part of
this repository** — a standalone follow-up project with a hardware partner.

## Phase 2 — arm active learning (months 10–18)

`learning/speed2_lora.py` goes from interface to real implementation (PEFT/LoRA
training, O-LoRA orthogonality, contextual experience replay from real experiment
data). Prerequisite: Phase 0 metrics stable, Phase 1 data flow established.

## Phase 3 — consolidation & validation (months 19–30)

`learning/speed3_consolidation.py` is armed (EWC-based distillation). External,
independent review of the catastrophic-forgetting rate and the calibration curve.

## Phase 4 — domain transfer (from month 30)

Test of the architecture hypothesis: transferring the domain-agnostic core
(`memory/`, `learning/`, `verification/`, `hypothesis/`) to a second domain by
swapping `data/simulated_materials.py` and `safety/hazard_screening.py` for
domain-specific equivalents (see concept paper chapter 7, generalization table).

---

**Principle for every phase:** failing the go/no-go criteria is a valid outcome.
Do not put more capital/effort into the next phase before the current phase meets
its criteria — phase discipline.
