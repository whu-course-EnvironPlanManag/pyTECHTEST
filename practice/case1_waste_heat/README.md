# 实训案例一：工业余热回收系统 (Waste Heat Recovery)

## 1. 案例背景
本案例取自美国能源部官方示例：饮料制造行业工业废水降温工艺（`Example TECHTEST 1.0 Waste Heat Recovery (Process).xlsx`）。
- **传统商业基准技术（Commercial Benchmark）**：采用 4 台传统的蒸发式冷凝器（Evaporative Condensers），耗电量大，设备投资高；
- **拟开发低碳新技术（New Technology）**：采用先进工业热泵余热回收系统（Industrial Heat Pump / Waste Heat Recovery System），大幅降低制冷耗电量，回收低温余热。

---

## 2. 核心实验任务
同学们需要根据 `data/excel_templates/Example TECHTEST 1.0 Waste Heat Recovery (Process).xlsx` 中记录的参数，补全本目录下的 [`student_template.yaml`](student_template.yaml) 配置文件，并使用 Python 计算图网完成对标。

### 关键参数对照表（从 Excel Sheet 映射）
| 序号 | 模块与维度 | 官方 Excel 对应工作表 | 关键参数要求 |
| :--- | :--- | :--- | :--- |
| 1 | **功能单位 (FU)** | Sheet 4 ('Project & FU') | 评估基准量为 **2.0 Million Gallons** 冷却废水；替代比为 **1.0**。 |
| 2 | **全国市场规模** | Sheet 4 ('Project & FU') | 美国年化市场总量 **10,000 MG**，目标渗透率 **10%**（即 1,000 MG/年）。 |
| 3 | **基准技术设备投资** | Sheet 10 ('CapEx') | 4台蒸发冷凝器总价 **$1,000,000**，寿命 **25 年**，维护费率 **5%**。 |
| 4 | **新技术设备投资** | Sheet 10 ('CapEx') | 余热回收机组总价 **$254,305.60**，寿命 **10 年**，维护费率 **5%**。 |
| 5 | **综合人工** | Sheet 11 ('OpEx') | 基准 FTE 为 **0.03317**，新技术 FTE 为 **0.00962**；年薪 $75,000，综合福利间接费率 **72%**。 |
| 6 | **电力公用工程** | Sheet 8 ('Mfg Energy') | 电价为 **$0.0718/kWh**；基准电耗 **3,758.4 kWh/ref**，新技术电耗 **1,548.8 kWh/ref**。 |

---

## 3. 验收基准目标（数值精确吻合）
当你补全 `student_template.yaml` 并运行验证脚本后，必须达到如下产出指标：
1. **单位产品成本节约**：$\Delta\text{Cost} = \$214.00$（节约比例 $52.41\%$）
2. **单位产品初级能耗节约**：$\Delta\text{Energy} = 7.58\text{ MMBtu}$（降幅 $58.70\%$）
3. **单位产品温室气体减排**：$\Delta\text{GHG} = 818.69\text{ lb CO2e}$（减排 $58.79\%$）
4. **简单静态投资回收期**：由于新技术的设备投资大幅低于基准技术（无需额外增量投资），计算回收期为负值（立即实现净节约）。

---

## 4. 本地运行验证
在补全 `student_template.yaml` 后，在当前目录运行自测脚本：
```bash
python practice/case1_waste_heat/verify_case1.py
```
若完全通过，即可提交至个人 Git 分支！
