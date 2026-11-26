/*
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
  Uji preset hy4 pada simulator browser. Dijalankan lewat test_presets.sh.
*/

"use strict";

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "..", "..", "..");
const REPORT = path.join(ROOT, "chip", "reports", "browser_presets.json");
const DEFAULT_URL = "http://127.0.0.1:8769/chip/simulator.html";
const FALLBACK_URL = "file://" + path.join(ROOT, "site", "chip", "simulator.html");

const CASES = [
  { key: "hy4_dot4", module: "hy4_dot4", out: "y" },
  { key: "hy4_quant", module: "hy4_quant", out: "level" },
  { key: "hy4_top", module: "hy4_top", out: "level" },
  { key: "index_match4", module: "index_match4", out: "score" },
  { key: "tom05_soc", module: "tom05_soc", out: "score" },
  { key: "tom05_ai_accel", module: "tom05_ai_accel", out: "score" },
];

function expected(key, row, heads) {
  const at = (name) => row[heads.indexOf(name)];
  if (key === "hy4_dot4") {
    return (at("a0") + 2 * at("a1") + 3 * at("a2") + 4 * at("a3")) & 15;
  }
  if (key === "hy4_quant") {
    return (at("score") >> 2) & 3;
  }
  if (key === "index_match4") {
    const overlap = at("q") & at("k");
    return (overlap & 1) + ((overlap >> 1) & 1) +
           ((overlap >> 2) & 1) + ((overlap >> 3) & 1);
  }
  if (key === "tom05_soc") {
    return (at("cam0") + 2 * at("cam1") + 3 * at("cam2") + 4 * at("cam3") + at("mode")) & 15;
  }
  if (key === "tom05_ai_accel") {
    const a0 = at("a0"), a1 = at("a1"), a2 = at("a2"), a3 = at("a3");
    const mode = at("mode");
    const m0 = mode & 1, m1 = (mode >> 1) & 1;
    const hit = ((a0 >> 1) & 1) | ((a1 >> 1) & 1) | ((a2 >> 1) & 1) | ((a3 >> 1) & 1);
    const dTensor = (a0 + 2 * a1 + 3 * a2 + 4 * a3) & 31;
    const dLpu = (4 * a0 + 3 * a1 + 2 * a2 + a3) & 31;
    const dNearHit = (2 * a0 + 2 * a1 + a2 + a3) & 31;
    const dNearMiss = (a0 + a1 + 2 * a2 + 2 * a3) & 31;
    const dNear = ((1 - hit) * dNearMiss + hit * dNearHit) & 31;
    const dMesh = (2 * (a0 + a1 + a2 + a3)) & 31;
    return (
      ((1 - m0) & (1 - m1)) * dTensor +
      (m0 & (1 - m1)) * dLpu +
      ((1 - m0) & m1) * dNear +
      (m0 & m1) * dMesh
    ) & 31;
  }
  return (((at("a0") + 2 * at("a1") + 3 * at("a2") + 4 * at("a3")) & 15) >> 2) & 3;
}

function chromePath() {
  if (process.env.CHIP_CHROME_PATH && fs.existsSync(process.env.CHIP_CHROME_PATH)) {
    return process.env.CHIP_CHROME_PATH;
  }
  const base = process.env.PLAYWRIGHT_BROWSERS_PATH || "/opt/ms-playwright";
  if (!fs.existsSync(base)) return undefined;
  const dirs = fs
    .readdirSync(base)
    .filter((d) => d.startsWith("chromium-"))
    .sort()
    .reverse();
  for (const dir of dirs) {
    for (const rel of ["chrome-linux/chrome", "chrome-linux64/chrome"]) {
      const candidate = path.join(base, dir, rel);
      if (fs.existsSync(candidate)) return candidate;
    }
  }
  return undefined;
}

async function reachable(url) {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 2000);
    try {
      const res = await fetch(url, { method: "HEAD", signal: controller.signal });
      return res.ok;
    } finally {
      clearTimeout(timer);
    }
  } catch {
    return false;
  }
}

async function main() {
  const requested = process.argv[2] || process.env.CHIP_SIM_URL || DEFAULT_URL;
  const executablePath = chromePath();
  const browser = await chromium.launch({
    headless: true,
    ...(executablePath ? { executablePath } : {}),
  });
  const page = await browser.newPage();
  const scopedErrors = [];
  page.on("pageerror", (e) => scopedErrors.push("pageerror: " + e.message));
  page.on("console", (m) => {
    if (m.type() === "error") scopedErrors.push("console: " + m.text());
  });

  let url = (await reachable(requested)) ? requested : FALLBACK_URL;
  try {
    await page.goto(url, { waitUntil: "load", timeout: 15000 });
  } catch (err) {
    url = FALLBACK_URL;
    // Beri Chromium waktu menyelesaikan navigasi ke halaman error sebelum
    // navigasi berikutnya, kalau tidak goto() bisa terinterupsi.
    await page.goto("about:blank", { waitUntil: "load", timeout: 5000 }).catch(() => {});
    await page.goto(url, { waitUntil: "load", timeout: 15000 });
  }

  const results = [];
  for (const item of CASES) {
    await page.selectOption("#preset", item.key);
    await page.click("#run");
    const data = await page.evaluate(() => ({
      badge: document.getElementById("result-badge").textContent.trim(),
      module: document.getElementById("module-name").textContent.trim(),
      heads: Array.from(document.querySelectorAll("#results thead th")).map((x) =>
        x.textContent.trim()
      ),
      rows: Array.from(document.querySelectorAll("#results tbody tr")).map((tr) =>
        Array.from(tr.querySelectorAll("td")).map((td) => Number(td.textContent.trim()))
      ),
      waves: document.querySelectorAll("#waveform svg").length,
    }));
    let mismatches = 0;
    data.rows.forEach((row) => {
      const score = expected(item.key, row, data.heads);
      if (score !== row[data.heads.indexOf(item.out)]) {
        mismatches += 1;
      }
      if (item.key === "tom05_soc") {
        const level = (score >> 2) & 3;
        const irq = (((level >> 1) & 1) & (row[data.heads.indexOf("irq_clear")] ^ 1)) & 1;
        if (row[data.heads.indexOf("level")] !== level) mismatches += 1;
        if (row[data.heads.indexOf("irq")] !== irq) mismatches += 1;
        if (row[data.heads.indexOf("ready")] !== 1) mismatches += 1;
      }
      if (item.key === "tom05_ai_accel") {
        const atRow = (name) => row[data.heads.indexOf(name)];
        const level = (score >> 3) & 3;
        const a0 = atRow("a0"), a1 = atRow("a1"), a2 = atRow("a2"), a3 = atRow("a3");
        const hit = ((a0 >> 1) & 1) | ((a1 >> 1) & 1) | ((a2 >> 1) & 1) | ((a3 >> 1) & 1);
        const irq = (((level >> 1) & 1) & (atRow("irq_clear") ^ 1)) & 1;
        if (row[data.heads.indexOf("level")] !== level) mismatches += 1;
        if (row[data.heads.indexOf("hit")] !== hit) mismatches += 1;
        if (row[data.heads.indexOf("irq")] !== irq) mismatches += 1;
        if (row[data.heads.indexOf("ready")] !== 1) mismatches += 1;
      }
    });
    results.push({
      preset: item.key,
      module: data.module,
      badge: data.badge,
      vectors: data.rows.length,
      waveform: data.waves >= 1,
      mismatches,
      pass:
        data.module === item.module &&
        data.rows.length === 8 &&
        data.waves >= 1 &&
        data.badge.startsWith("berhasil") &&
        mismatches === 0,
    });
  }

  const pageInfo = await page.evaluate(() => ({
    secureContext: window.isSecureContext,
    serviceWorker: "serviceWorker" in navigator,
    externalResources: performance
      .getEntriesByType("resource")
      .map((e) => e.name)
      .filter((name) => !name.startsWith(location.origin)),
  }));

  await browser.close();

  const report = {
    license: "Tom05ivier-commits-1.0",
    owner: "Tomi vier",
    timestamp: new Date().toISOString(),
    url,
    presets: results,
    scopedErrors,
    page: pageInfo,
    status:
      results.every((r) => r.pass) && scopedErrors.length === 0 ? "PASS" : "FAIL",
  };
  fs.mkdirSync(path.dirname(REPORT), { recursive: true });
  fs.writeFileSync(REPORT, JSON.stringify(report, null, 2) + "\n", "utf8");
  console.log(
    JSON.stringify(
      {
        status: report.status,
        url: report.url,
        presets: results.map((r) => [r.preset, r.vectors, r.mismatches]),
        scopedErrors: scopedErrors.length,
        report: path.relative(ROOT, REPORT),
      },
      null,
      2
    )
  );
  process.exit(report.status === "PASS" ? 0 : 1);
}

main().catch((err) => {
  console.error("GAGAL:", err && err.message ? err.message : String(err));
  process.exit(2);
});
