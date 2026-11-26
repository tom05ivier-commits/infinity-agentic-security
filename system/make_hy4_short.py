#!/usr/bin/env python3
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
"""Video vertikal 9:16 (TikTok / YouTube Shorts) untuk model hy4.

1080x1920, H.264 + AAC, narasi suara neural edge-tts dengan fallback
espeak-ng. Teks dan caption dirancang masuk dalam area aman platform:
bagian atas dan bawah dikosongkan untuk tombol serta judul UI.
"""

import json
import math
import os
import random
import subprocess
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 24
DURATION = 40.0
TOTAL_FRAMES = int(FPS * DURATION)
WORK = "/tmp/opencode/hy4_short_build"
OUT = "/root/workspace/hy4-short-9x16.mp4"
POSTER = "/root/workspace/hy4-short-poster.png"
VIDEO_TITLE = "hy4 — IT Agenty Infinity (Short)"

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

CYAN = (59, 224, 239)
BLUE = (92, 133, 255)
RED = (255, 83, 105)
WHITE = (246, 249, 255)
MUTED = (158, 178, 212)
DIM = (112, 134, 173)
PANEL = (13, 26, 53, 240)
PANEL_EDGE = (58, 96, 160, 210)

SCENES = [
    {"start": 0.0, "end": 5.2},
    {"start": 5.2, "end": 11.2},
    {"start": 11.2, "end": 21.2},
    {"start": 21.2, "end": 32.2},
    {"start": 32.2, "end": 40.0},
]
CROSS = 0.5

NARRATION = [
    "Memperkenalkan Hai Four, untuk IT Agenty Infinity.",
    "Apa itu Hai Four? Model OpenCode yang ringan dan gratis.",
    "Kemampuan Hai Four: menulis kode, eksplorasi codebase, keamanan dan S O C, otomasi platform, serta riset teknis.",
    "Keunggulannya: gratis, terintegrasi, sembilan agent, delapan perintah, dukungan CLI, dan privasi terjaga.",
    "Hai Four. Otak dari IT Agenty Infinity. Coba sekarang.",
]

CAPTIONS = [
    "Memperkenalkan hy4 — model AI IT Agenty",
    "Model OpenCode yang ringan & gratis",
    "Kode, eksplorasi, keamanan, otomasi, riset",
    "10 agent + 10 command, privasi terjaga",
    'Coba: tom05 "pertanyaan Anda"',
]

CAPABILITIES = [
    ("01", "Berpikir & Menulis Kode", "build agent: dari ide menjadi implementasi"),
    ("02", "Eksplorasi Codebase", "explore agent: memahami struktur & dependensi"),
    ("03", "Keamanan & SOC", "security agent: deteksi, karantina, audit"),
    ("04", "Platform Engineering", "platform agent: CLI, infrastruktur, otomasi"),
    ("05", "Riset & Penjelasan", "professor: dokumentasi & troubleshooting"),
]

ADVANTAGES = [
    ("Gratis & ringan", "Tanpa biaya, respons cepat.", "01"),
    ("Konteks workspace penuh", "Panduan kerja dari AGENTS.md.", "02"),
    ("10 agent + 10 command", "Sinkron otomatis ke Copilot CLI.", "03"),
    ("Ekosistem CLI siap pakai", "gh, kubectl, terraform, tofu.", "04"),
    ("Privasi & lisensi aman", "Tom05ivier-commits-1.0.", "05"),
]

FONTS = {}


def get_font(size, bold=True, mono=False):
    key = (size, bold, mono)
    if key not in FONTS:
        path = FONT_MONO_BOLD if (mono and bold) else FONT_MONO if mono else FONT_BOLD if bold else FONT_REG
        FONTS[key] = ImageFont.truetype(path, size)
    return FONTS[key]


def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def smooth(v):
    v = clamp(v)
    return v * v * (3.0 - 2.0 * v)


def ease_out(v):
    v = clamp(v)
    return 1.0 - (1.0 - v) ** 3


@lru_cache(maxsize=512)
def sprite(text, size, color, bold=True, mono=False, glow=None, radius=14, tracking=0):
    font = get_font(size, bold, mono)
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    lines = text.split("\n")
    widths = []
    for line in lines:
        if tracking:
            widths.append(sum(probe.textlength(c, font=font) for c in line) + tracking * max(0, len(line) - 1))
        else:
            widths.append(probe.textlength(line, font=font))
    tw = int(max(widths)) + 6
    lh = int(size * 1.32)
    th = lh * len(lines) + 6
    pad = int(radius * 2.6) if glow else 4
    img = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        x, y = pad + 3, pad + 3 + i * lh
        if tracking:
            for ch in line:
                d.text((x, y), ch, font=font, fill=color + (255,))
                x += probe.textlength(ch, font=font) + tracking
        else:
            d.text((x, y), line, font=font, fill=color + (255,))
    if glow:
        blur = img.filter(ImageFilter.GaussianBlur(radius))
        blur.putalpha(blur.getchannel("A").point(lambda a: int(a * 0.9)))
        img = Image.alpha_composite(blur, img)
    return img


def wrap_text(text, size, max_width, bold=False):
    font = get_font(size, bold)
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    lines, current = [], ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if probe.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def paste(frame, sp, x, y, alpha=1.0, anchor="lt", scale=1.0):
    if alpha <= 0.002:
        return
    if scale != 1.0:
        sp = sp.resize((max(1, int(sp.width * scale)), max(1, int(sp.height * scale))), Image.LANCZOS)
    if anchor in ("mm", "mt", "mb"):
        x -= sp.width / 2
    if anchor in ("mm", "lm", "rm"):
        y -= sp.height / 2
    if anchor in ("rm", "rt", "rb"):
        x -= sp.width
    if alpha < 0.999:
        sp = sp.copy()
        sp.putalpha(sp.getchannel("A").point(lambda a: int(a * alpha)))
    frame.alpha_composite(sp, (int(x), int(y)))


def make_background():
    base = Image.new("RGB", (W, H))
    px = base.load()
    for y in range(H):
        f = y / H
        r = int(5 + 7 * f)
        g = int(10 + 17 * f)
        b = int(24 + 34 * f)
        for x in range(W):
            px[x, y] = (r, g, b)
    base = base.convert("RGBA")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-500, -300, 900, 700], fill=(20, 120, 190, 65))
    gd.ellipse([300, 1000, 1500, 2100], fill=(45, 70, 180, 58))
    gd.ellipse([-300, 1500, 700, 2300], fill=(150, 30, 70, 30))
    base.alpha_composite(glow.filter(ImageFilter.GaussianBlur(150)))
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(grid)
    for x in range(0, W, 60):
        nd.line([(x, 0), (x, H)], fill=(90, 140, 210, 12), width=1)
    for y in range(0, H, 60):
        nd.line([(0, y), (W, y)], fill=(90, 140, 210, 12), width=1)
    base.alpha_composite(grid)
    return base


BASE = None
PARTICLES = []


def init_particles():
    rnd = random.Random(20261120)
    for _ in range(58):
        PARTICLES.append({
            "x": rnd.uniform(0, W), "y": rnd.uniform(0, H),
            "r": rnd.uniform(1.0, 2.8), "vy": rnd.uniform(6, 20),
            "vx": rnd.uniform(-4, 4), "phase": rnd.uniform(0, 6.28),
            "color": rnd.choice([CYAN, BLUE, WHITE]),
        })


def draw_particles(frame, t):
    d = ImageDraw.Draw(frame)
    for p in PARTICLES:
        y = (p["y"] - t * p["vy"]) % H
        x = (p["x"] + t * p["vx"]) % W
        a = int(25 + 45 * (0.5 + 0.5 * math.sin(t * 1.6 + p["phase"])))
        r = p["r"]
        d.ellipse([x - r, y - r, x + r, y + r], fill=p["color"] + (a,))


def scene_one(local, t):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, 800
    appear = ease_out(local / 0.9)
    for rad, col, wid in [(330, (40, 90, 160, 60), 2), (392, (30, 200, 225, 38), 1)]:
        d.arc([cx - rad, cy - rad, cx + rad, cy + rad], start=t * 24, end=t * 24 + 205, fill=col, width=wid)
    d.ellipse([cx - 300, cy - 300, cx + 300, cy + 300], outline=(60, 200, 235, 32), width=1)
    paste(im, sprite("MEMPERSENALKAN", 26, CYAN, bold=True, tracking=6), cx, 520, appear, "mm")
    logo = sprite("hy4", 220, WHITE, bold=True, mono=True, glow=CYAN, radius=30)
    paste(im, logo, cx, cy, appear, "mm", 0.84 + 0.16 * ease_out(local / 1.1))
    paste(im, sprite("MODEL AI UNTUK IT AGENTY", 40, WHITE, bold=True, tracking=1), cx, 1080, ease_out((local - 0.5) / 0.8), "mm")
    pill = sprite("  opencode/hy4-flash-free  ", 28, CYAN, bold=True, mono=True)
    pw, ph = pill.size
    a = ease_out((local - 1.0) / 0.8)
    d.rounded_rectangle([cx - pw / 2 - 26, 1180 - 12, cx + pw / 2 + 26, 1180 + ph + 12], radius=24, fill=(16, 38, 72, 235), outline=(60, 160, 210, 180), width=2)
    paste(im, pill, cx, 1180, a, "mm")
    return im


def scene_two(local, t):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    a0 = ease_out(local / 0.6)
    paste(im, sprite("APA ITU hy4?", 72, WHITE, bold=True, glow=CYAN, radius=12), 90, 300, a0)
    d.rounded_rectangle([92, 412, 280, 420], radius=4, fill=CYAN + (int(220 * a0),))
    paste(im, sprite("Ringan. Cepat. Terintegrasi.", 34, MUTED), 92, 446, a0)
    items = [
        "Model AI default di OpenCode",
        "Ringan & gratis — flash-free",
        "Berjalan langsung di workspace",
        "Konteks penuh lewat AGENTS.md",
    ]
    for i, item in enumerate(items):
        p = ease_out((local - 0.5 - i * 0.65) / 0.6)
        if p <= 0:
            continue
        y = 580 + i * 155
        d.rounded_rectangle([94, y + 8, 116, y + 30], radius=4, fill=CYAN + (int(225 * p),))
        paste(im, sprite(item, 38, WHITE, bold=True), 144, y - 4, p)
        d.line([(144, y + 64), (990, y + 64)], fill=(60, 100, 160, int(70 * p)), width=1)
    p = ease_out((local - 1.0) / 0.7)
    if p > 0:
        x1, y1, x2, y2 = 80, 1250, 1000, 1460
        d.rounded_rectangle([x1, y1, x2, y2], radius=22, fill=PANEL, outline=PANEL_EDGE, width=2)
        d.rounded_rectangle([x1, y1, x2, y1 + 54], radius=22, fill=(20, 40, 78, 245))
        d.rectangle([x1, y1 + 30, x2, y1 + 54], fill=(20, 40, 78, 245))
        for i, col in enumerate([RED, (255, 195, 90), CYAN]):
            d.ellipse([x1 + 24 + i * 28, y1 + 19, x1 + 40 + i * 28, y1 + 35], fill=col + (235,))
        paste(im, sprite("terminal — hy4", 19, MUTED, mono=True), x1 + 130, y1 + 16, p)
        for i, (line, col) in enumerate([
            ('$ tom05 "lindungi hardware"', WHITE),
            ("> AGENTS.md terbaca · siap.", CYAN),
        ]):
            paste(im, sprite(line, 25, col, mono=True), x1 + 30, y1 + 84 + i * 48, ease_out((local - 1.3 - i * 0.5) / 0.5))
    return im


def scene_three(local, t):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    a0 = ease_out(local / 0.6)
    paste(im, sprite("KEMAMPUAN", 68, WHITE, bold=True, glow=BLUE, radius=12), 90, 280, a0)
    paste(im, sprite("Lima peran dalam satu model.", 30, MUTED), 92, 380, a0)
    for i, ((num, title, desc), y) in enumerate(zip(CAPABILITIES, [440 + i * 202 for i in range(5)])):
        p = ease_out((local - 0.4 - i * 1.45) / 0.8)
        if p <= 0:
            continue
        yy = y + int((1 - p) * 28)
        d.rounded_rectangle([82, yy + 6, 998, yy + 196], radius=20, fill=(0, 0, 0, int(45 * p)))
        d.rounded_rectangle([80, yy, 996, yy + 190], radius=20, fill=(15, 30, 60, int(238 * p)), outline=(58, 96, 160, int(195 * p)), width=2)
        d.rounded_rectangle([80, yy + 22, 86, yy + 168], radius=3, fill=CYAN + (int(235 * p),))
        paste(im, sprite(num, 24, CYAN, bold=True, mono=True), 112, yy + 18, p)
        paste(im, sprite(title, 36, WHITE, bold=True), 112, yy + 56, p)
        for j, part in enumerate(wrap_text(desc, 26, 820)):
            paste(im, sprite(part, 26, MUTED), 112, yy + 112 + j * 34, p * 0.96)
    return im


def scene_four(local, t):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    a0 = ease_out(local / 0.6)
    paste(im, sprite("KEUNGGULAN", 68, WHITE, bold=True, glow=CYAN, radius=12), 90, 280, a0)
    paste(im, sprite("Kenapa hy4 jadi pilihan utama.", 30, MUTED), 92, 380, a0)
    for i, ((title, desc, num), y) in enumerate(zip(ADVANTAGES, [450 + i * 205 for i in range(5)])):
        p = ease_out((local - 0.4 - i * 1.6) / 0.8)
        if p <= 0:
            continue
        d.rounded_rectangle([82, y, 998, y + 190], radius=20, fill=(15, 30, 60, int(232 * p)), outline=(58, 96, 160, int(175 * p)), width=2)
        d.ellipse([106, y + 24, 156, y + 74], outline=CYAN + (int(235 * p),), width=3)
        d.line([(120, y + 49), (130, y + 60), (146, y + 37)], fill=CYAN + (int(245 * p),), width=4)
        paste(im, sprite(title, 38, WHITE, bold=True), 180, y + 24, p)
        paste(im, sprite(desc, 27, MUTED), 180, y + 84, p)
        paste(im, sprite(num, 24, DIM, mono=True), 930, y + 30, p)
    return im


def scene_five(local, t):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = W // 2, 760
    appear = ease_out(local / 0.8)
    for rad in (300, 356, 414):
        d.arc([cx - rad, cy - rad, cx + rad, cy + rad], start=t * 20 + rad, end=t * 20 + rad + 160, fill=(45, 130, 200, 45), width=1)
    paste(im, sprite("hy4", 200, WHITE, bold=True, mono=True, glow=CYAN, radius=30), cx, cy, appear, "mm")
    paste(im, sprite("OTAK DARI IT AGENTY — INFINITY", 40, WHITE, bold=True, tracking=2), cx, 1060, ease_out((local - 0.45) / 0.8), "mm")
    cmd = sprite('  $ tom05 "pertanyaan Anda"  ', 30, CYAN, bold=True, mono=True)
    cw, ch = cmd.size
    p = ease_out((local - 1.0) / 0.8)
    d.rounded_rectangle([cx - cw / 2 - 30, 1210, cx + cw / 2 + 30, 1210 + ch + 20], radius=22, fill=(14, 34, 68, 240), outline=(58, 150, 205, 185), width=2)
    paste(im, cmd, cx, 1220, p, "mm")
    paste(im, sprite("Tomi vier  ·  Infinity  ·  2026", 24, DIM), cx, 1400, ease_out((local - 1.6) / 0.8), "mm")
    return im


SCENE_FUNCS = [scene_one, scene_two, scene_three, scene_four, scene_five]


def active_scenes(t):
    result = []
    for i, sc in enumerate(SCENES):
        if sc["start"] - CROSS <= t <= sc["end"] + CROSS:
            local = t - sc["start"]
            w = 1.0
            if sc["start"] - CROSS < t < sc["start"]:
                w = smooth((t - (sc["start"] - CROSS)) / CROSS)
            elif sc["end"] < t < sc["end"] + CROSS:
                w = 1.0 - smooth((t - sc["end"]) / CROSS)
            result.append((i, local, w))
    return result


def draw_caption(frame, t):
    idx = None
    for i, sc in enumerate(SCENES):
        if sc["start"] <= t < sc["end"]:
            idx = i
            break
    if idx is None:
        return
    a = min(smooth((t - SCENES[idx]["start"]) / 0.35), smooth((SCENES[idx]["end"] - t) / 0.35))
    if a <= 0.01:
        return
    d = ImageDraw.Draw(frame)
    sp = sprite(CAPTIONS[idx], 36, WHITE, bold=True)
    x, y = (W - sp.width) / 2 - 30, 1560
    d.rounded_rectangle([x, y, x + sp.width + 60, y + sp.height + 28], radius=22, fill=(6, 14, 32, int(225 * a)), outline=(60, 110, 170, int(120 * a)), width=1)
    paste(frame, sp, W / 2, y + 12, a, "mt")


def draw_hud(frame, t):
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle([80, 118, 118, 156], radius=9, fill=CYAN + (235,))
    paste(frame, sprite("hy", 17, (6, 14, 32), bold=True, mono=True), 99, 137, 1.0, "mm")
    paste(frame, sprite("IT AGENTY", 23, WHITE, bold=True, tracking=1), 136, 120)
    paste(frame, sprite("— INFINITY", 21, CYAN, bold=True), 340, 121)
    paste(frame, sprite("hy4-flash-free", 18, MUTED, mono=True), 1000, 126, 1.0, "rt")
    d.line([(80, 176), (1000, 176)], fill=(70, 115, 180, 90), width=1)
    d.rounded_rectangle([80, 1510, 1000, 1514], radius=2, fill=(60, 95, 150, 80))
    pw = int(920 * clamp(t / DURATION))
    if pw > 4:
        d.rounded_rectangle([80, 1510, 80 + pw, 1514], radius=2, fill=CYAN + (225,))
        d.ellipse([80 + pw - 5, 1505, 80 + pw + 5, 1519], fill=WHITE + (235,))


def render_frame(t):
    frame = BASE.copy()
    draw_particles(frame, t)
    overlays = [(SCENE_FUNCS[i](max(0.0, local), t), w) for i, local, w in active_scenes(t)]
    if overlays:
        total = sum(w for _, w in overlays)
        for overlay, w in overlays:
            alpha = w / total if total else w
            if alpha < 0.999:
                overlay = overlay.copy()
                overlay.putalpha(overlay.getchannel("A").point(lambda a: int(a * alpha)))
            frame.alpha_composite(overlay)
    draw_hud(frame, t)
    draw_caption(frame, t)
    fade = min(smooth(t / 0.5), smooth((DURATION - t) / 0.9))
    if fade < 0.999:
        frame.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - fade)))))
    return frame.convert("RGB")


def synthesize(text, wav):
    mp3 = wav[:-4] + ".mp3"
    try:
        import edge_tts  # noqa: F401
        r1 = subprocess.run(
            ["python3", "-m", "edge_tts", "--voice", "id-ID-GadisNeural",
             "--rate=+5%", "--text", text, "--write-media", mp3],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        r2 = subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", mp3, "-ar", "44100",
             "-ac", "1", "-c:a", "pcm_s16le", wav],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        if r1.returncode == 0 and r2.returncode == 0 and os.path.exists(wav):
            return "edge-tts/id-ID-GadisNeural"
    except Exception:
        pass
    subprocess.run(
        ["espeak-ng", "-v", "id", "-s", "148", "-p", "40", "-a", "185", "-w", wav, text],
        check=True,
    )
    return "espeak-ng/id"


def build_narration():
    os.makedirs(WORK, exist_ok=True)
    wavs = []
    engines = []
    for i, text in enumerate(NARRATION):
        wav = os.path.join(WORK, f"narr{i}.wav")
        engines.append(synthesize(text, wav))
        wavs.append(wav)
    print("   mesin TTS:", ", ".join(engines))
    target = [4.9, 5.7, 9.7, 10.7, 7.5]
    parts = []
    for i, wav in enumerate(wavs):
        raw = subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=nw=1:nk=1", wav,
        ], text=True)
        dur = float(raw.strip())
        tempo = clamp(dur / target[i], 0.72, 1.45)
        delay = int(SCENES[i]["start"] * 1000) + 320
        parts.append(f"[{i}:a]atempo={tempo:.4f},adelay={delay}|{delay}[a{i}]")
    mix = "".join(f"[a{i}]" for i in range(len(parts)))
    voice_filter = ";".join(parts) + ";" + mix + f"amix=inputs={len(parts)}:duration=longest:normalize=0[voice]"
    narration = os.path.join(WORK, "narration.wav")
    cmd = ["ffmpeg", "-y"]
    for wav in wavs:
        cmd += ["-i", wav]
    cmd += [
        "-filter_complex", voice_filter,
        "-map", "[voice]", "-ar", "44100", "-ac", "1", "-t", str(DURATION),
        "-c:a", "pcm_s16le", narration,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return narration


def render_video(narration):
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", narration,
        "-f", "lavfi", "-i", "sine=frequency=110:sample_rate=44100",
        "-f", "lavfi", "-i", "sine=frequency=164.81:sample_rate=44100",
        "-filter_complex",
        "[2:a]volume=0.012[b1];[3:a]volume=0.008[b2];[b1][b2]amix=inputs=2,afade=t=in:st=0:d=2,afade=t=out:st=37:d=3[bed];"
        "[1:a]volume=1.8[voice];[voice][bed]amix=inputs=2:duration=first,volume=1.15,alimiter=limit=0.95[aout]",
        "-map", "0:v:0", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-t", str(DURATION),
        "-metadata", f"title={VIDEO_TITLE}",
        "-metadata", "author=Tomi vier",
        "-metadata", "comment=SPDX-License-Identifier: Tom05ivier-commits-1.0; Copyright (c) 2026 Tomi vier",
        OUT,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        for n in range(TOTAL_FRAMES):
            proc.stdin.write(render_frame(n / FPS).tobytes())
            if n % 200 == 0:
                print(f"  frame {n}/{TOTAL_FRAMES}", flush=True)
        proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "replace")
        if proc.wait() != 0:
            raise RuntimeError(err[-3000:])
    except Exception:
        proc.kill()
        raise


def main():
    global BASE
    print("[1/4] Latar & partikel ...")
    BASE = make_background()
    init_particles()
    print("[2/4] Narasi neural ...")
    narration = build_narration()
    print(f"[3/4] Merender {TOTAL_FRAMES} frame vertikal ...")
    render_video(narration)
    print("[4/4] Poster & verifikasi ...")
    render_frame(3.2).save(POSTER)
    info = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size:stream=index,codec_type,codec_name,width,height",
        "-of", "json", OUT,
    ], text=True)
    print(json.dumps(json.loads(info), indent=2))
    print("SELESAI:", OUT)


if __name__ == "__main__":
    main()
