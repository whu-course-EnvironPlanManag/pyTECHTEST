"""
Harry Silla (2003) Process Plant Labor Estimation Mini-Tool.
Matches US DOE TECHTEST 1.0 Sheet 21 ('Labor Estimation Mini-Tool').
Reference: Harry Silla, Chemical Process Engineering: Design and Economics (Marcel Dekker, 2003), Eq 2.1.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from pytechtest.core.types import ProcessType

def _find_data_dir() -> Path:
    current = Path(__file__).resolve()
    for p in current.parents:
        cand = p / "data"
        if cand.exists() and (cand / "summary_ref_tables.json").exists():
            return cand
    return current.parents[2] / "data"

_DATA_DIR = _find_data_dir()

def load_silla_config() -> Dict[str, Any]:
    path = _DATA_DIR / "silla_labor_parameters.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

_SILLA_CONFIG = load_silla_config()


class SillaLaborEstimator:
    """Estimates operating and supervision labor hours and costs from plant capacity."""

    def __init__(self,
                 annual_production_lb: float,
                 process_units_N: int,
                 process_type: ProcessType = ProcessType.CONTINUOUS_AUTOMATED,
                 hours_of_operation_per_year: float = 8000.0,
                 average_annual_salary: float = 75000.0,
                 evaluation_year: int = 2021,
                 productivity_growth_p: float = 0.02,
                 supervision_rate: float = 0.20,
                 fringe_overhead_rate: float = 0.72):
        self.annual_production_lb = max(1.0, annual_production_lb)
        self.process_units_N = max(1, process_units_N)
        self.process_type = process_type
        self.hours_of_operation = max(1.0, min(8760.0, hours_of_operation_per_year))
        self.average_salary = average_annual_salary
        self.evaluation_year = evaluation_year
        self.productivity_growth_p = productivity_growth_p
        self.supervision_rate = supervision_rate
        self.fringe_overhead_rate = fringe_overhead_rate

    @property
    def years_since_base_year(self) -> int:
        """n = Number of years since 1952 base year."""
        base_year = _SILLA_CONFIG.get("base_year", 1952)
        return max(0, self.evaluation_year - base_year)

    @property
    def hourly_production_rate_lb_per_hr(self) -> float:
        """Hourly facility production rate in lb / hr."""
        return self.annual_production_lb / self.hours_of_operation

    @property
    def hourly_production_rate_m_kg_per_hr(self) -> float:
        """Production rate m in kg/hr (Silla Eq 2.1)."""
        return self.hourly_production_rate_lb_per_hr / 2.20462262

    def get_exponents(self) -> Dict[str, float]:
        """Lookup capacity exponent b and productivity factor K."""
        exps = _SILLA_CONFIG.get("exponents_and_k", {}).get(self.process_type.value, {})
        threshold = _SILLA_CONFIG.get("capacity_threshold_kg_per_hr", 5670.0)
        if self.hourly_production_rate_m_kg_per_hr < threshold:
            return exps.get("low_capacity", {"b": 0.76, "K": 0.296})
        return exps.get("high_capacity", {"b": 0.84, "K": 0.396})

    @property
    def labor_hours_per_kg(self) -> float:
        """
        Operator labor hours required to produce 1 kg of product.
        L = K * N * (1 / (1 + p)^n) * (1 / m^b)
        """
        params = self.get_exponents()
        K = params["K"]
        b = params["b"]
        N = float(self.process_units_N)
        n = float(self.years_since_base_year)
        p = self.productivity_growth_p
        m = self.hourly_production_rate_m_kg_per_hr

        # Silla Equation 2.1
        L = K * N * (1.0 / ((1.0 + p) ** n)) * (1.0 / (m ** b))
        return L

    @property
    def labor_hours_per_lb(self) -> float:
        """Operator labor hours per lb produced."""
        return self.labor_hours_per_kg / 2.20462262

    @property
    def annual_operating_labor_hours(self) -> float:
        """Annual total operating labor hours (excluding supervision)."""
        return self.labor_hours_per_lb * self.annual_production_lb

    @property
    def operating_labor_fte(self) -> float:
        """Number of full-time equivalent operators (based on 2080 hr/yr)."""
        return self.annual_operating_labor_hours / 2080.0

    @property
    def annual_total_labor_hours_with_supervision(self) -> float:
        """Annual total labor hours including 20% supervision."""
        return self.annual_operating_labor_hours * (1.0 + self.supervision_rate)

    @property
    def total_labor_fte_with_supervision(self) -> float:
        """Total FTEs (direct operators + supervisors)."""
        return self.annual_total_labor_hours_with_supervision / 2080.0

    @property
    def base_labor_cost(self) -> float:
        """Base annual direct labor cost without fringe benefits ($/yr)."""
        return self.total_labor_fte_with_supervision * self.average_salary

    @property
    def fringe_overhead_cost(self) -> float:
        """Fringe benefits and general overhead ($/yr)."""
        return self.base_labor_cost * self.fringe_overhead_rate

    @property
    def total_direct_labor_cost(self) -> float:
        """Total annual direct labor cost ($/yr) matching TECHTEST Sheet 21 Cell F66."""
        return self.base_labor_cost + self.fringe_overhead_cost

    # Convenience aliases
    total_fte_requirement = total_labor_fte_with_supervision
    annual_total_labor_cost = total_direct_labor_cost
    operating_labor_hours = annual_operating_labor_hours

    @property
    def supervision_labor_hours(self) -> float:
        """Annual supervision labor hours."""
        return self.annual_operating_labor_hours * self.supervision_rate

    def to_dict(self) -> Dict[str, Any]:
        """Summary report of labor estimation."""
        return {
            "annual_production_lb": self.annual_production_lb,
            "production_rate_kg_hr": round(self.hourly_production_rate_m_kg_per_hr, 2),
            "process_units_N": self.process_units_N,
            "process_type": self.process_type.value,
            "labor_hours_per_kg": round(self.labor_hours_per_kg, 6),
            "operating_labor_fte": round(self.operating_labor_fte, 4),
            "total_fte_with_supervision": round(self.total_labor_fte_with_supervision, 4),
            "total_direct_labor_cost_usd": round(self.total_direct_labor_cost, 2)
        }
