#!/usr/bin/env python3
"""Owner's Math reel generator: data-driven 9:16 explainer videos.

Pipeline: scene data -> Kokoro TTS voiceover -> Pillow frames -> ffmpeg (H.264 + AAC, -14 LUFS).

Usage:
    render.py <content_module> <clip_id> <out_dir>      # one reel
    render.py <content_module> --pins <out_dir>         # Pinterest pins (1000x1500 PNG)

Env:
    KOKORO_DIR  folder with kokoro-v1.0.int8.onnx and voices-v1.0.bin
"""
import importlib
import math
import os
import re
import subprocess
import sys
import wave

import numpy as np
from num2words import num2words
from PIL import Image, ImageDraw, ImageFont

KOKORO_DIR = os.environ.get("KOKORO_DIR", "/tmp/kokoro")
VOICE = os.environ.get("REEL_VOICE", "am_michael")
SPEED = 1.0
W, H, FPS = 1080, 1920, 30
X0, X1 = 120, 960  # content column

# Two looks so Instagram and TikTok get visibly different videos.
THEMES = {
    "light": dict(bg=(244, 239, 230), ink=(29, 29, 31), acc=(232, 89, 12), pos=(43, 138, 62),
                  mute=(138, 133, 120), line=(217, 210, 195), dim=(170, 164, 150), on=(255, 255, 255)),
    "dark": dict(bg=(17, 19, 24), ink=(240, 238, 232), acc=(255, 196, 61), pos=(74, 222, 128),
                 mute=(150, 156, 168), line=(48, 53, 64), dim=(95, 101, 114), on=(17, 19, 24)),
}

FONT_PATHS = ["/usr/share/fonts/opentype/inter/Inter-Bold.otf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
FONT_FILE = next(p for p in FONT_PATHS if os.path.exists(p))
_fonts = {}


def F(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(FONT_FILE, size)
    return _fonts[size]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def seg(u, a, b):
    return ease((u - a) / (b - a))


# ------------------------------------------------------------------ speech normaliser
def _n(x):
    s = num2words(float(x)) if "." in x else num2words(int(x))
    return s.replace(" and ", " ").replace(",", "")


def speakable(text):
    """Turn caption text ($1.5M, 18-30%, 2019, 10,000) into words the TTS reads reliably."""
    t = text.replace("–", "-").replace("—", ", ").replace("&", " and ")
    t = re.sub(r"(?<=\d),(?=\d{3})", "", t)
    suf = {"K": "thousand", "M": "million", "B": "billion"}

    def mn(x):  # 4.50 -> "four fifty", 1.5 -> "one point five"
        if re.fullmatch(r"\d+\.\d\d", x):
            a, c = x.split(".")
            return _n(a) if c == "00" else f"{_n(a)} {_n(c)}"
        return _n(x)

    def money_range(m):
        a, sa, b, sb = m.group(1), m.group(2), m.group(3), m.group(4)
        if sa and sb and sa != sb:
            return f"{mn(a)} {suf[sa]} to {mn(b)} {suf[sb]} dollars"
        s = sb or sa
        tail = f" {suf[s]}" if s else ""
        return f"{mn(a)} to {mn(b)}{tail} dollars"

    t = re.sub(r"(\d+)\s*-\s*(\d+)x\b", lambda m: f"{_n(m.group(1))} to {_n(m.group(2))} times", t)
    t = re.sub(r"\$(\d+(?:\.\d+)?)([KMB])?\s*(?:-|to)\s*\$?(\d+(?:\.\d+)?)([KMB])?\b", money_range, t)
    t = re.sub(r"\$(\d+(?:\.\d+)?)([KMB])\b", lambda m: f"{_n(m.group(1))} {suf[m.group(2)]} dollars", t)
    t = re.sub(r"\$(\d+(?:\.\d+)?)\s+(million|billion|thousand)", lambda m: f"{_n(m.group(1))} {m.group(2)} dollars", t)
    t = re.sub(r"\$(\d+)\.(\d\d)\b", lambda m: f"{_n(m.group(1))} dollars {_n(m.group(2))}" if m.group(2) != "00" else f"{_n(m.group(1))} dollars", t)
    t = re.sub(r"\$(\d+)", lambda m: f"{_n(m.group(1))} dollars", t)
    t = re.sub(r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)%", lambda m: f"{_n(m.group(1))} to {_n(m.group(2))} percent", t)
    t = re.sub(r"(\d+(?:\.\d+)?)%", lambda m: f"{_n(m.group(1))} percent", t)
    t = re.sub(r"\b(19|20)(\d\d)\b", lambda m: num2words(int(m.group(0)), to="year"), t)
    t = re.sub(r"(\d+)\s*-\s*(\d+)", lambda m: f"{_n(m.group(1))} to {_n(m.group(2))}", t)
    t = re.sub(r"(\d+)x\b", lambda m: f"{_n(m.group(1))} times", t)
    t = re.sub(r"\d+(?:\.\d+)?", lambda m: _n(m.group(0)), t)
    return re.sub(r"\s+", " ", t).strip()


# ------------------------------------------------------------------ drawing helpers
class Pen:
    def __init__(self, d, th):
        self.d, self.th = d, th

    def c(self, key):
        return self.th[key] if isinstance(key, str) else key

    def text(self, xy, s, size, col="ink", anchor="mm"):
        self.d.text(xy, s, font=F(size), fill=self.c(col), anchor=anchor)

    def fit(self, xy, s, size, col="ink", maxw=X1 - X0 + 60, anchor="mm"):
        while size > 30 and F(size).getlength(s) > maxw:
            size -= 4
        self.text(xy, s, size, col, anchor)

    def multi(self, xy, s, size, col="ink"):
        self.d.multiline_text(xy, s, font=F(size), fill=self.c(col), anchor="ma", align="center", spacing=6)

    def pill(self, box, col, r=None):
        x0, y0, x1, y1 = box
        r = r if r is not None else (y1 - y0) // 2
        if x1 - x0 >= 2 * r:
            self.d.rounded_rectangle(box, radius=r, fill=self.c(col))
        elif x1 > x0:
            self.d.rounded_rectangle((x0, y0, x0 + 2 * r, y1), radius=r, fill=self.c(col))


# ------------------------------------------------------------------ scene types
# Every scene is a dict with "type" plus fields; draw(p, sc, t, u) where u is 0..1 scene progress.
def draw_big(p, sc, t, u):
    y = sc.get("y", 560)
    if sc.get("label"):
        p.text((W // 2, y - 170), sc["label"], 40, "acc")
    p.fit((W // 2, y), sc["big"], sc.get("size", 150), sc.get("col", "acc"))
    if sc.get("sub"):
        p.fit((W // 2, y + 150), sc["sub"], 58)
    if sc.get("note") and u > 0.25:
        p.fit((W // 2, y + 240), sc["note"], 38, "mute")


def draw_bars(p, sc, t, u):
    """Horizontal range bars. rows: [label, lo, hi, text, colour]; scale: max value."""
    if sc.get("label"):
        p.text((W // 2, 380), sc["label"], 40, "acc")
    rows = sc["rows"]
    top = sc.get("top", 470)
    step = min(190, (1080 - top) // max(len(rows), 1))
    vmax = sc["scale"]
    for i, (lab, lo, hi, txt, col) in enumerate(rows):
        y = top + i * step
        pr = seg(u, 0.05 + i * 0.12, 0.35 + i * 0.12)
        p.text((X0, y), lab, 40, "ink", "lm")
        p.pill((X0, y + 34, X1, y + 34 + 42), "line")
        xa = X0 + lo / vmax * (X1 - X0)
        xb = X0 + hi / vmax * (X1 - X0)
        if pr > 0:
            p.pill((xa, y + 34, max(xa + 42, xa + (xb - xa) * pr), y + 76), col)
        if pr > 0.9:
            p.text((X1, y), txt, 40, col, "rm")


def draw_donut(p, sc, t, u):
    pr = seg(u, 0.05, 0.55)
    bb = (310, 380, 770, 840)
    p.d.arc(bb, 0, 360, fill=p.c("line"), width=64)
    p.d.arc(bb, -90, -90 + 360 * sc["frac"] * pr, fill=p.c(sc.get("col", "acc")), width=64)
    p.fit((W // 2, 610), sc["big"], 96, maxw=380)
    p.text((W // 2, 930), sc["line1"], 46)
    p.fit((W // 2, 995), sc["line2"], 54, sc.get("col", "acc"))


def draw_stack(p, sc, t, u):
    """100% bar split into parts: [fraction, colour, value label, name]."""
    p.text((W // 2, 400), sc["label"], 40, "acc")
    x = X0
    for i, (frac, col, lab, name) in enumerate(sc["parts"]):
        wpx = (X1 - X0) * frac
        pr = seg(u, 0.05 + i * 0.15, 0.3 + i * 0.15)
        if pr > 0:
            p.d.rectangle((x, 560, x + wpx * pr, 700), fill=p.c(col))
            if pr > 0.9:
                if wpx > 90:
                    p.fit((x + wpx / 2, 630), lab, 40, "on", maxw=wpx - 10)
                p.multi((x + wpx / 2, 730 + (i % 2) * 120 if sc.get("stagger") else 730), name, 32)
        x += wpx
    if sc.get("note"):
        p.fit((W // 2, 1000), sc["note"], 36, "mute")


def draw_eq(p, sc, t, u):
    lines = sc["lines"]
    n = len(lines)
    y0 = 470
    for i, s in enumerate(lines):
        if u > 0.05 + i * 0.15:
            p.fit((W // 2, y0 + i * 105), s, 76)
    yl = y0 + n * 105 - 25
    if u > 0.05 + n * 0.15:
        p.d.line((X0 + 120, yl, X1 - 120, yl), fill=p.c("ink"), width=6)
    if u > 0.12 + n * 0.15:
        p.fit((W // 2, yl + 120), sc["result"], 120, sc.get("col", "pos"))
        if sc.get("sub"):
            p.fit((W // 2, yl + 225), sc["sub"], 46, "mute")


def draw_cols(p, sc, t, u):
    """Vertical bar comparison. cols: [label, value, value text, colour]."""
    if sc.get("label"):
        p.text((W // 2, 380), sc["label"], 40, "acc")
    cols = sc["cols"]
    n = len(cols)
    base, hmax = 1000, 430
    vmax = max(c[1] for c in cols)
    gap = (X1 - X0) / n
    bw = min(220, gap * 0.62)
    for i, (lab, v, txt, col) in enumerate(cols):
        cx = X0 + gap * (i + 0.5)
        h = hmax * v / vmax * seg(u, 0.05 + i * 0.15, 0.4 + i * 0.15)
        if h > 16:
            p.d.rounded_rectangle((cx - bw / 2, base - h, cx + bw / 2, base), radius=14, fill=p.c(col))
        if h >= hmax * v / vmax * 0.97:
            p.fit((cx, base - h - 45), txt, 46 if n <= 3 else 38, col, maxw=gap)
        p.fit((cx, base + 50), lab, 40 if n <= 3 else 32, "mute", maxw=gap)
    p.d.line((X0 - 20, base, X1 + 20, base), fill=p.c("ink"), width=5)


def draw_ladder(p, sc, t, u):
    """Ranked list that reveals one row at a time. rows: [name, value text]."""
    p.text((W // 2, 370), sc["label"], 40, "acc")
    rows = sc["rows"]
    step = min(98, 700 // len(rows))
    for i, (name, val) in enumerate(rows):
        if u < 0.04 + i * (0.8 / len(rows)):
            continue
        y = 450 + i * step
        p.d.rounded_rectangle((X0 - 30, y - step // 2 + 6, X1 + 30, y + step // 2 - 6), radius=18,
                              fill=p.c("line"))
        p.text((X0, y), f"{i + 1}. {name}", 42, "ink", "lm")
        p.text((X1, y), val, 42, sc.get("col", "acc"), "rm")


def draw_blocks(p, sc, t, u):
    """Counting tiles, e.g. payback years."""
    p.fit((W // 2, 510), sc["big"], 130, sc.get("col", "acc"))
    if sc.get("sub"):
        p.fit((W // 2, 650), sc["sub"], 50, "mute")
    n = sc["n"]
    k = int(clamp((u - 0.1) / 0.7) * n + 1e-4)
    size = min(90, (X1 - X0) // n)
    x0 = W / 2 - size * n / 2
    for i in range(n):
        x = x0 + i * size
        on = i < k
        p.d.rounded_rectangle((x + 5, 790, x + size - 5, 790 + size - 10), radius=12,
                              fill=p.c(sc.get("col", "acc") if on else "line"))
        p.text((x + size / 2, 790 + (size - 10) / 2), str(i + 1), 34, "on" if on else "mute")
    if sc.get("foot"):
        p.fit((W // 2, 940), sc["foot"], 42)


def draw_cta(p, sc, t, u):
    p.fit((W // 2, 520), sc["big"], 160, "acc")
    p.fit((W // 2, 670), sc["sub"], 76)
    if u > 0.3:
        p.fit((W // 2, 880), sc.get("follow", "Follow for more business math"), 54)


DRAW = {"big": draw_big, "bars": draw_bars, "donut": draw_donut, "stack": draw_stack, "eq": draw_eq,
        "cols": draw_cols, "ladder": draw_ladder, "blocks": draw_blocks, "cta": draw_cta}


# ------------------------------------------------------------------ audio + video
def synth(clip, out_dir):
    from kokoro_onnx import Kokoro

    k = Kokoro(os.path.join(KOKORO_DIR, "kokoro-v1.0.int8.onnx"), os.path.join(KOKORO_DIR, "voices-v1.0.bin"))
    sr = 24000
    pieces, timeline = [np.zeros(int(sr * 0.15), np.float32)], []
    cur = 0.15
    for sc in clip["scenes"]:
        start, sents = cur, []
        for show in sc["say"]:
            samples, _ = k.create(speakable(show), voice=VOICE, speed=SPEED, lang="en-us")
            samples = samples.astype(np.float32)
            dur = len(samples) / sr
            pieces += [samples, np.zeros(int(sr * 0.3), np.float32)]
            sents.append((cur, cur + dur, show))
            cur += dur + 0.3
        timeline.append((start, cur, sents, sc))
    tail = 1.2
    if clip.get("min_len") and cur + tail < clip["min_len"]:
        tail = clip["min_len"] - cur  # hold the end card so TikTok clips clear 60 s
    pieces.append(np.zeros(int(sr * tail), np.float32))
    cur += tail
    st, se, ss, sc = timeline[-1]
    timeline[-1] = (st, cur, ss, sc)
    audio = np.concatenate(pieces)
    audio = audio / (float(np.max(np.abs(audio))) or 1.0) * 0.9
    path = os.path.join(out_dir, "voice.wav")
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((audio * 32767).astype(np.int16).tobytes())
    return path, timeline, cur


def wrap(words, font, maxw):
    lines, line, wl = [], [], 0
    sp = font.getlength(" ")
    for i, w in enumerate(words):
        ww = font.getlength(w)
        if line and wl + sp + ww > maxw:
            lines.append(line)
            line, wl = [], 0
        line.append(i)
        wl += (sp if wl else 0) + ww
    if line:
        lines.append(line)
    return lines


def caption(p, show, frac, y_mid):
    words = show.split()
    font = F(56)
    lines = wrap(words, font, 900)
    total = sum(len(w) + 1 for w in words)
    cum, starts = 0, []
    for w in words:
        starts.append(cum / total)
        cum += len(w) + 1
    cur = max(i for i, s in enumerate(starts) if s <= frac + 1e-6)
    lh, sp = 78, font.getlength(" ")
    y = y_mid - (len(lines) - 1) * lh / 2
    for line in lines:
        ws = [font.getlength(words[i]) for i in line]
        x = (W - sum(ws) - sp * (len(line) - 1)) / 2
        for j, wi in enumerate(line):
            col = "ink" if wi < cur else ("acc" if wi == cur else "dim")
            p.d.text((x, y), words[wi], font=font, fill=p.c(col), anchor="lm")
            x += ws[j] + sp
        y += lh


def render(clip, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    th = THEMES[clip.get("theme", "light")]
    wav, timeline, total = synth(clip, out_dir)
    out = os.path.join(out_dir, f"{clip['id']}.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
           "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "128k",
           "-movflags", "+faststart", "-shortest", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(math.ceil(total * FPS))
    for fi in range(n):
        t = fi / FPS
        img = Image.new("RGB", (W, H), th["bg"])
        p = Pen(ImageDraw.Draw(img), th)
        p.d.rectangle((0, 0, W * clamp(t / total), 10), fill=th["acc"])
        p.fit((W // 2, 190), clip["header"], 34, "acc")
        p.d.line((X0, 235, X1, 235), fill=th["line"], width=4)
        for st, en, sents, sc in timeline:
            if st <= t < en or (fi == n - 1 and sc is timeline[-1][3]):
                DRAW[sc["type"]](p, sc, t - st, clamp((t - st) / (en - st)))
                shown = sents[-1]
                for s in sents:
                    if t < s[1] + 0.15:
                        shown = s
                        break
                caption(p, shown[2], clamp((t - shown[0]) / max(shown[1] - shown[0], 0.01)),
                        sc.get("cap_y", 1260))
                break
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed")
    return out, total


# ------------------------------------------------------------------ Pinterest pins
def render_pin(pin, path):
    PW, PH = 1000, 1500
    th = THEMES[pin.get("theme", "light")]
    img = Image.new("RGB", (PW, PH), th["bg"])
    p = Pen(ImageDraw.Draw(img), th)
    p.d.rectangle((0, 0, PW, 16), fill=th["acc"])
    p.text((PW // 2, 110), pin.get("kicker", "THE ECONOMICS OF OWNING A"), 36, "acc")
    size = 104
    while F(size).getlength(pin["title"]) > PW - 120:
        size -= 4
    p.text((PW // 2, 215), pin["title"], size)
    p.d.line((90, 300, PW - 90, 300), fill=th["line"], width=4)
    y = 360
    for big, label in pin["stats"]:
        p.d.rounded_rectangle((70, y, PW - 70, y + 210), radius=28, fill=th["line"])
        s = 92
        while F(s).getlength(big) > PW - 200:
            s -= 4
        p.text((PW // 2, y + 82), big, s, "pos" if pin.get("green") == big else "acc")
        p.text((PW // 2, y + 165), label, 36)
        y += 240
    p.text((PW // 2, PH - 150), pin.get("source", ""), 26, "mute")
    p.text((PW // 2, PH - 80), "Owner's Math  |  full breakdowns on YouTube", 34, "ink")
    img.save(path)


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    mod = importlib.import_module(sys.argv[1])
    if sys.argv[2] == "--pins":
        os.makedirs(sys.argv[3], exist_ok=True)
        for pin in mod.PINS:
            render_pin(pin, os.path.join(sys.argv[3], f"{pin['id']}.png"))
            print("pin", pin["id"])
    else:
        clip = next(c for c in mod.CLIPS if c["id"] == sys.argv[2])
        out, total = render(clip, sys.argv[3])
        print(f"done {out} {total:.1f}s", flush=True)
