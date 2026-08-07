import numpy as np

from continuum.worldmodel.surrogate import SurrogateModel


def test_predict_returns_mean_and_std():
    model = SurrogateModel()
    X = np.array([[0.1, 0.2], [0.5, 0.5], [0.9, 0.8]])
    y = np.array([0.2, 0.6, 0.3])
    model.fit(X, y)

    mean, std = model.predict(np.array([[0.5, 0.5]]))
    assert mean.shape == (1,)
    assert std.shape == (1,)
    assert std[0] >= 0


def test_suggest_next_before_fit_is_exploration():
    model = SurrogateModel()
    bounds = [(0.0, 1.0), (0.0, 1.0)]
    suggestions = model.suggest_next(bounds, n=3)
    assert suggestions.shape == (3, 2)
    assert np.all(suggestions >= 0.0) and np.all(suggestions <= 1.0)


def test_suggest_next_after_fit():
    model = SurrogateModel()
    X = np.array([[0.1, 0.1], [0.9, 0.9], [0.5, 0.5]])
    y = np.array([0.1, 0.2, 0.8])
    model.fit(X, y)

    bounds = [(0.0, 1.0), (0.0, 1.0)]
    suggestions = model.suggest_next(bounds, n=2)
    assert suggestions.shape == (2, 2)
