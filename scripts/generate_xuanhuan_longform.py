from __future__ import annotations

import argparse
import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read_env_value(name: str) -> str:
    direct = os.getenv(name, "").strip()
    if direct:
        return direct
    for file_name in (".env.local", ".env"):
        p = REPO_ROOT / file_name
        if not p.exists():
            continue
        for raw in p.read_text(encoding="utf-8-sig").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == name:
                return value.strip().strip('"').strip("'")
    return ""


def _resolve_chat_endpoint(base_url: str) -> str:
    base = base_url.strip().rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    return f"{base}/chat/completions"


def _compact_len(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def _strip_reasoning_artifacts(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = text.replace("```markdown", "").replace("```md", "").replace("```text", "").replace("```", "")
    return text.strip()


def _extract_text_from_response(resp: dict[str, Any]) -> str:
    choices = resp.get("choices")
    if isinstance(choices, list) and choices:
        msg = choices[0].get("message") if isinstance(choices[0], dict) else None
        if isinstance(msg, dict):
            content = msg.get("content")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                chunks: list[str] = []
                for item in content:
                    if isinstance(item, dict):
                        t = item.get("text")
                        if isinstance(t, str):
                            chunks.append(t)
                if chunks:
                    return "\n".join(chunks)
    raise ValueError("unable-to-extract-model-text")


@dataclass
class Chapter:
    index: int
    title: str
    body: str
    summary: str
    hook: str
    chars: int


class ChatClient:
    def __init__(self, *, endpoint: str, api_key: str, model: str, timeout_seconds: float) -> None:
        self.endpoint = endpoint
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = max(10.0, timeout_seconds)

    def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float,
        max_attempts: int = 3,
    ) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": int(max_tokens),
            "temperature": float(temperature),
        }
        last_error: Exception | None = None
        for i in range(1, max(1, max_attempts) + 1):
            try:
                body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                req = Request(
                    self.endpoint,
                    data=body,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "Authorization": f"Bearer {self.api_key}",
                    },
                    method="POST",
                )
                with urlopen(req, timeout=self.timeout_seconds) as r:
                    raw = r.read().decode("utf-8")
                parsed = json.loads(raw)
                return _strip_reasoning_artifacts(_extract_text_from_response(parsed))
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if i >= max_attempts:
                    break
                time.sleep(min(2.0 * i, 5.0))
        raise RuntimeError(f"chat-completions-generation-failed: {last_error}") from last_error


def _default_outline() -> dict[str, Any]:
    return {
        "title": "《玄渊天命》",
        "premise": "边陲少年顾长渊意外觉醒古印，被卷入宗门、王庭与上古遗族的生死棋局。",
        "style_rules": [
            "每章必须推进冲突",
            "每章结尾有钩子",
            "战斗与情绪并重",
            "伏笔与回收闭环",
        ],
        "factions": ["天衡宗", "夜烬王庭", "万机阁", "荒古遗族"],
        "characters": [
            {"name": "顾长渊", "role": "主角", "goal": "打破天命枷锁"},
            {"name": "苏晚照", "role": "盟友", "goal": "守住宗门底线"},
            {"name": "宁玄策", "role": "智谋对手", "goal": "重塑秩序"},
        ],
        "arc_beats": [
            {"phase": "起势", "objective": "主角入局立敌"},
            {"phase": "扩张", "objective": "结盟夺势建立反制"},
            {"phase": "崩塌", "objective": "主角阵营遭重创"},
            {"phase": "反攻", "objective": "重组战线反向围猎"},
            {"phase": "登临", "objective": "终局决战改写天命"},
        ],
    }


def _parse_json_object(text: str) -> dict[str, Any]:
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*", "", t, flags=re.IGNORECASE)
        t = re.sub(r"\s*```$", "", t)
    try:
        obj = json.loads(t)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    m = re.search(r"\{.*\}", t, flags=re.DOTALL)
    if not m:
        raise ValueError("json-object-not-found")
    obj = json.loads(m.group(0))
    if not isinstance(obj, dict):
        raise ValueError("json-object-not-dict")
    return obj


def _build_outline(client: ChatClient, *, chapter_budget: int) -> dict[str, Any]:
    prompt = (
        "你是中文玄幻长篇总策划。输出严格JSON，不要解释。\n"
        f"目标连载长度约10万字，预计章节数{chapter_budget}。\n"
        "返回字段:\n"
        "{\n"
        '  "title":"",\n'
        '  "premise":"",\n'
        '  "style_rules":["","","",""],\n'
        '  "factions":["",""],\n'
        '  "characters":[{"name":"","role":"","goal":""}],\n'
        '  "arc_beats":[{"phase":"起势/扩张/崩塌/反攻/登临","objective":""}]\n'
        "}"
    )
    try:
        raw = client.generate(
            system_prompt="你是小说策划助手，只输出合法JSON。",
            user_prompt=prompt,
            max_tokens=900,
            temperature=0.6,
            max_attempts=2,
        )
        return _parse_json_object(raw)
    except Exception:
        return _default_outline()


def _render_outline(outline: dict[str, Any]) -> str:
    title = str(outline.get("title", "未命名"))
    premise = str(outline.get("premise", ""))
    rules = outline.get("style_rules", [])
    factions = outline.get("factions", [])
    chars = outline.get("characters", [])
    beats = outline.get("arc_beats", [])

    lines = [f"书名:{title}", f"设定:{premise}"]
    if isinstance(rules, list):
        lines.append("文风规则:" + "；".join(str(x) for x in rules[:5]))
    if isinstance(factions, list):
        lines.append("势力:" + "、".join(str(x) for x in factions[:6]))
    if isinstance(chars, list):
        c = []
        for item in chars[:8]:
            if isinstance(item, dict):
                c.append(f"{item.get('name','角色')}({item.get('role','定位')})")
        if c:
            lines.append("角色:" + "、".join(c))
    if isinstance(beats, list):
        b = []
        for i, item in enumerate(beats[:8], start=1):
            if isinstance(item, dict):
                b.append(f"{i}.{item.get('phase','')}-{item.get('objective','')}")
        if b:
            lines.append("阶段:" + " | ".join(b))
    return "\n".join(lines)


def _pick_phase(outline: dict[str, Any], chapter_index: int, max_chapters: int) -> str:
    beats = outline.get("arc_beats", [])
    if not isinstance(beats, list) or not beats:
        return "推进主线并制造新冲突"
    pos = min(chapter_index / max(max_chapters, 1), 0.9999)
    idx = min(int(pos * len(beats)), len(beats) - 1)
    beat = beats[idx]
    if not isinstance(beat, dict):
        return "推进主线并制造新冲突"
    return f"{beat.get('phase','阶段')}:{beat.get('objective','推进主线')}"


def _parse_chapter(raw: str, chapter_index: int) -> Chapter:
    title = ""
    body = ""
    summary = ""
    hook = ""

    m_title = re.search(r"\[TITLE\]\s*(.+)", raw)
    if m_title:
        title = m_title.group(1).strip()
    m_body = re.search(r"\[BODY\]\s*(.+?)(?:\[SUMMARY\]|$)", raw, flags=re.DOTALL)
    if m_body:
        body = m_body.group(1).strip()
    m_summary = re.search(r"\[SUMMARY\]\s*(.+?)(?:\[HOOK\]|$)", raw, flags=re.DOTALL)
    if m_summary:
        summary = m_summary.group(1).strip()
    m_hook = re.search(r"\[HOOK\]\s*(.+)$", raw, flags=re.DOTALL)
    if m_hook:
        hook = m_hook.group(1).strip()

    if not title:
        title = f"第{chapter_index}章"
    if not body:
        body = raw.strip()
    if not summary:
        summary = re.sub(r"\s+", " ", body)[:180]
    if not hook:
        hook = "风暴将至，新的对手已现身。"

    return Chapter(
        index=chapter_index,
        title=title,
        body=body,
        summary=summary,
        hook=hook,
        chars=_compact_len(body),
    )


def _generate_chapter(
    client: ChatClient,
    *,
    outline: dict[str, Any],
    chapter_index: int,
    chapter_target_chars: int,
    max_chapters: int,
    recent_summaries: list[str],
) -> Chapter:
    outline_text = _render_outline(outline)
    phase = _pick_phase(outline, chapter_index, max_chapters)
    history = "\n".join(f"- {x}" for x in recent_summaries[-8:]) if recent_summaries else "- (none)"

    user_prompt = (
        f"Write chapter {chapter_index} in Chinese xuanhuan style.\n"
        f"Target body length around {chapter_target_chars} Chinese characters.\n"
        "No chain-of-thought. No explanation.\n"
        "Output exact format:\n"
        "[TITLE]\n...\n"
        "[BODY]\n...\n"
        "[SUMMARY]\n...\n"
        "[HOOK]\n...\n\n"
        f"Outline:\n{outline_text}\n\n"
        f"Current phase:\n{phase}\n\n"
        f"Recent summaries:\n{history}\n"
    )

    raw = client.generate(
        system_prompt="You are a top Chinese fantasy novelist. Follow the requested output format exactly.",
        user_prompt=user_prompt,
        max_tokens=min(1500, max(900, int(chapter_target_chars * 1.15))),
        temperature=0.85,
        max_attempts=3,
    )
    chapter = _parse_chapter(raw, chapter_index)
    if chapter.chars >= int(chapter_target_chars * 0.72):
        return chapter

    expand_prompt = (
        f"Rewrite chapter {chapter_index} with longer body ({chapter_target_chars}+ chars). "
        "Keep continuity and output same format [TITLE]/[BODY]/[SUMMARY]/[HOOK].\n"
        f"Current draft:\n{raw[:2600]}"
    )
    raw2 = client.generate(
        system_prompt="You are a Chinese fantasy novelist.",
        user_prompt=expand_prompt,
        max_tokens=min(1700, max(1000, int(chapter_target_chars * 1.25))),
        temperature=0.82,
        max_attempts=2,
    )
    chapter2 = _parse_chapter(raw2, chapter_index)
    return chapter2 if chapter2.chars > chapter.chars else chapter


def _fallback_chapter(chapter_index: int, reason: str) -> Chapter:
    body = (
        "顾长渊在风雪夜中踏入新的战场，旧敌与新局同时逼近。"
        "他以残存灵力强行破阵，救下同伴，却也暴露命核异动。"
        "天衡宗与夜烬王庭的暗线同时收网，主角被迫提前进入下一轮死战。"
        f"（自动保底段落，原因：{reason}）"
    ) * 10
    return Chapter(
        index=chapter_index,
        title=f"第{chapter_index}章 临时续写",
        body=body,
        summary="主角在围猎中突围，局势升级，新的危机迫近。",
        hook="天幕裂开，新的裁决降临。",
        chars=_compact_len(body),
    )


def run(
    *,
    output_dir: Path,
    target_chars: int,
    chapter_target_chars: int,
    max_chapters: int,
    request_timeout_seconds: float,
    sleep_seconds: float,
    resume: bool,
) -> None:
    base_url = _read_env_value("BENCHMARK_BASE_URL")
    model = _read_env_value("BENCHMARK_MODEL")
    api_key = _read_env_value("BENCHMARK_API_KEY")
    if not base_url or not model or not api_key:
        raise RuntimeError("missing BENCHMARK_BASE_URL/BENCHMARK_MODEL/BENCHMARK_API_KEY")

    endpoint = _resolve_chat_endpoint(base_url)
    client = ChatClient(endpoint=endpoint, api_key=api_key, model=model, timeout_seconds=request_timeout_seconds)

    output_dir.mkdir(parents=True, exist_ok=True)
    outline_path = output_dir / "outline.json"
    novel_path = output_dir / "novel.md"
    progress_path = output_dir / "progress.jsonl"
    report_path = output_dir / "report.md"

    outline: dict[str, Any]
    rows: list[dict[str, Any]] = []
    recent_summaries: list[str] = []
    total_chars = 0
    chapter_start = 1

    if resume and outline_path.exists() and novel_path.exists() and progress_path.exists():
        outline = json.loads(outline_path.read_text(encoding="utf-8-sig"))
        for raw in progress_path.read_text(encoding="utf-8-sig").splitlines():
            line = raw.strip()
            if not line:
                continue
            row = json.loads(line)
            if isinstance(row, dict):
                rows.append(row)
        if rows:
            total_chars = int(rows[-1].get("cumulative_chars", 0))
            chapter_start = int(rows[-1].get("chapter", 0)) + 1
            for row in rows[-20:]:
                summary = str(row.get("summary", "")).strip()
                if summary:
                    recent_summaries.append(f"第{row.get('chapter')}章:{summary[:180]}")
    else:
        outline = _build_outline(client, chapter_budget=max_chapters)
        outline_path.write_text(json.dumps(outline, ensure_ascii=False, indent=2), encoding="utf-8")
        title = str(outline.get("title", "未命名玄幻长篇"))
        novel_path.write_text(
            f"# {title}\n\n> generated_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n",
            encoding="utf-8",
        )
        if progress_path.exists():
            progress_path.unlink()

    started = time.perf_counter()

    for chapter_idx in range(chapter_start, max_chapters + 1):
        chapter: Chapter | None = None
        chapter_started = time.perf_counter()
        last_error = ""
        for attempt in range(1, 4):
            try:
                chapter = _generate_chapter(
                    client,
                    outline=outline,
                    chapter_index=chapter_idx,
                    chapter_target_chars=chapter_target_chars,
                    max_chapters=max_chapters,
                    recent_summaries=recent_summaries,
                )
                break
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
                print(f"[warn] chapter={chapter_idx} attempt={attempt} failed: {exc}")
                time.sleep(1.5 * attempt)

        if chapter is None:
            chapter = _fallback_chapter(chapter_idx, last_error)

        elapsed = round(time.perf_counter() - chapter_started, 2)
        total_chars += chapter.chars

        chunk = (
            f"## 第{chapter_idx}章 {chapter.title}\n\n"
            f"{chapter.body}\n\n"
            f"### 本章摘要\n{chapter.summary}\n\n"
            f"### 连载钩子\n{chapter.hook}\n\n"
            "---\n\n"
        )
        with novel_path.open("a", encoding="utf-8") as f:
            f.write(chunk)

        recent_summaries.append(f"第{chapter_idx}章:{chapter.summary[:180]}")
        if len(recent_summaries) > 20:
            recent_summaries = recent_summaries[-20:]

        row = {
            "chapter": chapter_idx,
            "title": chapter.title,
            "chars": chapter.chars,
            "summary": chapter.summary,
            "elapsed_seconds": elapsed,
            "cumulative_chars": total_chars,
        }
        rows.append(row)
        with progress_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

        print(f"[chapter {chapter_idx}] chars={chapter.chars} cumulative={total_chars}/{target_chars} elapsed={elapsed}s")

        if total_chars >= target_chars:
            break
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

    total_elapsed = round(time.perf_counter() - started, 2)
    title = str(outline.get("title", "未命名玄幻长篇"))
    done_chapters = len(rows)
    avg_chars = int(total_chars / done_chapters) if done_chapters else 0

    report_lines = [
        "# 玄幻长篇生成报告",
        "",
        f"- 书名: {title}",
        f"- 模型: {model}",
        f"- Endpoint: {endpoint}",
        f"- 目标字数: {target_chars}",
        f"- 实际字数: {total_chars}",
        f"- 章节数: {done_chapters}",
        f"- 单章均字数: {avg_chars}",
        f"- 本轮耗时(秒): {total_elapsed}",
        "",
        "## 章节统计",
        "",
        "| 章 | 标题 | 字数 | 累计字数 | 耗时(秒) |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in rows:
        report_lines.append(
            f"| {row['chapter']} | {row['title']} | {row['chars']} | "
            f"{row['cumulative_chars']} | {row['elapsed_seconds']} |"
        )
    report_lines.append("")
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"[done] novel={novel_path}")
    print(f"[done] report={report_path}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Generate a 100k-class xuanhuan novel via chat/completions.")
    p.add_argument("--target-chars", type=int, default=100_000)
    p.add_argument("--chapter-target-chars", type=int, default=1500)
    p.add_argument("--max-chapters", type=int, default=90)
    p.add_argument("--request-timeout-seconds", type=float, default=95.0)
    p.add_argument("--sleep-seconds", type=float, default=0.12)
    p.add_argument("--output-dir", type=Path, default=None)
    p.add_argument("--resume", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    out_dir = args.output_dir or (
        REPO_ROOT / "artifacts" / "testing" / "novel_generation" / f"xuanhuan_m25_{datetime.now().strftime('%Y%m%dT%H%M%S')}"
    )
    try:
        run(
            output_dir=out_dir,
            target_chars=max(1000, int(args.target_chars)),
            chapter_target_chars=max(1000, int(args.chapter_target_chars)),
            max_chapters=max(1, int(args.max_chapters)),
            request_timeout_seconds=max(10.0, float(args.request_timeout_seconds)),
            sleep_seconds=max(0.0, float(args.sleep_seconds)),
            resume=bool(args.resume),
        )
        return 0
    except (HTTPError, URLError, TimeoutError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"[error] {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
