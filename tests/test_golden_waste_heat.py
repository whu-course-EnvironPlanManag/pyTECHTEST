"""
Golden Test 1: US DOE Waste Heat Recovery Cooling in Beverage Manufacturing.
Tests numerical outputs against US DOE reference benchmarks.
"""

from pathlib import Path
import pytest
from pytechtest.engines.full_engine import TechTestFullEngine
from pytechtest.io.excel_loader import TechTestExcelLoader


def test_waste_heat_recovery_yaml(examples_dir: Path):
    yaml_path = examples_dir / "waste_heat_recovery.yaml"
    assert yaml_path.exists(), f"Missing {yaml_path}"

    engine = TechTestFullEngine.from_yaml(yaml_path)
    results = engine.run()

    summary = results.summary
    assert summary.cost_savings_per_ref_volume > 0.0
    assert summary.energy_savings_per_ref_volume_mmbtu > 0.0
    assert summary.emissions_reduction_per_ref_volume_lb > 0.0

    # Assert expected ranges
    assert 150.0 < summary.cost_savings_per_ref_volume < 250.0
    assert 5.0 < summary.energy_savings_per_ref_volume_mmbtu < 10.0
    assert 700.0 < summary.emissions_reduction_per_ref_volume_lb < 950.0


def test_waste_heat_recovery_excel(doe_excel_dir: Path):
    excel_path = doe_excel_dir / "Example TECHTEST 1.0 Waste Heat Recovery (Process).xlsx"
    if not excel_path.exists():
        pytest.skip("DOE Excel file not found on local path")

    loader = TechTestExcelLoader(excel_path)
    full_inp = loader.load_full_input()
    engine = TechTestFullEngine(full_inp)
    results = engine.run()

    summary = results.summary
    assert summary.cost_savings_per_ref_volume > 0.0
    assert summary.energy_savings_per_ref_volume_mmbtu > 0.0
    assert summary.emissions_reduction_per_ref_volume_lb > 0.0
