#!/usr/bin/env python3
# SPDX-License-Identifier: Tom05ivier-commits-1.0
# Copyright (c) 2026 Tomi vier
# Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
"""Buat latar musik ambient korporat sederhana (tanpa aset pihak ketiga)."""
import argparse
import math
import struct
import wave

SR = 22050
CHORDS = [
    (220.00, 261.63, 329.63),  # Am
    (174.61, 220.00, 261.63),  # F
    (261.63, 329.63, 392.00),  # C
    (196.00, 246.94, 293.66),  # G
]
CHORD_LEN = 4.0


def envelope(t, length):
    fade = min(1.4, length / 3)
    if t < fade:
        return 0.5 - 0.5 * math.cos(math.pi * t / fade)
    if t > length - fade:
        return 0.5 - 0.5 * math.cos(math.pi * (length - t) / fade)
    return 1.0


def sample(t, chord_index, local_t, length):
    f1, f2, f3 = CHORDS[chord_index]
    env = envelope(local_t, length)
    # Pad: fundamental + harmonic lembut, shimmer lambat, bass root.
    v = (
        0.42 * math.sin(2 * math.pi * f1 * t)
        + 0.30 * math.sin(2 * math.pi * f2 * t + 0.6)
        + 0.24 * math.sin(2 * math.pi * f3 * t + 1.2)
        + 0.10 * math.sin(2 * math.pi * f1 * 2 * t)
        + 0.07 * math.sin(2 * math.pi * f3 * 0.5 * t)
    )
    shimmer = 0.05 * math.sin(2 * math.pi * 0.25 * t)
    return v * env * (0.85 + shimmer)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--duration', type=float, required=True)
    p.add_argument('--output', required=True)
    a = p.parse_args()

    total = int(a.duration * SR)
    with wave.open(a.output, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        chunk = []
        for n in range(total):
            t = n / SR
            idx = int(t // CHORD_LEN) % len(CHORDS)
            local = t % CHORD_LEN
            chunk.append(struct.pack('<h', int(max(-1, min(1, sample(t, idx, local, CHORD_LEN))) * 24000)))
            if len(chunk) >= 8192:
                w.writeframes(b''.join(chunk))
                chunk = []
        if chunk:
            w.writeframes(b''.join(chunk))


if __name__ == '__main__':
    main()
