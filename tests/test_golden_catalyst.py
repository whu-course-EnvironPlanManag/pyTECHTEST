"""
Golden Test 2: US DOE Advanced Manufacturilium Catalyst.
Tests numerical outputs against official US DOE reference workbook benchmarks.
"""

from pathlib import Path
import pytest
from pytechtest.engines.full_engine import TechTestFullEngine
from pytechtest.io.excel_loader import TechTestExcelLoader


def test_manufacturilium_catalyst_yaml(examples_dir: Path):
    yaml_path = examples_dir / "manufacturilium_catalyst.yaml"
    assert yaml_path.exists(), f"Missing {yaml_path}"

    engine = TechTestFullEngine.from_yaml(yaml_path)
    results = engine.run()

    summary = results.summary
    # Cost savings: $581.50 / ref (19.92%)
    assert abs(summary.cost_savings_per_ref_volume - 581.50) < 2.0
    assert abs(summary.percent_cost_savings - 0.1992) < 0.01

    # Emissions reduction: 1329.90 lb CO2e / ref (74.82%)
    assert abs(summary.emissions_reduction_per_ref_volume_lb - 1329.90) < 2.0
    assert abs(summary.percent_emissions_reduction - 0.7482) < 0.01

    # Energy savings: 0.86 MMBtu / ref (39.05%)
    assert abs(summary.energy_savings_per_ref_volume_mmbtu - 0.86) < 0.05


def test_manufacturilium_catalyst_excel(doe_excel_dir: Path):
    excel_path = doe_excel_dir / "TECHTEST 1.0 Manufacturilium Catalyst.xlsx"
    if not excel_path.exists():
        pytest.skip("DOE Excel file not found on local path")

    loader = TechTestExcelLoader(excel_path)
    full_inp = loader.load_full_input()
    engine = TechTestFullEngine(full_inp)
    results = engine.run()

    summary = results.summary
    assert abs(summary.cost_savings_per_ref_volume - 581.50) < 2.0
    assert abs(summary.percent_cost_savings - 0.1992) < 0.01
    assert abs(summary.emissions_reduction_per_ref_volume_lb - 1329.90) < 2.0
    assert abs(summary.percent_emissions_reduction - 0.7482) < 0.01
