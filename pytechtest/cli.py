"""
Command Line Interface for US DOE TECHTEST 1.0 Python Suite.
Provides run, convert, labor-estimate, and grid-mix queries.
"""

import sys
import argparse
from pathlib import Path

from pytechtest.engines.full_engine import TechTestFullEngine
from pytechtest.engines.rapid_engine import TechTestRapidEngine
from pytechtest.io.excel_loader import TechTestExcelLoader
from pytechtest.io.excel_exporter import TechTestExcelExporter
from pytechtest.io.reporter import TechTestReporter
from pytechtest.core.mini_tools.silla_labor import SillaLaborEstimator
from pytechtest.core.types import ProcessType
from pytechtest.core.grid_mix import GridMixCalculator, GridScenario


def cmd_run(args):
    path = Path(args.input)
    if not path.exists():
        print(f"Error: Input file '{path}' not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Loading TECHTEST case from: {path} ...")
    if path.suffix.lower() in [".xlsx", ".xlsm"]:
        loader = TechTestExcelLoader(path)
        config = loader.load_full_input()
        engine = TechTestFullEngine(config)
    elif path.suffix.lower() in [".yaml", ".yml"]:
        # Try full engine first, then rapid
        try:
            engine = TechTestFullEngine.from_yaml(path)
        except Exception:
            engine = TechTestRapidEngine.from_yaml(path)
    else:
        print(f"Unsupported file format: {path.suffix}", file=sys.stderr)
        sys.exit(1)

    results = engine.run()
    TechTestReporter.print_terminal_dashboard(results)

    if args.export_markdown:
        TechTestReporter.save_markdown_report(results, args.export_markdown)
        print(f"Saved Markdown report to: {args.export_markdown}")

    if args.export_excel:
        exporter = TechTestExcelExporter()
        exporter.export(results, args.export_excel)
        print(f"Exported populated Excel template to: {args.export_excel}")


def cmd_labor(args):
    ptype = ProcessType(args.process_type)
    estimator = SillaLaborEstimator(
        annual_production_lb=args.production_lb,
        process_units_N=args.units_n,
        process_type=ptype,
        hours_of_operation_per_year=args.hours,
        average_annual_salary=args.salary
    )
    print("\n=== Harry Silla (2003) Chemical Process Plant Labor Estimation ===")
    for k, v in estimator.to_dict().items():
        print(f"  {k:35s}: {v}")
    print()


def cmd_grid(args):
    scen = GridScenario(args.scenario)
    calc = GridMixCalculator(scenario=scen)
    print(f"\n=== US DOE Grid Mix Scenario: {scen.value} ===")
    print(f"  Weighted Emissions (lb CO2e/MMBtu): {calc.compute_weighted_emission_factor_lb_per_mmbtu():.4f}")
    print(f"  Weighted Emissions (lb CO2e/kWh)  : {calc.compute_weighted_emission_factor_lb_per_kwh():.6f}")
    print(f"  Weighted Emissions (kg CO2e/kWh)  : {calc.compute_weighted_emission_factor_kg_per_kwh():.6f}\n")


def main():
    parser = argparse.ArgumentParser(
        prog="pytechtest",
        description="US DOE TECHTEST 1.0 (Techno-economic, Energy & Carbon Heuristic Tool for Early Stage Technologies)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # run command
    p_run = subparsers.add_parser("run", help="Run TECHTEST TEA & LCA evaluation on Excel or YAML input")
    p_run.add_argument("--input", "-i", required=True, help="Path to input .xlsx or .yaml file")
    p_run.add_argument("--export-markdown", "-m", help="Path to save Markdown summary report")
    p_run.add_argument("--export-excel", "-e", help="Path to save populated Excel template")
    p_run.set_defaults(func=cmd_run)

    # labor command
    p_labor = subparsers.add_parser("labor", help="Run Harry Silla Labor Estimation Mini-Tool (Sheet 21)")
    p_labor.add_argument("--production-lb", "-p", type=float, required=True, help="Annual facility production (lb/yr)")
    p_labor.add_argument("--units-n", "-n", type=int, required=True, help="Number of significant process units (N)")
    p_labor.add_argument("--process-type", "-t", choices=[p.value for p in ProcessType], default=ProcessType.CONTINUOUS_AUTOMATED.value)
    p_labor.add_argument("--hours", type=float, default=8000.0, help="Annual operating hours (default 8000)")
    p_labor.add_argument("--salary", type=float, default=75000.0, help="Average annual salary in USD (default 75000)")
    p_labor.set_defaults(func=cmd_labor)

    # grid command
    p_grid = subparsers.add_parser("grid", help="Query or compute US grid mix carbon intensities (Sheet 13)")
    p_grid.add_argument("--scenario", "-s", choices=[s.value for s in GridScenario if s != GridScenario.CUSTOM], default=GridScenario.BASELINE_2022.value)
    p_grid.set_defaults(func=cmd_grid)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
