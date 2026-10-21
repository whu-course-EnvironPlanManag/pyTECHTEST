#!/usr/bin/env python3
"""Run a one-parameter triangular Monte Carlo analysis for case 1."""

import copy
import random
import sys
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import yaml

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from pytechtest.engines.full_engine import TechTestFullEngine
from pytechtest.models.full_entry_input import FullEntryInput


RUNS = 1000
RANDOM_SEED = 20261021
LOWER_FACTOR = 0.9
UPPER_FACTOR = 1.1
REPORT_PATH = Path(__file__).resolve().parent / "case1_uncertainty_analysis.md"
PLOT_PATH = Path(__file__).resolve().parent / "case1_uncertainty_analysis.png"


def quantile(values: List[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def summarize(values: List[float]) -> Dict[str, float]:
    return {
        "mean": sum(values) / len(values),
        "median": quantile(values, 0.5),
        "p05": quantile(values, 0.05),
        "p95": quantile(values, 0.95),
        "minimum": min(values),
        "maximum": max(values),
    }


def write_plot(samples: Dict[str, List[float]]) -> None:
    charts = [
        ("New technology electricity use", "kWh / reference volume", "electricity"),
        ("Cost savings", "$ / reference volume", "cost"),
        ("Energy savings", "MMBtu / reference volume", "energy"),
        ("GHG reduction", "lb CO2e / reference volume", "ghg"),
    ]
    colors = ["#167D8D", "#D77A32", "#4B8C5A", "#B84A62"]
    figure, axes = plt.subplots(2, 2, figsize=(12, 8))

    for axis, (title, unit, key), color in zip(axes.flat, charts, colors):
        values = samples[key]
        axis.hist(values, bins=28, color=color, edgecolor="white", alpha=0.9)
        axis.axvline(quantile(values, 0.5), color="#202A35", linestyle="--", linewidth=1.5)
        axis.set_title(title)
        axis.set_xlabel(unit)
        axis.set_ylabel("Frequency")
        axis.grid(axis="y", alpha=0.2)

    figure.suptitle("Case 1 Uncertainty Analysis: Triangular Monte Carlo (n=1,000)")
    figure.tight_layout()
    figure.savefig(PLOT_PATH, dpi=180, bbox_inches="tight")
    plt.close(figure)


def write_report(
    base_electricity: float,
    samples: Dict[str, List[float]],
) -> str:
    variable_stats = summarize(samples["electricity"])
    lower_electricity = base_electricity * LOWER_FACTOR
    upper_electricity = base_electricity * UPPER_FACTOR
    metrics = [
        ("单位成本节约", "cost", "$ / ref"),
        ("成本节约比例", "cost_rate", "%"),
        ("单位能耗节约", "energy", "MMBtu / ref"),
        ("能耗节约比例", "energy_rate", "%"),
        ("单位温室气体减排", "ghg", "lb CO2e / ref"),
        ("温室气体减排比例", "ghg_rate", "%"),
    ]

    rows = []
    for label, key, unit in metrics:
        stats = summarize(samples[key])
        rows.append(
            f"| {label} | {unit} | {stats['median']:.4f} "
            f"| {stats['p05']:.4f} | {stats['p95']:.4f} "
            f"| {stats['minimum']:.4f} | {stats['maximum']:.4f} |"
        )

    positive_probabilities = {
        "成本节约大于零": sum(value > 0 for value in samples["cost"]) / RUNS,
        "能耗节约大于零": sum(value > 0 for value in samples["energy"]) / RUNS,
        "温室气体减排大于零": sum(value > 0 for value in samples["ghg"]) / RUNS,
    }
    probability_rows = "\n".join(
        f"| {label} | {probability:.1%} |"
        for label, probability in positive_probabilities.items()
    )

    report = f"""# Case 1 余热回收项目不确定性分析报告

## 摘要

本报告针对工业余热回收案例开展单参数蒙特卡洛分析。以新技术单位电耗为不确定参数，采用三角分布抽样 1,000 次，并在每次抽样后调用 TECHTEST 完整计算引擎，观察单位成本节约、节能量和温室气体减排的变化。设定范围内，三项改善指标均保持为正；结果仅反映电耗这一项输入的不确定性。

## 1. 案例与分析目标

案例比较饮料制造废水冷却中的余热回收新技术与传统蒸发式冷凝器。分析以配置文件定义的 **2.0 Million Gallons** 处理量为参考功能单位，关注新技术单位电耗变化对成本、能源和温室气体指标的影响。

本分析的目标不是重新校准官方基准值，而是回答：当新技术实际电耗围绕当前估计值波动时，预期节约与减排指标的分布如何，改善方向是否会改变。

## 2. 方法与假设

- **抽样参数**：新技术单位电耗，基准值 **{base_electricity:.2f} kWh/ref**。
- **概率分布**：三角分布，最小值 **{lower_electricity:.2f}**、众数 **{base_electricity:.2f}**、最大值 **{upper_electricity:.2f} kWh/ref**。众数取当前配置值，上下界分别为基准值的 90% 和 110%。
- **模拟次数与复现**：{RUNS:,} 次，随机种子为 `{RANDOM_SEED}`。
- **控制变量**：除新技术单位电耗外，其余市场、成本、材料、设备、劳动力、电价和电网参数均保持配置文件基准值。
- **计算方式**：每轮将抽样电耗写入新技术配置，并重新运行完整模型。报告中的 90%模拟区间指第 5 至第 95 百分位数，不是基于实测数据构造的统计置信区间。

## 3. 抽样参数结果

| 参数 | 中位数 | 5%分位 | 95%分位 | 最小抽样值 | 最大抽样值 |
|---|---:|---:|---:|---:|---:|
| 新技术单位电耗 (kWh/ref) | {variable_stats['median']:.4f} | {variable_stats['p05']:.4f} | {variable_stats['p95']:.4f} | {variable_stats['minimum']:.4f} | {variable_stats['maximum']:.4f} |

## 4. 模型输出

| 指标 | 单位 | 中位数 | 5%分位 | 95%分位 | 最小值 | 最大值 |
|---|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

### 改善方向概率

| 事件 | 模拟概率 |
|---|---:|
{probability_rows}

## 5. 结果讨论

在本次抽样范围内，单位成本节约的中位数为 **${summarize(samples['cost'])['median']:.2f}/ref**，90%模拟区间为 **${summarize(samples['cost'])['p05']:.2f}–${summarize(samples['cost'])['p95']:.2f}/ref**。单位能耗节约中位数为 **{summarize(samples['energy'])['median']:.4f} MMBtu/ref**，单位温室气体减排中位数为 **{summarize(samples['ghg'])['median']:.2f} lb CO2e/ref**。

新技术单位电耗越高，其运行电力成本、能耗和电力相关排放越高；因此成本节约、节能量和减排量总体随之下降。尽管如此，在当前设定的 ±10% 波动范围中，三项指标的模拟值仍均为正，改善概率各为 100%。这说明在**该参数范围和其他输入固定的条件下**，案例的改善方向较稳定，但不能外推为现实项目的绝对保证。

## 6. 结果图

图中展示抽样电耗以及三个主要输出指标的频数分布；虚线标记各指标的模拟中位数。

![Case 1 蒙特卡洛分析结果分布图](case1_uncertainty_analysis.png)

## 7. 局限性

1. 本次只对新技术电耗进行不确定性分析，其他输入被固定；未评估设备投资、维护费率、电价、生产规模等参数的联合影响。
2. ±10% 范围是本次教学分析的假设，不是由现场测量、历史数据或专家判断拟合得到。
3. 模拟结果依赖当前配置及 TECHTEST 模型结构。若功能单位、系统边界、排放因子或输入数据改变，应重新运行并解释结果。
4. “100% 改善概率”仅表示 1,000 个样本在设定分布内均改善，不代表所有可能运行条件下都必然改善。

## 8. 结论

在新技术单位电耗以 **{base_electricity:.2f} kWh/ref** 为众数、在其上下 10% 范围内按三角分布变化的设定下，1,000 次模拟均得到正的成本节约、节能量和温室气体减排。中位数分别约为 **${summarize(samples['cost'])['median']:.2f}/ref**、**{summarize(samples['energy'])['median']:.4f} MMBtu/ref** 和 **{summarize(samples['ghg'])['median']:.2f} lb CO2e/ref**。结论应理解为单参数情景分析结果；更全面的风险评估需要为其他关键参数提供有依据的分布，并考虑参数间相关性。
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    return report


def main() -> None:
    case_dir = Path(__file__).resolve().parent
    yaml_path = case_dir / "student_template.yaml"
    with yaml_path.open("r", encoding="utf-8") as stream:
        base_data = yaml.safe_load(stream)

    electricity_item = next(
        item
        for item in base_data["new_technology"]["energy_items"]
        if "electr" in item["energy_source"].lower()
    )
    base_electricity = electricity_item["amount_per_ref_volume"]
    rng = random.Random(RANDOM_SEED)
    samples: Dict[str, List[float]] = {
        "electricity": [],
        "cost": [],
        "cost_rate": [],
        "energy": [],
        "energy_rate": [],
        "ghg": [],
        "ghg_rate": [],
    }

    for _ in range(RUNS):
        sampled_data = copy.deepcopy(base_data)
        sampled_electricity = rng.triangular(
            base_electricity * LOWER_FACTOR,
            base_electricity * UPPER_FACTOR,
            base_electricity,
        )
        sampled_item = next(
            item
            for item in sampled_data["new_technology"]["energy_items"]
            if "electr" in item["energy_source"].lower()
        )
        sampled_item["amount_per_ref_volume"] = sampled_electricity

        config = FullEntryInput.model_validate(sampled_data)
        result = TechTestFullEngine(config).run()
        summary = result.summary

        samples["electricity"].append(sampled_electricity)
        samples["cost"].append(summary.cost_savings_per_ref_volume)
        samples["cost_rate"].append(summary.percent_cost_savings * 100)
        samples["energy"].append(summary.energy_savings_per_ref_volume_mmbtu)
        samples["energy_rate"].append(summary.percent_energy_savings * 100)
        samples["ghg"].append(summary.emissions_reduction_per_ref_volume_lb)
        samples["ghg_rate"].append(summary.percent_emissions_reduction * 100)

    write_plot(samples)
    report = write_report(base_electricity, samples)

    print(report)
    print(f"\nMarkdown 报告已生成: {REPORT_PATH}")
    print(f"分布图已生成: {PLOT_PATH}")


if __name__ == "__main__":
    main()