# YouTube Knowledge Pack

Turn a YouTube video into an agent-ready knowledge pack.

Given a YouTube URL, this tool pulls subtitles and builds a reusable folder with:

- `transcript.md`: cleaned transcript with timestamps
- `summary.md`: concise notes for fast context loading
- `chunks.json`: retrieval-friendly transcript chunks
- `metadata.json`: source and artifact metadata

This is useful when you want a coding agent or RAG workflow to use video content as structured context instead of treating it like an opaque link.

## Requirements

- Python 3.11+
- `yt-dlp` installed and available on your `PATH`

Install `yt-dlp` if needed:

```bash
python3 -m pip install yt-dlp
```

## Installation

### Option 1: Clone and install locally

```bash
git clone https://github.com/YOUR_USERNAME/youtube-knowledge-pack.git
cd youtube-knowledge-pack
python3 -m pip install -e .
```

### Option 2: Use without installing globally

```bash
git clone https://github.com/YOUR_USERNAME/youtube-knowledge-pack.git
cd youtube-knowledge-pack
```

Then run commands with:

```bash
PYTHONPATH=src python3 -m youtube_knowledge_pack.cli --help
```

## Quick Start

Build a knowledge pack from a live YouTube URL:

```bash
youtube-knowledge-pack build \
  --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

By default, packs are written to:

```bash
~/knowledge-packs/
```

## Using an Existing Subtitle File

If you already have a subtitle JSON3 file:

```bash
youtube-knowledge-pack build \
  --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --subtitle-json /absolute/path/to/captions.json3 \
  --title "Example title" \
  --author "Example author"
```

## Output Structure

Each run creates a folder like:

```text
~/knowledge-packs/<video-id>-<slug>/
```

Example contents:

```text
transcript.md
summary.md
chunks.json
metadata.json
```

## Suggested Workflow

1. Build the knowledge pack once per video.
2. Point your agent at `summary.md` for quick context.
3. Use `chunks.json` or `transcript.md` when you want retrieval by topic or timestamp.
4. Store the generated folder inside a shared `knowledge/` or `sources/` directory if multiple projects or agents will reuse it.

## Notes

- This currently relies on available YouTube subtitles or auto-generated captions.
- If subtitles are not available for a video, the build will fail.
- The default summary is heuristic and local; you can extend it later with an LLM pass.

## CLI

```bash
youtube-knowledge-pack build --help
```

If you did not install it globally:

```bash
PYTHONPATH=src python3 -m youtube_knowledge_pack.cli build --help
```
