/*
 * SPDX-License-Identifier: Tom05ivier-commits-1.0
 * Copyright (c) 2026 Tomi vier
 * Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
 *
 * Rekam presentation-infinity.html menjadi MP4 dengan narasi voice id
 * (pitch lebih tinggi, tempo lebih pelan) dan musik latar yang di-duck.
 */
const fs = require('fs');
const os = require('os');
const path = require('path');
const {execFileSync} = require('child_process');
const {chromium} = require('/usr/local/lib/nodejs/current/lib/node_modules/playwright');

const ROOT = '/root/workspace';
const HTML = path.join(ROOT, 'presentation-infinity.html');
const OUT = path.join(ROOT, 'presentation-infinity.mp4');
const CHROME = '/opt/ms-playwright/chromium-1212/chrome-linux/chrome';
const RATE = 118; // wpm — narasi lebih pelan
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), 'infinity-rec-'));
const VIDEO_DIR = path.join(TMP, 'video');
fs.mkdirSync(VIDEO_DIR, {recursive:true});

const html = fs.readFileSync(HTML, 'utf8');
const notes = [...html.matchAll(/note:"((?:[^"\\]|\\.)*)"/g)].map(m => m[1].replace(/\\"/g,'"'));
if (notes.length !== 10) throw new Error(`Harap 10 slide, ditemukan ${notes.length}`);
const DUR = notes.map(n => Math.max(30,
  Math.ceil(n.split(/\s+/).filter(Boolean).length / RATE * 60) + 4));
const TOTAL = DUR.reduce((a,b)=>a+b,0);
console.log(`[1/5] ${notes.length} narasi, total ${TOTAL} detik`);

const wavs = [];
notes.forEach((note, idx) => {
  const clean = note.replace(/[()]/g,'').replace(/[—…]/g,' - ');
  const raw = path.join(TMP, `n${idx}.wav`);
  const pad = path.join(TMP, `p${idx}.wav`);
  // Pitch espeak maks (99) ≈ 172 Hz lalu digeser ke ≈ 235 Hz agar mirip
  // warna suara perempuan pada inbox/hy4-tutorial-9x16.mp4 (F0 median 234,6 Hz).
  execFileSync('espeak-ng', ['-v','id','-p','99','-a','170','-g','0','-s',String(RATE),
    '-w',raw,clean], {stdio:'pipe'});
  const shifted = path.join(TMP, `s${idx}.wav`);
  execFileSync('ffmpeg', ['-y','-loglevel','error','-i',raw,
    '-af','asetrate=22050*1.366,aresample=22050,atempo=0.732',
    '-ar','22050','-ac','1',shifted], {stdio:'pipe'});
  execFileSync('ffmpeg', ['-y','-loglevel','error','-i',shifted,'-af','apad','-t',String(DUR[idx]),
    '-c:a','pcm_s16le','-ar','22050','-ac','1',pad], {stdio:'pipe'});
  wavs.push(pad);
  console.log(`  slide ${idx+1}: ${DUR[idx]} detik`);
});

const list = path.join(TMP, 'list.txt');
fs.writeFileSync(list, wavs.map(w => `file '${w}'`).join('\n') + '\n');
const narration = path.join(TMP, 'narration.wav');
execFileSync('ffmpeg', ['-y','-loglevel','error','-f','concat','-safe','0','-i',list,
  '-c','copy',narration], {stdio:'pipe'});
console.log('[2/5] Narasi siap');

const music = path.join(TMP, 'music.wav');
execFileSync('python3', [path.join(ROOT,'scripts/infinity_music.py'),
  '--duration',String(TOTAL),'--output',music], {stdio:'pipe'});
const mixed = path.join(TMP, 'mixed.wav');
execFileSync('ffmpeg', ['-y','-loglevel','error','-i',narration,'-i',music,
  '-filter_complex',
  '[1:a]volume=0.18[mg];[mg][0:a]sidechaincompress=threshold=0.012:ratio=8:attack=40:release=600[duck];[0:a][duck]amix=inputs=2:duration=first:weights=1 0.9[out]',
  '-map','[out]','-c:a','pcm_s16le','-ar','22050','-ac','1',mixed], {stdio:'pipe'});
console.log('[3/5] Musik latar dicampur (duck saat narasi)');

(async () => {
  const browser = await chromium.launch({
    executablePath: CHROME,
    headless: true,
    args: ['--no-sandbox','--disable-dev-shm-usage','--autoplay-policy=no-user-gesture-required']
  });
  const context = await browser.newContext({
    viewport: {width:1280, height:720},
    recordVideo: {dir: VIDEO_DIR, size:{width:1280, height:720}}
  });
  const page = await context.newPage();
  await page.goto('file://' + HTML, {waitUntil:'load'});
  await page.click('#mute');           // TTS browser dimatikan; pakai audio espeak + musik
  await page.click('#play');
  console.log(`[4/5] Rekam ${TOTAL} detik...`);
  let done = 0;
  for (let idx = 0; idx < DUR.length; idx++) {
    await page.waitForTimeout(DUR[idx] * 1000);
    done += DUR[idx];
    console.log(`  ${done}/${TOTAL} detik`);
  }
  await page.close();
  const videoPath = await page.video().path();
  await context.close();
  await browser.close();
  console.log('[5/5] Mux video + audio ->', OUT);
  execFileSync('ffmpeg', ['-y','-loglevel','error','-i',videoPath,'-i',mixed,
    '-c:v','libx264','-crf','22','-preset','veryfast','-c:a','aac','-b:a','128k',
    '-shortest','-movflags','+faststart',OUT], {stdio:'pipe'});
  console.log('SELESAI:', OUT, (fs.statSync(OUT).size/1048576).toFixed(1), 'MB');
  fs.rmSync(TMP, {recursive:true, force:true});
})().catch(e => { console.error('GAGAL:', e); process.exit(1); });
