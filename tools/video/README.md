# Topic videos

Turns a handbook chapter into a narrated 1080p slide video (MP4) plus timed subtitles (SRT).
Slides use the site's dark theme; narration is generated offline with the
[Kokoro](https://github.com/thewh1teagle/kokoro-onnx) text-to-speech model, so there are no API keys or per-minute costs.

| Topic module | Chapter | Length |
|---|---|---|
| `topics/ch06.py` | Ch 06 · Lambdas & Functional Interfaces | 10:03 |

## Setup (once)

Needs Python 3.10+, Node 18+, `ffmpeg` and ~400 MB of disk for the voice model.

```bash
tools/video/setup.sh
```

## Build a video

```bash
tools/video/make.sh ch06
```

Output: `tools/video/out/ch06.mp4` and `ch06.srt` (both git-ignored; upload them to YouTube and link from the chapter page).
A 10-minute video takes about 4–5 minutes to build.

Options: `--voice af_heart` (any Kokoro voice, default `am_michael`), `--speed 1.1`,
`--frames-only` (render slide images only, no audio — fast layout check).

## How it works

1. **`topics/<topic>.py`** — the content. A list of `SLIDES`, each with a title, kicker, HTML body and a list of
   `narration` strings. Narration string *n* plays while step *n* is on screen; elements marked with
   `data-step="n"` (via the helpers in `kit.py`) appear at that step, so points reveal as they are spoken.
2. **`build.py`** — writes one HTML page per step and calls `render.js` (Playwright/Chromium) to screenshot it at
   1920×1080. **The build stops if any slide's content overflows the frame**, naming the slide.
3. Each narration string is voiced with Kokoro and laid end to end with short pauses; the image timeline is
   derived from the same durations, so slides stay in sync with the voice. Subtitles come from the same timings.
4. `ffmpeg` encodes H.264 + AAC with `+faststart` for web playback.

## Adding a chapter

Copy `topics/ch06.py` to `topics/chNN.py` and rewrite `CHAPTER`, `SECTION` and `SLIDES` from the chapter's page
in `docs/`. Guidelines from the pilot:

- 10–12 slides, one idea each; aim for 5–8 minutes of narration (roughly 150 words per minute).
- Write narration for the ear: spell out symbols (`::` → "colon colon", `@FunctionalInterface` → "at FunctionalInterface").
- Keep code to ≤ 10 lines per block; use `size=` on `code()` to shrink dense blocks.
- Run with `--frames-only` first and fix any overflow before building audio.

## Publishing to the site

Copy the finished `out/chNN.mp4` and `.srt` files into the repo-root `videos/` folder, then run
`python3 tools/video/link_videos.py` from the repo root. It embeds a player at the top of each chapter page
and rewrites `docs/watch.md` (the **Videos** tab). The deploy workflow copies `videos/` into the built site
and converts the subtitles to WebVTT.
