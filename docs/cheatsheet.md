---
render_macros: true
---

# Kaappi Cheatsheet

The whole language on one sheet of paper: R7RS-small syntax forms and
standard procedures across two A4 pages, plus the `kaappi` CLI, the
REPL's comma-commands, and thottam package management. Covers Kaappi
v{{ kaappi_version }}.

[Download the PDF](assets/kaappi-cheatsheet.pdf){ .md-button .md-button--primary }

Print it double-sided on A4 — "flip on long edge" — and it comes out as
a single sheet: syntax and tooling on the front, procedures on the back.

## View online

<div class="book-viewer" id="sheet-viewer">
  <div class="book-viewer__toolbar">
    <button type="button" class="book-viewer__toggle" onclick="kpToggleSheetViewer()">⛶ Maximize</button>
  </div>
  <iframe src="../assets/kaappi-cheatsheet.pdf" title="Kaappi Cheatsheet (PDF)"></iframe>
</div>

<script>
function kpToggleSheetViewer() {
  var el = document.getElementById('sheet-viewer');
  var btn = el.querySelector('.book-viewer__toggle');
  var maximized = el.classList.toggle('book-viewer--maximized');
  btn.textContent = maximized ? '✕ Close' : '⛶ Maximize';
  document.body.style.overflow = maximized ? 'hidden' : '';
}
</script>

Prefer hypertext? The same material, with detail: the
[Language Reference](guide/language.md), the
[Procedure Reference](procedures/index.md), and the
[CLI](guide/cli.md) and [REPL](guide/repl.md) guides.
