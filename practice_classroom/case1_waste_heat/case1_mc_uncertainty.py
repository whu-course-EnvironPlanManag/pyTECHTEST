"""
Case1 工业余热回收——新技术电耗（单参数）蒙特卡洛不确定性分析（升级版）

作业要求：选择一个参数，进行 1000 次蒙特卡洛抽样，输出 Py 文件 / md 报告 / 分布图。

本版选择【新技术电力公用工程消耗量】为唯一不确定参数：
  - 基准值 1548.8 kWh/ref（DOE Golden Case），对数正态分布，变异系数 COV=10%；
  - 其余参数（CapEx、人工、材料、电价、基准技术电耗等）全部锁定为 DOE 基准值；
  - 不确定性线性传播至三大决策指标：ΔCost / ΔEnergy / ΔGHG；
  - 额外进行【解析解验证】：σ(指标) = |斜率| × σ_E 的理论值与蒙特卡洛实测值对照。
  - 固定随机种子 20261020，结果可复现；输出样本明细 CSV、统计 JSON、两张分布图。

运行环境：Python 3 + numpy + matplotlib（scipy 可选，用于 KDE 平滑曲线）。
"""
import numpy as np
import json
import csv

# ========== 固定输入参数（全部来自 student_template.yaml / verify_case1.py） ==========
BASE_ELEC = 3758.4               # 基准工艺电耗 kWh/ref
NEW_ELEC_REF = 1548.8            # 新技术电耗基准值 kWh/ref（DOE Golden Case）
ELEC_DIFF_REF = BASE_ELEC - NEW_ELEC_REF   # = 2209.6 kWh/ref

ELEC_PRICE = 0.0718              # 电价 $/kWh（固定，不作不确定参数）
FIXED_SAVING = 214.00 - ELEC_DIFF_REF * ELEC_PRICE   # 非电耗部分固定节约 = 55.35072 $/ref

# 线性换算因子（由 DOE 基准推导：电耗差 2209.6 kWh → 7.58 MMBtu / 818.69 lb CO2e / 214.00 $）
ENERGY_FACTOR = 7.58 / ELEC_DIFF_REF      # MMBtu per kWh
GHG_FACTOR = 818.69 / ELEC_DIFF_REF       # lb CO2e per kWh

# ========== 不确定性分布设定：对数正态（算术均值=1548.8，COV=10%） ==========
COV = 0.10
N_TRIALS = 1000
RANDOM_SEED = 20261020

# 对数正态参数换算：E[X]=μ，COV=σ/μ → σ_ln = sqrt(ln(1+COV²))，μ_ln = ln(μ) - σ_ln²/2
SIGMA_LN = float(np.sqrt(np.log(1.0 + COV**2)))
MU_LN = float(np.log(NEW_ELEC_REF) - 0.5 * SIGMA_LN**2)

# ========== 蒙特卡洛抽样 ==========
rng = np.random.default_rng(RANDOM_SEED)
E_new = rng.lognormal(MU_LN, SIGMA_LN, size=N_TRIALS)      # 新技术电耗样本 (kWh/ref)

dE = BASE_ELEC - E_new                                       # 电耗差
dCost = dE * ELEC_PRICE + FIXED_SAVING                      # ΔCost 单位成本节约 ($/ref)
dEnergy = dE * ENERGY_FACTOR                                # ΔEnergy 一次能源节约 (MMBtu/ref)
dGHG = dE * GHG_FACTOR                                      # ΔGHG 温室气体减排 (lb CO2e/ref)

# ========== 描述性统计 ==========
def summarize(x, doe_base):
    return {
        "DOE基准": doe_base,
        "均值": round(float(np.mean(x)), 4),
        "中位数": round(float(np.median(x)), 4),
        "标准差": round(float(np.std(x)), 4),
        "P5": round(float(np.percentile(x, 5)), 4),
        "P95": round(float(np.percentile(x, 95)), 4),
        "CI2.5": round(float(np.percentile(x, 2.5)), 4),
        "CI97.5": round(float(np.percentile(x, 97.5)), 4),
        "变异系数CV%": round(float(np.std(x) / np.mean(x) * 100), 2),
    }

stats = {
    "method": "单参数不确定性分析（新技术电耗）",
    "distribution": "对数正态（算术均值1548.8 kWh/ref，COV=10%），其余参数锁定DOE基准",
    "n_trials": N_TRIALS,
    "random_seed": RANDOM_SEED,
    "electricity_dCost": summarize(dCost, 214.00),
    "electricity_dEnergy": summarize(dEnergy, 7.58),
    "electricity_dGHG": summarize(dGHG, 818.69),
    "all_positive": {
        "dCost": bool((dCost > 0).all()),
        "dEnergy": bool((dEnergy > 0).all()),
        "dGHG": bool((dGHG > 0).all()),
    },
    "worst_case": round(float(dCost.min()), 4),   # 最差情景成本节约
    "sample_E_new": {
        "mean": round(float(E_new.mean()), 4),
        "std": round(float(E_new.std()), 4),
        "min": round(float(E_new.min()), 4),
        "max": round(float(E_new.max()), 4),
    },
}

# ========== 解析解验证（差异化亮点）：σ(指标) = |斜率| × σ_E ==========
sigma_E_emp = float(np.std(E_new))
analytic = {
    "dCost": ELEC_PRICE * sigma_E_emp,
    "dEnergy": ENERGY_FACTOR * sigma_E_emp,
    "dGHG": GHG_FACTOR * sigma_E_emp,
}
empirical = {
    "dCost": float(np.std(dCost)),
    "dEnergy": float(np.std(dEnergy)),
    "dGHG": float(np.std(dGHG)),
}
verification = {}
for k in analytic:
    rel_err = abs(analytic[k] - empirical[k]) / empirical[k] * 100
    verification[k] = {
        "解析预测σ": round(analytic[k], 4),
        "蒙特卡洛实测σ": round(empirical[k], 4),
        "相对误差%": round(rel_err, 3),
    }
stats["analytic_verification"] = verification

# ========== 输出：CSV（样本明细） ==========
with open("case1_mc_samples.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["trial", "new_elec_kwh", "dCost_usd", "dEnergy_mmbtu", "dGHG_lb"])
    for i in range(N_TRIALS):
        writer.writerow([i + 1, round(E_new[i], 4), round(dCost[i], 4),
                         round(dEnergy[i], 4), round(dGHG[i], 4)])

# ========== 输出：JSON（统计指标） ==========
with open("case1_mc_stats.json", "w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

# ========== 输出：图1 三指标分布直方图 + KDE ==========
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    from scipy.stats import gaussian_kde
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
plot_specs = [
    (dCost, "ΔCost 单位成本节约 ($/ref)", "dCost", 214.00),
    (dEnergy, "ΔEnergy 一次能源节约 (MMBtu/ref)", "dEnergy", 7.58),
    (dGHG, "ΔGHG 温室气体减排 (lb CO2e/ref)", "dGHG", 818.69),
]
for ax, (data, title, key, base) in zip(axes, plot_specs):
    ax.hist(data, bins=35, density=True, color="#4C72B0", edgecolor="white", alpha=0.75, label="直方图")
    if HAS_SCIPY:
        xs = np.linspace(data.min(), data.max(), 200)
        kde = gaussian_kde(data)
        ax.plot(xs, kde(xs), color="#C44E52", lw=2, label="KDE")
    ax.axvline(stats["electricity_" + key]["均值"], color="red", ls="--",
               label="均值 %.2f" % stats["electricity_" + key]["均值"])
    ax.axvspan(stats["electricity_" + key]["CI2.5"], stats["electricity_" + key]["CI97.5"],
               color="orange", alpha=0.15, label="95% CI")
    ax.axvline(base, color="green", ls=":", lw=1.5, label="DOE基准 %.2f" % base)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_xlabel("数值")
    ax.set_ylabel("概率密度")
    ax.legend(fontsize=7)
    ax.grid(True, ls="--", alpha=0.5)
fig.suptitle("Case1 新技术电耗不确定性下三大决策指标分布（1000次蒙特卡洛，对数正态 COV=10%）",
             fontsize=13, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig("case1_mc_histograms.png", dpi=150)

# ========== 输出：图2 三指标标准化箱线图（离散度对比） ==========
fig2, ax2 = plt.subplots(figsize=(9, 5.5))
# 标准化为相对 DOE 基准的百分比偏移，便于横向比较离散度
norm = {
    "ΔCost": (dCost / 214.00 - 1) * 100,
    "ΔEnergy": (dEnergy / 7.58 - 1) * 100,
    "ΔGHG": (dGHG / 818.69 - 1) * 100,
}
bp = ax2.boxplot(list(norm.values()), patch_artist=True,
                 medianprops=dict(color="red", lw=2),
                 flierprops=dict(marker="o", markersize=2, alpha=0.4))
ax2.set_xticks(range(1, len(norm) + 1), list(norm.keys()))
for patch, color in zip(bp["boxes"], ["#4C72B0", "#55A868", "#C44E52"]):
    patch.set_facecolor(color)
    patch.set_alpha(0.75)
ax2.axhline(0, color="green", ls=":", lw=1.5, label="DOE 基准 (0% 偏移)")
ax2.set_title("三大决策指标相对 DOE 基准的偏移分布对比（箱线图）", fontsize=13, fontweight="bold")
ax2.set_ylabel("相对基准偏移 (%)")
ax2.legend()
ax2.grid(True, ls="--", alpha=0.5)
fig2.tight_layout()
fig2.savefig("case1_mc_boxplot.png", dpi=150)

# ========== 终端摘要 ==========
s = stats["electricity_dCost"]
print("已完成 %d 次蒙特卡洛抽样（对数正态 COV=10%%，种子 %d）" % (N_TRIALS, RANDOM_SEED))
print("新技术电耗样本: 均值 %.4f | 标准差 %.4f | 范围 [%.4f, %.4f] kWh/ref"
      % (stats["sample_E_new"]["mean"], stats["sample_E_new"]["std"],
         stats["sample_E_new"]["min"], stats["sample_E_new"]["max"]))
print("-" * 60)
print("ΔCost  均值 %.4f | σ %.4f | P5 %.4f | P95 %.4f | 95%%CI [%.4f, %.4f]"
      % (s["均值"], s["标准差"], s["P5"], s["P95"], s["CI2.5"], s["CI97.5"]))
print("ΔEnergy 均值 %.4f | σ %.4f | 95%%CI [%.4f, %.4f]"
      % (stats["electricity_dEnergy"]["均值"], stats["electricity_dEnergy"]["标准差"],
         stats["electricity_dEnergy"]["CI2.5"], stats["electricity_dEnergy"]["CI97.5"]))
print("ΔGHG   均值 %.4f | σ %.4f | 95%%CI [%.4f, %.4f]"
      % (stats["electricity_dGHG"]["均值"], stats["electricity_dGHG"]["标准差"],
         stats["electricity_dGHG"]["CI2.5"], stats["electricity_dGHG"]["CI97.5"]))
print("全部为正: %s | 最差情景 ΔCost = %.4f $/ref" % (stats["all_positive"], stats["worst_case"]))
print("-" * 60)
print("解析解验证 σ(指标)=|斜率|×σ_E：")
for k, v in verification.items():
    print("  %-8s 解析 %.4f | 实测 %.4f | 相对误差 %.3f%%" % (k, v["解析预测σ"], v["蒙特卡洛实测σ"], v["相对误差%"]))
print("已生成：case1_mc_samples.csv / case1_mc_stats.json / case1_mc_histograms.png / case1_mc_boxplot.png")
#（注：内容由AI生成）
