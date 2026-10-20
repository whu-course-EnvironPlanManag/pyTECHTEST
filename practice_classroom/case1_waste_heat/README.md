# 案例一：工业余热回收系统

## 案例与配置

本练习采用美国能源部（US DOE）饮料制造废水冷却案例，对比余热回收热泵与蒸发式冷凝器。配置文件为 [`student_template.yaml`](student_template.yaml)，参考工作簿为 [`Example TECHTEST 1.0 Waste Heat Recovery (Process).xlsx`](../TECHTEST_tool-Conceived-by-USDOE/Example%20TECHTEST%201.0%20Waste%20Heat%20Recovery%20(Process).xlsx)。

学生任务 1.1–1.6 对应的设备投资、人工和电耗字段均已在 YAML 中填写并通过案例自测。参数来源单元格已注释在配置旁。`John Doe` 是工作簿 `Project Basics & Benchmarks!C10` 中的示例项目负责人，不是学生姓名。数值在仓库原始模板中已存在；本次提交核对并说明了配置，没有擅自改动数值。

| 参数 | 案例值 | 工作簿来源 |
|---|---:|---|
| 功能单位 | 2.0 Million Gallons | `Functional Unit!D20`、`D29` |
| 新技术设备购置价 / 寿命 | $254,305.60 / 10 年 | `CapEx!E22`、`F22` |
| 基准设备购置价 / 寿命 | $1,000,000 / 25 年 | `CapEx!M22`、`N22` |
| 新技术 / 基准维护费率 | 5% / 5% | `CapEx!G43`、`O43` |
| 新技术 / 基准操作人员 FTE | 0.009615 / 0.033173 | `OpEx!C22`、`J22` |
| 人工年薪 / 福利间接费率 | $75,000 / 72% | `OpEx!D22`、`E22`、`K22`、`L22` |

**电耗单位待核实：**练习 YAML 将新技术和基准电耗写为 1,548.8 与 3,758.4 `kWh/ref`。官方工作簿 `Manufacturing Energy!D17`、`N17` 使用 `MMBtu/ref` 单位，不能直接视为相同单位的数值。本次保留仓库模板原值，没有自行换算；请教师确认课程要求采用哪组数据/单位。

## 验证结果

运行案例验证：

```powershell
python practice_classroom/case1_waste_heat/verify_case1.py
```

| 指标 | DOE 基准 | 本地结果 | 相对偏差 |
|---|---:|---:|---:|
| 单位产品成本节约 | $214.00 | $214.00 | 0.00% |
| 单位产品初级能耗节约 | 7.58 MMBtu | 7.58 MMBtu | 0.00% |
| 单位产品碳减排量 | 818.69 lb CO2e | 818.69 lb CO2e | 0.00% |

本地案例验证通过；仓库测试 `python -m pytest -v tests/` 为 17/17 通过。

## 敏感性与不确定性检查

仓库进阶 Notebook 展示电价与电网情景的确定性敏感性扫描。案例工作簿和案例配置未见概率分布、置信区间或蒙特卡洛不确定性分析。本次仅检查并记录现有内容，没有新增不确定性分析。
