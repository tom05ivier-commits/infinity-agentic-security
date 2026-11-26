#!/usr/bin/env python3
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
"""Generator video TikTok: kucing joget 40 detik, 9:16, + beat sintesis.

Bukan model neural / bukan generasi AI: semua frame digambar secara prosedural
dengan PIL dan audio disintesis dengan numpy. Output: MP4 H.264 + AAC.
"""

from __future__ import annotations

import math
import subprocess
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "tiktok-kucing-joget.mp4"
WAV = Path("/tmp/tom05_chao_beat.wav")

FPS = 24
DUR = 40
W, H = 720, 1280
TOTAL = FPS * DUR
BPM = 124
SPB = 60.0 / BPM
SR = 44100


def font(size: int):
    for p in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ):
        if Path(p).is_file():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


F_TITLE = font(74)
F_SUB = font(34)
F_SMALL = font(24)


def make_audio() -> None:
    rng = np.random.default_rng(20261123)
    n = SR * DUR
    t = np.arange(n) / SR
    audio = np.zeros(n, dtype=np.float64)

    beats = int(DUR / SPB)
    # Kick: swept sine, decay tiap beat.
    for b in range(beats):
        s = int(b * SPB * SR)
        L = min(int(0.30 * SR), n - s)
        if L <= 0:
            break
        x = np.arange(L) / SR
        freq = 145 * np.exp(-x * 26) + 47
        kick = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-x * 13)
        audio[s:s + L] += kick * 0.95

    # Snare/clap di beat 2 dan 4.
    for b in range(1, beats, 2):
        s = int(b * SPB * SR)
        L = min(int(0.16 * SR), n - s)
        if L <= 0:
            break
        x = np.arange(L) / SR
        noise = rng.normal(0, 1, L)
        tone = np.sin(2 * np.pi * 190 * x)
        env = np.exp(-x * 26)
        audio[s:s + L] += (noise * 0.5 + tone * 0.35) * env * 0.55

    # Hi-hat tiap setengah beat.
    half = int(DUR / (SPB / 2))
    for h in range(half):
        s = int(h * SPB / 2 * SR)
        L = min(int(0.055 * SR), n - s)
        if L <= 0:
            break
        x = np.arange(L) / SR
        audio[s:s + L] += rng.normal(0, 1, L) * np.exp(-x * 70) * 0.10

    # Bassline pentatonik sederhana.
    seq = [55.00, 55.00, 65.41, 73.42, 82.41, 73.42, 65.41, 61.74]
    for i in range(int(DUR / SPB)):
        s = int(i * SPB * SR)
        L = min(int(SPB * 0.85 * SR), n - s)
        if L <= 0:
            break
        x = np.arange(L) / SR
        f = seq[i % len(seq)]
        bass = (np.sin(2 * np.pi * f * x) + 0.35 * np.sin(4 * np.pi * f * x))
        audio[s:s + L] += bass * np.exp(-x * 3.2) * 0.20

    # Melodi pluck di atasnya.
    mel = [440.0, 523.25, 587.33, 523.25, 659.25, 587.33, 493.88, 523.25]
    for i in range(int(DUR / (SPB / 2))):
        s = int(i * SPB / 2 * SR)
        L = min(int(SPB * 0.42 * SR), n - s)
        if L <= 0:
            break
        x = np.arange(L) / SR
        f = mel[i % len(mel)]
        pluck = np.sin(2 * np.pi * f * x) + 0.25 * np.sin(6 * np.pi * f * x)
        audio[s:s + L] += pluck * np.exp(-x * 9) * 0.085

    peak = float(np.max(np.abs(audio))) or 1.0
    audio = audio / peak * 0.88
    stereo = np.repeat(audio[:, None], 2, axis=1)
    pcm = (np.clip(stereo, -1, 1) * 32767).astype("<i2").tobytes()
    with wave.open(str(WAV), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm)


def star(draw, cx, cy, r, fill):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    draw.polygon(pts, fill=fill)


def draw_cat(d, cx, cy, t, beat_phase):
    sway = math.sin(2 * math.pi * t / (SPB * 2)) * 26
    bounce = abs(math.sin(math.pi * t / SPB)) * 22
    x = cx + sway
    y = cy - bounce
    orange = (247, 150, 54)
    dark = (198, 99, 28)
    cream = (255, 224, 170)
    pink = (255, 138, 156)

    # Bayangan
    d.ellipse([x - 120, cy + 150, x + 120, cy + 186], fill=(90, 40, 90, 70))

    # Ekor (menggoyang)
    tail = []
    for i in range(13):
        a = -0.5 + i * 0.19 + math.sin(2 * math.pi * t / SPB + i * 0.55) * 0.30
        tail.append((x + 72 + i * 13, y + 60 - math.sin(a) * 95))
    d.line(tail, fill=dark, width=20, joint="curve")
    d.line(tail, fill=orange, width=13, joint="curve")

    # Kaki belakang
    d.ellipse([x - 78, y + 96, x - 18, y + 168], fill=dark)
    d.ellipse([x + 18, y + 96, x + 78, y + 168], fill=dark)
    # Badan
    d.ellipse([x - 92, y - 20, x + 92, y + 140], fill=orange, outline=dark, width=5)
    for i in range(3):
        d.arc([x - 88 + i * 8, y + 4 + i * 27, x + 88 - i * 8, y + 60 + i * 27],
              200, 340, fill=dark, width=7)
    d.ellipse([x - 56, y + 42, x + 56, y + 116], fill=cream)

    # Kaki depan: naik-turun bergantian mengikuti beat
    lift = math.sin(2 * math.pi * t / SPB) * 34
    for side, off in ((-1, lift), (1, -lift)):
        px = x + side * 52
        py = y + 40 - max(0, off)
        d.line([px, y + 10, px + side * 10, py + 40], fill=orange, width=22)
        d.ellipse([px + side * 10 - 18, py + 28, px + side * 10 + 18, py + 60], fill=cream)

    # Kepala
    hy = y - 96
    d.ellipse([x - 100, hy - 82, x + 100, hy + 86], fill=orange, outline=dark, width=5)
    # Telinga
    d.polygon([(x - 88, hy - 48), (x - 64, hy - 124), (x - 18, hy - 70)], fill=orange)
    d.polygon([(x + 88, hy - 48), (x + 64, hy - 124), (x + 18, hy - 70)], fill=orange)
    d.polygon([(x - 76, hy - 56), (x - 62, hy - 104), (x - 34, hy - 68)], fill=pink)
    d.polygon([(x + 76, hy - 56), (x + 62, hy - 104), (x + 34, hy - 68)], fill=pink)

    # Mata (berkedip tiap 8 beat)
    blink = (int(t / SPB) % 8 == 7) and beat_phase < 0.25
    for side in (-1, 1):
        ex = x + side * 40
        if blink:
            d.line([ex - 20, hy - 4, ex + 20, hy - 4], fill=(40, 30, 40), width=6)
        else:
            d.ellipse([ex - 23, hy - 28, ex + 23, hy + 18], fill=(255, 255, 255))
            d.ellipse([ex - 10, hy - 18, ex + 10, hy + 10], fill=(35, 30, 45))
            d.ellipse([ex - 5, hy - 14, ex + 1, hy - 7], fill=(255, 255, 255))

    # Pipi, hidung, mulut, kumis
    d.ellipse([x - 76, hy + 14, x - 46, hy + 38], fill=(255, 170, 170))
    d.ellipse([x + 46, hy + 14, x + 76, hy + 38], fill=(255, 170, 170))
    d.polygon([(x - 11, hy + 16), (x + 11, hy + 16), (x, hy + 31)], fill=pink)
    d.arc([x - 24, hy + 20, x, hy + 48], 10, 170, fill=(60, 40, 50), width=4)
    d.arc([x, hy + 20, x + 24, hy + 48], 10, 170, fill=(60, 40, 50), width=4)
    for side in (-1, 1):
        for k in (-1, 0, 1):
            d.line([x + side * 26, hy + 24 + k * 2,
                    x + side * 96, hy + 12 + k * 16], fill=(255, 245, 230), width=3)


def render_frame(frame_idx: int) -> Image.Image:
    t = frame_idx / FPS
    beat = int(t / SPB)
    phase = (t % SPB) / SPB
    pulse = 1.0 + 0.10 * (1.0 - phase) ** 3

    yy = np.linspace(0, 1, H)[:, None]
    top = np.array([92, 26, 132])
    mid = np.array([214, 46, 126])
    bot = np.array([255, 140, 74])
    grad = np.where(yy < 0.55,
                    top[None, :] * (1 - yy / 0.55) + mid[None, :] * (yy / 0.55),
                    mid[None, :] * (1 - (yy - 0.55) / 0.45) + bot[None, :] * ((yy - 0.55) / 0.45))
    grad = np.clip(grad * pulse, 0, 255).astype(np.uint8)
    img = Image.fromarray(np.broadcast_to(grad[:, None, :], (H, W, 3)).copy(), "RGB")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    # Bokeh berjalan naik
    for i in range(16):
        bx = (i * 131 + int(t * (28 + i % 5 * 12))) % (W + 120) - 60
        by = H - ((i * 97 + int(t * (60 + i % 7 * 18))) % (H + 200))
        r = 14 + (i % 5) * 9
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=(255, 255, 255, 26))

    # Lantai
    d.rectangle([0, H - 250, W, H], fill=(60, 18, 74, 120))
    d.line([0, H - 250, W, H - 250], fill=(255, 220, 150, 160), width=5)

    draw_cat(d, W // 2, H - 430, t, phase)

    # Sparkle tiap beat
    if phase < 0.30:
        rr = int((1 - phase / 0.30) * 46) + 10
        for i in range(5):
            sx = 90 + (i * 143 + beat * 71) % (W - 180)
            sy = 220 + (i * 211 + beat * 53) % 620
            star(d, sx, sy, rr, (255, 246, 170, 230))
            star(d, sx, sy, rr * 0.45, (255, 255, 255, 255))

    # Not musik melayang
    for i in range(7):
        nx = 70 + (i * 157 + int(t * 40)) % (W - 140)
        ny = H - 120 - ((i * 173 + int(t * 90)) % 900)
        d.ellipse([nx - 9, ny + 8, nx + 7, ny + 22], fill=(255, 255, 255, 170))
        d.line([nx + 7, ny + 20, nx + 7, ny - 18], fill=(255, 255, 255, 170), width=5)
        d.line([nx + 7, ny - 18, nx + 26, ny - 10], fill=(255, 255, 255, 170), width=5)

    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    td = ImageDraw.Draw(img)

    # Judul & caption
    title = "CHAO MANIA"
    tw = td.textbbox((0, 0), title, font=F_TITLE)[2]
    td.text(((W - tw) / 2 + 4, 92), title, font=F_TITLE, fill=(70, 20, 80))
    td.text(((W - tw) / 2, 88), title, font=F_TITLE, fill=(255, 250, 210))
    cap = "KUCING JOGET  ·  40 DETIK"
    cw = td.textbbox((0, 0), cap, font=F_SUB)[2]
    td.text(((W - cw) / 2, 176), cap, font=F_SUB, fill=(255, 255, 255))

    # Progress bar
    prog = int(W * (frame_idx + 1) / TOTAL)
    td.rounded_rectangle([40, H - 54, W - 40, H - 38], radius=8, fill=(255, 255, 255, 90))
    td.rounded_rectangle([40, H - 54, 40 + prog, H - 38], radius=8, fill=(255, 246, 170))
    return img


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print("[1/2] Sintesis audio beat ...", flush=True)
    make_audio()
    print("[2/2] Render 960 frame + encode MP4 ...", flush=True)
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-",
        "-i", str(WAV),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
        "-shortest", "-movflags", "+faststart", str(OUT),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        for i in range(TOTAL):
            proc.stdin.write(render_frame(i).tobytes())
            if i % 240 == 0:
                print(f"  frame {i}/{TOTAL}", flush=True)
        proc.stdin.close()
    except Exception:
        proc.kill()
        raise
    rc = proc.wait()
    if rc != 0:
        raise SystemExit(f"ffmpeg gagal: kode {rc}")
    print(f"SELESAI: {OUT} ({OUT.stat().st_size / 1e6:.1f} MB)", flush=True)


if __name__ == "__main__":
    main()
