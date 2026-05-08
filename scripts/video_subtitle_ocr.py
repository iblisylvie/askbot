#!/usr/bin/env python3
"""
视频硬字幕 OCR 提取脚本（PaddleOCR 版）

通过读取视频帧并对底部区域进行 OCR，提取画面中的硬字幕（burned-in subtitles）。
适用于访谈、纪录片、影视剧等底部字幕场景。

用法:
    python video_subtitle_ocr.py input.mp4 [output.txt]

依赖:
    pip install opencv-python paddlepaddle paddleocr numpy
"""

# /// script
# dependencies = [
#     "opencv-python",
#     "paddlepaddle",
#     "paddleocr",
#     "numpy",
# ]
# ///

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np


@dataclass
class SubtitleEntry:
    """单条字幕记录。"""

    start_time: float
    end_time: float = field(default=0.0)
    text: str = ""


def extract_roi(frame: np.ndarray, bottom_ratio: float) -> np.ndarray:
    """提取帧的底部 ROI 区域。"""
    h, w = frame.shape[:2]
    y_start = int(h * (1 - bottom_ratio))
    return frame[y_start:h, 0:w]


def frame_difference(roi1: np.ndarray, roi2: np.ndarray) -> float:
    """计算两帧 ROI 的灰度 MSE（均方误差）。"""
    if roi1.shape != roi2.shape:
        # 尺寸不同时 resize 到相同大小
        h, w = min(roi1.shape[0], roi2.shape[0]), min(roi1.shape[1], roi2.shape[1])
        roi1 = cv2.resize(roi1, (w, h))
        roi2 = cv2.resize(roi2, (w, h))
    gray1 = cv2.cvtColor(roi1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(roi2, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(gray1, gray2)
    return float(np.mean(diff))


def normalize_text(text: str) -> str:
    """文本归一化：去首尾空白、统一中英文标点、折叠内部空白。"""
    text = text.strip()
    if not text:
        return ""
    # 统一全角/半角标点
    text = unicodedata.normalize("NFKC", text)
    # 去除内部多余空白和换行
    text = re.sub(r"\s+", " ", text)
    # 统一常见标点
    text = text.replace(",", "，").replace(".", "。").replace("!", "！").replace("?", "？")
    return text.strip()


def format_timestamp_txt(seconds: float) -> str:
    """格式化为 [MM:SS.mmm] 样式。"""
    m = int(seconds // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{m:02d}:{s:02d}.{ms:03d}"


def format_timestamp_srt(seconds: float) -> str:
    """格式化为 SRT 时间戳 HH:MM:SS,mmm。"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_output(entries: list[SubtitleEntry], output_path: Path, fmt: str) -> None:
    """将字幕条目写入文件。"""
    output_path.write_text("", encoding="utf-8")
    lines: list[str] = []

    if fmt == "srt":
        for idx, entry in enumerate(entries, start=1):
            if not entry.text:
                continue
            start = format_timestamp_srt(entry.start_time)
            end = format_timestamp_srt(entry.end_time)
            lines.append(f"{idx}")
            lines.append(f"{start} --> {end}")
            lines.append(entry.text)
            lines.append("")
    else:
        for entry in entries:
            if not entry.text:
                continue
            start = format_timestamp_txt(entry.start_time)
            end = format_timestamp_txt(entry.end_time)
            lines.append(f"[{start} - {end}] {entry.text}")

    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="从视频中通过 OCR 提取底部硬字幕")
    parser.add_argument("input", help="输入 MP4 视频文件路径")
    parser.add_argument("output", nargs="?", help="输出文件路径（默认 input_subtitles.txt）")
    parser.add_argument(
        "--bottom-ratio",
        type=float,
        default=0.18,
        help="字幕区域占画面底部的比例（0-1，默认 0.18）",
    )
    parser.add_argument(
        "--sample-interval",
        type=float,
        default=1.0,
        help="最小采样间隔（秒，默认 1.0）",
    )
    parser.add_argument(
        "--diff-threshold",
        type=float,
        default=3.0,
        help="帧间灰度差异阈值（MSE，默认 3.0）。低于此值视为画面未变化",
    )
    parser.add_argument(
        "--ocr-interval",
        type=float,
        default=2.0,
        help="对同一条字幕的最小 OCR 间隔（秒，默认 2.0）",
    )
    parser.add_argument(
        "--format",
        choices=["txt", "srt"],
        default="txt",
        help="输出格式（默认 txt）",
    )
    parser.add_argument(
        "--lang",
        default="ch",
        help="PaddleOCR 语言（默认 ch，可选 en / ch_en 等）",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="打印处理进度",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误: 输入文件不存在: {input_path}", file=sys.stderr)
        return 1

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix(f"_subtitles.{args.format}")

    if args.verbose:
        print(f"[INFO] 输入: {input_path}")
        print(f"[INFO] 输出: {output_path}")
        print(f"[INFO] 底部区域比例: {args.bottom_ratio}")
        print(f"[INFO] 采样间隔: {args.sample_interval}s")
        print(f"[INFO] 差异阈值: {args.diff_threshold}")
        print(f"[INFO] OCR 语言: {args.lang}")

    # ---- 初始化 PaddleOCR（延迟导入，首次加载较慢） ----
    if args.verbose:
        print("[INFO] 正在初始化 PaddleOCR 模型...")
    from paddleocr import PaddleOCR

    ocr = PaddleOCR(
        use_angle_cls=True,
        lang=args.lang,
        show_log=False,
    )
    if args.verbose:
        print("[INFO] PaddleOCR 初始化完成")

    # ---- 打开视频 ----
    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        print(f"错误: 无法打开视频: {input_path}", file=sys.stderr)
        return 1

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0
    if args.verbose:
        print(f"[INFO] 视频时长: {duration:.1f}s, FPS: {fps:.2f}, 总帧数: {total_frames}")

    # ---- 主循环：启发式采样 + OCR ----
    entries: list[SubtitleEntry] = []
    current_entry: SubtitleEntry | None = None

    prev_roi: np.ndarray | None = None
    prev_text: str = ""
    prev_ocr_time: float = -999.0
    last_diff: float = 0.0

    sample_interval = max(0.1, args.sample_interval)
    timestamp = 0.0
    ocr_count = 0
    skip_count = 0

    while timestamp <= duration:
        frame_idx = int(timestamp * fps)
        if frame_idx >= total_frames:
            break

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret or frame is None:
            timestamp += sample_interval
            continue

        roi = extract_roi(frame, args.bottom_ratio)

        # --- 启发式 1: 帧间差异检测 ---
        should_ocr = True
        if prev_roi is not None:
            diff = frame_difference(prev_roi, roi)
            last_diff = diff
            if diff < args.diff_threshold:
                # 画面几乎没变化
                should_ocr = False
                skip_count += 1
                if args.verbose:
                    print(
                        f"  [{format_timestamp_txt(timestamp)}] SKIP (diff={diff:.2f} < {args.diff_threshold})"
                    )

        # --- 启发式 2: 同一条字幕最小 OCR 间隔 ---
        if should_ocr and (timestamp - prev_ocr_time) < args.ocr_interval:
            should_ocr = False
            skip_count += 1
            if args.verbose:
                print(
                    f"  [{format_timestamp_txt(timestamp)}] SKIP (ocr_interval, last={prev_ocr_time:.1f}s)"
                )

        if should_ocr:
            # 执行 OCR
            result = ocr.ocr(roi, cls=True)
            texts: list[str] = []
            if result and result[0]:
                for line in result[0]:
                    if line:
                        texts.append(str(line[1][0]))
            raw_text = " ".join(texts)
            text = normalize_text(raw_text)
            ocr_count += 1
            prev_ocr_time = timestamp

            if args.verbose:
                status = text if text else "(无文字)"
                print(f"  [{format_timestamp_txt(timestamp)}] OCR: {status} (diff={last_diff:.2f})")

            # --- 启发式 3: 文本去重合并 ---
            if text:
                if current_entry is None:
                    current_entry = SubtitleEntry(start_time=timestamp, end_time=timestamp, text=text)
                elif text == prev_text:
                    # 同一条字幕延续
                    current_entry.end_time = timestamp
                else:
                    # 新字幕出现，保存上一条（结束时间设为当前时刻）
                    current_entry.end_time = timestamp
                    entries.append(current_entry)
                    current_entry = SubtitleEntry(start_time=timestamp, end_time=timestamp, text=text)
                prev_text = text
            else:
                # 当前帧无文字，如果之前有字幕，给它一个结束缓冲
                if current_entry is not None:
                    current_entry.end_time = timestamp
                    entries.append(current_entry)
                    current_entry = None
                    prev_text = ""

        prev_roi = roi
        timestamp += sample_interval

    # 收尾
    if current_entry is not None:
        if current_entry.end_time <= current_entry.start_time:
            current_entry.end_time = duration
        entries.append(current_entry)

    cap.release()

    # 合并时间过近且文本相同的条目（缓冲去重）
    merged: list[SubtitleEntry] = []
    for e in entries:
        if not merged:
            merged.append(e)
            continue
        last = merged[-1]
        if last.text == e.text and (e.start_time - last.end_time) <= sample_interval * 1.5:
            last.end_time = e.end_time
        else:
            merged.append(e)

    # ---- 输出 ----
    write_output(merged, output_path, args.format)

    if args.verbose:
        print(f"\n[INFO] 处理完成")
        print(f"[INFO] 总采样帧数: {int(duration / sample_interval)}")
        print(f"[INFO] 实际 OCR 次数: {ocr_count}")
        print(f"[INFO] 跳过次数: {skip_count}")
        print(f"[INFO] 提取字幕条数: {len(merged)}")
        print(f"[INFO] 输出文件: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
