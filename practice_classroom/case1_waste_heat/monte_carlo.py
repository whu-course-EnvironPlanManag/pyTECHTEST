"""Single-parameter electricity-price uncertainty analysis (1,000 trials)."""
import csv
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from pytechtest import TechTestFullEngine


def main():
    folder = Path(__file__).resolve().parent
    config = TechTestFullEngine.from_yaml(folder / "student_template.yaml").config
    electricity = lambda sub: [e for e in sub.energy_items if e.energy_source.lower() == "electricity"]
    new_items = electricity(config.new_technology)
    old_items = electricity(config.commercial_benchmark)
    assert len(new_items) == len(old_items) == 1
    mode = new_items[0].unit_price
    assert mode == old_items[0].unit_price and mode > 0
    low, high = mode * 0.8, mode * 1.2
    seed, count = 20261020, 1000
    prices = np.random.default_rng(seed).triangular(low, mode, high, count)
    baseline = TechTestFullEngine(config).run()
    rows = []
    for i, price in enumerate(prices, 1):
        sample = config.model_copy(deep=True)
        for subsystem in (sample.new_technology, sample.commercial_benchmark):
            for item in electricity(subsystem):
                item.unit_price = float(price)
        result = TechTestFullEngine(sample).run()
        s = result.summary
        expected = baseline.summary.cost_savings_per_ref_volume + (old_items[0].amount_per_ref_volume - new_items[0].amount_per_ref_volume) * (price - mode)
        assert np.isclose(s.cost_savings_per_ref_volume, expected)
        assert np.isclose(s.energy_savings_per_ref_volume_mmbtu, baseline.summary.energy_savings_per_ref_volume_mmbtu)
        assert np.isclose(s.emissions_reduction_per_ref_volume_lb, baseline.summary.emissions_reduction_per_ref_volume_lb)
        rows.append(dict(trial=i, electricity_price_usd_per_kwh=float(price), cost_savings_usd_per_fu=s.cost_savings_per_ref_volume, cost_savings_fraction=s.percent_cost_savings, simple_payback_years=s.simple_payback_years, annual_market_cost_savings_usd=s.annual_potential_us_cost_savings, energy_savings_mmbtu_per_fu=s.energy_savings_per_ref_volume_mmbtu, ghg_reduction_lb_co2e_per_fu=s.emissions_reduction_per_ref_volume_lb))
    with (folder / "monte_carlo_samples.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    def stats(key):
        a = np.array([r[key] for r in rows])
        return dict(mean=float(a.mean()), sample_std=float(a.std(ddof=1)), minimum=float(a.min()), p5=float(np.quantile(a, .05)), median=float(np.median(a)), p95=float(np.quantile(a, .95)), maximum=float(a.max()))
    summary = dict(trials=count, seed=seed, distribution="triangular", assumption="Analyst-assumed +/-20% bounds; not a fitted empirical distribution", price_low=low, price_mode=mode, price_high=high, baseline_cost_savings=baseline.summary.cost_savings_per_ref_volume, positive_cost_savings_trials=sum(r["cost_savings_usd_per_fu"] > 0 for r in rows), statistics={k: stats(k) for k in rows[0] if k != "trial"})
    (folder / "monte_carlo_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    axes[0].hist(prices, bins=30, color="#3c78a8", edgecolor="white")
    axes[0].axvline(mode, color="#b64032", linestyle="--", label="Baseline")
    axes[0].set(xlabel="Electricity price (USD/kWh)", ylabel="Trials", title="Triangular electricity price: 1,000 draws")
    savings = [r["cost_savings_usd_per_fu"] for r in rows]
    axes[1].hist(savings, bins=30, color="#39826a", edgecolor="white")
    for q in (.05, .95):
        axes[1].axvline(np.quantile(savings, q), color="#b64032", linestyle="--", label=f"P{int(q*100)}")
    axes[1].set(xlabel="Cost savings (USD / functional unit)", ylabel="Trials", title="Cost savings distribution")
    for ax in axes:
        ax.legend(frameon=False)
        ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(folder / "monte_carlo.png", dpi=180)
    plt.close(fig)
    c = summary["statistics"]["cost_savings_usd_per_fu"]
    p = summary["statistics"]["simple_payback_years"]
    report = f"""# 案例一：电价不确定性分析

## 方法与假设

选取电价为唯一不确定参数，采用三角分布：最低 {low:.5f}、最可能 {mode:.5f}、最高 {high:.5f} 美元/kWh。范围为课程基准上下浮动 20%，属于分析者设定的情景假设，没有作为历史电价统计分布。抽样 1000 次，随机种子为 {seed}，使用 NumPy default_rng。

每次将同一抽样电价同时用于新技术和商业基准，避免将同一市场中的电价误设为两个独立变量。其他输入（电耗、投资、寿命、人工、材料、电网排放因子、市场规模）固定。每次调用完整课程引擎计算。

功能单位为冷却 2 Million Gallons 废水。输出重点为每功能单位成本节约，同时记录成本降幅、静态回收期、市场年节约、能耗节约和减排量。

## 结果

| 成本节约指标 | 美元/功能单位 |
|---|---:|
| 基准电价下结果 | {baseline.summary.cost_savings_per_ref_volume:.4f} |
| 蒙特卡洛均值 | {c['mean']:.4f} |
| 样本标准差 | {c['sample_std']:.4f} |
| 中位数 | {c['median']:.4f} |
| P5 | {c['p5']:.4f} |
| P95 | {c['p95']:.4f} |
| 抽样最小值 | {c['minimum']:.4f} |
| 抽样最大值 | {c['maximum']:.4f} |

1000 次中有 {summary['positive_cost_savings_trials']} 次成本节约大于零。该样本比例仅适用于本次分布及固定条件，不等于实际项目的成功概率。P5–P95 是输出分布的中央 90% 分位区间，不是均值的置信区间。

![电价与成本节约分布](monte_carlo.png)

## 解释与核验

两方案每功能单位电耗差为 3758.4 - 1548.8 = 2209.6 kWh。成本节约满足：基准节约 + 2209.6 ×（抽样电价 - 0.0718）。因此电价每上涨 0.01 美元/kWh，成本节约增加 22.096 美元/功能单位。脚本逐次将引擎结果与该独立关系核对。

电价区间两端的理论成本节约约为 {baseline.summary.cost_savings_per_ref_volume + 2209.6*(low-mode):.4f} 至 {baseline.summary.cost_savings_per_ref_volume + 2209.6*(high-mode):.4f} 美元/功能单位，整个假设区间均为正，因此在该单参数范围内，新技术的成本优势稳定。1000 次抽样不能排除其他参数或更宽电价范围下的不同结果。

回收期均值为 {p['mean']:.4f} 年，P5–P95 为 {p['p5']:.4f} 至 {p['p95']:.4f} 年。负值源于新技术初始投资更低，不能解释为现实中经过负数年回本。回收期分位数与成本节约分位数分别统计，不代表同一次抽样配对。

能耗节约固定为 {baseline.summary.energy_savings_per_ref_volume_mmbtu:.8f} MMBtu/功能单位，减排固定为 {baseline.summary.emissions_reduction_per_ref_volume_lb:.8f} lb CO2e/功能单位，因为本次只改变价格，没有改变能耗或电网排放因子。脚本对每次抽样均检查这两项不变。

分析沿用课程引擎，维护费重复计入等已知局限见 submission.md。本分析不修正这些实现，也不宣称对原 Excel 完整模型完成不确定性验证。

## 复现与文件

安装仓库依赖后，在仓库根目录运行：

```powershell
python practice_classroom/case1_waste_heat/monte_carlo.py
```

monte_carlo_samples.csv 保存全部 1000 次输入输出；monte_carlo_summary.json 保存统计量；monte_carlo.png 为分布图。固定种子用于复现，有限样本分位数仍有蒙特卡洛抽样误差。
"""
    (folder / "uncertainty_analysis.md").write_text(report, encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
