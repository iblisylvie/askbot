#!/usr/bin/env python3
"""
PDF → Markdown 转换脚本（MinerU API 版）

用法:
    python pdf2md.py input.pdf [output.md] [--language ch|en]

环境变量（按优先级读取，均支持 .env 文件）:
    MINERU_API_KEY            - MinerU API 密钥（必填）
    MINERU_LANGUAGE           - OCR 语言: ch / en（默认 ch）
    MINERU_MAX_FILE_SIZE_MB   - 大文件拆分阈值 MB（默认 2）
    MINERU_PAGES_PER_SPLIT    - 每片段最大页数（默认 400）
    MINERU_TIMEOUT            - 轮询超时秒数（默认 1800）

依赖:
    pip install httpx requests PyPDF2 python-dotenv
"""

import argparse
import io
import os
import sys
import tempfile
import time
import zipfile
from datetime import datetime
from pathlib import Path

import httpx
import requests
from dotenv import load_dotenv

# 从脚本所在目录的 .env 加载环境变量
_SCRIPT_DIR = Path(__file__).resolve().parent
load_dotenv(_SCRIPT_DIR / ".env")

MINERU_BASE_URL = "https://mineru.net/api/v4"
PAGES_PER_SPLIT = int(os.getenv("MINERU_PAGES_PER_SPLIT", "400"))
MAX_FILE_SIZE_MB = int(os.getenv("MINERU_MAX_FILE_SIZE_MB", "2"))
MINERU_TIMEOUT = int(os.getenv("MINERU_TIMEOUT", "1800"))


def get_page_count(file_path: Path) -> int:
    """获取 PDF 页数。"""
    try:
        from PyPDF2 import PdfReader
        return len(PdfReader(file_path).pages)
    except ImportError:
        size_kb = file_path.stat().st_size / 1024
        return max(1, int(size_kb / 100))


def split_pdf(file_path: Path, pages_per_split: int = PAGES_PER_SPLIT) -> list[Path]:
    """将 PDF 拆分为多个小文件。"""
    from PyPDF2 import PdfReader, PdfWriter

    reader = PdfReader(file_path)
    total_pages = len(reader.pages)
    num_splits = (total_pages + pages_per_split - 1) // pages_per_split
    temp_dir = Path(tempfile.mkdtemp(prefix="mineru_splits_"))
    split_files = []

    for i in range(num_splits):
        start_page = i * pages_per_split
        end_page = min((i + 1) * pages_per_split, total_pages)
        writer = PdfWriter()
        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])
        split_path = temp_dir / f"{file_path.stem}_part{i + 1:02d}.pdf"
        with open(split_path, "wb") as f:
            writer.write(f)
        split_files.append(split_path)
        print(f"[SPLIT] 生成片段 {i + 1}/{num_splits}: 页码 {start_page + 1}-{end_page}")

    return split_files


def request_upload_url(client: httpx.Client, filename: str, api_key: str, language: str) -> dict:
    """请求预签名上传 URL。"""
    url = f"{MINERU_BASE_URL}/file-urls/batch"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "files": [
            {
                "name": filename,
                "is_ocr": True,
                "enable_formula": True,
                "enable_table": True,
                "language": language,
            }
        ]
    }
    response = client.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    if data.get("code") != 0:
        raise RuntimeError(f"API error: {data.get('msg', 'Unknown error')}")
    result = data["data"]
    return {"batch_id": result["batch_id"], "upload_url": result["file_urls"][0]}


def upload_file(upload_url: str, file_path: Path) -> None:
    """通过 PUT 请求上传文件。"""
    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    print(f"[UPLOAD] 上传 {file_path.name} ({file_size_mb:.1f} MB)...")
    with open(file_path, "rb") as f:
        response = requests.put(upload_url, data=f, timeout=600)
    response.raise_for_status()
    print(f"[UPLOAD] 上传完成")


def wait_for_completion(client: httpx.Client, batch_id: str, api_key: str, poll_interval: int = 5, timeout: int = MINERU_TIMEOUT) -> dict:
    """轮询等待提取完成。"""
    url = f"{MINERU_BASE_URL}/extract-results/batch/{batch_id}"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            raise TimeoutError(f"提取超时（{timeout} 秒）")

        response = client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get("code") != 0:
            raise RuntimeError(f"API error: {data.get('msg', 'Unknown error')}")

        results = data.get("data", {})
        extract_results = results.get("extract_result", [])
        if not extract_results:
            time.sleep(poll_interval)
            continue

        file_result = extract_results[0]
        state = file_result.get("state", "unknown")

        if state == "done":
            print(f"[DONE] 提取完成，耗时 {elapsed:.0f} 秒")
            return file_result
        elif state == "failed":
            raise RuntimeError(f"提取失败: {file_result.get('err_msg', 'Unknown error')}")
        else:
            progress = file_result.get("extract_progress", {})
            extracted = progress.get("extracted_pages", 0)
            total = progress.get("total_pages", "?")
            print(f"[WAIT] 提取中... {state} | 页码 {extracted}/{total} | 已耗时 {elapsed:.0f}s")
            time.sleep(poll_interval)


def download_and_extract(client: httpx.Client, zip_url: str, images_dir: Path) -> str:
    """下载 ZIP 结果并提取 Markdown 内容与图片。"""
    print(f"[DOWNLOAD] 下载提取结果...")
    response = client.get(zip_url)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        md_files = [f for f in zf.namelist() if f.endswith(".md")]
        if not md_files:
            raise RuntimeError("结果 ZIP 中未找到 Markdown 文件")
        md_file = "full.md" if "full.md" in md_files else md_files[0]
        content = zf.read(md_file).decode("utf-8")

        # 提取图片到 images_dir
        image_files = [f for f in zf.namelist() if f.startswith("images/") and not f.endswith("/")]
        if image_files:
            images_dir.mkdir(parents=True, exist_ok=True)
            for img_path in image_files:
                img_data = zf.read(img_path)
                dest = images_dir / Path(img_path).name
                dest.write_bytes(img_data)
            print(f"[DOWNLOAD] 提取 {len(image_files)} 张图片到 {images_dir}")

    print(f"[DOWNLOAD] 成功提取 Markdown（{len(content)} 字符）")
    return content


def process_single_pdf(file_path: Path, api_key: str, language: str, images_dir: Path) -> str:
    """处理单个 PDF（或拆分后的片段）。"""
    with httpx.Client(timeout=300) as client:
        upload_data = request_upload_url(client, file_path.name, api_key, language)
        batch_id = upload_data["batch_id"]
        upload_url = upload_data["upload_url"]
        upload_file(upload_url, file_path)
        result = wait_for_completion(client, batch_id, api_key)
        zip_url = result.get("full_zip_url")
        if not zip_url:
            raise RuntimeError("结果中缺少下载 URL")
        return download_and_extract(client, zip_url, images_dir)


def process_large_pdf(file_path: Path, page_count: int, pages_per_split: int, api_key: str, language: str, images_dir: Path) -> str:
    """处理大体积 PDF：拆分、逐个处理、合并结果。"""
    split_files = split_pdf(file_path, pages_per_split)
    try:
        parts = []
        for i, split_path in enumerate(split_files, 1):
            print(f"\n[PROCESS] 处理片段 {i}/{len(split_files)}: {split_path.name}")
            content = process_single_pdf(split_path, api_key, language, images_dir)
            parts.append(content)

        combined = []
        for i, content in enumerate(parts, 1):
            if i > 1:
                combined.append(f"\n\n---\n\n# Part {i}\n\n")
            combined.append(content)
        return "".join(combined)
    finally:
        for split_path in split_files:
            try:
                split_path.unlink()
            except Exception:
                pass
        try:
            split_files[0].parent.rmdir()
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(description="PDF → Markdown 转换（MinerU API）")
    parser.add_argument("input", help="输入 PDF 文件路径")
    parser.add_argument("output", nargs="?", help="输出 Markdown 文件路径（默认与 PDF 同名）")
    parser.add_argument("--language", default=os.getenv("MINERU_LANGUAGE", "ch"), choices=["ch", "en"], help="OCR 语言（默认从 MINERU_LANGUAGE 环境变量读取）")
    args = parser.parse_args()

    api_key = os.environ.get("MINERU_API_KEY")
    if not api_key:
        print("[ERROR] 环境变量 MINERU_API_KEY 未设置", file=sys.stderr)
        sys.exit(1)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[ERROR] 文件不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output) if args.output else input_path.with_suffix(".md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    images_dir = output_path.parent / "images"

    print(f"[START] 开始处理: {input_path.name}")
    started_at = datetime.now()

    page_count = get_page_count(input_path)
    file_size_mb = input_path.stat().st_size / (1024 * 1024)
    print(f"[INFO] 页数: {page_count}, 大小: {file_size_mb:.1f} MB")

    needs_split = page_count > PAGES_PER_SPLIT or file_size_mb > MAX_FILE_SIZE_MB
    if needs_split:
        if file_size_mb > MAX_FILE_SIZE_MB:
            pages_per_mb = page_count / file_size_mb
            pages_per_split = int(pages_per_mb * MAX_FILE_SIZE_MB * 0.8)
            pages_per_split = max(50, min(pages_per_split, PAGES_PER_SPLIT))
        else:
            pages_per_split = PAGES_PER_SPLIT
        print(f"[SPLIT] 文件过大，按 {pages_per_split} 页/片段拆分处理")
        content = process_large_pdf(input_path, page_count, pages_per_split, api_key, args.language, images_dir)
    else:
        content = process_single_pdf(input_path, api_key, args.language, images_dir)

    output_path.write_text(content, encoding="utf-8")
    duration = (datetime.now() - started_at).total_seconds()
    print(f"[SUCCESS] 输出已保存: {output_path} ({len(content)} 字符, 耗时 {duration:.1f} 秒)")


if __name__ == "__main__":
    main()
