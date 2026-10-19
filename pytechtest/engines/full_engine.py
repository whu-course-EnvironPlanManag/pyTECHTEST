"""
Method 1: Full Analytical Engine orchestrator.
Coordinates CapEx, OpEx, Materials, Energy, and Dashboard layers.
"""

from typing import Dict, Any, Union, Optional
from pathlib import Path
from pytechtest.models.full_entry_input import FullEntryInput, SubsystemConfig
from pytechtest.models.results import TechTestResults, DashboardSummary
from pytechtest.core.dashboard import TechnologyProfile, DashboardCalculator
from pytechtest.core.grid_mix import GridMixCalculator
from pytechtest.core.capex import CapExModel
from pytechtest.core.opex import OpExModel
from pytechtest.core.inventory import InventoryManager


class TechTestFullEngine:
    """Orchestrator for Method 1: Full Analytical Lifecycle Assessment & TEA."""

    def __init__(self, config: FullEntryInput):
        self.config = config
        self.grid_calc = GridMixCalculator(
            scenario=config.grid_scenario,
            custom_shares=config.custom_grid_shares
        )

    def _evaluate_subsystem(self,
                            sub: SubsystemConfig,
                            tech_name: str,
                            product_name: str,
                            ref_vol: Optional[float] = None) -> TechnologyProfile:
        if ref_vol is None:
            ref_vol = self.config.functional_unit.reference_volume
        fac_prod = sub.annual_facility_production

        # 1. CapEx
        capex_model = CapExModel(
            items=sub.capex_items,
            maintenance_rate=sub.capex_maintenance_rate,
            annual_facility_production=fac_prod,
            reference_production_volume=ref_vol
        )

        # 2. Inventory (Materials + Manufacturing Energy + In-Use)
        inv_manager = InventoryManager(
            materials=sub.materials,
            energy_items=sub.energy_items,
            in_use=sub.in_use,
            grid_calc=self.grid_calc,
            annual_facility_production=fac_prod,
            reference_production_volume=ref_vol
        )

        # 3. OpEx
        opex_model = OpExModel(
            labor=sub.labor,
            annual_material_cost=inv_manager.annual_material_cost,
            annual_energy_cost=inv_manager.annual_energy_cost,
            annual_maintenance_cost=capex_model.annual_maintenance_cost,
            annual_other_recurring=sub.other_recurring_opex,
            annual_facility_production=fac_prod,
            reference_production_volume=ref_vol
        )

        return TechnologyProfile(
            name=tech_name,
            product_name=product_name,
            reference_volume=ref_vol,
            reference_volume_unit=self.config.functional_unit.reference_volume_unit,
            facility_production_volume=fac_prod,
            capex_per_ref_volume=capex_model.capex_per_reference_volume,
            opex_per_ref_volume=opex_model.opex_per_reference_volume,
            direct_labor_per_ref_volume=opex_model.labor_cost_per_reference_volume,
            materials_cost_per_ref_volume=inv_manager.material_cost_per_ref_volume,
            energy_cost_per_ref_volume=inv_manager.energy_cost_per_ref_volume,
            maintenance_cost_per_ref_volume=capex_model.to_reference_volume(capex_model.annual_maintenance_cost),
            other_recurring_per_ref_volume=opex_model.to_reference_volume(sub.other_recurring_opex),
            total_initial_capex=capex_model.total_initial_purchase_cost,
            total_annual_opex=opex_model.total_annual_opex,
            manufacturing_energy_per_ref_volume_mmbtu=inv_manager.manufacturing_energy_consumption_per_ref_volume_mmbtu,
            raw_material_embodied_energy_mmbtu=inv_manager.material_embodied_energy_per_ref_volume_mmbtu,
            in_use_energy_per_ref_volume_mmbtu=sub.in_use.annual_energy_consumption_per_unit,
            manufacturing_emissions_per_ref_volume_lb=inv_manager.manufacturing_emissions_per_ref_volume_lb,
            raw_material_embodied_emissions_lb=inv_manager.material_embodied_ghg_per_ref_volume_lb,
            in_use_emissions_per_ref_volume_lb=0.0
        )

    def run(self) -> TechTestResults:
        """Execute full calculation graph and synthesize Results Dashboard."""
        ref_vol_new = self.config.functional_unit.reference_volume
        ref_vol_bench = ref_vol_new * self.config.functional_unit.equivalence_ratio

        profile_new = self._evaluate_subsystem(
            self.config.new_technology,
            tech_name="New Technology (Industrial Scale)",
            product_name=self.config.functional_unit.product_name_new_tech,
            ref_vol=ref_vol_new
        )
        profile_bench = self._evaluate_subsystem(
            self.config.commercial_benchmark,
            tech_name="Commercial Benchmark",
            product_name=self.config.functional_unit.product_name_benchmark,
            ref_vol=ref_vol_bench
        )

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
    def from_yaml(cls, path: Union[str, Path]) -> "TechTestFullEngine":
        """Convenience loader from YAML configuration."""
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        config = FullEntryInput(**data)
        return cls(config)
