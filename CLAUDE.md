# Kaappi Documentation Site

MkDocs Material site for [Kaappi](https://github.com/kaappi/kaappi), an R7RS Scheme implementation in Zig.

Served at **https://kaappi-lang.org/** (custom domain via `docs/CNAME`).

## Related repos

| Repo | Local path | What it is |
|------|-----------|------------|
| [kaappi](https://github.com/kaappi/kaappi) | `../kaappi/` | Core Scheme implementation (Zig). Dev docs at `docs/dev/` |
| [kaappi-book](https://github.com/kaappi/kaappi-book) | `../kaappi-book/` | XeLaTeX book teaching Kaappi Scheme (18 chapters + appendices) |

This repo is exclusively for **end-user documentation**. Developer/contributor
docs (architecture, testing, adding-features, postmortems) live in the main
repo under `docs/dev/` — do not add dev docs here. The book (`kaappi-book`)
covers Scheme from scratch for programmers; this site is reference and guide material.

## Site map

The authoritative page list is the `nav:` section of `mkdocs.yml` — check it
when adding, renaming, or removing pages (do not rely on this table for exact
page names). Section overview:

| Section | Path | Pages | Content |
|---------|------|:-----:|---------|
| Home | `docs/index.md` | 1 | Stub; rendered by `overrides/home.html` |
| Try It (playground) | `docs/playground.md` | 1 | Stub; rendered by `overrides/playground.html` |
| Tour | `docs/tour.md` | 1 | Stub; rendered by `overrides/tour.html` (12 lessons) |
| Download | `docs/download.md` | 1 | Install script + binary links; **version in H1** |
| Guide | `docs/guide/` | 19 + index | Installation through troubleshooting; incl. tutorial, library authoring, concurrency, C/Zig extensions, SRFI support, editors, migrating, security, deployment |
| Procedures | `docs/procedures/` | 20 + index | Per-category API reference (numbers, lists, strings, SRFI-1/13/18/133/170/254, syntax forms, extensions, …) |
| Cookbook | `docs/cookbook/` | 10 + index | Task recipes: REST API, HTTP client, HTML templates, JSON, CSV, SQLite, config files, concurrency, testing, CLI tool |
| Ecosystem | `docs/ecosystem/` | 21 + index | thottam (package manager) + one page per kaappi-* library |
| Top-level | `docs/*.md` | 7 | glossary, stability, community, faq, conformance, book, cheatsheet (PDF viewer page, nav under Guide → Language) |

Files in `docs/` that are not nav pages:

- `docs/install.sh` — the `curl | bash` installer served at kaappi-lang.org/install.sh; copied verbatim into the built site. Always fetches the latest GitHub release.
- `docs/wasm/kaappi.wasm` — the WASM binary powering playground and tour. **Gitignored** (kept out of history); `scripts/fetch-wasm.sh` downloads it from the kaappi release matching `kaappi_version`, verified against the release SHA256SUMS. CI fetches it before deploy; run the script once locally before `mkdocs serve`.
- `docs/assets/kaappi-book.pdf` — the book PDF embedded by the `/book/` viewer. **Gitignored**, same pattern: `scripts/fetch-book.sh` downloads it from the kaappi-book release matching `book_version` in mkdocs.yml, verified against that release's SHA256SUMS. After a book release, bump `book_version` and push — the deploy picks it up. (The page's download link points at `releases/latest` and needs no bump; `docs/assets/book-cover.png` stays committed.)
- `docs/assets/book-3d.webp` — the angled 3D paperback in the landing page's book band. **Committed** (like `book-cover.png`). Regenerate with `scripts/generate-book-3d.py`: it renders `../kaappi-book/build/cover.pdf`, crops the front panel, hands it to the Gemini API (`gemini-3-pro-image`) as an image reference, and masks the result so it dissolves into the band's `#180E09`. Only needed if the cover art changes — a page-count bump alone doesn't warrant it. Needs `GEMINI_API_KEY`; pass `--raw FILE` to re-mask an existing render without calling the API.
- `docs/assets/kaappi-cheatsheet.pdf` — two-page A4 quick reference (language + CLI/REPL/thottam), embedded by the `/cheatsheet/` page (`docs/cheatsheet.md`, nav: Guide → Language, book-viewer pattern) and linked from the download page, the language guide, and a landing-page card. **Committed** (small-asset pattern — the inverse of the fetched book PDF). Source in `cheatsheet/`; rebuild with `make -C cheatsheet` (XeLaTeX from TeX Live; Space Grotesk + JetBrains Mono are bundled in `cheatsheet/fonts/`, the Source Sans 3 body font loads from the sibling `../kaappi-book/fonts/` checkout, and the version stamp reads `kaappi_version` from mkdocs.yml — always build via the Makefile, which also handles fontspec's cwd-relative paths and the two-pass TikZ bands). The crema page background is intentional brand identity, not wasted ink. Sheet snippets are NOT covered by the docs-samples sweep — verify `;=>` claims by hand against the kaappi binary when editing (see the omissions comment atop the .tex before adding content).
- `docs/stylesheets/extra.css` — design bridge into content pages (see Styling).
- `docs/assets/` — `logo.svg`, `favicon.png`.
- `docs/ideas.md` and `docs/errata-corrected-r7rs.pdf` — excluded from the build via `exclude_docs` in mkdocs.yml (internal notes / local R7RS spec copy).

Nav gotcha: the Tour nav entry links to the absolute URL
`https://kaappi-lang.org/tour/`, not to `tour.md` — which is therefore
declared in `not_in_nav` in mkdocs.yml so the omitted-page warning
doesn't fail the strict build.

## Playground and Tour

Full-page client-side apps built into the MkDocs site:

- `docs/index.md`, `docs/playground.md`, `docs/tour.md` are frontmatter-only
  stubs; their `template:` key selects the matching template in `overrides/`,
  which contains all markup, CSS, and JS.
- Code editing uses CodeMirror 6 with Scheme highlighting (Kaappi palette) via
  the committed bundle `docs/js/codemirror-bundle.mjs`. Regenerate it and
  `wasi-shim-bundle.mjs` with `scripts/build-bundles.sh` (npm + esbuild; it
  self-verifies the export surface and runs `kaappi.wasm` through the fresh
  shim). Keep `codemirror` pinned at 6.0.1, and load the playground in a
  browser before committing regenerated bundles.
- Execution is fully client-side in `playground-worker.js`, which fetches
  `wasm/kaappi.wasm` and instantiates it against `wasi-shim-bundle.mjs`. It
  feature-detects the WASM's exports and picks one of two paths:
  - **Stepped** (preferred) — when the binary exports the bounded-step entry
    point (kaappi#2283: `kaappi_step_alloc`/`setup`/`run`/`stop`/`reset`), the
    worker pumps `kaappi_step_run(budget)` in a loop: run a chunk of bytecode,
    flush streamed stdout/stderr to the page, yield, honor a cooperative **Stop**
    button, enforce a generous wall-clock backstop (30 s) and an output cap, then
    repeat. This is what powers the real Stop button and lets a long,
    constant-space program keep running and streaming instead of dying at 5 s.
  - **Batch** (fallback) — an older binary without those exports runs the classic
    way: the editor content is written as `program.scm` in a virtual FS and a
    single blocking WASI `_start` runs it to completion. No mid-run streaming or
    cooperative stop; `kp-runner.mjs`'s hard-kill timeout is the only guard.
  The site is safe to deploy against a released WASM that predates the step entry
  point — it runs batch and upgrades to stepped automatically once `update-wasm`
  syncs a release that ships the exports. `kp-runner.mjs` owns the worker
  lifecycle and the `run(code, {onStdout, onStderr}) -> Promise` / `stop()` API.
- The tour's 12 lessons live in the `LESSONS` array in `docs/js/tour-lessons.mjs`
  (dynamically imported by `overrides/tour.html`); the playground's example
  programs are likewise in `docs/js/playground-examples.mjs`.
- `overrides/partials/header.html` customizes Material's header (dark/light
  toggle moved to the far right).

## Release checklist

After each kaappi release (cut with the `/github-release` skill in the core repo),
the core repo's Step 11 triggers the `update-wasm` workflow in this repo. It
downloads the released `kaappi.wasm`, verifies its SHA256, bumps `kaappi_version`
and the count variables (`builtin_count`, `srfi_count`, `srfi_builtin`,
`srfi_portable` — extracted from the release tag's CONFORMANCE.md in the core
repo) in `mkdocs.yml`, tags the merge `docs-vX.Y.Z`, and deploys. Every count
the site states renders from those variables (markdown via `{{ var }}` with
`render_macros: true`, home.html via `config.extra`), so no count is
hand-edited per release anymore.

The `docs-vX.Y.Z` tags double as a version ledger over the docs history:
`git log docs-v0.22.3..docs-v0.23.0` lists every docs change from that
release's era, and `git tag --merged <sha> -l 'docs-v*' | sort -V | tail -1`
reports the kaappi version current when an arbitrary docs commit landed
(tags exist from v0.11.1 on).

One manual step remains: after `update-wasm` bumps `kaappi_version`, run
`make -C cheatsheet` locally and commit the refreshed
`docs/assets/kaappi-cheatsheet.pdf` — the sheet's version stamp comes from
mkdocs.yml at build time, and CI cannot rebuild it (no TeX toolchain). If
the release changed the language surface, CLI/REPL commands, or thottam
behavior, update the sheet's content too and re-verify its `;=>` claims
against the new binary (they are not covered by the sample sweep).

`docs/install.sh` and the download-table links target `releases/latest`, so
they normally need no per-release changes.

## Build

```bash
pip install -r requirements.txt   # one-time setup (pinned versions)
scripts/fetch-wasm.sh          # populate the gitignored playground WASM (once per clone / version bump)
scripts/fetch-book.sh          # populate the gitignored embedded book PDF (same cadence)
mkdocs serve                   # local dev server at http://127.0.0.1:8000
mkdocs build                   # build to site/
mkdocs build --strict          # build with strict link checking
```

Strict mode fails on any warning, including broken anchors (`validation:`
in mkdocs.yml checks link anchors, not just pages). Renamed or removed
pages must get an entry in the `redirects` plugin's `redirect_maps`.

`mkdocs.yml` has `watch: overrides`, but in practice `mkdocs serve` does not
reliably hot-reload edits to `overrides/` templates — restart the serve
process if template changes don't show up. `.claude/launch.json` defines a
`kaappi-docs` preview server that runs `mkdocs serve` on port 8000.

## CI and deploy

- `.github/workflows/ci.yml` — one workflow, two jobs:
  - **build** (every push/PR to `main`): runs `mkdocs build --strict` (fails on
    broken links/anchors). `docs/procedures/index.md` is **generated** from the
    subpages — each category is a `{{ procedures_table("page.md") }}` macro call
    (see `main.py`) that reads the `### name { #anchor }` headings (and inline
    table-row anchors) plus their `<!-- index: arity | description -->` metadata
    comment. To add/remove a procedure, edit only the subpage (heading +
    metadata); the index regenerates. A heading missing its metadata comment
    fails the build (macros `on_error_fail`). Special forms use
    `procedures_table(page, kind="form")` (2-column).
  - **deploy** (push to `main` only, `needs: build`): `mkdocs gh-deploy --force
    --strict` builds and pushes to the `gh-pages` branch, so a failing build
    never publishes. GitHub Pages serves `gh-pages` at kaappi-lang.org.
- `.github/workflows/update-wasm.yml` — `workflow_dispatch` only; syncs the
  playground WASM from a kaappi release (see Release checklist). Shares a
  `pages` concurrency group with `ci.yml` so the two never race on `gh-pages`.
- `.github/workflows/docs-samples.yml` — weekly (+ manual) **sample sweep**:
  runs every code sample on the site against the latest released kaappi
  binary via `scripts/sweep/` (live redis/postgres services included) and
  fails on any drifted `;=>` claim. Non-blocking — independent of deploy.
  When editing samples, run the matching section locally first:
  `scripts/sweep/run.sh guide` (see `scripts/sweep/README.md`; local runs
  want `KAAPPI_WS=~/kaappi` for workspace-only libraries).

Normal workflow: edit markdown in `docs/`, commit, push — CI validates and,
if the build passes, deploys automatically.

## Styling

The visual identity ("Dark Roast": coffee browns/ambers, Space Grotesk
headings, the `⇒` motif) is expressed on the landing page in
`overrides/home.html`. The palette itself lives in
`docs/stylesheets/extra.css`: it defines the `--kp-*` design tokens (single
source, consumed by the playground/tour/home templates via `var(--kp-*)`)
and bridges the identity into content pages by overriding Material's CSS
variables. Change brand colors in `extra.css` — the teal/amber palette in
`mkdocs.yml` is effectively overridden there, not honored.

## Kaappi Reference Sources

When writing about Kaappi features, verify against these sources (not from memory).
All paths are relative to this repo root (`kaappi.github.io/`):

- **Kaappi source code**: `../kaappi/` — the Zig implementation
  - `../kaappi/src/` — core runtime, compiler, VM, GC, primitives (~100k lines)
  - `../kaappi/lib/` — portable Scheme SRFI libraries (.sld files)
  - `../kaappi/docs/dev/` — architecture, IR, LLVM backend docs
  - `../kaappi/CONFORMANCE.md` — R7RS compliance details
  - `../kaappi/CLAUDE.md` — detailed build options, architecture, coding patterns
- **Book source**: `../kaappi-book/` — XeLaTeX book teaching Kaappi Scheme
  - `../kaappi-book/chapters/` — one .tex per chapter (ch01–ch18, appendix-a–g)
  - `../kaappi-book/CLAUDE.md` — book structure, writing guidelines, LaTeX conventions
- **Wiki**: `../wiki/` — Scheme language reference

## Conventions

- CLI examples use `kaappi` (not `zig build run --`); assume user has installed per guide
- REPL examples use `kaappi>` prompt and `;=>` for results
- Procedure subpages use `###` per procedure with `{ #anchor-id }` for explicit anchors,
  each followed by an `<!-- index: arity | description -->` comment that feeds the
  generated `procedures/index.md` table (see the CI section)
- Procedure anchor convention (the `{ #anchor }` ids; the `procedures_table` macro
  depends on them, so match these when adding a procedure):
  - `?` predicate: normally removed (`pair?` → `#pair`), but `-pred` when the
    bare name is itself a procedure — `exact?` → `#exact-pred` (because `exact`
    exists), likewise `eof-object?` → `#eof-object-pred`
  - `!` mutator: normally removed (`set-car!` → `#set-car`), `-mut` on collision
    (`bytevector-copy!` → `#bytevector-copy-mut`)
  - `->` becomes `-to-` (`string->list` → `#string-to-list`)
  - leading `%` stripped (`%make-record-type` → `#make-record-type`)
  - bare operators are spelled out: `+`→`#plus`, `-`→`#minus`, `*`→`#star`,
    `/`→`#slash`; numeric relationals take a `num-` prefix: `=`→`#num-equal`,
    `<`→`#num-lt`, `>`→`#num-gt`, `<=`→`#num-le`, `>=`→`#num-ge`
  - type-prefixed comparison predicates drop `?` and spell the operator
    (`lt`/`le`/`gt`/`ge`/`eq`): `string<?`→`#string-lt`, `char>=?`→`#char-ge`,
    `string=?`→`#string-eq`
  - `/` inside a name: `floor/`→`#floor-div`, `call/cc`→`#callcc`
  - `*` as a suffix becomes `-star` (`cons*`→`#cons-star`)
  - genuine collisions beyond these are disambiguated case-by-case — check
    existing pages, and the CI script is the source of truth
- `!!! note` admonitions for edge cases (sparingly)
- Cross-references use relative markdown links: `./page.md#anchor`
- Landing page uses "600+" for procedure count (not an exact number that drifts)
- Guide pages link to procedure reference for detailed docs
- Site copy uses Latin script only (international audience); the kaappi =
  "coffee" (Malayalam/Tamil) origin is always written romanized
- Dev docs live in the main kaappi repo (`docs/dev/`), not here
