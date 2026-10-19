#!/usr/bin/env python3
"""
Example 3: Method 2 Rapid Data Entry Assessment Demo.
Matches US DOE TECHTEST 1.0 Sheet 16-18 ('Rapid Data Entry Approach').
Ideal for early-stage screening (TRL 1-3) with aggregated cards.
"""

import sys
from pathlib import Path

# Support running directly without installation or git
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pytechtest import TechTestRapidEngine, TechTestReporter, TRLLevel
from pytechtest.models.project import ProjectMetadata, MarketDefinition, FunctionalUnitDefinition
from pytechtest.models.rapid_entry_input import RapidEntryInput, RapidTechCard


def main():
    print("Initializing US DOE TECHTEST Method 2 (Rapid Data Entry) Card Model ...")

    # 1. Project & Market Definition
    proj = ProjectMetadata(
        title="Rapid Screening of Bio-based Polymer Synthesis",
        lead_organization="Wuhan University Environmental Lab",
        principal_investigator="Dr. Siqi Tang",
        funding_mechanism="Early Stage R&D",
        trl=TRLLevel.TRL_2
    )
    
    mkt = MarketDefinition(
        generic_end_use_product="Bio-Polyester Film",
        annual_us_market_volume=500000.0,
        market_units="metric tons",
        target_penetration_fraction=0.15,
        market_description="Food packaging film replacement"
    )

    fu = FunctionalUnitDefinition(
        product_name_new_tech="Bio-Polyester Film",
        product_name_benchmark="Petrochemical PET Film",
        reference_volume=1.0,
        reference_volume_unit="metric ton",
        equivalence_ratio=1.0
    )

    # 2. Technology Cards (Method 2 inputs)
    card_new = RapidTechCard(
        name="Direct Enzymatic Polymerization (New Tech)",
        product_name="Bio-Polyester Film",
        annual_facility_production=10000.0,
        total_initial_capex=12000000.0,
        annualized_capex_with_maint=1800000.0,
        annual_opex=14000000.0,
        manufacturing_energy_mmbtu=15.0,
        raw_material_embodied_energy_mmbtu=22.0,
        in_use_energy_mmbtu=0.0,
        manufacturing_emissions_lb=1200.0,
        raw_material_embodied_emissions_lb=1800.0,
        in_use_emissions_lb=0.0
    )

    card_bench = RapidTechCard(
        name="Standard Fossil PET Polymerization (Benchmark)",
        product_name="Petrochemical PET Film",
        annual_facility_production=10000.0,
        total_initial_capex=15000000.0,
        annualized_capex_with_maint=2250000.0,
        annual_opex=16500000.0,
        manufacturing_energy_mmbtu=28.0,
        raw_material_embodied_energy_mmbtu=35.0,
        in_use_energy_mmbtu=0.0,
        manufacturing_emissions_lb=2400.0,
        raw_material_embodied_emissions_lb=3100.0,
        in_use_emissions_lb=0.0
    )

    # 3. Assemble and Run Rapid Engine
    rapid_input = RapidEntryInput(
        project=proj,
        market=mkt,
        functional_unit=fu,
        new_technology=card_new,
        commercial_benchmark=card_bench
    )

    engine = TechTestRapidEngine(rapid_input)
    results = engine.run()

    # 4. Display Results
    reporter = TechTestReporter()
    reporter.print_dashboard(results)

    print("\n--- Method 2 Rapid Assessment Verified ---")
    s = results.summary
    print(f"Cost Savings: ${s.cost_savings_per_ref_volume:.2f}/ton ({s.percent_cost_savings*100:.2f}%)")
    print(f"Energy Savings: {s.energy_savings_per_ref_volume_mmbtu:.2f} MMBtu/ton ({s.percent_energy_savings*100:.2f}%)")
    print(f"Emissions Reduction: {s.emissions_reduction_per_ref_volume_lb:.2f} lb/ton ({s.percent_emissions_reduction*100:.2f}%)")
    print(f"Annual US Potential Savings: ${s.annual_potential_us_cost_savings:,.2f}/yr")
    print("✅ Method 2 Rapid Data Entry workflow successfully validated!")


if __name__ == "__main__":
    main()
