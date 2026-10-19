"""
Grid Mix Customization Engine matching US DOE TECHTEST 1.0 Sheet 13 & Sheet 24.
Computes weighted life-cycle greenhouse gas emission intensity for electric power.
"""

import json
from pathlib import Path
from typing import Dict, Optional
from pytechtest.core.types import GridScenario

def _find_data_dir() -> Path:
    current = Path(__file__).resolve()
    for p in current.parents:
        cand = p / "data"
        if cand.exists() and (cand / "summary_ref_tables.json").exists():
            return cand
    return current.parents[2] / "data"

_DATA_DIR = _find_data_dir()

def load_grid_data() -> Dict:
    path = _DATA_DIR / "grid_mix_scenarios.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"scenarios": {}, "emission_factors_lb_co2e_per_mmbtu": {}}

_GRID_CONFIG = load_grid_data()


class GridMixCalculator:
    """Calculates weighted grid carbon intensity across official or custom scenarios."""

    def __init__(self, scenario: GridScenario = GridScenario.BASELINE_2022, custom_shares: Optional[Dict[str, float]] = None):
        self.scenario = scenario
        self.custom_shares = custom_shares or {}
        self.emission_factors = _GRID_CONFIG.get("emission_factors_lb_co2e_per_mmbtu", {})
        self.scenarios = _GRID_CONFIG.get("scenarios", {})

    def get_shares(self) -> Dict[str, float]:
        """Return the source shares for the selected scenario."""
        if self.scenario == GridScenario.CUSTOM:
            if not self.custom_shares:
                # Fallback to 2022 default if custom not provided
                return {k: v["share"] for k, v in self.scenarios.get("2022_default", {}).items()}
            # Normalize custom shares to sum to 1.0
            tot = sum(self.custom_shares.values())
            if tot > 0:
                return {k: v / tot for k, v in self.custom_shares.items()}
            return self.custom_shares
        
        scen_key = self.scenario.value
        scen_dict = self.scenarios.get(scen_key, self.scenarios.get("2022_default", {}))
        return {k: v["share"] for k, v in scen_dict.items()}

    def compute_weighted_emission_factor_lb_per_mmbtu(self) -> float:
        """
        Calculate weighted average emissions intensity in lb CO2-eq / MMBtu.
        Matches Excel formula in Sheet 13 / Sheet 24.
        """
        shares = self.get_shares()
        weighted_sum = 0.0
        for source, share in shares.items():
            ef = self.emission_factors.get(source, 0.0)
            weighted_sum += share * ef
        return weighted_sum

    def compute_weighted_emission_factor_lb_per_kwh(self) -> float:
        """Calculate weighted average emissions intensity in lb CO2-eq / kWh."""
        # 1 MMBtu = 293.07107 kWh -> 1 kWh = 0.003412142 MMBtu
        return self.compute_weighted_emission_factor_lb_per_mmbtu() * 0.003412142

    def compute_weighted_emission_factor_kg_per_kwh(self) -> float:
        """Calculate weighted average emissions intensity in kg CO2-eq / kWh."""
        return self.compute_weighted_emission_factor_lb_per_kwh() * 0.45359237
