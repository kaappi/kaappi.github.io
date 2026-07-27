#!/usr/bin/env python3
"""Bespoke verification for testing.md, cli-tool.md, html-templates.md,
rest-api.md — the cookbook pages that need transcripts, argv, or a live server."""
import re, subprocess, sys, os, shutil, time, socket, shlex, pathlib, urllib.request
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _common import WS, work, lib_args, platformize

DOCS = pathlib.Path(sys.argv[1])
WS_PATH = pathlib.Path(WS) if WS else pathlib.Path("/nonexistent")
ROOT = work("cookbook2")
if ROOT.exists():
    shutil.rmtree(ROOT)
ROOT.mkdir()
FAILURES, PASSES = [], []
TEST_LIB = WS_PATH / "kaappi-test" / "lib"

def all_fences(page):
    """Tokenize fenced blocks in order → [(lang, content)]."""
    out, lang, buf = [], None, []
    for line in (DOCS / page).read_text().splitlines():
        if lang is None and line.startswith("```"):
            lang, buf = line[3:].strip(), []
        elif lang is not None and line.rstrip() == "```":
            out.append((lang, "\n".join(buf) + "\n"))
            lang = None
        elif lang is not None:
            buf.append(line)
    return out

def fenced(page, lang):
    return [c for l, c in all_fences(page) if l == lang]

def scheme(page):
    return fenced(page, "scheme")

def run(name, args, cwd, expect=None, contains=(), rc=0, timeout=90):
    r = subprocess.run(["kaappi", *args], cwd=cwd, capture_output=True,
                       text=True, timeout=timeout)
    if r.returncode != rc:
        FAILURES.append(f"{name}: exit {r.returncode} (want {rc})\n{r.stdout}{r.stderr}")
        return False
    if expect is not None and r.stdout != expect:
        FAILURES.append(f"{name}: exact mismatch\n--- got ---\n{r.stdout!r}\n--- want ---\n{expect!r}")
        return False
    for c in contains:
        if c not in r.stdout:
            FAILURES.append(f"{name}: missing {c!r} in\n{r.stdout}{r.stderr}")
            return False
    PASSES.append(name)
    return True

def transcript(bash_block, script):
    """Parse '$ kaappi <script> args…' transcript → [(argv, expected_output)]."""
    runs, cur_args, cur_out = [], None, []
    for line in bash_block.splitlines():
        if line.startswith("$ "):
            if cur_args is not None:
                runs.append((cur_args, "\n".join(cur_out).rstrip("\n")))
            argv = shlex.split(line[2:])
            assert argv[0] == "kaappi" and argv[1] == script, line
            cur_args, cur_out = argv[2:], []
        elif cur_args is not None:
            cur_out.append(line)
    runs.append((cur_args, "\n".join(cur_out).rstrip("\n")))
    return runs

def wait_port(port, timeout=20):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), 0.5):
                return True
        except OSError:
            time.sleep(0.25)
    return False

def probe(name, cwd, script, curls, libs=()):
    args = ["kaappi"] + sum((["--lib-path", str(l)] for l in libs), []) + [script]
    proc = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    try:
        if not wait_port(8080):
            proc.terminate()
            FAILURES.append(f"{name}: server never listened\n{proc.communicate(timeout=5)[0]}")
            return
        for method, path, data, expects in curls:
            req = urllib.request.Request("http://127.0.0.1:8080" + path,
                data=data.encode() if data else None, method=method)
            if data:
                req.add_header("Content-Type", "application/x-www-form-urlencoded")
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    body = resp.read().decode()
            except urllib.error.HTTPError as e:
                body = e.read().decode()
            for expect in expects:
                if expect not in body:
                    FAILURES.append(f"{name}: {method} {path}: missing {expect!r} in\n{body[:600]}")
                    return
        PASSES.append(name)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

# ================= testing.md =================
tb = scheme("testing.md")
texts = fenced("testing.md", "")          # untyped ``` blocks (expected outputs)
wd = ROOT / "testing"; (wd / "tests").mkdir(parents=True); (wd / "lib" / "my-lib").mkdir(parents=True)
L = ["--lib-path", str(TEST_LIB)] if TEST_LIB.exists() else []

# b0 minimal file → exact output from the page's first untyped block
(wd / "t0.scm").write_text(tb[0])
run("test-minimal", L + ["t0.scm"], wd, expect=texts[0])

# b1..b4 assertion families in one program
(wd / "t1.scm").write_text("(import (kaappi test))\n" + "\n".join(tb[1:5]) + "\n(test-exit)\n")
run("test-assertions", L + ["t1.scm"], wd, contains=[
    "ok: lists", "ok: char", "ok: positive", "ok: string", "ok: empty",
    "ok: pi", "ok: division by zero", "ok: type error", "8 tests: 8 passed"])

# b5 nested groups — parse provided by harness; exact output vs page block
(wd / "t5.scm").write_text(
    "(import (scheme base) (kaappi test))\n"
    "(define (parse s) (read (open-input-string s)))\n" + tb[5] + "(test-exit)\n")
run("test-groups", L + ["t5.scm"], wd, expect=texts[1])

# b6 library test — fixture library with capitalize
(wd / "lib" / "my-lib" / "utils.sld").write_text(
    "(define-library (my-lib utils)\n  (export capitalize)\n"
    "  (import (scheme base) (scheme char))\n  (begin\n"
    "    (define (capitalize s)\n"
    "      (if (string=? s \"\") \"\"\n"
    "          (string-append (string (char-upcase (string-ref s 0)))\n"
    "                         (substring s 1 (string-length s)))))))\n")
(wd / "tests" / "test-utils.scm").write_text(tb[6])
run("test-library", L + ["--lib-path", "lib", "tests/test-utils.scm"], wd,
    contains=["ok: capitalize", "ok: capitalize empty", "2 tests: 2 passed"])

# b7 error conditions — create-user harness that validates
(wd / "t7.scm").write_text(
    "(import (scheme base) (kaappi test))\n"
    "(define (create-user name email)\n"
    "  (when (string=? name \"\") (error \"empty name\"))\n"
    "  (unless (let loop ((i 0)) (cond ((= i (string-length email)) #f)\n"
    "                                  ((char=? (string-ref email i) #\\@) #t)\n"
    "                                  (else (loop (+ i 1)))))\n"
    "    (error \"invalid email\"))\n"
    "  (list name email))\n" + tb[7] + "(test-exit)\n")
run("test-errors", L + ["t7.scm"], wd,
    contains=["ok: rejects empty name", "ok: rejects invalid email", "2 tests: 2 passed"])

# b8 setup/teardown with sqlite
(wd / "t8.scm").write_text("(import (scheme base) (kaappi test) (kaappi sqlite))\n"
                           + tb[8] + "(test-exit)\n")
run("test-sqlite", L + ["t8.scm"], wd,
    contains=["ok: insert returns 1", "ok: query returns row", "2 tests: 2 passed"])

# b9 verbose-off
(wd / "t9.scm").write_text("(import (kaappi test))\n" + tb[9])
run("test-verbose", L + ["t9.scm"], wd, contains=["0 tests"])

# b10 load-based runner — loaded files rely on the runner's toplevel import
# (import forms inside load'd files are not supported)
for n in ("parser", "validator", "handlers"):
    (wd / "tests" / f"test-{n}.scm").write_text(
        f'(test-group "{n}" (test-equal "one" 1 1))\n')
(wd / "tests" / "test-all.scm").write_text(tb[10])
run("test-runner-load", L + ["tests/test-all.scm"], wd,
    contains=["ok: one", "3 tests: 3 passed"])

# b11 SRFI-64 + `kaappi test tests/`
sd = ROOT / "srfi64"; (sd / "tests").mkdir(parents=True)
(sd / "tests" / "test-strings.scm").write_text(tb[11])
(sd / "tests" / "test-demo.scm").write_text(
    '(import (scheme base) (srfi 64))\n(test-begin "demo")\n'
    '(test-equal "id" 1 1)\n(test-end "demo")\n')
run("test-srfi64-runner", ["test", "tests"], sd,
    contains=["PASS  tests/test-demo.scm", "PASS  tests/test-strings.scm",
              "Summary: 3 passed, 0 failed"])

# ================= cli-tool.md =================
cb = scheme("cli-tool.md")
bash = fenced("cli-tool.md", "bash")
cwd = ROOT / "cli"; cwd.mkdir()
CLI_LIB = lib_args("kaappi-cli")
(cwd / "greet.scm").write_text(cb[0])
for i, (argv, exp) in enumerate(transcript(bash[1], "greet.scm")):
    run(f"cli-greet-{i}", CLI_LIB + ["greet.scm"] + argv, cwd, expect=exp + "\n")
(cwd / "tasks.scm").write_text(cb[1])
for i, (argv, exp) in enumerate(transcript(bash[2], "tasks.scm")):
    run(f"cli-tasks-{i}", CLI_LIB + ["tasks.scm"] + argv, cwd, expect=exp + "\n")

# b2 type coercion — three option declarations exercised through run-cli
def coercion(name, option_line, argv, expected):
    f = cwd / f"{name}.scm"
    f.write_text(
        "(import (scheme base) (scheme write) (kaappi cli))\n"
        f'(define app (cli "t" "d"\n  {option_line}))\n'
        "(run-cli app\n"
        "  `((#f . ,(lambda (result)\n"
        "             (write (parsed-ref result \"" + name.split('-')[0] + "\")) (newline)))))\n")
    run(f"cli-coerce-{name}", CLI_LIB + [f.name] + argv, cwd, expect=expected)

coercion("output-str", '(option "-o" "--output" "Output file" "out.txt")',
         ["--output", "report.txt"], '"report.txt"\n')
coercion("count-num", '(option "-n" "--count" "Item count" 10)', ["-n", "42"], "42\n")
coercion("format-set", '(option "-f" "--format" "Output format")', ["--format", "json"], '"json"\n')
coercion("format-unset", '(option "-f" "--format" "Output format")', [], "#f\n")

# ================= html-templates.md =================
hb = scheme("html-templates.md")
twd = ROOT / "templates"; twd.mkdir()
(twd / "app1.scm").write_text(hb[0])
probe("tpl-minimal-server", twd, "app1.scm",
      [("GET", "/", None, ["Welcome to Kaappi!", "<h1>Home</h1>"])])

# layout + page-template composition, incl. auto-escape proof
(twd / "layout.scm").write_text(
    "(import (scheme base) (kaappi template))\n" + hb[1] + hb[2] +
    '(display (render-page "X" (template-render-html contact-list-template\n'
    "  '((\"contacts\" . ())))))\n(newline)\n"
    '(display (render-page "X" (template-render-html contact-list-template\n'
    "  '((\"contacts\" . (((\"name\" . \"A&B\") (\"email\" . \"e@x\"))))))))\n(newline)\n")
run("tpl-layout", ["layout.scm"], twd,
    contains=["<title>X — My App</title>", "No contacts yet.", "<td>A&amp;B</td>"])

# full contact-book app over HTTP (sqlite-backed)
(twd / "app2.scm").write_text(hb[3])
probe("tpl-contact-app", twd, "app2.scm", [
    ("GET", "/", None, ["Contact Book"]),
    ("GET", "/contacts", None, ["No contacts yet."]),
    ("POST", "/contacts", "name=Alice&email=alice%40example.org", ["Alice"]),
    ("GET", "/contacts", None, ["Contacts (1)", "<td>Alice</td>", "alice@example.org"])])

# pre-parse block: reuse list-body from the app source
m = re.search(r'(\(define list-body ".*?")\)\n', hb[3], re.S)
assert m, "list-body not found"
pre = hb[4].splitlines()
(twd / "preparse.scm").write_text(
    "(import (scheme base) (kaappi template))\n" + m.group(1) + ")\n" +
    pre[0] + "\n"
    "(define data '((\"count\" . 1) (\"contacts\" . (((\"name\" . \"N\") (\"email\" . \"E\"))))))\n"
    "(display " + pre[3].strip() + ")\n(newline)\n")
run("tpl-preparse", ["preparse.scm"], twd, contains=["Contacts (1)", "<td>N</td>"])

# ================= rest-api.md =================
rb = scheme("rest-api.md")
rwd = ROOT / "rest"; (rwd / "lib" / "bookshelf").mkdir(parents=True)
for i, name in enumerate(["db", "cache", "validate", "handlers"]):
    (rwd / "lib" / "bookshelf" / f"{name}.sld").write_text(rb[i])
(rwd / "app.scm").write_text(rb[4])
# The real pg/redis libs dlopen their C shims even under `check`; stub the
# same exported names so the check validates the sample's own code.
(rwd / "stub" / "kaappi").mkdir(parents=True)
(rwd / "stub" / "kaappi" / "pg.sld").write_text(
    "(define-library (kaappi pg)\n  (export pg-connect pg-exec pg-query)\n"
    "  (import (scheme base))\n  (begin\n"
    "    (define (pg-connect s) #f)\n"
    "    (define (pg-exec c q . args) 0)\n"
    "    (define (pg-query c q . args) '())))\n")
(rwd / "stub" / "kaappi" / "redis.sld").write_text(
    "(define-library (kaappi redis)\n"
    "  (export redis-connect redis-get redis-setex redis-del)\n"
    "  (import (scheme base))\n  (begin\n"
    "    (define (redis-connect h p) #f)\n"
    "    (define (redis-get r k) #f)\n"
    "    (define (redis-setex r k ttl v) #t)\n"
    "    (define (redis-del r k) #t)))\n")
r = subprocess.run(["kaappi", "check",
                    "--lib-path", "lib",
                    "--lib-path", "stub",
                    *lib_args("kaappi-log"),
                    "app.scm"], cwd=rwd, capture_output=True, text=True, timeout=120)
if r.returncode == 0:
    PASSES.append("rest-api-check")
else:
    FAILURES.append(f"rest-api-check: exit {r.returncode}\n{r.stdout}{r.stderr}")

# ================= ecosystem spot-checks =================
ECO = DOCS.parent / "ecosystem"

def eco_scheme(page):
    out, lang, buf = [], None, []
    for line in (ECO / page).read_text().splitlines():
        if lang is None and line.startswith("```"):
            lang, buf = line[3:].strip(), []
        elif lang is not None and line.rstrip() == "```":
            out.append((lang, "\n".join(buf) + "\n"))
            lang = None
        elif lang is not None:
            buf.append(line)
    return out

# json.md null-handling blocks (just fixed) — run with claims
jf = [c for l, c in eco_scheme("json.md") if "json-null" in c]
src = "(import (scheme base) (scheme write) (kaappi json))\n" + "".join(jf)
(ROOT / "eco-json.scm").write_text(src)
r = subprocess.run(["kaappi", str(ROOT / "eco-json.scm")], capture_output=True,
                   text=True, timeout=60)
exp = ["null", "null", "#t", "#f", "#f", '"{\\"value\\":null}"']
if r.returncode == 0 and all(e in r.stdout for e in exp):
    PASSES.append("eco-json-null")
else:
    FAILURES.append(f"eco-json-null: exit {r.returncode}\n{r.stdout}{r.stderr}")

# template.md layout pattern (just fixed) — escape/verbatim behavior
tf = [c for l, c in eco_scheme("template.md") if "render-page" in c][0]
(ROOT / "eco-tpl.scm").write_text(
    "(import (scheme base) (kaappi template))\n" + tf +
    '(display (render-page "A&B" "<b>x</b>"))\n(newline)\n')
run("eco-template-layout", [str(ROOT / "eco-tpl.scm")], ROOT,
    contains=["<title>A&amp;B</title>", "<nav><a href='/'>Home</a></nav>", "<b>x</b>"])

# cli.md deploy example — reproduce its full transcript incl. --help
cf = [c for l, c in eco_scheme("cli.md") if '(cli "deploy"' in c][0]
tr = [c for l, c in eco_scheme("cli.md") if c.startswith("$ kaappi deploy.scm")][0]
dwd = ROOT / "eco-cli"; dwd.mkdir()
head = "(import (scheme base) (scheme write) (kaappi cli))\n" \
       if "(import" not in cf else ""
(dwd / "deploy.scm").write_text(head + cf)
for i, (argv, exp) in enumerate(transcript(tr, "deploy.scm")):
    run(f"eco-cli-deploy-{i}", CLI_LIB + ["deploy.scm"] + argv, dwd, expect=exp + "\n")

print(f"\npassed {len(PASSES)}: {', '.join(PASSES)}")
if FAILURES:
    print(f"\nFAILED {len(FAILURES)}:")
    for f in FAILURES:
        print("\n===", f)
sys.exit(1 if FAILURES else 0)
