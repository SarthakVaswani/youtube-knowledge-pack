from __future__ import annotations

import json
from pathlib import Path

import pytest

from youtube_knowledge_pack.cli import build_pack_from_inputs, find_downloaded_subtitle
from youtube_knowledge_pack.pipeline import (
    TranscriptSegment,
    build_knowledge_pack,
    clean_text,
    parse_subtitle_events,
)


def test_parse_subtitle_events_creates_timestamped_segments() -> None:
    subtitle_payload = {
        "events": [
            {
                "tStartMs": 0,
                "dDurationMs": 1800,
                "segs": [{"utf8": "Hello "}, {"utf8": "world"}],
            },
            {
                "tStartMs": 2500,
                "dDurationMs": 2100,
                "segs": [{"utf8": "This is "}, {"utf8": "a test"}],
            },
        ]
    }

    segments = parse_subtitle_events(subtitle_payload)

    assert segments == [
        TranscriptSegment(start_ms=0, end_ms=1800, timestamp="00:00", text="Hello world"),
        TranscriptSegment(start_ms=2500, end_ms=4600, timestamp="00:02", text="This is a test"),
    ]


def test_clean_text_removes_noise_and_normalizes_spacing() -> None:
    noisy = "  [Music]\nHello   world\n\nVisit  example.com  "

    assert clean_text(noisy) == "Hello world Visit example.com"


def test_build_knowledge_pack_writes_expected_artifacts(tmp_path: Path) -> None:
    segments = [
        TranscriptSegment(start_ms=0, end_ms=1800, timestamp="00:00", text="Intro to retrieval augmented generation."),
        TranscriptSegment(start_ms=2500, end_ms=4600, timestamp="00:02", text="Chunk transcripts and store them for search."),
        TranscriptSegment(start_ms=5000, end_ms=7200, timestamp="00:05", text="Use summaries, concepts, and actions for agent memory."),
    ]

    result = build_knowledge_pack(
        video_id="abc123",
        url="https://www.youtube.com/watch?v=abc123",
        title="RAG from videos",
        author="Demo Author",
        segments=segments,
        output_dir=tmp_path,
        chunk_size=2,
    )

    transcript = (result.output_dir / "transcript.md").read_text()
    summary = (result.output_dir / "summary.md").read_text()
    chunks = json.loads((result.output_dir / "chunks.json").read_text())
    metadata = json.loads((result.output_dir / "metadata.json").read_text())

    assert result.output_dir == tmp_path / "abc123-rag-from-videos"
    assert "# RAG from videos" in transcript
    assert "- [00:00] Intro to retrieval augmented generation." in transcript
    assert "## Core ideas" in summary
    assert "retrieval augmented generation" in summary.lower()
    assert len(chunks) == 2
    assert chunks[0]["text"].startswith("Intro to retrieval augmented generation.")
    assert metadata["source"]["video_id"] == "abc123"
    assert metadata["artifact_paths"]["summary"] == "summary.md"


def test_build_pack_from_inputs_uses_fixture_inputs_without_network(tmp_path: Path) -> None:
    subtitle_json = tmp_path / "captions.json"
    subtitle_json.write_text(
        json.dumps(
            {
                "events": [
                    {"tStartMs": 0, "dDurationMs": 1000, "segs": [{"utf8": "Learn from transcripts."}]},
                    {"tStartMs": 1200, "dDurationMs": 1000, "segs": [{"utf8": "Create notes and chunks."}]},
                ]
            }
        )
    )

    output_dir = build_pack_from_inputs(
        url="https://www.youtube.com/watch?v=xyz987",
        output_root=tmp_path,
        subtitle_json_path=subtitle_json,
        title="Agent memory video",
        author="Fixture Author",
    )

    assert output_dir.exists()
    assert (output_dir / "summary.md").exists()
    assert "agent-memory-video" in output_dir.name


def test_find_downloaded_subtitle_falls_back_to_globbed_json3_file(tmp_path: Path) -> None:
    subtitle_file = tmp_path / "xyz987.en-orig.json3"
    subtitle_file.write_text("{}")

    found = find_downloaded_subtitle({"id": "xyz987"}, tmp_path)

    assert found == subtitle_file
