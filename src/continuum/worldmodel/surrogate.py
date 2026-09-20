"""A Bayesian surrogate model for the perception/world-model layer.

See ARCHITECTURE.md, section 4, and the concept paper chapter 5.1. Deliberately
NO attempt to solve the general (unsolved) problem of intuitive physics —
instead a narrowly scoped, tractable regression task:
synthesis parameters -> material property, with explicit
uncertainty estimation.
"""

from __future__ import annotations

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel


class SurrogateModel:
    """Gaussian-process regression with expected-improvement acquisition.

    Usage:
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
        """Returns (mean, std) — NEVER only a point value.

        See CLAUDE.md, principle 1: every statement needs an
        uncertainty estimate if it is not a direct measurement.
        """
        if not self._fitted:
            raise RuntimeError("SurrogateModel must be trained with fit() before predict().")
        X = np.atleast_2d(X)
        mean, std = self._gp.predict(X, return_std=True)
        return mean, std

    def suggest_next(self, bounds: list[tuple[float, float]], n: int = 1, n_candidates: int = 500,
                      random_state: int = 0) -> np.ndarray:
        """Suggests the next `n` experiment parameters via expected improvement.

        Phase-0 implementation: random sampling in the search space +
        ranking by expected improvement, instead of a full
        gradient-based optimizer — sufficient for low-dimensional
        material-parameter spaces (see the concept paper chapter 5.1).
        """
        if not self._fitted:
            # Before the first fit: uniform sampling (pure exploration).
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
