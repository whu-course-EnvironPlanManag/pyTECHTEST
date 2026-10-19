#!/usr/bin/env python3
"""
Example 1: Waste Heat Recovery Cooling in Beverage Manufacturing.
Golden benchmark reference matching US DOE TECHTEST 1.0 Example Workbook.
"""

import sys
from pathlib import Path

# Support running directly without installation or git
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pytechtest import TechTestFullEngine, TechTestReporter


def main():
    yaml_path = Path(__file__).resolve().parent / "waste_heat_recovery.yaml"
    print(f"Loading Waste Heat Recovery model from: {yaml_path} ...")
    
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
    print(f"Simple Payback Period: {summary.simple_payback_years:.2f} years")

    assert summary.cost_savings_per_ref_volume > 0, "Cost savings should be positive"
    assert summary.energy_savings_per_ref_volume_mmbtu > 0, "Energy savings should be positive"
    assert summary.emissions_reduction_per_ref_volume_lb > 0, "Emissions reduction should be positive"
    print("✅ All US DOE Waste Heat Recovery benchmarks verified successfully!")


if __name__ == "__main__":
    main()
