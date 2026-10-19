"""
Decision Dashboard and Summary Tables Engine matching US DOE TECHTEST 1.0 Sheets 14 & 15.
Calculates Cradle-to-Gate comparative indicators, cost/energy/carbon savings, and payback period.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class TechnologyProfile(BaseModel):
    """Aggregate profile for one technology (New Tech or Commercial Benchmark)."""
    name: str
    product_name: str
    reference_volume: float = 1.0
    reference_volume_unit: str = "Million Gallons"
    facility_production_volume: float = 1.0
    
    # Cost per reference volume ($)
    capex_per_ref_volume: float = 0.0
    opex_per_ref_volume: float = 0.0
    direct_labor_per_ref_volume: float = 0.0
    materials_cost_per_ref_volume: float = 0.0
    energy_cost_per_ref_volume: float = 0.0
    maintenance_cost_per_ref_volume: float = 0.0
    other_recurring_per_ref_volume: float = 0.0

    # Total initial equipment purchase cost (un-depreciated, for payback calculation)
    total_initial_capex: float = 0.0
    total_annual_opex: float = 0.0

    # Energy per reference volume (MMBtu)
    manufacturing_energy_per_ref_volume_mmbtu: float = 0.0
    raw_material_embodied_energy_mmbtu: float = 0.0
    in_use_energy_per_ref_volume_mmbtu: float = 0.0

    # Emissions per reference volume (lb CO2e)
    manufacturing_emissions_per_ref_volume_lb: float = 0.0
    raw_material_embodied_emissions_lb: float = 0.0
    in_use_emissions_per_ref_volume_lb: float = 0.0

    @property
    def total_cost_per_reference_volume(self) -> float:
        """Cradle-to-gate total manufacturing cost per reference volume ($)."""
        return self.capex_per_ref_volume + self.opex_per_ref_volume

    @property
    def total_energy_per_reference_volume_mmbtu(self) -> float:
        """Cradle-to-gate primary energy per reference volume (MMBtu)."""
        return (self.manufacturing_energy_per_ref_volume_mmbtu +
                self.raw_material_embodied_energy_mmbtu +
                self.in_use_energy_per_ref_volume_mmbtu)

    @property
    def total_emissions_per_reference_volume_lb(self) -> float:
        """Cradle-to-gate GHG emissions per reference volume (lb CO2e)."""
        return (self.manufacturing_emissions_per_ref_volume_lb +
                self.raw_material_embodied_emissions_lb +
                self.in_use_emissions_per_ref_volume_lb)

    @property
    def total_emissions_per_reference_volume_metric_tons(self) -> float:
        """Cradle-to-gate GHG emissions per reference volume (metric tons CO2e)."""
        return (self.total_emissions_per_reference_volume_lb * 0.45359237) / 1000.0


class DashboardCalculator:
    """Synthesizes comparative metrics, savings, and nationwide market scaling."""

    def __init__(self,
                 new_tech: TechnologyProfile,
                 benchmark: TechnologyProfile,
                 annual_us_market_volume: float = 0.0,
                 market_penetration_fraction: float = 1.0):
        self.new_tech = new_tech
        self.benchmark = benchmark
        self.annual_us_market_volume = annual_us_market_volume
        self.market_penetration_fraction = market_penetration_fraction

    # --- Unit / Reference Volume Differences ---
    @property
    def cost_savings_per_ref_volume(self) -> float:
        """Dollar savings per reference volume ($): Benchmark - NewTech."""
        return self.benchmark.total_cost_per_reference_volume - self.new_tech.total_cost_per_reference_volume

    @property
    def percent_cost_savings(self) -> float:
        """Relative cost reduction per unit of production replaced."""
        base = self.benchmark.total_cost_per_reference_volume
        return (self.cost_savings_per_ref_volume / base) if base > 1e-9 else 0.0

    @property
    def energy_savings_per_ref_volume_mmbtu(self) -> float:
        """Energy reduction per reference volume (MMBtu): Benchmark - NewTech."""
        return self.benchmark.total_energy_per_reference_volume_mmbtu - self.new_tech.total_energy_per_reference_volume_mmbtu

    @property
    def percent_energy_savings(self) -> float:
        base = self.benchmark.total_energy_per_reference_volume_mmbtu
        return (self.energy_savings_per_ref_volume_mmbtu / base) if base > 1e-9 else 0.0

    @property
    def emissions_reduction_per_ref_volume_lb(self) -> float:
        """GHG emissions reduction per reference volume (lb CO2e): Benchmark - NewTech."""
        return self.benchmark.total_emissions_per_reference_volume_lb - self.new_tech.total_emissions_per_reference_volume_lb

    @property
    def percent_emissions_reduction(self) -> float:
        base = self.benchmark.total_emissions_per_reference_volume_lb
        return (self.emissions_reduction_per_ref_volume_lb / base) if base > 1e-9 else 0.0

    # --- Payback Period ---
    @property
    def simple_payback_years(self) -> Optional[float]:
        """
        Static investment payback period (years) = Delta CapEx / Annual OpEx Savings.
        Matches Lecture 7 Slide 27: 450,000 / 120,000 = 3.75 years.
        """
        delta_capex = self.new_tech.total_initial_capex - self.benchmark.total_initial_capex
        annual_opex_savings = self.benchmark.total_annual_opex - self.new_tech.total_annual_opex
        if annual_opex_savings > 1e-6:
            return delta_capex / annual_opex_savings
        return None

    # --- National US Market Scaling (Sheet 5 & 15) ---
    @property
    def annual_addressable_market_volume(self) -> float:
        return self.annual_us_market_volume * self.market_penetration_fraction

    @property
    def national_market_scale_multiplier(self) -> float:
        ref_vol = self.new_tech.reference_volume
        if ref_vol <= 1e-9:
            return 0.0
        return self.annual_addressable_market_volume / ref_vol

    @property
    def annual_potential_us_cost_savings(self) -> float:
        """Annual potential cost savings to US manufacturers ($/year)."""
        return self.cost_savings_per_ref_volume * self.national_market_scale_multiplier

    @property
    def annual_potential_us_energy_savings_mmbtu(self) -> float:
        """Annual potential energy savings across US market (MMBtu/year)."""
        return self.energy_savings_per_ref_volume_mmbtu * self.national_market_scale_multiplier

    @property
    def annual_potential_us_carbon_reduction_metric_tons(self) -> float:
        """Annual potential GHG emissions reduction (metric tons CO2e/year)."""
        reduction_tons_per_ref = (self.emissions_reduction_per_ref_volume_lb * 0.45359237) / 1000.0
        return reduction_tons_per_ref * self.national_market_scale_multiplier
