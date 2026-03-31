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

脚本自动移除 `<script>`、`<style>`、`<head>` 等无用标签，清理微信 UI 元素，保留正文和链接。

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

### 🚨 准确性红线（生成前必读）

**绝对禁止（会导致严重后果）：**
1. **编造文章** - 周报中提到的每篇文章必须能在`summary.csv`中找到
2. **编造链接** - 任何URL必须能在原文中找到，禁止推测
3. **编造数据** - 融资/收入/用户量等数字必须原文明确写出
4. **混淆来源** - 每篇文章来源必须独立确认

**生成前强制验证：**

**Step A: 日期归属核查（头条文章必做）**
```bash
# 触发条件：当文章提到以下任何关键词时，必须执行
# 关键词：开源、发布、推出、上市、融资、收购、官宣、首次亮相

# 执行方法：
# 1. 提取产品/事件核心名称（如"Step 3.5 Flash"）
# 2. 搜索历史日期
$ grep "Step 3.5 Flash" output/2026-03-*/summary.csv
# 输出示例：
# output/2026-03-04/summary.csv:...Step 3.5 Flash开源...  ← 这是真实发布日期
# output/2026-03-23/summary.csv:...Step 3.5 Flash实测...  ← 这是后续评测文章

# 3. 判断规则：
# - 如果最早日期 = 本周内 → 可以列为"本周发布"
# - 如果最早日期 < 本周 → 这是回顾/评测文章，标题必须改为"XXX实测/解读"而非"XXX发布"
```

**Step B: 基础信息核查（所有文章必做）**
```bash
# 确认文章存在
grep "文章标题" output/2026-03-*/summary.csv

# 确认链接存在于原文
grep "github.com" output/2026-03-*/文章标题.md

# 确认来源准确
cat output/2026-03-08/summary.csv | grep "文章标题"
```

**🚨 关键禁令：**
- **禁止**仅凭文章所在目录判断新闻时间（如放在 output/2026-03-23/ 不代表是3月23日发布的新闻）
- **禁止**将"评测/解读/回顾"文章表述为"发布/开源"新闻
- 所有提到"开源/发布"的内容，**必须**通过 Step A 验证原始日期

### 内容筛选优先级

**【新增】日期归属前置核查（生成头条前必须执行）：**

在确定任何头条新闻之前，**必须**执行以下检查，防止历史新闻被误认为本周发布：

```bash
# 强制检查：当文章提到以下关键词时，必须搜索历史日期
# 关键词：开源、发布、推出、上市、融资、收购、官宣

# 示例检查流程（对每篇候选头条文章执行）：
1. 提取文章中提到的产品/事件名称
2. 运行搜索：grep "产品名" output/2026-03-*/summary.csv | head -5
3. 如果最早出现的日期早于本周 → 这是历史回顾文章，**不能**列为"本周发布"
4. 如果文章确实在报道新的发布 → 确认后列入头条
```

**⚠️ 强制性规则（无例外）：**
- 任何包含"开源/发布/推出"的文章，**必须**先执行日期搜索再决定是否列为头条
- 如果发现该事件在本周之前的 summary.csv 中已存在 → 这是"回顾/评测"文章，不是"本周发布"
- **禁止**仅凭文章所在目录日期（如 output/2026-03-23/）判断新闻发布时间

**常见陷阱（务必避免）：**
- ❌ 错误："Step 3.5 Flash本周开源"（实际3月4日已开源，3月23日文章只是评测）
- ✅ 正确："Step 3.5 Flash实测：在OpenClaw排名中表现优异"（准确反映文章内容）

---

**头条（2-3条）**：大厂新模型发布 > 重大产品发布 > 技术范式变化 > 开源重磅项目

**必须检查的大厂模型发布（遍历所有 summary.csv 搜索关键词）：**
- 国外：OpenAI（GPT、Codex、o3）、Anthropic（Claude、Opus、Sonnet）、Google（Gemini、Genie）、Meta（Llama）、xAI（Grok）
- 国内（容易遗漏）：智谱AI（GLM）、MiniMax（M2）、字节（豆包、Seedance）、DeepSeek、月之暗面（Kimi）、百川、零一万物（Yi）、阶跃星辰（Step）、面壁智能（MiniCPM）、阿里（通义千问、Qwen）、百度（文心）

**工具（3-4个）**：优先有代码/可试用的开源项目，必须回答"用它能做什么"

**学习资源（1-2个）**：高质量博客/教程/论文解读，避免纯营销内容

### 链接处理（严禁编造）

- 非微信链接优先。微信链接标注"（需在微信内打开）"
- **🚫 严禁编造链接**：任何URL必须能在原文Markdown中找到，禁止根据命名规则推测（如`github.com/公司名/产品名`）
- 原文未提供链接时，必须写"原文未提供链接"
- 来源统一格式：`（来源：XXX，YYYY-MM-DD）`，日期取自文件路径中的日期文件夹
- **来源核实**：每篇文章的来源必须查看summary.csv确认，禁止凭记忆或推测

**常见错误：**
- ❌ 原文只提到项目名称，却编造`https://github.com/xxx/xxx`
- ❌ 将文章A的内容与文章B的来源混淆
- ❌ 未查看summary.csv就标注来源

### 期号确定

扫描 `output/` 目录下已有的 `AI技术周刊_第*期_*.md` 文件，使用下一个序号。无历史记录则从第 1 期开始。

**输出：** `output/AI技术周刊_第X期_YYYY-MM-DD.md`

**⚠️ 重要：生成后必须执行 Step 7 准确性核查**

周报生成后，**必须**逐条对比原始数据核查每一条信息（文章存在性、链接真实性、数据准确性、来源准确性）。详见 Step 7。

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

## Step 7: 准确性核查（关键步骤）

**⚠️ 本步骤不可跳过。**

### 快速核查流程（推荐）

**Step 1: 运行自动核查脚本**

```bash
node $AI_WEEKLY_WRITER_HOME/scripts/verify-weekly.js output/AI技术周刊_第X期_YYYY-MM-DD.md
```

脚本会自动检查：
- ✅ 文章存在性（是否在 summary.csv 中）
- ✅ 链接真实性（是否在原文中提及）
- ⚠️ 日期关键词（标记需人工确认的时间描述）

**Step 2: 人工重点核查（脚本无法替代）**

脚本运行后，重点人工检查以下 **P0 级别**项目：

| 检查项 | 检查方法 | 修正动作 |
|--------|----------|----------|
| **日期归属** | 搜索"本周/今天/昨天"+"开源/发布" | 确认是本周发布还是历史回顾 |
| **主语归属** | 检查含"同时/此外/还"的句子 | 确认后半句主语是否正确 |
| **数据准确性** | 检查所有数字（融资额、用户数） | 与原文对比，"未披露"不能写具体数字 |
| **来源准确性** | `cat summary.csv \| grep 标题` | 必须与 account_name 一致 |

**致命错误清单（发现必须修正）：**
- ❌ 文章标题在 summary.csv 中找不到 → **删除该条目**
- ❌ 链接在原文中找不到 → **改为"原文未提供链接"**
- ❌ 日期错误（历史新闻写成本周） → **修正时间描述**
- ❌ 融资金额编造 → **改为"具体金额未披露"**

### 完整检查清单

如需详细检查清单，参考：
- `references/accuracy-checklist.md` - 完整核查指南
- `references/error-examples.md` - 历史错误案例

### 核查通过标准

- ✅ 自动脚本检查通过
- ✅ 人工确认 P0 项目无错误
- ✅ 用户确认无误（或用户说"发布"）

---

**修正后才能进入下一步。**

## Step 8: 转换为微信格式（可选）

- 调用 `baoyu-markdown-to-html` 转为公众号 HTML
- 调用 `baoyu-post-to-wechat` 发布

## 常见场景

**用户想强调某主题**：将该主题放在头条，工具和资源也优先相关方向。

**用户反馈遗漏内容**：在原数据中搜索，确认是否因筛选遗漏，重新生成并更新检查清单。

## 参考示例

详见 [references/examples.md](references/examples.md) 获取完整周报和拆条图文示例。
