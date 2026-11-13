"""Build a narrated slide video for one topic module.

usage: python -I build.py <topic-module-name> <out-dir> [--voice am_michael] [--speed 1.0]
"""
import argparse, importlib, json, os, subprocess, sys, wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE / "topics")]
from kit import PYGMENTS_CSS  # noqa: E402

KOKORO = Path(os.environ.get("KOKORO_DIR", HERE / "models"))
SR = 24000
GAP_STEP, GAP_SLIDE, LEAD_IN = 0.45, 0.9, 0.6

CSS = """
@page { size: 1920px 1080px; margin: 0 }
* { box-sizing: border-box }
html, body { margin: 0; width: 1920px; height: 1080px; overflow: hidden }
body { font-family: Inter, 'DejaVu Sans', sans-serif; color: #e6e8f5;
  background: radial-gradient(1200px 700px at 85% -10%, rgba(99,102,241,.35), transparent 60%),
              radial-gradient(900px 600px at -10% 110%, rgba(217,70,239,.22), transparent 60%), #0d0f1f; }
.top { position: absolute; top: 0; left: 0; right: 0; height: 84px; display: flex; align-items: center;
  padding: 0 96px; gap: 18px; font-size: 24px; color: #a3acc7; border-bottom: 1px solid #2a2f5a }
.logo { width: 34px; height: 34px; border-radius: 9px; background: linear-gradient(135deg,#6366f1,#d946ef) }
.top b { color: #e6e8f5; font-weight: 700 }
.top .sec { margin-left: auto; color: #818cf8; font-weight: 600 }
.main { position: absolute; top: 84px; bottom: 60px; left: 96px; right: 96px; padding-top: 44px;
  display: flex; flex-direction: column; gap: 22px }
.kicker { font-size: 26px; text-transform: uppercase; letter-spacing: .14em; color: #e879f9; font-weight: 700 }
h1 { margin: -14px 0 6px; font: 800 68px/1.08 'Inter Display', Inter, sans-serif; letter-spacing: -.02em;
  background: linear-gradient(90deg,#fff,#c7d2fe); -webkit-background-clip: text; color: transparent }
.title .main { justify-content: center; padding-top: 0; gap: 34px }
.title h1 { font-size: 112px }
.title .kicker { font-size: 32px }
p.sub { font-size: 40px; line-height: 1.4; color: #c7d2fe; max-width: 1400px; margin: 0 }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: .86em; background: rgba(129,140,248,.16);
  color: #c7d2fe; padding: .08em .32em; border-radius: 6px }
.code { background: #151833; border: 1px solid #2a2f5a; border-radius: 16px; overflow: hidden }
.code-title { font-size: 20px; color: #a3acc7; padding: 10px 22px; border-bottom: 1px solid #2a2f5a;
  font-family: 'DejaVu Sans Mono', monospace; background: rgba(255,255,255,.02) }
.code pre { margin: 0; padding: 18px 24px; font: 32px/1.42 'DejaVu Sans Mono', monospace; color: #e6edf3; white-space: pre }
.code pre code { background: none; padding: 0; font-size: 1em }
.callout { margin: 0; font-size: 34px; line-height: 1.4; color: #e6e8f5; padding: 18px 28px;
  border-left: 6px solid #d946ef; background: rgba(217,70,239,.08); border-radius: 0 12px 12px 0 }
.main > * { flex-shrink: 0 }
table.sm { font-size: 25px } table.sm td { padding: 11px 16px }
.frag { opacity: 1 }
.frag.hidden { opacity: 0 }
.flow { display: flex; align-items: stretch; gap: 14px }
.flow .fbox { flex: 1; font-size: 27px; line-height: 1.45; padding: 20px 22px; border-radius: 14px;
  background: rgba(99,102,241,.14); border: 1px solid rgba(129,140,248,.45) }
.flow .arrow { font-size: 44px; color: #e879f9; display: flex; align-items: center }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; align-items: stretch }
.grid2.start { align-items: start }
.grid4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 22px }
.card { border-radius: 16px; padding: 26px 28px; background: rgba(255,255,255,.035); border: 1px solid #2a2f5a;
  border-top: 6px solid var(--c); height: 100% }
.card.indigo { --c: #6366f1 } .card.fuchsia { --c: #d946ef } .card.cyan { --c: #06b6d4 } .card.amber { --c: #fbbf24 }
.card-h { font-size: 34px; font-weight: 750; margin-bottom: 12px; font-family: 'DejaVu Sans Mono', monospace; color: #fff }
.grid2 .card-h { font-family: Inter, sans-serif }
.card-b { font-size: 29px; line-height: 1.45; color: #c7d2fe }
ul.bullets { margin: 0; padding-left: 0; list-style: none; display: flex; flex-direction: column; gap: 18px }
ul.bullets li { font-size: 36px; line-height: 1.35; padding-left: 46px; position: relative }
ul.bullets li::before { content: ''; position: absolute; left: 6px; top: .45em; width: 18px; height: 18px;
  border-radius: 5px; background: linear-gradient(135deg,#6366f1,#d946ef) }
ul.bullets.sm li { font-size: 31px }
ul.bullets.bad li::before { background: #f43f5e; border-radius: 50% }
ul.bullets.recap li { font-size: 42px }
.col-h { font-size: 30px; font-weight: 800; text-transform: uppercase; letter-spacing: .12em; margin-bottom: 18px }
.col-h.ok { color: #34d399 } .col-h.bad { color: #fb7185 }
table { border-collapse: collapse; width: 100%; font-size: 29px; background: rgba(255,255,255,.03);
  border-radius: 14px; overflow: hidden }
th { text-align: left; color: #a5b4fc; font-weight: 700; padding: 14px 20px; background: rgba(99,102,241,.16) }
td { padding: 13px 20px; border-top: 1px solid #2a2f5a; line-height: 1.3 }
table.wide { font-size: 34px } table.wide td:first-child { width: 220px; color: #e879f9 }
.pipeline { display: flex; gap: 20px; align-items: center; font-size: 36px; color: #818cf8; font-weight: 700 }
.pipeline span { color: #e6e8f5; background: rgba(99,102,241,.16); padding: 6px 22px; border-radius: 12px }
.pipeline span.hl { background: linear-gradient(135deg,#6366f1,#d946ef) }
.foot { position: absolute; left: 96px; right: 96px; bottom: 26px; display: flex; align-items: center; gap: 24px;
  font-size: 20px; color: #a3acc7 }
.bar { flex: 1; height: 6px; background: #2a2f5a; border-radius: 3px; overflow: hidden }
.bar i { display: block; height: 100%; background: linear-gradient(90deg,#6366f1,#d946ef) }
""" + PYGMENTS_CSS


def page(mod, idx, total, slide, step):
    kind = slide.get("kind", "content")
    body = slide["body"]
    pct = 100 * (idx + 1) / total
    script = f"""<script>document.querySelectorAll('.frag').forEach(e=>{{
      if (+e.dataset.step > {step}) e.classList.add('hidden') }});</script>"""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body class="{kind}"><div class="top"><div class="logo"></div><b>Modern Java Enterprise Handbook</b>
<span>·</span><span>{mod.CHAPTER}</span><span class="sec">{mod.SECTION}</span></div>
<div class="main"><div class="kicker">{slide['kicker']}</div><h1>{slide['title']}</h1>{body}</div>
<div class="foot"><span>{idx + 1} / {total}</span><div class="bar"><i style="width:{pct:.1f}%"></i></div>
<span>khiruashish.github.io/java-playbook</span></div>{script}</body></html>"""


def silence(sec):
    import numpy as np
    return np.zeros(int(sec * SR), dtype="float32")


def srt_time(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("topic"); ap.add_argument("out")
    ap.add_argument("--voice", default="am_michael"); ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--frames-only", action="store_true")
    a = ap.parse_args()
    mod = importlib.import_module(a.topic)
    out = Path(a.out).resolve(); work = out / f"{a.topic}-work"; work.mkdir(parents=True, exist_ok=True)

    # 1) HTML for every step, then screenshot them all in one Chromium session
    steps = []  # (png, text, is_last_step_of_slide)
    total = len(mod.SLIDES)
    for i, s in enumerate(mod.SLIDES):
        for k, text in enumerate(s["narration"]):
            h = work / f"s{i:02}_{k:02}.html"
            h.write_text(page(mod, i, total, s, k), encoding="utf-8")
            steps.append((h.with_suffix(".png"), text, k == len(s["narration"]) - 1))
    if subprocess.run(["node", str(HERE / "render.js"), *[str(p.with_suffix(".html")) for p, _, _ in steps]]).returncode:
        sys.exit("slides overflow — fix layout first")
    if a.frames_only:
        return

    # 2) narration, one clip per step, laid end to end with pauses
    import numpy as np, soundfile as sf
    from kokoro_onnx import Kokoro
    tts = Kokoro(str(KOKORO / "kokoro-v1.0.onnx"), str(KOKORO / "voices-v1.0.bin"))
    audio, concat, cues, t = [silence(LEAD_IN)], ["ffconcat version 1.0"], [], LEAD_IN
    for n, (png, text, last) in enumerate(steps):
        clip, sr = tts.create(text, voice=a.voice, speed=a.speed, lang="en-us")
        assert sr == SR
        gap = GAP_SLIDE if last else GAP_STEP
        dur = len(clip) / SR
        cues.append((t, t + dur, text))
        seg = dur + gap + (LEAD_IN if n == 0 else 0)
        audio += [clip.astype("float32"), silence(gap)]
        t += dur + gap
        concat += [f"file '{png}'", f"duration {seg:.3f}"]
        print(f"  step {n + 1}/{len(steps)}  {dur:5.1f}s", flush=True)
    concat.append(f"file '{steps[-1][0]}'")
    wav = work / "narration.wav"; sf.write(wav, np.concatenate(audio), SR)
    (work / "frames.ffconcat").write_text("\n".join(concat) + "\n")

    # 3) subtitles (sentence-ish chunks spread over each step's clip)
    import re
    lines, n = [], 1
    for start, end, text in cues:
        parts = [p for p in re.split(r"(?<=[.?!])\s+", text) if p]
        weights = [len(p) for p in parts]; acc = start
        for p, w in zip(parts, weights):
            d = (end - start) * w / sum(weights)
            lines += [str(n), f"{srt_time(acc)} --> {srt_time(acc + d)}", p, ""]; n += 1; acc += d
    srt = out / f"{a.topic}.srt"; srt.write_text("\n".join(lines), encoding="utf-8")

    # 4) encode
    mp4 = out / f"{a.topic}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(work / "frames.ffconcat"),
                    "-i", str(wav), "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "medium",
                    "-tune", "stillimage", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
                    "-movflags", "+faststart", "-shortest", str(mp4)], check=True)
    print(json.dumps({"mp4": str(mp4), "srt": str(srt), "seconds": round(t, 1), "steps": len(steps)}))


if __name__ == "__main__":
    main()
