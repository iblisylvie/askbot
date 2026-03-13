# AI Weekly Writer Skill Optimization — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the ai-weekly-writer skill from a technical-focused newsletter generator into a dual-output system (weekly report + split articles with infographics) targeting general AI interest audiences with "anxiety + remedy" narrative style.

**Architecture:** Split the monolithic 703-line SKILL.md into focused files (core workflow, accuracy checklist, error examples, templates). Add a new "split article" generation phase after the weekly report. Rewrite writing style guidance throughout.

**Tech Stack:** Markdown files only — no code changes. All edits in `/root/askbot/skills/ai-weekly-writer/`.

**Spec:** `docs/superpowers/specs/2026-03-13-ai-weekly-writer-optimization-design.md`

---

## Chunk 1: Extract and Create Reference Files

### Task 1: Extract accuracy checklist to standalone file

**Files:**
- Create: `skills/ai-weekly-writer/references/accuracy-checklist.md`
- Source: Current `skills/ai-weekly-writer/SKILL.md` lines 406-496 (准确性要求 sections 1-4) and lines 535-573 (检查清单 section 6)

**Note:** The extracted content will be removed from SKILL.md in Task 6 (full rewrite). Do not modify SKILL.md in this task.

- [ ] **Step 1: Create `references/accuracy-checklist.md`**

Extract the following sections from current SKILL.md into a new file, preserving content exactly:
- "## 准确性要求（关键）" (lines 406-495): sections 1 through 4 (严格遵循原文, 信息必须可验证, 融资状态, 企业案例)
- "### 6. 检查清单（输出前必做）" (lines 535-573): the full checklist with all checkbox items
- "## 数据核实操作指南" (lines 648-678): keyword verification table and verification method

Add a header:
```markdown
# 准确性检查清单

> 本文件在周报生成的 Step 7（准确性核查）阶段加载。
> 生成完成后，逐条检查以下所有项目。
```

- [ ] **Step 2: Verify extraction completeness**

Confirm the new file contains:
- 4 accuracy requirement sections (严格遵循原文, 信息可验证, 融资状态, 企业案例)
- Complete checklist (头条检查, 内容准确性, 格式检查)
- Data verification guide with keyword table and code example

- [ ] **Step 3: Commit**

```bash
git add skills/ai-weekly-writer/references/accuracy-checklist.md
git commit -m "refactor: extract accuracy checklist from SKILL.md to standalone file"
```

---

### Task 2: Extract error examples to standalone file

**Files:**
- Create: `skills/ai-weekly-writer/references/error-examples.md`
- Source: Current `skills/ai-weekly-writer/SKILL.md` lines 497-532 (常见错误案例 section 5)

**Note:** The extracted content will be removed from SKILL.md in Task 6 (full rewrite). Do not modify SKILL.md in this task.

- [ ] **Step 1: Create `references/error-examples.md`**

Extract "### 5. 常见错误案例（务必警惕）" (lines 497-532) from current SKILL.md. Preserve all 4 error type tables exactly.

Add a header:
```markdown
# 常见错误案例

> 本文件在周报生成的 Step 7（准确性核查）阶段加载。
> 以下是从历史周报中总结的高频错误类型，生成时务必警惕。
```

- [ ] **Step 2: Verify extraction completeness**

Confirm the file contains all 4 error types:
1. 单位/数量级错误
2. 产品归属错误
3. 融资/上市状态错误
4. 修饰对象错误

Each with: 错误/正确对比表 + 根因分析。

- [ ] **Step 3: Commit**

```bash
git add skills/ai-weekly-writer/references/error-examples.md
git commit -m "refactor: extract error examples from SKILL.md to standalone file"
```

---

### Task 3: Create split article template

**Files:**
- Create: `skills/ai-weekly-writer/assets/article-template.md`

- [ ] **Step 1: Create `assets/article-template.md`**

Content (from spec Part 2):

```markdown
# 拆条图文模板

> 每篇图文 500-800 字，配 1 张竖版信息图。

## 模板结构

按以下结构生成每篇拆条图文：

~~~markdown
# [吸引眼球的标题]

[1-2句钩子：制造紧迫感/好奇心]

## 发生了什么

[3-5句简明交代事件，不用术语]

## 这跟你有什么关系

[2-3句：为什么普通人需要关注]

## 你现在可以做的

[1-3个具体可操作的行动建议]
- 行动1：...
- 行动2：...

---
*来源：AI技术周刊第X期 | 更多AI情报关注 [公众号名]*
~~~

## 标题写作模板

- **反差型**："X已经能做Y了，你还在手动做Z？"
- **数字型**："3个AI工具让我每天多出2小时"
- **恐惧型**："你的行业正在被AI重写，这5件事你必须知道"
- **利益型**："用这个免费工具，一个人就能干原来3个人的活"

## 信息图参数推荐

| 话题类型 | layout | style |
|----------|--------|-------|
| 新模型/产品发布 | bridge | technical-schematic |
| 行业趋势/数据 | bento-grid | data-storytelling |
| 工具推荐 | flow-process | craft-handmade |
| 通用话题 | magazine-spread | editorial-clean |

统一参数：`--aspect portrait --lang zh`
```

- [ ] **Step 2: Commit**

```bash
git add skills/ai-weekly-writer/assets/article-template.md
git commit -m "feat: add split article template for standalone image-text posts"
```

---

## Chunk 2: Update Weekly Template and Examples

### Task 4: Update weekly report template

**Files:**
- Modify: `skills/ai-weekly-writer/assets/template.md`

- [ ] **Step 1: Rewrite `assets/template.md`**

Apply Part 3 board-level adjustments from spec. Key changes to the existing template:

1. **Opening**: Change `> 本周一句话：` to `> 本周AI圈最值得你知道的一件事：` + add a hook paragraph
2. **Add events overview table** after opening (with "跟你的关系" tags per event)
3. **Headlines section**: Change from "技术影响" to "这跟你有什么关系" + "你可以做什么"
4. **Tools section**: Replace tech-focused table with "用它能做什么" oriented format, remove `技术栈` row, add `谁适合用` row
5. **Learning resources**: Change framing to "不想被淘汰就看这个"
6. **Add 实战技巧 section**: Non-technical "今天就能用" action guide
7. **Editor observation**: Change to "我本周最大的感受", more personal tone
8. **Add 转发钩子** at the end: "这周AI圈发生了X件大事，第3件跟每个人都有关"

The full new template content (replace entire file):

```markdown
# 【AI技术周刊】第 X 期 | YYYY年MM月DD日

> 本周AI圈最值得你知道的一件事：[一句话钩子，制造紧迫感]

[2-3句展开：为什么这件事跟每个人都有关]

---

## 本周重要事件一览

| 类别 | 事件 | 跟你的关系 |
|------|------|------------|
| 🏢 **大厂动态** | - 事件1<br>- 事件2 | [标签] |
| 🤖 **新模型** | - 事件1<br>- 事件2 | [标签] |
| 🛠️ **新工具** | - 事件1<br>- 事件2 | [标签] |
| 🎬 **多模态** | - 事件1<br>- 事件2 | [标签] |
| 🏭 **行业应用** | - 事件1<br>- 事件2 | [标签] |

**标签说明：** [你的工作可能受影响] [免费工具，立刻可用] [暂时观望] [创业机会] [值得学习]

---

## 🔥 本周头条（2-3条）

### 1. [新闻标题 — 用"焦虑+解药"风格]

**发生了什么：**
[2-3句简明交代，避免术语]

**这跟你有什么关系：**
[为什么普通人需要关注这件事]

**你可以做什么：**
- 行动建议1
- 行动建议2

---

## 🛠️ 本周值得试的工具（3-4个）

### 1. [工具名称]

| 属性 | 内容 |
|------|------|
| **一句话介绍** | |
| **最大亮点** | |
| **谁适合用** | |
| **链接** | |

**用它能做什么：** [具体场景描述]

**马上试：**
```bash
# 一行命令开始
```

---

## 📚 不想被淘汰就看这个（1-2个）

### 1. [资源名称]

- **类型：**
- **来源：**
- **为什么值得看：**
- **链接：**

**适合谁：** [用通俗语言描述]

---

## 🎯 今天就能用的技巧

### 技巧1：[具体技巧名称]

**场景：** 什么时候用

**怎么做：**
[步骤说明，不假设技术背景]

**效果：** 能省多少时间/多赚多少

---

## 💡 我本周最大的感受

[150-200字，个人化的趋势洞察]

**行动建议：**
- 建议1
- 建议2

---

## 💼 彩蛋

> [一句话企业应用案例]（来源：XXX，YYYY-MM-DD）

---

*下周关注：*

**转发话术：** 这周AI圈发生了X件大事，第Y件跟每个人都有关。

*更多AI情报关注 [公众号名]*
```

- [ ] **Step 2: Verify template has all required sections**

Check that all 9 sections are present:
1. Opening hook
2. Events overview table with tags
3. Headlines (焦虑+解药 style)
4. Tools (用它能做什么 oriented)
5. Learning resources (不想被淘汰)
6. Actionable tips (今天就能用)
7. Editor personal observation (我的感受)
8. Bonus (彩蛋)
9. Forward hook (转发话术)

- [ ] **Step 3: Commit**

```bash
git add skills/ai-weekly-writer/assets/template.md
git commit -m "feat: update weekly template with anxiety+remedy style and relevance tags"
```

---

### Task 5: Add split article example to examples.md

**Files:**
- Modify: `skills/ai-weekly-writer/references/examples.md`

- [ ] **Step 1: Append a split article example**

Add after the existing content (line 312) a new section:

```markdown
---

## 示例 3：拆条图文示例

基于示例 1 的头条"OpenAI 发布 Operator"生成的独立图文：

输出：

# AI 已经能帮你操作电脑了，你还在手动复制粘贴？

上周，OpenAI 发布了一个叫 Operator 的新工具。简单说，它能像真人一样操作浏览器——打开网页、点按钮、填表单、甚至帮你订机票。

这不是概念片，已经有人实测用它自动比价、自动填报销单了。

## 发生了什么

OpenAI 让 AI 从"你问我答"升级成了"你说我做"。以前你得告诉 AI 怎么做，现在你只需要说"帮我订一张下周三去上海的机票"，它自己打开携程、搜航班、选座位。

目前只对 Pro 用户开放（$200/月），但免费版预计很快跟上。

## 这跟你有什么关系

如果你的工作中有大量重复的网页操作（填表、查数据、比价格、发邮件），这些工作正在被 AI 接管。不是将来，是现在。

好消息是：会用这些工具的人，效率会比不会用的人高出 5-10 倍。这是一个拉开差距的窗口期。

## 你现在可以做的

- **立刻可试**：去 chatgpt.com 看看 Operator 的 demo 视频，感受一下 AI 操作浏览器是什么样
- **免费替代**：试试开源的 Browser Use（github.com/browser-use/browser-use），用 Python 自己搭一个类似的工具
- **思考一下**：你每天花最多时间的 3 个重复操作是什么？哪些可以交给 AI？

---
*来源：AI技术周刊第 12 期 | 更多AI情报关注 [公众号名]*
```

Also add a brief writing technique note:

```markdown
### 5. 拆条图文写作技巧

**核心公式：** 焦虑（钩子）→ 事件（简明）→ 相关性（跟你的关系）→ 解药（行动建议）

**标题**：必须让非技术人群也想点进来。用反差、数字、恐惧或利益驱动。

**语言**：
- 禁用术语，用比喻代替（"token" → "AI 的记忆容量"）
- 多用"你"，少用被动句
- 每段回答"所以呢？跟我有什么关系？"

**长度**：500-800 字，能在 2 分钟内读完。
```

- [ ] **Step 2: Commit**

```bash
git add skills/ai-weekly-writer/references/examples.md
git commit -m "feat: add split article example and writing technique to examples.md"
```

---

## Chunk 3: Rewrite SKILL.md

### Task 6: Rewrite SKILL.md with new workflow and writing style

This is the largest task. The new SKILL.md should be ~300 lines, containing:
1. Frontmatter (unchanged trigger words)
2. Overview with new dual-output workflow
3. Input format (unchanged)
4. Writing style guide (new: anxiety+remedy formula)
5. Step 1-2: Data prep and daily report (mostly unchanged)
6. Step 3: Weekly report generation (updated references to new template)
7. Step 4-6: Split article selection, generation, infographic (new)
8. Step 7: Accuracy check (reference to external file)
9. Step 8: WeChat conversion (optional)
10. Content selection criteria (condensed from current)
11. Link handling rules (condensed)
12. Common scenarios (condensed)

**Files:**
- Modify: `skills/ai-weekly-writer/SKILL.md` (full rewrite)

- [ ] **Step 1: Write the new SKILL.md**

Replace the entire SKILL.md with the following content:

````markdown
---
name: ai-weekly-writer
description: Generate AI technology weekly reports from daily news raw files. Use when user provides daily news raw content (HTML files and summary.csv in output/YYYY-MM-DD/) and wants to create a structured weekly newsletter for engineers and career switchers. Triggers on phrases like "生成周报", "写周报", "weekly report", or when user provides multiple daily news items to summarize.
---

# AI 周报 + 图文生成器

根据每日新闻原件，生成两种输出：
1. **周报**：完整的 AI 技术周刊（信息全景）
2. **拆条图文**：3-5 篇独立短文 + 信息图（适合公众号图文发布）

## 工作流程概览

```
每日新闻原件 (output/YYYY-MM-DD/)
    ↓ Step 1: HTML 转 Markdown
    ↓ Step 2: 生成每日日报
    ↓ Step 3: 汇总生成周报
    ↓ Step 4: 拆条选题（用户确认）
    ↓ Step 5: 生成拆条图文
    ↓ Step 6: 生成信息图
    ↓ Step 7: 准确性核查
    ↓ Step 8: 转换为微信格式（可选）
```

## 输入格式

每日新闻原件存储在 `output/YYYY-MM-DD/` 目录下：
- `summary.csv` - 文章元数据（标题、公众号、摘要、链接、本地文件路径）
- `文章标题.html` - 文章内容 HTML 文件（原始爬取）
- `文章标题.md` - 文章内容 Markdown 文件（HTML 转换后）

### summary.csv 格式

```csv
account_name,app_msg_id,digest,link,title,create_time,local_file_path
机器之心,2651012094,真正让一个人活成一支队伍。,http://mp.weixin.qq.com/s?...,实测夸克...,2026-01-15 03:48:47,output/2026-01-15/实测夸克....html
```

## 写作风格

### 核心公式

```
每条内容 = 钩子（制造紧迫感）+ 事件（简明交代）+ 解药（你能做什么）
```

### 风格对比

| 维度 | 不要这样写 | 要这样写 |
|------|-----------|---------|
| 标题 | "OpenAI 发布 Codex，AI 编程工具进入新阶段" | "程序员的饭碗又危险了？Codex 让 AI 独立写代码" |
| 摘要 | "Codex 支持在沙箱中执行代码任务..." | "OpenAI 新发的 Codex 能独立接需求、写代码、跑测试。你不需要恐慌，但你需要知道怎么用它来提升10倍效率..." |
| 语气 | 客观中性 | 有立场、有温度、制造参与感 |
| 行动项 | 无 | "今天就可以试：去 chatgpt.com/codex 领免费额度" |

### 语言规范

- 避免专业术语，必须使用时加括号解释（如"token" → "AI 的记忆容量"）
- 每段话都回答"这跟我有什么关系"
- 多用第二人称"你"，少用被动句
- 英文前后加空格，重要信息用 **加粗**

### 写作风格适用范围

- **周报**：混合风格 — 开头/标题/标签用"焦虑+解药"吸引注意，内容主体保留事实准确性和技术可信度，但降低术语密度
- **拆条图文**：完全"焦虑+解药"风格 — 纯面向泛人群，不假设读者有技术背景

## Step 1: 数据准备

### HTML 转 Markdown

对每篇文章的 HTML 文件，使用 `html2md.js` 转换为 Markdown：

**脚本位置：** `$AI_WEEKLY_WRITER_HOME/scripts/html2md.js`

**环境变量设置：**
```bash
export AI_WEEKLY_WRITER_HOME="$HOME/.agents/skills/ai-weekly-writer"
```

**首次使用：**
```bash
cd $AI_WEEKLY_WRITER_HOME && npm install
```

**使用：**
```bash
# 单个文件
node $AI_WEEKLY_WRITER_HOME/scripts/html2md.js output/2026-01-15/文章标题.html

# 批量转换
for f in output/2026-01-15/*.html; do
    node $AI_WEEKLY_WRITER_HOME/scripts/html2md.js "$f"
done
```

脚本会自动移除 `<script>`、`<style>`、`<head>` 等无用标签，清理微信 UI 元素，保留正文和链接。

## Step 2: 生成每日日报

1. 读取 `output/YYYY-MM-DD/summary.csv` 获取文章元数据
2. 读取每篇文章的 Markdown 内容，提取核心信息
3. 按重要性/热度排序，过滤低质量内容
4. 生成 `output/AI科技日报_YYYY-MM-DD_content.md`

### 日报格式

```markdown
# AI科技日报 - YYYY年MM月DD日

## 今日精选文章

### 1. [文章标题]
- **来源**: 公众号名称
- **摘要**: 文章摘要
- **链接**: 文章链接
- **核心内容**: 关键信息

## 今日热点标签
- 标签1, 标签2, 标签3...

## 主编简评
今日AI领域的主要动态...
```

## Step 3: 生成周报

读取 `assets/template.md` 获取周报模板，基于所有日报汇总生成周报。

### 内容筛选优先级

**头条（2-3条）**：大厂新模型发布 > 重大产品发布 > 技术范式变化 > 开源重磅项目

**必须检查的大厂模型发布：**
- 国外：OpenAI、Anthropic、Google、Meta、xAI
- 国内（易遗漏）：智谱AI、MiniMax、字节跳动、DeepSeek、月之暗面、百川、零一万物、阶跃星辰、面壁智能、阿里、百度
- 遍历所有 summary.csv 搜索关键词确认

**工具（3-4个）**：优先有代码/可试用的开源项目，必须回答"用它能做什么"

**学习资源（1-2个）**：高质量博客/教程/论文解读，避免纯营销内容

### 链接处理

- 非微信链接优先。微信链接标注"（需在微信内打开）"
- **禁止编造链接**，未提供则写"原文未提供链接"
- 来源统一格式：`（来源：XXX，YYYY-MM-DD）`，日期取自文件路径中的日期文件夹

### 期号确定

扫描 `output/` 目录下已有的 `AI技术周刊_第*期_*.md` 文件，使用下一个序号。无历史记录则从第 1 期开始。

**输出：** `output/AI技术周刊_第X期_YYYY-MM-DD.md`

## Step 4: 拆条选题

从周报内容中选出 3-5 个最有传播力的话题。

### 评分标准

| 维度 | 权重 | 说明 |
|------|------|------|
| 情绪冲击力 | 40% | 能否引发"我也得关注"的反应 |
| 可操作性 | 30% | 读者看完能立刻做什么 |
| 新鲜度 | 20% | 本周首次出现的新事物 |
| 话题热度 | 10% | 社交媒体上已有讨论 |

### 用户确认流程

- **默认**：展示选题列表并等待用户确认
- 用户可以：接受全部 / 替换某条 / 要求重选
- 如用户在触发 skill 时说"全自动"，则跳过确认直接生成

## Step 5: 生成拆条图文

读取 `assets/article-template.md` 获取模板，为每个选中的话题生成独立短文。

**要求：**
- 每篇 500-800 字
- 完全"焦虑+解药"风格，不假设读者有技术背景
- 标题使用反差型/数字型/恐惧型/利益型模板

**输出：** `output/AI图文_第X期_01.md` ~ `output/AI图文_第X期_05.md`

## Step 6: 生成信息图

为每篇拆条图文调用 `baoyu-infographic` skill 生成配图。

### 参数选择

| 话题类型 | layout | style |
|----------|--------|-------|
| 新模型/产品发布 | bridge | technical-schematic |
| 行业趋势/数据 | bento-grid | data-storytelling |
| 工具推荐 | flow-process | craft-handmade |
| 通用话题 | magazine-spread | editorial-clean |

统一参数：`--aspect portrait --lang zh`

如果信息图生成失败，跳过配图，仅输出 Markdown 文件。

**输出：** `output/AI图文_第X期_01.png` ~ `output/AI图文_第X期_05.png`

## Step 7: 准确性核查

读取 `references/accuracy-checklist.md` 并逐项执行完整检查清单。

读取 `references/error-examples.md` 并对照历史错误模式进行核查。

重点核查：
- 所有数字的单位（美元/人民币）和数量级
- 产品归属（哪家公司开发的）
- 融资/上市状态（拟/官宣/完成）
- 所有链接来自原文，无编造

最后生成转发话术，添加到周报末尾。

## Step 8: 转换为微信格式（可选）

- 调用 `baoyu-markdown-to-html` 转为公众号 HTML
- 调用 `baoyu-post-to-wechat` 发布

## 常见场景

**用户想强调某主题**：将该主题放在头条，工具和资源也优先相关方向。

**用户反馈遗漏内容**：在原数据中搜索，确认是否因筛选遗漏，重新生成并更新检查清单。

## 参考示例

详见 [references/examples.md](references/examples.md) 获取完整周报和拆条图文示例。
````

- [ ] **Step 2: Verify line count is ~300 lines (±50)**

Run: `wc -l skills/ai-weekly-writer/SKILL.md`
Expected: 250-350 lines

- [ ] **Step 3: Verify all external file references are correct**

Check that SKILL.md references these files and they exist:
- `assets/template.md`
- `assets/article-template.md`
- `references/accuracy-checklist.md`
- `references/error-examples.md`
- `references/examples.md`
- `scripts/html2md.js`

- [ ] **Step 4: Commit**

```bash
git add skills/ai-weekly-writer/SKILL.md
git commit -m "feat: rewrite SKILL.md with dual-output workflow and anxiety+remedy writing style"
```

---

## Chunk 4: Final Verification

### Task 7: End-to-end verification

- [ ] **Step 1: Verify file structure**

Run `find skills/ai-weekly-writer/ -type f | sort` and confirm it matches:
```
skills/ai-weekly-writer/SKILL.md
skills/ai-weekly-writer/assets/article-template.md
skills/ai-weekly-writer/assets/template.md
skills/ai-weekly-writer/references/accuracy-checklist.md
skills/ai-weekly-writer/references/error-examples.md
skills/ai-weekly-writer/references/examples.md
skills/ai-weekly-writer/scripts/html2md.js
```

- [ ] **Step 2: Verify symlink still works**

Run: `ls -la ~/.agents/skills/ai-weekly-writer/SKILL.md`
Expected: file exists and is readable

- [ ] **Step 3: Verify no content was lost**

Cross-check that the following content from the original SKILL.md exists somewhere in the new file set:
- Input format (summary.csv) → SKILL.md
- html2md.js usage → SKILL.md
- Content selection criteria → SKILL.md (condensed)
- Link handling rules → SKILL.md (condensed)
- Accuracy requirements (sections 1-4) → references/accuracy-checklist.md
- Error examples (4 types) → references/error-examples.md
- Checklist → references/accuracy-checklist.md
- Data verification guide → references/accuracy-checklist.md

- [ ] **Step 4: Spot-check critical rules are preserved**

Verify these critical rules appear in the new files:
1. "禁止编造链接" — in accuracy-checklist.md
2. "融资状态必须准确" — in accuracy-checklist.md
3. "大厂新模型发布检查" — in accuracy-checklist.md or SKILL.md
4. html2md.js usage instructions — in SKILL.md

- [ ] **Step 5: Final commit if any fixes were needed**

```bash
git add skills/ai-weekly-writer/
git commit -m "fix: address verification issues in ai-weekly-writer skill"
```
