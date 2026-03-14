from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from textwrap import shorten


NOISE_PATTERNS = (
    re.compile(r"\[(?:music|applause|laughter|__+)\]", re.IGNORECASE),
    re.compile(r"\((?:music|applause|laughter)\)", re.IGNORECASE),
)


@dataclass(eq=True)
class TranscriptSegment:
    start_ms: int
    end_ms: int
    timestamp: str
    text: str


@dataclass
class BuildResult:
    output_dir: Path


def clean_text(text: str) -> str:
    cleaned = text.replace("\n", " ")
    for pattern in NOISE_PATTERNS:
        cleaned = pattern.sub(" ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def format_timestamp(milliseconds: int) -> str:
    total_seconds = max(0, milliseconds // 1000)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def parse_subtitle_events(payload: dict) -> list[TranscriptSegment]:
    segments: list[TranscriptSegment] = []
    for event in payload.get("events", []):
        segs = event.get("segs") or []
        if not segs:
            continue
        text = clean_text("".join(seg.get("utf8", "") for seg in segs))
        if not text:
            continue
        start_ms = int(event.get("tStartMs", 0))
        duration_ms = int(event.get("dDurationMs", 0))
        segments.append(
            TranscriptSegment(
                start_ms=start_ms,
                end_ms=start_ms + duration_ms,
                timestamp=format_timestamp(start_ms),
                text=text,
            )
        )
    return segments


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "video"


def chunk_segments(segments: list[TranscriptSegment], chunk_size: int) -> list[dict[str, object]]:
    chunks: list[dict[str, object]] = []
    for index in range(0, len(segments), chunk_size):
        batch = segments[index : index + chunk_size]
        chunks.append(
            {
                "chunk_id": len(chunks) + 1,
                "start_timestamp": batch[0].timestamp,
                "end_timestamp": batch[-1].timestamp,
                "text": " ".join(segment.text for segment in batch),
                "segments": [
                    {
                        "timestamp": segment.timestamp,
                        "text": segment.text,
                    }
                    for segment in batch
                ],
            }
        )
    return chunks


def summarize_segments(segments: list[TranscriptSegment], chunks: list[dict[str, object]]) -> str:
    key_lines = [segment.text for segment in segments[:5]]
    concept_lines = []
    for line in key_lines:
        sentence = shorten(line, width=90, placeholder="...")
        if sentence not in concept_lines:
            concept_lines.append(sentence)

    action_lines = []
    lower_text = " ".join(segment.text.lower() for segment in segments)
    if "chunk" in lower_text:
        action_lines.append("Chunk the transcript into topic-sized passages for retrieval.")
    if "summary" in lower_text or "summaries" in lower_text:
        action_lines.append("Store a concise summary beside the raw transcript for quick context loading.")
    if "search" in lower_text or "retrieval" in lower_text:
        action_lines.append("Index the chunks so the agent can pull only relevant moments at answer time.")
    if not action_lines:
        action_lines.append("Review the transcript chunks and promote important ideas into reusable notes.")

    overview = shorten(" ".join(segment.text for segment in segments[:3]), width=220, placeholder="...")
    chunk_count = len(chunks)

    lines = [
        "## Overview",
        overview,
        "",
        "## Core ideas",
        *[f"- {line}" for line in concept_lines],
        "",
        "## Suggested agent workflow",
        *[f"- {line}" for line in action_lines],
        "",
        "## Retrieval notes",
        f"- Generated {chunk_count} transcript chunks for downstream search.",
        "- Use the timestamps in `transcript.md` to jump back to the original moment in the video.",
    ]
    return "\n".join(lines).strip() + "\n"


def build_knowledge_pack(
    *,
    video_id: str,
    url: str,
    title: str,
    author: str,
    segments: list[TranscriptSegment],
    output_dir: Path,
    chunk_size: int = 8,
) -> BuildResult:
    pack_dir = output_dir / f"{video_id}-{slugify(title)}"
    pack_dir.mkdir(parents=True, exist_ok=True)

    chunks = chunk_segments(segments, chunk_size=max(1, chunk_size))
    transcript_lines = [
        f"# {title}",
        "",
        f"- URL: {url}",
        f"- Author: {author}",
        f"- Segments: {len(segments)}",
        "",
        "## Transcript",
        *[f"- [{segment.timestamp}] {segment.text}" for segment in segments],
        "",
    ]
    transcript_content = "\n".join(transcript_lines)
    summary_content = summarize_segments(segments, chunks)

    metadata = {
        "source": {
            "video_id": video_id,
            "url": url,
            "title": title,
            "author": author,
        },
        "counts": {
            "segments": len(segments),
            "chunks": len(chunks),
        },
        "artifact_paths": {
            "transcript": "transcript.md",
            "summary": "summary.md",
            "chunks": "chunks.json",
        },
    }

    (pack_dir / "transcript.md").write_text(transcript_content)
    (pack_dir / "summary.md").write_text(summary_content)
    (pack_dir / "chunks.json").write_text(json.dumps(chunks, indent=2))
    (pack_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    return BuildResult(output_dir=pack_dir)
