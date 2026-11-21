/*
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
*/

"use strict";

const els = {
  form: document.getElementById("post-form"),
  submit: document.getElementById("post-submit"),
  posts: document.getElementById("posts"),
  status: document.getElementById("status"),
  refresh: document.getElementById("refresh-btn"),
};

let statusTimer = null;

/* Escape semua data pengguna sebelum disisipkan ke HTML. */
function escapeHtml(value) {
  const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
  return String(value == null ? "" : value).replace(/[&<>"']/g, (ch) => map[ch]);
}

function formatDate(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return escapeHtml(value);
  return escapeHtml(date.toLocaleString("id-ID", {
    year: "numeric", month: "short", day: "numeric",
    hour: "2-digit", minute: "2-digit",
  }));
}

function showStatus(message, type) {
  els.status.textContent = message; // textContent = aman dari XSS
  els.status.className = "status" + (type ? " " + type : "");
  els.status.hidden = false;
  if (statusTimer) clearTimeout(statusTimer);
  statusTimer = setTimeout(() => { els.status.hidden = true; }, 6000);
}

async function api(path, options) {
  let response;
  try {
    response = await fetch(path, options);
  } catch (err) {
    throw new Error("Tidak dapat terhubung ke server komunitas.");
  }
  let data = null;
  try {
    data = await response.json();
  } catch (err) {
    data = null;
  }
  if (!response.ok) {
    const message = data && data.error ? data.error : "Permintaan gagal (" + response.status + ").";
    throw new Error(message);
  }
  return data;
}

function postJSON(path, payload) {
  return api(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

function renderPosts(posts) {
  if (!Array.isArray(posts) || posts.length === 0) {
    els.posts.innerHTML = '<p class="empty">Belum ada posting. Jadilah yang pertama.</p>';
    return;
  }

  els.posts.innerHTML = posts.map((post) => {
    const id = escapeHtml(post.id);
    const replies = Array.isArray(post.replies) ? post.replies : [];

    const replyHtml = replies.length
      ? replies.map((reply) => `
          <div class="reply">
            <div class="meta"><span class="author">${escapeHtml(reply.author)}</span>
              &middot; ${formatDate(reply.created_at)}</div>
            <p class="reply-body">${escapeHtml(reply.body)}</p>
          </div>`).join("")
      : '<p class="replies-title">Belum ada balasan.</p>';

    return `
      <article class="post" data-id="${id}">
        <div class="post-head">
          <h3>${escapeHtml(post.title)}</h3>
          <div class="meta"><span class="author">${escapeHtml(post.author)}</span>
            &middot; ${formatDate(post.created_at)}</div>
        </div>
        <p class="post-body">${escapeHtml(post.body)}</p>
        <div class="replies">
          <p class="replies-title">Balasan (${replies.length})</p>
          ${replyHtml}
          <form class="reply-form" data-id="${id}">
            <div class="row">
              <input type="text" class="reply-author" name="author" maxlength="60"
                     placeholder="Nama Anda" required autocomplete="name">
              <button type="submit">Balas</button>
            </div>
            <textarea class="reply-body" name="body" rows="2" maxlength="2000"
                      placeholder="Tulis balasan..." required></textarea>
          </form>
        </div>
      </article>`;
  }).join("");
}

async function loadPosts() {
  try {
    const data = await api("/api/posts");
    renderPosts(data.posts);
  } catch (err) {
    els.posts.innerHTML = '<p class="error-box">Gagal memuat posting.</p>';
    showStatus(err.message, "error");
  }
}

els.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = els.form.elements.title.value.trim();
  const author = els.form.elements.author.value.trim();
  const body = els.form.elements.body.value.trim();

  if (!title || !author || !body) {
    showStatus("Judul, nama, dan isi wajib diisi.", "error");
    return;
  }

  els.submit.disabled = true;
  try {
    await postJSON("/api/posts", { title, author, body });
    els.form.reset();
    showStatus("Posting berhasil diterbitkan.", "ok");
    await loadPosts();
  } catch (err) {
    showStatus(err.message, "error");
  } finally {
    els.submit.disabled = false;
  }
});

els.posts.addEventListener("submit", async (event) => {
  const form = event.target.closest("form.reply-form");
  if (!form) return;
  event.preventDefault();

  const id = form.dataset.id;
  const author = form.querySelector(".reply-author").value.trim();
  const body = form.querySelector(".reply-body").value.trim();
  if (!author || !body) {
    showStatus("Nama dan balasan wajib diisi.", "error");
    return;
  }

  const button = form.querySelector("button[type='submit']");
  button.disabled = true;
  try {
    await postJSON("/api/posts/" + encodeURIComponent(id) + "/reply", { author, body });
    showStatus("Balasan terkirim.", "ok");
    await loadPosts();
  } catch (err) {
    showStatus(err.message, "error");
    button.disabled = false;
  }
});

els.refresh.addEventListener("click", loadPosts);

loadPosts();
