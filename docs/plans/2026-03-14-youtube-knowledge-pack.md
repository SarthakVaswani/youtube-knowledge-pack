# YouTube Knowledge Pack Pipeline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a standalone CLI that takes a YouTube URL and produces an agent-friendly knowledge pack containing transcript, cleaned notes, chunks, and metadata.

**Architecture:** Use a small Python package with a command-line entry point. The pipeline will call `yt-dlp` to fetch video metadata and transcript subtitles, normalize the transcript into timestamped segments, derive a concise structured summary locally, and write a reusable knowledge pack to disk.

**Tech Stack:** Python 3.13, `pytest`, standard library, external `yt-dlp` CLI

---

### Task 1: Scaffold project and failing tests

**Files:**
- Create: `pyproject.toml`
- Create: `tests/test_pipeline.py`
- Create: `src/youtube_knowledge_pack/__init__.py`

**Step 1: Write the failing tests**

Add tests for:
- parsing subtitle JSON into transcript segments
- cleaning transcript text
- generating chunk files and summary artifacts

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest -q`
Expected: FAIL because the package and functions do not exist yet.

**Step 3: Write minimal implementation stubs**

Create package structure and exported function names only.

**Step 4: Run test to verify failure changes**

Run: `python3 -m pytest -q`
Expected: FAIL with missing behavior rather than import errors.

### Task 2: Implement transcript parsing and pack generation

**Files:**
- Create: `src/youtube_knowledge_pack/pipeline.py`
- Modify: `tests/test_pipeline.py`

**Step 1: Write the failing test**

Add concrete expectations around transcript parsing, summary generation, and chunk indexing.

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_pipeline.py -q`
Expected: FAIL on output mismatch.

**Step 3: Write minimal implementation**

Implement:
- subtitle event parsing
- timestamp formatting
- transcript cleaning
- chunk generation
- markdown/json artifact writing

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_pipeline.py -q`
Expected: PASS

### Task 3: Implement CLI workflow

**Files:**
- Create: `src/youtube_knowledge_pack/cli.py`
- Modify: `pyproject.toml`
- Modify: `tests/test_pipeline.py`

**Step 1: Write the failing test**

Add CLI-level test that exercises pack generation from fixture metadata and subtitle inputs without network access.

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_pipeline.py -q`
Expected: FAIL because CLI workflow is not implemented.

**Step 3: Write minimal implementation**

Implement a CLI with:
- `build` command
- `--url`, `--output-dir`, `--title`, `--author`, and fixture-based `--subtitle-json`
- optional `yt-dlp` integration for live URLs

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_pipeline.py -q`
Expected: PASS

### Task 4: Add usage docs and final verification

**Files:**
- Create: `README.md`

**Step 1: Write docs**

Document installation, required `yt-dlp`, output folder structure, and example commands.

**Step 2: Run full verification**

Run: `python3 -m pytest -q`
Expected: PASS

Run: `python3 -m youtube_knowledge_pack.cli build --help`
Expected: CLI usage output
