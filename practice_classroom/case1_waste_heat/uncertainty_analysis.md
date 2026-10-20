# Case 1: Monte Carlo Uncertainty Analysis

This document and its supporting files are the separate second assignment for Case 1. It does not modify the first-assignment configuration or README.

## Assumptions

The course instructions did not specify probability distributions or parameter ranges. The following are explicit demonstration assumptions, not DOE-provided probability data:

- New-technology and benchmark equipment purchase price, operating FTE, and electricity consumption are sampled independently.
- Electricity price is sampled once per iteration and shared by both technologies, representing the same market condition.
- Each sampled value follows a triangular distribution with lower bound 90% of the template value, mode equal to the template value, and upper bound 110% of the template value.
- Grid scenario, materials, and all other inputs remain fixed. No other input correlations are modeled.
- The analysis uses the template values without editing the first-assignment YAML.

## Reproduction

Run 1,000 simulations with the fixed default seed:

```powershell
python practice_classroom/case1_waste_heat/monte_carlo_case1.py
```

The script writes one row per iteration to [`monte_carlo_case1_results.csv`](monte_carlo_case1_results.csv). Use `--iterations` and `--seed` to change the count or seed. The saved CSV corresponds to 1,000 iterations with seed `20261020`.

## Results

| Metric | Mean | Standard deviation | P5 | Median | P95 | Positive samples |
|---|---:|---:|---:|---:|---:|---:|
| Cost savings ($/ref) | 214.38 | 14.57 | 191.53 | 213.87 | 238.90 | 100.0% |
| Energy savings (MMBtu/ref) | 7.589 | 0.570 | 6.645 | 7.577 | 8.538 | 100.0% |
| Emissions reduction (lb CO2e/ref) | 820.04 | 61.87 | 717.51 | 818.72 | 923.06 | 100.0% |

All three metrics remained positive in the 1,000 simulated draws under these assumptions. This is a result conditional on the chosen distributions and ranges, not a guarantee or an estimate based on empirically validated probabilities. The repository's price/grid scenario sweep is deterministic sensitivity analysis, not this Monte Carlo analysis.
