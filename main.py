"""mkdocs-macros module: generate the procedures/index.md tables from subpages.

Each procedure subpage under docs/procedures/ carries its index metadata inline,
right after the heading:

    ### `name` { #anchor }
    <!-- index: <arity> | <one-line description> -->

`{{ procedures_table("numbers.md") }}` in index.md then emits the
`Procedure | Arity | Description` table for that page, so the index can't drift
from the subpages. Special forms (no arity) use `kind="form"` for a two-column
`Form | Description` table and leave the arity field empty. A heading missing
its `<!-- index: -->` comment raises at build time (fails the build via the
macros plugin's on_error_fail). Compact table-row procedures (an inline
`{ #anchor }` in a table row) carry `<!-- index: ... -->` on the same row.
"""

import re
from pathlib import Path

PROC_DIR = Path(__file__).resolve().parent / "docs" / "procedures"

_HEADING_RE = re.compile(r"^### `?(.+?)`? *\{ *#([A-Za-z0-9_-]+) *\}")
_ROW_ANCHOR_RE = re.compile(r"^\s*\|\s*`([^`]+)`.*?\{ *#([A-Za-z0-9_-]+) *\}")
_META_RE = re.compile(r"<!-- index: (.*?) \| (.*?) -->")


def _procedures(page):
    """Return [(name, anchor, arity, desc), ...] for a subpage, in page order."""
    lines = (PROC_DIR / page).read_text().split("\n")
    procs = []
    for i, line in enumerate(lines):
        heading = _HEADING_RE.match(line)
        row = None if heading else _ROW_ANCHOR_RE.match(line)
        if not heading and not row:
            continue
        name, anchor = (heading or row).group(1), (heading or row).group(2)
        if row:
            # A table row's first cell may be a signature (`(first pair)`) or a
            # bare name (`file-info:inode`). Take the operator from a signature,
            # otherwise the cell as-is.
            sig = re.match(r"\(([^\s)]+)", name)
            name = sig.group(1) if sig else name
        # Heading metadata is on one of the next few lines; row metadata is on
        # the same line (a trailing comment after the cell).
        meta = None
        if heading:
            for j in range(i + 1, min(i + 4, len(lines))):
                mm = _META_RE.search(lines[j])
                if mm:
                    meta = mm
                    break
        else:
            meta = _META_RE.search(line)
        if meta is None:
            raise ValueError(
                f"{page}: procedure `{name}` (#{anchor}) is missing its "
                f"`<!-- index: arity | description -->` comment"
            )
        procs.append((name, anchor, meta.group(1).strip(), meta.group(2).strip()))
    return procs


def define_env(env):
    @env.macro
    def procedures_table(page, kind="proc"):
        procs = _procedures(page)
        if kind == "form":
            header = "| Form | Description |\n|------|-------------|"
            body = [f"| [`{n}`]({page}#{a}) | {d} |" for n, a, _ar, d in procs]
        else:
            header = "| Procedure | Arity | Description |\n|-----------|-------|-------------|"
            body = [f"| [`{n}`]({page}#{a}) | {ar} | {d} |" for n, a, ar, d in procs]
        return header + "\n" + "\n".join(body)
