#!/usr/bin/env python3
"""
播客摘要处理脚本 - 分块-提取-组装流水线
"""

import re
import os
from pathlib import Path

def semantic_chunking(text, target_chunk_size=8000, overlap=500):
    """
    语义分块：按字符数分割，尽量在句子边界处断开
    目标：每个块约3000字符（中文约1000-1500 tokens）
    """
    # 按句子边界分割（。！？等）
    sentence_endings = r'([。！？\.\?\!])'
    sentences = re.split(sentence_endings, text)

    # 合并句子和其结束符
    pieces = []
    i = 0
    while i < len(sentences) - 1:
        if sentences[i+1] in '。！？.?!':
            pieces.append(sentences[i] + sentences[i+1])
            i += 2
        else:
            pieces.append(sentences[i])
            i += 1
    if i < len(sentences):
        pieces.append(sentences[i])

    chunks = []
    current_chunk = []
    current_size = 0

    for piece in pieces:
        piece = piece.strip()
        if not piece:
            continue

        piece_size = len(piece)

        # 如果添加这个句子会超出目标大小，先保存当前块
        if current_size + piece_size > target_chunk_size and current_chunk:
            chunks.append('\n'.join(current_chunk))
            # 保留重叠部分
            overlap_text = []
            overlap_size = 0
            for p in reversed(current_chunk):
                if overlap_size + len(p) <= overlap:
                    overlap_text.insert(0, p)
                    overlap_size += len(p)
                else:
                    break
            current_chunk = overlap_text
            current_size = overlap_size

        current_chunk.append(piece)
        current_size += piece_size

    # 添加最后一个块
    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    return chunks

def main():
    # 读取输入文件
    input_path = "/root/askbot/anything2post/Anything2Ontology/20260402-130209-bilibili_张晓珺对谢赛宁的7小时马拉松访谈/input/bilibili_张晓珺对谢赛宁的7小时马拉松访谈.md"

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"总字符数: {len(content)}")

    # 提取元数据
    title_match = re.search(r'\*\*Title:\*\* (.+)', content)
    url_match = re.search(r'\*\*Video URL:\*\* (.+)', content)

    metadata = {
        'title': title_match.group(1) if title_match else 'Unknown',
        'url': url_match.group(1) if url_match else 'Unknown',
        'type': '播客访谈',
        'duration': '7小时'
    }

    print(f"标题: {metadata['title']}")
    print(f"URL: {metadata['url']}")

    # 提取正文（Transcript部分之后）
    transcript_match = re.search(r'## Transcript\n\n(.+)', content, re.DOTALL)
    if transcript_match:
        transcript = transcript_match.group(1)
    else:
        transcript = content

    print(f"正文字符数: {len(transcript)}")

    # 分块
    chunks = semantic_chunking(transcript, target_chunk_size=8000, overlap=300)
    print(f"分块数量: {len(chunks)}")

    # 保存分块
    chunks_dir = Path("/root/.agents/skills/content-summarizer-workspace/my-run/chunks")
    chunks_dir.mkdir(exist_ok=True)

    for i, chunk in enumerate(chunks, 1):
        chunk_file = chunks_dir / f"chunk_{i:03d}.txt"
        with open(chunk_file, 'w', encoding='utf-8') as f:
            f.write(f"# Chunk {i}\n\n")
            f.write(chunk)
        print(f"  保存: chunk_{i:03d}.txt ({len(chunk)} 字符)")

    # 保存元数据
    with open(chunks_dir / "metadata.json", 'w', encoding='utf-8') as f:
        import json
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print("\n分块完成!")
    return len(chunks)

if __name__ == '__main__':
    main()
