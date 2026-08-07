"""Simuliertes Labor: Phase-0-Platzhalter fuer die robotische Ausfuehrungsschicht.

Siehe ARCHITECTURE.md, Abschnitt 5, und Konzeptpapier Kapitel 5.5. Diese
Klasse ersetzt in Phase 0 echte Roboter-Hardware durch eine feste, aber
verrauschte Zielfunktion, damit `worldmodel.SurrogateModel` etwas Echtes zu
lernen hat. `run_experiment()` ist so geschnitten, dass sie 1:1 durch eine
echte Laboranbindung ersetzt werden kann (siehe ROADMAP.md, Phase 1) —
Aufrufer duerfen sich niemals auf Implementierungsdetails dieser Klasse
verlassen, nur auf die Signatur von `run_experiment`.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass
class ExperimentResult:
    parameters: dict[str, float]
    ionic_conductivity: float  # simulierte Zielgroesse, willkuerliche Einheit
    noise_std: float


class SimulatedLab:
    """Simuliert die Synthese eines Festkoerperelektrolyten.

    Die "wahre" Zielfunktion ist absichtlich unbekannt fuer den Aufrufer
    (so wie ein echtes Labor auch keine geschlossene Formel liefert) und nur
    hier im Simulator kodiert. Sie hat ein einzelnes, klar definiertes
    Optimum, damit sich Lernfortschritt des Weltmodells eindeutig messen
    laesst (vgl. ROADMAP.md, Phase-0-Kriterium: sinkender Vorhersagefehler).
    """

    def __init__(self, seed: int = 7, noise_std: float = 0.05) -> None:
        self._rng = random.Random(seed)
        self._noise_std = noise_std

    def run_experiment(self, parameters: dict[str, float]) -> ExperimentResult:
        """Fuehrt eine simulierte Synthese aus. Erwartet Keys 'dopant_fraction'
        und 'sinter_temp_c' (normalisiert auf [0, 1])."""
        x = parameters.get("dopant_fraction", 0.0)
        t = parameters.get("sinter_temp_c", 0.0)
        true_value = self._true_conductivity(x, t)
        noisy_value = true_value + self._rng.gauss(0, self._noise_std)
        return ExperimentResult(
            parameters=dict(parameters),
            ionic_conductivity=max(0.0, noisy_value),
            noise_std=self._noise_std,
        )

    @staticmethod
    def _true_conductivity(x: float, t: float) -> float:
        # Zwei ueberlagerte Gauss-Huegel als "wahre" Zielfunktion mit einem
        # globalen Optimum bei (0.3, 0.7) — unbekannt fuer das Weltmodell,
        # das es durch Bayes'sche Optimierung entdecken soll.
        peak1 = math.exp(-(((x - 0.3) ** 2) / 0.02 + ((t - 0.7) ** 2) / 0.02))
        peak2 = 0.4 * math.exp(-(((x - 0.7) ** 2) / 0.05 + ((t - 0.3) ** 2) / 0.05))
        return peak1 + peak2
