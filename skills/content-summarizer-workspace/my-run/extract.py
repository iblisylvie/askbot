#!/usr/bin/env python3
"""
提取阶段：从每个块中提取结构化信息
"""

import json
from pathlib import Path

def extract_chunk(chunk_path, chunk_num):
    """从单个块中提取信息"""

    with open(chunk_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取模板（由LLM填充）
    extraction = f"""# Chunk {chunk_num} Extraction

## 原始内容预览
```
{content[:1000]}...
```

## Key Points
- [待提取]

## Key Quotes
- [待提取]

## Entities Mentioned
- People: [待提取]
- Organizations: [待提取]
- Concepts: [待提取]

## Questions Raised
- [待提取]

## Connections
- [待提取]

---

**说明**: 此文件需要由LLM处理填充。请读取原始块文件并提取上述信息。
"""

    return extraction

def main():
    chunks_dir = Path("chunks")
    extractions_dir = Path("extractions")
    extractions_dir.mkdir(exist_ok=True)

    chunk_files = sorted(chunks_dir.glob("chunk_*.txt"))

    for chunk_file in chunk_files:
        chunk_num = int(chunk_file.stem.split('_')[1])
        extraction = extract_chunk(chunk_file, chunk_num)

        output_file = extractions_dir / f"extraction_{chunk_num:03d}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(extraction)

        print(f"创建提取模板: {output_file.name}")

if __name__ == '__main__':
    main()
