"""
Tests for TechTestRapidEngine (Method 2: Sheets 16-18).
"""

import pytest
from pytechtest.engines.rapid_engine import TechTestRapidEngine
from pytechtest.core.types import TRLLevel
from pytechtest.models.project import ProjectMetadata, MarketDefinition, FunctionalUnitDefinition
from pytechtest.models.rapid_entry_input import RapidEntryInput, RapidTechCard


def test_rapid_engine_evaluation():
    proj = ProjectMetadata(
        title="Test Rapid Tech",
        lead_organization="Test Org",
        principal_investigator="Test PI",
        funding_mechanism="R&D",
        trl=TRLLevel.TRL_2
    )
    mkt = MarketDefinition(
        generic_end_use_product="Test Product",
        annual_us_market_volume=10000.0,
        market_units="kg",
        target_penetration_fraction=0.20
    )
    fu = FunctionalUnitDefinition(
        product_name_new_tech="Test Product",
        product_name_benchmark="Benchmark Product",
        reference_volume=10.0,
        reference_volume_unit="kg",
        equivalence_ratio=1.0
    )

    card_new = RapidTechCard(
        name="New Tech",
        product_name="Test Product",
        annual_facility_production=1000.0,
        total_initial_capex=50000.0,
        annualized_capex_with_maint=5000.0,
        annual_opex=10000.0,
        manufacturing_energy_mmbtu=2.0,
        raw_material_embodied_energy_mmbtu=3.0,
        in_use_energy_mmbtu=0.0,
        manufacturing_emissions_lb=150.0,
        raw_material_embodied_emissions_lb=250.0,
        in_use_emissions_lb=0.0
    )

    card_bench = RapidTechCard(
        name="Benchmark",
        product_name="Benchmark Product",
        annual_facility_production=1000.0,
        total_initial_capex=60000.0,
        annualized_capex_with_maint=6000.0,
        annual_opex=15000.0,
        manufacturing_energy_mmbtu=4.0,
        raw_material_embodied_energy_mmbtu=5.0,
        in_use_energy_mmbtu=0.0,
        manufacturing_emissions_lb=300.0,
        raw_material_embodied_emissions_lb=400.0,
        in_use_emissions_lb=0.0
    )

    rapid_input = RapidEntryInput(
        project=proj,
        market=mkt,
        functional_unit=fu,
        new_technology=card_new,
        commercial_benchmark=card_bench
    )

    engine = TechTestRapidEngine(rapid_input)
    results = engine.run()

    summary = results.summary
    assert summary.cost_savings_per_ref_volume > 0
    assert summary.energy_savings_per_ref_volume_mmbtu == 4.0  # (4+5) - (2+3) = 4.0
    assert summary.emissions_reduction_per_ref_volume_lb == 300.0  # (300+400) - (150+250) = 300.0
    assert summary.percent_cost_savings > 0
