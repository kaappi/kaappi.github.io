#!/usr/bin/env python3
"""Check that docs/procedures/index.md stays in sync with its subpages.

The index is a hand-curated table (name, arity, description) with one row
per procedure. Subpages document procedures under headings of the form

    ### `procedure-name` { #anchor-id }

or, for compact groups (e.g. SRFI-1's `first`..`tenth`), as table rows
carrying an inline `{ #anchor-id }` attribute.

This script fails (exit 1) when the two drift apart:

  1. a subpage has a procedure the index doesn't link to — either a
     `### ... { #anchor }` heading or a table row with an inline
     `{ #anchor }` (e.g. SRFI-1's `first`..`tenth`) — or
  2. the index links to an anchor that doesn't exist in the subpage
     (explicit `{ #anchor }` anywhere, or a heading's auto-generated slug).

Run from the repo root:  python3 scripts/check_procedures_index.py
"""

import re
import sys
from pathlib import Path

PROCEDURES_DIR = Path(__file__).resolve().parent.parent / "docs" / "procedures"

# Pages whose index.md table is generated at build time from inline
# `<!-- index: arity | description -->` metadata (see main.py's procedures_table
# macro). Their links live in the macro output, not the index.md source, so
# they're excluded from the source-link check below — the macro fails the build
# if a heading is missing its metadata comment. As categories migrate to
# generation, add them here.
GENERATED_PAGES = {
    "numbers.md", "pairs-and-lists.md", "strings.md", "characters.md",
    "vectors.md", "bytevectors.md", "ports-and-io.md", "control-flow.md",
    "type-checking.md", "system.md", "srfi-13.md", "srfi-133.md",
    "threads.md", "hash-tables.md", "extensions.md", "other.md",
}

PROC_HEADING_RE = re.compile(r"^### `?(.+?)`? *\{ *#([A-Za-z0-9_-]+) *\}", re.MULTILINE)
EXPLICIT_ANCHOR_RE = re.compile(r"\{ *#([A-Za-z0-9_-]+) *\}")
ANY_HEADING_RE = re.compile(r"^#{2,4} +(.+?)(?: *\{.*\})? *$", re.MULTILINE)
INDEX_LINK_RE = re.compile(r"\]\((?:\./)?([a-z0-9-]+\.md)#([A-Za-z0-9_-]+)\)")
# Compact procedures (e.g. SRFI-1's first..tenth) are documented as table
# rows carrying an inline { #anchor } rather than a ### heading. Match the
# first backticked cell as the name so these are index-required too, and
# deleting such a row from index.md is caught (not just a dangling link).
TABLE_ROW_ANCHOR_RE = re.compile(
    r"^\s*\|\s*`([^`]+)`.*?\{ *#([A-Za-z0-9_-]+) *\}", re.MULTILINE
)


def slugify(heading: str) -> str:
    """Approximate the toc extension's auto-generated anchor for a heading."""
    s = heading.strip().lower().replace("`", "")
    s = re.sub(r"[^\w\- ]", "", s)
    return re.sub(r"[\s]+", "-", s).strip("-")


def main() -> int:
    index_path = PROCEDURES_DIR / "index.md"
    index_links = set(INDEX_LINK_RE.findall(index_path.read_text()))

    procedures = {}  # (page, anchor) -> procedure name, from ### headings
    all_anchors = set()  # (page, anchor), every anchor a page defines
    for page in sorted(PROCEDURES_DIR.glob("*.md")):
        if page.name == "index.md":
            continue
        text = page.read_text()
        if page.name not in GENERATED_PAGES:
            for name, anchor in PROC_HEADING_RE.findall(text):
                procedures[(page.name, anchor)] = name
            for name, anchor in TABLE_ROW_ANCHOR_RE.findall(text):
                procedures[(page.name, anchor)] = name
        for anchor in EXPLICIT_ANCHOR_RE.findall(text):
            all_anchors.add((page.name, anchor))
        for heading in ANY_HEADING_RE.findall(text):
            all_anchors.add((page.name, slugify(heading)))

    errors = []

    for page, anchor in sorted(set(procedures) - index_links):
        errors.append(
            f"not in index: `{procedures[(page, anchor)]}` ({page}#{anchor})"
        )

    for page, anchor in sorted(index_links - all_anchors):
        errors.append(f"index links to missing anchor: {page}#{anchor}")

    if errors:
        print(f"procedures/index.md is out of sync ({len(errors)} problems):")
        for e in errors:
            print(f"  - {e}")
        print(
            "\nEvery procedure in docs/procedures/*.md (a `### name { #anchor }` "
            "heading or a table row with an inline `{ #anchor }`) needs a "
            "matching link in index.md, and every index link needs an "
            "existing target anchor."
        )
        return 1

    generated = ", ".join(sorted(GENERATED_PAGES)) or "none"
    print(
        f"procedures/index.md OK: {len(index_links)} hand-listed index links, "
        f"{len(procedures)} procedure entries, no drift "
        f"(generated pages, checked by the build: {generated})."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
