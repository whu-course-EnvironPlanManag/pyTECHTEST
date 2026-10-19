"""
Standardized TECHTEST Output Results Contract.
Matches US DOE TECHTEST 1.0 Summary Tables and Results Dashboards.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from pytechtest.core.dashboard import TechnologyProfile
from pytechtest.models.project import ProjectMetadata, MarketDefinition, FunctionalUnitDefinition


class DashboardSummary(BaseModel):
    """Consolidated KPI decision metrics."""
    cost_savings_per_ref_volume: float = Field(..., description="Cost savings ($/ref_volume)")
    percent_cost_savings: float = Field(..., description="Percent cost reduction")
    energy_savings_per_ref_volume_mmbtu: float = Field(..., description="Energy savings (MMBtu/ref_volume)")
    percent_energy_savings: float = Field(..., description="Percent energy reduction")
    emissions_reduction_per_ref_volume_lb: float = Field(..., description="GHG reduction (lb CO2e/ref_volume)")
    percent_emissions_reduction: float = Field(..., description="Percent GHG reduction")
    simple_payback_years: Optional[float] = Field(default=None, description="Static payback period in years")

    # National US Market Scale
    annual_potential_us_cost_savings: float = Field(default=0.0, description="Annual potential US cost savings ($/yr)")
    annual_potential_us_energy_savings_mmbtu: float = Field(default=0.0, description="Annual US energy savings (MMBtu/yr)")
    annual_potential_us_carbon_reduction_metric_tons: float = Field(default=0.0, description="Annual US CO2e reduction (t/yr)")


class TechTestResults(BaseModel):
    """Complete consolidated output artifact for TECHTEST evaluation."""
    project: ProjectMetadata
    market: MarketDefinition
    functional_unit: FunctionalUnitDefinition
    new_technology: TechnologyProfile
    commercial_benchmark: TechnologyProfile
    summary: DashboardSummary

    def to_markdown(self) -> str:
        """Generate high-impact Markdown decision summary."""
        pb = f"{self.summary.simple_payback_years:.2f} 年" if self.summary.simple_payback_years else "N/A (无额外收益或增量CapEx为0)"
        md = f"""# US DOE TECHTEST 1.0 技术经济与碳减排综合评估简报

## 一、 项目基础与市场定义
- **项目名称**: {self.project.title}
- **牵头单位**: {self.project.lead_organization} | **负责人**: {self.project.principal_investigator}
- **技术就绪度 (TRL)**: Level {self.project.trl.value} ({self.project.trl.name})
- **对标产品**: 新技术 [{self.new_technology.product_name}] vs 商业基准 [{self.commercial_benchmark.product_name}]
- **基准产量 (Ref Volume)**: {self.functional_unit.reference_volume:,.1f} {self.functional_unit.reference_volume_unit}

---

## 二、 核心决策看板 (Results Dashboard)
| 评价维度 | 商业基准 (Benchmark) | 创新技术 (New Tech) | 净差异 (Δ) | 节约 / 减排比率 |
| :--- | :---: | :---: | :---: | :---: |
| **全口径制造总成本 ($/ref)** | ${self.commercial_benchmark.total_cost_per_reference_volume:,.2f} | ${self.new_technology.total_cost_per_reference_volume:,.2f} | **${self.summary.cost_savings_per_ref_volume:,.2f}** | **{self.summary.percent_cost_savings * 100:.2f}%** |
| ├─ 资本支出折旧 (CapEx) | ${self.commercial_benchmark.capex_per_ref_volume:,.2f} | ${self.new_technology.capex_per_ref_volume:,.2f} | ${self.commercial_benchmark.capex_per_ref_volume - self.new_technology.capex_per_ref_volume:,.2f} | - |
| └─ 运营管理支出 (OpEx) | ${self.commercial_benchmark.opex_per_ref_volume:,.2f} | ${self.new_technology.opex_per_ref_volume:,.2f} | ${self.commercial_benchmark.opex_per_ref_volume - self.new_technology.opex_per_ref_volume:,.2f} | - |
| **一次能源能耗 (MMBtu/ref)** | {self.commercial_benchmark.total_energy_per_reference_volume_mmbtu:,.2f} | {self.new_technology.total_energy_per_reference_volume_mmbtu:,.2f} | **{self.summary.energy_savings_per_ref_volume_mmbtu:,.2f} MMBtu** | **{self.summary.percent_energy_savings * 100:.2f}%** |
| **全生命周期碳排 (lb CO2e/ref)**| {self.commercial_benchmark.total_emissions_per_reference_volume_lb:,.2f} | {self.new_technology.total_emissions_per_reference_volume_lb:,.2f} | **{self.summary.emissions_reduction_per_ref_volume_lb:,.2f} lb** | **{self.summary.percent_emissions_reduction * 100:.2f}%** |
| └─ 折合公制吨 (t CO2e/ref) | {self.commercial_benchmark.total_emissions_per_reference_volume_metric_tons:,.2f} t | {self.new_technology.total_emissions_per_reference_volume_metric_tons:,.2f} t | **{self.commercial_benchmark.total_emissions_per_reference_volume_metric_tons - self.new_technology.total_emissions_per_reference_volume_metric_tons:,.2f} t** | **{self.summary.percent_emissions_reduction * 100:.2f}%** |

---

## 三、 投资回报与全美潜在市场规模化效益
- **静态投资回收期 (Simple Payback Period)**: **{pb}**
- **全美年均潜在经济节约 (US Market Cost Savings)**: **${self.summary.annual_potential_us_cost_savings:,.2f} / 年**
- **全美年均潜在节能量 (US Market Energy Savings)**: **{self.summary.annual_potential_us_energy_savings_mmbtu:,.2f} MMBtu / 年**
- **全美年均潜在碳减排 (US Market GHG Reduction)**: **{self.summary.annual_potential_us_carbon_reduction_metric_tons:,.2f} 吨 CO2-e / 年**
"""
        return md

    def print_dashboard(self):
        """Print rich ASCII dashboard to stdout."""
        print(self.to_markdown())
