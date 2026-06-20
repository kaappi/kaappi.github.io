# Kaappi Documentation Site

MkDocs Material site for [Kaappi](https://github.com/kaappi/kaappi), an R7RS Scheme implementation in Zig.

Served at **https://kaappi.github.io/**

## Source repo

The Kaappi implementation lives at [github.com/kaappi/kaappi](https://github.com/kaappi/kaappi).
Local path: `/Users/bmuthuka/kaappi/kaappi`.
Dev docs (architecture, testing, adding-features) remain in that repo under `docs/dev/`.

## Structure

```
docs/                  Markdown source (single source of truth)
├── index.md           Landing page trigger (uses custom template)
├── guide/             User guide (9 pages)
│   ├── index.md       Guide overview with per-page descriptions
│   ├── installation.md
│   ├── first-program.md
│   ├── language.md    Language quick reference
│   ├── libraries.md   Importing and authoring (links to ../libraries.md for details)
│   ├── advanced.md    FFI, REPL commands, bytecode caching, debugger
│   ├── cli.md         Command-line reference
│   ├── tips.md        22 tips in 5 sections
│   └── troubleshooting.md  15 common errors with causes and fixes
├── procedures/        Procedure reference (19 subpages + index)
│   ├── index.md       Summary table with links to each subpage
│   ├── numbers.md     Numbers and Arithmetic (65 procs)
│   ├── pairs-and-lists.md
│   ├── srfi-1.md      SRFI-1 List Library (71 procs)
│   ├── strings.md
│   ├── srfi-13.md     SRFI-13 String Library
│   ├── characters.md
│   ├── vectors.md
│   ├── srfi-133.md    SRFI-133 Vector Library
│   ├── bytevectors.md
│   ├── ports-and-io.md
│   ├── control-flow.md
│   ├── type-checking.md  Type Checking and Equivalence
│   ├── hash-tables.md
│   ├── system.md
│   ├── syntax-forms.md
│   ├── threads.md     SRFI-18 Threads
│   ├── extensions.md  Kaappi Extensions (FFI + Fibers)
│   ├── other.md       Other Primitives (Lazy + Records + Random)
│   └── srfi-170.md    SRFI-170 Filesystem (67 procs)
├── libraries.md       Library authoring guide + full library list
└── benchmarks.md      Performance benchmarks
overrides/
└── home.html          Custom landing page template (Jinja2, extends main.html)
mkdocs.yml             MkDocs Material configuration
```

## Build

```bash
pip install mkdocs-material    # one-time setup
mkdocs serve                   # local dev server at http://127.0.0.1:8000
mkdocs build                   # build to site/
mkdocs build --strict          # build with strict link checking
```

## Deploy

Automatic via GitHub Actions on push to `main`. The workflow runs `mkdocs gh-deploy --force`
which builds and pushes to the `gh-pages` branch. GitHub Pages serves from that branch.

## Editing docs

Edit markdown files in `docs/`, commit, push. The site regenerates automatically.
The landing page content is in `overrides/home.html` (HTML with MkDocs Material template tags).

## Conventions

- CLI examples use `kaappi` (not `zig build run --`); assume user has installed per guide
- REPL examples use `kaappi>` prompt and `;=>` for results
- Procedure subpages use `###` per procedure with `{ #anchor-id }` for explicit anchors
- Anchor convention: `?` removed, `!` removed, `->` becomes `-to-`, `*` becomes `-star`
- `!!! note` admonitions for edge cases (sparingly)
- Cross-references use relative markdown links: `./page.md#anchor`
- Landing page uses "600+" for procedure count (not an exact number that drifts)
- Guide pages link to procedure reference for detailed docs
- The `docs/dev/` directory is excluded from the site build (`exclude_docs` in mkdocs.yml)
