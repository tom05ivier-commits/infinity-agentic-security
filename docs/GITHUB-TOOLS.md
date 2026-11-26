<!--
  SPDX-License-Identifier: Tom05ivier-commits-1.0
  Copyright (c) 2026 Tomi vier
  Lisensi: Tom05ivier-commits v1.0 — lihat file LICENSE di root proyek.
-->

# Katalog tool GitHub MCP

Terdaftar 26 tool GitHub MCP di sesi ini. Tool **tidak dipanggil langsung**;
aksesnya hanya lewat `execute`, lalu panggil lewat `path` hasil `search(...)`.
Katalog bersifat parsial — jangan menebak nama tool.

## Daftar tool

| Tool | Fungsi |
|---|---|
| `github.add_issue_comment` | Add a comment to an existing issue |
| `github.create_branch` | Create a new branch in a GitHub repository |
| `github.create_issue` | Create a new issue in a GitHub repository |
| `github.create_or_update_file` | Create or update a single file in a GitHub repository |
| `github.create_pull_request` | Create a new pull request in a GitHub repository |
| `github.create_pull_request_review` | Create a review on a pull request |
| `github.create_repository` | Create a new GitHub repository in your account |
| `github.fork_repository` | Fork a GitHub repository to your account or specified organization |
| `github.get_file_contents` | Get the contents of a file or directory from a GitHub repository |
| `github.get_issue` | Get details of a specific issue in a GitHub repository. |
| `github.get_pull_request` | Get details of a specific pull request |
| `github.get_pull_request_comments` | Get the review comments on a pull request |
| `github.get_pull_request_files` | Get the list of files changed in a pull request |
| `github.get_pull_request_reviews` | Get the reviews on a pull request |
| `github.get_pull_request_status` | Get the combined status of all status checks for a pull request |
| `github.list_commits` | Get list of commits of a branch in a GitHub repository |
| `github.list_issues` | List issues in a GitHub repository with filtering options |
| `github.list_pull_requests` | List and filter repository pull requests |
| `github.merge_pull_request` | Merge a pull request |
| `github.push_files` | Push multiple files to a GitHub repository in a single commit |
| `github.search_code` | Search for code across GitHub repositories |
| `github.search_issues` | Search for issues and pull requests across GitHub repositories |
| `github.search_repositories` | Search for GitHub repositories |
| `github.search_users` | Search for users on GitHub |
| `github.update_issue` | Update an existing issue in a GitHub repository |
| `github.update_pull_request_branch` | Update a pull request branch with the latest changes from the base branch |

## Pola pemanggilan

```js
const r = await search({ namespace: "github", limit: 100 });
// r.items[i].path mis. "tools.github.search_repositories"
const repos = await tools.github.search_repositories({ query: "org:tom05ivier-commits" });
```

Catatan: `search_repositories` memakai `query`, `search_users` memakai `q`.
Kredensial tidak pernah dicetak; `gh auth status` hanya menampilkan status dan empat karakter terakhir token.

## Contoh alur kerja

Cari isu lintas repo (baca saja, aman untuk sesi publik):

```js
const r = await tools.github.search_issues({
  q: "repo:tom05ivier-commits/infinity-agentic-security is:issue is:open",
  per_page: 5,
});
return r.items?.map((i) => ({ title: i.title, url: i.html_url }));
```

Baca berkas lalu ringkas tanpa menulis balik:

```js
const f = await tools.github.get_file_contents({
  owner: "tom05ivier-commits",
  repo: "infinity-agentic-security",
  path: "README.md",
});
return f.content?.map((c) => c.text).join("").slice(0, 2000);
```

Buat perubahan hanya lewat alur review — `create_branch` → `push_files` →
`create_pull_request` → `pull_request_review_write(create)` →
`add_comment_to_pending_review` → `pull_request_review_write(submit_pending)`.
Jangan pernah memasukkan token ke dalam body issue/PR, chat, atau log.

Tool mutasi (`create_*`, `update_*`, `merge_pull_request`, `push_files`) tunduk
pada `surat-izin-github.md` dan dicatat di `security/reports/github_actions.jsonl`.
Pemasangan tool lokal dan klone repo dicatat terpisah di
`security/reports/github_tools_install.jsonl`.
