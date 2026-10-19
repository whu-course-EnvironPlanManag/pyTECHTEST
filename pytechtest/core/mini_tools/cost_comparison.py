"""
Cost Comparison Mini-Tool Engine matching US DOE TECHTEST 1.0 Sheet 19.
Performs side-by-side parametric breakdown comparing New Technology vs Commercial Benchmark.
"""

from typing import Dict, Any
from pydantic import BaseModel, Field


class CostBreakdown(BaseModel):
    """Detailed category breakdown of manufacturing costs ($/ref_volume)."""
    manufacturing_energy: float = Field(default=0.0, ge=0.0)
    raw_materials: float = Field(default=0.0)
    annualized_capex_with_maint: float = Field(default=0.0, ge=0.0)
    direct_labor: float = Field(default=0.0, ge=0.0)
    other_recurring_opex: float = Field(default=0.0, ge=0.0)

    @property
    def total_manufacturing_cost(self) -> float:
        """Total manufacturing cost per reference volume ($)."""
        return (self.manufacturing_energy +
                self.raw_materials +
                self.annualized_capex_with_maint +
                self.direct_labor +
                self.other_recurring_opex)


class CostComparisonTool:
    """Side-by-side cost difference and percentage savings analyzer."""

    def __init__(self, new_tech: CostBreakdown, benchmark: CostBreakdown):
        self.new_tech = new_tech
        self.benchmark = benchmark

    @property
    def total_cost_difference(self) -> float:
        """Net cost difference ($/ref_volume): New Tech - Benchmark."""
        return self.new_tech.total_manufacturing_cost - self.benchmark.total_manufacturing_cost

    @property
    def total_cost_savings(self) -> float:
        """Potential cost savings ($/ref_volume): Benchmark - New Tech."""
        return self.benchmark.total_manufacturing_cost - self.new_tech.total_manufacturing_cost

    @property
    def percent_cost_savings(self) -> float:
        """Percent cost savings (1 - NewTech/Benchmark)."""
        base = self.benchmark.total_manufacturing_cost
        if base <= 1e-9:
            return 0.0
        return 1.0 - (self.new_tech.total_manufacturing_cost / base)

    def category_savings(self) -> Dict[str, Dict[str, float]]:
        """Category-by-category dollar savings and percentage changes."""
        categories = [
            ("manufacturing_energy", "Manufacturing Energy"),
            ("raw_materials", "Raw Materials"),
            ("annualized_capex_with_maint", "Capital Expenses & Maintenance"),
            ("direct_labor", "Direct Labor"),
            ("other_recurring_opex", "Other Operating Costs")
        ]
        res = {}
        for attr, label in categories:
            val_nt = getattr(self.new_tech, attr)
            val_bm = getattr(self.benchmark, attr)
            diff = val_bm - val_nt
            pct = (1.0 - (val_nt / val_bm)) if val_bm > 1e-9 else 0.0
            entry = {
                "label": label,
                "new_technology": val_nt,
                "benchmark": val_bm,
                "dollar_savings": diff,
                "percent_savings": pct
            }
            res[attr] = entry
            res[label] = entry
        return res
