#!/usr/bin/env python3
"""
语音转写文本处理器
自动解析会议转写文本，识别主持人，按session拆分，生成结构化素材。
支持通过LLM生成session标题。
"""

import re
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# LLM支持
try:
    from litellm import completion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    print("警告: litellm未安装，LLM标题生成功能不可用")


@dataclass
class Segment:
    """转写段落"""
    speaker: str
    timestamp: str
    content: str
    line_number: int


@dataclass
class Session:
    """一个session（讨论主题）"""
    index: int
    title: str
    speaker: str  # 主讲人ID (如: 说话人1) - 保留主发言人用于LLM提示
    speaker_name: str  # 主讲人显示名称 (如: 秦立明老师)
    all_speakers: Dict[str, str]  # 所有参与讲者 {speaker_id: display_name}
    segments: List[Segment]
    start_time: str
    end_time: str


def parse_time_to_seconds(time_str: str) -> int:
    """将时间字符串转换为秒数"""
    parts = time_str.strip().split(':')
    if len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + int(seconds)
    elif len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
    return 0


def parse_transcript(content: str) -> Tuple[List[Segment], str]:
    """解析转写文件内容"""
    segments = []
    lines = content.split('\n')

    # 第一行通常是录音信息
    recording_info = lines[0].strip() if lines else ""

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 匹配说话人和时间戳行
        # 格式: 说话人1 00:00 或 说话人1 01:23:45
        speaker_match = re.match(r'^(说话人\d+|\S+)\s+(\d{1,2}:\d{2}(?::\d{2})?)\s*$', line)

        if speaker_match:
            speaker = speaker_match.group(1)
            timestamp = speaker_match.group(2)

            # 下一行是内容
            i += 1
            content_lines = []
            while i < len(lines):
                # 如果遇到下一个说话人或空行（后面跟着说话人），停止
                if re.match(r'^(说话人\d+|\S+)\s+\d{1,2}:\d{2}(?::\d{2})?\s*$', lines[i].strip()):
                    break
                content_lines.append(lines[i])
                i += 1

            content_text = '\n'.join(content_lines).strip()

            if content_text:  # 只保留有内容的段落
                segments.append(Segment(
                    speaker=speaker,
                    timestamp=timestamp,
                    content=content_text,
                    line_number=i
                ))
        else:
            i += 1

    return segments, recording_info


def identify_host(segments: List[Segment]) -> Optional[str]:
    """识别主持人（说话最少且包含过渡语的人）"""
    if not segments:
        return None

    speaker_stats = {}
    host_keywords = ['接下来', '下面', '有请', '欢迎', '感谢.*分享', '掌声', '环节']

    for seg in segments:
        if seg.speaker not in speaker_stats:
            speaker_stats[seg.speaker] = {'count': 0, 'host_signals': 0}
        speaker_stats[seg.speaker]['count'] += 1

        # 检测主持关键词
        for kw in host_keywords:
            if re.search(kw, seg.content):
                speaker_stats[seg.speaker]['host_signals'] += 1

    # 排序：优先看主持信号，然后看说话数量（少的更可能是主持人）
    candidates = sorted(speaker_stats.items(),
                       key=lambda x: (-x[1]['host_signals'], x[1]['count']))

    # 如果有主持信号，选信号最多的；否则选说话最少的
    if candidates and candidates[0][1]['host_signals'] > 0:
        return candidates[0][0]
    elif candidates:
        return min(speaker_stats.items(), key=lambda x: x[1]['count'])[0]
    return None


def detect_session_boundaries(segments: List[Segment], host: Optional[str]) -> List[int]:
    """
    检测session边界
    基于主持人过渡语识别
    """
    if not segments:
        return []

    boundaries = [0]  # 第一个session从0开始

    # session切换信号（主持人明确切换议程）
    transition_patterns = [
        r'接下来.*有请.*老师',
        r'接下来.*(进入|是).*环节',
        r'下面.*欢迎.*老师',
        r'掌声.*有请',
        r'.*带来.*(主题|演讲|分享)',
    ]

    last_boundary_time = 0

    for i, seg in enumerate(segments):
        if i == 0:
            continue

        is_host = host and seg.speaker == host
        curr_time = parse_time_to_seconds(seg.timestamp)

        # 主持人+切换关键词，且距离上一个边界有一定间隔（>2分钟）
        if is_host:
            for pattern in transition_patterns:
                if re.search(pattern, seg.content):
                    if curr_time - last_boundary_time > 120:  # 至少2分钟间隔
                        boundaries.append(i)
                        last_boundary_time = curr_time
                        break

    return boundaries


def extract_speakers_with_llm(intro_content: str) -> Dict[str, str]:
    """使用LLM从主持人介绍中提取所有讲者姓名

    Returns:
        Dict[speaker_id, display_name] - 讲者ID到显示名称的映射
        例如: {"说话人3": "张老师", "说话人5": "尹老师"}
    """
    if not LITELLM_AVAILABLE:
        return {}

    api_key = os.getenv('LLM_API_KEY')
    api_base = os.getenv('LLM_API_BASE', 'https://api.openai.com/v1')
    model = os.getenv('LLM_MODEL', 'gpt-4o-mini')

    if not api_key:
        return {}

    system_prompt = """你是一个专业的会议内容解析助手。请从主持人的介绍语中提取所有被介绍的讲者姓名。

要求：
1. 识别所有被提及的讲者（可能有多人）
2. 提取讲者的称呼（如张老师、李博士、王工程师等）
3. 如果有职位/头衔，一并提取（如"腾讯云安全专家张玉峰"提取为"腾讯云安全专家张玉峰"或"张玉峰老师"）
4. 以JSON格式返回，格式: {"讲者1": "称呼", "讲者2": "称呼"}
5. 如果无法确定具体人名，返回空对象 {}
6. 只返回JSON，不要其他解释文字"""

    user_prompt = f"""请从以下主持人介绍语中提取所有讲者姓名：

{intro_content}

请以JSON格式返回："""

    try:
        response = completion(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=200,
            temperature=0.1,
            api_key=api_key,
            api_base=api_base if 'openai' in model or 'http' in api_base else None
        )

        result = response.choices[0].message.content.strip()
        # 清理markdown代码块
        result = result.replace('```json', '').replace('```', '').strip()

        import json
        speakers = json.loads(result)
        return speakers if isinstance(speakers, dict) else {}
    except Exception as e:
        print(f"    LLM提取讲者失败: {e}")
        return {}


def extract_speaker_from_intro(content: str) -> Optional[Tuple[str, str]]:
    """从主持人介绍中提取主讲人姓名（备用方案）

    Returns:
        Tuple[身份标识, 姓名] 或 None
        身份标识如: "老师", "专家", "博士"等
    """
    # 匹配模式扩展
    patterns = [
        # 有请/欢迎 XXX老师/专家/博士/经理
        (r'有请\s*(\S+?)(老师|专家|博士|经理|总监|架构师|工程师)', 2),
        (r'欢迎\s*(\S+?)(老师|专家|博士|经理|总监|架构师|工程师)', 2),
        # XXX老师/专家 为我们分享
        (r'(\S+?)(老师|专家|博士)\s+(?:为?我们)?(?:带来|分享|演讲|介绍)', 2),
        # 掌声有请 XXX
        (r'掌声.*有请\s+(\S+?)(?:老师|专家)?[,，\s]', 1),
        # 接下来.*XXX.*分享
        (r'接下来.*?(\S+?)(?:老师|专家)?.*?(?:分享|演讲|介绍)', 1),
    ]

    for pattern, name_group in patterns:
        match = re.search(pattern, content)
        if match:
            name = match.group(1).strip()
            # 过滤掉常见干扰词
            if name in ['大家', '各位', '我们', '接下来', '掌声']:
                continue
            # 尝试获取身份标识
            title = match.group(2) if match.lastindex >= 2 else "老师"
            return (title, name)

    return None


def extract_all_speakers_from_intro(content: str) -> List[str]:
    """从主持人介绍中提取所有讲者姓名（备用方案的多讲者版本）

    Returns:
        List[姓名+称呼] - 讲者列表，如 ["张老师", "李老师", "王专家"]
    """
    speakers = []
    found_names = set()

    # 优先匹配完整姓名（2-4个中文字符）
    patterns = [
        # 职位+姓名+头衔
        r'(?:首席专家|专家|架构师|总监|经理|工程师)([\u4e00-\u9fff]{2,4})(老师|专家|博士)',
        # 欢迎/有请+姓名+头衔
        r'(?:有请|欢迎)\s*([\u4e00-\u9fff]{2,4})(老师|专家|博士)',
        # 接下来...姓名+头衔
        r'接下来.*?([\u4e00-\u9fff]{2,4})(老师|专家|博士)',
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            name = match.group(1).strip()
            title = match.group(2)

            # 过滤边界问题（如"师秦立明"）和干扰词
            if '师' in name or name in ['大家', '各位', '我们', '接下来', '掌声']:
                continue
            if len(name) < 2 or len(name) > 4:
                continue

            full_name = f"{name}{title}"
            if name not in found_names:
                found_names.add(name)
                speakers.append(full_name)

    return speakers


def build_speaker_name_map(segments: List[Segment], host: Optional[str],
                           boundaries: List[int]) -> Dict[str, str]:
    """建立说话人ID到真实姓名的映射

    策略：
    1. 在每个session边界前后，查找主持人的介绍语
    2. 使用LLM从介绍语中提取所有讲者姓名
    3. 根据发言顺序和频率，将姓名映射到speaker_id
    """
    speaker_map = {}

    for i, boundary_idx in enumerate(boundaries):
        # 确定session范围
        session_start = boundary_idx
        session_end = boundaries[i + 1] if i + 1 < len(boundaries) else len(segments)

        # 收集这个session中所有非主持人的发言者
        session_speakers = []
        speaker_counts = {}
        for k in range(session_start, session_end):
            if k < len(segments):
                spk = segments[k].speaker
                if spk != host and spk not in session_speakers:
                    session_speakers.append(spk)
                if spk != host:
                    speaker_counts[spk] = speaker_counts.get(spk, 0) + 1

        if not session_speakers:
            continue

        # 在边界前后查找主持人的介绍语（扩大搜索范围）
        search_range = range(max(0, boundary_idx - 5), min(len(segments), session_start + 10))
        intro_content = ""

        for j in search_range:
            seg = segments[j]
            if host and seg.speaker == host:
                intro_content += seg.content + "\n"

        if not intro_content:
            continue

        # 使用LLM提取所有讲者
        print(f"  Session {i+1}: 使用LLM提取讲者...")
        llm_speakers = extract_speakers_with_llm(intro_content)

        if llm_speakers:
            # 将提取的讲者与实际的speaker_id匹配
            # 策略：按介绍顺序和发言频率匹配
            llm_names = list(llm_speakers.values())

            # 按发言量排序的speaker_id
            sorted_speakers = sorted(speaker_counts.items(), key=lambda x: -x[1])

            for idx, (spk_id, count) in enumerate(sorted_speakers):
                if idx < len(llm_names):
                    speaker_map[spk_id] = llm_names[idx]
                    print(f"    {spk_id} -> {llm_names[idx]}")
                else:
                    # 如果LLM提取的数量少于实际speaker，使用ID
                    speaker_map[spk_id] = spk_id
        else:
            # LLM失败，使用备用方案（正则提取多个讲者）
            # 合并所有主持人发言一起提取，避免遗漏
            backup_speakers = extract_all_speakers_from_intro(intro_content)
            if backup_speakers:
                sorted_speakers = sorted(speaker_counts.items(), key=lambda x: -x[1])
                for idx, (spk_id, count) in enumerate(sorted_speakers):
                    if idx < len(backup_speakers):
                        speaker_map[spk_id] = backup_speakers[idx]
                        print(f"    备用: {spk_id} -> {backup_speakers[idx]}")
                    else:
                        speaker_map[spk_id] = spk_id
            else:
                # 多讲者提取失败，尝试逐段提取单讲者
                for j in search_range:
                    seg = segments[j]
                    if host and seg.speaker != host:
                        continue
                    result = extract_speaker_from_intro(seg.content)
                    if result:
                        title, name = result
                        if speaker_counts:
                            main_speaker_id = max(speaker_counts.items(), key=lambda x: x[1])[0]
                            speaker_map[main_speaker_id] = f"{name}{title}"
                            print(f"    备用方案: {main_speaker_id} -> {name}{title}")
                        break

    return speaker_map


def generate_title_with_llm(session: Session) -> str:
    """使用LLM生成session标题"""
    if not LITELLM_AVAILABLE:
        return session.title

    # 从环境变量获取配置
    api_key = os.getenv('LLM_API_KEY')
    api_base = os.getenv('LLM_API_BASE', 'https://api.openai.com/v1')
    model = os.getenv('LLM_MODEL', 'gpt-4o-mini')

    if not api_key:
        print(f"  警告: LLM_API_KEY未设置，使用简单标题")
        return session.title

    # 准备内容摘要 - 优化token成本
    # 策略：取前3个非空段落，每段最多150字符，总计最多400字符
    content_sample = ""
    char_limit_per_seg = 150
    total_char_limit = 400
    seg_count = 0

    for seg in session.segments:
        if seg_count >= 3:
            break
        content = seg.content.strip()
        if not content:
            continue
        # 截取段落内容
        if len(content) > char_limit_per_seg:
            content = content[:char_limit_per_seg] + "..."
        content_sample += content + "\n"
        seg_count += 1

        # 检查总长度
        if len(content_sample) >= total_char_limit:
            content_sample = content_sample[:total_char_limit] + "..."
            break

    # 构建讲者列表
    speaker_list = ", ".join([f"{name}({id})" for id, name in session.all_speakers.items()])

    system_prompt = """你是一个专业的会议内容分析师。请根据会议转写内容，生成一个简洁明了的session标题。

要求：
1. 标题长度不超过20个字
2. 准确概括session的核心主题
3. 不要包含人名，聚焦主题内容
4. 返回纯标题文本，不要有任何解释"""

    user_prompt = f"""请为以下会议内容生成标题：

参与讲者：{speaker_list}
时间范围：{session.start_time} - {session.end_time}
段落数：{len(session.segments)}

内容摘要：
{content_sample}

请生成标题："""

    try:
        response = completion(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=50,
            temperature=0.3,
            api_key=api_key,
            api_base=api_base if 'openai' in model or 'http' in api_base else None
        )

        title = response.choices[0].message.content.strip()
        # 清理标题
        title = title.strip('"').strip("'")
        if len(title) > 30:
            title = title[:30] + "..."
        return title
    except Exception as e:
        print(f"  LLM生成标题失败: {e}")
        return session.title


def extract_title_from_session(session: Session, host: Optional[str]) -> str:
    """从session内容中提取标题"""
    # 跳过开头的主持人和客套话
    start_idx = 0
    for i, seg in enumerate(session.segments[:15]):  # 看前15段
        # 跳过主持人
        if host and seg.speaker == host:
            start_idx = i + 1
            continue
        # 跳过开场客套话和过短内容
        polite_patterns = [r'^感谢', r'^大家好', r'^我是', r'^非常荣幸', r'^好的[，。]?$', r'^嗯+[，。]?$', r'^对[，。]?$', r'^这个[，。]?$']
        is_polite = any(re.search(p, seg.content.strip()) for p in polite_patterns)
        # 跳过太短的内容（少于10个字）
        is_too_short = len(seg.content.strip()) < 10
        if is_polite or is_too_short:
            start_idx = i + 1
        else:
            break

    content_segments = session.segments[start_idx:] if start_idx < len(session.segments) else session.segments

    if not content_segments:
        return "未命名章节"

    # 取前两段内容
    content = ""
    for seg in content_segments[:2]:
        content += seg.content

    # 提取第一句话
    first_sentence = content.split('。')[0].split('？')[0].strip()

    # 清理前缀词
    prefixes = ['接下来', '下面', '首先', '今天', '本次', '我们将', '我会']
    for prefix in prefixes:
        if first_sentence.startswith(prefix):
            first_sentence = first_sentence[len(prefix):].lstrip('，, ')

    if len(first_sentence) > 40:
        first_sentence = first_sentence[:40] + "..."

    return first_sentence if first_sentence else "未命名章节"


def split_into_sessions(segments: List[Segment], use_llm: bool = False) -> List[Session]:
    """将段落分割成多个session"""
    host = identify_host(segments)
    print(f"  识别到主持人: {host}")

    boundaries = detect_session_boundaries(segments, host)

    # 建立讲者姓名映射
    print("  识别讲者姓名...")
    speaker_name_map = build_speaker_name_map(segments, host, boundaries)

    sessions = []
    for i in range(len(boundaries)):
        start_idx = boundaries[i]
        end_idx = boundaries[i + 1] if i + 1 < len(boundaries) else len(segments)

        session_segments = segments[start_idx:end_idx]
        if not session_segments:
            continue

        # 确定主讲人（说话最多且不是主持人的）
        speaker_counts = {}
        for seg in session_segments:
            if seg.speaker != host:
                speaker_counts[seg.speaker] = speaker_counts.get(seg.speaker, 0) + 1

        main_speaker = max(speaker_counts.items(), key=lambda x: x[1])[0] if speaker_counts else "未知"

        # 获取讲者显示名称
        speaker_display_name = speaker_name_map.get(main_speaker, main_speaker)

        # 构建所有参与讲者字典
        all_speakers = {}
        for seg in session_segments:
            spk = seg.speaker
            if spk != host and spk not in all_speakers:
                all_speakers[spk] = speaker_name_map.get(spk, spk)

        # 如果没有找到非主持人讲者（不太可能），至少包含主讲人
        if not all_speakers and main_speaker != "未知":
            all_speakers[main_speaker] = speaker_display_name

        # 提取标题
        title = extract_title_from_session(Session(0, "", "", "", {}, session_segments, "", ""), host)

        start_time = session_segments[0].timestamp
        end_time = session_segments[-1].timestamp

        session = Session(
            index=i + 1,
            title=title,
            speaker=main_speaker,
            speaker_name=speaker_display_name,
            all_speakers=all_speakers,
            segments=session_segments,
            start_time=start_time,
            end_time=end_time
        )

        # 使用LLM优化标题
        if use_llm:
            print(f"  Session {i+1}: 使用LLM生成标题...")
            session.title = generate_title_with_llm(session)

        sessions.append(session)

    return sessions


def generate_session_markdown(session: Session) -> str:
    """生成单个session的markdown内容"""
    # 使用讲者显示名称（如果有）
    speaker_display = session.speaker_name if session.speaker_name != session.speaker else session.speaker

    # 构建所有讲者列表
    speakers_list = []
    for spk_id, spk_name in session.all_speakers.items():
        if spk_name != spk_id:
            speakers_list.append(f"{spk_name} ({spk_id})")
        else:
            speakers_list.append(spk_id)
    speakers_str = ", ".join(speakers_list) if speakers_list else speaker_display

    lines = [
        "---",
        f"title: {session.title}",
        f"session: {session.index}",
        f"speaker: {speaker_display}",
        f"speaker_id: {session.speaker}",
        f"speakers: {speakers_str}",
        f"time_range: {session.start_time} - {session.end_time}",
        "source: 讯飞转写",
        f"generated_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "---",
        "",
        f"# {session.title}",
        "",
        f"> 时间范围：{session.start_time} - {session.end_time}",
    ]

    # 显示讲者信息（单讲者或多讲者）
    if len(session.all_speakers) <= 1:
        lines.append(f"> 主讲人：{speaker_display}")
    else:
        lines.append(f"> 主讲人：{speaker_display}")
        lines.append(f"> 参与讲者：{speakers_str}")

    lines.extend([
        f"> 段落数：{len(session.segments)}",
        "",
        "## 内容纪要",
        "",
    ])

    # 生成摘要
    summary_parts = []
    for seg in session.segments[:5]:
        sentences = seg.content.split('。')
        if sentences and sentences[0].strip():
            summary_parts.append(sentences[0].strip())

    if summary_parts:
        lines.append("**核心要点：**")
        lines.append("")
        for part in summary_parts[:3]:
            lines.append(f"- {part}")
        lines.append("")

    # 详细内容
    lines.append("## 详细内容")
    lines.append("")

    current_speaker = None
    for seg in session.segments:
        # 如果说话人变化，添加说话人标题
        if seg.speaker != current_speaker:
            lines.append(f"\n### {seg.speaker} [{seg.timestamp}]\n")
            current_speaker = seg.speaker

        # 按句子分行便于阅读
        sentences = seg.content.split('。')
        for sent in sentences:
            sent = sent.strip()
            if sent:
                lines.append(f"{sent}。")
        lines.append("")

    return '\n'.join(lines)


def generate_index(sessions: List[Session], source_name: str, recording_info: str) -> str:
    """生成索引文件"""
    total_segments = sum(len(s.segments) for s in sessions)
    total_duration = 0
    for s in sessions:
        start = parse_time_to_seconds(s.start_time)
        end = parse_time_to_seconds(s.end_time)
        total_duration += (end - start)

    lines = [
        "---",
        f"title: {source_name}",
        f"recording_info: {recording_info}",
        f"sessions: {len(sessions)}",
        f"total_segments: {total_segments}",
        f"generated_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "---",
        "",
        f"# {source_name}",
        "",
        f"> 录音信息：{recording_info}",
        "",
        "## 概览",
        "",
        f"- **Session数量**: {len(sessions)}",
        f"- **总段落数**: {total_segments}",
        f"- **总时长**: 约 {total_duration // 60} 分钟",
        "",
        "## Session列表",
        "",
    ]

    for session in sessions:
        duration = parse_time_to_seconds(session.end_time) - parse_time_to_seconds(session.start_time)
        # 使用讲者显示名称
        speaker_display = session.speaker_name if session.speaker_name != session.speaker else session.speaker

        # 构建所有讲者列表（用于多讲者session）
        all_speakers_str = ""
        if len(session.all_speakers) > 1:
            speakers_list = []
            for spk_id, spk_name in session.all_speakers.items():
                if spk_name != spk_id:
                    speakers_list.append(f"{spk_name}")
                else:
                    speakers_list.append(spk_id)
            all_speakers_str = "、".join(speakers_list)

        lines.append(f"### Session {session.index:02d}: {session.title}")
        lines.append("")
        lines.append(f"- **主讲人**: {speaker_display}")
        if all_speakers_str:
            lines.append(f"- **参与讲者**: {all_speakers_str}")
        lines.append(f"- **时间**: {session.start_time} - {session.end_time}")
        lines.append(f"- **时长**: {duration // 60}分{duration % 60}秒")
        lines.append(f"- **段落数**: {len(session.segments)}")
        lines.append(f"- **文件**: [查看详情](./session-{session.index:02d}.md)")
        lines.append("")

        # 要点预览
        key_points = []
        for seg in session.segments[:5]:
            sentences = seg.content.split('。')
            if sentences and sentences[0].strip():
                key_points.append(sentences[0].strip())
                if len(key_points) >= 3:
                    break

        if key_points:
            lines.append("**要点预览：**")
            for point in key_points:
                lines.append(f"- {point}")
            lines.append("")

    return '\n'.join(lines)


def process_transcript(input_path: str, output_dir: str, use_llm: bool = False):
    """处理转写文件"""
    input_path = Path(input_path)
    output_dir = Path(output_dir)

    if not input_path.exists():
        print(f"错误: 文件不存在 {input_path}")
        return False

    # 读取文件
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"正在解析: {input_path.name}")

    # 解析段落
    segments, recording_info = parse_transcript(content)
    print(f"  录音信息: {recording_info}")
    print(f"  共解析 {len(segments)} 个段落")

    if not segments:
        print("  警告: 未找到有效段落")
        return False

    # 分割成sessions
    sessions = split_into_sessions(segments, use_llm)
    print(f"  识别到 {len(sessions)} 个session")

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成source_name（去掉前缀）
    source_name = input_path.stem
    for prefix in ['讯飞转写_', '转写_', '录音转写_']:
        if source_name.startswith(prefix):
            source_name = source_name[len(prefix):]
            break

    # 为每个session生成文件
    for session in sessions:
        md_content = generate_session_markdown(session)
        output_file = output_dir / f"session-{session.index:02d}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"  生成: {output_file.name}")

    # 生成索引文件
    index_content = generate_index(sessions, source_name, recording_info)
    index_file = output_dir / "index.md"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content)
    print(f"  生成: {index_file.name}")

    print(f"\n完成! 输出目录: {output_dir.absolute()}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='语音转写处理器 - 自动解析和结构化会议转写文本'
    )
    parser.add_argument('input', help='输入的转写文本文件路径')
    parser.add_argument('-o', '--output', default='./output',
                        help='输出目录 (默认: ./output)')
    parser.add_argument('--llm', action='store_true',
                        help='使用LLM生成session标题 (需要在.env中配置API密钥)')

    args = parser.parse_args()

    success = process_transcript(args.input, args.output, args.llm)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
