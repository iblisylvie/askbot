#!/usr/bin/env python3
"""
Bilibili 视频字幕提取脚本。

通过 yt-dlp 提取 CC/AI 字幕，无字幕时可选 faster-whisper 转录。
Bilibili 的 AI 字幕（ai-zh）存在同音字识别错误（如"罗福利"→"罗福莉"），
对准确度要求高的场景建议加 --transcribe 用 Whisper 重新转录。

用法:
    python bilibili_subtitle.py <URL> [-o output.md] [-f markdown|txt|json|srt]

依赖:
    pip install yt-dlp
    # 如需转录 fallback:
    pip install faster-whisper
"""

import argparse
import json
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# ---- 配置 ----

LANG_PRIORITY = ["zh-Hans", "zh", "zh-CN", "en", "ai-zh"]
PREFERRED_EXTS = ["json3", "srv3", "vtt", "srt", "json"]

_SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_COOKIE_FILE = _SCRIPT_DIR / "bilibili.com_cookies.txt"


# ---- yt-dlp 获取字幕 ----

def extract_info(url: str, cookie_opts: dict) -> tuple[str, str]:
    import yt_dlp

    ydl_opts = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
        **cookie_opts,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if info is None:
            raise ValueError(f"无法提取视频信息: {url}")

        video_id = info.get("id", "")
        title = info.get("title", "Untitled")

        bv_match = re.search(r"(BV[a-zA-Z0-9]+)", info.get("webpage_url", url))
        if bv_match:
            video_id = bv_match.group(1)

        if not video_id:
            raise ValueError(f"无法提取视频 ID: {url}")

        return video_id, title


def try_subtitles(url: str, cookie_opts: dict) -> list[dict] | None:
    import yt_dlp

    ydl_opts = {
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": LANG_PRIORITY,
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
        **cookie_opts,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if info is None:
            return None

        req_subs = info.get("requested_subtitles") or {}
        all_subs = info.get("subtitles") or {}
        auto_subs = info.get("automatic_captions") or {}

        # 1. requested_subtitles（yt-dlp 按优先级已选定的字幕）
        for lang in LANG_PRIORITY:
            sub_info = req_subs.get(lang)
            if sub_info:
                segments = _fetch_subtitle_data(ydl, sub_info, lang)
                if segments:
                    return segments

        # 2. manual subtitles（人工上传字幕）
        for lang in LANG_PRIORITY:
            sub_info = all_subs.get(lang)
            if sub_info:
                segments = _parse_subtitle_formats(ydl, sub_info, lang)
                if segments:
                    return segments

        # 3. automatic captions（自动生成字幕）
        for lang in LANG_PRIORITY:
            sub_info = auto_subs.get(lang)
            if sub_info:
                segments = _parse_subtitle_formats(ydl, sub_info, lang)
                if segments:
                    return segments

    return None


def _fetch_subtitle_data(ydl, sub_info: dict, lang: str) -> list[dict] | None:
    """处理 requested_subtitles 中的字幕（可能是内嵌 data 或需下载 url）。"""
    if "data" in sub_info:
        return parse_subtitle_content(sub_info["data"], sub_info.get("ext", "json"))

    sub_url = sub_info.get("url")
    if not sub_url:
        return None

    try:
        data = ydl.urlopen(sub_url).read().decode("utf-8")
        return parse_subtitle_content(data, sub_info.get("ext", "json"))
    except Exception as e:
        print(f"[WARN] 获取字幕失败 ({lang}): {e}", file=sys.stderr)
        return None


def _parse_subtitle_formats(ydl, sub_formats: list, lang: str) -> list[dict] | None:
    """尝试多种格式，优先 json3 / srv3 / vtt。"""
    sorted_formats = sorted(
        sub_formats,
        key=lambda f: (
            PREFERRED_EXTS.index(f.get("ext", ""))
            if f.get("ext", "") in PREFERRED_EXTS
            else len(PREFERRED_EXTS)
        ),
    )
    for fmt in sorted_formats:
        sub_url = fmt.get("url")
        if not sub_url:
            continue
        try:
            data = ydl.urlopen(sub_url).read().decode("utf-8")
            segments = parse_subtitle_content(data, fmt.get("ext", "json"))
            if segments:
                return segments
        except Exception as e:
            print(f"[WARN] 解析字幕格式失败 ({lang}, {fmt.get('ext')}): {e}", file=sys.stderr)
            continue
    return None


def parse_subtitle_content(data: str, ext: str) -> list[dict] | None:
    """解析各种字幕格式为统一结构。"""
    segments = []

    try:
        if ext in ("json3", "json"):
            parsed = json.loads(data)
            events = parsed.get("events") or parsed.get("body") or []
            if isinstance(events, list):
                for event in events:
                    if "segs" in event:
                        text = "".join(
                            seg.get("utf8", "") for seg in event.get("segs", [])
                        ).strip()
                        if text and text != "\n":
                            segments.append({
                                "text": text,
                                "start": event.get("tStartMs", 0) / 1000,
                            })
                    elif "content" in event:
                        text = event["content"].strip()
                        if text:
                            segments.append({
                                "text": text,
                                "start": event.get("from", 0),
                            })
                    elif "text" in event:
                        text = event["text"].strip()
                        if text:
                            segments.append({
                                "text": text,
                                "start": event.get("start", 0),
                            })

        elif ext in ("srv3", "srv2", "srv1"):
            import xml.etree.ElementTree as ET
            root = ET.fromstring(data)
            for p in root.iter("p"):
                text = (p.text or "").strip()
                if text:
                    t = int(p.get("t", "0"))
                    segments.append({"text": text, "start": t / 1000})

        elif ext == "vtt":
            lines = data.strip().split("\n")
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if "-->" in line:
                    text_parts = []
                    i += 1
                    while i < len(lines) and lines[i].strip():
                        text_parts.append(lines[i].strip())
                        i += 1
                    text = " ".join(text_parts)
                    text = re.sub(r"<[^>]+>", "", text).strip()
                    if text:
                        time_match = re.match(r"(\d+):(\d+):(\d+)\.(\d+)", line)
                        start = 0.0
                        if time_match:
                            h, m, s, ms = time_match.groups()
                            start = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
                        segments.append({"text": text, "start": start})
                i += 1

        elif ext == "srt":
            blocks = re.split(r"\n\n+", data.strip())
            for block in blocks:
                block_lines = block.strip().split("\n")
                if len(block_lines) >= 3:
                    time_line = block_lines[1]
                    text = " ".join(block_lines[2:]).strip()
                    text = re.sub(r"<[^>]+>", "", text)
                    if text:
                        time_match = re.match(r"(\d+):(\d+):(\d+),(\d+)", time_line)
                        start = 0.0
                        if time_match:
                            h, m, s, ms = time_match.groups()
                            start = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
                        segments.append({"text": text, "start": start})

    except Exception as e:
        print(f"[WARN] 解析字幕内容失败 ({ext}): {e}", file=sys.stderr)
        return None

    return segments if segments else None


# ---- 转录 fallback ----

def download_and_transcribe(url: str, cookie_opts: dict, model_size: str = "small") -> list[dict]:
    import yt_dlp
    from faster_whisper import WhisperModel

    try:
        import torch
        device, compute_type = ("cuda", "float16") if torch.cuda.is_available() else ("cpu", "int8")
    except ImportError:
        device, compute_type = "cpu", "int8"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "wav"}],
            "outtmpl": str(temp_path / "%(id)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
            **cookie_opts,
        }

        print("[INFO] 正在下载音频用于转录...", file=sys.stderr)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info is None:
                raise RuntimeError("音频下载失败")

        wav_files = list(temp_path.glob("*.wav"))
        if not wav_files:
            raise RuntimeError("未找到下载的音频文件")

        audio_path = wav_files[0]
        print(f"[INFO] 使用 faster-whisper ({model_size}, {device}) 转录...", file=sys.stderr)

        model = WhisperModel(model_size, device=device, compute_type=compute_type)
        raw_segments, transcribe_info = model.transcribe(str(audio_path), language="zh")

        segments = []
        for seg in raw_segments:
            text = seg.text.strip()
            if text:
                segments.append({"text": text, "start": seg.start})

        print(f"[INFO] 转录完成: {len(segments)} 段, 语言={transcribe_info.language}", file=sys.stderr)
        return segments


# ---- 输出格式化 ----

def format_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_markdown(url: str, video_id: str, title: str, segments: list[dict]) -> str:
    lines = [
        "# Bilibili Video Transcript",
        "",
        f"**Video URL:** {url}",
        f"**Video ID:** {video_id}",
        f"**Title:** {title}",
        "",
        "---",
        "",
        "## Transcript",
        "",
    ]

    current_paragraph = []
    for segment in segments:
        text = segment.get("text", "").strip()
        if text:
            current_paragraph.append(text)
            if text.endswith((".", "!", "?", "...", "。", "！", "？")):
                lines.append(" ".join(current_paragraph))
                lines.append("")
                current_paragraph = []

    if current_paragraph:
        lines.append(" ".join(current_paragraph))

    return "\n".join(lines)


def format_txt(segments: list[dict]) -> str:
    lines = []
    current_paragraph = []
    for segment in segments:
        text = segment.get("text", "").strip()
        if text:
            current_paragraph.append(text)
            if text.endswith((".", "!", "?", "...", "。", "！", "？")):
                lines.append("".join(current_paragraph))
                current_paragraph = []
    if current_paragraph:
        lines.append("".join(current_paragraph))
    return "\n\n".join(lines)


def format_json(url: str, video_id: str, title: str, segments: list[dict]) -> str:
    return json.dumps({
        "url": url,
        "video_id": video_id,
        "title": title,
        "segments": segments,
    }, ensure_ascii=False, indent=2)


def format_srt(segments: list[dict]) -> str:
    lines = []
    for i, segment in enumerate(segments, 1):
        start = segment.get("start", 0)
        end = start + 3.0
        if i < len(segments):
            end = segments[i].get("start", start + 3.0)

        lines.append(str(i))
        lines.append(f"{format_time(start)} --> {format_time(end)}")
        lines.append(segment.get("text", ""))
        lines.append("")
    return "\n".join(lines)


def format_output(segments: list[dict], fmt: str, url: str, video_id: str, title: str) -> str:
    if fmt == "markdown":
        return format_markdown(url, video_id, title, segments)
    if fmt == "txt":
        return format_txt(segments)
    if fmt == "json":
        return format_json(url, video_id, title, segments)
    if fmt == "srt":
        return format_srt(segments)
    raise ValueError(f"不支持的格式: {fmt}")


# ---- CLI ----

def main():
    parser = argparse.ArgumentParser(description="提取 Bilibili 视频字幕")
    parser.add_argument("url", help="Bilibili 视频链接")
    parser.add_argument("-o", "--output", help="输出文件路径（默认输出到 stdout）")
    parser.add_argument(
        "-f", "--format",
        default="markdown",
        choices=["markdown", "txt", "json", "srt"],
        help="输出格式（默认 markdown）",
    )
    parser.add_argument("--cookiefile", help="Netscape cookie 文件路径")
    parser.add_argument("--cookies-from-browser", help="从浏览器读取 cookies（如 chrome, firefox）")
    parser.add_argument("--transcribe", action="store_true", help="无字幕时下载音频并转录")
    parser.add_argument("--model", default="small", help="Whisper 模型大小（默认 small）")
    args = parser.parse_args()

    cookie_opts = {}
    if args.cookiefile:
        cookie_opts["cookiefile"] = args.cookiefile
    elif args.cookies_from_browser:
        cookie_opts["cookiesfrombrowser"] = (args.cookies_from_browser,)
    elif DEFAULT_COOKIE_FILE.exists():
        cookie_opts["cookiefile"] = str(DEFAULT_COOKIE_FILE)

    started_at = datetime.now()
    print(f"[START] 开始处理: {args.url}", file=sys.stderr)

    video_id, title = extract_info(args.url, cookie_opts)
    print(f"[INFO] 视频 ID: {video_id}, 标题: {title}", file=sys.stderr)

    segments = try_subtitles(args.url, cookie_opts)

    if segments is None:
        print("[INFO] 未找到在线字幕", file=sys.stderr)
        if args.transcribe:
            try:
                segments = download_and_transcribe(args.url, cookie_opts, args.model)
            except ImportError:
                print("[ERROR] faster-whisper 未安装，无法转录。请执行: pip install faster-whisper", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"[ERROR] 转录失败: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print("[ERROR] 无可用字幕。如需转录，请添加 --transcribe 参数。", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"[INFO] 找到字幕，共 {len(segments)} 段", file=sys.stderr)

    content = format_output(segments, args.format, args.url, video_id, title)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        duration = (datetime.now() - started_at).total_seconds()
        print(f"[SUCCESS] 已保存: {output_path} ({len(content)} 字符, 耗时 {duration:.1f} 秒)", file=sys.stderr)
    else:
        print(content)


if __name__ == "__main__":
    main()
