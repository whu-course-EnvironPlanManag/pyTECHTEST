"""
Reporting utilities for TECHTEST evaluation results.
Supports Rich terminal tables, Markdown reports, and CSV dumps.
"""

from typing import Optional
from pathlib import Path
from pytechtest.models.results import TechTestResults

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False


class TechTestReporter:
    """Formats and displays TECHTEST evaluation results."""

    @staticmethod
    def print_terminal_dashboard(results: TechTestResults):
        """Print rich or ASCII dashboard to the terminal."""
        if not _HAS_RICH:
            results.print_dashboard()
            return

        console = Console()
        title_panel = Panel(
            f"[bold green]{results.project.title}[/bold green]\n"
            f"[cyan]Lead Org:[/cyan] {results.project.lead_organization} | "
            f"[cyan]PI:[/cyan] {results.project.principal_investigator} | "
            f"[cyan]TRL:[/cyan] Level {results.project.trl.value}\n"
            f"[cyan]Basis:[/cyan] {results.functional_unit.reference_volume:,.1f} {results.functional_unit.reference_volume_unit} of {results.market.generic_end_use_product}",
            title="[bold yellow]US DOE TECHTEST 1.0 Assessment Summary[/bold yellow]",
            expand=False
        )
        console.print(title_panel)

        table = Table(title="Results Dashboard (Cradle-to-Gate Indicators)", header_style="bold magenta")
        table.add_column("Indicator / Metric", style="dim", width=32)
        table.add_column("Commercial Benchmark", justify="right")
        table.add_column("New Technology", justify="right")
        table.add_column("Net Difference (Δ)", justify="right", style="bold green")
        table.add_column("Savings (%)", justify="right", style="bold yellow")

        # Cost
        table.add_row(
            "Manufacturing Cost ($/ref)",
            f"${results.commercial_benchmark.total_cost_per_reference_volume:,.2f}",
            f"${results.new_technology.total_cost_per_reference_volume:,.2f}",
            f"${results.summary.cost_savings_per_ref_volume:,.2f}",
            f"{results.summary.percent_cost_savings * 100:.2f}%"
        )
        table.add_row(
            "  ├─ CapEx with Maint ($/ref)",
            f"${results.commercial_benchmark.capex_per_ref_volume:,.2f}",
            f"${results.new_technology.capex_per_ref_volume:,.2f}",
            f"${results.commercial_benchmark.capex_per_ref_volume - results.new_technology.capex_per_ref_volume:,.2f}",
            "-"
        )
        table.add_row(
            "  └─ OpEx ($/ref)",
            f"${results.commercial_benchmark.opex_per_ref_volume:,.2f}",
            f"${results.new_technology.opex_per_ref_volume:,.2f}",
            f"${results.commercial_benchmark.opex_per_ref_volume - results.new_technology.opex_per_ref_volume:,.2f}",
            "-"
        )

        # Energy
        table.add_row(
            "Primary Energy (MMBtu/ref)",
            f"{results.commercial_benchmark.total_energy_per_reference_volume_mmbtu:,.2f}",
            f"{results.new_technology.total_energy_per_reference_volume_mmbtu:,.2f}",
            f"{results.summary.energy_savings_per_ref_volume_mmbtu:,.2f}",
            f"{results.summary.percent_energy_savings * 100:.2f}%"
        )

        # Emissions
        table.add_row(
            "GHG Emissions (lb CO2e/ref)",
            f"{results.commercial_benchmark.total_emissions_per_reference_volume_lb:,.2f}",
            f"{results.new_technology.total_emissions_per_reference_volume_lb:,.2f}",
            f"{results.summary.emissions_reduction_per_ref_volume_lb:,.2f}",
            f"{results.summary.percent_emissions_reduction * 100:.2f}%"
        )
        table.add_row(
            "  └─ Metric Tons (t CO2e/ref)",
            f"{results.commercial_benchmark.total_emissions_per_reference_volume_metric_tons:,.2f}",
            f"{results.new_technology.total_emissions_per_reference_volume_metric_tons:,.2f}",
            f"{results.commercial_benchmark.total_emissions_per_reference_volume_metric_tons - results.new_technology.total_emissions_per_reference_volume_metric_tons:,.2f}",
            f"{results.summary.percent_emissions_reduction * 100:.2f}%"
        )

        console.print(table)

        # Payback & Market summary
        pb_str = f"{results.summary.simple_payback_years:.2f} years" if results.summary.simple_payback_years else "N/A"
        panel_market = Panel(
            f"[bold]Simple Payback Period:[/bold] {pb_str}\n"
            f"[bold]Annual US Market Cost Savings:[/bold] ${results.summary.annual_potential_us_cost_savings:,.2f} / yr\n"
            f"[bold]Annual US Market Energy Savings:[/bold] {results.summary.annual_potential_us_energy_savings_mmbtu:,.2f} MMBtu / yr\n"
            f"[bold]Annual US Market Carbon Reduction:[/bold] {results.summary.annual_potential_us_carbon_reduction_metric_tons:,.2f} t CO2e / yr",
            title="[bold blue]Investment Payback & National Scale-up[/bold blue]",
            expand=False
        )
        console.print(panel_market)

    print_dashboard = print_terminal_dashboard

    @staticmethod
    def save_markdown_report(results: TechTestResults, output_path: str):
        """Write Markdown report to disk."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(results.to_markdown())
