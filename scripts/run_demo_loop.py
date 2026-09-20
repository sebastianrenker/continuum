#!/usr/bin/env python3
"""End-to-end demo of the full 11-step control loop (phase 0).

See ARCHITECTURE.md, section 0. Steps 6/7 (robotic execution,
sensing) are mocked by `SimulatedLab`, all other steps run
for real. No API key needed (MockLLMClient), no hardware.

Invocation:
    python scripts/run_demo_loop.py [--rounds 20]
"""

from __future__ import annotations

import argparse
import time
import warnings

import numpy as np
from sklearn.exceptions import ConvergenceWarning

# GP-kernel convergence warnings are harmless for this demo (a small
# dataset, a narrow search space) and are deliberately suppressed, so that the
# actual cycle output stays readable.
warnings.filterwarnings("ignore", category=ConvergenceWarning)

from continuum.data.simulated_materials import SimulatedLab
from continuum.eval.harness import format_report, run_full_eval
from continuum.hypothesis.tournament import run_tournament
from continuum.llm.client import MockLLMClient
from continuum.memory.consolidation import Consolidator
from continuum.memory.episodic import EpisodicMemory
from continuum.memory.models import EpisodicEvent
from continuum.memory.store import MemoryStore
from continuum.safety.governance import GovernanceGate
from continuum.safety.hazard_screening import screen
from continuum.verification.checker import ClaimChecker
from continuum.verification.evidence import Claim, Evidence
from continuum.worldmodel.surrogate import SurrogateModel

# The search space for dopant_fraction stays deliberately within the
# approval threshold defined in data/hazard_denylist.json
# (max_dopant_fraction_without_review=0.5) -- the world model should, in
# normal operation, explore only within the already-approved safety space.
# Suggestions outside this space are hard-rejected by the governance gate
# anyway (see safety/governance.py); that is intended
# behavior, not a bug of this demo.
BOUNDS = [(0.0, 0.45), (0.0, 1.0)]  # dopant_fraction, sinter_temp_c


def run(rounds: int) -> None:
    print(f"=== CONTINUUM demo loop: {rounds} rounds ===\n")

    store = MemoryStore("continuum_demo.db")
    episodic = EpisodicMemory(store)
    consolidator = Consolidator(store)
    checker = ClaimChecker(store)
    gate = GovernanceGate(audit_log_path="audit.log")
    lab = SimulatedLab(seed=7)
    world_model = SurrogateModel()
    llm = MockLLMClient()

    X_history: list[list[float]] = []
    y_history: list[float] = []
    predictions_for_calibration: list[tuple[float, float]] = []
    outcomes_for_calibration: list[float] = []
    run_log: list[dict] = []
    hypothesis_records: list[dict] = []

    for i in range(rounds):
        t0 = time.time()

        # Steps 1-2: retrieval + hypothesis generation
        context = "solid-state electrolyte with high ionic conductivity"
        tournament = run_tournament(context, llm, n_initial=3, top_k=1, rounds=1)
        hypothesis = tournament.final_hypotheses[0]

        # Step 5: experiment planning (Bayesian optimization)
        if i < 3:
            rng = np.random.default_rng(i)
            next_params = np.array([[rng.uniform(lo, hi) for lo, hi in BOUNDS]])
        else:
            next_params = world_model.suggest_next(BOUNDS, n=1, random_state=i)
        dopant_fraction, sinter_temp_c = next_params[0]

        # Step 3: safety check
        composition = {"elements": ["Li", "La", "Zr", "O"], "dopant_fraction": float(dopant_fraction)}
        hazard = screen(composition)

        # Step 4: governance approval
        decision = gate.request_approval(
            experiment_id=f"exp-{i}",
            estimated_cost=2.0,
            hazard_blocked=hazard.is_blocked,
        )
        if not decision.approved:
            print(f"[Round {i}] experiment rejected: {decision.reason}")
            continue

        # Steps 6-7: robotic execution + sensing [MOCK]
        result = lab.run_experiment({"dopant_fraction": dopant_fraction, "sinter_temp_c": sinter_temp_c})

        # Step 8: compare prediction vs. result
        if world_model._fitted:
            mean, std = world_model.predict(next_params)
            predictions_for_calibration.append((float(mean[0]), float(std[0])))
            outcomes_for_calibration.append(result.ionic_conductivity)

        # Step 9: instant update (speed 1)
        event = EpisodicEvent(
            description=hypothesis.text,
            parameters={"dopant_fraction": dopant_fraction, "sinter_temp_c": sinter_temp_c},
            outcome={"ionic_conductivity": result.ionic_conductivity},
        )
        record = episodic.record_event(event)

        # Verification: every statement needs a provenance tag
        claim = Claim(
            text=f"the composition yielded a conductivity of {result.ionic_conductivity:.3f}",
            evidence_kind=Evidence.EXPERIMENTAL,
            confidence=0.95,
            source_ref=record.id,
        )
        store.mark_validated(record.id)  # simplified consolidation for the demo
        verification = checker.verify(claim, raise_on_invalid=False)

        # Update the world model
        X_history.append([dopant_fraction, sinter_temp_c])
        y_history.append(result.ionic_conductivity)
        world_model.fit(np.array(X_history), np.array(y_history))

        run_log.append({"cost": 2.0, "latency_ms": (time.time() - t0) * 1000, "validated": verification.is_valid})
        hypothesis_records.append({"tested": True, "confirmed": result.ionic_conductivity > 0.5})

        print(
            f"[Round {i}] params=({dopant_fraction:.2f}, {sinter_temp_c:.2f}) "
            f"-> conductivity={result.ionic_conductivity:.3f} | "
            f"claim valid={verification.is_valid}"
        )

    # Steps 10-11: the speed-2/3 updates are interfaces in phase 0
    # (see learning/speed2_lora.py, speed3_consolidation.py) — not
    # called here, to avoid a NotImplementedError. Instead, a final
    # consolidation round of the memory runs:
    report = consolidator.run_consolidation_pass()
    print(f"\nConsolidation: {len(report.promoted)} promoted, "
          f"{len(report.rejected_duplicates)} duplicates, "
          f"{len(report.rejected_low_importance)} too low importance")

    eval_report = run_full_eval(
        hypothesis_records=hypothesis_records,
        retrieved_ids=[],
        relevant_ids=[],
        run_log=run_log,
        audit_events=gate.read_audit_log(),
        predictions=predictions_for_calibration,
        outcomes=outcomes_for_calibration,
    )
    print("\n" + format_report(eval_report))

    store.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=20)
    args = parser.parse_args()
    run(args.rounds)
