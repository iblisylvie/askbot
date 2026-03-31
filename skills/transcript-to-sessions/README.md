# 语音转写文本处理器

自动解析会议语音转写文本，识别主持人，按session拆分，并生成结构化的markdown素材。

## 功能特性

1. **智能Session拆分**
   - 自动识别主持人（说话最少+过渡语关键词）
   - 基于主持人过渡语检测session边界
   - 自动提取主讲人信息

2. **标题生成**
   - 默认从内容提取标题
   - 支持调用LLM生成更精准的标题（需要配置API密钥）

3. **输出结构**
   - `index.md` - 会话总览索引
   - `session-XX.md` - 每个session的详细内容

## 安装依赖

```bash
pip install python-dotenv litellm
```

## 使用方法

### 基础用法

```bash
# 处理转写文件
python process_transcript.py /path/to/转写文件.txt

# 指定输出目录
python process_transcript.py /path/to/转写文件.txt -o ./my-output
```

### 使用LLM生成标题

1. 复制环境变量示例文件并配置：
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥
```

2. 运行（添加 `--llm` 参数）：
```bash
python process_transcript.py /path/to/转写文件.txt --llm
```

## 环境变量配置

在 `.env` 文件中配置：

```bash
# LLM API配置（用于生成标题）
LLM_API_KEY=your_api_key_here
LLM_API_BASE=https://api.openai.com/v1  # 可选，默认为OpenAI
LLM_MODEL=gpt-4o-mini  # 可选，默认模型
```

支持任何与OpenAI API兼容的服务商（如Azure、DeepSeek、SiliconFlow等）。

## 输入格式

支持讯飞转写的txt格式：

```
录音信息
说话人1 00:00
包括模型纳管，我们的钛平台支撑它...
说话人1 00:31
今天我们分享的重要产品是腾讯云智能体开发平台...
说话人2 18:19
感谢秦立明老师的精彩分享...
```

## 输出示例

```
output/
├── index.md              # 会话索引
├── session-01.md         # 第一个session
├── session-02.md         # 第二个session
└── session-03.md         # 第三个session
```

每个session文件包含：
- YAML frontmatter（标题、主讲人、时间等元数据）
- 内容纪要（核心要点摘要）
- 详细内容（按说话人分段）
