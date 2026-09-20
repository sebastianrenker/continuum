"""Simulated lab: a phase-0 placeholder for the robotic execution layer.

See ARCHITECTURE.md, section 5, and the concept paper chapter 5.5. This
class replaces real robot hardware in phase 0 with a fixed but
noisy objective function, so that `worldmodel.SurrogateModel` has something real to
learn. `run_experiment()` is cut so that it can be replaced 1:1 by a
real lab connection (see ROADMAP.md, phase 1) —
callers must never rely on implementation details of this class,
only on the signature of `run_experiment`.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass
class ExperimentResult:
    parameters: dict[str, float]
    ionic_conductivity: float  # the simulated target quantity, in an arbitrary unit
    noise_std: float


class SimulatedLab:
    """Simulates the synthesis of a solid-state electrolyte.

    The "true" objective function is deliberately unknown to the caller
    (just as a real lab does not provide a closed formula either) and only
    encoded here in the simulator. It has a single, clearly defined
    optimum, so that the world model's learning progress can be measured
    unambiguously (cf. ROADMAP.md, phase-0 criterion: a decreasing prediction error).
    """

    def __init__(self, seed: int = 7, noise_std: float = 0.05) -> None:
        self._rng = random.Random(seed)
        self._noise_std = noise_std

    def run_experiment(self, parameters: dict[str, float]) -> ExperimentResult:
        """Runs a simulated synthesis. Expects keys 'dopant_fraction'
        and 'sinter_temp_c' (normalized to [0, 1])."""
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
        # Two superimposed Gaussian hills as the "true" objective function with a
        # global optimum at (0.3, 0.7) — unknown to the world model,
        # which is meant to discover it through Bayesian optimization.
        peak1 = math.exp(-(((x - 0.3) ** 2) / 0.02 + ((t - 0.7) ** 2) / 0.02))
        peak2 = 0.4 * math.exp(-(((x - 0.7) ** 2) / 0.05 + ((t - 0.3) ** 2) / 0.05))
        return peak1 + peak2
