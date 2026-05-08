# Evolution Log — content-summarizer

## Round 1 (2026-04-20)

### 触发原因
用户反馈：当原始 content 里面有图表时，建议保留一些有助于说明的重要图表，来增加 summary 的可读性。

### 核心模式
**P01: 完全忽略图表/数据可视化等非文本元素**
- skill 的 extraction、assembly、quality checklist 全部围绕纯文本设计
- 长文（报告、论文、分析）中图表往往是信息密度最高的部分，完全丢失严重削弱 summary 价值

**P02: 输出模板没有预留图表位置**
- 即使提取了图表信息，也没有在最终输出中给出放置或引用的位置

### 改动（四处）
1. **Extraction Template**：在 "Entities Mentioned" 后新增 "Charts & Visuals" 类别，要求提取图表标题、类型、关键数据点、重要性说明和建议用法。
2. **Assembly Template**：在 "Core Arguments" 后新增 "Key Data & Visuals" 区块，给出两种处理方式：
   - Option A：保留原图引用（附简短描述和关键 takeaway）
   - Option B：用文字还原数据（描述核心对比/趋势/分布）
   并给出规则：如果图表是某论点最密集或最有说服力的证据，不许跳过。
3. **Quality Checklist**：在 "Coverage & Completeness" 下新增检查项：若原文含图表，summary 是否描述了其关键结论或做了引用？不许静默丢弃高密度视觉证据。
4. **Usage Notes**：增加图表处理说明，强调 extraction 阶段提取关键数据，assembly 阶段决定保留引用还是文字还原。

### 预期效果
- 处理含图表的报告/论文时，summary 会主动提取并描述关键图表的数据结论
- 用户看到的不只是文字摘要，还有对核心数据可视化的引用或还原
