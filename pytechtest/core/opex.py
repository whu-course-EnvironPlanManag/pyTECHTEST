"""
Manufacturing Operating Expenses (OpEx) Engine matching US DOE TECHTEST 1.0 Sheet 11.
Computes recurring operations costs: Direct Labor, Materials, Energy, Maintenance, and Waste.
"""

from typing import Optional
from pydantic import BaseModel, Field


class LaborInput(BaseModel):
    """Direct labor cost specification (Sheet 11)."""
    fte_count: float = Field(default=0.0, ge=0.0, description="Full-time equivalent employees")
    average_annual_salary: float = Field(default=75000.0, ge=0.0, description="Average annual wage ($/yr)")
    fringe_overhead_rate: float = Field(default=0.72, ge=0.0, description="Default 72% fringe & overhead")
    direct_annual_cost_override: Optional[float] = Field(default=None, description="Direct cost override if known")

    @property
    def annual_labor_cost(self) -> float:
        """Annual total labor cost including overhead for the facility ($/yr)."""
        if self.direct_annual_cost_override is not None:
            return self.direct_annual_cost_override
        return self.fte_count * self.average_annual_salary * (1.0 + self.fringe_overhead_rate)


class OpExModel:
    """Consolidated OpEx calculation engine."""

    def __init__(self,
                 labor: Optional[LaborInput] = None,
                 annual_material_cost: float = 0.0,
                 annual_energy_cost: float = 0.0,
                 annual_maintenance_cost: float = 0.0,
                 annual_other_recurring: float = 0.0,
                 annual_facility_production: float = 1.0,
                 reference_production_volume: float = 1.0):
        self.labor = labor or LaborInput()
        self.annual_material_cost = annual_material_cost
        self.annual_energy_cost = annual_energy_cost
        self.annual_maintenance_cost = annual_maintenance_cost
        self.annual_other_recurring = annual_other_recurring
        self.annual_facility_production = max(1e-9, annual_facility_production)
        self.reference_production_volume = reference_production_volume

    @property
    def annual_labor_cost(self) -> float:
        return self.labor.annual_labor_cost

    @property
    def total_annual_opex(self) -> float:
        """Total annual operating expenses for the entire facility ($/year)."""
        return (self.annual_labor_cost +
                self.annual_material_cost +
                self.annual_energy_cost +
                self.annual_maintenance_cost +
                self.annual_other_recurring)

    def to_reference_volume(self, annual_cost: float) -> float:
        """Scale annual facility cost ($/year) to reference production volume ($/ref_volume)."""
        return annual_cost * (self.reference_production_volume / self.annual_facility_production)

    @property
    def labor_cost_per_reference_volume(self) -> float:
        return self.to_reference_volume(self.annual_labor_cost)

    @property
    def opex_per_reference_volume(self) -> float:
        """Operating cost per reference volume manufactured ($/ref_volume)."""
        return self.to_reference_volume(self.total_annual_opex)
