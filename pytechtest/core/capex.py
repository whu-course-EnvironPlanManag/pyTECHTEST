"""
Manufacturing Capital Expenses (CapEx) Engine matching US DOE TECHTEST 1.0 Sheet 10.
Computes upfront investment, linear depreciation, and maintenance overheads.
"""

from typing import List, Dict, Optional
from pytechtest.core.types import CapExItem, CapExCategory


class CapExModel:
    """CapEx calculation engine for facility and reference volume scaling."""

    def __init__(self,
                 items: Optional[List[CapExItem]] = None,
                 maintenance_rate: float = 0.05,
                 annual_facility_production: float = 1.0,
                 reference_production_volume: float = 1.0):
        self.items = items or []
        self.maintenance_rate = maintenance_rate
        self.annual_facility_production = max(1e-9, annual_facility_production)
        self.reference_production_volume = reference_production_volume

    def add_item(self, item: CapExItem):
        self.items.append(item)

    @property
    def total_initial_purchase_cost(self) -> float:
        """Total un-depreciated upfront initial purchase cost ($)."""
        return sum(item.purchase_price for item in self.items)

    def get_annual_cost_by_category(self) -> Dict[CapExCategory, float]:
        """Annual straight-line capital depreciation grouped by category ($/year)."""
        res = {cat: 0.0 for cat in CapExCategory}
        for item in self.items:
            res[item.category] += item.annual_depreciation
        return res

    @property
    def total_annual_depreciation(self) -> float:
        """Total annual capital depreciation for the entire industrial facility ($/year)."""
        return sum(item.annual_depreciation for item in self.items)

    @property
    def annual_maintenance_cost(self) -> float:
        """Annual equipment and facility maintenance cost (default 5% of annualized CapEx)."""
        return self.total_annual_depreciation * self.maintenance_rate

    @property
    def total_annual_capex_with_maintenance(self) -> float:
        """Annual CapEx including maintenance ($/year)."""
        return self.total_annual_depreciation + self.annual_maintenance_cost

    def to_reference_volume(self, annual_cost: float) -> float:
        """Scale annual facility cost ($/year) to reference production volume ($/ref_volume)."""
        return annual_cost * (self.reference_production_volume / self.annual_facility_production)

    @property
    def capex_per_reference_volume(self) -> float:
        """Annual CapEx (with maintenance) allocated per reference volume."""
        return self.to_reference_volume(self.total_annual_capex_with_maintenance)
