from continuum.eval.metrics import (
    calibration_curve,
    efficiency,
    forgetting_rate,
    governance_compliance,
    memory_quality,
    task_effectiveness,
)


def test_task_effectiveness():
    records = [
        {"tested": True, "confirmed": True},
        {"tested": True, "confirmed": False},
        {"tested": False, "confirmed": False},
    ]
    report = task_effectiveness(records)
    assert report.n_hypotheses_tested == 2
    assert report.n_confirmed == 1
    assert report.hit_rate == 0.5


def test_memory_quality_precision():
    report = memory_quality(["a", "b", "c"], ["a", "c"])
    assert report.precision_at_k == 2 / 3


def test_efficiency():
    run_log = [
        {"cost": 10.0, "latency_ms": 100, "validated": True},
        {"cost": 5.0, "latency_ms": 50, "validated": False},
    ]
    report = efficiency(run_log)
    assert report.cost_per_validated_hypothesis == 15.0
    assert report.mean_latency_ms == 75.0


def test_governance_compliance_full_coverage():
    events = [{"timestamp": 1.0, "event": "x"}, {"timestamp": 2.0, "event": "y"}]
    report = governance_compliance(events)
    assert report.audit_coverage == 1.0


def test_calibration_curve():
    predictions = [(0.5, 0.1), (0.8, 0.05)]
    outcomes = [0.52, 0.9]
    report = calibration_curve(predictions, outcomes)
    assert report.mean_absolute_error > 0
    assert 0.0 <= report.within_uncertainty_band_fraction <= 1.0


def test_forgetting_rate():
    rate = forgetting_rate([1.0, 1.0], [0.9, 0.9])
    assert abs(rate - 0.1) < 1e-9
