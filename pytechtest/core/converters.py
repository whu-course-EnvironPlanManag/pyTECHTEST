"""
Unit Conversion Engine matching US DOE TECHTEST 1.0 Sheet 12 ('Unit Conversion Page').
Provides exact dimensional conversions across Metric and Imperial standards.
"""

import json
from pathlib import Path
from typing import Dict, Any

def _find_data_dir() -> Path:
    current = Path(__file__).resolve()
    for p in current.parents:
        cand = p / "data"
        if cand.exists() and (cand / "summary_ref_tables.json").exists():
            return cand
    return current.parents[2] / "data"

_DATA_DIR = _find_data_dir()

def load_conversion_factors() -> Dict[str, float]:
    path = _DATA_DIR / "conversion_factors.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

_FACTORS = load_conversion_factors()


class UnitConverter:
    """Universal Unit Converter matching TECHTEST Sheet 12 formulas."""

    # Mass Conversions
    @staticmethod
    def lb_to_kg(val: float) -> float:
        return val * _FACTORS.get("lb_to_kg", 0.45359237)

    @staticmethod
    def kg_to_lb(val: float) -> float:
        return val * _FACTORS.get("kg_to_lb", 2.20462262)

    @staticmethod
    def metric_ton_to_kg(val: float) -> float:
        return val * 1000.0

    @staticmethod
    def us_short_ton_to_kg(val: float) -> float:
        return val * _FACTORS.get("ton_us_short_to_kg", 907.18474)

    # Volume Conversions
    @staticmethod
    def gallon_to_liter(val: float) -> float:
        return val * _FACTORS.get("gallon_to_liter", 3.785411784)

    @staticmethod
    def liter_to_gallon(val: float) -> float:
        return val * _FACTORS.get("liter_to_gallon", 0.264172052)

    @staticmethod
    def million_gallons_to_gallons(val: float) -> float:
        return val * 1_000_000.0

    # Energy Conversions
    @staticmethod
    def kwh_to_mmbtu(val: float) -> float:
        return val * _FACTORS.get("kwh_to_mmbtu", 0.003412142)

    @staticmethod
    def mmbtu_to_kwh(val: float) -> float:
        return val * _FACTORS.get("mmbtu_to_kwh", 293.07107)

    @staticmethod
    def mmbtu_to_gj(val: float) -> float:
        return val * _FACTORS.get("mmbtu_to_gj", 1.05505585)

    @staticmethod
    def gj_to_mmbtu(val: float) -> float:
        return val * _FACTORS.get("gj_to_mmbtu", 0.94781712)

    @staticmethod
    def kwh_to_mj(val: float) -> float:
        return val * 3.6

    @staticmethod
    def mj_to_kwh(val: float) -> float:
        return val / 3.6

    @staticmethod
    def mmbtu_to_btu(val: float) -> float:
        return val * 1_000_000.0

    @staticmethod
    def btu_to_mmbtu(val: float) -> float:
        return val / 1_000_000.0

    @staticmethod
    def mj_to_mmbtu(val: float) -> float:
        return val * _FACTORS.get("mj_to_mmbtu", 0.000947817)

    @staticmethod
    def metric_ton_co2_to_lb(val: float) -> float:
        return val * 2204.62262

    @staticmethod
    def lb_co2_to_metric_ton(val: float) -> float:
        return val / 2204.62262

    # Emission Intensity Factors (Dropdown Sheet 25 & Sheet 12)
    @staticmethod
    def lb_co2_per_mmbtu_to_kg_co2_per_kwh(val: float) -> float:
        return val * _FACTORS.get("lb_co2_per_mmbtu_to_kg_co2_per_kwh", 0.00154772)

    @staticmethod
    def kg_co2_per_kwh_to_lb_co2_per_mmbtu(val: float) -> float:
        return val * _FACTORS.get("kg_co2_per_kwh_to_lb_co2_per_mmbtu", 646.1371629542789)

    @staticmethod
    def lb_co2_per_mmbtu_to_kg_co2_per_gj(val: float) -> float:
        return val * _FACTORS.get("lb_co2_per_mmbtu_to_kg_co2_per_gj", 0.4295473953885568)

    @staticmethod
    def kg_co2_per_gj_to_lb_co2_per_mmbtu(val: float) -> float:
        return val * _FACTORS.get("kg_co2_per_gj_to_lb_co2_per_mmbtu", 2.3273809523809526)
