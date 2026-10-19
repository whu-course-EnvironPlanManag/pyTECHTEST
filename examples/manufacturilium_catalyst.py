#!/usr/bin/env python3
"""
Example 2: Advanced Manufacturilium Catalyst.
Golden benchmark reference matching US DOE TECHTEST 1.0 Manufacturilium Catalyst Workbook.
Demonstrates:
- Non-unity performance equivalence ratio (10 kg new tech replaces 13.5 kg benchmark)
- Raw material credit (-$500/ref volume credit)
- Multi-component capital equipment depreciation & maintenance
- Overnight national market penetration (70% market share)
"""

import sys
from pathlib import Path

# Support running directly without installation or git
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pytechtest import TechTestFullEngine, TechTestReporter


def main():
    yaml_path = Path(__file__).resolve().parent / "manufacturilium_catalyst.yaml"
    print(f"Loading Manufacturilium Catalyst model from: {yaml_path} ...")
    
    engine = TechTestFullEngine.from_yaml(yaml_path)
    results = engine.run()

    # Display professional terminal dashboard
    reporter = TechTestReporter()
    reporter.print_dashboard(results)

    # Validate against DOE Golden Benchmarks
    print("\n--- Validation against US DOE Official Workbook ---")
    summary = results.summary
    print(f"Cost Savings: ${summary.cost_savings_per_ref_volume:.2f}/ref ({summary.percent_cost_savings*100:.2f}%)")
    print(f"Energy Savings: {summary.energy_savings_per_ref_volume_mmbtu:.2f} MMBtu/ref ({summary.percent_energy_savings*100:.2f}%)")
    print(f"Emissions Reduction: {summary.emissions_reduction_per_ref_volume_lb:.2f} lb CO2e/ref ({summary.percent_emissions_reduction*100:.2f}%)")
    print(f"Annual US Market Cost Savings: ${summary.annual_potential_us_cost_savings:,.2f}/yr")
    print(f"Annual US Market Carbon Reduction: {summary.annual_potential_us_carbon_reduction_metric_tons:,.2f} t CO2e/yr")

    # Assert exact parity within rounding tolerances
    assert abs(summary.cost_savings_per_ref_volume - 581.50) < 1.0, f"Expected ~$581.50, got {summary.cost_savings_per_ref_volume}"
    assert abs(summary.emissions_reduction_per_ref_volume_lb - 1329.90) < 1.0, f"Expected ~1329.90 lb, got {summary.emissions_reduction_per_ref_volume_lb}"
    assert abs(summary.percent_emissions_reduction - 0.7482) < 0.01, f"Expected ~74.8% reduction, got {summary.percent_emissions_reduction}"
    print("✅ All US DOE Manufacturilium Catalyst benchmarks verified successfully!")


if __name__ == "__main__":
    main()
