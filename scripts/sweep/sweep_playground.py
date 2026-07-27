#!/usr/bin/env python3
"""Verify the tour lessons and playground example programs.

These live as code strings in docs/js/tour-lessons.mjs (LESSONS) and
docs/js/playground-examples.mjs (EXAMPLES) and run in the browser against
the WASM build of the same interpreter, so the native binary verifies
them directly. Each program must run cleanly (exit 0, empty stderr), and
must not use capabilities the WASM build lacks (file I/O, FFI, OS
threads) — a lesson that only works natively is broken in the browser.
"""
import json, re, subprocess, sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _common import REPO, work

WD = work("playground")
FAILURES, PASSES = [], []

# The modules are ES modules; let node evaluate them rather than parsing
# JS with regexes.
dump = subprocess.run(
    ["node", "-e",
     "Promise.all(["
     f"import('{REPO}/docs/js/tour-lessons.mjs'),"
     f"import('{REPO}/docs/js/playground-examples.mjs')"
     "]).then(([t, p]) => {"
     "const lessons = t.LESSONS.map(l => ({name: l.title, code: l.code}));"
     "const examples = Object.entries(p.EXAMPLES)"
     ".map(([name, code]) => ({name, code}));"
     "console.log(JSON.stringify({lessons, examples}));})"],
    capture_output=True, text=True, timeout=60)
if dump.returncode != 0:
    print("could not evaluate the JS modules:", dump.stderr, file=sys.stderr)
    sys.exit(2)
data = json.loads(dump.stdout)

# capabilities absent from the WASM build (guide/deployment.md)
WASM_FORBIDDEN = re.compile(
    r"open-input-file|open-output-file|call-with-input-file"
    r"|call-with-output-file|with-input-from-file|with-output-to-file"
    r"|delete-file|file-exists\?|ffi-open|ffi-fn|thread-start!"
    r"|\(load ")

for kind, programs in [("lesson", data["lessons"]),
                       ("example", data["examples"])]:
    for prog in programs:
        slug = re.sub(r"\W+", "-", prog["name"].lower()).strip("-")
        name = f"{kind}-{slug}"
        m = WASM_FORBIDDEN.search(prog["code"])
        if m:
            FAILURES.append(
                f"{name}: uses {m.group(0)!r}, unavailable in the browser WASM build")
            continue
        f = WD / f"{name}.scm"
        f.write_text(prog["code"])
        try:
            r = subprocess.run(["kaappi", str(f)], cwd=WD, capture_output=True,
                               text=True, timeout=60)
        except subprocess.TimeoutExpired:
            FAILURES.append(f"{name}: TIMEOUT")
            continue
        if r.returncode != 0 or r.stderr.strip():
            FAILURES.append(
                f"{name}: exit {r.returncode}\n{r.stderr[:400]}")
        else:
            PASSES.append(name)

print(f"\npassed {len(PASSES)}:")
for p in PASSES:
    print("  ", p)
if FAILURES:
    print(f"\nFAILED {len(FAILURES)}:")
    for f in FAILURES:
        print("\n===", f)
sys.exit(1 if FAILURES else 0)
