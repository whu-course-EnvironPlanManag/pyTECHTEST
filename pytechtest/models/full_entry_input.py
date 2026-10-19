"""
Full Analytical Entry (Method 1) Input Schemas.
Matches US DOE TECHTEST 1.0 Full Analytical workflow.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from pytechtest.core.types import (
    CapExItem,
    MaterialItem,
    EnergyItem,
    InUseItem,
    GridScenario
)
from pytechtest.core.opex import LaborInput
from pytechtest.models.project import ProjectMetadata, MarketDefinition, FunctionalUnitDefinition


class SubsystemConfig(BaseModel):
    """Configuration for one technology branch (New Tech or Benchmark)."""
    annual_facility_production: float = Field(..., gt=0.0, description="Annual facility output of end-use product")
    capex_items: List[CapExItem] = Field(default_factory=list, description="Capital expenses items")
    capex_maintenance_rate: float = Field(default=0.05, ge=0.0, description="Annual maintenance rate on CapEx (default 5%)")
    labor: LaborInput = Field(default_factory=LaborInput, description="Direct operating labor")
    materials: List[MaterialItem] = Field(default_factory=list, description="Raw materials inputs")
    energy_items: List[EnergyItem] = Field(default_factory=list, description="Manufacturing energy inputs")
    in_use: InUseItem = Field(default_factory=InUseItem, description="Use phase energy consumption")
    other_recurring_opex: float = Field(default=0.0, ge=0.0, description="Other annual recurring expenses ($/yr)")


class FullEntryInput(BaseModel):
    """Complete specification for Method 1 Full Analytical evaluation."""
    project: ProjectMetadata
    market: MarketDefinition
    functional_unit: FunctionalUnitDefinition
    grid_scenario: GridScenario = Field(default=GridScenario.BASELINE_2022)
    custom_grid_shares: Optional[Dict[str, float]] = Field(default=None)
    new_technology: SubsystemConfig
    commercial_benchmark: SubsystemConfig
