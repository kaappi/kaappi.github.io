#!/usr/bin/env python3
"""Verify every ;=> claim in docs/procedures/ by replaying each page as one
piped REPL session with block-boundary sentinels."""
import re, subprocess, sys, shutil, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _common import (WS, work, platformize, lib_args, core_lib_args,
                     importable, port_open, install_workspace_dylibs)

DOCS = pathlib.Path(sys.argv[1])            # docs/procedures
ONLY = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else None
ROOT = work("eco")
FAILURES, PASSES = [], []

EXTRA_ARGS = {
    "cli.md":  lib_args("kaappi-cli"),
    "yaml.md": lib_args("kaappi-yaml"),
    "log.md":  lib_args("kaappi-log"),
    "test.md": lib_args("kaappi-test"),
    "bdd.md":  lib_args("kaappi-bdd"),
    "email.md": lib_args("kaappi-email"),
    "mpl.md":  lib_args("kaappi-mpl"),
    "crypto.md": lib_args("kaappi-crypto"),
    "math.md": lib_args("kaappi-math"),
    "redis.md": lib_args("kaappi-redis"),
    "pg.md":   lib_args("kaappi-pg"),
}
# each page's primary library import (page skipped when unavailable)
PAGE_LIB = {
    "cli.md": "kaappi cli", "yaml.md": "kaappi yaml",
    "log.md": "kaappi log", "test.md": "kaappi test",
    "bdd.md": "kaappi bdd", "email.md": "kaappi email mime",
    "mpl.md": "mpl all", "crypto.md": "kaappi crypto",
    "math.md": "kaappi math", "redis.md": "kaappi redis",
    "pg.md": "kaappi pg", "json.md": "kaappi json",
    "csv.md": "kaappi csv", "toml.md": "kaappi toml",
    "sqlite.md": "kaappi sqlite", "template.md": "kaappi template",
    "http.md": "kaappi http", "web.md": "kaappi web",
    "net.md": "kaappi net",
}
PRELUDE = {"email.md": "(import (kaappi email mime))",
           "http.md": "(import (kaappi http))",
           "redis.md": "(import (kaappi redis))",
           "sqlite.md": "(import (kaappi sqlite))",
           "web.md": "(import (kaappi web))",
           "pg.md": '(import (kaappi pg)) (define email "alice@example.org")',
           "srfi-170.md": "(import (srfi 170))",
           "srfi-254.md": "(import (srfi 254) (srfi 111))"}
FIXTURE = "first line of file\nsecond line\n"
PER_BLOCK = {
    "pg.md": ('(define conn (pg-connect "host=localhost dbname=myapp"))'
              '(pg-exec conn "DROP TABLE IF EXISTS users, sessions,'
              ' large_table, invitees CASCADE")'
              '(pg-exec conn "CREATE TABLE users (id SERIAL, name TEXT,'
              ' age INT, email TEXT)")'
              """(pg-exec conn "INSERT INTO users (name, age) VALUES"""
              """ ('Alice', 30), ('Bob', 35)")"""
              '(pg-exec conn "CREATE TABLE sessions (id SERIAL,'
              ' expired TIMESTAMPTZ)")'
              '(pg-exec conn "CREATE TABLE large_table (name TEXT, age INT)")'
              """(pg-exec conn "INSERT INTO large_table VALUES ('Alice', 30)")"""),
    "redis.md": '(define conn (redis-connect "127.0.0.1" 6379))',
    "sqlite.md": '(define db (sqlite-open ":memory:"))'
                 '(sqlite-exec db "CREATE TABLE IF NOT EXISTS users '
                 '(id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")'
                 '(sqlite-exec db "INSERT INTO users (name, age) '
                 "VALUES ('Alice', 30), ('Bob', 28)\")"
                 '(sqlite-exec db "CREATE TABLE IF NOT EXISTS scores '
                 '(id INTEGER, name TEXT, score REAL)")'
                 '(sqlite-exec db "INSERT INTO scores VALUES '
                 "(1, 'Alice', 95.5), (2, 'Bob', 87.0)\")"
                 '(sqlite-exec db "CREATE TABLE IF NOT EXISTS large_table '
                 '(id INTEGER, name TEXT)")'
                 '(sqlite-exec db "INSERT INTO large_table VALUES '
                 "(1, 'Alice')\")",
}

def blocks_of(page):
    out, inb, buf = [], False, []
    for line in (DOCS / page).read_text().splitlines():
        if not inb and line.startswith("```scheme"):
            inb, buf = True, []
        elif inb and line.rstrip() == "```":
            out.append(buf)
            inb = False
        elif inb:
            buf.append(line)
    return out

def norm_claim(c):
    c = c.split(" — ")[0].strip()
    m = re.match(r"\d{9,}[\d.]*\s+(\S.*)$", c)
    if m:
        c = m.group(1)            # drop leading wall-clock timestamp
    if " or " in c:
        return ""                 # "x or y" alternatives are prose
    if re.fullmatch(r"[a-z][a-z ,/-]*( [a-z,/-]+)+", c.strip()):
        return ""                 # prose description, not a value
    if re.match(r"^[a-z][\w-]* or ", c.strip()):
        return ""                 # "x or y" prose alternatives
    m = re.match(r"^(\S+)\s+\([a-z ]+\)$", c.strip())
    if m:
        c = m.group(1)            # strip trailing type annotation
    if c.startswith('"'):
        m = re.match(r'("(?:[^"\\]|\\.)*")\s+;', c)
        if m:
            c = m.group(1)                          # comment after string
    else:
        c = re.sub(r"\s+;;?\s.*$", "", c).strip()   # trailing inline comment
    m = re.match(r"(#<[a-zA-Z?!/*+-]+)", c)
    if m and c.startswith("#<"):
        return m.group(1)          # unreadable objects: prefix-match
    return c

def paren_delta(s):
    s = re.sub(r"#\\.", "", s)
    s = re.sub(r'"(?:[^"\\]|\\.)*"', "", s)
    s = re.sub(r";.*$", "", s)
    return s.count("(") - s.count(")")

def build_session(blocks):
    stdin_lines, expect, err_expect = [], [], []
    for bi, block in enumerate(blocks):
        marker = f"<<B{bi}>>"
        stdin_lines.append(f'(display "{marker}") (newline)')
        expect.append(marker)
        pending_read = False
        balance = 0
        i = 0
        lines = block
        while i < len(lines):
            line = lines[i]
            if line.startswith("kaappi> "):
                code = line[8:]
                if re.match(r"\(exit\b|\(emergency-exit\b", code):
                    i += 1
                    continue          # would terminate the whole session
                stdin_lines.append(code)
                balance = paren_delta(code)
                pending_read = bool(re.search(r"\(read-line\)|\(read\)|\(read-char\)", code))
            elif re.match(r"\s*\.\.\.\s?", line):
                code = re.sub(r"^\s*\.\.\.\s?", "", line)
                stdin_lines.append(code)
                balance += paren_delta(code)
            elif balance > 0 and ";=>" not in line:
                stdin_lines.append(line)      # indentation-style continuation
                balance += paren_delta(line)
            elif ";=>" in line:
                claim = line.split(";=>", 1)[1]
                # join multi-line continuations (';    ...' lines)
                while i + 1 < len(lines):
                    nxt = lines[i + 1].strip()
                    if nxt.startswith(";") and not nxt.startswith(";;") and ";=>" not in nxt:
                        claim += " " + nxt.lstrip("; ").strip()
                        i += 1
                    else:
                        break
                claim = norm_claim(claim)
                if claim.startswith("error"):
                    err_expect.append(claim.split(":", 1)[-1].strip() or "error")
                elif claim:
                    expect.append(claim)
            elif line.strip() == "" or line.strip().startswith(";"):
                pass
            elif pending_read:
                stdin_lines.append(line)
                pending_read = False
            else:
                expect.append(line.rstrip())
        # non-transcript blocks (no prompts at all): feed lines as code
            i += 1
        if not any(l.startswith("kaappi> ") for l in block):
            pass  # already fed above line-by-line via the else branch? no:
    return stdin_lines, expect, err_expect

def plain_block_feed(block):
    """Blocks without kaappi> prompts: every non-comment line is code;
    ;=> claims still assert."""
    stdin_lines, expect, errs = [], [], []
    i = 0
    while i < len(block):
        line = block[i]
        if ";=>" in line:
            code = line.split(";=>")[0].rstrip()
            if code.strip():
                stdin_lines.append(code)
            claim = line.split(";=>", 1)[1]
            while i + 1 < len(block):
                nxt = block[i + 1].strip()
                if nxt.startswith(";") and not nxt.startswith(";;") and ";=>" not in nxt:
                    claim += " " + nxt.lstrip("; ").strip()
                    i += 1
                else:
                    break
            claim = norm_claim(claim)
            if claim.startswith("error"):
                errs.append(claim.split(":", 1)[-1].strip() or "error")
            elif claim:
                expect.append(claim)
        elif (re.match(r"^\(", line) and re.search(r"\)\s+;; ", line)
              and paren_delta(line) == 0):
            pass                  # top-level signature line in a mixed block
        else:
            stdin_lines.append(line)
        i += 1
    return stdin_lines, expect, errs

def assert_ordered(name, stdout, matchers):
    pos = 0
    prev = None
    for m in matchers:
        if "..." in m:            # elided claim: match the parts in order
            ok = True
            for part in (p for p in m.split("...") if p.strip()):
                f = stdout.find(part.strip(), pos)
                if f < 0:
                    ok = False
                    break
                pos = f + len(part.strip())
            if ok:
                prev = m
                continue
            FAILURES.append(f"{name}: missing elided {m!r} after {prev!r}")
            return False
        found = stdout.find(m, pos)
        if found < 0:
            ctx = stdout[max(0, pos - 80):pos + 400]
            FAILURES.append(
                f"{name}: missing (in order) {m!r} after {prev!r} matched at {pos}\n--- near ---\n{ctx}")
            return False
        pos = found + len(m)
        prev = m
    return True

pages = sorted(p.name for p in DOCS.glob("*.md") if p.name != "index.md")
if ONLY:
    pages = [p for p in pages if p.replace(".md", "") in ONLY]


# ---------- service / dylib setup (cleaned up via atexit) ----------
import atexit, os, time as _t
for _tgt in install_workspace_dylibs("crypto", "math", "redis", "pg"):
    atexit.register(lambda t=_tgt: t.unlink(missing_ok=True))

if any(p.startswith("redis") for p in pages) and not port_open(6379):
    _r = subprocess.Popen(["redis-server", "--port", "6379", "--save", "",
                           "--appendonly", "no"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    atexit.register(_r.terminate)
    _t.sleep(0.6)

PG_LIVE = False
if any(p.startswith("pg") for p in pages):
    # the user's own postgres runs on 5432 — never initdb over it; use it
    # only via a scratch database we create and drop, and only when no
    # database named myapp already exists
    _r = subprocess.run(["psql", "-h", "localhost", "-lqt"],
                        capture_output=True, text=True, timeout=30)
    if os.environ.get("SWEEP_PG_USE_EXISTING") == "1":
        PG_LIVE = True
    elif _r.returncode == 0 and "myapp" not in _r.stdout:
        _c = subprocess.run(["createdb", "-h", "localhost", "myapp"],
                            capture_output=True, timeout=30)
        if _c.returncode == 0:
            PG_LIVE = True
            atexit.register(lambda: subprocess.run(
                ["dropdb", "-h", "localhost", "myapp"], capture_output=True))
            subprocess.run(["psql", "-h", "localhost", "-d", "myapp", "-c",
                "CREATE TABLE events (id INT, created_at TIMESTAMPTZ DEFAULT now());"
                "CREATE TABLE accounts (id INT, balance INT);"
                "INSERT INTO accounts VALUES (1,500),(2,500);"
                "CREATE TABLE log (id SERIAL, msg TEXT);"
                "CREATE TABLE config (key TEXT, value TEXT);"],
                capture_output=True, timeout=30)

for page in pages:
    if page in PAGE_LIB and not importable(PAGE_LIB[page],
                                           EXTRA_ARGS.get(page, [])):
        print(f"{page}: SKIPPED ({PAGE_LIB[page]} not importable here)")
        continue
    if page == "pg.md" and not PG_LIVE:
        print("pg.md: SKIPPED live run (no safe scratch database)")
        continue
    blocks = blocks_of(page)
    if not blocks:
        continue
    wd = ROOT / page.replace(".md", "")
    if wd.exists():
        shutil.rmtree(wd)
    wd.mkdir(parents=True)
    (wd / "data.txt").write_text(FIXTURE)
    (wd / "image.bin").write_bytes(bytes([137, 80, 78, 71]))
    (wd / "utils.scm").write_text("(define utils-loaded #t)\n")
    (wd / "config.json").write_text('{"server":{"host":"localhost","port":8080},"debug":true}\n')
    (wd / "config.toml").write_text('[server]\nhost = "127.0.0.1"\nport = 8080\n\n[logging]\nlevel = "info"\n')
    (wd / "config.yml").write_text('name: My Service\nversion: "1.2.0"\nfeatures:\n  - auth\n  - logging\n')
    (wd / "data.csv").write_text("name,age,city\nAlice,30,Berlin\nBob,25,Tokyo\n")
    (wd / "app.toml").write_text('[server]\nhost = "127.0.0.1"\nport = 8080\n')
    (wd / "app.yml").write_text("server:\n  host: 127.0.0.1\n  port: 8080\n")
    (wd / "transactions.csv").write_text("id,desc,amount\n1,a,10\n2,b,5\n")
    if page == "srfi-170.md":     # samples create files under /tmp
        for m in set(re.findall(r'"(/tmp/[\w.-]+)"', (DOCS / page).read_text())):
            pth = pathlib.Path(m)
            try:
                pth.unlink()
            except (FileNotFoundError, PermissionError):
                pass
            except IsADirectoryError:
                try:
                    pth.rmdir()
                except OSError:
                    pass
            try:
                pth.rmdir()
            except OSError:
                pass
        pathlib.Path("/tmp/test.txt").write_text("x\n")
    stdin_lines, expect, err_expect = [], [], []
    if page in PRELUDE:
        stdin_lines.append(PRELUDE[page])
    for bi, block in enumerate(blocks):
        marker = f"<<B{bi}>>"
        text = "\n".join(block)
        if len(re.findall(r"\)\s+;; ", text)) >= 2 and ";=>" not in text:
            continue              # API signature summary block
        claims_txt = re.findall(r";=>\s*(.+)", text)
        prose = [c for c in claims_txt
                 if norm_claim(c) == ""
                 or (re.search(r"[a-z]+ [a-z]+", c)
                     and not c.strip().startswith(('"', "(", "'", "`", "#")))]
        if claims_txt and len(prose) * 2 >= len(claims_txt) and len(prose) >= 2:
            continue              # signature summary: claims are prose
        if re.search(r"\(random-|get-environment-variable|current-second"
                     r"|current-jiffy|file-info:|user-info|group-info"
                     r"|directory-files|current-directory|real-path"
                     r"|processor-count|set-umask|umask|\(pid\)"
                     r"|parent-pid|nice |user-uid|user-gid|user-effective"
                     r"|current-time|time->seconds|seconds->time"
                     r"|supplementary|terminal\?|temp-file|temp-dir"
                     r"|mkstemp|mkdtemp|set-file-owner|set-file-group"
                     r"|http-get|http-post|http-put|http-delete|smtp-|send-email|example\.com|httpbin|api\.github|\(serve |serve-prefork|http-listen|thottam |redis-subscribe|redis-brpop|redis-blpop", text):
            continue          # outputs vary per run / per machine
        if re.search(r"^\(GET \"|^\(POST \"", text, re.M) and "(routes" not in text:
            continue              # route-clause fragment (GET is routes-only syntax)
        if page in ("http.md", "web.md") and re.search(r"\breq\b", text) \
                and "(define req" not in text:
            continue              # needs a live request object
        if page == "http.md" and re.search(r"\bresp\b", text) and "(define resp" not in text:
            continue              # depends on a response from a skipped network call
        if page == "cli.md" and "run-cli" in text:
            continue              # argv-driven; verified via cookbook transcripts
        if page == "system.md" and "(command-line)" in text:
            # transcript documents a `kaappi script.scm foo bar` run
            (wd / "script.scm").write_text(
                "(import (scheme base) (scheme write) (scheme process-context))\n"
                "(write (command-line)) (newline)\n")
            r = subprocess.run(["kaappi", "script.scm", "foo", "bar"], cwd=wd,
                               capture_output=True, text=True, timeout=30)
            if r.returncode == 0 and '("script.scm" "foo" "bar")' in r.stdout:
                PASSES.append("system-command-line-file")
            else:
                FAILURES.append(f"system-command-line-file: {r.stdout}{r.stderr}")
            continue
        is_repl = any(l.startswith("kaappi> ") for l in block)
        if not is_repl and ";=>" not in "\n".join(block):
            # claim-less plain blocks are pattern fragments with free
            # variables — feed only if they are pure definitions
            forms_ok = all(not l.strip()
                           or l.lstrip().startswith(("(define", ";"))
                           or l.startswith((" ", "\t"))
                           for l in block)
            if not forms_ok or not any("(define" in l for l in block):
                continue
        stdin_lines.append(f'(display "{marker}") (newline)')
        expect.append(marker)
        if page in PER_BLOCK:
            stdin_lines.append(PER_BLOCK[page])
        if is_repl:
            s, e, er = build_session([block])
            stdin_lines += s[1:]          # drop the duplicate marker
            expect += e[1:]
            err_expect += er
        else:
            s, e, er = plain_block_feed(block)
            stdin_lines += s
            expect += e
            err_expect += er
    stdin_lines.append('(display "<<PAGE-END>>") (newline)')
    expect.append("<<PAGE-END>>")
    args = ["kaappi"] + EXTRA_ARGS.get(page, [])
    try:
        stdin_text = platformize("\n".join(stdin_lines) + "\n")
        r = subprocess.run(args, input=stdin_text, cwd=wd,
                           capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        FAILURES.append(f"{page}: TIMEOUT")
        continue
    (wd / "stdout.txt").write_text(r.stdout)
    (wd / "stderr.txt").write_text(r.stderr)
    (wd / "stdin.txt").write_text("\n".join(stdin_lines))
    ok = assert_ordered(page, r.stdout, expect)
    for e in err_expect:
        if e not in r.stderr and e not in r.stdout:
            FAILURES.append(f"{page}: expected error text {e!r} not seen")
            ok = False
    if ok and r.returncode != 0 and not err_expect:
        FAILURES.append(f"{page}: exit {r.returncode} with no expected errors\n{r.stderr[-800:]}")
        ok = False
    if ok:
        PASSES.append(f"{page} ({len(expect)} checks)")

print(f"\npassed {len(PASSES)}:")
for p in PASSES:
    print("  ", p)
if FAILURES:
    print(f"\nFAILED {len(FAILURES)}:")
    for f in FAILURES[:14]:
        print("\n===", f[:900])
sys.exit(1 if FAILURES else 0)
