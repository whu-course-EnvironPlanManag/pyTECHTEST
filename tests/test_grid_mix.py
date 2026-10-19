"""
Tests for GridMixCalculator (Sheet 13 & 24).
"""

import pytest
from pytechtest.core.grid_mix import GridMixCalculator
from pytechtest.core.types import GridScenario


def test_baseline_2022_grid():
    calc = GridMixCalculator(scenario=GridScenario.BASELINE_2022)
    shares = calc.get_shares()
    assert abs(sum(shares.values()) - 1.0) < 1e-4

    ef_mmbtu = calc.compute_weighted_emission_factor_lb_per_mmbtu()
    # Baseline 2022 US Grid is around ~108.59 lb CO2e / MMBtu
    assert 90.0 < ef_mmbtu < 130.0

    ef_kwh = calc.compute_weighted_emission_factor_lb_per_kwh()
    assert 0.2 < ef_kwh < 0.6


def test_net_zero_grid():
    calc = GridMixCalculator(scenario=GridScenario.NET_ZERO)
    ef_mmbtu = calc.compute_weighted_emission_factor_lb_per_mmbtu()
    # Net zero scenario should have significantly lower emissions than baseline
    calc_base = GridMixCalculator(scenario=GridScenario.BASELINE_2022)
    assert ef_mmbtu < calc_base.compute_weighted_emission_factor_lb_per_mmbtu()


def test_custom_grid_mix():
    # 100% Solar
    custom = {
        "Coal": 0.0,
        "Natural Gas": 0.0,
        "Petroleum": 0.0,
        "Nuclear": 0.0,
        "Hydroelectric": 0.0,
        "Wind": 0.0,
        "Solar": 1.0,
        "Geothermal": 0.0,
        "Biomass": 0.0,
        "Other": 0.0
    }
    calc = GridMixCalculator(scenario=GridScenario.CUSTOM, custom_shares=custom)
    ef_mmbtu = calc.compute_weighted_emission_factor_lb_per_mmbtu()
    assert ef_mmbtu == calc.emission_factors.get("Solar", 0.0)
