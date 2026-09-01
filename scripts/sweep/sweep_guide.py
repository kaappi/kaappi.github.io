#!/usr/bin/env python3
"""Verify guide-page samples: REPL-transcript replay + cumulative file runs."""
import re, subprocess, sys, os, shutil, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _common import (WS, LIBM, DYLIB_EXT, HAVE_FFI, work, platformize,
                     lib_args, core_lib_args)
VER = subprocess.run(['kaappi', '--version'], capture_output=True,
                     text=True).stdout.strip()

DOCS = pathlib.Path(sys.argv[1])            # docs/guide
ONLY = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else None
ROOT = work("guide")
FAILURES, PASSES = [], []

def all_fences(page):
    out, lang, buf = [], None, []
    for line in (DOCS / page).read_text().splitlines():
        if lang is None and line.startswith("```"):
            lang, buf = line[3:].strip(), []
        elif lang is not None and line.rstrip() == "```":
            out.append((lang, buf))
            lang = None
        elif lang is not None:
            buf.append(line)
    return out

def scheme_blocks(page):
    return [b for l, b in all_fences(page) if l == "scheme"]

def assert_ordered(name, stdout, matchers):
    pos = 0
    for m in matchers:
        found = stdout.find(m, pos)
        if found < 0:
            FAILURES.append(f"{name}: missing (in order) {m!r}\n--- stdout ---\n{stdout[:4000]}")
            return False
        pos = found + len(m)
    return True

def repl_replay(name, blocks, extra_expect=()):
    """Rebuild a kaappi> transcript: prompts+continuations become stdin;
    a bare line is stdin data iff the previous expression called read/read-line;
    other bare lines and ;=> claims become ordered expected output."""
    stdin_lines, expect = [], []
    for block in blocks:
        pending_read = False
        for line in block:
            if line.startswith("kaappi> "):
                code = line[len("kaappi> "):]
                stdin_lines.append(code)
                pending_read = bool(re.search(r"\(read-line\)|\(read\)", code))
            elif re.match(r"\s*\.\.\.\s?", line):
                code = re.sub(r"^\s*\.\.\.\s?", "", line)
                stdin_lines.append(code)
                pending_read = pending_read or bool(re.search(r"\(read-line\)|\(read\)", code))
            elif ";=>" in line:
                expect.append(line.split(";=>", 1)[1].split(" — ")[0].strip())
            elif line.strip() == "":
                continue
            elif pending_read:
                stdin_lines.append(line)      # user-typed data
                pending_read = False
            else:
                expect.append(line.rstrip())  # printed output
    expect.extend(extra_expect)
    r = subprocess.run(["kaappi"], input="\n".join(stdin_lines) + "\n",
                       capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        FAILURES.append(f"{name}: exit {r.returncode}\n{r.stdout[-2000:]}{r.stderr[-2000:]}")
        return
    if assert_ordered(name, r.stdout, expect):
        PASSES.append(name)

def run_file(name, source, expect, cwd=None, args=(), rc=0, fixtures=None):
    wd = ROOT / name
    wd.mkdir(exist_ok=True)
    for fn, content in (fixtures or {}).items():
        (wd / fn).write_text(content)
    f = wd / "prog.scm"
    f.write_text(platformize(source))
    r = subprocess.run(["kaappi", *args, str(f)], cwd=cwd or wd,
                       capture_output=True, text=True, timeout=180)
    if r.returncode != rc:
        FAILURES.append(f"{name}: exit {r.returncode} (want {rc})\n{r.stdout[-1500:]}{r.stderr[-1500:]}")
        return
    if assert_ordered(name, r.stdout, expect):
        PASSES.append(name)

def claims_and_code(block_lines):
    """For plain blocks: code as-is; matchers from ;=> plus 'prints:' comments."""
    code, matchers = [], []
    for line in block_lines:
        if ";=>" in line:
            code.append(line.split(";=>")[0].rstrip())
            matchers.append(line.split(";=>", 1)[1].split(" — ")[0].strip())
        else:
            code.append(line)
            m = re.search(r";; prints: (.+)$", line)
            if m:
                matchers.append(m.group(1).strip())
    return "\n".join(code) + "\n", matchers

def cumulative_page(name, page, skip_idx=(), isolate=(), extra=None, fixtures=None):
    """Run a plain-block page as one program; isolate= blocks run alone."""
    blocks = scheme_blocks(page)
    src, matchers = "(import (scheme base) (scheme write))\n", []
    for i, b in enumerate(blocks):
        if i in skip_idx or i in isolate:
            continue
        c, m = claims_and_code(b)
        src += c
        matchers += m
    if extra:
        for code, exp in extra:
            src += code + "\n"
            matchers.append(exp)
    run_file(name, src, matchers, fixtures=fixtures)
    for i in isolate:
        c, m = claims_and_code(blocks[i])
        run_file(f"{name}-iso{i}", "(import (scheme base) (scheme write))\n" + c, m)

# ================= tutorial.md =================
if ONLY is None or "tutorial" in ONLY:
    blocks = scheme_blocks("tutorial.md")
    repl_blocks = [b for b in blocks if any(l.startswith("kaappi> ") for l in b)]
    plain = [b for b in blocks if not any(l.startswith("kaappi> ") for l in b)]
    # The piped REPL pre-buffers stdin for its form reader, so interactive
    # read/read-line transcripts can't be replayed by pipe (works in a real
    # tty) — verify those two samples in file mode with stdin instead.
    interactive = [b for b in repl_blocks
                   if any("(read-line)" in l or "(read)" in l for l in b)]
    repl_replay("tutorial-repl", [b for b in repl_blocks if b not in interactive])
    r = subprocess.run(
        ["kaappi", "/dev/stdin"], input="", capture_output=True, text=True)
    f1 = ROOT / "tut-readline.scm"
    f1.write_text('(import (scheme base))\n(display "Name: ")\n'
                  "(define name (read-line))\n"
                  '(display (string-append "Hello, " name "!"))\n(newline)\n')
    r = subprocess.run(["kaappi", str(f1)], input="Alice\n",
                       capture_output=True, text=True, timeout=60)
    if r.returncode == 0 and "Hello, Alice!" in r.stdout:
        PASSES.append("tutorial-readline")
    else:
        FAILURES.append(f"tutorial-readline: exit {r.returncode}\n{r.stdout}{r.stderr}")
    f2 = ROOT / "tut-read.scm"
    f2.write_text("(import (scheme base) (scheme write))\n"
                  "(define x (read))\n(write (car x)) (newline)\n")
    r = subprocess.run(["kaappi", str(f2)], input="(1 2 3)\n",
                       capture_output=True, text=True, timeout=60)
    if r.returncode == 0 and r.stdout.startswith("1"):
        PASSES.append("tutorial-read")
    else:
        FAILURES.append(f"tutorial-read: exit {r.returncode}\n{r.stdout}{r.stderr}")
    # the equivalence block and the with-input-from-file block are plain
    eq = next(b for b in plain if any("lambda (x)" in l for l in b))
    run_file("tutorial-let-equiv",
             "(import (scheme base) (scheme write))\n" + "\n".join(eq) + "\n",
             ["25", "25"])
    fio = next(b for b in plain if any("with-input-from-file" in l for l in b))
    run_file("tutorial-file-io",
             "(import (scheme base))\n" + "\n".join(fio) + "\n",
             ["line one", "line two"],
             fixtures={"data.txt": "line one\nline two\n"})

# ================= language.md =================
if ONLY is None or "language" in ONLY:
    # block 1 (raw strings) claims use write-format with escapes; verified in
    # the cumulative run like everything else. with-exception-handler block
    # isolated in case the non-continuable raise aborts the program.
    cumulative_page("language", "language.md",
        isolate=(),
        extra=[("(display \"end-of-page\") (newline)", "end-of-page")])

# ================= library-authoring.md =================
if ONLY is None or "libauth" in ONLY:
    bs = scheme_blocks("library-authoring.md")
    wd = ROOT / "libauth"
    (wd / "mylib").mkdir(parents=True, exist_ok=True)
    mathlib = next(b for b in bs if any("(mylib math)" in l and "define-library" in l for l in b))
    (wd / "mylib" / "math.sld").write_text("\n".join(mathlib) + "\n")
    prog = next(b for b in bs if any("(import (mylib math))" in l for l in b))
    c, m = claims_and_code(prog)
    (wd / "main.scm").write_text(c)
    r = subprocess.run(["kaappi", "main.scm"], cwd=wd, capture_output=True,
                      text=True, timeout=60)
    if r.returncode == 0 and assert_ordered("libauth-math", r.stdout, m):
        PASSES.append("libauth-math")
    elif r.returncode != 0:
        FAILURES.append(f"libauth-math: exit {r.returncode}\n{r.stdout}{r.stderr}")
    # nested import modifiers + features
    run_file("libauth-modifiers",
        "(import (scheme base) (scheme write))\n"
        "(import (scheme base)\n        (prefix (only (scheme char) char-upcase) c:))\n"
        "(write (c:char-upcase #\\a)) (newline)\n"
        "(let ((fs (features)))\n"
        "  (write (and (memq 'r7rs fs) (memq 'kaappi fs) #t))) (newline)\n",
        ["#\\A", "#t"])
    # cond-expand compat library
    compat = next(b for b in bs if any("(mylib compat)" in l for l in b))
    (wd / "mylib" / "compat.sld").write_text("\n".join(compat) + "\n")
    (wd / "compat-main.scm").write_text(
        "(import (scheme base) (mylib compat))\n(display platform-name) (newline)\n")
    r = subprocess.run(["kaappi", "compat-main.scm"], cwd=wd,
                      capture_output=True, text=True, timeout=60)
    if r.returncode == 0 and "kaappi" in r.stdout:
        PASSES.append("libauth-condexpand")
    else:
        FAILURES.append(f"libauth-condexpand: exit {r.returncode}\n{r.stdout}{r.stderr}")
    # include-based split library (fill the ... export)
    (wd / "big-part1.scm").write_text("(define (part1) 'one)\n")
    (wd / "big-part2.scm").write_text("(define (part2) 'two)\n")
    (wd / "mylib" / "big.sld").write_text(
        "(define-library (mylib big)\n  (export part1 part2)\n"
        "  (import (scheme base))\n"
        '  (include "big-part1.scm")\n  (include "big-part2.scm"))\n')
    (wd / "big-main.scm").write_text(
        "(import (scheme base) (scheme write) (mylib big))\n"
        "(write (list (part1) (part2))) (newline)\n")
    r = subprocess.run(["kaappi", "big-main.scm"], cwd=wd,
                      capture_output=True, text=True, timeout=60)
    if r.returncode == 0 and "(one two)" in r.stdout:
        PASSES.append("libauth-include")
    else:
        FAILURES.append(f"libauth-include: exit {r.returncode}\n{r.stdout}{r.stderr}")
    # search order: ./ beats ./lib/
    (wd / "mylib" / "prec.sld").write_text(
        "(define-library (mylib prec) (export whence) (import (scheme base))\n"
        "  (begin (define whence 'cwd)))\n")
    (wd / "lib" / "mylib").mkdir(parents=True, exist_ok=True)
    (wd / "lib" / "mylib" / "prec.sld").write_text(
        "(define-library (mylib prec) (export whence) (import (scheme base))\n"
        "  (begin (define whence 'libdir)))\n")
    (wd / "prec-main.scm").write_text(
        "(import (scheme base) (mylib prec))\n(display whence) (newline)\n")
    r = subprocess.run(["kaappi", "prec-main.scm"], cwd=wd,
                      capture_output=True, text=True, timeout=60)
    if r.returncode == 0 and "cwd" in r.stdout:
        PASSES.append("libauth-search-order")
    else:
        FAILURES.append(f"libauth-search-order: exit {r.returncode}\n{r.stdout}{r.stderr}")
    # cache status + fmt --check
    r = subprocess.run(["kaappi", "cache", "status"], capture_output=True,
                      text=True, timeout=60)
    (PASSES if r.returncode == 0 else FAILURES).append(
        "libauth-cache-status" if r.returncode == 0
        else f"libauth-cache-status: exit {r.returncode}\n{r.stdout}{r.stderr}")
    # exercise fmt + fmt --check as documented (canonicalize first — doc
    # snippets are wrapped for readability, not fmt-canonical)
    subprocess.run(["kaappi", "fmt", "mylib/math.sld"], cwd=wd,
                   capture_output=True, text=True, timeout=60)
    r = subprocess.run(["kaappi", "fmt", "--check", "mylib/math.sld"], cwd=wd,
                      capture_output=True, text=True, timeout=60)
    (PASSES if r.returncode == 0 else FAILURES).append(
        "libauth-fmt-check" if r.returncode == 0
        else f"libauth-fmt-check: exit {r.returncode}\n{r.stdout}{r.stderr}")

# ================= c-extensions.md =================
if (ONLY is None or "cext" in ONLY) and HAVE_FFI:
    text = (DOCS / "c-extensions.md").read_text()
    wd = ROOT / "cext" / "kaappi-mylib"
    (wd / "csrc").mkdir(parents=True, exist_ok=True)
    (wd / "lib" / "kaappi" / "mylib").mkdir(parents=True, exist_ok=True)
    (wd / "tests").mkdir(exist_ok=True)
    cblocks = re.findall(r"```c\n(.*?)```", text, re.S)
    mk = re.findall(r"```makefile\n(.*?)```", text, re.S)
    sb = scheme_blocks("c-extensions.md")
    (wd / "csrc" / "kaappi_mylib.c").write_text(cblocks[0])
    (wd / "Makefile").write_text(mk[0])
    ffisld = next(b for b in sb if any("(kaappi mylib ffi)" in l and "define-library" in l for l in b))
    (wd / "lib" / "kaappi" / "mylib" / "ffi.sld").write_text("\n".join(ffisld) + "\n")
    apisld = next(b for b in sb if any("(define-library (kaappi mylib)" in l for l in b))
    (wd / "lib" / "kaappi" / "mylib.sld").write_text("\n".join(apisld) + "\n")
    testb = next(b for b in sb if any("test" in l and "string-byte-length" in l for l in b)
                 or any('(display (add 40 2))' in l for l in b))
    (wd / "tests" / "test-mylib.scm").write_text("\n".join(testb) + "\n")
    r = subprocess.run(["make"], cwd=wd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        FAILURES.append(f"cext-make: exit {r.returncode}\n{r.stdout}{r.stderr}")
    else:
        PASSES.append("cext-make")
        # per the fixed Step 6: bare-name ffi-open resolves via ~/.kaappi/lib
        home_lib = pathlib.Path.home() / ".kaappi" / "lib" / f"libkaappi_mylib.{DYLIB_EXT}"
        shutil.copy(wd / f"libkaappi_mylib.{DYLIB_EXT}", home_lib)
        try:
            r = subprocess.run(["kaappi", "--lib-path", "./lib",
                                "tests/test-mylib.scm"],
                              cwd=wd, capture_output=True, text=True, timeout=60)
        finally:
            home_lib.unlink(missing_ok=True)
        if r.returncode == 0 and assert_ordered("cext-test", r.stdout, ["5.0", "2", "42"]):
            PASSES.append("cext-test")
        elif r.returncode != 0:
            FAILURES.append(f"cext-test: exit {r.returncode}\n{r.stdout}{r.stderr}")
    # direct-call block (pow claim) + callback block
    run_file("cext-direct",
        "(import (scheme base) (scheme write) (kaappi ffi))\n"
        '(define libm (ffi-open "libm.dylib"))\n'
        "(define c-sqrt (ffi-fn libm \"sqrt\" '(double) 'double))\n"
        "(define c-pow  (ffi-fn libm \"pow\"  '(double double) 'double))\n"
        "(write (c-sqrt 2.0)) (newline)\n(write (c-pow 2.0 10.0)) (newline)\n"
        "(define cb (ffi-callback (lambda (a b) (- a b)) '(pointer pointer) 'int))\n"
        "(ffi-callback-release cb)\n(ffi-close libm)\n(display 'done) (newline)\n",
        ["1.4142135623730951", "1024.0", "done"])

# ================= security.md =================
if ONLY is None or "security" in ONLY:
    wd = ROOT / "security"
    wd.mkdir(exist_ok=True)
    # runnable claims: validation, XSS escaping, FFI type-safety
    HAVE_FFI and run_file("security-run",
        "(import (scheme base) (scheme write) (kaappi template) (kaappi ffi))\n"
        '(define (validate-email s) (and (string? s) (> (string-length s) 0) (string-contains s "@")))\n'
        "(define (validate-positive-integer s) (let ((n (string->number s))) (and n (exact-integer? n) (positive? n))))\n"
        '(write (and (validate-email "a@b.c") #t)) (newline)\n'
        '(write (validate-email "nope")) (newline)\n'
        '(write (validate-positive-integer "42")) (newline)\n'
        '(define user-input "<b>hi</b>")\n'
        '(display (template-render-html "<p>{{.name}}</p>" `(("name" . ,user-input)))) (newline)\n'
        '(display (template-render "<p>{{.name}}</p>" `(("name" . ,user-input)))) (newline)\n'
        '(display (html-escape "<script>alert(\'xss\')</script>")) (newline)\n'
        '(define libm (ffi-open "libm.dylib"))\n'
        "(define c-abs (ffi-fn libm \"abs\" '(int) 'int))\n"
        "(write (c-abs 42)) (newline)\n"
        "(write (guard (e (#t 'type-error-raised)) (c-abs \"hello\"))) (newline)\n"
        "(define c-sqrt (ffi-fn libm \"sqrt\" '(double) 'double))\n"
        "(define (safe-sqrt x) (unless (and (number? x) (>= x 0)) (error \"sqrt: expected non-negative number\" x)) (c-sqrt x))\n"
        "(write (safe-sqrt 9)) (newline)\n"
        "(define (my-compare a b) 0)\n"
        "(define cb (ffi-callback my-compare '(pointer pointer) 'int))\n"
        "(ffi-callback-release cb)\n(ffi-close libm)\n"
        "(display 'ffi-done) (newline)\n",
        ["#t", "#f", "#t",
         "<p>&lt;b&gt;hi&lt;/b&gt;</p>", "<p><b>hi</b></p>",
         "&lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt;",
         "42", "type-error-raised", "3.0", "ffi-done"])
    # fragments (pg/web/tls/secrets) must at least pass `kaappi check`
    frag = "\n".join("\n".join(b) for b in scheme_blocks("security.md")
                     if any("pg-query" in l or "POST" in l or "tls-connect" in l
                            or "pg-connect" in l for l in b))
    (wd / "frags.scm").write_text(frag + "\n")
    r = subprocess.run(["kaappi", "check", "frags.scm"], cwd=wd,
                      capture_output=True, text=True, timeout=60)
    if not HAVE_FFI:
        print("security-frag-check: SKIPPED (no dynamic loading)")
    elif r.returncode == 0:
        PASSES.append("security-frag-check")
    else:
        FAILURES.append(f"security-frag-check: exit {r.returncode}\n{r.stdout}{r.stderr}")
    # sandbox-blocked matrix from the page's table
    BLOCKED = [
        ("file", '(open-input-file "/etc/hosts")'),
        ("ffi", '(import (kaappi ffi)) (ffi-open "libm.dylib")'),
        ("eval", "(eval '(+ 1 2) (interaction-environment))"),
        ("env", '(get-environment-variable "HOME")'),
        ("exit", "(exit 0)"),
        ("srfi170", "(import (srfi 170)) (file-info \".\" #t)"),
        ("threads", "(import (srfi 18)) (thread-start! (make-thread (lambda () 1)))"),
    ]
    for name, code in BLOCKED:
        f = wd / f"sb-{name}.scm"
        f.write_text(code + "\n")
        r = subprocess.run(["kaappi", "--sandbox", str(f)],
                          capture_output=True, text=True, timeout=60)
        combined = (r.stdout + r.stderr).lower()
        # gated capabilities are blocked either with an explicit sandbox
        # error or by being unbound entirely under --sandbox
        if r.returncode != 0 and ("sandbox" in combined
                                  or "undefined variable" in combined):
            PASSES.append(f"security-sandbox-{name}")
        else:
            FAILURES.append(
                f"security-sandbox-{name}: exit {r.returncode}\n{(r.stdout + r.stderr)[:300]}")
    # sandbox-allowed: display + fibers still work
    f = wd / "sb-ok.scm"
    f.write_text("(import (scheme base) (kaappi fibers))\n"
                 "(define ch (make-channel))\n"
                 "(spawn (lambda () (channel-send ch 'ok)))\n"
                 "(display (channel-receive ch)) (newline)\n")
    r = subprocess.run(["kaappi", "--sandbox", str(f)],
                      capture_output=True, text=True, timeout=60)
    if r.returncode == 0 and "ok" in r.stdout:
        PASSES.append("security-sandbox-allowed")
    else:
        FAILURES.append(f"security-sandbox-allowed: exit {r.returncode}\n{r.stdout}{r.stderr}")

# ================= concurrency.md =================
if ONLY is None or "concurrency" in ONLY:
    bs = scheme_blocks("concurrency.md")
    join = lambda idxs: "\n".join("\n".join(bs[i]) for i in idxs) + "\n"
    run_file("concurrency-fibers-threads",
             "(import (scheme base) (scheme write))\n" + join([0, 1, 2, 3, 4]),
             ["hello from fiber", "send-timed-out", "42", "42"])
    if core_lib_args() is None:
        print("concurrency-parallel: SKIPPED ((kaappi parallel) unavailable)")
    else:
        run_file("concurrency-parallel",
             "(import (scheme base) (scheme write))\n" + join([5]) +
             "(define (expensive-computation) (* 7 6))\n" +
             "\n".join(l.split(";=>")[0] for l in bs[6]) + "\n" +
             "(display 'pool-done) (newline)\n",
             ["(1 4 9 16 25)", "pool-done"],
             args=(core_lib_args() or []))

# ================= first-program.md =================
if ONLY is None or "first-program" in ONLY:
    bs = scheme_blocks("first-program.md")
    hello = next(b for b in bs if any("Hello, world!" in l for l in b))
    run_file("first-hello", "\n".join(hello) + "\n", ["Hello, world!"])
    stats = next(b for b in bs if any("define-library (mylib stats)" in l for l in b))
    mainb = next(b for b in bs
                 if b is not stats and any("(mylib stats))" in l for l in b))
    wd = ROOT / "first-stats"
    (wd / "mylib").mkdir(parents=True, exist_ok=True)
    (wd / "mylib" / "stats.sld").write_text("\n".join(stats) + "\n")
    (wd / "main.scm").write_text("\n".join(mainb) + "\n")
    r = subprocess.run(["kaappi", "main.scm"], cwd=wd, capture_output=True,
                      text=True, timeout=60)
    want = "Data:   (7 2 9 4 1 8 3 6 5)\nMean:   5.0\nMedian: 5\n"
    if r.returncode == 0 and r.stdout == want:
        PASSES.append("first-stats")
    else:
        FAILURES.append(f"first-stats: exit {r.returncode}\n{r.stdout}{r.stderr}")
    # the lib/ subdirectory claim
    wd2 = ROOT / "first-stats-lib"
    (wd2 / "lib" / "mylib").mkdir(parents=True, exist_ok=True)
    (wd2 / "lib" / "mylib" / "stats.sld").write_text("\n".join(stats) + "\n")
    (wd2 / "main.scm").write_text("\n".join(mainb) + "\n")
    r = subprocess.run(["kaappi", "main.scm"], cwd=wd2, capture_output=True,
                      text=True, timeout=60)
    if r.returncode == 0 and r.stdout == want:
        PASSES.append("first-stats-libdir")
    else:
        FAILURES.append(f"first-stats-libdir: exit {r.returncode}\n{r.stdout}{r.stderr}")
    # the REPL multi-line block, piped
    r = subprocess.run(["kaappi"], input="(define (square x)\n   (* x x))\n"
                       "(square 7)\n(map square '(1 2 3 4 5))\n",
                       capture_output=True, text=True, timeout=60)
    if r.returncode == 0 and "49" in r.stdout and "(1 4 9 16 25)" in r.stdout:
        PASSES.append("first-repl")
    else:
        FAILURES.append(f"first-repl: exit {r.returncode}\n{r.stdout}{r.stderr}")

# ================= srfi-support.md + libraries.md =================
if ONLY is None or "small" in ONLY:
    for page, name in [("srfi-support.md", "srfi-support"),
                       ("libraries.md", "libraries")]:
        bs = scheme_blocks(page)
        src, matchers = "(import (scheme base) (scheme write))\n", []
        for b in bs:
            c, m = claims_and_code(b)
            src += c
            matchers += m
        src += "(display 'page-end) (newline)\n"
        matchers.append("page-end")
        run_file(name, src, matchers)

# ================= troubleshooting.md =================
if ONLY is None or "troubleshooting" in ONLY:
    wd = ROOT / "trouble"
    wd.mkdir(exist_ok=True)
    ERR_CASES = [
        ("kp1001", '(define (square x)\n  (* x x)\n',
         [":3:1: read error[KP1001]: unexpected end of input"]),
        ("kp1006", '(display "hello)\n',
         [":2:1: read error[KP1006]: unterminated string literal"]),
        ("kp1007", '(display "hello\\q")\n',
         [":1:17: read error[KP1007]: invalid escape sequence"]),
        ("kp1008a", "#(1 . 2)\n",
         [":1:6: read error[KP1008]: '.' outside of a list"]),
        ("kp1008b", "(1 . 2 . 3)\n",
         [":1:8: read error[KP1002]: unexpected character"]),
        ("kp1009", "#|" * 257 + "x" + "|#" * 257 + "\n",
         ["read error[KP1009]: nesting too deep"]),
        ("kp2001", "(lambda)\n",
         ["compile error[KP2001]: invalid syntax"]),
        ("kp3002a", '(+ "a" 1)\n',
         ["error[KP3002]: type error in 'arithmetic': expected number, got #<string>"]),
        ("kp3002b", "(car 42)\n",
         ["error[KP3002]: type error in 'car': expected pair, got 42"]),
        ("kp3003a", "(cons 1)\n",
         ["error[KP3003]: 'cons': expected 2 arguments, got 1"]),
        ("kp3003b", "(cons 1 2 3)\n",
         ["error[KP3003]: 'cons': expected 2 arguments, got 3"]),
        ("kp3005a", "(42 1 2)\n", ["error[KP3005]: not a procedure"]),
        ("kp3005b", '("hello" 1)\n', ["error[KP3005]: not a procedure"]),
        ("kp3004a", "(/ 1 0)\n", ["error[KP3004]: division by zero"]),
        ("kp3004b", "(quotient 5 0)\n", ["error[KP3004]: division by zero"]),
        ("kp3006a", "(vector-ref #(1 2 3) 5)\n",
         ["error[KP3006]: vector-ref: index 5 out of range for length 3"]),
        ("kp3006b", '(string-ref "abc" 10)\n',
         ["error[KP3006]: string-ref: index 10 out of range for length 3"]),
        ("kp3008", "(define (forever n) (+ 1 (forever (+ n 1))))\n(forever 0)\n",
         ["error[KP3008]: stack overflow", "called from"]),
        ("kp3001a", '(dispaly "hi")\n',
         ["error[KP3001]: undefined variable 'dispaly'. Did you mean 'display'?"]),
        ("kp3001b", "(set! y 10)\n",
         ["error[KP3001]: set!: unbound variable 'y'"]),
        ("libnotfound", "(import (kaappi jsonx))\n",
         ["error[KP2001]: library not found: (kaappi.jsonx)"]),
        ("exportnotfound", "(import (only (scheme base) frobnicate))\n",
         ["error[KP2001]: import only: identifier 'frobnicate' not found in import set"]),
        *([] if not HAVE_FFI else [("ffiopen", '(import (kaappi ffi))\n(ffi-open "libmissing")\n',
         ["ffi-open: dlopen", "libmissing"]),
        ("ffisym", '(import (kaappi ffi))\n(define lib (ffi-open "libm.dylib"))\n'
                    "(ffi-fn lib \"no_such_symbol\" '(double) 'double)\n",
         ["ffi-fn: dlsym", "no_such_symbol", "symbol not found"])]),
    ]
    for name, src, frags in ERR_CASES:
        f = wd / f"{name}.scm"
        f.write_text(src)
        r = subprocess.run(["kaappi", str(f)], capture_output=True, text=True,
                          timeout=90)
        combined = r.stdout + r.stderr
        if r.returncode != 0 and all(fr in combined for fr in frags):
            PASSES.append(f"trouble-{name}")
        else:
            FAILURES.append(
                f"trouble-{name}: exit {r.returncode}; want {frags}\n{combined[:500]}")
    # pitfalls (positive samples with claims)
    run_file("trouble-pitfalls", "(import (scheme base) (scheme write))\n"
        "(write (eq? 42 42)) (newline)\n"
        "(write (eq? (expt 2 100) (expt 2 100))) (newline)\n"
        "(write (= (expt 2 100) (expt 2 100))) (newline)\n"
        "(define x 10)\n(define (change! v) (set! v 99))\n(change! x)\n"
        "(write x) (newline)\n"
        '(define s (string-copy "hello"))\n(string-set! s 0 #\\H)\n'
        "(write s) (newline)\n"
        "(write (map + '(1 2 3) '(10 20))) (newline)\n"
        "(begin (define a 1) (define b 2))\n(write (+ a b)) (newline)\n",
        ["#t", "#f", "#t", "10", '"Hello"', "(11 22)", "3"])
    # kaappi doctor: loose structural check
    r = subprocess.run(["kaappi", "doctor"], capture_output=True, text=True,
                      timeout=60)
    combined = r.stdout + r.stderr
    if all(s in combined for s in ["binary", "library", "native-backend",
                                   "package-manager", "Summary:"]):
        PASSES.append("trouble-doctor")
    else:
        FAILURES.append(f"trouble-doctor:\n{combined[:800]}")

# ================= diagnostics.md =================
if ONLY is None or "diagnostics" in ONLY:
    text = (DOCS / "diagnostics.md").read_text()
    entries = re.findall(
        r"### `(KP\d+)`[^\n]*\n(.*?)(?=\n### `KP|\Z)", text, re.S)
    wd = ROOT / "diag"
    wd.mkdir(exist_ok=True)
    SKIP_RUN = {"KP1009", "KP1010", "KP9000", "KP9001"}  # pseudo examples
    page_codes = []
    for code, body in entries:
        page_codes.append(code)
        m = re.search(r"```scheme\n(.*?)```", body, re.S)
        example = m.group(1) if m else None
        # every code must be known to `kaappi explain`
        r = subprocess.run(["kaappi", "explain", code],
                          capture_output=True, text=True, timeout=30)
        if r.returncode != 0 or code not in (r.stdout + r.stderr):
            FAILURES.append(f"diag-explain-{code}: exit {r.returncode}\n{r.stdout}{r.stderr}")
        else:
            PASSES.append(f"diag-explain-{code}")
        if example is None or code in SKIP_RUN:
            continue
        f = wd / f"{code}.scm"
        # unique content per run: a cached .sbc would skip read/expand and
        # mask read- and expand-stage diagnostics (notably KP2003)
        f.write_text(f";; sweep-{os.getpid()}-{id(example)}\n" + example)
        if code.startswith("KP4"):
            args = ["check", str(f)]
        elif code == "KP3009":
            args = ["--timeout", "500", str(f)]
        else:
            args = [str(f)]
        r = subprocess.run(["kaappi", *args], capture_output=True,
                          text=True, timeout=90)
        combined = r.stdout + r.stderr
        want = f"[{code}]"
        if code == "KP4001":
            ok = f"warning[{code}]" in combined   # the page insists: warning
        elif code.startswith("KP4"):
            ok = want in combined                  # check may error or warn
        else:
            ok = r.returncode != 0 and want in combined
        if ok:
            PASSES.append(f"diag-trigger-{code}")
        else:
            FAILURES.append(
                f"diag-trigger-{code}: exit {r.returncode}; want {want}\n{combined[:600]}")
    # the page must cover exactly the binary's registry
    r = subprocess.run(["kaappi", "explain", "--all"], capture_output=True,
                      text=True, timeout=30)
    bin_codes = sorted(set(re.findall(r"KP\d{4}", r.stdout)))
    if bin_codes and sorted(set(page_codes)) != bin_codes:
        FAILURES.append(
            f"diag-registry: page={sorted(set(page_codes))}\nbinary={bin_codes}")
    else:
        PASSES.append("diag-registry")

# ================= repl.md =================
if ONLY is None or "repl" in ONLY:
    wd = ROOT / "repl"
    wd.mkdir(exist_ok=True)
    (wd / "helpers.scm").write_text("(define (helper-val) 7)\n")
    SESSION = [
        ("(+ 1 2)", ["3"]), ("_", ["3"]),
        ("(define (square x)", []), ("   (* x x))", []),
        ("(square 7)", ["49"]),
        ("(* 6 7)", ["42"]), ("(+ _ 8)", ["50"]),
        ('(string-append "answer: " (number->string _))', ['"answer: 50"']),
        ("'((name \"Alice\" age 30) (name \"Bob\" age 25) (name \"Carol\" age 28))",
         ['(name "Alice" age 30)', '(name "Bob" age 25)', '(name "Carol" age 28)']),
        ("(values 1 2 3)", ["1\n2\n3"]),
        ("(define (fib n) (if (< n 2) n (+ (fib (- n 1)) (fib (- n 2)))))", []),
        (",time (fib 30)", ["832040", "seconds"]),
        (",type (+ 1 2)", ["; integer"]),
        (',type "hello"', ["; string"]),
        (",type (list 1 2 3)", ["; pair"]),
        (",type car", ["; procedure"]),
        (",type #t", ["; boolean"]),
        ("(define-syntax my-when (syntax-rules () ((_ test body ...) (if test (begin body ...)))))", []),
        (',expand (my-when #t (display "yes"))',
         ['(__hyg_1_if #t (begin (display "yes")))']),
        (",profile (fib 25)", ["75025", "Profile (", "Self ms", "fib (<repl>:1)"]),
        ("(define (factorial n) (if (<= n 1) 1 (* n (factorial (- n 1)))))", []),
        (",dis factorial", ["; Function: factorial", "; Source: <repl>:1",
                            "Arity: 1, Locals: 7, Upvalues: 0", "load_const"]),
        (",describe car", ["car", "type: procedure", "arity: 1"]),
        (",describe map", ["arity: 2, locals: 9"]),
        (",describe +", ["arity: 0+"]),
        ('(define (greet name) (string-append "Hello, " name))', []),
        (",describe greet", ["greet", "type: procedure",
                             "arity: 1, locals: 4", "source: <repl>:1"]),
        (",apropos vector", ["vector-every", "make-vector", "; 65 matches"]),
        (",env string-", ["string->number", "string-copy", "; 55 bindings"]),
        (",gc", ["GC Statistics:", "Collections:"]),
        (",version", [VER]),
        (",load helpers.scm", []), ("(helper-val)", ["7"]),
        (",import (srfi 1)", []), ("(iota 5)", ["(0 1 2 3 4)"]),
        (",import (only (srfi 1) iota fold)", []),
        (",help", ["Commands:", ",quit", ",time <expr>", ",describe <sym>",
                   ",break <name>", ",import <lib>",
                   "The variable _ holds the last result."]),
        (",break fib", ["Breakpoint set on fib"]),
        (",condition 0 (> n 10)", ["Condition set"]),
        (",breakpoints", ["[0] fib"]),
        (",delete all", ["All breakpoints deleted"]),
        # ,step enters the interactive stepper (own input loop) — the page
        # block shows no output, so there is nothing assertable via pty here;
        # its existence is covered by the ,help listing.
        (",quit", []),
    ]
    # Comma commands are only handled by the interactive line editor (piped
    # stdin reads ,cmd as unquote), so drive a real pty.
    import pty as ptymod, select, time as timemod

    def clean_text(b):
        s = b.decode("utf-8", "replace")
        return re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]|\x1b[()][A-Z0-9]|\r", "", s)

    def pty_repl(name, session, cwd):
        master, slave = ptymod.openpty()
        p = subprocess.Popen(["kaappi"], stdin=slave, stdout=slave,
                             stderr=slave, cwd=cwd, close_fds=True,
                             env=dict(os.environ, TERM="xterm-256color"))
        os.close(slave)
        raw = b""

        def answer_dsr(chunk):
            # linenoise queries cursor position (ESC[6n); after ESC[999C it
            # is probing terminal width — report col 80 there, col 1 else.
            parts = chunk.split(b"\x1b[6n")
            for i in range(1, len(parts)):
                col = 80 if b"\x1b[999C" in parts[i - 1] else 1
                os.write(master, b"\x1b[1;%dR" % col)

        def read_until(pred, timeout):
            # Prompt must be present AND the stream quiet for 0.4s — a chunk
            # boundary can land right after a mid-redraw prompt, and sending
            # early drops the next command into the redraw.
            nonlocal raw
            t0 = timemod.time()
            last_data = timemod.time()
            while timemod.time() - t0 < timeout:
                rl, _, _ = select.select([master], [], [], 0.2)
                if rl:
                    try:
                        chunk = os.read(master, 65536)
                    except OSError:
                        return False
                    if not chunk:
                        return False
                    raw += chunk
                    answer_dsr(chunk)
                    last_data = timemod.time()
                elif pred(clean_text(raw)) and timemod.time() - last_data > 0.4:
                    return True
            return False

        ok = True
        if not read_until(lambda s: s.rstrip().endswith("kaappi>"), 15):
            FAILURES.append(f"{name}: no initial prompt\n{clean_text(raw)[-800:]}")
            ok = False
        for cmd, _ in session:
            if not ok:
                break
            mark = len(clean_text(raw))
            os.write(master, cmd.encode() + b"\r")
            if not read_until(
                    lambda s: s[mark:].rstrip().endswith(
                        ("kaappi>", "...", "debug>")),
                    30):
                if cmd == ",quit":
                    break     # no prompt after quit — fine
                FAILURES.append(f"{name}: no prompt after {cmd!r}\n{clean_text(raw)[-1000:]}")
                ok = False
        try:
            p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            p.kill()
            if ok:
                FAILURES.append(f"{name}: did not exit after ,quit")
                ok = False
        os.close(master)
        text = clean_text(raw)
        (ROOT / f"{name}-transcript.txt").write_text(text)
        if ok:
            expect = [VER,
                      "Type ,help for commands, ,quit to exit."] + \
                     [m for _, ms in session for m in ms]
            if assert_ordered(name, text, expect):
                PASSES.append(name)
        return text

    pty_repl("repl-session", SESSION, wd)

# ================= debugging.md (interactive parts) =================
if ONLY is not None and "debugging-pty" in ONLY:
    wd = ROOT / "debugging"
    wd.mkdir(exist_ok=True)
    DBG = [
        (",describe map", ["arity: 2"]),
        ('(define (greet name) (string-append "hello " name))', []),
        (",describe greet", ["greet", "source: <repl>"]),
        ("(define-syntax my-when (syntax-rules () ((_ test body ...) (if test (begin body ...)))))", []),
        (',expand (my-when #t (display "yes"))', ["(__hyg_1_if"]),
        ("(define (factorial n) (if (<= n 1) 1 (* n (factorial (- n 1)))))", []),
        (",profile (factorial 20)", ["2432902008176640000", "Profile ("]),
        (",dis factorial", ["; Source: <repl>:1", "0065  return"]),
        (",break factorial", ["Breakpoint set on factorial"]),
        ("(factorial 3)", ["Break at factorial"]),
        ("locals", ["n = 3"]),
        ("backtrace", ["factorial"]),
        ("continue", ["Break at factorial"]),
        ("locals", ["n = 2"]),
        ("backtrace", ["factorial"]),
        ("up", []), ("locals", []), ("down", []),
        ("watch n", ["Watching n"]),
        ("continue", []),
        ("unwatch n", []),
        ("continue", []), ("continue", []), ("continue", []),
        (",delete all", ["All breakpoints deleted"]),
        (",quit", []),
    ]
    pty_repl("debugging-pty", DBG, wd)

print(f"\npassed {len(PASSES)}: {', '.join(PASSES)}")
if FAILURES:
    print(f"\nFAILED {len(FAILURES)}:")
    for f in FAILURES:
        print("\n===", f)
sys.exit(1 if FAILURES else 0)
