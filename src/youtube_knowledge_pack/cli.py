from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from youtube_knowledge_pack.pipeline import build_knowledge_pack, parse_subtitle_events

DEFAULT_OUTPUT_DIR = Path.home() / "knowledge-packs"


def infer_video_id(url: str) -> str:
    parsed = urlparse(url)
    if parsed.hostname in {"youtu.be"}:
        return parsed.path.strip("/") or "video"
    query_video_id = parse_qs(parsed.query).get("v", [""])[0]
    return query_video_id or parsed.path.strip("/").split("/")[-1] or "video"


def run_yt_dlp_json(url: str, output_root: Path) -> dict:
    command = [
        "yt-dlp",
        "--skip-download",
        "--dump-single-json",
        url,
    ]
    completed = subprocess.run(command, cwd=output_root, capture_output=True, text=True, check=True)
    return json.loads(completed.stdout)


def download_subtitles(url: str, output_root: Path) -> None:
    command = [
        "yt-dlp",
        "--skip-download",
        "--write-auto-sub",
        "--sub-langs",
        "en.*",
        "--sub-format",
        "json3",
        "--output",
        "%(id)s.%(ext)s",
        url,
    ]
    subprocess.run(command, cwd=output_root, capture_output=True, text=True, check=True)


def find_downloaded_subtitle(info: dict, output_root: Path) -> Path:
    requested = info.get("requested_subtitles") or info.get("automatic_captions") or {}
    subtitle_info = None
    for key in requested:
        subtitle_info = requested[key]
        if subtitle_info:
            break
    if isinstance(subtitle_info, dict):
        filepath = subtitle_info.get("filepath")
        if filepath:
            return Path(filepath)

    video_id = info.get("id", "video")
    candidates = sorted(output_root.glob(f"{video_id}*.json3"))
    if not candidates:
        raise FileNotFoundError("yt-dlp did not produce a subtitle JSON3 file.")
    return candidates[0]


def build_pack_from_inputs(
    *,
    url: str,
    output_root: Path,
    subtitle_json_path: Path,
    title: str | None = None,
    author: str | None = None,
) -> Path:
    payload = json.loads(subtitle_json_path.read_text())
    segments = parse_subtitle_events(payload)
    if not segments:
        raise ValueError("No transcript segments were found in the subtitle JSON.")

    result = build_knowledge_pack(
        video_id=infer_video_id(url),
        url=url,
        title=title or infer_video_id(url),
        author=author or "Unknown author",
        segments=segments,
        output_dir=output_root,
    )
    return result.output_dir


def build_pack_from_url(
    *,
    url: str,
    output_root: Path,
    title: str | None = None,
    author: str | None = None,
) -> Path:
    info = run_yt_dlp_json(url, output_root)
    download_subtitles(url, output_root)
    subtitle_json_path = find_downloaded_subtitle(info, output_root)
    return build_pack_from_inputs(
        url=url,
        output_root=output_root,
        subtitle_json_path=subtitle_json_path,
        title=title or info.get("title"),
        author=author or info.get("channel") or info.get("uploader"),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build an agent knowledge pack from a YouTube video.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Build a knowledge pack")
    build_parser.add_argument("--url", required=True, help="YouTube URL")
    build_parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for generated packs",
    )
    build_parser.add_argument("--subtitle-json", help="Existing subtitle JSON3 file to use instead of yt-dlp")
    build_parser.add_argument("--title", help="Override title")
    build_parser.add_argument("--author", help="Override author")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    output_root = Path(args.output_dir).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    if args.command == "build":
        if args.subtitle_json:
            output_dir = build_pack_from_inputs(
                url=args.url,
                output_root=output_root,
                subtitle_json_path=Path(args.subtitle_json).resolve(),
                title=args.title,
                author=args.author,
            )
        else:
            output_dir = build_pack_from_url(
                url=args.url,
                output_root=output_root,
                title=args.title,
                author=args.author,
            )
        print(output_dir)


if __name__ == "__main__":
    main()
