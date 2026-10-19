"""
Tests for UnitConverter (Sheet 12 'Unit Conversion Page').
"""

import pytest
from pytechtest.core.converters import UnitConverter


def test_mass_conversions():
    # 1 kg = 2.20462 lb
    lb = UnitConverter.kg_to_lb(10.0)
    assert abs(lb - 22.0462) < 0.01

    # 1 lb = 0.45359 kg
    kg = UnitConverter.lb_to_kg(lb)
    assert abs(kg - 10.0) < 1e-4

    # 1 metric ton = 1000 kg
    assert UnitConverter.metric_ton_to_kg(5.0) == 5000.0


def test_volume_conversions():
    # 1 gallon = 3.78541 liters
    liters = UnitConverter.gallon_to_liter(100.0)
    assert abs(liters - 378.541) < 0.01

    # 1 million gallons = 1,000,000 gallons
    assert UnitConverter.million_gallons_to_gallons(2.5) == 2_500_000.0


def test_energy_conversions():
    # 1 kWh = 0.003412 MMBtu
    mmbtu = UnitConverter.kwh_to_mmbtu(1000.0)
    assert abs(mmbtu - 3.41214) < 0.01

    # 1 MMBtu = 1,000,000 Btu
    assert UnitConverter.mmbtu_to_btu(1.5) == 1_500_000.0

    # 1 MJ to MMBtu
    mmbtu_from_mj = UnitConverter.mj_to_mmbtu(1055.056)
    assert abs(mmbtu_from_mj - 1.0) < 0.01


def test_emission_conversions():
    # 1 metric ton CO2 = 2204.62 lb CO2
    lb = UnitConverter.metric_ton_co2_to_lb(1.0)
    assert abs(lb - 2204.62) < 0.1

    t = UnitConverter.lb_co2_to_metric_ton(lb)
    assert abs(t - 1.0) < 1e-4
