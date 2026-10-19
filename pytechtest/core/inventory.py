"""
Raw Materials, Manufacturing Energy, and In-Use Energy Inventory Engine.
Matches US DOE TECHTEST 1.0 Sheets 7 ('Raw Materials'), 8 ('Manufacturing Energy'), and 9 ('Use Phase Energy').
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from pytechtest.core.types import MaterialItem, EnergyItem, InUseItem
from pytechtest.core.grid_mix import GridMixCalculator

def _find_data_dir() -> Path:
    current = Path(__file__).resolve()
    for p in current.parents:
        cand = p / "data"
        if cand.exists() and (cand / "summary_ref_tables.json").exists():
            return cand
    return current.parents[2] / "data"

_DATA_DIR = _find_data_dir()

def load_summary_ref_tables() -> List[Dict]:
    path = _DATA_DIR / "summary_ref_tables.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("energy_sources", [])
    return []

_SUMMARY_REF = load_summary_ref_tables()


class InventoryManager:
    """Calculates cradle-to-gate inventory for materials and energy."""

    def __init__(self,
                 materials: Optional[List[MaterialItem]] = None,
                 energy_items: Optional[List[EnergyItem]] = None,
                 in_use: Optional[InUseItem] = None,
                 grid_calc: Optional[GridMixCalculator] = None,
                 annual_facility_production: float = 1.0,
                 reference_production_volume: float = 1.0):
        self.materials = materials or []
        self.energy_items = energy_items or []
        self.in_use = in_use or InUseItem()
        self.grid_calc = grid_calc or GridMixCalculator()
        self.annual_facility_production = max(1e-9, annual_facility_production)
        self.reference_production_volume = reference_production_volume

    # --- Raw Materials Calculations (Sheet 7) ---
    @property
    def material_cost_per_ref_volume(self) -> float:
        """Total raw materials cost per reference volume ($)."""
        tot = 0.0
        for m in self.materials:
            effective_qty = m.amount_per_ref_volume * (1.0 + m.scrap_fraction)
            tot += effective_qty * m.unit_price
        return tot

    @property
    def material_embodied_energy_per_ref_volume_mmbtu(self) -> float:
        """Embodied energy from raw materials per ref volume (in MMBtu)."""
        tot_btu = 0.0
        for m in self.materials:
            effective_qty = m.amount_per_ref_volume * (1.0 + m.scrap_fraction)
            tot_btu += effective_qty * m.embodied_energy_factor
        return tot_btu / 1_000_000.0  # Convert Btu to MMBtu

    @property
    def material_embodied_ghg_per_ref_volume_lb(self) -> float:
        """Embodied cradle-to-gate GHG emissions from materials per ref volume (lb CO2e)."""
        tot_lb = 0.0
        for m in self.materials:
            effective_qty = m.amount_per_ref_volume * (1.0 + m.scrap_fraction)
            tot_lb += effective_qty * m.embodied_ghg_factor
        return tot_lb

    # --- Manufacturing Energy Calculations (Sheet 8) ---
    def _get_energy_defaults(self, source_name: str) -> Tuple[float, float, float]:
        """Lookup (price_per_physical_unit, heat_content_mmbtu_per_unit, gwp_lb_per_unit)."""
        # Check if electricity
        if "electr" in source_name.lower():
            # Price default ~0.0718 $/kWh, heat ~0.003412 MMBtu/kWh
            gwp_lb_kwh = self.grid_calc.compute_weighted_emission_factor_lb_per_kwh()
            return (0.0718, 0.003412142, gwp_lb_kwh)
        
        # Check against EIA summary ref tables
        for row in _SUMMARY_REF:
            if row["energy_source"].lower() in source_name.lower() or source_name.lower() in row["energy_source"].lower():
                return (
                    row["price_dollar_per_physical_unit"],
                    row["heat_content_mmbtu_per_unit"],
                    row["gwp_lb_co2e_per_physical_unit"]
                )
        # Fallback default: 0
        return (0.0, 1.0, 0.0)

    @property
    def energy_cost_per_ref_volume(self) -> float:
        """Manufacturing process energy cost per reference volume ($)."""
        tot = 0.0
        for item in self.energy_items:
            default_p, _, _ = self._get_energy_defaults(item.energy_source)
            price = item.unit_price if item.unit_price is not None else default_p
            tot += item.amount_per_ref_volume * price
        return tot

    @property
    def manufacturing_energy_consumption_per_ref_volume_mmbtu(self) -> float:
        """Process energy consumption in MMBtu per reference volume."""
        tot = 0.0
        for item in self.energy_items:
            _, heat_content, _ = self._get_energy_defaults(item.energy_source)
            tot += item.amount_per_ref_volume * heat_content
        return tot

    @property
    def manufacturing_emissions_per_ref_volume_lb(self) -> float:
        """Process direct + indirect GHG emissions in lb CO2e per reference volume."""
        tot = 0.0
        for item in self.energy_items:
            _, _, default_gwp = self._get_energy_defaults(item.energy_source)
            ef = item.custom_emission_factor if item.custom_emission_factor is not None else default_gwp
            tot += item.amount_per_ref_volume * ef
        return tot

    # --- Annual Facility Roll-up Helpers ---
    def to_annual_facility(self, val_per_ref_volume: float) -> float:
        """Scale per reference volume value up to annual facility production."""
        return val_per_ref_volume * (self.annual_facility_production / self.reference_production_volume)

    @property
    def annual_material_cost(self) -> float:
        return self.to_annual_facility(self.material_cost_per_ref_volume)

    @property
    def annual_energy_cost(self) -> float:
        return self.to_annual_facility(self.energy_cost_per_ref_volume)
