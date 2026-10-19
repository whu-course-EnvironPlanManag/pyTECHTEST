# 《环境规划与管理》课程随堂实训实践专区

欢迎进入 **US DOE TECHTEST 1.0 绿色低碳技术评估 Python 随堂实训**！

本项目为武汉大学《环境规划与管理》本科核心课程配套代码仓。同学们将通过新建 Git 分支、阅读美国能源部（US DOE）官方 Excel 评估案例、完成参数配置并运行 Python 计算图网，亲身体验如何将传统繁复的 Excel 工业评估工具转化为现代化、模块化、可复现的代码工程。

---

## 🎯 实训目标与两大练习案例

课程精选了 US DOE 官方发布的两个经典黄金基准案例（Excel 原始文件已内置于 `data/excel_templates/` 目录中）：

| 实验编号 | 案例名称 | 对应官方 Excel 文件 | 关键考查机制 |
| :--- | :--- | :--- | :--- |
| **案例一 (Case 1)** | **工业余热回收冷却系统**<br>(Waste Heat Recovery) | `data/excel_templates/Example TECHTEST 1.0 Waste Heat Recovery (Process).xlsx` | Method 1 全量分析法：设备 CapEx 直线折旧与 5% 维护费、公用工程（电力/冷却水）分项清单积分、投资回收期计算。 |
| **案例二 (Case 2)** | **先进催化剂合成**<br>(Manufacturilium Catalyst) | `data/excel_templates/TECHTEST 1.0 Manufacturilium Catalyst.xlsx` | 复杂工程工况：**非等量替代比（1.35x 等效系数）**、**原材料回收抵扣（负单价 Credit -$500）**、MFI 隐含碳多原料生命周期追踪。 |

---

## 🌿 Git 分支工作流指引 (Student Git Workflow)

遵循软件工程与团队协作规范（参考 `agency-agents` 的 Git Workflow Master 最佳实践），**严禁直接向 `main` 分支提交任何个人修改**。所有练习必须在独立个人分支上完成。

### 步骤 1：克隆代码仓并检出个人实训分支
在本地终端执行：
```bash
# 克隆代码仓
git clone https://github.com/whu-course-EnvironPlanManag/pyTECHTEST.git
cd pyTECHTEST

# 规范分支命名格式：student/<学号>-<姓名拼音>-<case1/case2>
# 例如：
git checkout -b student/2023300000-zhangsan-case1
```

### 步骤 2：完成指定案例的配置与计算
- **练习案例一**：进入 [`practice_classroom/case1_waste_heat/`](case1_waste_heat/)，阅读该目录下的 `README.md`，根据提示补全 `student_template.yaml` 中的 `# TODO` 项；
- **练习案例二**：进入 [`practice_classroom/case2_catalyst/`](case2_catalyst/)，阅读该目录下的 `README.md`，补全 `student_template.yaml` 中的非等量折算比与副产物回收抵扣项。

### 步骤 3：本地执行自测验证脚本
在完成配置文件编写后，运行对应的验证脚本进行即时评测：
```bash
# 验证案例 1：
python practice_classroom/case1_waste_heat/verify_case1.py

# 验证案例 2：
python practice_classroom/case2_catalyst/verify_case2.py

# 运行全量单元测试套件：
pytest -v tests/
```
若终端打印 `🎉 恭喜！各项指标与美国能源部官方基准严格对齐！` 且单元测试 100% 通过，说明你的模型构建完全正确。

### 步骤 4：提交代码并推送到个人分支
```bash
git add .
git commit -m "feat(case1): complete waste heat recovery parameters by <姓名>"
git push -u origin student/<学号>-<姓名拼音>-<case1/case2>
```

### 步骤 5：在 GitHub 上发起 Pull Request (PR)
1. 访问代码仓页面：`https://github.com/whu-course-EnvironPlanManag/pyTECHTEST`；
2. 点击 **Compare & pull request**；
3. 按照 PR 模板勾选自测结果并填写实训反思；
4. 提交后，GitHub Actions CI 将会自动触发测试并显示绿色通过标记 ✅。

---

## 📂 实践子目录快速导航
- [👉 进入案例 1：工业余热回收模型练习 (case1_waste_heat)](case1_waste_heat/)
- [👉 进入案例 2：先进催化剂合成练习 (case2_catalyst)](case2_catalyst/)
