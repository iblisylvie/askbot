#!/usr/bin/env python3
"""Generate a fixed-section markdown scaffold for LLM concept explanations."""

import argparse
import datetime
import os
import re
import sys


FULL_TEMPLATE = """# {concept}：一句话定义

> 引用锚点：一句权威观点（可意译）

作者导语：第一人称个人困惑/经历（2-4句）
导读：本文先...再...最后...

---

## 1. 你有没有想过
问题引入 + 生活场景

## 2. 这个概念从哪来
背景痛点 -> 旧方案 -> 新突破 -> 名称来源

## 3. 直觉建立
核心比喻 + 对应关系

## 4. 原理最小集
用 3 步解释机制（必要时给极简公式）

## 5. 如果没有它
旧方案、优势、代价、未来替代

## 6. 比喻的边界
比喻遮蔽了什么、何时失效

## 7. 概念关系图
与相关概念的区别与连接

## 8. 如果我是这个概念
第一人称独白（4-8行）

## 9. 顿悟压缩
### The One 公式
`{concept} = 输入 -> 核心变换 -> 输出`

### 一句话记住它
> TODO: 20-35 字费曼式总结

### ASCII 拓扑图
```text
[输入] -> [{concept}] -> [输出]
```

---

生成信息：
- 术语：`{concept}`
- 受众：`{audience}`
- 模板模式：`full`
- 生成日期：`{today}`
"""


SHORT_TEMPLATE = """# {concept}：简版概念卡片

## 1. 一句话定义
TODO

## 2. 一个生活比喻
TODO

## 3. 一个易混淆对比
`{concept}` vs `TODO`

## 4. 一句代价提醒
TODO

---

生成信息：
- 术语：`{concept}`
- 受众：`{audience}`
- 模板模式：`short`
- 生成日期：`{today}`
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a markdown scaffold for explaining an LLM concept."
    )
    parser.add_argument("concept", help="Concept name, e.g. token / embedding / MHA")
    parser.add_argument(
        "-o",
        "--output",
        help="Output markdown path. If omitted, uses --out-dir/<slug>-concept.md",
    )
    parser.add_argument(
        "--out-dir",
        default="output/explainer",
        help="Output directory when --output is omitted (default: output/explainer)",
    )
    parser.add_argument(
        "--audience",
        default="不懂技术的文科生",
        help="Target audience label to include in metadata",
    )
    parser.add_argument(
        "--short",
        action="store_true",
        help="Generate short 4-section card template",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing file",
    )
    return parser.parse_args()


def slugify(text):
    base = text.strip().lower()
    base = re.sub(r"\s+", "-", base)
    base = re.sub(r"[^a-z0-9\-_]", "-", base)
    base = re.sub(r"-{2,}", "-", base).strip("-")
    return base or "concept"


def resolve_output_path(args):
    if args.output:
        return args.output
    filename = "{}-concept.md".format(slugify(args.concept))
    return os.path.join(args.out_dir, filename)


def main():
    args = parse_args()
    out_path = resolve_output_path(args)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    if os.path.exists(out_path) and not args.force:
        print("File exists: {} (use --force to overwrite)".format(out_path), file=sys.stderr)
        return 1

    today = datetime.date.today().isoformat()
    data = {
        "concept": args.concept.strip(),
        "audience": args.audience.strip(),
        "today": today,
    }
    template = SHORT_TEMPLATE if args.short else FULL_TEMPLATE
    content = template.format(**data)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("Generated: {}".format(out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
