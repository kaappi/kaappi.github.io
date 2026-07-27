#!/usr/bin/env bash
# Regenerate the vendored browser bundles for the playground and tour:
#   docs/js/codemirror-bundle.mjs — CodeMirror 6 editor + Scheme mode (minified ESM)
#   docs/js/wasi-shim-bundle.mjs  — @bjorn3/browser_wasi_shim (minified ESM)
#
# The bundles are committed so the site has no CDN dependency (commit a8c602a
# eliminated esm.sh). Run this only to pick up upstream fixes or change the
# export surface — normal site work never needs it.
#
# Pins: codemirror stays at 6.0.1 (the CM6 meta-package; `@6` historically
# resolved to CM5 on esm.sh, and 6.0.1 is the only 6.x release). The other
# pins are simply the versions verified when this script was last run —
# bumping them is fine as long as the self-verification below passes AND you
# load the playground in a browser before committing new bundles.
#
# Usage: scripts/build-bundles.sh
# Requires: node + npm. If docs/wasm/kaappi.wasm is present (fetch-wasm.sh),
# the WASI bundle is verified by actually executing the interpreter through it.
set -euo pipefail

cd "$(dirname "$0")/.."
docsdir=$(pwd)

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

cat > "$tmp/package.json" <<'EOF'
{
  "name": "kaappi-docs-bundles",
  "private": true,
  "dependencies": {
    "codemirror": "6.0.1",
    "@codemirror/state": "^6.0.0",
    "@codemirror/language": "^6.0.0",
    "@lezer/highlight": "^1.0.0",
    "@codemirror/legacy-modes": "6.5.3",
    "@bjorn3/browser_wasi_shim": "0.4.2"
  },
  "devDependencies": {
    "esbuild": "0.28.1"
  }
}
EOF

# Entry points reproduce the export surface the pages rely on
# (kp-editor.mjs destructures the CodeMirror names; playground-worker.js
# destructures the WASI names).
cat > "$tmp/cm-entry.mjs" <<'EOF'
export { basicSetup, EditorView } from "codemirror";
export { EditorState } from "@codemirror/state";
export { StreamLanguage, HighlightStyle, syntaxHighlighting } from "@codemirror/language";
export { tags } from "@lezer/highlight";
export { scheme } from "@codemirror/legacy-modes/mode/scheme";
EOF

cat > "$tmp/wasi-entry.mjs" <<'EOF'
export { WASI, File, OpenFile, ConsoleStdout, PreopenDirectory } from "@bjorn3/browser_wasi_shim";
EOF

echo "Installing pinned packages ..."
(cd "$tmp" && npm install --no-audit --no-fund --loglevel=error)

echo "Bundling ..."
esbuild="$tmp/node_modules/.bin/esbuild"
"$esbuild" "$tmp/cm-entry.mjs" --bundle --minify --format=esm --target=es2022 \
    --outfile="$tmp/codemirror-bundle.mjs" --log-level=warning
"$esbuild" "$tmp/wasi-entry.mjs" --bundle --minify --format=esm --target=es2022 \
    --outfile="$tmp/wasi-shim-bundle.mjs" --log-level=warning

echo "Verifying ..."
cat > "$tmp/verify.mjs" <<EOF
import * as cm from "./codemirror-bundle.mjs";
import * as wasi from "./wasi-shim-bundle.mjs";
import { readFileSync, existsSync } from "node:fs";

const need = (mod, names, label) => {
  for (const n of names) if (!(n in mod)) throw new Error(label + " missing export: " + n);
};
need(cm, ["EditorState", "EditorView", "HighlightStyle", "StreamLanguage",
          "basicSetup", "scheme", "syntaxHighlighting", "tags"], "codemirror-bundle");
need(wasi, ["WASI", "File", "OpenFile", "ConsoleStdout", "PreopenDirectory"], "wasi-shim-bundle");

// DOM-free functional smoke of the pieces kp-editor.mjs uses at setup time.
cm.HighlightStyle.define([{ tag: cm.tags.keyword, color: "#fff" }]);
cm.StreamLanguage.define(cm.scheme);

// If the playground WASM is around, run the interpreter through the fresh
// shim exactly the way playground-worker.js does.
const wasmPath = "${docsdir}/docs/wasm/kaappi.wasm";
if (existsSync(wasmPath)) {
  const mod = await WebAssembly.compile(readFileSync(wasmPath));
  const out = [];
  const fds = [
    new wasi.OpenFile(new wasi.File([])),
    wasi.ConsoleStdout.lineBuffered(l => out.push(l)),
    wasi.ConsoleStdout.lineBuffered(l => out.push(l)),
    new wasi.PreopenDirectory(".", [
      ["program.scm", new wasi.File(new TextEncoder().encode(
        '(display (+ 1 2)) (newline)'))],
    ]),
  ];
  const w = new wasi.WASI(["kaappi", "program.scm"], [], fds);
  const instance = await WebAssembly.instantiate(mod, { wasi_snapshot_preview1: w.wasiImport });
  try { w.start(instance); } catch (e) { if (e.code !== 0) throw e; }
  if (out.join("\n").trim() !== "3")
    throw new Error("kaappi.wasm through new shim printed " + JSON.stringify(out));
  console.log("wasi-shim-bundle: kaappi.wasm executed OK");
} else {
  console.log("wasi-shim-bundle: kaappi.wasm not fetched, skipped execution check");
}
console.log("verify OK");
EOF
node "$tmp/verify.mjs"

mv -f "$tmp/codemirror-bundle.mjs" docs/js/codemirror-bundle.mjs
mv -f "$tmp/wasi-shim-bundle.mjs" docs/js/wasi-shim-bundle.mjs
ls -l docs/js/codemirror-bundle.mjs docs/js/wasi-shim-bundle.mjs

echo "Done. Before committing: mkdocs serve and exercise the playground and tour."
