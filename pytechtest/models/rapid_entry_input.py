"""
Rapid Data Entry (Method 2) Input Schemas.
Matches US DOE TECHTEST 1.0 Sheet 16 ('Rapid Data Input (Method 2)').
"""

from pydantic import BaseModel, Field
from pytechtest.models.project import ProjectMetadata, MarketDefinition, FunctionalUnitDefinition


class RapidTechCard(BaseModel):
    """Card data for Method 2 Rapid Assessment."""
    name: str = Field(..., description="Technology name")
    product_name: str = Field(..., description="Product name")
    annual_facility_production: float = Field(..., gt=0.0, description="Facility annual production")
    
    # Financial indicators
    total_initial_capex: float = Field(..., ge=0.0, description="Total initial equipment CapEx purchase price ($)")
    annualized_capex_with_maint: float = Field(..., ge=0.0, description="Annual CapEx with 5% maintenance ($/year)")
    annual_opex: float = Field(..., ge=0.0, description="Annual operating OpEx for facility ($/year)")

    # Energy indicators (per reference volume)
    manufacturing_energy_mmbtu: float = Field(default=0.0, ge=0.0, description="Manufacturing energy (MMBtu/ref_volume)")
    raw_material_embodied_energy_mmbtu: float = Field(default=0.0, ge=0.0, description="Raw material embodied energy (MMBtu/ref_volume)")
    in_use_energy_mmbtu: float = Field(default=0.0, ge=0.0, description="In-use energy (MMBtu/ref_volume)")

    # Emission indicators (per reference volume)
    manufacturing_emissions_lb: float = Field(default=0.0, ge=0.0, description="Manufacturing emissions (lb CO2e/ref_volume)")
    raw_material_embodied_emissions_lb: float = Field(default=0.0, ge=0.0, description="Raw material embodied GHG (lb CO2e/ref_volume)")
    in_use_emissions_lb: float = Field(default=0.0, ge=0.0, description="In-use emissions (lb CO2e/ref_volume)")


class RapidEntryInput(BaseModel):
    """High-level input schema for Method 2 Rapid Data Entry."""
    project: ProjectMetadata
    market: MarketDefinition
    functional_unit: FunctionalUnitDefinition
    new_technology: RapidTechCard
    commercial_benchmark: RapidTechCard
