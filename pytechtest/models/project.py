"""
Project Metadata, Technology Benchmarks, and Market Definitions.
Matches US DOE TECHTEST 1.0 Sheets 4 ('Project Basics & Benchmarks'), 5 ('Market'), and 6 ('Functional Unit').
"""

from typing import Optional
from pydantic import BaseModel, Field
from pytechtest.core.types import TRLLevel


class ProjectMetadata(BaseModel):
    """Project description and administrative information (Sheet 4)."""
    title: str = Field(..., description="Project title")
    lead_organization: str = Field(default="Wuhan University", description="Lead organization / institution")
    partners: str = Field(default="", description="Collaborating partners / industry liaisons")
    principal_investigator: str = Field(default="Dr. Siqi Tang", description="Principal investigator name")
    pi_organization: str = Field(default="School of Resource and Environmental Sciences", description="PI Department")
    technology_manager: str = Field(default="", description="DOE AMO / Industrial Technology Manager")
    start_date: str = Field(default="2026-01-01", description="Project start date")
    end_date: str = Field(default="2027-12-31", description="Project end date")
    funding_mechanism: str = Field(default="R&D Project", description="Funding mechanism / grant type")
    trl: TRLLevel = Field(default=TRLLevel.TRL_3, description="Technology Readiness Level (1-9)")


class MarketDefinition(BaseModel):
    """Market size and addressable adoption scaling (Sheet 5)."""
    generic_end_use_product: str = Field(..., description="Generic market end-use product description")
    annual_us_market_volume: float = Field(default=1000.0, ge=0.0, description="Total annual US market production")
    market_units: str = Field(default="Million Gallons", description="Units of market volume")
    target_penetration_fraction: float = Field(default=0.10, ge=0.0, le=1.0, description="Target market penetration fraction (0.0 to 1.0)")
    market_description: Optional[str] = Field(default="", description="Market sector notes")


class FunctionalUnitDefinition(BaseModel):
    """Functional unit and reference volume specification (Sheet 6)."""
    product_name_new_tech: str = Field(..., description="Specific product name for New Technology")
    product_name_benchmark: str = Field(..., description="Specific product name for Commercial Benchmark")
    functional_unit_description: str = Field(default="Cooling 1 Million Gallons of wastewater", description="Functional unit basis")
    reference_volume: float = Field(default=1.0, gt=0.0, description="Reference production volume")
    reference_volume_unit: str = Field(default="Million Gallons", description="Unit of reference volume")
    equivalence_ratio: float = Field(default=1.0, gt=0.0, description="Equivalent benchmark units per new tech unit")
