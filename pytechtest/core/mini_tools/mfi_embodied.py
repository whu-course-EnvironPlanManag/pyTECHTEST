"""
NREL Materials Flow through Industry (MFI) Embodied Energy & Carbon Mini-Tool.
Matches US DOE TECHTEST 1.0 Sheet 20 ('MFI Embodied Energy Mini-Tool').
"""

import json
from pathlib import Path
from typing import Dict, Any, List

def _find_data_dir() -> Path:
    current = Path(__file__).resolve()
    for p in current.parents:
        cand = p / "data"
        if cand.exists() and (cand / "summary_ref_tables.json").exists():
            return cand
    return current.parents[2] / "data"

_DATA_DIR = _find_data_dir()

def load_mfi_config() -> Dict[str, Any]:
    path = _DATA_DIR / "mfi_factors.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

_MFI_CONFIG = load_mfi_config()


class MFIEmbodiedEnergyExtractor:
    """Extracts and computes embodied energy and cradle-to-gate carbon from MFI inventories."""

    def __init__(self):
        self.default_materials = _MFI_CONFIG.get("default_materials", {})
        self.default_multiplier = _MFI_CONFIG.get("default_energy_multiplier_btu_per_unit", 430.0)

    def lookup_material(self, material_key: str) -> Dict[str, float]:
        """Lookup standard material factors."""
        key = material_key.lower().replace(" ", "_").replace("-", "_")
        for k, v in self.default_materials.items():
            if k in key or key in k:
                return v
        return {"embodied_energy_btu_per_lb": 0.0, "embodied_ghg_lb_co2e_per_lb": 0.0}

    def compute_material_bundle(self, items: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Compute aggregate embodied metrics for a bundle of materials.
        Each item: {'name': str, 'quantity_lb': float, 'energy_factor_btu_per_lb': Optional[float], 'ghg_factor_lb_per_lb': Optional[float]}
        """
        total_energy_btu = 0.0
        total_ghg_lb = 0.0
        total_mass_lb = 0.0

        for item in items:
            qty = item.get("quantity_lb", 0.0)
            total_mass_lb += qty
            defaults = self.lookup_material(item.get("name", ""))
            e_fac = item.get("energy_factor_btu_per_lb", defaults.get("embodied_energy_btu_per_lb", 0.0))
            g_fac = item.get("ghg_factor_lb_per_lb", defaults.get("embodied_ghg_lb_co2e_per_lb", 0.0))
            
            total_energy_btu += qty * e_fac
            total_ghg_lb += qty * g_fac

        return {
            "total_mass_lb": total_mass_lb,
            "total_embodied_energy_btu": total_energy_btu,
            "total_embodied_energy_mmbtu": total_energy_btu / 1_000_000.0,
            "total_embodied_ghg_lb_co2e": total_ghg_lb,
            "weighted_energy_intensity_btu_per_lb": (total_energy_btu / total_mass_lb) if total_mass_lb > 0 else 0.0,
            "weighted_ghg_intensity_lb_per_lb": (total_ghg_lb / total_mass_lb) if total_mass_lb > 0 else 0.0
        }
