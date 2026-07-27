#!/usr/bin/env python3
"""Run every Kaappi code sample in docs/guide/migrating.md through the
installed kaappi binary, asserting outputs (incl. the page's ;=> claims)."""
import re, subprocess, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _common import work, platformize, HAVE_FFI

PAGE = pathlib.Path(sys.argv[1])
SCRATCH = work("migrating")
LIB = SCRATCH / "libroot"

blocks = re.findall(r"```scheme\n(.*?)```", PAGE.read_text(), re.S)
assert len(blocks) == 17, f"expected 17 scheme blocks, got {len(blocks)}"

def kaappi_part(b, marker=";; Kaappi"):
    """Text from the (last) marker line to the end of the block."""
    lines = b.splitlines()
    idx = max(i for i, l in enumerate(lines) if l.startswith(marker))
    return "\n".join(lines[idx + 1 :]) + "\n"

def claims(text):
    """(code, expected) for each line carrying a ;=> claim; expected ends at ' — '."""
    out = []
    for line in text.splitlines():
        if ";=>" in line:
            code, exp = line.split(";=>", 1)
            out.append((code.strip(), exp.split(" — ")[0].strip()))
    return out

PRELUDE = "(import (scheme base) (scheme write))\n"
results, failures = [], []

def run(name, source, expect_stdout, extra_args=()):
    f = SCRATCH / f"mig-{name}.scm"
    source = platformize(source)
    f.write_text(source)
    r = subprocess.run(["kaappi", *extra_args, str(f)],
                       capture_output=True, text=True, timeout=60)
    got = r.stdout
    ok = r.returncode == 0 and got == expect_stdout
    (results if ok else failures).append(
        f"{name}: exit={r.returncode}\n--- got ---\n{got}{r.stderr}--- want ---\n{expect_stdout}")
    return ok

def wr(expr, res):  # write+newline a claim
    return f"(write {expr}) (newline)\n", f"{res}\n"

# -- b0: import comparison — the import line must simply succeed
run("b0-imports", kaappi_part(blocks[0]) + '(display "ok")(newline)\n', "ok\n")

# -- b1: define-library in my-lib/utils.sld, then import and call it
LIB.mkdir(exist_ok=True)
(LIB / "my-lib").mkdir(exist_ok=True)
(LIB / "my-lib" / "utils.sld").write_text(kaappi_part(blocks[1], ";; Kaappi ("))
run("b1-deflib", PRELUDE + "(import (my-lib utils))\n(write (my-func 4)) (newline)\n",
    "16\n", extra_args=["--lib-path", str(LIB)])

# -- b2: add1 with unless-guard; happy path and error path
src = PRELUDE + kaappi_part(blocks[2]) + \
    "(write (add1 2)) (newline)\n" + \
    "(write (guard (e (#t 'caught)) (add1 \"x\"))) (newline)\n"
run("b2-add1", src, "3\ncaught\n")

# -- b3: SRFI-69 hash tables — the block's own bare call self-prints
# (kaappi write-echoes top-level expression values in file mode)
run("b3-srfi69", PRELUDE + kaappi_part(blocks[3]), "1\n")

# -- b4: match comparison (regression of this morning's fix)
body = kaappi_part(blocks[4], ";; Kaappi (SRFI 257)")
imp, match_form = body.split("\n", 1)
src = PRELUDE + imp + "\n(define (f x)\n" + match_form + ")\n" + \
    '(write (f (list 1 2))) (newline)\n(write (f 5)) (newline)\n(write (f "s")) (newline)\n'
run("b4-match", src, "3\n10\n0\n")

# -- b5: simplify block claims
defn, calls = blocks[5].split("\n\n", 1)
src = PRELUDE + "(import (srfi 257))\n" + defn + "\n"
exp = ""
for code, res in claims(calls):
    w, e = wr(code, res); src += w; exp += e
run("b5-simplify", src, exp)

# -- b6: predicate comparison
body = kaappi_part(blocks[6], ";; Kaappi (SRFI 257)")
src = PRELUDE + "(import (srfi 257))\n(define (g p)\n" + body + ")\n" + \
    "(write (g (list 3 4))) (newline)\n(write (g (list 3 'a))) (newline)\n"
run("b6-pred", src, "7\nnot-two-numbers\n")

# -- b7: for/list -> map
body = kaappi_part(blocks[7])
imp, call = body.split("\n", 1)
src = PRELUDE + imp + "\n(write\n" + call + ") (newline)\n"
run("b7-map", src, "(1 4 9)\n")

# -- b8: define-library skeleton has a literal `...` body — structural; adapt
body = kaappi_part(blocks[8]).replace("(begin ...)", "(begin (define (my-func) 'ok))")
(LIB / "my-lib2").mkdir(exist_ok=True)
body = body.replace("(my-lib utils)", "(my-lib2 utils)")
(LIB / "my-lib2" / "utils.sld").write_text(body)
run("b8-deflib2", PRELUDE + "(import (my-lib2 utils))\n(write (my-func)) (newline)\n",
    "ok\n", extra_args=["--lib-path", str(LIB)])

# -- b9: SRFI-9 records
src = PRELUDE + kaappi_part(blocks[9]) + \
    "(define p (make-point 1 2))\n(write (list (point? p) (point-x p) (point-y p))) (newline)\n"
run("b9-records", src, "(#t 1 2)\n")

if not HAVE_FFI:
    print("b10/b11 (FFI): SKIPPED — no dynamic loading in this build")
HAVE = HAVE_FFI
# -- b10: Guile-comparison FFI block (contains its own ;=> claim)
body = kaappi_part(blocks[10])
lines, src, exp = body.splitlines(), PRELUDE, ""
for l in lines:
    if ";=>" in l:
        code, res = l.split(";=>")
        w, e = wr(code.strip(), res.strip()); src += w; exp += e
    else:
        src += l + "\n"
HAVE and run("b10-ffi", src, exp)

# -- b11: Chicken-comparison FFI block (no claim; add one)
src = PRELUDE + kaappi_part(blocks[11]) + "(write (c-sqrt 2.0)) (newline)\n"
HAVE and run("b11-ffi2", src, "1.4142135623730951\n")

# -- b12: call/ec with trailing ;=> -3 claim
body = blocks[12]
expr_lines = [l for l in body.splitlines() if not l.lstrip().startswith(";")]
expr = "\n".join(l.split(";=>")[0] for l in expr_lines if l.strip())
src = PRELUDE + "(write\n" + expr + ") (newline)\n"
run("b12-callec", src, "-3\n")

# -- b13: CL defun -> define
body = kaappi_part(blocks[13])
defn, call = body.rsplit("\n", 2)[0], body.strip().splitlines()[-1]
src = PRELUDE + defn + "\n(write " + call + ") (newline)\n"
run("b13-square", src, "25\n")

# -- b14: truthiness block — four ;=> claims
src, exp = PRELUDE, ""
for code, res in claims(blocks[14]):
    w, e = wr(code, res); src += w; exp += e
run("b14-truthy", src, exp)

# -- b15: iteration block — two Kaappi segments (map, do-loop)
segs, cur, mode = [], [], None
for l in blocks[15].splitlines():
    if l.startswith(";; Kaappi"):
        mode = "k"; cur = []; segs.append(cur)
    elif l.startswith(";;"):
        mode = None
    elif mode == "k":
        cur.append(l)
seg_map, seg_do = ["\n".join(s).strip() for s in segs]
run("b15a-map", PRELUDE + "(write " + seg_map + ") (newline)\n", "(1 4 9)\n")
run("b15b-do", PRELUDE + seg_do + "\n", "0\n1\n2\n3\n4\n")

# -- b16: guard around (/ 1 0)
run("b16-guard", PRELUDE + kaappi_part(blocks[16]) + "\n", "caught\n")

print(f"passed {len(results)}/{len(results) + len(failures)}")
for f in failures:
    print("\n=== FAIL", f)
sys.exit(1 if failures else 0)
