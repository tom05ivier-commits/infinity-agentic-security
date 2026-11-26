/*
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
  Simulator HDL mini — berjalan sepenuhnya di browser, tanpa dependensi.
*/

(function () {
  "use strict";

  var PRESETS = {
    adder:
      "// adder 4-bit: menjumlahkan a dan b\n" +
      "module adder(input [3:0] a, b, output [4:0] sum);\n" +
      "  assign sum = a + b;\n" +
      "endmodule\n",
    counter:
      "// counter 4-bit: nilai berikutnya dari hitungan\n" +
      "module counter(input [3:0] count, output [3:0] next);\n" +
      "  assign next = count + 1;\n" +
      "endmodule\n",
    traffic:
      // lampu merah -> kuning -> hijau direpresentasikan sebagai bit
      "module traffic_light(input [1:0] phase, output [2:0] lamp);\n" +
      "  assign lamp = 1 << phase;\n" +
      "endmodule\n",
    andgate:
      "module and_gate(input a, b, output y);\n" +
      "  assign y = a & b;\n" +
      "endmodule\n",
    full_adder:
      "module full_adder(input a, b, cin, output sum, cout);\n" +
      "  assign sum = a ^ b ^ cin;\n" +
      "  assign cout = (a & b) | (a & cin) | (b & cin);\n" +
      "endmodule\n",
    mux2:
      "module mux2(input a, b, sel, output y);\n" +
      "  assign y = (a & ~sel) | (b & sel);\n" +
      "endmodule\n",
    decoder2:
      "module decoder2(input a, b, output y0, y1, y2, y3);\n" +
      "  assign y0 = ~a & ~b;\n" +
      "  assign y1 = a & ~b;\n" +
      "  assign y2 = ~a & b;\n" +
      "  assign y3 = a & b;\n" +
      "endmodule\n",
    parity4:
      "module parity4(input a, b, c, d, output odd);\n" +
      "  assign odd = a ^ b ^ c ^ d;\n" +
      "endmodule\n",
    alu4:
      "module alu4(input [3:0] a, b, input op0, op1, output [3:0] y);\n" +
      "  assign y = (((a + b) * (1 - op0) * (1 - op1)) |\n" +
      "              ((a & b) * op0 * (1 - op1)) |\n" +
      "              ((a | b) * (1 - op0) * op1) |\n" +
      "              ((a ^ b) * op0 * op1));\n" +
      "endmodule\n",
    hy4_dot4:
      "// hy4: skor berbobot 4 fitur\n" +
      "module hy4_dot4(input [1:0] a0, a1, a2, a3, output [3:0] y);\n" +
      "  assign y = (a0 + (a1 * 2) + (a2 * 3) + (a3 * 4)) & 15;\n" +
      "endmodule\n",
    hy4_quant:
      "// hy4: kuantisasi skor\n" +
      "module hy4_quant(input [3:0] score, output [1:0] level);\n" +
      "  assign level = (score >> 2) & 3;\n" +
      "endmodule\n",
    hy4_top:
      "// hy4: inti akselerator model\n" +
      "module hy4_top(input [1:0] a0, a1, a2, a3, output [1:0] level);\n" +
      "  assign level = (((a0 + (a1 * 2) + (a2 * 3) + (a3 * 4)) & 15) >> 2) & 3;\n" +
      "endmodule\n",
    tom05_soc:
      "// tom05: SoC untuk smartphone Android\n" +
      "module tom05_soc(input [1:0] cam0, cam1, cam2, cam3, input mode, input irq_clear, output [3:0] score, output [1:0] level, output irq, output ready);\n" +
      "  assign score = (cam0 + (cam1 * 2) + (cam2 * 3) + (cam3 * 4) + mode) & 15;\n" +
      "  assign level = (score >> 2) & 3;\n" +
      "  assign irq = ((level >> 1) & 1) & (irq_clear ^ 1);\n" +
      "  assign ready = 1;\n" +
      "endmodule\n",
    index_match4:
      "// indeks aman: irisan masker kata kunci\n" +
      "module index_match4(input [3:0] q, input [3:0] k, output [2:0] score);\n" +
      "  assign score = ((q & k) & 1) + (((q & k) >> 1) & 1) + (((q & k) >> 2) & 1) + (((q & k) >> 3) & 1);\n" +
      "endmodule\n",
    tom05_ai_accel:
      "// tom05: akselerator AI TAI-1 dengan empat profil dataflow\n" +
      "module tom05_ai_accel(input [1:0] a0, a1, a2, a3, input [1:0] mode, input irq_clear, output [4:0] score, output [1:0] level, output hit, output irq, output ready);\n" +
      "  assign score = (((1 - (mode & 1)) & (1 - ((mode >> 1) & 1))) * (a0 + (a1 * 2) + (a2 * 3) + (a3 * 4)))\n" +
      "    + (((mode & 1) & (1 - ((mode >> 1) & 1))) * ((a0 * 4) + (a1 * 3) + (a2 * 2) + a3))\n" +
      "    + (((1 - (mode & 1)) & ((mode >> 1) & 1)) * (((1 - (((a0 >> 1) & 1) | ((a1 >> 1) & 1) | ((a2 >> 1) & 1) | ((a3 >> 1) & 1))) * (a0 + a1 + (a2 * 2) + (a3 * 2))) + ((((a0 >> 1) & 1) | ((a1 >> 1) & 1) | ((a2 >> 1) & 1) | ((a3 >> 1) & 1))) * ((a0 * 2) + (a1 * 2) + a2 + a3)))\n" +
      "    + (((mode & 1) & ((mode >> 1) & 1)) * ((a0 * 2) + (a1 * 2) + (a2 * 2) + (a3 * 2))) & 31;\n" +
      "  assign level = (score >> 3) & 3;\n" +
      "  assign hit = ((a0 >> 1) & 1) | ((a1 >> 1) & 1) | ((a2 >> 1) & 1) | ((a3 >> 1) & 1);\n" +
      "  assign irq = ((level >> 1) & 1) & (irq_clear ^ 1);\n" +
      "  assign ready = 1;\n" +
      "endmodule\n"
  };

  var STORE_KEY = "chip-merah-putih-designs";
  var DRAFT_KEY = "chip-merah-putih-draft";

  var codeEl = document.getElementById("code");
  var presetEl = document.getElementById("preset");
  var runBtn = document.getElementById("run");
  var saveBtn = document.getElementById("save");
  var downloadBtn = document.getElementById("download");
  var statusEl = document.getElementById("status");
  var moduleNameEl = document.getElementById("module-name");
  var resultBadge = document.getElementById("result-badge");
  var resultsEl = document.getElementById("results");
  var waveEl = document.getElementById("waveform");
  var savedList = document.getElementById("saved-list");

  function esc(value) {
    return String(value).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function bin(value, width) {
    if (width > 12) return String(value);
    var s = (value >>> 0).toString(2);
    while (s.length < width) s = "0" + s;
    return s;
  }

  function maskFor(width) {
    var bits = Math.min(width, 31);
    return bits >= 31 ? 0x7fffffff : (1 << bits) - 1;
  }

  function setStatus(message, kind) {
    statusEl.textContent = message;
    statusEl.className = "status" + (kind ? " " + kind : "");
  }

  /* ---------- Pengurai ekspresi ---------- */

  function tokenize(src) {
    var out = [];
    var i = 0;
    var re = /\s*(?:(\d+'[bB][01]+)|(\d+'[dD]\d+)|(\d+'[hH][0-9a-fA-F]+)|(\d+)|([A-Za-z_]\w*)|(<<|>>)|([~&|^+*()\-]))/y;
    src = src.trim();
    while (i < src.length) {
      re.lastIndex = i;
      var m = re.exec(src);
      if (!m) throw new Error("Bagian kode tidak dikenali: " + src.slice(i, i + 14));
      i = re.lastIndex;
      if (m[1]) out.push({ t: "num", v: parseInt(m[1].split("'")[1].slice(1), 2) });
      else if (m[2]) out.push({ t: "num", v: parseInt(m[2].split("'")[1].slice(1), 10) });
      else if (m[3]) out.push({ t: "num", v: parseInt(m[3].split("'")[1].slice(1), 16) });
      else if (m[4]) out.push({ t: "num", v: parseInt(m[4], 10) });
      else if (m[5]) out.push({ t: "id", v: m[5] });
      else out.push({ t: "op", v: m[6] || m[7] });
    }
    return out;
  }

  var PRECEDENCE = { "|": 1, "^": 2, "&": 3, "<<": 4, ">>": 4, "+": 5, "-": 5, "*": 6 };

  function parseExpression(src) {
    var tokens = tokenize(src);
    var pos = 0;

    function peek() { return tokens[pos]; }
    function isOp(value) {
      var t = peek();
      return t && t.t === "op" && t.v === value;
    }

    function atom() {
      var t = tokens[pos++];
      if (!t) throw new Error("Ekspresi belum lengkap");
      if (t.t === "num") return { k: "num", v: t.v };
      if (t.t === "id") return { k: "id", v: t.v };
      if (t.v === "(") {
        var inner = expression(1);
        if (!isOp(")")) throw new Error("Kurung tutup hilang");
        pos++;
        return inner;
      }
      if (t.v === "~" || t.v === "-" || t.v === "+") {
        return { k: "un", op: t.v, x: atom() };
      }
      throw new Error("Token tak terduga: " + t.v);
    }

    function expression(min) {
      var left = atom();
      while (true) {
        var t = peek();
        if (!t || t.t !== "op" || !(t.v in PRECEDENCE) || PRECEDENCE[t.v] < min) break;
        var op = t.v;
        pos++;
        var right = expression(PRECEDENCE[op] + 1);
        left = { k: "bin", op: op, a: left, b: right };
      }
      return left;
    }

    var ast = expression(1);
    if (pos < tokens.length) throw new Error("Sisa kode pada ekspresi: " + tokens[pos].v);
    return ast;
  }

  function evaluate(node, ctx) {
    if (node.k === "num") return node.v;
    if (node.k === "id") {
      if (!(node.v in ctx)) throw new Error("Sinyal belum dikenal: " + node.v);
      return ctx[node.v];
    }
    if (node.k === "un") {
      var x = evaluate(node.x, ctx);
      return node.op === "~" ? ~x : node.op === "-" ? -x : x;
    }
    var a = evaluate(node.a, ctx);
    var b = evaluate(node.b, ctx);
    switch (node.op) {
      case "|": return a | b;
      case "^": return a ^ b;
      case "&": return a & b;
      case "<<": return a << b;
      case ">>": return a >> b;
      case "+": return a + b;
      case "-": return a - b;
      case "*": return a * b;
      default: throw new Error("Operator belum didukung: " + node.op);
    }
  }

  /* ---------- Pengurai desain ---------- */

  function parseDesign(source) {
    var code = source
      .replace(/\/\/[^\n]*/g, "")
      .replace(/\/\*[\s\S]*?\*\//g, "");

    var moduleMatch = code.match(/module\s+([A-Za-z_]\w*)\s*\(([\s\S]*?)\)\s*;([\s\S]*?)endmodule/i);
    if (!moduleMatch) {
      throw new Error("Tidak menemukan blok module ...; ... endmodule");
    }

    var ports = [];
    // Pemisah deklarasi: titik koma, atau awal kata kunci input/output/inout
    // berikutnya (sering muncul setelah koma dalam satu baris deklarasi).
    var parts = moduleMatch[2].split(/;|\s+(?=(?:input|output|inout)\b)/i);
    parts.forEach(function (part) {
      part = part.trim().replace(/,+$/, "").trim();
      if (!part) return;
      var m = part.match(/^(input|output|inout)\s*(?:\[\s*(\d+)\s*:\s*0\s*\])?\s*([\s\S]*)$/i);
      if (!m) throw new Error("Deklarasi port tidak dikenali: " + part);
      var width = m[2] ? parseInt(m[2], 10) + 1 : 1;
      m[3].split(",").forEach(function (raw) {
        var name = raw.trim().replace(/\[[^\]]*\]/g, "").trim();
        if (!name) return;
        if (!/^[A-Za-z_]\w*$/.test(name)) throw new Error("Nama port tidak valid: " + name);
        ports.push({ name: name, dir: m[1].toLowerCase(), width: width });
      });
    });

    var inputs = ports.filter(function (p) { return p.dir === "input" || p.dir === "inout"; });
    var outputs = ports.filter(function (p) { return p.dir === "output"; });
    if (!inputs.length) throw new Error("Desain perlu minimal satu port input");
    if (!outputs.length) throw new Error("Desain perlu minimal satu port output");

    var assigns = [];
    var reAssign = /assign\s+([A-Za-z_]\w*)\s*=\s*([^;]+);/gi;
    var match;
    while ((match = reAssign.exec(moduleMatch[3])) !== null) {
      assigns.push({
        target: match[1],
        source: match[2].trim(),
        ast: parseExpression(match[2])
      });
    }
    if (!assigns.length) throw new Error("Tidak menemukan pernyataan assign");
    assigns.forEach(function (a) {
      if (!outputs.some(function (p) { return p.name === a.target; })) {
        throw new Error("Assign ke sinyal yang bukan output: " + a.target);
      }
    });

    return { name: moduleMatch[1], inputs: inputs, outputs: outputs, assigns: assigns };
  }

  /* ---------- Simulasi ---------- */

  function makeVectors(inputs) {
    var rows = [];
    for (var i = 0; i < 8; i++) {
      var vec = {};
      inputs.forEach(function (port, idx) {
        var raw = idx === 0 ? i : i * (2 * idx + 1);
        vec[port.name] = raw & maskFor(port.width);
      });
      rows.push(vec);
    }
    return rows;
  }

  function simulate(design) {
    var vectors = makeVectors(design.inputs);
    var widthOf = {};
    design.inputs.concat(design.outputs).forEach(function (p) { widthOf[p.name] = p.width; });

    var rows = vectors.map(function (vec) {
      var ctx = Object.assign({}, vec);
      design.assigns.forEach(function (a) {
        var value = evaluate(a.ast, ctx) & maskFor(widthOf[a.target]);
        ctx[a.target] = value;
      });
      return ctx;
    });

    return {
      signals: design.inputs.concat(design.outputs),
      vectors: vectors,
      rows: rows
    };
  }

  /* ---------- Tampilan ---------- */

  function renderTable(result) {
    var names = result.signals.map(function (s) { return s.name; });
    var head = "<tr><th>#</th>" + names.map(function (n) {
      return "<th>" + esc(n) + "</th>";
    }).join("") + "</tr>";
    var body = result.rows.map(function (row, i) {
      return "<tr><td>" + i + "</td>" + names.map(function (n) {
        var port = result.signals.filter(function (s) { return s.name === n; })[0];
        return "<td title='" + bin(row[n], port.width) + "'>" + row[n] + "</td>";
      }).join("") + "</tr>";
    }).join("");
    resultsEl.innerHTML = "<thead>" + head + "</thead><tbody>" + body + "</tbody>";
  }

  function renderWave(result) {
    var W = 660;
    var LEFT = 112;
    var seg = (W - LEFT - 12) / result.vectors.length;
    var height = 40 + result.signals.length * 48 + 26;
    var parts = ['<svg viewBox="0 0 ' + W + ' ' + height + '" width="100%" role="img" aria-label="Bentuk gelombang hasil simulasi">'];

    // Grid waktu
    for (var j = 0; j <= result.vectors.length; j++) {
      var gx = LEFT + j * seg;
      parts.push('<line x1="' + gx + '" y1="26" x2="' + gx + '" y2="' + (height - 24) + '" stroke="#e8edf4" stroke-width="1"/>');
      if (j < result.vectors.length) {
        parts.push('<text x="' + (gx + seg / 2) + '" y="' + (height - 8) + '" fill="#8b9bb4" font-size="10" text-anchor="middle">t' + j + "</text>");
      }
    }

    result.signals.forEach(function (signal, i) {
      var y0 = 40 + i * 48;
      var max = Math.max(1, maskFor(signal.width));
      var color = signal.dir === "input" ? "#28a4a0" : "#e14b4b";
      parts.push('<text x="8" y="' + (y0 + 24) + '" fill="#1c2738" font-size="11" font-family="monospace">' + esc(signal.name) + "</text>");
      parts.push('<line x1="' + LEFT + '" y1="' + (y0 + 40) + '" x2="' + (W - 12) + '" y2="' + (y0 + 40) + '" stroke="#eef1f6" stroke-width="1"/>');

      var points = [];
      result.rows.forEach(function (row, j) {
        var value = row[signal.name];
        var y = y0 + 38 - (value / max) * 30;
        var x = LEFT + j * seg;
        // Tahan nilai secara horizontal, lalu lompat vertikal di batas vektor
        // agar bentuknya menyerupai waveform digital, bukan garis miring.
        points.push(x + "," + y);
        points.push((x + seg) + "," + y);
        parts.push('<text x="' + (x + seg / 2) + '" y="' + (y - 5) + '" fill="' + color + '" font-size="9" font-family="monospace" text-anchor="middle">' + value + "</text>");
      });
      parts.push('<polyline fill="none" stroke="' + color + '" stroke-linejoin="miter" stroke-width="2.2" points="' + points.join(" ") + '"/>');
    });

    parts.push("</svg>");
    waveEl.innerHTML = parts.join("");
  }

  function run() {
    try {
      var design = parseDesign(codeEl.value);
      var result = simulate(design);
      moduleNameEl.textContent = design.name;
      resultBadge.textContent = "berhasil · " + result.rows.length + " vektor";
      resultBadge.className = "ok";
      renderTable(result);
      renderWave(result);
      setStatus("Simulasi " + design.name + " berhasil. " + result.rows.length + " vektor uji dijalankan.", "ok");
    } catch (err) {
      resultBadge.textContent = "gagal";
      resultBadge.className = "err";
      setStatus(err.message || String(err), "err");
    }
  }

  /* ---------- Penyimpanan lokal ---------- */

  function loadSaved() {
    try {
      var data = JSON.parse(localStorage.getItem(STORE_KEY) || "[]");
      return Array.isArray(data) ? data : [];
    } catch (e) {
      return [];
    }
  }

  function persist(list) {
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify(list));
      return true;
    } catch (e) {
      setStatus("Penyimpanan browser tidak tersedia.", "err");
      return false;
    }
  }

  function nameFromCode(source) {
    var m = source.match(/module\s+([A-Za-z_]\w*)/i);
    return m ? m[1] : "desain";
  }

  function renderSaved() {
    var items = loadSaved();
    if (!items.length) {
      savedList.innerHTML = '<li class="muted">Belum ada desain tersimpan.</li>';
      return;
    }
    savedList.innerHTML = items.map(function (item, i) {
      return '<li class="saved-item"><span>' + esc(item.name) + "</span>" +
        '<button type="button" data-load="' + i + '">Muat</button>' +
        '<button type="button" class="del" data-delete="' + i + '">Hapus</button></li>';
    }).join("");
  }

  function save() {
    var items = loadSaved();
    items.unshift({
      name: nameFromCode(codeEl.value) + " · " + new Date().toLocaleString("id-ID"),
      code: codeEl.value,
      savedAt: new Date().toISOString()
    });
    if (persist(items.slice(0, 20))) {
      renderSaved();
      setStatus("Desain tersimpan di browser ini.", "ok");
    }
  }

  function download() {
    var blob = new Blob([codeEl.value], { type: "text/plain;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = nameFromCode(codeEl.value) + ".v";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setStatus("Berkas " + a.download + " diunduh.", "ok");
  }

  /* ---------- Inisialisasi ---------- */

  function applyPreset(key) {
    if (PRESETS[key]) {
      codeEl.value = PRESETS[key];
      run();
    }
  }

  var draftTimer = null;
  codeEl.addEventListener("input", function () {
    if (draftTimer) clearTimeout(draftTimer);
    draftTimer = setTimeout(function () {
      try { localStorage.setItem(DRAFT_KEY, codeEl.value); } catch (e) { /* abaikan */ }
    }, 400);
  });

  function restoreDraft() {
    try {
      var draft = localStorage.getItem(DRAFT_KEY);
      if (draft) {
        codeEl.value = draft;
        return true;
      }
    } catch (e) { /* abaikan */ }
    return false;
  }

  presetEl.addEventListener("change", function () { applyPreset(presetEl.value); });
  runBtn.addEventListener("click", run);
  saveBtn.addEventListener("click", save);
  downloadBtn.addEventListener("click", download);
  savedList.addEventListener("click", function (e) {
    var loadIndex = e.target.getAttribute("data-load");
    var delIndex = e.target.getAttribute("data-delete");
    var items = loadSaved();
    if (loadIndex !== null) {
      codeEl.value = items[Number(loadIndex)].code;
      run();
      setStatus("Desain dimuat.", "ok");
    } else if (delIndex !== null) {
      items.splice(Number(delIndex), 1);
      persist(items);
      renderSaved();
    }
  });

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("sw.js").catch(function () { /* abaikan */ });
  }

  if (restoreDraft()) {
    run();
    setStatus("Draft sebelumnya dipulihkan. Perubahan tersimpan otomatis di browser ini.", "ok");
  } else {
    applyPreset(presetEl.value);
  }
  renderSaved();
})();
