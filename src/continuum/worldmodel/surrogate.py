"""Bayes'sches Surrogatmodell fuer die Wahrnehmungs-/Weltmodell-Schicht.

Siehe ARCHITECTURE.md, Abschnitt 4, und Konzeptpapier Kapitel 5.1. Bewusst
KEIN Versuch, das allgemeine (ungeloeste) Problem intuitiver Physik zu
loesen — stattdessen eine eng gefasste, tractable Regressionsaufgabe:
Syntheseparameter -> Materialeigenschaft, mit expliziter
Unsicherheitsschaetzung.
"""

from __future__ import annotations

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel


class SurrogateModel:
    """Gaussian-Process-Regression mit Expected-Improvement-Akquisition.

    Nutzung:
        model = SurrogateModel()
        model.fit(X, y)
        mean, std = model.predict(X_new)
        next_points = model.suggest_next(bounds, n=3)
    """

    def __init__(self, random_state: int = 0) -> None:
        kernel = RBF(length_scale=0.2) + WhiteKernel(noise_level=0.01)
        self._gp = GaussianProcessRegressor(kernel=kernel, normalize_y=True, random_state=random_state)
        self._fitted = False
        self._best_y: float = -np.inf

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        X = np.atleast_2d(X)
        y = np.asarray(y).ravel()
        self._gp.fit(X, y)
        self._fitted = True
        self._best_y = float(np.max(y))

    def predict(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Liefert (mean, std) — NIEMALS nur einen Punktwert.

        Siehe CLAUDE.md, Prinzip 1: jede Aussage braucht eine
        Unsicherheitsangabe, wenn sie keine direkte Messung ist.
        """
        if not self._fitted:
            raise RuntimeError("SurrogateModel muss vor predict() mit fit() trainiert werden.")
        X = np.atleast_2d(X)
        mean, std = self._gp.predict(X, return_std=True)
        return mean, std

    def suggest_next(self, bounds: list[tuple[float, float]], n: int = 1, n_candidates: int = 500,
                      random_state: int = 0) -> np.ndarray:
        """Schlaegt die naechsten `n` Experimentparameter per Expected Improvement vor.

        Phase-0-Implementierung: Zufalls-Sampling im Suchraum +
        Ranking nach Expected Improvement, statt eines vollen
        Gradienten-basierten Optimierers — ausreichend fuer niedrigdimensionale
        Materialparameterraeume (siehe Konzeptpapier Kapitel 5.1).
        """
        if not self._fitted:
            # Vor dem ersten Fit: gleichverteiltes Sampling (reine Exploration).
            rng = np.random.default_rng(random_state)
            return np.array([
                [rng.uniform(lo, hi) for lo, hi in bounds] for _ in range(n)
            ])

        rng = np.random.default_rng(random_state)
        candidates = np.array([
            [rng.uniform(lo, hi) for lo, hi in bounds] for _ in range(n_candidates)
        ])
        mean, std = self.predict(candidates)
        ei = _expected_improvement(mean, std, self._best_y)
        top_idx = np.argsort(ei)[::-1][:n]
        return candidates[top_idx]


def _expected_improvement(mean: np.ndarray, std: np.ndarray, best_y: float, xi: float = 0.01) -> np.ndarray:
    from scipy.stats import norm

    std = np.maximum(std, 1e-9)
    improvement = mean - best_y - xi
    z = improvement / std
    return improvement * norm.cdf(z) + std * norm.pdf(z)
