"""
Core domain types, enums, and data definitions for US DOE TECHTEST 1.0.
Strictly decoupled domain definitions.
"""

from enum import Enum, IntEnum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class TRLLevel(IntEnum):
    """DOE Technology Readiness Levels 1 to 9."""
    TRL_1 = 1
    TRL_2 = 2
    TRL_3 = 3
    TRL_4 = 4
    TRL_5 = 5
    TRL_6 = 6
    TRL_7 = 7
    TRL_8 = 8
    TRL_9 = 9


class GridScenario(str, Enum):
    """Grid mix customization scenarios (Sheet 13)."""
    BASELINE_2022 = "2022_default"
    MODERATE = "moderate"
    NET_ZERO = "net_zero"
    CUSTOM = "custom"


class ProcessType(str, Enum):
    """Harry Silla process types for labor estimation (Sheet 21)."""
    BATCH = "batch"
    CONTINUOUS_AUTOMATED = "continuous_automated"
    CONTINUOUS_HIGHLY_AUTOMATED = "continuous_highly_automated"


class CapExCategory(str, Enum):
    """Capital expense classifications (Sheet 10)."""
    PROCESS_EQUIPMENT = "Process Equipment"
    NON_PROCESS_EQUIPMENT = "Non-Process Equipment"
    CONSTRUCTION = "Facility Construction / Site Improvements"
    OTHER = "Other Capital Expenses"


class CapExItem(BaseModel):
    """Single CapEx equipment entry."""
    name: str = Field(..., description="Equipment / component name")
    category: CapExCategory = Field(default=CapExCategory.PROCESS_EQUIPMENT)
    purchase_price: float = Field(..., ge=0.0, description="Purchase price in USD ($)")
    lifetime_years: float = Field(..., gt=0.0, description="Expected operational lifetime in years")
    salvage_value: float = Field(default=0.0, ge=0.0, description="Salvage value at end of life ($)")

    @property
    def annual_depreciation(self) -> float:
        """Straight-line annual capital cost (Purchase Price / Lifetime)."""
        return (self.purchase_price - self.salvage_value) / self.lifetime_years


class MaterialItem(BaseModel):
    """Raw material inventory input (Sheet 7)."""
    name: str = Field(..., description="Raw material name")
    amount_per_ref_volume: float = Field(..., ge=0.0, description="Mass or quantity per reference volume")
    unit: str = Field(default="lb", description="Physical unit of measurement")
    unit_price: float = Field(default=0.0, description="Unit cost in $/unit (can be negative for credits)")
    scrap_fraction: float = Field(default=0.0, ge=0.0, le=1.0, description="Scrap or loss rate")
    embodied_energy_factor: float = Field(default=0.0, ge=0.0, description="Embodied energy per unit (Btu/unit or MJ/unit)")
    embodied_ghg_factor: float = Field(default=0.0, ge=0.0, description="Embodied GHG per unit (lb CO2e/unit or kg CO2e/unit)")


class EnergyItem(BaseModel):
    """Manufacturing process energy input (Sheet 8)."""
    energy_source: str = Field(..., description="e.g. Electricity, Natural Gas, Diesel, Steam")
    amount_per_ref_volume: float = Field(..., ge=0.0, description="Energy consumption per reference volume")
    unit: str = Field(default="kWh", description="Energy unit (kWh, MMBtu, thousand cf, gallons)")
    unit_price: Optional[float] = Field(default=None, description="Optional custom price. If None, lookup EIA Ref Tables")
    custom_emission_factor: Optional[float] = Field(default=None, description="Optional custom emission factor in lb CO2e/unit")


class InUseItem(BaseModel):
    """In-use operational phase energy difference (Sheet 9)."""
    energy_source: str = Field(default="Electricity", description="Operational energy source")
    annual_energy_consumption_per_unit: float = Field(default=0.0, description="Annual consumption in use phase")
    unit: str = Field(default="kWh", description="Unit of energy")
    product_lifetime_years: float = Field(default=10.0, gt=0.0, description="End-use product operational lifespan")
