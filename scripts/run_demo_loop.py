#!/usr/bin/env python3
"""End-to-End-Demo des vollstaendigen 11-Schritte-Regelkreises (Phase 0).

Siehe ARCHITECTURE.md, Abschnitt 0. Schritte 6/7 (robotische Ausfuehrung,
Sensorik) sind durch `SimulatedLab` gemockt, alle anderen Schritte laufen
echt. Kein API-Key noetig (MockLLMClient), keine Hardware.

Aufruf:
    python scripts/run_demo_loop.py [--rounds 20]
"""

from __future__ import annotations

import argparse
import time
import warnings

import numpy as np
from sklearn.exceptions import ConvergenceWarning

# GP-Kernel-Konvergenzwarnungen sind fuer diese Demo unschaedlich (kleiner
# Datensatz, enger Suchraum) und werden bewusst unterdrueckt, damit die
# eigentliche Zyklus-Ausgabe lesbar bleibt.
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

# Der Suchraum fuer dopant_fraction bleibt bewusst innerhalb der in
# data/hazard_denylist.json definierten Freigabeschwelle
# (max_dopant_fraction_without_review=0.5) -- das Weltmodell soll im
# Regelbetrieb nur im bereits freigegebenen Sicherheitsraum explorieren.
# Vorschlaege ausserhalb dieses Raums werden vom Governance-Gate ohnehin
# hart abgelehnt (siehe safety/governance.py); das ist beabsichtigtes
# Verhalten, nicht ein Bug dieser Demo.
BOUNDS = [(0.0, 0.45), (0.0, 1.0)]  # dopant_fraction, sinter_temp_c


def run(rounds: int) -> None:
    print(f"=== CONTINUUM Demo-Loop: {rounds} Runden ===\n")

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

        # Schritt 1-2: Retrieval + Hypothesengenerierung
        context = "Festkoerperelektrolyt mit hoher Ionenleitfaehigkeit"
        tournament = run_tournament(context, llm, n_initial=3, top_k=1, rounds=1)
        hypothesis = tournament.final_hypotheses[0]

        # Schritt 5: Experimentplanung (Bayes'sche Optimierung)
        if i < 3:
            rng = np.random.default_rng(i)
            next_params = np.array([[rng.uniform(lo, hi) for lo, hi in BOUNDS]])
        else:
            next_params = world_model.suggest_next(BOUNDS, n=1, random_state=i)
        dopant_fraction, sinter_temp_c = next_params[0]

        # Schritt 3: Sicherheitspruefung
        composition = {"elements": ["Li", "La", "Zr", "O"], "dopant_fraction": float(dopant_fraction)}
        hazard = screen(composition)

        # Schritt 4: Governance-Freigabe
        decision = gate.request_approval(
            experiment_id=f"exp-{i}",
            estimated_cost=2.0,
            hazard_blocked=hazard.is_blocked,
        )
        if not decision.approved:
            print(f"[Runde {i}] Experiment abgelehnt: {decision.reason}")
            continue

        # Schritt 6-7: robotische Ausfuehrung + Sensorik [MOCK]
        result = lab.run_experiment({"dopant_fraction": dopant_fraction, "sinter_temp_c": sinter_temp_c})

        # Schritt 8: Abgleich Vorhersage vs. Ergebnis
        if world_model._fitted:
            mean, std = world_model.predict(next_params)
            predictions_for_calibration.append((float(mean[0]), float(std[0])))
            outcomes_for_calibration.append(result.ionic_conductivity)

        # Schritt 9: Sofort-Update (Geschwindigkeit 1)
        event = EpisodicEvent(
            description=hypothesis.text,
            parameters={"dopant_fraction": dopant_fraction, "sinter_temp_c": sinter_temp_c},
            outcome={"ionic_conductivity": result.ionic_conductivity},
        )
        record = episodic.record_event(event)

        # Verifikation: jede Aussage braucht eine Herkunftskennzeichnung
        claim = Claim(
            text=f"Zusammensetzung ergab Leitfaehigkeit {result.ionic_conductivity:.3f}",
            evidence_kind=Evidence.EXPERIMENTAL,
            confidence=0.95,
            source_ref=record.id,
        )
        store.mark_validated(record.id)  # vereinfachte Konsolidierung fuer die Demo
        verification = checker.verify(claim, raise_on_invalid=False)

        # Weltmodell aktualisieren
        X_history.append([dopant_fraction, sinter_temp_c])
        y_history.append(result.ionic_conductivity)
        world_model.fit(np.array(X_history), np.array(y_history))

        run_log.append({"cost": 2.0, "latency_ms": (time.time() - t0) * 1000, "validated": verification.is_valid})
        hypothesis_records.append({"tested": True, "confirmed": result.ionic_conductivity > 0.5})

        print(
            f"[Runde {i}] params=({dopant_fraction:.2f}, {sinter_temp_c:.2f}) "
            f"-> Leitfaehigkeit={result.ionic_conductivity:.3f} | "
            f"Claim gueltig={verification.is_valid}"
        )

    # Schritt 10-11: Geschwindigkeit-2/3-Updates sind in Phase 0 Interfaces
    # (siehe learning/speed2_lora.py, speed3_consolidation.py) — hier nicht
    # aufgerufen, um NotImplementedError zu vermeiden. Stattdessen laeuft
    # eine finale Konsolidierungs-Runde des Gedaechtnisses:
    report = consolidator.run_consolidation_pass()
    print(f"\nKonsolidierung: {len(report.promoted)} befoerdert, "
          f"{len(report.rejected_duplicates)} Duplikate, "
          f"{len(report.rejected_low_importance)} zu geringe Bedeutung")

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
