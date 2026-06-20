# Kaappi Documentation Site

MkDocs Material site for [Kaappi](https://github.com/kaappi/kaappi), an R7RS Scheme implementation in Zig.

Served at **https://kaappi.github.io/**

## Source repo

The Kaappi implementation lives at [github.com/kaappi/kaappi](https://github.com/kaappi/kaappi).
Dev docs (architecture, testing, adding-features) remain in that repo under `docs/dev/`.

## Structure

```
docs/                  Markdown source (single source of truth)
├── index.md           Landing page trigger (uses custom template)
├── guide/             User guide (7 pages)
├── procedures.md      Procedure reference (554 procedures)
├── libraries.md       Library reference (51 SRFIs)
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
```

## Deploy

Automatic via GitHub Actions on push to `main`. The workflow runs `mkdocs gh-deploy --force`
which builds and pushes to the `gh-pages` branch. GitHub Pages serves from that branch.

## Editing docs

Edit markdown files in `docs/`, commit, push. The site regenerates automatically.
The landing page content is in `overrides/home.html` (HTML with MkDocs Material template tags).
