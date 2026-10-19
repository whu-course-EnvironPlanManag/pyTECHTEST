# 实训案例二：先进催化剂合成 (Manufacturilium Catalyst)

## 1. 案例背景
本案例取自美国能源部官方复杂工业示范项目（`TECHTEST 1.0 Manufacturilium Catalyst.xlsx`）。
- **行业应用**：化学品与特种材料加工行业中的大宗均相/多相催化反应；
- **传统商业基准技术（Commercial Benchmark）**：采用传统配方的贵金属铝基催化剂（含铂 Platinum、氧化铝 Alumina 等），催化效率较低且原料消耗大；
- **拟开发先进新技术（New Technology）**：采用全新活性组分与高选择性结构的新型催化剂，单耗更低、反应选择性显著提升。

---

## 2. 核心考查机制与工程难点 (必读)

本案例考查两个极为重要的工业技术经济与生命周期评价机制：

### 难点 1：非等量替代比（Equivalence Ratio）
- 在评估基准中，由于新催化剂活性显著提高，**生产相同批次的目标产物，仅需使用 10 kg 新技术催化剂，即可等效替代 13.5 kg 的传统基准催化剂**。
- **参数填报要求**：在 `functional_unit` 中：
  - `reference_volume: 10.0`
  - `equivalence_ratio: 1.35`
- 计算图网在评估基准技术时，会自动将基准物耗、能耗与排放乘以 $1.35$，以确保在**完全相同的产出功能单位**下进行公平对标。

### 难点 2：原材料回收与副产物综合利用抵扣（Credit）
- 新技术工艺中引入了废催化剂清洁回收机制（Clean Catalyst Recovery），每次使用产生副产物回收抵扣收益。
- **参数填报要求**：在 `new_technology.materials` 清单中增加一项：
  ```yaml
  - name: "*Clean Catalyst Credit*"
    amount_per_ref_volume: 1.0
    unit: "Credit"
    unit_price: -500.0  # 负单价表示收益抵扣，每基准量扣减 $500 成本！
    embodied_energy_factor: 0.0
    embodied_ghg_factor: 0.0
  ```

---

## 3. 验收基准目标（数值精确吻合）
当你补全 `student_template.yaml` 并运行验证脚本后，必须达到如下产出指标：
1. **单位产品制造成本节约**：$\Delta\text{Cost} = \$581.50 / 10\text{ kg}$（节约比例 $19.92\%$）
2. **单位产品初级能耗节约**：$\Delta\text{Energy} = 0.86\text{ MMBtu} / 10\text{ kg}$（节约比例 $39.05\%$）
3. **单位产品温室气体减排**：$\Delta\text{GHG} = 1,329.90\text{ lb CO2e} / 10\text{ kg}$（减排比例 $74.82\%$）
4. **全美完全推广年化降碳量**：$346,254.45\text{ t CO2e/年}$

---

## 4. 本地运行验证
在补全 `student_template.yaml` 后，在当前目录运行自测脚本：
```bash
python practice_classroom/case2_catalyst/verify_case2.py
```
若完全通过，即可提交至个人 Git 分支！
