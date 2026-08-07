from continuum.data.simulated_materials import SimulatedLab


def test_run_experiment_near_optimum_is_high():
    lab = SimulatedLab(seed=1, noise_std=0.0)
    result = lab.run_experiment({"dopant_fraction": 0.3, "sinter_temp_c": 0.7})
    assert result.ionic_conductivity > 0.9


def test_run_experiment_far_from_optimum_is_low():
    lab = SimulatedLab(seed=1, noise_std=0.0)
    result = lab.run_experiment({"dopant_fraction": 0.0, "sinter_temp_c": 0.0})
    assert result.ionic_conductivity < 0.1


def test_result_is_never_negative():
    lab = SimulatedLab(seed=2, noise_std=0.5)
    for _ in range(20):
        result = lab.run_experiment({"dopant_fraction": 0.1, "sinter_temp_c": 0.1})
        assert result.ionic_conductivity >= 0.0
