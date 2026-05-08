# 改写记录 — Round 1

## 目标模式
- P01: 完全忽略图表/数据可视化等非文本元素
- P02: 输出模板没有预留图表位置

## 改动清单
1. [SKILL.md:Extraction Template] 在 "Entities Mentioned" 后新增 "Charts & Visuals" 类别，要求提取：
   - 图表标题/描述
   - 图表类型（柱状图/折线图/饼图/表格/流程图等）
   - 核心数据点或趋势
   - 为什么这个图表重要（它说明了什么关键结论）
2. [SKILL.md:Assembly Template] 在 "Core Arguments" 下新增可选区块 "Key Data & Visuals"，给出两种引用方式：
   - 若图表可获取：描述图表内容并建议保留原图引用
   - 若图表不可获取：用文字还原图表传达的核心数据对比或趋势
3. [SKILL.md:Quality Checklist] 在 "Coverage & Completeness" 下新增检查项：
   - 原始内容中是否有图表/数据可视化？如有，summary 中是否对其关键结论做了描述或引用？
4. [SKILL.md:Usage Notes] 增加一条：
   - 若原始内容包含图表或数据可视化，在 extraction 阶段识别其关键信息，在 assembly 阶段决定是否保留原图引用或用文字还原数据

## 预期效果
- 再次处理含图表的报告/论文时，summary 会主动提取并描述关键图表的数据结论
- 用户看到的不只是文字摘要，还有对核心数据可视化的引用或还原
