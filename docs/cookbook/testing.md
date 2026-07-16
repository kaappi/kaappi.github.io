# Write Tests

This recipe covers test organization, all assertion types, error testing,
test output control, and running tests in CI.

## Setup

```bash
thottam install kaappi-test
```

## A minimal test file

```scheme
(import (kaappi test))

(test-group "math"
  (test-equal "addition" 4 (+ 2 2))
  (test-equal "multiplication" 6 (* 2 3)))

(test-exit)
```

Run it:

```bash
kaappi tests/test-math.scm
```

```
math
  ok: addition
  ok: multiplication

2 tests: 2 passed
```

`test-exit` prints the summary and exits with code 1 if any test failed —
this is what makes CI work.

## Assertions

### Equality

```scheme
;; equal? comparison (deep structural)
(test-equal "lists" '(1 2 3) (list 1 2 3))

;; eqv? comparison (numbers, characters, booleans)
(test-eqv "char" #\a (string-ref "abc" 0))
```

### Truthiness

```scheme
;; True (any non-#f value)
(test-assert "positive" (> 5 0))
(test-assert "string" (string? "hello"))

;; False
(test-not "empty" (pair? '()))
```

### Approximate (floating point)

```scheme
(test-approximate "pi" 3.14159 (acos -1) 0.001)
```

The third argument is the tolerance — the test passes if the actual value
is within that distance from expected.

### Errors

```scheme
;; Verify that an expression raises an error
(test-error "division by zero" (lambda () (/ 1 0)))
(test-error "type error" (lambda () (+ 1 "two")))
```

The thunk must raise an error for the test to pass.

## Test groups

Groups organize tests and show structure in the output:

```scheme
(test-group "parser"
  (test-group "numbers"
    (test-equal "integer" 42 (parse "42"))
    (test-equal "float" 3.14 (parse "3.14")))

  (test-group "strings"
    (test-equal "simple" "hello" (parse "\"hello\""))
    (test-equal "escaped" "a\"b" (parse "\"a\\\"b\""))))
```

Output:

```
parser
  numbers
    ok: integer
    ok: float
  strings
    ok: simple
    ok: escaped

4 tests: 4 passed
```

## Test a library

Typical layout for a library with tests:

```
my-lib/
  lib/
    my-lib/
      utils.sld
  tests/
    test-utils.scm
```

`tests/test-utils.scm`:

```scheme
(import (scheme base)
        (kaappi test)
        (my-lib utils))

(test-group "utils"
  (test-equal "capitalize"
    "Hello" (capitalize "hello"))
  (test-equal "capitalize empty"
    "" (capitalize "")))

(test-exit)
```

Run from the project root:

```bash
kaappi tests/test-utils.scm
```

## Test error conditions

Test that your code raises errors on bad input:

```scheme
(test-group "validation"
  (test-error "rejects empty name"
    (lambda () (create-user "" "alice@example.com")))

  (test-error "rejects invalid email"
    (lambda () (create-user "Alice" "not-an-email"))))
```

## Test with setup and teardown

Use `let` for per-group setup. For cleanup, wrap in `guard`:

```scheme
(test-group "database"
  (let ((db (sqlite-open ":memory:")))
    (sqlite-exec db "CREATE TABLE t (id INTEGER, name TEXT)")

    (test-equal "insert returns 1"
      1 (sqlite-exec db "INSERT INTO t VALUES (?, ?)" 1 "Alice"))

    (test-equal "query returns row"
      '#(1 "Alice")
      (car (sqlite-query db "SELECT * FROM t")))

    (sqlite-close db)))
```

## Suppress passing tests

For large test suites, show only failures:

```scheme
(test-verbose! #f)

(test-group "large suite"
  ;; ... hundreds of tests ...
  )

(test-exit)
```

Output shows only failures and the summary.

## Check procedure coverage

After writing tests, check that all exported procedures are exercised:

```bash
kaappi --coverage --lib-path ./lib tests/test-utils.scm
```

```
Coverage:
  (my-lib utils)    5/5  100.0%
  Overall: 5/5 procedures covered (100.0%)
```

Any uncalled procedures are listed by name. For CI, generate a Cobertura
report:

```bash
kaappi --coverage-xml coverage.xml --lib-path ./lib tests/test-utils.scm
```

## CI integration

A GitHub Actions workflow for testing:

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Kaappi
        run: curl -fsSL https://kaappi-lang.org/install.sh | bash
      - name: Install dependencies
        run: thottam install kaappi-test
      - name: Run tests
        run: kaappi tests/test-all.scm
```

`test-exit` exits with code 1 on failure, so the CI step fails automatically.

## Run multiple test files

Create a runner file that loads all test files:

`tests/test-all.scm`:

```scheme
(import (kaappi test))

(load "tests/test-parser.scm")
(load "tests/test-validator.scm")
(load "tests/test-handlers.scm")

(test-exit)
```

Or run them individually and let the shell aggregate the exit codes:

```bash
kaappi tests/test-parser.scm && \
kaappi tests/test-validator.scm && \
kaappi tests/test-handlers.scm
```

## SRFI-64 suites and the built-in runner

Everything above uses the `(kaappi test)` framework, run as ordinary
programs. Kaappi also bundles
[SRFI 64](https://srfi.schemers.org/srfi-64/srfi-64.html); suites
written against `(srfi 64)` get discovery and aggregation from the
built-in `kaappi test` runner, with no install step at all:

```scheme
;; tests/test-strings.scm
(import (scheme base) (srfi 64))

(test-begin "strings")
(test-equal "upcase" "ABC" (string-upcase "abc"))
(test-equal "append" "ab" (string-append "a" "b"))
(test-end "strings")
```

```console
$ kaappi test tests/
kaappi test: seed 76958 (reproduce with: kaappi test --seed 76958)
  PASS  tests/test-demo.scm  (1 tests, 0 skipped, 4ms)
  PASS  tests/test-strings.scm  (2 tests, 0 skipped, 7ms)

Summary: 3 passed, 0 failed, 0 unexpected-pass, 0 expected-fail, 0 skipped
Files:   2 run, 0 failed, 0 errored (133ms)
Seed:    76958  (reproduce with: kaappi test --seed 76958)
```

Each file runs in its own subprocess, so one crashing suite cannot take
down the rest; the runner aggregates the counts and exits non-zero on
any failure. The printed seed is fed to SRFI-27's default random source
in every subprocess, so a failing randomized test reproduces exactly
with `kaappi test --seed <n>`.

The runner discovers files that import `(srfi 64)` under the paths you
give it — suites written with `(kaappi test)` are not picked up; run
those directly as shown above. Useful flags:

- `--json` — one JSON object per file plus a summary line, for tooling
- `--changed` — run only suites whose import closure changed since
  `HEAD` (`--since <rev>` for another baseline); `--list-affected`
  prints them without running
- `--lib-path ./lib` — same meaning as everywhere else

For SRFI-64 suites the CI step becomes a single command:

```yaml
      - name: Run tests
        run: kaappi test tests/
```
