#!/usr/bin/env python3
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
"""Tutorial 40 detik (9:16) membuat video dengan hy4.

Lima langkah: prompt -> skrip -> jalankan -> ambil MP4 -> unggah.
Menggunakan ulang mesin render dari make_hy4_short.py agar konsisten.
"""

import os
import subprocess
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_hy4_short as base  # noqa: E402

W, H = 1080, 1920
FPS, DURATION = 24, 40.0
SCENE_LEN = 8.0

base.W, base.H = W, H
base.FPS, base.DURATION = FPS, DURATION
base.TOTAL_FRAMES = int(FPS * DURATION)
base.SCENES = [{"start": i * SCENE_LEN, "end": (i + 1) * SCENE_LEN} for i in range(5)]
base.CROSS = 0.5
base.OUT = "/root/workspace/hy4-tutorial-9x16.mp4"
base.POSTER = "/root/workspace/hy4-tutorial-poster.png"
base.VIDEO_TITLE = "Tutorial membuat video dengan hy4 — IT Agenty Infinity"
base.WORK = "/tmp/opencode/hy4_tutorial_build"

base.NARRATION = [
    "Bikin video pakai hy4? Ikuti lima langkah singkat ini.",
    "Pertama, kirim prompt. Sebutkan topik, durasi, dan gaya video.",
    "Kedua, hy4 menulis skrip untuk gambar, suara, dan video.",
    "Ketiga, jalankan satu perintah. hy4 merender seluruh frame dan audio.",
    "Keempat, ambil berkas M P4-nya. Kelima, unggah ke TikTok atau YouTube Shorts.",
]

base.CAPTIONS = [
    "Bikin video pakai hy4? 5 langkah!",
    "1. Kirim prompt: topik + durasi + gaya",
    "2. hy4 menulis skrip produksi",
    "3. Jalankan satu perintah",
    "4-5. Ambil MP4, unggah, selesai",
]

sprite = base.sprite
paste = base.paste
ease_out = base.ease_out
smooth = base.smooth
CYAN, BLUE, RED = base.CYAN, base.BLUE, base.RED
WHITE, MUTED, DIM = base.WHITE, base.MUTED, base.DIM
PANEL, PANEL_EDGE = base.PANEL, base.PANEL_EDGE


def header(im, step, title, subtitle, local):
    d = ImageDraw.Draw(im)
    a = ease_out(local / 0.6)
    bw = 250
    d.rounded_rectangle([90, 268, 90 + bw, 330], radius=20, fill=CYAN + (int(235 * a),))
    paste(im, sprite(step, 24, (6, 14, 32), bold=True), 90 + bw / 2, 299, a, "mm")
    paste(im, sprite(title, 56, WHITE, bold=True, glow=CYAN, radius=10), 90, 356, a)
    paste(im, sprite(subtitle, 30, MUTED), 92, 448, ease_out((local - 0.25) / 0.6))
    return a


def panel(im, y1, y2, label, local, delay=0.6):
    d = ImageDraw.Draw(im)
    p = ease_out((local - delay) / 0.7)
    if p <= 0:
        return 0.0
    d.rounded_rectangle([80, y1, 1000, y2], radius=24, fill=(10, 22, 46, int(242 * p)), outline=(58, 96, 160, int(200 * p)), width=2)
    d.rounded_rectangle([80, y1, 1000, y1 + 56], radius=24, fill=(20, 40, 78, 245))
    d.rectangle([80, y1 + 30, 1000, y1 + 56], fill=(20, 40, 78, 245))
    for i, col in enumerate([RED, (255, 195, 90), CYAN]):
        d.ellipse([104 + i * 28, y1 + 20, 120 + i * 28, y1 + 36], fill=col + (235,))
    paste(im, sprite(label, 20, MUTED, mono=True), 210, y1 + 17, p)
    return p


def lines(im, items, x, y, size, gap, local, start, step=0.45):
    for i, (text, color) in enumerate(items):
        q = ease_out((local - start - i * step) / 0.45)
        paste(im, sprite(text, size, color, mono=True), x, y + i * gap, q)


def step_one(local, t):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = W // 2
    a = ease_out(local / 0.8)
    d.ellipse([cx - 250, 1000 - 250, cx + 250, 1000 + 250], outline=(45, 180, 215, 55), width=2)
    d.ellipse([cx - 310, 1000 - 310, cx + 310, 1000 + 310], outline=(45, 120, 200, 30), width=1)
    paste(im, sprite("TUTORIAL", 26, CYAN, bold=True, tracking=6), cx, 540, a, "mm")
    paste(im, sprite("BUAT VIDEO", 78, WHITE, bold=True), cx, 660, a, "mm")
    paste(im, sprite("DENGAN hy4", 100, WHITE, bold=True, mono=True, glow=CYAN, radius=22), cx, 780, ease_out((local - 0.3) / 0.8), "mm")
    paste(im, sprite("Dari ide jadi MP4 dalam 5 langkah", 36, MUTED), cx, 1300, ease_out((local - 0.8) / 0.8), "mm")
    # Tombol play
    pc = ease_out((local - 1.2) / 0.6)
    if pc > 0:
        r = 56 + int(4 * math_sin(t * 4))
        d.ellipse([cx - r, 1400 - r, cx + r, 1400 + r], fill=CYAN + (int(225 * pc),))
        d.polygon([(cx - 12, 1376), (cx - 12, 1424), (cx + 22, 1400)], fill=(6, 14, 32, int(245 * pc)))
    return im


def math_sin(x):
    import math
    return math.sin(x)


def step_two(local, t):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    header(im, "LANGKAH 1", "Kirim prompt ke hy4", "Sebutkan topik, durasi, dan gaya.", local)
    p = panel(im, 540, 1160, "PROMPT", local)
    if p > 0:
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([112, 624, 968, 1110], radius=16, fill=(7, 17, 38, 235), outline=(45, 80, 140, 140), width=1)
        lines(im, [
            ('hy4 "buat video 40 detik', WHITE),
            ('tentang cara pakai hy4,', WHITE),
            ('gaya tutorial, vertikal 9:16"', CYAN),
        ], 140, 680, 32, 62, local, 1.0, 0.6)
        q = ease_out((local - 3.2) / 0.5)
        paste(im, sprite("→ hy4 memahami maksud Anda", 26, MUTED), 140, 950, q)
        d.rectangle([140, 1010, 148, 1044], fill=CYAN + (int(200 + 55 * math_sin(t * 5)),))
    return im


def step_three(local, t):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    header(im, "LANGKAH 2", "hy4 menulis skrip", "Otomatis: gambar + narasi + video.", local)
    p = panel(im, 540, 1240, "make_video.py", local)
    if p > 0:
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([112, 624, 968, 1200], radius=16, fill=(7, 17, 38, 235), outline=(45, 80, 140, 140), width=1)
        lines(im, [
            ("from PIL import Image", CYAN),
            ("import edge_tts, subprocess", CYAN),
            ("", MUTED),
            ("frame  = render_frame(t)", WHITE),
            ("suara = tts(narasi)", WHITE),
            ("video = ffmpeg(frame, suara)", WHITE),
            ("# hasil: output.mp4", DIM),
        ], 140, 672, 27, 66, local, 0.95, 0.5)
    return im


def step_four(local, t):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    header(im, "LANGKAH 3", "Jalankan satu perintah", "hy4 merender frame dan audio.", local)
    p = panel(im, 540, 1240, "terminal", local)
    if p > 0:
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([112, 624, 968, 1200], radius=16, fill=(7, 17, 38, 235), outline=(45, 80, 140, 140), width=1)
        lines(im, [
            ("$ python3 make_video.py", WHITE),
            ("[1/4] Narasi neural ...... OK", CYAN),
            ("[2/4] Render 960 frame ... OK", CYAN),
            ("[3/4] Audio + video ...... OK", CYAN),
            ("SELESAI: video.mp4", WHITE),
        ], 140, 680, 27, 78, local, 1.0, 0.62)
        q = ease_out((local - 4.0) / 0.6)
        d.rounded_rectangle([140, 1120, 940, 1130], radius=4, fill=(60, 95, 150, 90))
        pw = int(800 * clamp01((local - 4.0) / 2.2))
        if pw > 4:
            d.rounded_rectangle([140, 1120, 140 + pw, 1130], radius=4, fill=CYAN + (230,))
        paste(im, sprite("100%", 22, CYAN, mono=True), 940, 1090, q, "rt")
    return im


def clamp01(v):
    return max(0.0, min(1.0, v))


def step_five(local, t):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    header(im, "LANGKAH 4 & 5", "Ambil MP4, lalu unggah", "TikTok • YouTube Shorts • feed", local)
    d = ImageDraw.Draw(im)
    a = ease_out((local - 0.5) / 0.7)
    cx = W // 2
    d.rounded_rectangle([180, 600, 900, 1000], radius=30, fill=(12, 30, 62, int(240 * a)), outline=(58, 150, 205, int(190 * a)), width=2)
    d.rounded_rectangle([cx - 56, 690, cx + 56, 762], radius=14, fill=CYAN + (int(235 * a),))
    d.polygon([(cx - 12, 700), (cx - 12, 752), (cx + 24, 726)], fill=(6, 14, 32, int(245 * a)))
    paste(im, sprite("video.mp4", 46, WHITE, bold=True, mono=True), cx, 820, a, "mm")
    paste(im, sprite("Siap diputar", 30, CYAN, bold=True), cx, 1060, ease_out((local - 1.2) / 0.6), "mm")
    paste(im, sprite("Siap diunggah", 30, CYAN, bold=True), cx, 1140, ease_out((local - 1.8) / 0.6), "mm")
    paste(im, sprite("hy4 — IT Agenty Infinity", 26, DIM), cx, 1350, ease_out((local - 2.4) / 0.8), "mm")
    return im


base.SCENE_FUNCS = [step_one, step_two, step_three, step_four, step_five]


def build_narration():
    base.os.makedirs(base.WORK, exist_ok=True)
    wavs, engines = [], []
    for i, text in enumerate(base.NARRATION):
        wav = os.path.join(base.WORK, f"narr{i}.wav")
        engines.append(base.synthesize(text, wav))
        wavs.append(wav)
    print("   mesin TTS:", ", ".join(engines))
    parts = []
    for i, wav in enumerate(wavs):
        dur = float(subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=nw=1:nk=1", wav,
        ], text=True).strip())
        tempo = base.clamp(dur / 7.2, 0.72, 1.45)
        delay = int(base.SCENES[i]["start"] * 1000) + 320
        parts.append(f"[{i}:a]atempo={tempo:.4f},adelay={delay}|{delay}[a{i}]")
    mix = "".join(f"[a{i}]" for i in range(len(parts)))
    filt = ";".join(parts) + ";" + mix + f"amix=inputs={len(parts)}:duration=longest:normalize=0[voice]"
    narration = os.path.join(base.WORK, "narration.wav")
    cmd = ["ffmpeg", "-y"]
    for wav in wavs:
        cmd += ["-i", wav]
    cmd += [
        "-filter_complex", filt,
        "-map", "[voice]", "-ar", "44100", "-ac", "1", "-t", str(DURATION),
        "-c:a", "pcm_s16le", narration,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return narration


base.build_narration = build_narration


if __name__ == "__main__":
    base.main()
