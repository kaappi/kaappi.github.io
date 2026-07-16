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
| Guide | `docs/guide/` | 18 + index | Installation through troubleshooting; incl. tutorial, library authoring, concurrency, C/Zig extensions, SRFI support, editors, migrating, security, deployment |
| Procedures | `docs/procedures/` | 19 + index | Per-category API reference (numbers, lists, strings, SRFI-1/13/18/133/170, syntax forms, extensions, …) |
| Cookbook | `docs/cookbook/` | 10 + index | Task recipes: REST API, HTTP client, HTML templates, JSON, CSV, SQLite, config files, concurrency, testing, CLI tool |
| Ecosystem | `docs/ecosystem/` | 19 + index | thottam (package manager) + one page per kaappi-* library |
| Top-level | `docs/*.md` | 4 | glossary, stability, community, faq |

Files in `docs/` that are not nav pages:

- `docs/install.sh` — the `curl | bash` installer served at kaappi-lang.org/install.sh; copied verbatim into the built site. Always fetches the latest GitHub release.
- `docs/wasm/kaappi.wasm` — the WASM binary powering playground and tour. **Gitignored** (kept out of history); `scripts/fetch-wasm.sh` downloads it from the kaappi release matching `kaappi_version`, verified against the release SHA256SUMS. CI fetches it before deploy; run the script once locally before `mkdocs serve`.
- `docs/assets/kaappi-book.pdf` — the book PDF embedded by the `/book/` viewer. **Gitignored**, same pattern: `scripts/fetch-book.sh` downloads it from the kaappi-book release matching `book_version` in mkdocs.yml, verified against that release's SHA256SUMS. After a book release, bump `book_version` and push — the deploy picks it up. (The page's download link points at `releases/latest` and needs no bump; `docs/assets/book-cover.png` stays committed.)
- `docs/js/` — `codemirror-bundle.mjs` (prebuilt CodeMirror 6), `wasi-shim-bundle.mjs` (prebuilt @bjorn3/browser_wasi_shim), `playground-worker.js` (Web Worker that runs the WASM), `kp-editor.mjs` / `kp-runner.mjs` (shared editor + worker-runner factories used by both the playground and tour), and the content modules `tour-lessons.mjs` (`LESSONS`) and `playground-examples.mjs` (`EXAMPLES`).
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
  the committed bundle `docs/js/codemirror-bundle.mjs`. If regenerating the
  bundle: pin `codemirror@6.0.1` (plain `@6` resolves to CM5) and don't use
  `?bundle` on esm.sh imports — it creates duplicate module instances that
  break `@lezer/highlight` tag matching.
- Execution is fully client-side: `playground-worker.js` fetches
  `wasm/kaappi.wasm`, instantiates it against `wasi-shim-bundle.mjs`, writes
  the editor content as `program.scm` in a virtual FS, and streams
  stdout/stderr back to the page.
- The tour's 12 lessons live in the `LESSONS` array in `docs/js/tour-lessons.mjs`
  (dynamically imported by `overrides/tour.html`); the playground's example
  programs are likewise in `docs/js/playground-examples.mjs`.
- `overrides/partials/header.html` customizes Material's header (dark/light
  toggle moved to the far right).

## Release checklist

After each kaappi release (cut with the `/github-release` skill in the core repo),
the core repo's Step 11 triggers the `update-wasm` workflow in this repo. It
downloads the released `kaappi.wasm`, verifies its SHA256, bumps `kaappi_version`
in `mkdocs.yml`, and deploys. No manual action needed.

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
  - `../kaappi/src/` — core runtime, compiler, VM, GC, primitives (~48k lines)
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
