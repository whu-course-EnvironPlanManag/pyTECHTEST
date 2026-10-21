#!/usr/bin/env python3
"""
Verification Script for Student Practice Case 1: Waste Heat Recovery.
Runs the student's YAML file and compares output against US DOE Golden Benchmarks.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from pytechtest import TechTestFullEngine, TechTestReporter


def main():
    yaml_path = Path(__file__).resolve().parent / "student_template.yaml"
    print(f"\n=======================================================")
    print(f"🔍 正在评测学生实训案例一 (余热回收模型): {yaml_path.name}")
    print(f"=======================================================\n")

    if not yaml_path.exists():
        print(f"❌ 错误：未找到学生配置文件 {yaml_path}", file=sys.stderr)
        sys.exit(1)

    try:
        engine = TechTestFullEngine.from_yaml(yaml_path)
        results = engine.run()
    except Exception as e:
        print(f"❌ 运行报错：模型解析或计算图网执行失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 打印终端仪表盘
    TechTestReporter.print_terminal_dashboard(results)

    # 提取核心指标
    s = results.summary
    cost_diff = s.cost_savings_per_ref_volume
    energy_diff = s.energy_savings_per_ref_volume_mmbtu
    ghg_diff = s.emissions_reduction_per_ref_volume_lb
    payback_years = s.simple_payback_years

    # 官方基准目标
    golden_cost = 214.00
    golden_energy = 7.58
    golden_ghg = 818.69

    print("\n--- 🎯 与美国能源部官方基准对齐校验 ---")
    print(f"1. 单位成本节约:   学生值 = ${cost_diff:.6f}  | 官方基准 = ${golden_cost:.2f}")
    print(f"2. 初级能耗节约:   学生值 = {energy_diff:.6f} MMBtu | 官方基准 = {golden_energy:.2f} MMBtu")
    print(f"3. 温室气体减排:   学生值 = {ghg_diff:.6f} lb CO2e | 官方基准 = {golden_ghg:.2f} lb CO2e")
    payback_display = f"{payback_years:.6f} 年" if payback_years is not None else "无法计算"
    print(f"4. 静态投资回收期: 学生值 = {payback_display} | 验收要求 = 负值")

    err_cost = abs(cost_diff - golden_cost) / golden_cost
    err_energy = abs(energy_diff - golden_energy) / golden_energy
    err_ghg = abs(ghg_diff - golden_ghg) / golden_ghg

    print("\n--- 📊 相对官方基准偏差 ---")
    print(f"1. 单位成本节约相对偏差: {err_cost:.6%}")
    print(f"2. 初级能耗节约相对偏差: {err_energy:.6%}")
    print(f"3. 温室气体减排相对偏差: {err_ghg:.6%}")

    payback_is_negative = payback_years is not None and payback_years < 0
    if err_cost < 0.001 and err_energy < 0.001 and err_ghg < 0.001 and payback_is_negative:
        print("\n🎉 恭喜！各项指标与美国能源部官方基准严格 100% 对齐！案例一练习顺利完成！")
        print("💡 提示：请执行 git add、git commit 并提交至你的个人实训分支！\n")
    else:
        print("\n⚠️ 提示：计算结果与官方基准或回收期要求存在偏差，请核对 student_template.yaml 中的填报参数！\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
