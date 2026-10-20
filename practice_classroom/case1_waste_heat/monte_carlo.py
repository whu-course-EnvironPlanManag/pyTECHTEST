"""
案例一（工业余热回收系统）1000 次蒙特卡洛不确定性分析

对 student_template.yaml 中全部数值型输入参数（排除 trl 枚举常量）施加
三角分布 ±10% 扰动（最小值 0.9×基准、最可能值=基准、最大值 1.1×基准），
抽样 1000 次，每次调用完整 TECHTEST 计算图网，统计核心决策指标的分布。

输出（位于本目录）：
  monte_carlo_samples.csv   —— 1000 次明细（输入扰动值 + 输出指标）
  monte_carlo_summary.json  —— 统计量（均值/标准差/分位数/极值）
  monte_carlo.png           —— 核心指标分布直方图
"""

import csv
import json
import random
import sys
from copy import deepcopy
from pathlib import Path

import numpy as np
import yaml
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from pytechtest.models.full_entry_input import FullEntryInput
from pytechtest.engines.full_engine import TechTestFullEngine

CASE_DIR = Path(__file__).resolve().parent
TEMPLATE = CASE_DIR / "student_template.yaml"

N = 1000
SEED = 42
LO, HI = 0.9, 1.1          # 三角分布相对基准的下界 / 上界
EXCLUDE_KEYS = {"trl"}      # TRL 为枚举整数，不参与数值扰动

# (DashboardSummary 属性, 输出列名, 中文标签)
METRICS = [
    ("cost_savings_per_ref_volume", "cost_savings_usd_per_ref", "单位成本节约 ($/ref)"),
    ("percent_cost_savings", "percent_cost_savings", "成本节约比例"),
    ("energy_savings_per_ref_volume_mmbtu", "energy_savings_mmbtu_per_ref", "初级能耗节约 (MMBtu/ref)"),
    ("percent_energy_savings", "percent_energy_savings", "能耗降幅"),
    ("emissions_reduction_per_ref_volume_lb", "ghg_reduction_lb_co2e_per_ref", "温室气体减排 (lb CO2e/ref)"),
    ("percent_emissions_reduction", "percent_ghg_reduction", "GHG 减排比例"),
    ("simple_payback_years", "simple_payback_years", "静态回收期 (年)"),
    ("annual_potential_us_cost_savings", "annual_us_cost_savings_usd", "全美年均成本节约 ($/yr)"),
    ("annual_potential_us_energy_savings_mmbtu", "annual_us_energy_savings_mmbtu", "全美年均节能量 (MMBtu/yr)"),
    ("annual_potential_us_carbon_reduction_metric_tons", "annual_us_carbon_reduction_tons", "全美年均减排量 (t CO2e/yr)"),
]
HIST_IDX = [0, 2, 4, 6]    # 直方图聚焦 4 个核心指标


def perturb_collect(node, prefix=""):
    """递归扰动 float 叶子，返回 (扰动后节点, [(路径, 扰动值)...])。"""
    pairs = []
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            if k in EXCLUDE_KEYS:
                out[k] = v
            else:
                nv, c = perturb_collect(v, f"{prefix}.{k}" if prefix else k)
                out[k] = nv
                pairs.extend(c)
        return out, pairs
    if isinstance(node, list):
        out = []
        for i, v in enumerate(node):
            nv, c = perturb_collect(v, f"{prefix}[{i}]")
            out.append(nv)
            pairs.extend(c)
        return out, pairs
    if isinstance(node, bool):
        return node, pairs
    if isinstance(node, float):
        nv = node * random.triangular(LO, HI, 1.0)
        pairs.append((prefix, nv))
        return nv, pairs
    if isinstance(node, int):
        return node, pairs
    return node, pairs


def main():
    random.seed(SEED)
    np.random.seed(SEED)

    base_data = yaml.safe_load(TEMPLATE.read_text(encoding="utf-8"))
    out_attrs = [m[0] for m in METRICS]
    out_labels = [m[1] for m in METRICS]
    cn_labels = [m[2] for m in METRICS]

    # 基准（无扰动）结果
    base_summary = TechTestFullEngine(FullEntryInput(**deepcopy(base_data))).run().summary
    base_vals = [float(getattr(base_summary, a)) for a in out_attrs]

    # 第一次扰动确定参数路径顺序
    _, first_pairs = perturb_collect(deepcopy(base_data))
    param_paths = [p for p, _ in first_pairs]

    param_rows, output_rows = [], []
    for i in range(1, N + 1):
        data, pairs = perturb_collect(deepcopy(base_data))
        val_map = {p: v for p, v in pairs}
        param_rows.append([val_map[p] for p in param_paths])
        s = TechTestFullEngine(FullEntryInput(**data)).run().summary
        output_rows.append([np.nan if getattr(s, a) is None else float(getattr(s, a)) for a in out_attrs])
        if i % 250 == 0:
            print(f"    ... {i}/{N} 完成", flush=True)

    out_arr = np.array(output_rows, dtype=float)

    # ---- 明细 CSV ----
    csv_path = CASE_DIR / "monte_carlo_samples.csv"
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["iteration"] + param_paths + out_labels)
        for i in range(N):
            w.writerow([i + 1] + param_rows[i] + output_rows[i])

    # ---- 统计量 JSON ----
    statistics = {}
    for j, (attr, out_label, cn_label) in enumerate(METRICS):
        col = out_arr[:, j]
        statistics[out_label] = {
            "mean": float(np.nanmean(col)),
            "sample_std": float(np.nanstd(col)),
            "minimum": float(np.nanmin(col)),
            "p5": float(np.nanpercentile(col, 5)),
            "median": float(np.nanpercentile(col, 50)),
            "p95": float(np.nanpercentile(col, 95)),
            "maximum": float(np.nanmax(col)),
        }
    summary = {
        "trials": N,
        "seed": SEED,
        "distribution": "triangular",
        "assumption": f"Analyst-assumed +/-{int((1 - LO) * 100)}% bounds on ALL numeric inputs; not fitted empirical distributions",
        "sampled_parameters_count": len(param_paths),
        "baseline_cost_savings": base_vals[0],
        "positive_cost_savings_trials": int(np.sum(out_arr[:, 0] > 0)),
        "statistics": statistics,
    }
    json_path = CASE_DIR / "monte_carlo_summary.json"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- 直方图 ----
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, j in zip(axes.ravel(), HIST_IDX):
        col = out_arr[:, j]
        ax.hist(col, bins=40, color="#2b6cb0", edgecolor="white", alpha=0.85)
        ax.axvline(base_vals[j], color="#c53030", linestyle="--", linewidth=1.6, label=f"基准 {base_vals[j]:.4g}")
        ax.set_title(cn_labels[j], fontsize=11)
        ax.legend(fontsize=8)
        ax.grid(alpha=0.25)
    fig.suptitle("案例一核心决策指标不确定性分布（1000 次蒙特卡洛，全部参数三角 ±10%）", fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    png_path = CASE_DIR / "monte_carlo.png"
    fig.savefig(png_path, dpi=130)
    plt.close(fig)

    # ---- 终端统计表 ----
    print("\n" + "=" * 104)
    print(f"案例一蒙特卡洛不确定性分析（全部数值参数 · 三角 ±10% · N={N} · seed={SEED}）")
    print("=" * 104)
    print(f"{'指标':<26}{'基准':>12}{'均值':>12}{'标准差':>12}{'P5':>12}{'P50':>12}{'P95':>12}")
    print("-" * 104)
    for j in range(len(METRICS)):
        col = out_arr[:, j]
        print(f"{cn_labels[j]:<26}{base_vals[j]:>12.4f}{np.nanmean(col):>12.4f}{np.nanstd(col):>12.4f}"
              f"{np.nanpercentile(col, 5):>12.4f}{np.nanpercentile(col, 50):>12.4f}{np.nanpercentile(col, 95):>12.4f}")
    print("=" * 104)
    print(f"扰动参数数: {len(param_paths)}   正成本节约次数: {summary['positive_cost_savings_trials']}/{N}")
    print(f"明细: {csv_path}")
    print(f"汇总: {json_path}")
    print(f"直方图: {png_path}")
    print("\n完成。")


if __name__ == "__main__":
    main()