"""
Tests for Mini-Tools:
- Harry Silla Labor Estimation (Sheet 21)
- NREL MFI Embodied Energy (Sheet 20)
- Cost Comparison Tool (Sheet 19)
"""

import pytest
from pytechtest.core.types import ProcessType
from pytechtest.core.mini_tools.silla_labor import SillaLaborEstimator
from pytechtest.core.mini_tools.mfi_embodied import MFIEmbodiedEnergyExtractor
from pytechtest.core.mini_tools.cost_comparison import CostComparisonTool, CostBreakdown


def test_silla_labor_estimator():
    # Example: 10,000,000 lb/yr, 5 process units, continuous automated plant
    estimator = SillaLaborEstimator(
        annual_production_lb=10_000_000.0,
        process_units_N=5,
        process_type=ProcessType.CONTINUOUS_AUTOMATED,
        hours_of_operation_per_year=8000.0,
        average_annual_salary=80000.0
    )

    fte = estimator.total_fte_requirement
    assert fte > 0.0

    annual_cost = estimator.annual_total_labor_cost
    assert annual_cost > 0.0

    # Test supervision overhead is 20%
    assert estimator.supervision_labor_hours == estimator.operating_labor_hours * 0.20


def test_mfi_embodied_extractor():
    extractor = MFIEmbodiedEnergyExtractor()
    steel = extractor.lookup_material("steel")
    assert steel.get("embodied_energy_btu_per_lb", 0) > 0

    bundle = [
        {"name": "steel", "quantity_lb": 1000.0},
        {"name": "aluminum", "quantity_lb": 500.0}
    ]
    res = extractor.compute_material_bundle(bundle)
    assert res["total_mass_lb"] == 1500.0
    assert res["total_embodied_energy_mmbtu"] > 0.0
    assert res["total_embodied_ghg_lb_co2e"] > 0.0


def test_cost_comparison_tool():
    new_tech = CostBreakdown(
        manufacturing_energy=10.0,
        raw_materials=50.0,
        annualized_capex_with_maint=20.0,
        direct_labor=15.0,
        other_recurring_opex=5.0
    )
    benchmark = CostBreakdown(
        manufacturing_energy=18.0,
        raw_materials=65.0,
        annualized_capex_with_maint=30.0,
        direct_labor=20.0,
        other_recurring_opex=7.0
    )

    tool = CostComparisonTool(new_tech=new_tech, benchmark=benchmark)
    # Benchmark = 140, New Tech = 100
    assert tool.benchmark.total_manufacturing_cost == 140.0
    assert tool.new_tech.total_manufacturing_cost == 100.0
    assert tool.total_cost_savings == 40.0
    assert abs(tool.percent_cost_savings - (40.0 / 140.0)) < 1e-4

    cat_savings = tool.category_savings()
    assert cat_savings["manufacturing_energy"]["dollar_savings"] == 8.0
    assert cat_savings["raw_materials"]["dollar_savings"] == 15.0
