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
| Cookbook | `docs/cookbook/` | 6 + index | Task recipes: REST API, HTML templates, JSON, CSV, testing, CLI tool |
| Ecosystem | `docs/ecosystem/` | 19 + index | thottam (package manager) + one page per kaappi-* library |
| Top-level | `docs/*.md` | 4 | glossary, stability, community, faq |

Files in `docs/` that are not nav pages:

- `docs/install.sh` — the `curl | bash` installer served at kaappi-lang.org/install.sh; copied verbatim into the built site. Always fetches the latest GitHub release.
- `docs/wasm/kaappi.wasm` — committed WASM binary powering playground and tour.
- `docs/js/` — `codemirror-bundle.mjs` (prebuilt CodeMirror 6), `wasi-shim-bundle.mjs` (prebuilt @bjorn3/browser_wasi_shim), `playground-worker.js` (Web Worker that runs the WASM).
- `docs/stylesheets/extra.css` — design bridge into content pages (see Styling).
- `docs/assets/` — `logo.svg`, `favicon.png`.
- `docs/ideas.md` and `docs/errata-corrected-r7rs.pdf` — excluded from the build via `exclude_docs` in mkdocs.yml (internal notes / local R7RS spec copy).

Nav gotcha: the Tour nav entry links to the absolute URL
`https://kaappi-lang.org/tour/`, not to `tour.md`.

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
- The tour's 12 lessons live in the `LESSONS` array inside `overrides/tour.html`.
- `overrides/partials/header.html` customizes Material's header (dark/light
  toggle moved to the far right).

## Release checklist

After each kaappi release (cut with the `/github-release` skill in the core repo):

1. Replace `docs/wasm/kaappi.wasm` with the released `kaappi.wasm`
2. Bump `kaappi_version` in `mkdocs.yml` (single source of truth for all version references)

`docs/install.sh` and the download-table links target `releases/latest`, so
they normally need no per-release changes.

## Build

```bash
pip install mkdocs-material mkdocs-macros-plugin mkdocs-redirects   # one-time setup
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

- `.github/workflows/ci.yml` — `mkdocs build --strict` on every push/PR to
  `main`; fails on broken links and anchors. Also runs
  `scripts/check_procedures_index.py`, which fails if
  `docs/procedures/index.md` (the hand-curated per-procedure table) drifts
  from the `### name { #anchor }` headings in the procedure subpages —
  when adding or removing a procedure, update both.
- `.github/workflows/pages.yml` — on push to `main` (or manual dispatch), runs
  `mkdocs gh-deploy --force`, which builds and pushes to the `gh-pages`
  branch; GitHub Pages serves it at kaappi-lang.org.

Normal workflow: edit markdown in `docs/`, commit, push — the site deploys
automatically.

## Styling

The visual identity ("Dark Roast": coffee browns/ambers, Space Grotesk
headings, the `⇒` motif) is defined in `overrides/home.html`;
`docs/stylesheets/extra.css` bridges it into content pages by overriding
Material's CSS variables. The teal/amber palette in `mkdocs.yml` is
effectively overridden by `extra.css` — change colors there, not in
`mkdocs.yml`.

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
- Procedure subpages use `###` per procedure with `{ #anchor-id }` for explicit anchors
- Anchor convention: `?` removed, `!` removed, `->` becomes `-to-`, `*` becomes `-star`
- `!!! note` admonitions for edge cases (sparingly)
- Cross-references use relative markdown links: `./page.md#anchor`
- Landing page uses "600+" for procedure count (not an exact number that drifts)
- Guide pages link to procedure reference for detailed docs
- Site copy uses Latin script only (international audience); the kaappi =
  "coffee" (Malayalam/Tamil) origin is always written romanized
- Dev docs live in the main kaappi repo (`docs/dev/`), not here
