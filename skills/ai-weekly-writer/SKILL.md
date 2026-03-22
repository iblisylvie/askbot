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
```bash
# 确认文章存在
grep "文章标题" output/2026-03-*/summary.csv

# 确认链接存在于原文
grep "github.com" output/2026-03-*/文章标题.md

# 确认来源准确
cat output/2026-03-08/summary.csv | grep "文章标题"
```

### 内容筛选优先级

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

**⚠️ 本步骤不可跳过，必须逐项检查。**

### 核心要求：逐条对比原始数据

**生成周报后，必须逐条核查周报中的每条信息，对比原始数据。**

**强制核查流程：**

```bash
# 1. 提取周报中提到的所有文章标题
# 2. 对每个标题，在summary.csv中确认存在
grep "文章标题" output/2026-03-*/summary.csv

# 3. 对周报中提到的每个链接，确认在原文md中
grep "链接关键词" output/2026-03-*/文章标题.md

# 4. 对周报中提到的每个来源，确认与summary.csv一致
cat output/2026-03-*/summary.csv | grep "文章标题"
```

### 详细核查步骤

**Step 7.1: 文章存在性核查**
- 周报中提到的每篇文章 → 必须在 `summary.csv` 中找到
- 使用 `grep -r "文章标题" output/YYYY-MM-DD/summary.csv` 确认
- 发现不存在文章 → **立即删除**

**Step 7.2: 链接真实性核查**
- 周报中的每个URL → 必须在原文 `.md` 文件中存在
- 使用 `grep "链接" output/YYYY-MM-DD/文章.md` 确认
- 发现编造链接 → **替换为"原文未提供链接"**

**Step 7.3: 数据准确性核查**
- 周报中的每个数字（融资额、收入、用户数等） → 必须与原文完全一致
- 查看原文中是否明确写出该数字
- 发现"未披露"写成具体数字 → **修正为"未披露"**

**Step 7.4: 来源准确性核查**
- 周报中的每个来源 → 必须与 `summary.csv` 中的 `account_name` 一致
- 使用 `cat summary.csv | grep "文章标题"` 确认
- 发现来源错误 → **修正为summary.csv中的来源**

**Step 7.5: 检查清单对照**

读取 `references/accuracy-checklist.md` 并逐项执行完整检查清单。

读取 `references/error-examples.md` 并对照历史错误模式进行核查。

### 核查规则（按优先级排序）

**P0 — 主语/因果归属（最易犯、最致命）：**
- 同一段落出现多个事件时，逐句确认每个动作的真实主语
- 禁止把不同主体的行为合并到一句话中（例如：不能写"黄仁勋宣布了X并宣布了Y"，如果Y其实是另一家公司自己披露的）
- 特别注意"同时/此外/还"等连接词——它们很容易让读者把后半句的主语误认为前半句的主语

**P0 — 时间归属：**
- 所有"同一周/同时/同期"等时间副词必须回查原文确认实际时间
- 原文说"去年""上个月""此前"的事件，禁止写成"本周"
- 禁止为了制造趋势感或巧合感而篡改时间

**P0 — 文章标题 vs 官方主题：**
- 引用发布会/产品主题时，必须打开原文确认——公众号文章标题不等于发布会官方主题
- 原文标题中的修辞手法（如"把龙虾融进飞书"）不能直接当作被报道事件的事实性描述

**P1 — 数字/单位/数量级：**
- 所有数字的单位（美元/人民币）和数量级（万/亿）
- 产品归属（哪家公司/开发者）
- 融资/上市状态（拟/官宣/完成）

**P1 — 统计断言：**
- 所有统计描述（如"X篇中有Y篇提到Z"）必须运行脚本实际统计，禁止目测估算

**P2 — 链接/来源：**
- 所有链接来自原文，无编造
- 来源格式统一

### 重点核查项（根据历史错误）

| 检查项 | 检查方法 | 常见错误 |
|--------|----------|----------|
| **文章存在性** | `grep 标题 output/2026-03-*/summary.csv` | 编造不存在的文章 |
| **链接真实性** | `grep 链接 output/2026-03-*/文章.md` | 推测GitHub链接 |
| **数据准确性** | 查看原文是否明确写出 | 把"未披露"写成具体金额 |
| **来源准确性** | `cat summary.csv \| grep 标题` | 混淆不同文章的来源 |
| **融资状态** | 查看原文用词"拟"/"完成"/"官宣" | 把"拟融资"写成"完成融资" |

### 核查失败处理

如果发现以下内容，**必须删除或修正**：
- ❌ 无法找到原文支撑的信息
- ❌ 推测/编造的链接
- ❌ 错误标注的来源
- ❌ 未经验证的金额数据

**修正后才能进入下一步。**

### 核查流程

1. 逐段对照原文，标记所有"合并表述"（一句话中包含多个事件的地方），确认主语归属
2. 标记所有时间副词（"同时/同期/本周/同一周"），逐个回查原文确认
3. 标记所有引用/主题描述，确认是否来自原文正文而非文章标题
4. 执行数字/单位/融资状态核查
5. 运行统计脚本验证所有统计断言

最后生成转发话术，添加到周报末尾。

## Step 8: 转换为微信格式（可选）

- 调用 `baoyu-markdown-to-html` 转为公众号 HTML
- 调用 `baoyu-post-to-wechat` 发布

## 常见场景

**用户想强调某主题**：将该主题放在头条，工具和资源也优先相关方向。

**用户反馈遗漏内容**：在原数据中搜索，确认是否因筛选遗漏，重新生成并更新检查清单。

## 参考示例

详见 [references/examples.md](references/examples.md) 获取完整周报和拆条图文示例。
