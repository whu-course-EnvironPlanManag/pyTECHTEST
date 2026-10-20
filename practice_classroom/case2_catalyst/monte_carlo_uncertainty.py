# -*- coding: utf-8 -*-
"""
案例二 · 蒙特卡洛不确定性分析（Monte Carlo, N=1000）

要点：先选"一个"不确定输入参数，给它一个概率分布，抽样 1000 次代入引擎重算，
      观察某个输出指标（成本节约 / 能耗节约 / GHG 减排量）的分布。

说明（重要）：在本引擎里
  - 扰动 equivalence_ratio  ->  只会改变【成本节约】（CapEx/人工/维护按基准量折算），
                                不影响能耗与 GHG（它们按"每基准量"的固定用量计算）。
  - 扰动某材料的 embodied_ghg_factor ->  直接改变【GHG 减排量】。

因此用 MODE 切换两种典型做法，默认做 GHG（更贴合环境规划主题）。
"""
import copy
import csv
import random
import statistics
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pytechtest import TechTestFullEngine
from pytechtest.models.full_entry_input import FullEntryInput

YAML_PATH = ROOT / "practice_classroom" / "case2_catalyst" / "student_template.yaml"
OUT_CSV = Path(__file__).resolve().parent / "sampled_results.csv"

# ----------------------------- 可调参数 -------------------------------------
N_SAMPLES = 1000          # 抽样次数
SEED = 42                 # 随机种子（复现用）
MODE = "ghg"              # "ghg"：铂的隐含碳因子（影响 GHG）；"cost"：equivalence_ratio（影响成本）
SPREAD = 0.20             # 相对波动幅度（±20%）
# ---------------------------------------------------------------------------

# 基准值（对应两种模式）
if MODE == "ghg":
    BASELINE = 500.0      # 基准催化剂 铂 Platinum 的 embodied_ghg_factor (lb CO2e/kg)
    param_desc = "Platinum embodied_ghg_factor"
else:
    BASELINE = 1.35       # equivalence_ratio
    param_desc = "equivalence_ratio"

LO, HI = BASELINE * (1 - SPREAD), BASELINE * (1 + SPREAD)
random.seed(SEED)

with open(YAML_PATH, encoding="utf-8") as f:
    base = yaml.safe_load(f)


def apply_perturbation(cfg: dict, value: float) -> None:
    """把抽样值写回配置（按 MODE 决定写哪个字段）。"""
    if MODE == "ghg":
        # 找到基准技术里的 Platinum，改它的隐含碳因子
        for m in cfg["commercial_benchmark"]["materials"]:
            if m["name"].lower() == "platinum":
                m["embodied_ghg_factor"] = value
                return
        raise RuntimeError("未找到 Platinum 材料项")
    else:
        cfg["functional_unit"]["equivalence_ratio"] = value


rows = []
for i in range(N_SAMPLES):
    value = random.uniform(LO, HI)          # 均匀分布 U(LO, HI)
    # value = random.gauss(BASELINE, BASELINE*SPREAD/2)   # 备选：正态分布

    cfg_data = copy.deepcopy(base)
    apply_perturbation(cfg_data, value)

    s = TechTestFullEngine(FullEntryInput(**cfg_data)).run().summary
    rows.append({
        "sample": i,
        param_desc: value,
        "cost_savings_$": s.cost_savings_per_ref_volume,
        "energy_savings_mmbtu": s.energy_savings_per_ref_volume_mmbtu,
        "ghg_reduction_lb": s.emissions_reduction_per_ref_volume_lb,
    })


def summary(name, values, unit):
    vals = sorted(values)
    n = len(vals)
    def pct(q):
        idx = (n - 1) * q
        a, b = int(idx), min(int(idx) + 1, n - 1)
        return vals[a] * (1 - (idx - a)) + vals[b] * (idx - a)
    print(f"\n【{name}】")
    print(f"  均值      = {statistics.mean(vals):.4f} {unit}")
    print(f"  标准差    = {statistics.stdev(vals):.4f} {unit}" if n > 1 else f"  标准差    = 0.0000 {unit}")
    print(f"  最小值    = {vals[0]:.4f} {unit}")
    print(f"  最大值    = {vals[-1]:.4f} {unit}")
    print(f"  P5        = {pct(0.05):.4f}")
    print(f"  中位数P50 = {pct(0.50):.4f}")
    print(f"  P95       = {pct(0.95):.4f}")
    return vals


print(f"扰动参数: {param_desc} ~ U({LO:.3f}, {HI:.3f})  (±{SPREAD*100:.0f}%), N={N_SAMPLES}, seed={SEED}")

cost = summary("单位产品成本节约", [r["cost_savings_$"] for r in rows], "$/10kg")
energy = summary("单位产品初级能耗节约", [r["energy_savings_mmbtu"] for r in rows], "MMBtu/10kg")
ghg = summary("单位产品温室气体减排", [r["ghg_reduction_lb"] for r in rows], "lb CO2e/10kg")


def histogram(name, values, unit):
    vals = sorted(values)
    mn, mx = vals[0], vals[-1]
    print(f"\n【{name} 分布直方图】(ASCII)")
    if mx - mn < 1e-9:
        print(f"  所有样本均为 {mn:.4f} {unit}（该参数不影响本指标，无分布）")
        return
    bins = 12
    width = (mx - mn) / bins
    counts = [0] * bins
    for v in vals:
        counts[min(int((v - mn) / width), bins - 1)] += 1
    max_count = max(counts)
    for i in range(bins):
        lo_b, hi_b = mn + i * width, mn + (i + 1) * width
        bar = "#" * int(counts[i] / max_count * 40)
        print(f"  {lo_b:9.2f} ~ {hi_b:9.2f} | {bar:<40} {counts[i]}")


# 只对"受扰动的指标"画直方图
if MODE == "ghg":
    histogram("温室气体减排量", ghg, "lb CO2e/10kg")
else:
    histogram("成本节约", cost, "$/10kg")

with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
print(f"\n已写出抽样明细: {OUT_CSV}")