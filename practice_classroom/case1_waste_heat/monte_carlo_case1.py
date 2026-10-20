#!/usr/bin/env python3
"""Run a reproducible Monte Carlo uncertainty analysis for Case 1."""

import argparse
import copy
import csv
import random
import sys
from pathlib import Path
from statistics import mean, stdev
from typing import Dict, List, Sequence

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from pytechtest import TechTestFullEngine


DEFAULT_ITERATIONS = 1000
DEFAULT_SEED = 20261020
UNCERTAINTY_FRACTION = 0.10
METRICS = (
    ("cost_savings_usd_per_ref", "Cost savings ($/ref)"),
    ("energy_savings_mmbtu_per_ref", "Energy savings (MMBtu/ref)"),
    ("emissions_reduction_lb_co2e_per_ref", "Emissions reduction (lb CO2e/ref)"),
)


def _sample_triangular(rng: random.Random, nominal: float) -> float:
    return rng.triangular(
        nominal * (1.0 - UNCERTAINTY_FRACTION),
        nominal * (1.0 + UNCERTAINTY_FRACTION),
        nominal,
    )


def _percentile(values: Sequence[float], percentile: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile / 100.0
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def run_monte_carlo(
    config_path: Path,
    output_path: Path,
    iterations: int = DEFAULT_ITERATIONS,
    seed: int = DEFAULT_SEED,
) -> List[Dict[str, float]]:
    """Evaluate the model for sampled inputs and write all iterations to CSV."""
    if iterations < 1:
        raise ValueError("iterations must be at least 1")

    base_config = TechTestFullEngine.from_yaml(config_path).config
    rng = random.Random(seed)
    samples: List[Dict[str, float]] = []

    for iteration in range(1, iterations + 1):
        config = copy.deepcopy(base_config)
        new_tech = config.new_technology
        benchmark = config.commercial_benchmark

        sampled: Dict[str, float] = {
            "iteration": float(iteration),
            "new_capex_usd": _sample_triangular(
                rng, new_tech.capex_items[0].purchase_price
            ),
            "benchmark_capex_usd": _sample_triangular(
                rng, benchmark.capex_items[0].purchase_price
            ),
            "new_labor_fte": _sample_triangular(rng, new_tech.labor.fte_count),
            "benchmark_labor_fte": _sample_triangular(
                rng, benchmark.labor.fte_count
            ),
            "new_electricity_kwh_per_ref": _sample_triangular(
                rng, new_tech.energy_items[0].amount_per_ref_volume
            ),
            "benchmark_electricity_kwh_per_ref": _sample_triangular(
                rng, benchmark.energy_items[0].amount_per_ref_volume
            ),
        }
        tariff = _sample_triangular(rng, new_tech.energy_items[0].unit_price)
        sampled["electricity_price_usd_per_kwh"] = tariff

        new_tech.capex_items[0].purchase_price = sampled["new_capex_usd"]
        benchmark.capex_items[0].purchase_price = sampled["benchmark_capex_usd"]
        new_tech.labor.fte_count = sampled["new_labor_fte"]
        benchmark.labor.fte_count = sampled["benchmark_labor_fte"]
        new_tech.energy_items[0].amount_per_ref_volume = sampled[
            "new_electricity_kwh_per_ref"
        ]
        benchmark.energy_items[0].amount_per_ref_volume = sampled[
            "benchmark_electricity_kwh_per_ref"
        ]
        for energy_item in new_tech.energy_items + benchmark.energy_items:
            energy_item.unit_price = tariff

        summary = TechTestFullEngine(config).run().summary
        sampled.update(
            {
                "cost_savings_usd_per_ref": summary.cost_savings_per_ref_volume,
                "energy_savings_mmbtu_per_ref": (
                    summary.energy_savings_per_ref_volume_mmbtu
                ),
                "emissions_reduction_lb_co2e_per_ref": (
                    summary.emissions_reduction_per_ref_volume_lb
                ),
            }
        )
        samples.append(sampled)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(samples[0]))
        writer.writeheader()
        writer.writerows(samples)
    return samples


def print_summary(samples: Sequence[Dict[str, float]]) -> None:
    print(f"Monte Carlo iterations: {len(samples)}")
    for key, label in METRICS:
        values = [sample[key] for sample in samples]
        positive_rate = sum(value > 0.0 for value in values) / len(values) * 100.0
        print(
            f"{label}: mean={mean(values):.4f}, "
            f"SD={stdev(values) if len(values) > 1 else 0.0:.4f}, "
            f"P5={_percentile(values, 5):.4f}, "
            f"median={_percentile(values, 50):.4f}, "
            f"P95={_percentile(values, 95):.4f}, "
            f"P(positive)={positive_rate:.1f}%"
        )


def main() -> None:
    case_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--iterations",
        type=int,
        default=DEFAULT_ITERATIONS,
        help=f"number of Monte Carlo iterations (default: {DEFAULT_ITERATIONS})",
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--output",
        type=Path,
        default=case_dir / "monte_carlo_case1_results.csv",
    )
    args = parser.parse_args()

    samples = run_monte_carlo(
        case_dir / "student_template.yaml",
        args.output,
        iterations=args.iterations,
        seed=args.seed,
    )
    print_summary(samples)
    print(f"Per-iteration results: {args.output}")


if __name__ == "__main__":
    main()
