#!/usr/bin/env python3
"""Verify every Kaappi sample in docs/cookbook/ against the installed binary.

Data pages run cumulatively with ;=> claims asserted as ordered substrings.
Server pages boot for real and get probed over HTTP. Network/pg/redis code
is compile-checked with `kaappi check`.
"""
import re, subprocess, sys, os, shutil, time, socket, pathlib, urllib.request
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _common import WS, HAVE_FFI, HAVE_PROCESS, work, platformize, lib_args, core_lib_args

DOCS = pathlib.Path(sys.argv[1])          # docs/cookbook dir
WS_PATH = pathlib.Path(WS) if WS else None
ROOT = work("cookbook")
if ROOT.exists():
    shutil.rmtree(ROOT)
ROOT.mkdir()
FAILURES, PASSES = [], []

def blocks_of(page):
    return re.findall(r"```scheme\n(.*?)```", (DOCS / page).read_text(), re.S)

def claims_of(text):
    """Ordered matchers from ;=> claims; multi-line continuations joined.
    A claim containing '...' becomes multiple ordered substring parts."""
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        line = lines[i]
        if ";=>" in line:
            claim = line.split(";=>", 1)[1].strip()
            while i + 1 < len(lines):
                nxt = lines[i + 1].strip()
                if nxt.startswith(";") and not nxt.startswith(";;") and ";=>" not in nxt:
                    claim += " " + nxt.lstrip("; ").strip()
                    i += 1
                else:
                    break
            out.append(claim)
        i += 1
    return out

def assert_ordered(name, stdout, matchers):
    pos = 0
    for m in matchers:
        parts = [p for p in m.split("...") if p]
        for p in parts:
            found = stdout.find(p, pos)
            if found < 0:
                FAILURES.append(f"{name}: missing (in order) {p!r}\n--- stdout ---\n{stdout}")
                return False
            pos = found + len(p)
    return True

def run_kaappi(name, workdir, args, env_extra=None, timeout=90):
    env = dict(os.environ)
    for k in ("PORT", "DATABASE_URL", "API_KEY"):
        env.pop(k, None)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(["kaappi", *args], cwd=workdir, env=env,
                       capture_output=True, text=True, timeout=timeout)
    return r

def check_rc(name, r, expect_rc=0):
    if r.returncode != expect_rc:
        FAILURES.append(f"{name}: exit {r.returncode}\n{r.stdout}{r.stderr}")
        return False
    PASSES.append(name)
    return True

def cumulative(name, page, idxs, fixtures=None, prelude="", inject=None,
               extra_expect=None, skip_claims=(), libs=(), env=None):
    """Concatenate the given block indexes, run, assert claims in order."""
    wd = ROOT / name
    wd.mkdir(exist_ok=True)
    for fn, content in (fixtures or {}).items():
        p = wd / fn
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    bs = blocks_of(page)
    src, matchers = prelude, []
    for i in idxs:
        if inject and i in inject:
            src += inject[i]
        src += bs[i] + "\n"
        matchers += [c for c in claims_of(bs[i])
                     if not any(s in c for s in skip_claims)]
    if extra_expect:
        for code, exp in extra_expect:
            src += code + "\n"
            matchers.append(exp)
    f = wd / "prog.scm"
    f.write_text(src)
    args = sum((["--lib-path", str(l)] for l in libs), []) + [str(f)]
    r = run_kaappi(name, wd, args, env)
    if r.returncode != 0:
        FAILURES.append(f"{name}: exit {r.returncode}\n{r.stdout}{r.stderr}")
        return
    if assert_ordered(name, r.stdout, matchers):
        PASSES.append(name)

def static_check(name, workdir, target, libs=()):
    args = ["check"] + sum((["--lib-path", str(l)] for l in libs), []) + [str(target)]
    r = run_kaappi(name, workdir, args)
    check_rc(name, r)

def wait_port(port, timeout=20):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), 0.5):
                return True
        except OSError:
            time.sleep(0.25)
    return False

def probe_server(name, workdir, script, curls, libs=()):
    args = ["kaappi"] + sum((["--lib-path", str(l)] for l in libs), []) + [script]
    env = dict(os.environ)
    proc = subprocess.Popen(args, cwd=workdir, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        if not wait_port(8080):
            proc.terminate()
            out = proc.communicate(timeout=5)[0]
            FAILURES.append(f"{name}: server never listened\n{out}")
            return
        for method, path, data, expect in curls:
            req = urllib.request.Request(
                "http://127.0.0.1:8080" + path,
                data=data.encode() if data else None, method=method)
            if data:
                req.add_header("Content-Type", "application/x-www-form-urlencoded")
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    body = resp.read().decode()
            except urllib.error.HTTPError as e:
                body = e.read().decode()
            if expect not in body:
                FAILURES.append(f"{name}: {method} {path}: missing {expect!r} in\n{body[:500]}")
                return
        PASSES.append(name)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

W = "(import (scheme base) (scheme write))\n"

# ---------- json-processing.md ----------
CONFIG_JSON = '{"server":{"host":"localhost","port":8080},"debug":true}'
cumulative("json-run", "json-processing.md", [0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12],
    fixtures={"config.json": CONFIG_JSON, "items.json": '[{"name":"a"}]'},
    prelude=W)
jb = blocks_of("json-processing.md")
(ROOT / "json-check").mkdir(exist_ok=True)
(ROOT / "json-check" / "net.scm").write_text(jb[6] + "\n" + jb[7])
HAVE_FFI and static_check("json-check-net", ROOT / "json-check", "net.scm")

# ---------- csv-processing.md ----------
DATA_CSV = "name,age,city\nAlice,30,Berlin\nBob,25,Tokyo\n"
cumulative("csv-run", "csv-processing.md", list(range(12)),
    fixtures={"data.csv": DATA_CSV,
              "scores.csv": "name,score\nAlice,95\nBob,87\n",
              "transactions.csv": "id,desc,amount\n1,a,10\n2,b,5\n"},
    prelude=W,
    extra_expect=[("(display total) (newline)", "15")])

# ---------- config-files.md ----------
APP_TOML = ('[server]\nhost = "127.0.0.1"\nport = 8080\n\n'
            '[database]\nurl = "sqlite:///app.db"\n\n[logging]\nlevel = "info"\n')
cumulative("config-run", "config-files.md", list(range(7)),
    fixtures={"app.toml": APP_TOML,
              "app.yml": "server:\n  host: 127.0.0.1\n  port: 8080\n"},
    prelude=W, env={"API_KEY": "test-key"},
    libs=([WS_PATH / "kaappi-yaml" / "lib"]
          if WS_PATH and (WS_PATH / "kaappi-yaml" / "lib").exists() else []),
    extra_expect=[("(display port) (newline)", "8080")])

# ---------- sqlite-storage.md ----------
HAVE_FFI and cumulative("sqlite-run", "sqlite-storage.md", list(range(8)),
    prelude=W,
    libs=([WS_PATH / "kaappi-test" / "lib"]
          if WS_PATH and (WS_PATH / "kaappi-test" / "lib").exists() else []),
    extra_expect=[('(display "done") (newline)', "done")])

# ---------- external-programs.md ----------
# Every block but the last runs cumulatively; the last one is the injection
# contrast pair, whose `branch` is deliberately undefined prose.
HAVE_PROCESS and cumulative("subprocess-run", "external-programs.md", list(range(12)))

# ---------- concurrent-tasks.md ----------
cumulative("fibers-run", "concurrent-tasks.md", [0, 1, 2, 3, 4],
    prelude=W, skip_claims=("results from all workers",),
    extra_expect=[
        ("(write (sum-range 0 10)) (newline)", "45"),
        ("(let sortl ((l (pool-map (lambda (n) (* n 10)) '(1 2 3 4 5 6 7 8) 3)) (r '()))\n"
         "  (if (null? l) (write (length r))\n"
         "      (sortl (cdr l) (cons (car l) r)))) (newline)", "8"),
    ])
# NOTE: (kaappi parallel) is missing from the v0.21.0 install because that
# release's tarball omits lib/kaappi/ (fixed on core main by kaappi#1759;
# core_lib_args probes the install first, so the next release activates
# this check on CI). Meanwhile, verify against the core repo's lib tree.
_PAR = core_lib_args()
if _PAR is None:
    print("parallel-run: SKIPPED ((kaappi parallel) not resolvable here)")
else:
    cumulative("parallel-run", "concurrent-tasks.md", [5, 6, 7],
        prelude=W + "(import (kaappi fibers))\n",
        inject={6: "(define (process x) (* x 2))\n(define items '(1 2 3))\n"},
        libs=[a for a in _PAR[1::2]],
        extra_expect=[("(write results) (newline)", "(2 4 6)")])
# the fiber-error block's expected print is a ;; comment, not a ;=> claim
cumulative("fiber-error", "concurrent-tasks.md", [7],
    prelude=W + "(import (kaappi fibers))\n",
    extra_expect=[('(display "end") (newline)', "fiber failed")])

# ---------- http-client.md ----------
hb = blocks_of("http-client.md")
(ROOT / "http-check").mkdir(exist_ok=True)
(ROOT / "http-check" / "all.scm").write_text("\n".join(hb))
HAVE_FFI and static_check("http-check-all", ROOT / "http-check", "all.scm")
# pure block: query-string builder actually runs offline
cumulative("http-query-run", "http-client.md", [7],
    prelude=W,
    extra_expect=[("(display url) (newline)",
                   "https://httpbin.org/get?page=1&limit=10")])

print(f"\npassed {len(PASSES)}: {', '.join(PASSES)}")
if FAILURES:
    print(f"\nFAILED {len(FAILURES)}:")
    for f in FAILURES:
        print("\n===", f)
sys.exit(1 if FAILURES else 0)
