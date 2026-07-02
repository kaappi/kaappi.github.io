#!/usr/bin/env python3
"""Check that docs/procedures/index.md stays in sync with its subpages.

The index is a hand-curated table (name, arity, description) with one row
per procedure. Subpages document procedures under headings of the form

    ### `procedure-name` { #anchor-id }

or, for compact groups (e.g. SRFI-1's `first`..`tenth`), as table rows
carrying an inline `{ #anchor-id }` attribute.

This script fails (exit 1) when the two drift apart:

  1. a subpage has a `### ... { #anchor }` procedure heading the index
     doesn't link to, or
  2. the index links to an anchor that doesn't exist in the subpage
     (explicit `{ #anchor }` anywhere, or a heading's auto-generated slug).

Run from the repo root:  python3 scripts/check_procedures_index.py
"""

import re
import sys
from pathlib import Path

PROCEDURES_DIR = Path(__file__).resolve().parent.parent / "docs" / "procedures"

PROC_HEADING_RE = re.compile(r"^### `?(.+?)`? *\{ *#([A-Za-z0-9_-]+) *\}", re.MULTILINE)
EXPLICIT_ANCHOR_RE = re.compile(r"\{ *#([A-Za-z0-9_-]+) *\}")
ANY_HEADING_RE = re.compile(r"^#{2,4} +(.+?)(?: *\{.*\})? *$", re.MULTILINE)
INDEX_LINK_RE = re.compile(r"\]\((?:\./)?([a-z0-9-]+\.md)#([A-Za-z0-9_-]+)\)")


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
        for name, anchor in PROC_HEADING_RE.findall(text):
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
            "\nEvery `### name { #anchor }` heading in docs/procedures/*.md "
            "needs a matching link in index.md, and every index link needs "
            "an existing target anchor."
        )
        return 1

    print(
        f"procedures/index.md OK: {len(index_links)} index links, "
        f"{len(procedures)} procedure headings, no drift."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
