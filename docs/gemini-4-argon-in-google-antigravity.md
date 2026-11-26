<!--
  Salinan lokal artikel publik (bukan kode, bukan lisensi proyek).
  Sumber : https://antigravity.google/blog/gemini-4-argon-in-google-antigravity
  Diambil: 2026-11-23
  Catatan: teks ini adalah dokumentasi referensi; tidak mengandung kredensial
           atau data pribadi, dan tidak mengubah lisensi repo mana pun.
-->

# Gemini 4 Argon in Google Antigravity

**Sumber:** https://antigravity.google/blog/gemini-4-argon-in-google-antigravity
**Penulis:** The Antigravity Team
**Tanggal:** 13 Oktober 2026 · 6 menit baca

---

Since the beginning, we built Google Antigravity for an agent-first future,
designing foundational primitives that would scale alongside model
intelligence. With Gemini 4 Argon, the agent-first experience truly comes to
life in the Antigravity App.

Earlier this month, we introduced Gemini 4 Argon, our latest model with
frontier performance in complex workflows across real-world software
engineering, enterprise knowledge work like legal and finance, and
cybersecurity defense. Today, we're rolling out Gemini 4 Argon directly inside
Google Antigravity for Google AI Pro and Ultra subscribers — available in the
Antigravity desktop app and the Antigravity CLI. For businesses, Gemini 4 Argon
is available via the API in Gemini platform and within Antigravity on eligible
Gemini Enterprise subscriptions.

While Argon is designed to tackle your hardest problems, we're equally excited
about future models that can be used as everyday drivers for an even broader
range of builders.

## Accelerating development across Google

Our most honest proving ground is our engineering teams. Before bringing Argon
to developers in Antigravity, we put it to work inside Google.

Today, over 100K users across Alphabet rely on Argon inside our internal
version of Antigravity each month to solve complex production problems across
our codebases. Over a four-week period, we have seen a 35% increase in agentic
code, improving not just developer velocity, but code quality with a 30%
decrease in post-submit rollbacks.

- **YouTube comment optimization:** Argon in Antigravity helped the team cut
  the CPU footprint of YouTube's comments frontend in half. By tracing
  production profile data, Argon identified that redundant emoji rendering
  alone accounted for nearly 45% of server overhead, leading to 12 targeted
  optimizations. The updates reduced server comment-load latency by 30 ms and
  dropped client end-to-end latency by 20 ms.

- **Debugging Wing drone physics simulator:** Argon in Antigravity reviewed
  Wing's proprietary internal drone physics simulator, reasoning through the
  underlying physics and math rather than just the structure of the code. It
  highlighted areas for improved physics simulations and proposed 18 targeted
  modelling improvements across aerodynamics, propulsion, and structural
  dynamics to resolve long-standing legacy issues.

Operating at Google-scale forced us to build Antigravity to be enterprise-ready
from Day 1, transforming our day-to-day development across Google.

- **Burning down the backlog:** Argon in Antigravity took an aging queue of 134
  open bug reports spanning multiple services, and ran agents to work out which
  were still real, cross-referencing commit histories, checking whether
  candidate fixes actually reached production, and inspecting live telemetry
  for whether the error still occurs. In under 3 hours it closed 97 stale or
  duplicate bugs with documented commit proof (a 72.4% queue reduction) and
  sorted the remaining 37 by owner with no unassigned tickets left.

- **Migrating legacy code:** Using a custom skill within Antigravity, a team
  deployed Argon to map and execute a complete rewrite of fragile legacy
  Fortran into modern Rust. Argon autonomously delivered the modernized
  codebase, achieving a 1.8x performance boost and memory safety.

- **Performing security audits:** Argon in Antigravity was used to audit a
  batch of access-control changes. Argon traced how permissions actually
  flowed at runtime rather than just reading the code diff, and found four
  critical security bugs. Two earlier frontier models had audited the
  identical code and both concluded there were zero security holes.

- **Triaging production support tickets:** Argon in Antigravity batch-processes
  dozens of tickets from an on-call rotation, sorts them by issue type, traces
  root causes through code and logs, proposes fixes and drafts replies for
  human approval. This freed up 2-3 hours per shift.

## Argon across disciplines

Monthly active usage outside of core engineering is soaring, with over half of
Cloud sales, almost half of finance, and over a third of business and
operations Googlers using Antigravity. Plugins, skills, and MCP integrations
make it straightforward to connect the agent to specialized data sources and
workflows.

- **Marketing website localization:** The Antigravity DevRel team used Argon in
  Antigravity to localize hundreds of pages of developer documentation into 17
  languages in a matter of hours.

- **Accelerating data center pipeline modernization:** A Data Science Technical
  Program Manager leveraged Argon to fast-track development of a 3,200-line
  Google Data Center fleet analytics pipeline (Python, SQL, dashboards) into
  production in days.

- **Vetting sales prospects:** Argon in Antigravity built an automated
  qualification workflow for an Ads sales account executive, reducing research
  time by 90% and saving upwards of 10 hours of manual work per week.

- **Financial planning and analysis:** With custom finance plugins, a finance
  lead used Argon for end-to-end financial reconciliations, budget tracking,
  contract extraction, and daily executive briefings across 80 separate
  workflows. Over seven business days, 15.5 hours of human direction produced
  about 335 human-equivalent hours of validated financial output.

## Getting started

Argon is rolling out in the Google Antigravity desktop app and CLI for Google
AI Pro and Ultra subscribers, eligible Gemini Enterprise subscriptions, and in
the API in Gemini platform. Update to the latest version of Antigravity to try
it on your most complex workflows.

---

**Catatan lokal:** artikel ini menjelaskan produk komersial Google. Tidak ada
source code atau model open-weight yang bisa di-clone dari halaman ini.
Mekanisme yang disebutkan (skills, plugins, integrasi MCP, `/goal`, `/swarm`)
adalah fitur di dalam produk Antigravity, bukan sesuatu yang dapat digabungkan
langsung dengan data workspace tanpa konfigurasi dan otorisasi terpisah.
