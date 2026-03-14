# YouTube Knowledge Pack

Build an agent-friendly knowledge pack from a YouTube video URL.

## What it produces

Each run creates a folder in `~/knowledge-packs/` by default containing:

- `transcript.md`: cleaned transcript with timestamps
- `summary.md`: concise notes and retrieval guidance
- `chunks.json`: transcript grouped into retrieval-ready chunks
- `metadata.json`: source metadata and artifact paths

## Requirements

- Python 3.11+
- `yt-dlp` installed and available on your `PATH`

Install `yt-dlp` if needed:

```bash
python3 -m pip install yt-dlp
```

## Run it

Using a live YouTube URL:

```bash
PYTHONPATH=src python3 -m youtube_knowledge_pack.cli build \
  --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --output-dir ~/knowledge-packs
```

Using an already-downloaded subtitle JSON file:

```bash
PYTHONPATH=src python3 -m youtube_knowledge_pack.cli build \
  --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --subtitle-json /absolute/path/to/captions.json3 \
  --title "Example title" \
  --author "Example author"
```

## Suggested agent workflow

1. Build the knowledge pack once for each video.
2. Point your coding agent at `summary.md` for quick context.
3. Use `chunks.json` or `transcript.md` when you want retrieval by topic or timestamp.
4. Keep the generated folder in a shared `knowledge/` or `sources/` directory so future sessions can reuse it.

## Install globally

To make the command available from any folder:

```bash
python3 -m pip install -e /Users/sarthakvaswani/ideas-exploration
```

Then run:

```bash
youtube-knowledge-pack build --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```
