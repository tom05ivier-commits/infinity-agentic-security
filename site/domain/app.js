/*
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
  Antarmuka generator domain. Semua data berasal dari API lokal yang sama.
*/
"use strict";

function el(id) { return document.getElementById(id); }

function node(tag, text, cls) {
  var item = document.createElement(tag);
  if (text !== undefined && text !== null) item.textContent = String(text);
  if (cls) item.className = cls;
  return item;
}

async function api(path, options) {
  var response = await fetch(path, options);
  if (!response.ok) throw new Error("HTTP " + response.status);
  return response.json();
}

function fallbackSuggest(seed, count) {
  var out = [];
  for (var i = 0; i < count; i++) {
    var h = 2166136261;
    var text = seed + ":" + i;
    for (var j = 0; j < text.length; j++) {
      h ^= text.charCodeAt(j);
      h = Math.imul(h, 16777619) >>> 0;
    }
    out.push({
      name: "ai-" + h.toString(16).padStart(8, "0").slice(0, 6),
      host: "ai-" + h.toString(16).padStart(8, "0").slice(0, 6) + ".agenty.local",
      available: true,
      seed: seed
    });
  }
  return out;
}

function renderSuggestions(items) {
  var list = el("suggestions");
  if (!list) return;
  list.replaceChildren();
  items.forEach(function (item) {
    var row = node("li");
    row.appendChild(node("span", item.host));
    row.appendChild(node("span", item.available ? "tersedia" : "terpakai",
      item.available ? "ok" : "bad"));
    list.appendChild(row);
  });
}

function renderDomains(data) {
  var list = el("domains");
  var note = el("hosts-note");
  if (!list) return;
  list.replaceChildren();
  (data.domains || []).forEach(function (item) {
    var row = node("li");
    row.appendChild(node("span", item.host + " → " + item.target));
    var button = node("button", "hapus", "danger");
    button.type = "button";
    button.addEventListener("click", function () { removeDomain(item.name); });
    row.appendChild(button);
    list.appendChild(row);
  });
  if (note) {
    note.textContent = data.hosts_installed
      ? "Blok /etc/hosts sudah terpasang di perangkat ini."
      : "Blok /etc/hosts belum terpasang. Gunakan tombol konfirmasi di bawah.";
  }
}

async function loadSuggest(seed, count) {
  try {
    var data = await api("/api/suggest?seed=" + encodeURIComponent(seed) + "&count=" + count);
    renderSuggestions(data.domains);
  } catch (err) {
    renderSuggestions(fallbackSuggest(seed, count));
  }
}

async function loadDomains() {
  try {
    renderDomains(await api("/api/domains"));
  } catch (err) {
    var note = el("hosts-note");
    if (note) note.textContent = "API tidak tersedia.";
  }
}

async function addDomain(name, target) {
  try {
    await api("/api/domains", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: name, target: target })
    });
    await loadDomains();
  } catch (err) {
    window.alert("Gagal mendaftarkan domain: " + err.message);
  }
}

async function removeDomain(name) {
  try {
    await api("/api/domains/remove", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: name })
    });
    await loadDomains();
  } catch (err) {
    window.alert("Gagal menghapus domain: " + err.message);
  }
}

async function loadDdns() {
  var target = el("ddns-status");
  if (!target) return;
  try {
    var data = await api("/api/ddns/status");
    var names = Object.keys(data.providers);
    var configured = names.filter(function (name) { return data.providers[name].configured; });
    target.textContent = configured.length
      ? "Token terkonfigurasi untuk: " + configured.join(", ") + ". Update tetap memerlukan --authorize."
      : "Belum ada token DDNS. Update otomatis dinonaktifkan.";
  } catch (err) {
    target.textContent = "Status DDNS tidak tersedia.";
  }
}

async function loadGuide() {
  var target = el("guide-list");
  if (!target) return;
  try {
    var data = await api("/api/guide");
    data.providers.forEach(function (item) {
      var row = node("div", null, "panel");
      row.appendChild(node("h2", item.name));
      row.appendChild(node("p", item.type + " — " + item.usage));
      row.appendChild(node("p", item.note, "muted"));
      target.appendChild(row);
    });
  } catch (err) {
    target.appendChild(node("p", "Panduan tidak tersedia.", "bad"));
  }
}

document.addEventListener("DOMContentLoaded", function () {
  var suggestForm = el("form-suggest");
  if (suggestForm) {
    suggestForm.addEventListener("submit", function (event) {
      event.preventDefault();
      var seed = el("seed").value || "agenty";
      var count = parseInt(el("count").value, 10) || 8;
      loadSuggest(seed, count);
    });
    loadSuggest("agenty", 8);
    loadDomains();
    loadDdns();
  }

  var addForm = el("form-add");
  if (addForm) {
    addForm.addEventListener("submit", function (event) {
      event.preventDefault();
      var name = el("name").value.trim();
      if (!name) return;
      addDomain(name, el("target").value);
      el("name").value = "";
    });
  }

  var install = el("install-hosts");
  if (install) {
    install.addEventListener("click", async function () {
      if (!window.confirm("Pasang blok domain lokal ke /etc/hosts? Backup akan dibuat.")) return;
      try {
        var result = await api("/api/install", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ authorize: true })
        });
        window.alert("Terpasang: " + result.domains + " domain. Backup: " + (result.backup || "tidak ada"));
        await loadDomains();
      } catch (err) {
        window.alert("Gagal memasang: " + err.message);
      }
    });
  }

  loadGuide();
});
