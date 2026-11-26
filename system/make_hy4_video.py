#!/usr/bin/env python3
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
"""Produksi video perkenalan model hy4 (40 detik, 1280x720, H.264 + AAC).

Konten sepenuhnya dibuat di workspace IT Agenty — Infinity. Narasi Bahasa
Indonesia disintesis dengan suara neural edge-tts (id-ID-GadisNeural), dengan
fallback ke espeak-ng bila jaringan tidak tersedia. Frame digambar dengan
Pillow; ffmpeg menggabungkan keduanya menjadi satu berkas MP4 siap diputar.
"""

import json
import math
import os
import random
import subprocess
import sys
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
FPS = 20
DURATION = 40.0
TOTAL_FRAMES = int(FPS * DURATION)
WORK = "/tmp/opencode/hy4_video_build"
OUT = "/root/workspace/hy4-intro-40s.mp4"
POSTER = "/root/workspace/hy4-intro-poster.png"

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

BG_TOP = (5, 9, 22)
BG_BOTTOM = (11, 24, 52)
CYAN = (59, 224, 239)
BLUE = (92, 133, 255)
RED = (255, 83, 105)
WHITE = (244, 248, 255)
MUTED = (150, 170, 205)
DIM = (103, 124, 163)
PANEL = (13, 26, 53, 236)
PANEL_EDGE = (58, 96, 160, 200)

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
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * f)
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * f)
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * f)
        for x in range(W):
            px[x, y] = (r, g, b)
    base = base.convert("RGBA")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-260, -300, 560, 420], fill=(20, 120, 190, 60))
    gd.ellipse([820, 300, 1560, 1020], fill=(45, 70, 180, 55))
    gd.ellipse([420, 560, 900, 960], fill=(150, 30, 70, 28))
    glow = glow.filter(ImageFilter.GaussianBlur(110))
    base.alpha_composite(glow)
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(grid)
    for x in range(0, W, 48):
        nd.line([(x, 0), (x, H)], fill=(90, 140, 210, 13), width=1)
    for y in range(0, H, 48):
        nd.line([(0, y), (W, y)], fill=(90, 140, 210, 13), width=1)
    base.alpha_composite(grid)
    return base


BASE = None
PARTICLES = []


def init_particles():
    rnd = random.Random(20261120)
    for _ in range(46):
        PARTICLES.append({
            "x": rnd.uniform(0, W),
            "y": rnd.uniform(0, H),
            "r": rnd.uniform(0.8, 2.4),
            "vy": rnd.uniform(4, 16),
            "vx": rnd.uniform(-3, 3),
            "phase": rnd.uniform(0, 6.28),
            "color": rnd.choice([CYAN, BLUE, WHITE]),
        })


def draw_particles(frame, t):
    d = ImageDraw.Draw(frame)
    for p in PARTICLES:
        y = (p["y"] - t * p["vy"]) % H
        x = (p["x"] + t * p["vx"]) % W
        a = int(28 + 42 * (0.5 + 0.5 * math.sin(t * 1.6 + p["phase"])))
        r = p["r"]
        d.ellipse([x - r, y - r, x + r, y + r], fill=p["color"] + (a,))


def scene_one(local, t):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    appear = ease_out(local / 0.9)
    cx, cy = W // 2, H // 2 - 40
    for i, (rad, col, wid) in enumerate([(232, (40, 90, 160, 70), 2), (274, (30, 200, 225, 45), 1)]):
        d.arc([cx - rad, cy - rad, cx + rad, cy + rad], start=t * 26 + i * 120, end=t * 26 + i * 120 + 210, fill=col, width=wid)
    d.ellipse([cx - 196, cy - 196, cx + 196, cy + 196], outline=(60, 200, 235, 38), width=1)
    paste(im, sprite("MEMPERSENALKAN", 22, CYAN, bold=True, tracking=6), cx, 158, appear * 0.95, "mm")
    logo = sprite("hy4", 196, WHITE, bold=True, mono=True, glow=CYAN, radius=26)
    sc = 0.82 + 0.18 * ease_out(local / 1.1)
    paste(im, logo, cx, cy, appear, "mm", sc)
    paste(im, sprite("MODEL AI UNTUK IT AGENTY — INFINITY", 30, WHITE, bold=True, tracking=2), cx, 470, ease_out((local - 0.5) / 0.8), "mm")
    pill = sprite("  opencode/hy4-flash-free  ", 22, CYAN, bold=True, mono=True)
    pw, ph = pill.size
    a = ease_out((local - 1.0) / 0.8)
    d.rounded_rectangle([cx - pw / 2 - 22, 540 - 10, cx + pw / 2 + 22, 540 + ph], radius=20, fill=(16, 38, 72, 230), outline=(60, 160, 210, 170), width=1)
    paste(im, pill, cx, 540, a, "mm")
    return im


def scene_two(local, t):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    a0 = ease_out(local / 0.6)
    paste(im, sprite("APA ITU hy4?", 66, WHITE, bold=True, glow=CYAN, radius=12), 78, 72, a0)
    d.rounded_rectangle([82, 198, 214, 204], radius=3, fill=CYAN + (int(210 * a0),))
    paste(im, sprite("Ringan. Cepat. Terintegrasi.", 27, MUTED), 80, 218, a0)
    items = [
        "Model AI default di OpenCode",
        "Ringan & gratis — flash-free",
        "Berjalan langsung di workspace Anda",
        "Konteks penuh lewat AGENTS.md",
    ]
    for i, item in enumerate(items):
        p = ease_out((local - 0.55 - i * 0.55) / 0.55)
        if p <= 0:
            continue
        y = 300 + i * 78
        d.rounded_rectangle([84, y + 4, 100, y + 20], radius=3, fill=CYAN + (int(220 * p),))
        paste(im, sprite(item, 27, WHITE, bold=True), 122, y - 4, p)
        d.line([(122, y + 40), (630, y + 40)], fill=(60, 100, 160, int(70 * p)), width=1)
    # Panel terminal
    p = ease_out((local - 1.0) / 0.7)
    if p > 0:
        x1, y1, x2, y2 = 700, 232, 1204, 566
        d.rounded_rectangle([x1, y1, x2, y2], radius=16, fill=PANEL, outline=PANEL_EDGE, width=2)
        d.rounded_rectangle([x1, y1, x2, y1 + 42], radius=16, fill=(20, 40, 78, 240))
        d.rectangle([x1, y1 + 24, x2, y1 + 42], fill=(20, 40, 78, 240))
        for i, col in enumerate([RED, (255, 195, 90), CYAN]):
            d.ellipse([x1 + 18 + i * 22, y1 + 15, x1 + 30 + i * 22, y1 + 27], fill=col + (230,))
        paste(im, sprite("terminal — hy4", 15, MUTED, mono=True), x1 + 100, y1 + 12, p)
        lines = [
            ('$ tom05 "lindungi hardware"', WHITE),
            ("> Memuat AGENTS.md .......... OK", CYAN),
            ("> Model: hy4-flash-free ..... OK", CYAN),
            ("> Agen aktif: build, security", MUTED),
            ("> Siap. Ada yang bisa dibantu?", WHITE),
        ]
        for i, (line, col) in enumerate(lines):
            q = ease_out((local - 1.25 - i * 0.42) / 0.45)
            paste(im, sprite(line, 18, col, mono=True), x1 + 26, y1 + 62 + i * 40, q)
        d.rectangle([x1 + 26, y1 + 284, x1 + 40, y1 + 300], fill=CYAN + (int(180 + 60 * math.sin(t * 5)),))
    return im


CAPABILITIES = [
    ("01", "Berpikir & Menulis Kode", "build agent: dari ide menjadi implementasi"),
    ("02", "Eksplorasi Codebase", "explore agent: memahami struktur & dependensi"),
    ("03", "Keamanan & SOC", "security agent: deteksi, karantina, audit"),
    ("04", "Platform Engineering", "platform agent: CLI, infrastruktur, otomasi"),
    ("05", "Riset & Penjelasan", "professor: dokumentasi & troubleshooting"),
]


def scene_three(local, t):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    a0 = ease_out(local / 0.6)
    paste(im, sprite("KEMAMPUAN", 64, WHITE, bold=True, glow=BLUE, radius=12), 78, 72, a0)
    paste(im, sprite("Lima peran dalam satu model.", 26, MUTED), 82, 218, a0)
    positions = [(78, 258), (463, 258), (848, 258), (270, 458), (655, 458)]
    cw, ch = 354, 190
    for i, ((num, title, desc), (x, y)) in enumerate(zip(CAPABILITIES, positions)):
        p = ease_out((local - 0.45 - i * 0.9) / 0.7)
        if p <= 0:
            continue
        yy = y + int((1 - p) * 26)
        shadow = int(40 * p)
        d.rounded_rectangle([x + 3, yy + 5, x + cw + 3, yy + ch + 5], radius=16, fill=(0, 0, 0, shadow))
        d.rounded_rectangle([x, yy, x + cw, yy + ch], radius=16, fill=(15, 30, 60, int(232 * p)), outline=(58, 96, 160, int(190 * p)), width=2)
        d.rounded_rectangle([x, yy + 20, x + 5, yy + ch - 20], radius=3, fill=CYAN + (int(230 * p),))
        paste(im, sprite(num, 20, CYAN, bold=True, mono=True), x + 24, yy + 22, p)
        paste(im, sprite(title, 23, WHITE, bold=True), x + 24, yy + 60, p)
        for j, part in enumerate(wrap_text(desc, 17, 300)):
            paste(im, sprite(part, 17, MUTED), x + 24, yy + 110 + j * 28, p * 0.95)
    return im


ADVANTAGES = [
    ("Gratis & ringan", "Model flash-free tanpa biaya, respons cepat.", "01"),
    ("Konteks workspace penuh", "Membaca AGENTS.md sebagai panduan kerja.", "02"),
    ("10 agent + 10 command", "Sinkron otomatis ke Copilot CLI.", "03"),
    ("Ekosistem CLI siap pakai", "gh, kubectl, terraform, tofu, doctor.", "04"),
    ("Privasi & lisensi aman", "Tom05ivier-commits-1.0, data disamarkan.", "05"),
]


def scene_four(local, t):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    a0 = ease_out(local / 0.6)
    paste(im, sprite("KEUNGGULAN", 64, WHITE, bold=True, glow=CYAN, radius=12), 78, 72, a0)
    paste(im, sprite("Kenapa hy4 jadi pilihan utama.", 26, MUTED), 82, 218, a0)
    for i, ((title, desc, num), y) in enumerate(zip(ADVANTAGES, [264, 346, 428, 510, 592])):
        p = ease_out((local - 0.4 - i * 0.85) / 0.7)
        if p <= 0:
            continue
        xt = 84 + int((1 - p) * 30)
        d.ellipse([xt, y + 2, xt + 34, y + 36], outline=CYAN + (int(230 * p),), width=2)
        d.line([(xt + 10, y + 19), (xt + 16, y + 26), (xt + 26, y + 11)], fill=CYAN + (int(240 * p),), width=3)
        paste(im, sprite(num, 16, DIM, mono=True), xt + 48, y - 6, p)
        paste(im, sprite(title, 29, WHITE, bold=True), xt + 48, y + 14, p)
        paste(im, sprite(desc, 19, MUTED), xt + 600, y + 20, p)
        d.line([(xt + 48, y + 62), (1200, y + 62)], fill=(60, 100, 160, int(55 * p)), width=1)
    return im


def scene_five(local, t):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = W // 2
    appear = ease_out(local / 0.8)
    for rad in (200, 244, 292):
        d.arc([cx - rad, 300 - rad, cx + rad, 300 + rad], start=t * 20 + rad, end=t * 20 + rad + 160, fill=(45, 130, 200, 45), width=1)
    paste(im, sprite("hy4", 172, WHITE, bold=True, mono=True, glow=CYAN, radius=30), cx, 300, appear, "mm")
    paste(im, sprite("OTAK DARI IT AGENTY — INFINITY", 34, WHITE, bold=True, tracking=3), cx, 448, ease_out((local - 0.45) / 0.8), "mm")
    cmd = sprite('  $ tom05 "pertanyaan Anda"  ', 24, CYAN, bold=True, mono=True)
    cw, ch = cmd.size
    p = ease_out((local - 1.0) / 0.8)
    d.rounded_rectangle([cx - cw / 2 - 26, 524, cx + cw / 2 + 26, 524 + ch + 16], radius=18, fill=(14, 34, 68, 235), outline=(58, 150, 205, 170), width=1)
    paste(im, cmd, cx, 532, p, "mm")
    paste(im, sprite("Tomi vier  ·  Infinity  ·  2026", 18, DIM), cx, 640, ease_out((local - 1.6) / 0.8), "mm")
    return im


SCENE_FUNCS = [scene_one, scene_two, scene_three, scene_four, scene_five]


def active_scenes(t):
    result = []
    for i, sc in enumerate(SCENES):
        if sc["start"] - CROSS <= t <= sc["end"] + CROSS:
            local = t - sc["start"]
            weight = 1.0
            if t < sc["start"] and t > sc["start"] - CROSS:
                weight = smooth((t - (sc["start"] - CROSS)) / CROSS)
            elif t > sc["end"] and t < sc["end"] + CROSS:
                weight = 1.0 - smooth((t - sc["end"]) / CROSS)
            result.append((i, local, weight))
    return result


def draw_hud(frame, t):
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle([48, 17, 76, 45], radius=8, fill=CYAN + (235,))
    paste(frame, sprite("hy", 14, (6, 14, 32), bold=True, mono=True), 62, 31, 1.0, "mm")
    paste(frame, sprite("IT AGENTY", 18, WHITE, bold=True, tracking=1), 88, 18)
    paste(frame, sprite("— INFINITY", 17, CYAN, bold=True), 248, 19)
    paste(frame, sprite("MODEL · hy4-flash-free", 16, MUTED, mono=True), 1232, 21, 1.0, "rt")
    d.line([(48, 56), (1232, 56)], fill=(70, 115, 180, 95), width=1)
    # Progress bar
    d.rounded_rectangle([48, H - 30, 1232, H - 27], radius=2, fill=(60, 95, 150, 80))
    pw = int((1232 - 48) * clamp(t / DURATION))
    if pw > 4:
        d.rounded_rectangle([48, H - 30, 48 + pw, H - 27], radius=2, fill=CYAN + (220,))
        d.ellipse([48 + pw - 4, H - 34, 48 + pw + 4, H - 26], fill=WHITE + (230,))
    paste(frame, sprite("40s", 14, DIM, mono=True), 1232, H - 46, 1.0, "rb")


def render_frame(t):
    frame = BASE.copy()
    draw_particles(frame, t)
    active = active_scenes(t)
    if active:
        overlays = [(SCENE_FUNCS[i](max(0.0, local), t), w) for i, local, w in active]
        total = sum(w for _, w in overlays)
        for overlay, w in overlays:
            alpha = w / total if total else w
            if alpha < 0.999:
                overlay = overlay.copy()
                overlay.putalpha(overlay.getchannel("A").point(lambda a: int(a * alpha)))
            frame.alpha_composite(overlay)
    draw_hud(frame, t)
    fade = min(smooth(t / 0.5), smooth((DURATION - t) / 0.9))
    if fade < 0.999:
        black = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - fade))))
        frame.alpha_composite(black)
    return frame.convert("RGB")


def synthesize(text, wav):
    """Suara neural edge-tts; jatuh ke espeak-ng bila tidak tersedia."""
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
    mix_names = "".join(f"[a{i}]" for i in range(len(parts)))
    voice_filter = ";".join(parts) + ";" + mix_names + f"amix=inputs={len(parts)}:duration=longest:normalize=0[voice]"
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
        "-metadata", "title=Memperkenalkan hy4 — IT Agenty Infinity",
        "-metadata", "author=Tomi vier",
        "-metadata", "comment=SPDX-License-Identifier: Tom05ivier-commits-1.0; Copyright (c) 2026 Tomi vier",
        OUT,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    try:
        for n in range(TOTAL_FRAMES):
            frame = render_frame(n / FPS)
            proc.stdin.write(frame.tobytes())
            if n % 100 == 0:
                print(f"  frame {n}/{TOTAL_FRAMES}", flush=True)
        proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "replace")
        rc = proc.wait()
        if rc != 0:
            raise RuntimeError(err[-3000:])
    except Exception:
        proc.kill()
        raise


def main():
    global BASE
    print("[1/4] Menyiapkan latar & partikel ...")
    BASE = make_background()
    init_particles()
    print("[2/4] Membuat narasi Bahasa Indonesia ...")
    narration = build_narration()
    print("[3/4] Merender 800 frame animasi ...")
    render_video(narration)
    print("[4/4] Membuat poster & memverifikasi ...")
    render_frame(3.2).save(POSTER)
    info = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size:stream=index,codec_type,codec_name,width,height,r_frame_rate",
        "-of", "json", OUT,
    ], text=True)
    print(json.dumps(json.loads(info), indent=2))
    print("SELESAI:", OUT)


if __name__ == "__main__":
    main()
