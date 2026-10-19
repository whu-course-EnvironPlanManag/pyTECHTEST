"""
Method 2: Rapid Data Entry Engine orchestrator.
Matches US DOE TECHTEST 1.0 Sheet 16, 17, and 18 ('Rapid Data Entry Approach').
"""

from typing import Union
from pathlib import Path
from pytechtest.models.rapid_entry_input import RapidEntryInput, RapidTechCard
from pytechtest.models.results import TechTestResults, DashboardSummary
from pytechtest.core.dashboard import TechnologyProfile, DashboardCalculator


class TechTestRapidEngine:
    """Orchestrator for Method 2: Rapid Data Entry Assessment."""

    def __init__(self, config: RapidEntryInput):
        self.config = config

    def _convert_card_to_profile(self, card: RapidTechCard, is_benchmark: bool = False) -> TechnologyProfile:
        ref_vol = self.config.functional_unit.reference_volume
        if is_benchmark:
            ref_vol = ref_vol * self.config.functional_unit.equivalence_ratio
        fac_prod = card.annual_facility_production
        scale_to_ref = ref_vol / fac_prod

        # Scale annual CapEx & OpEx to reference volume
        capex_per_ref = card.annualized_capex_with_maint * scale_to_ref
        opex_per_ref = card.annual_opex * scale_to_ref

        # Per ref volume indicators (scaled by equivalence ratio for benchmark)
        scale_factor = self.config.functional_unit.equivalence_ratio if is_benchmark else 1.0

        return TechnologyProfile(
            name=card.name,
            product_name=card.product_name,
            reference_volume=ref_vol,
            reference_volume_unit=self.config.functional_unit.reference_volume_unit,
            facility_production_volume=fac_prod,
            capex_per_ref_volume=capex_per_ref,
            opex_per_ref_volume=opex_per_ref,
            total_initial_capex=card.total_initial_capex,
            total_annual_opex=card.annual_opex,
            manufacturing_energy_per_ref_volume_mmbtu=card.manufacturing_energy_mmbtu * scale_factor,
            raw_material_embodied_energy_mmbtu=card.raw_material_embodied_energy_mmbtu * scale_factor,
            in_use_energy_per_ref_volume_mmbtu=card.in_use_energy_mmbtu * scale_factor,
            manufacturing_emissions_per_ref_volume_lb=card.manufacturing_emissions_lb * scale_factor,
            raw_material_embodied_emissions_lb=card.raw_material_embodied_emissions_lb * scale_factor,
            in_use_emissions_per_ref_volume_lb=card.in_use_emissions_lb * scale_factor
        )

    def run(self) -> TechTestResults:
        """Run rapid comparative assessment and synthesize dashboard."""
        profile_new = self._convert_card_to_profile(self.config.new_technology, is_benchmark=False)
        profile_bench = self._convert_card_to_profile(self.config.commercial_benchmark, is_benchmark=True)

        dashboard = DashboardCalculator(
            new_tech=profile_new,
            benchmark=profile_bench,
            annual_us_market_volume=self.config.market.annual_us_market_volume,
            market_penetration_fraction=self.config.market.target_penetration_fraction
        )

        summary = DashboardSummary(
            cost_savings_per_ref_volume=dashboard.cost_savings_per_ref_volume,
            percent_cost_savings=dashboard.percent_cost_savings,
            energy_savings_per_ref_volume_mmbtu=dashboard.energy_savings_per_ref_volume_mmbtu,
            percent_energy_savings=dashboard.percent_energy_savings,
            emissions_reduction_per_ref_volume_lb=dashboard.emissions_reduction_per_ref_volume_lb,
            percent_emissions_reduction=dashboard.percent_emissions_reduction,
            simple_payback_years=dashboard.simple_payback_years,
            annual_potential_us_cost_savings=dashboard.annual_potential_us_cost_savings,
            annual_potential_us_energy_savings_mmbtu=dashboard.annual_potential_us_energy_savings_mmbtu,
            annual_potential_us_carbon_reduction_metric_tons=dashboard.annual_potential_us_carbon_reduction_metric_tons
        )

        return TechTestResults(
            project=self.config.project,
            market=self.config.market,
            functional_unit=self.config.functional_unit,
            new_technology=profile_new,
            commercial_benchmark=profile_bench,
            summary=summary
        )

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> "TechTestRapidEngine":
        """Convenience loader from YAML configuration."""
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        config = RapidEntryInput(**data)
        return cls(config)
