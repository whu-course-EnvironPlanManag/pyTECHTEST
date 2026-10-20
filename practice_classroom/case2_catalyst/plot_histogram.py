# -*- coding: utf-8 -*-
"""读取 sampled_results.csv，绘制 GHG 减排量的蒙特卡洛分布直方图并保存 PNG。"""
import csv
import statistics
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "sampled_results.csv"
OUT_PNG = HERE / "monte_carlo_ghg_histogram.png"

ghg = []
with open(CSV_PATH, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        ghg.append(float(row["ghg_reduction_lb"]))

ghg.sort()
n = len(ghg)


def pct(q):
    idx = (n - 1) * q
    a, b = int(idx), min(int(idx) + 1, n - 1)
    return ghg[a] * (1 - (idx - a)) + ghg[b] * (idx - a)


mean = statistics.mean(ghg)
p5, p50, p95 = pct(0.05), pct(0.50), pct(0.95)
baseline = 1329.90  # 官方基准值（factor=500）

fig, ax = plt.subplots(figsize=(9, 5.5), dpi=150)
ax.hist(ghg, bins=24, color="#4C72B0", edgecolor="white", alpha=0.85)

ax.axvline(mean, color="#C44E52", linestyle="-", linewidth=2, label=f"均值 {mean:.1f}")
ax.axvline(p5, color="#55A868", linestyle="--", linewidth=1.5, label=f"P5 {p5:.1f}")
ax.axvline(p95, color="#55A868", linestyle="--", linewidth=1.5, label=f"P95 {p95:.1f}")
ax.axvline(baseline, color="gray", linestyle=":", linewidth=1.5, label=f"官方基准 {baseline:.1f}")

ax.set_xlabel("单位产品温室气体减排量 (lb CO2e / 10 kg)")
ax.set_ylabel("抽样频次")
ax.set_title("蒙特卡洛不确定性分析（N=1000）\n扰动参数：铂 Platinum 隐含碳因子 (±20%)")
ax.legend(loc="upper right")
ax.grid(axis="y", alpha=0.25)

fig.tight_layout()
fig.savefig(OUT_PNG)
print(f"已生成直方图: {OUT_PNG}")
print(f"均值={mean:.2f}  标准差={statistics.stdev(ghg):.2f}  P5={p5:.2f}  P50={p50:.2f}  P95={p95:.2f}")