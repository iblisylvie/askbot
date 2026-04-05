---
name: transcript-to-sessions
description: 处理讯飞语音转写文本，自动识别主持人、按session拆分会议内容并生成结构化markdown素材。当用户需要处理会议录音转写文件、将长文本按主题分段、提取演讲内容时，必须使用此skill。
---

# Transcript To Sessions

处理讯飞语音转写文本，自动识别主持人、按session拆分会议内容并生成结构化markdown素材。

## 何时使用

- 处理讯飞转写的会议录音文本（txt格式）
- 将长会议内容按主题/演讲人自动分段
- 生成结构化的markdown笔记，包含目录索引
- 需要识别主持人过渡语进行智能分段
- 使用LLM优化session标题生成

## 工作流程

1. **准备输入文件** - 确保是讯飞转写格式的txt文件
2. **运行处理命令** - 调用 skill 执行解析和拆分
3. **检查输出** - 查看生成的 index.md 和各 session 文件

## 使用方法

### 基础用法

```
/transcript-to-sessions /path/to/转写文件.txt
```

### 指定输出目录

```
/transcript-to-sessions /path/to/转写文件.txt -o ./my-output
```

### 禁用LLM标题生成（使用自动提取）

```
/transcript-to-sessions /path/to/转写文件.txt --use_llm=false
```

## 环境配置

首次使用需要配置API密钥（用于LLM标题生成）：

```bash
cd ~/.agents/skills/transcript-to-sessions
cp .env.example .env
# 编辑 .env 填入你的API密钥
```

支持任意兼容OpenAI API格式的服务商（SiliconFlow、DeepSeek等）。

## 输出结构

```
output/
├── index.md          # 会议总览和session列表
├── session-01.md     # 第一个session的内容
├── session-02.md     # 第二个session的内容
└── session-03.md     # ...更多session
```

## 输入格式要求

支持讯飞转写标准格式：

```
录音信息行

说话人1 00:00
这是第一段内容...

说话人2 00:30
这是第二段内容...

说话人1 01:15
这是第三段内容...
```

## 技术细节

- **主持人识别**：基于说话频次和过渡关键词（"接下来"、"有请"、"欢迎"等）
- **Session分割**：识别主持人过渡语，结合时间间隔（>2分钟）
- **标题生成**：默认使用LLM生成高质量标题，失败时自动回退到首句提取
- **LLM集成**：通过litellm支持多模型后端
